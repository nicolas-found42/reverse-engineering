"""Tests at the verify_ptg.py CLI boundary; the real-corpus case skips when the corpus is absent."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games" / "ford-racing-2"
DD = 0xDDDDDDDD
F32 = lambda v: struct.unpack("<I", struct.pack("<f", v))[0]  # noqa: E731


def tiled_dd(width=80, height=40, cell=32, **overrides):
    """A synthetic file with the measured 0xDDDDDDDD-trailer layout."""
    cols, rows = -(-width // cell), -(-height // cell)
    count = cols * rows
    out = bytearray(struct.pack("<8I", count, cols, rows, cell, cell, width, height, DD))
    out += bytes([0xAA]) * 48
    for i in range(count):
        fu = min(cell, width - (i % cols) * cell) / cell
        fv = min(cell, height - (i // cols) * cell) / cell
        out += struct.pack("<IIII", F32(fu), F32(fv), 0x07C00000 + i * 0x1000, DD)
    for i in range(count):
        out += struct.pack("<16I", 0x01C905E0, 0, *([DD] * 8), 0x08020000 + i, DD, 0xD0820004, 0xDDDDDD03, 0xAAAA8C45, DD)
    out += bytes((i * 7 + 3) & 0xFF for i in range(count * 1024))
    out += bytes([0xFE]) * 1040
    data = bytearray(out)
    for name, value in overrides.items():
        offset = {"count": 0, "cols": 4, "rows": 8, "last": 28}[name]
        data[offset : offset + 4] = struct.pack("<I", value)
    return bytes(data)


class PtgVerifier(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def command(self, *args):
        out = self.root / "results"
        p = subprocess.run(
            [sys.executable, str(TOOLS / "verify_ptg.py"), *map(str, args), "--output", str(out)],
            capture_output=True,
            text=True,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda r: r.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        self.assertTrue(reports[-1].with_name("report.md").exists())
        return p.returncode, json.loads(reports[-1].read_text())

    def file(self, data, name="t.ptg"):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_valid_tiled_file_reports_profile_and_unresolved_semantics(self):
        code, result = self.command("file", self.file(tiled_dd()))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        details = result["details"]
        self.assertEqual(details["profile"], "tiled_dd")
        self.assertEqual((details["tiles"]["columns"], details["tiles"]["rows"], details["tiles"]["count"]), (3, 2, 6))
        self.assertEqual(details["tiles"]["order"], "row-major")
        self.assertEqual(len(details["pixel_sha256"]), 64)
        self.assertEqual(details["pointer_values_within_file"], False)
        for topic in ("palette", "tile pointer values", "descriptor words"):
            self.assertTrue(any(topic in u for u in details["unresolved"]), details["unresolved"])

    def test_tile_extent_floats_follow_row_major_position(self):
        data = bytearray(tiled_dd())
        # swap the extents of tile 0 (full) and tile 2 (right edge, half width): row-major position is violated
        a, b = bytes(data[80:88]), bytes(data[112:120])
        data[80:88], data[112:120] = b, a
        code, result = self.command("file", self.file(bytes(data)))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("tile 0" in d and "extent" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_header_relations_are_enforced(self):
        for overrides, text in (
            ({"count": 7}, "count"),
            ({"cols": 4}, "columns"),
            ({"rows": 3}, "rows"),
        ):
            code, result = self.command("file", self.file(tiled_dd(**overrides)))
            self.assertEqual((code, result["status"]), (1, "fail"), overrides)
            self.assertTrue(any(text in d for d in result["diagnostics"]), (overrides, result["diagnostics"]))

    def test_size_model_is_exact(self):
        for data in (tiled_dd() + b"\0", tiled_dd()[:-16]):
            code, result = self.command("file", self.file(data))
            self.assertEqual((code, result["status"]), (1, "fail"))
            self.assertTrue(any("1120 + 1104" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_descriptor_padding_and_constancy_are_enforced(self):
        count = 6
        base = 80 + 16 * count
        broken = bytearray(tiled_dd())
        broken[base + 64 * 2 + 8] = 0x00  # a word that must be 0xDDDDDDDD
        code, result = self.command("file", self.file(bytes(broken)))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("descriptor 2" in d for d in result["diagnostics"]), result["diagnostics"])
        varying = bytearray(tiled_dd())
        varying[base + 64 * 4 + 48] ^= 0x01  # word 12 differs in one tile
        code, result = self.command("file", self.file(bytes(varying)))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("not constant" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_truncated_and_oversized_inputs_fail(self):
        code, result = self.command("file", self.file(b"\0" * 20))
        self.assertEqual((code, result["status"]), (1, "fail"))
        big = self.root / "big.ptg"
        with big.open("wb") as stream:
            stream.truncate(128 * 1024 * 1024 + 1)
        code, result = self.command("file", big)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("exceeds" in d for d in result["diagnostics"]))

    def test_multi_tile_files_outside_the_measured_profile_are_header_only(self):
        header = struct.pack("<8I", 6, 3, 2, 32, 32, 74, 60, 1) + bytes(200)
        code, result = self.command("file", self.file(header))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        self.assertEqual(result["details"]["profile"], "tiled_header_only")
        self.assertTrue(any("layout" in u for u in result["details"]["unresolved"]))

    def test_single_tile_file_outside_the_sprite_contract_is_incomplete_in_file_mode(self):
        header = struct.pack("<8I", 1, 1, 1, 32, 32, 28, 28, 1) + bytes(300)
        code, result = self.command("file", self.file(header))
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        self.assertTrue(any("sprite" in d for d in result["diagnostics"]), result["diagnostics"])
        self.assertEqual(result["details"]["profile"], "single_unsupported")

    def test_missing_input_is_incomplete(self):
        code, result = self.command("file", self.root / "absent.ptg")
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_corpus_real_integration(self):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus integration; absent corpus is `incomplete` for the milestone")
        code, result = self.command("corpus", GAME)
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"][:5])
        details = result["details"]
        self.assertEqual(details["files"], 548)
        self.assertEqual(
            details["profiles"],
            {"sprite": 16, "single_unsupported": 24, "tiled_dd": 17, "tiled_header_only": 491},
        )
        self.assertEqual(details["header_relation_violations"], 0)


if __name__ == "__main__":
    unittest.main()
