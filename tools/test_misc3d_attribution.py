"""Independent ELF controls for raw source/caller attribution evidence."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid, identity, sha256
import misc3d_attribution as attribution


class AttributionControls(unittest.TestCase):
    def fixture(self, root):
        path = '../fr2/source/synthetic.c'
        words = (15 << 26 | 4 << 16, 9 << 26 | 4 << 21 | 4 << 16 | 0x5000,
                 3 << 26 | 0x105888 >> 2, 0, 3 << 26 | 0x2000 >> 2, 0,
                 2 << 26 | 0x12c218 >> 2, 0)
        code = struct.pack('<8I', *words)
        leaf = struct.pack('<II', 31 << 21 | 8, 43 << 26 | 28 << 21 | 4 << 16 | 0x94cc)
        data = build_elf([Spec('.text', code, flags=6, address=0x1000),
                          Spec('.leaf', leaf, flags=6, address=0x12c218),
                          Spec('.rodata', path.encode() + b'\0', flags=2, address=0x5000)])
        inventory = root/'inventory.json'
        inventory.write_text(json.dumps({'functions': [{'entry': '00001000', 'instructions': [
            {'address': '00001004', 'references': [{'to': '00005000'}]},
            {'address': '00001010', 'references': [{'to': '00002000'}]}]}]}))
        contract = root/'contract.json'
        source = {'source_path': path, 'source_string_address': '00005000',
                  'source_string_sha256': sha256(path.encode() + b'\0'),
                  'saved_function': '00001000', 'site': '00001004', 'word_sha256': sha256(code[4:8]),
                  'upper_address_site': '00001000', 'upper_word_sha256': sha256(code[:4]),
                  'diagnostic_transfer_site': '00001008', 'diagnostic_word_sha256': sha256(code[8:12])}
        contract.write_text(json.dumps({'corpus_sha256': sha256(data), 'inventory_identity': identity(inventory),
            'candidate_main_ranges': [{'start': '00001000', 'end_exclusive': '00001020',
                                       'bytes': 32, 'sha256': sha256(code)}],
            'direct_source_evidence': [source], 'independent_startup_calls': [
                {'saved_caller': '00001000', 'site': '00001010', 'target': '00002000',
                 'word_sha256': sha256(code[16:20])}],
            'remote_terminal': {'range': {'start': '0012c218', 'end_exclusive': '0012c220',
                                         'bytes': 8, 'sha256': sha256(leaf)},
                                'call_site': '00001018', 'call_word_sha256': sha256(code[24:28]),
                                'entry_restore_sites': []}}))
        return data, inventory, contract

    def check(self, data, inventory, contract):
        with patch.object(attribution, 'CONTRACT', contract), patch.object(attribution, 'EE_CORPUS_SHA256', sha256(data)), patch.object(attribution, 'MAIN_RANGES', ((0x1000, 0x1020),)):
            return attribution.check(data, inventory)

    def test_positive_keeps_external_leaf_and_zero_credit(self):
        with tempfile.TemporaryDirectory() as temp:
            data, inventory, contract = self.fixture(Path(temp))
            result = self.check(data, inventory, contract)
            self.assertEqual(result['main_bytes'], 32)
            self.assertEqual(result['external_leaf']['range']['bytes'], 8)
            self.assertEqual(result['new_attributed_match_bytes'], 0)

    def test_changed_source_address_fails_even_when_inventory_absent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, contract = self.fixture(root)
            recorded = json.loads(contract.read_text())
            recorded['direct_source_evidence'][0]['upper_address_site'] = '00001004'
            recorded['direct_source_evidence'][0]['upper_word_sha256'] = recorded['direct_source_evidence'][0]['word_sha256']
            contract.write_text(json.dumps(recorded))
            with self.assertRaisesRegex(Invalid, 'A0 source-path construction'):
                self.check(data, root/'absent.json', contract)

    def test_missing_inventory_remains_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, contract = self.fixture(root)
            with self.assertRaisesRegex(Incomplete, 'raw inventory is absent'):
                self.check(data, root/'absent.json', contract)

    def test_changed_caller_edge_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            data, inventory, contract = self.fixture(Path(temp))
            recorded = json.loads(contract.read_text())
            recorded['independent_startup_calls'][0]['target'] = '00002004'
            contract.write_text(json.dumps(recorded))
            with self.assertRaisesRegex(Invalid, 'independent startup transfer'):
                self.check(data, inventory, contract)


if __name__ == '__main__':
    unittest.main()
