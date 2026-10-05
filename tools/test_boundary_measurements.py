import unittest

from boundary_measurements import measure
from elf_fixture import Spec, build_elf

RODATA = (b"\0../fr2/source/a.c\0../fr2/source/b.c\0../modules4/3d/c.c\0"
          b"x../fr2/mid_string.c\0../fr2/source/a.c\0")
DATA = b"PsIIlibkernl2550\0\0PsIIlibpad  2500"


class MeasureTest(unittest.TestCase):
    def setUp(self):
        self.result = measure(build_elf([Spec(".rodata", RODATA), Spec(".data", DATA, flags=3)]))

    def test_source_paths_are_distinct_string_start_anchored_and_counted_by_prefix(self):
        paths = self.result["source_paths"]
        self.assertEqual(paths["distinct"], 3)  # the duplicate and the mid-string fragment are not counted
        self.assertEqual(paths["by_prefix"], {"fr2": 2, "modules4": 1})
        self.assertEqual(paths["by_section"], {".rodata": 3})

    def test_sdk_stamps_are_counted_by_section_and_library(self):
        stamps = self.result["sdk_stamps"]
        self.assertEqual(stamps["total"], 2)
        self.assertEqual(stamps["by_section"], {".data": 2})
        self.assertEqual(stamps["libraries"], ["libkernl", "libpad"])

    def test_the_command_that_reproduces_the_numbers_is_named_in_the_result(self):
        self.assertIn("boundary_measurements.py", self.result["reproduce"])


if __name__ == "__main__":
    unittest.main()
