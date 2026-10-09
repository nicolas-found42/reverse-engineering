"""Public raw-evidence lifetime seam, with independent synthetic ELF controls."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid, identity, sha256
import misc3d_lifetime as lifetime


class LifetimeControls(unittest.TestCase):
    def fixture(self, root):
        words = struct.pack('<II', 3 << 26 | 0x2000 >> 2, 0)
        data = build_elf([Spec('.text', words, flags=6, address=0x1000)])
        inventory = root/'inventory.json'
        inventory.write_text(json.dumps({'executable_sha256': sha256(data), 'functions': [
            {'entry': '00001000', 'callers': [], 'instructions': [
                {'address': '00001000', 'bytes': words[:4].hex()},
                {'address': '00001004', 'bytes': words[4:].hex()}]}]}))
        contract = root/'contract.json'
        contract.write_text(json.dumps({'schema': 'fr2-misc3d-lifetime/v1',
            'corpus_sha256': sha256(data), 'inventory_identity': identity(inventory),
            'functions': [{'entry': '00001000', 'saved_callers': [], 'ranges': [
                {'start': '00001000', 'end_exclusive': '00001008', 'bytes': 8,
                 'sha256': sha256(words)}]}],
            'direct_calls': [{'site': '00001000', 'target': '00002000',
                              'word_sha256': sha256(words[:4])}],
            'observed_contract': {'new_attributed_match_bytes': 0,
                                  'claim_limit': 'Static producer/use/release contract.'}}))
        return data, inventory, contract

    def test_positive_reconciles_private_raw_inventory_and_keeps_zero_credit(self):
        with tempfile.TemporaryDirectory() as temp:
            data, inventory, contract = self.fixture(Path(temp))
            with patch.object(lifetime, 'CONTRACT', contract), patch.object(lifetime, 'EE_CORPUS_SHA256', sha256(data)):
                result = lifetime.check(data, inventory)
            self.assertEqual(result['new_attributed_match_bytes'], 0)
            self.assertEqual(result['checked_functions'], 1)
            self.assertEqual(result['checked_direct_calls'], 1)

    def test_missing_inventory_remains_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, contract = self.fixture(root)
            with patch.object(lifetime, 'CONTRACT', contract), patch.object(lifetime, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Incomplete, 'raw inventory is absent'):
                    lifetime.check(data, root/'absent.json')

    def test_changed_saved_evidence_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            data, inventory, contract = self.fixture(Path(temp))
            inventory.write_text(inventory.read_text() + ' ')
            with patch.object(lifetime, 'CONTRACT', contract), patch.object(lifetime, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Invalid, 'inventory identity differs'):
                    lifetime.check(data, inventory)

    def test_changed_transfer_cannot_be_hidden_by_missing_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, _, contract = self.fixture(root)
            recorded = json.loads(contract.read_text())
            recorded['direct_calls'][0]['target'] = '00003000'
            contract.write_text(json.dumps(recorded))
            with patch.object(lifetime, 'CONTRACT', contract), patch.object(lifetime, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Invalid, 'direct transfer contradicts'):
                    lifetime.check(data, root/'absent.json')

    def test_required_code_absence_stays_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, _, contract = self.fixture(root)
            data = build_elf([Spec('.other', b'\0' * 8, flags=6, address=0x4000)])
            recorded = json.loads(contract.read_text())
            recorded['corpus_sha256'] = sha256(data)
            contract.write_text(json.dumps(recorded))
            with patch.object(lifetime, 'CONTRACT', contract), patch.object(lifetime, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Incomplete, 'required lifetime code absent'):
                    lifetime.check(data, root/'absent.json')

    def test_unpinned_corpus_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            data, inventory, _ = self.fixture(Path(temp))
            with self.assertRaisesRegex(Invalid, 'unchanged recorded executable'):
                lifetime.check(data, inventory)

    def test_public_cli_missing_corpus_writes_incomplete_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = subprocess.run([sys.executable, lifetime.__file__, str(root/'game'),
                                     str(root/'inventory.json'), '--output', str(root/'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            receipt = json.loads(next((root/'receipts').glob('*/result.json')).read_text())
            self.assertEqual(receipt['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
