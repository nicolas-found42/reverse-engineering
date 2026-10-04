"""Tests at the verify_model.py CLI boundary; the real-corpus case skips when the corpus is absent."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import unittest

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games" / "ford-racing-2"


def model_bytes(leading=24, geometry=bytes(range(16)), pad=None):
    """Root name offset 20, one group naming offset 22; pool A\\0B\\0 ends at 24; then pad and geometry."""
    tree = struct.pack("<5I", leading, 1, 20, 1, 22) + b"A\0B\0"
    pad = bytes(8) if pad is None else pad  # 24 -> next 16-byte boundary at 32
    return tree + pad + geometry


class ModelVerifier(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def command(self, *args, timeout=None):
        out = self.root / "results"
        p = subprocess.run(
            [sys.executable, str(TOOLS / "verify_model.py"), *map(str, args), "--output", str(out)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda r: r.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        self.assertTrue(reports[-1].with_name("report.md").exists())
        return p.returncode, json.loads(reports[-1].read_text())

    def file(self, data, name="m.ps2"):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_valid_model_reports_boundaries_and_unresolved_geometry(self):
        code, result = self.command("file", self.file(model_bytes()))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        d = result["details"]
        self.assertEqual((d["name_pool_end"], d["geometry_region_start"], d["pad_length"]), (24, 32, 8))
        self.assertEqual(d["geometry_bytes"], 16)
        self.assertEqual(len(d["geometry_sha256"]), 64)
        self.assertTrue(any("geometry" in u for u in d["unresolved"]), d["unresolved"])
        self.assertTrue(any("later header" in u for u in d["unresolved"]), d["unresolved"])

    def test_leading_field_must_equal_the_name_pool_end(self):
        code, result = self.command("file", self.file(model_bytes(leading=77)))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("77" in d and "name pool end 24" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_padding_before_geometry_must_be_zero(self):
        code, result = self.command("file", self.file(model_bytes(pad=b"\0\0\0\0\0\0\0\1")))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("padding" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_size_must_be_a_multiple_of_sixteen(self):
        code, result = self.command("file", self.file(model_bytes() + b"\0"))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("multiple of 16" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_name_tree_errors_from_the_milestone_contract_still_fail(self):
        broken = bytearray(model_bytes())
        broken[22] = 0x01  # name at offset 22 loses its terminator position
        broken[23] = 0x02
        code, result = self.command("file", self.file(bytes(broken)))
        self.assertEqual((code, result["status"]), (1, "fail"))

    def test_truncated_and_oversized_inputs_fail(self):
        code, result = self.command("file", self.file(b"\x18\0\0"))
        self.assertEqual((code, result["status"]), (1, "fail"))
        big = self.root / "big.ps2"
        with big.open("wb") as stream:
            stream.truncate(128 * 1024 * 1024 + 1)
        code, result = self.command("file", big)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("exceeds" in d for d in result["diagnostics"]))

    def test_many_groups_are_parsed_in_linear_time(self):
        groups = 30_000
        pool = 12 + 8 * groups
        data = bytearray(struct.pack("<3I", 0, 1, pool))
        for i in range(groups):
            data += struct.pack("<2I", 1, pool + 2 * (i + 1))
        data += b"A\0" * (groups + 1)
        data += bytes(-len(data) % 16)
        started = time.monotonic()
        try:
            code, result = self.command("file", self.file(bytes(data)), timeout=4)
        except subprocess.TimeoutExpired:
            self.fail("parsing 30,000 groups did not finish within 4 seconds (quadratic?)")
        self.assertLess(time.monotonic() - started, 4)
        self.assertEqual(code, 1)  # the leading field was left at 0, so the new boundary check rejects it
        self.assertTrue(any("leading u32 0 differs" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_missing_input_is_incomplete(self):
        code, result = self.command("file", self.root / "absent.ps2")
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_corpus_real_integration(self):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus integration; absent corpus is `incomplete` for the milestone")
        code, result = self.command("corpus", GAME)
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"][:5])
        d = result["details"]
        self.assertEqual(d["models"], 56)
        self.assertEqual((d["leading_equals_pool_end"], d["zero_padding"]), (56, 56))


if __name__ == "__main__":
    unittest.main()
