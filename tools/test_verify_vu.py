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
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved', 'incomplete_reasons': ['not fully mapped']} for i in range(8)]
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
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved', 'incomplete_reasons': ['not fully mapped']} for i in range(8)]
        rows[5] = {'index': 5, 'status': 'documented', 'interface': 'unresolved', 'entries': [{'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]}
        contradiction = {'entry_mapping': {'overlay_index': 5, 'vu_byte_address': '0x2e60',
                                           'global_value': '0x5cc', 'ee_builder': 'FUN_001124c0'}}
        with self.assertRaisesRegex(Invalid, 'contradicts its pinned'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence={'dispatch': contradiction})

    def test_missing_entry_evidence_is_incomplete(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved', 'incomplete_reasons': ['not fully mapped']} for i in range(8)]
        rows[5] = {'index': 5, 'status': 'documented', 'interface': 'unresolved', 'entries': [{'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]}
        with self.assertRaises(Incomplete): subject.validate_entry_map({'overlays': rows}, overlays, evidence={})

    def test_incomplete_entry_rows_require_a_falsifiable_reason(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved',
                 'incomplete_reasons': ['not fully mapped']} for i in range(8)]
        rows[3].pop('incomplete_reasons')
        with self.assertRaisesRegex(Invalid, 'must state why'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence={})

    def test_partial_interface_contract_requires_evidence_and_preserves_unknowns(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800,
                     'source_offset': i * 0x800} for i in range(8)]
        raw_anchors = {'0x2eb8': 'bc060180ff020000', '0x2ee8': '03084308ff020000'}
        executable = bytearray(8 * 0x800)
        for address, raw in raw_anchors.items():
            start = overlays[5]['source_offset'] + int(address, 16) - overlays[5]['vu_byte_address']
            executable[start:start + 8] = bytes.fromhex(raw)
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': {
            'status': 'unresolved', 'inputs': [], 'outputs': [], 'state': [],
            'evidence': [], 'unknowns': ['no complete contract']},
            'incomplete_reasons': ['entry coverage incomplete']} for i in range(8)]
        rows[5]['interface'] = {
            'status': 'partial', 'inputs': ['TOP+3.z in VU data memory'],
            'outputs': ['vi03 is used as a later VU data-memory base'],
            'state': ['XTOP vi01; ILW Z at offset 3'],
            'evidence': [{'source': 'consumer', 'anchor_addresses': ['0x2eb8', '0x2ee8']}],
            'unknowns': ['runtime TOPS and VIF mode/cycle state'],
        }
        evidence = {'consumer': {'overlay_index': 5, 'overlay_mapping': {'anchors': [
            {'address': address, 'raw_bytes': raw} for address, raw in raw_anchors.items()],
            'section_base': '0x2800'}}}
        result = subject.validate_entry_map({'overlays': rows}, overlays, evidence=evidence,
                                            executable=bytes(executable))
        self.assertEqual(result['partial_interface_overlay_indices'], [5])
        self.assertEqual(result['interface_status'], 'incomplete')
        rows[5]['interface']['evidence'] = [{'source': 'missing', 'anchor_addresses': ['0x2eb8']}]
        with self.assertRaisesRegex(Incomplete, 'interface evidence'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence=evidence)
        rows[5]['interface']['evidence'] = [{'source': 'consumer', 'anchor_addresses': ['0x2eb8', '0xdead']}]
        with self.assertRaisesRegex(Invalid, 'absent instruction anchor'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence=evidence,
                                        executable=bytes(executable))
        rows[5]['interface']['evidence'] = [{'source': 'consumer', 'anchor_addresses': ['0x2eb8']}]
        corrupted = bytearray(executable)
        corrupted[overlays[5]['source_offset'] + 0x6b8] ^= 1
        with self.assertRaisesRegex(Invalid, 'instruction anchor bytes differ'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence=evidence,
                                        executable=bytes(corrupted))

    def test_interface_contract_cannot_be_declared_complete_with_unknowns(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800,
                     'source_offset': i * 0x800} for i in range(8)]
        executable = bytearray(8 * 0x800)
        executable[5 * 0x800 + 0x6b8:5 * 0x800 + 0x6c0] = bytes.fromhex('bc060180ff020000')
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': {
            'status': 'unresolved', 'inputs': [], 'outputs': [], 'state': [],
            'evidence': [], 'unknowns': ['unmapped']},
            'incomplete_reasons': ['entry coverage incomplete']} for i in range(8)]
        rows[5]['interface'] = {'status': 'complete', 'inputs': ['input'], 'outputs': ['output'],
                                'state': ['state'], 'evidence': [{'source': 'consumer', 'anchor_addresses': ['0x2eb8']}], 'unknowns': ['TOPS unknown']}
        evidence = {'consumer': {'overlay_index': 5, 'overlay_mapping': {'section_base':'0x2800', 'anchors': [{'address': '0x2eb8', 'raw_bytes':'bc060180ff020000'}]}}}
        with self.assertRaisesRegex(Invalid, 'complete interface'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence=evidence,
                                        executable=bytes(executable))

    def test_instruction_anchor_must_match_the_executable_bytes(self):
        source = {'executable': {'sha256': 'abc'}, 'instruction_anchors': [
            {'address': '001124c0', 'bytes': '25186a00'}]}
        with self.assertRaisesRegex(Invalid, 'instruction anchor bytes'):
            subject.verify_instruction_anchors(source, executable_sha256='abc',
                                               read_address=lambda _address, _size: b'\0' * 4)
        with self.assertRaisesRegex(Invalid, 'executable SHA-256'):
            subject.verify_instruction_anchors(source, executable_sha256='def',
                                               read_address=lambda _address, _size: bytes.fromhex('25186a00'))

    def test_entry_evidence_instruction_anchors_are_checked_against_the_executable(self):
        overlays = [{'index': i, 'vu_byte_address': i * 0x800, 'bytes': 0x800,
                     'source_offset': i * 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved',
                 'incomplete_reasons': ['entry coverage incomplete']} for i in range(8)]
        rows[0]['entries'] = [{'msc_address': 0, 'vu_byte_address': 0,
                               'caller': 'FUN_001124c0', 'evidence': 'initialization', 'channel': 'VIF1'}]
        source = {'executable': {'sha256': 'wrong'},
                  'entry_mapping': {'overlay_index': 0, 'vu_byte_address': '0x0',
                                    'global_value': '0x0', 'ee_builder': 'FUN_001124c0', 'channel': 'VIF1'},
                  'instruction_anchors': [{'address': '001124c0', 'bytes': '25186a00'}]}
        with self.assertRaisesRegex(Invalid, 'executable SHA-256'):
            subject.validate_entry_map({'overlays': rows}, overlays,
                                       evidence={'initialization': source}, executable=b'fixture')

    def test_additional_static_callers_map_only_to_their_pinned_overlay_and_keep_scope_incomplete(self):
        overlays = [{'index': i, 'vu_byte_address': 0 if i == 7 else i * 0x800, 'bytes': 0x460 if i == 7 else 0x800} for i in range(8)]
        rows = [{'index': i, 'status': 'incomplete', 'entries': [], 'interface': 'unresolved', 'incomplete_reasons': ['runtime and exhaustive dispatch are unresolved']} for i in range(8)]
        rows[0]['entries'] = [{'msc_address': 0x1a, 'vu_byte_address': 0xd0, 'caller': 'FUN_0021c3e0', 'evidence': 'additional', 'channel': 'VIF1'}]
        rows[4]['entries'] = [{'msc_address': 0x4d1, 'vu_byte_address': 0x2688, 'caller': 'FUN_00228b38', 'evidence': 'additional', 'channel': 'VIF1'}]
        rows[5]['entries'] = [{'msc_address': 0x554, 'vu_byte_address': 0x2aa0, 'caller': 'FUN_0012a230', 'evidence': 'additional', 'channel': 'VIF1'}, {'msc_address': 0x5cc, 'vu_byte_address': 0x2e60, 'caller': 'FUN_00128ca0', 'evidence': 'dispatch'}]
        additional = {'derivations': [
            {'overlay_index': 0, 'vu_byte_address': '0xd0', 'msc_immediate': '0x1a', 'caller': 'FUN_0021c3e0', 'channel': 'VIF1'},
            {'overlay_index': 4, 'vu_byte_address': '0x2688', 'msc_immediate': '0x4d1', 'caller': 'FUN_00228b38', 'channel': 'VIF1'},
            {'overlay_index': 5, 'vu_byte_address': '0x2aa0', 'msc_immediate': '0x554', 'caller': 'FUN_0012a230', 'channel': 'VIF1'}]}
        dispatch = {'entry_mapping': {'overlay_index': 5, 'vu_byte_address': '0x2e60', 'global_value': '0x5cc', 'ee_builder': 'FUN_00128ca0'}}
        result = subject.validate_entry_map({'overlays': rows}, overlays, evidence={'additional': additional, 'dispatch': dispatch})
        self.assertEqual(result['documented_entry_count'], 4)
        self.assertEqual(result['incomplete_overlay_indices'], list(range(8)))
        additional['derivations'][0]['msc_immediate'] = '0x1b'
        with self.assertRaisesRegex(Invalid, 'contradicts its pinned'):
            subject.validate_entry_map({'overlays': rows}, overlays, evidence={'additional': additional, 'dispatch': dispatch})


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
                    'documented_entry_count': 0, 'incomplete_overlay_indices': [0],
                    'partial_interface_overlay_indices': [], 'complete_interface_overlay_indices': [],
                    'interface_status': 'incomplete', 'interfaces': []}), \
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
