"""Public linked-output seam; synthetic fixtures do not establish corpus acceptance."""
import unittest
from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid
from misc3d_lifecycle import verify_outputs


class LifecycleOutputTests(unittest.TestCase):
    def complete(self, *, shifted=False):
        ranges = [
            ('reset', 0x1d17a8, b'R' * 28), ('release', 0x1d17c8, b'L' * 56),
            ('get_database_id', 0x1d1800, b'A' * 60),
            ('get_state_cc', 0x1d1840, b'C' * 64),
            ('get_state_d4', 0x1d1880, b'D' * 64),
            ('get_state_d0', 0x1d18c0, b'E' * 64),
        ]
        text = bytearray(344)
        for _, address, payload in ranges:
            text[address - 0x1d17a8:address - 0x1d17a8 + len(payload)] = payload
        retail = build_elf([Spec('.text', bytes(text), flags=6, address=0x1d17a8),
                            Spec('.sbss', kind=8, flags=3, address=0x290ac4, size=20)])
        specs = [Spec('.text.fr2_misc3d_' + name, payload, flags=6, address=address)
                 for name, address, payload in ranges]
        specs += [Spec('.sbss.fr2_misc3d_db_id', kind=8, flags=3,
                       address=0x290ac4, size=4, alignment=4)]
        for suffix, address in [('c8', 0x290ac8), ('cc', 0x290acc),
                                ('d0', 0x290ad0), ('d4', 0x290ad4)]:
            specs.append(Spec('.sbss.fr2_misc3d_state_' + suffix, kind=8, flags=3,
                              address=address + (4 if shifted and suffix == 'cc' else 0),
                              size=4, alignment=4))
        return retail, build_elf(specs)

    def test_sibling_cells_cannot_move_even_with_matching_code(self):
        with self.assertRaisesRegex(Invalid, 'state_cc layout'):
            verify_outputs(*self.complete(shifted=True))

    def test_available_mismatch_takes_precedence_over_missing_code(self):
        retail, _ = self.complete()
        candidate = build_elf([Spec('.text.fr2_misc3d_release', b'X' * 56,
                                    flags=6, address=0x1d17c8)])
        with self.assertRaisesRegex(Invalid, 'release bytes'):
            verify_outputs(retail, candidate)

    def test_positive_compares_six_spans_and_counts_no_nobits_payload(self):
        result = verify_outputs(*self.complete())
        self.assertEqual(sum(row['bytes'] for row in result['spans'].values()), 336)
        self.assertEqual(len(result['cells']), 5)
        self.assertTrue(all(row['matched_file_bytes'] == 0 for row in result['cells'].values()))

    def test_missing_required_spans_is_incomplete(self):
        retail, _ = self.complete()
        with self.assertRaisesRegex(Incomplete, 'reset linked section'):
            verify_outputs(retail, build_elf([Spec('.text', b'', flags=6)]))

    def test_sibling_byte_change_fails_its_own_comparison(self):
        retail, candidate = self.complete()
        from ps2_executables import parse_elf
        elf = parse_elf(candidate)
        row = next(row for row in elf['sections'] if row['name'] == '.text.fr2_misc3d_get_state_cc')
        changed = bytearray(candidate)
        changed[row['offset']] ^= 1
        with self.assertRaisesRegex(Invalid, 'get_state_cc bytes'):
            verify_outputs(retail, bytes(changed))

    def test_reset_has_an_independent_comparison(self):
        retail = build_elf([
            Spec('.text', b'R' * 28, flags=6, address=0x1d17a8),
            Spec('.sbss', kind=8, flags=3, address=0x290ac4, size=20),
        ])
        candidate = build_elf([
            Spec('.text.fr2_misc3d_reset', b'X' * 28, flags=6, address=0x1d17a8),
        ])
        with self.assertRaisesRegex(Invalid, 'reset bytes'):
            verify_outputs(retail, candidate)


class LifecycleProvenanceTests(unittest.TestCase):
    def test_missing_recorded_observation_is_incomplete_before_tool_execution(self):
        from pathlib import Path
        from unittest.mock import patch
        import misc3d_lifecycle as contract
        with patch.object(contract, 'OBSERVATION', Path('/missing/lifecycle-observation.json')):
            with self.assertRaisesRegex(Incomplete, 'provenance missing'):
                contract.check(Path('/missing/game'), Path('/missing/tool-root'))

    def test_changed_source_outranks_missing_observation(self):
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        import misc3d_lifecycle as contract
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'changed.c'
            changed.write_text('void fr2_misc3d_reset(void) {}')
            with patch.object(contract, 'OBSERVATION', Path(tmp) / 'missing.json'), \
                 patch.dict(contract.SOURCES, {'lifecycle': changed}):
                with self.assertRaisesRegex(Invalid, 'lifecycle identity differs'):
                    contract.check(Path('/missing/game'), Path('/missing/tool-root'))

    def test_changed_source_outranks_missing_previous_provenance(self):
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        import misc3d_contract as previous
        import misc3d_lifecycle as contract
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'changed.c'
            changed.write_text('void fr2_misc3d_reset(void) {}')
            with patch.object(previous, 'OBSERVATION', Path(tmp) / 'missing-previous.json'), \
                 patch.dict(contract.SOURCES, {'lifecycle': changed}):
                with self.assertRaisesRegex(Invalid, 'lifecycle identity differs'):
                    contract.check(Path('/missing/game'), Path('/missing/tool-root'))

    def test_cli_changed_source_outranks_missing_source_and_retains_identities(self):
        from pathlib import Path
        import json
        import platform
        import subprocess
        import sys
        import tempfile
        from unittest.mock import patch
        import misc3d_lifecycle as contract
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changed = root / 'changed-sibling.c'
            changed.write_text('int changed_sibling(void) { return 0; }\n')
            platform.platform()
            with patch.dict(contract.SOURCES, {'lifecycle': root / 'missing.c', 'siblings': changed}), \
                 patch.object(sys, 'argv', ['misc3d_lifecycle.py', '/missing/game', '/missing/tools',
                                          '--output', str(root / 'receipts')]), \
                 patch.object(subprocess, 'Popen', side_effect=AssertionError('tool launch attempted')):
                code = contract.main()
            receipt = json.loads(next((root / 'receipts').glob('*/result.json')).read_text())
            self.assertEqual(code, 1)
            self.assertEqual(receipt['status'], 'fail')
            self.assertIn('siblings identity differs', ' '.join(receipt['diagnostics']))
            for path in (changed, contract.DECISION, contract.OBSERVATION):
                self.assertIn(str(path), receipt['inputs'])

    def test_cli_missing_source_without_contradiction_remains_incomplete(self):
        from pathlib import Path
        import json
        import platform
        import subprocess
        import sys
        import tempfile
        from unittest.mock import patch
        import misc3d_lifecycle as contract
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            platform.platform()
            with patch.dict(contract.SOURCES, {'lifecycle': root / 'missing.c'}), \
                 patch.object(sys, 'argv', ['misc3d_lifecycle.py', '/missing/game', '/missing/tools',
                                          '--output', str(root / 'receipts')]), \
                 patch.object(subprocess, 'Popen', side_effect=AssertionError('tool launch attempted')):
                code = contract.main()
            receipt = json.loads(next((root / 'receipts').glob('*/result.json')).read_text())
            self.assertEqual(code, 2)
            self.assertEqual(receipt['status'], 'incomplete')
            self.assertIn('lifecycle provenance missing', ' '.join(receipt['diagnostics']))

    def test_changed_source_identity_fails_before_tool_execution(self):
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        import misc3d_lifecycle as contract
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'changed.c'
            changed.write_text('void fr2_misc3d_reset(void) {}')
            with patch.dict(contract.SOURCES, {'lifecycle': changed}):
                with self.assertRaisesRegex(Invalid, 'lifecycle identity differs'):
                    contract.check(Path('/missing/game'), Path('/missing/tool-root'))


if __name__ == '__main__':
    unittest.main()
