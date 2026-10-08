"""Negative oracle checks for native-output validation, independent of GAS internals."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from evidence_common import Incomplete, Invalid
from test_ps2_vu import fixture
import verify_vu as subject


class EntryMapValidationTest(unittest.TestCase):
    def test_caller_reference_must_resolve_inside_the_named_overlay(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved'} for i in range(8)]
        rows[5] = {'index': 5, 'status': 'documented', 'interface': 'unresolved', 'entries': [{'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]}
        dispatch = {'entry_mapping': {'overlay_index': 5, 'vu_byte_address': '0x2e60',
                                      'global_value': '0x5cc', 'ee_builder': 'FUN_00128ca0'}}
        result = subject.validate_entry_map({'overlays': rows}, overlays, evidence={'dispatch': dispatch})
        self.assertEqual(result['documented_entry_count'], 1)
        self.assertEqual(result['incomplete_overlay_indices'], [0, 1, 2, 3, 4, 6, 7])
        rows[5]['entries'][0]['vu_byte_address'] = 0x3800
        with self.assertRaises(Invalid): subject.validate_entry_map({'overlays': rows}, overlays, evidence={'dispatch': dispatch})

    def test_caller_claim_cannot_exceed_the_pinned_evidence(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved'} for i in range(8)]
        rows[5] = {'index': 5, 'status': 'documented', 'interface': 'unresolved', 'entries': [{'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]}
        contradiction = {'entry_mapping': {'overlay_index': 5, 'vu_byte_address': '0x2e60',
                                           'global_value': '0x5cc', 'ee_builder': 'FUN_001124c0'}}
        with self.assertRaisesRegex(Invalid, 'contradicts its pinned'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence={'dispatch': contradiction})

    def test_missing_entry_evidence_is_incomplete(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved'} for i in range(8)]
        rows[5] = {'index': 5, 'status': 'documented', 'interface': 'unresolved', 'entries': [{'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]}
        with self.assertRaises(Incomplete): subject.validate_entry_map({'overlays': rows}, overlays, evidence={})


class NativeVuValidationTest(unittest.TestCase):
    def _run_fixture(self, mode):
        data, offsets, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable, tool = root / 'game.elf', root / 'native-tool'
            executable.write_bytes(data); tool.write_bytes(b'fixture tool identity')
            overlays = subject.parse_overlays(data)['overlays']
            entry_map = root / 'entry-map.json'
            entry_map.write_text(__import__('json').dumps({'evidence': {}, 'overlays': [
                {'index': row['index'], 'status': 'incomplete', 'entries': [], 'interface': 'unresolved'}
                for row in overlays
            ]}))

            def native(command, stem):
                stdout = stem.with_suffix('.stdout')
                if '-D' in command:
                    stdout.write_text('0:\t14 00 01 10 \tnop\tnop\n')
                elif mode != 'missing':
                    output = bytearray(data)
                    if mode == 'mismatch': output[offsets[1]] ^= 1
                    if mode == 'relocation':
                        # Use the existing nonempty overlay-table payload as a relocation section.
                        shoff = struct.unpack_from('<I', output, 32)[0]
                        struct.pack_into('<I', output, shoff + 2*40 + 4, 9)
                    Path(command[2]).write_bytes(output)
                return {'command': command, 'exit_code': 0,
                        'stdout': {'path': str(stdout)}}

            with patch.object(subject, 'validate_entry_map', return_value={
                    'documented_entry_count': 0, 'incomplete_overlay_indices': [0]}), \
                 patch.object(subject, '_run', side_effect=native):
                return subject.verify(executable, tool, tool, root / 'work', entry_map)

    def test_corrupted_native_object_cannot_pass(self):
        with self.assertRaisesRegex(Invalid, 'round trip differs') as caught:
            self._run_fixture('mismatch')
        self.assertFalse(caught.exception.details['overlays'][0]['exact_match'])
        self.assertEqual(caught.exception.details['overlays'][0]['byte_gate']['status'], 'fail')

    def test_byte_exact_reassembly_passes_the_per_unit_gate_but_keeps_unknown_maps_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'maps remain incomplete') as caught:
            self._run_fixture('exact')
        details = caught.exception.details
        self.assertEqual(details['overlays'][0]['byte_gate']['status'], 'pass')
        self.assertEqual(details['entry_map_disposition'], 'incomplete')
        self.assertEqual(details['interface_status'], 'incomplete')

    def test_success_without_native_output_is_invalid(self):
        with self.assertRaisesRegex(Invalid, 'without writing'):
            self._run_fixture('missing')

    def test_unresolved_native_relocation_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'unresolved relocations'):
            self._run_fixture('relocation')

    def test_missing_native_tool_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'native tool is missing'):
            subject._tool(Path('/nonexistent/fr2-verifier-native-tool'), 'dvp-as')


if __name__ == '__main__': unittest.main()
