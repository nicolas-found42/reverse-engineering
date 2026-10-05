import tempfile
import unittest
from pathlib import Path

from elf_fixture import Spec, build_elf
from evidence_common import Invalid
from matching_diff import compare
from matching_sections import sections
from slice_units import slice_units

TEXT = bytes(range(16))


class SliceUnitsTest(unittest.TestCase):
    def setUp(self):
        self.found = sections(build_elf([Spec(".text", TEXT, flags=6), Spec(".sbss", b"", kind=8),
                                         Spec(".reginfo", b"\0" * 24, kind=0x70000006)]))

    def test_scored_sections_become_identical_units_and_metadata_and_nobits_are_left_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(slice_units(self.found, Path(tmp)), [".text"])
            self.assertEqual(compare(self.found[".text"], (Path(tmp) / ".text.bin").read_bytes()).status, "pass")

    def test_corrupt_changes_exactly_one_word_and_the_gate_fails_there(self):
        with tempfile.TemporaryDirectory() as tmp:
            slice_units(self.found, Path(tmp), ".text:0x8")
            verdict = compare(self.found[".text"], (Path(tmp) / ".text.bin").read_bytes())
        self.assertEqual((verdict.status, (verdict.first_difference or {}).get("offset")), ("fail", 8))

    def test_corrupt_outside_a_scored_section_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(Invalid):
            slice_units(self.found, Path(tmp), ".text:0x40")


if __name__ == "__main__":
    unittest.main()
