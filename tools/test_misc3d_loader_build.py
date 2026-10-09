"""Synthetic ELF controls for the fixed main-loader source/output seam."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid, identity, sha256
from misc3d_loader_recipe import loader_build as loader


def fixture(changed=None, shifted=False, missing=False, hole_changed=False):
    main = bytearray(struct.pack('<I', 0x24020001) * 136)
    terminal = struct.pack('<II', 31 << 21 | 8, 43 << 26 | 28 << 21 | 4 << 16 | 0x94cc)
    reference = bytearray(0x1d1628 - 0x12c218)
    reference[:8] = terminal
    reference[0x1d1408 - 0x12c218:] = main
    retail = build_elf([Spec('.text', bytes(reference), flags=6, address=0x12c218)])
    if changed is not None:
        main[changed] ^= 1
    if hole_changed:
        for offset in (52, 372, 428, 452):
            main[offset] ^= 1
    sections = [Spec('.text.fr2_misc3d_loader_main', bytes(main), flags=6,
                     address=0x1d140c if shifted else 0x1d1408)]
    if not missing:
        sections.append(Spec('.text.fr2_misc3d_loader_terminal', terminal, flags=6, address=0x12c218))
    return retail, build_elf(sections)


class LoaderBuildControls(unittest.TestCase):
    def test_positive_compares_saved_ranges_and_separate_external_leaf(self):
        result = loader.compare(*fixture())
        self.assertEqual(result['main_instruction_bytes'], 528)
        self.assertEqual(result['excluded_main_hole_bytes'], 16)
        self.assertEqual(result['terminal']['candidate_byte_identical_bytes'], 8)
        self.assertEqual(result['new_attributed_match_bytes'], 0)

    def test_changed_main_instruction_fails(self):
        with self.assertRaisesRegex(Invalid, 'raw range bytes differ'):
            loader.compare(*fixture(changed=0))

    def test_changed_saved_range_after_holes_fails(self):
        with self.assertRaisesRegex(Invalid, 'raw range bytes differ'):
            loader.compare(*fixture(changed=456))

    def test_shifted_main_layout_fails(self):
        with self.assertRaisesRegex(Invalid, 'main address/size differs'):
            loader.compare(*fixture(shifted=True))

    def test_excluded_holes_receive_no_match_credit(self):
        result = loader.compare(*fixture(hole_changed=True))
        self.assertEqual(result['main_instruction_bytes'], 528)
        self.assertEqual(result['excluded_main_hole_bytes'], 16)
        self.assertEqual(result['new_attributed_match_bytes'], 0)

    def test_missing_external_leaf_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'candidate section is absent'):
            loader.compare(*fixture(missing=True))

    def test_missing_build_decision_is_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            executable = root/'extracted/SLES_517.05'
            executable.parent.mkdir()
            data, _ = fixture()
            executable.write_bytes(data)
            with patch.object(loader, 'DECISION', root/'absent.json'), patch.object(loader, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Incomplete, 'build decision is absent'):
                    loader.provenance(root, root)

    def test_stale_source_identity_outranks_missing_tool_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            executable = root/'extracted/SLES_517.05'
            executable.parent.mkdir()
            data, _ = fixture()
            executable.write_bytes(data)
            decision = root/'decision.json'
            inputs = {'source': dict(identity(loader.SOURCE), sha256='0' * 64)}
            decision.write_text(json.dumps({'corpus_sha256': sha256(data), 'inputs': inputs}))
            with patch.object(loader, 'DECISION', decision), patch.object(loader, 'EE_CORPUS_SHA256', sha256(data)):
                with self.assertRaisesRegex(Invalid, 'source/recipe identity differs: source'):
                    loader.provenance(root, root/'absent-tools')


if __name__ == '__main__':
    unittest.main()
