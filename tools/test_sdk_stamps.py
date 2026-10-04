import tempfile
import unittest
from pathlib import Path

from sdk_stamps import find_stamps, scan_files


class FindStampsTest(unittest.TestCase):
    def test_library_stamp_has_trimmed_name_four_digit_version_and_offset(self):
        data = b"xx" + b"PsIIlibkernl2550" + b"\0" * 3 + b"PsIIlibcdvd 2530"
        self.assertEqual(find_stamps(data), [
            {"offset": 2, "library": "libkernl", "version": "2550"},
            {"offset": 21, "library": "libcdvd", "version": "2530"}])

    def test_module_banner_with_padded_name_is_found(self):
        self.assertEqual(find_stamps(b"PsIIcdvdman 2550")[0]["library"], "cdvdman")

    def test_near_misses_are_not_stamps(self):
        for blob in (b"psIIlibkernl2550", b"PsIIlibkernl25", b"PsIIlibkernl25x0", b"PsII", b"PsIILIBKERNL2550"):
            self.assertEqual(find_stamps(blob), [], blob)


class ScanFilesTest(unittest.TestCase):
    def test_files_report_stamps_hashes_and_the_distinct_version_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.bin").write_bytes(b"PsIIlibpad  2500")
            (root / "b.bin").write_bytes(b"nothing here")
            (root / "c.bin").write_bytes(b"PsIIlibpad  2500 PsIImcman   2540")
            result = scan_files([root / "a.bin", root / "b.bin", root / "c.bin"])
        self.assertEqual(result["files_scanned"], 3)
        self.assertEqual(result["files_with_stamps"], 2)
        self.assertEqual(result["libraries"], {"libpad": ["2500"], "mcman": ["2540"]})
        self.assertEqual(len(result["files"][0]["sha256"]), 64)
        self.assertTrue(any("not" in limit for limit in result["claim_limits"]))
