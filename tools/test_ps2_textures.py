"""Tests for the .PS2 texture-library section: parser, decoder and the verify_textures CLI."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

import ps2_container
from evidence_common import Invalid

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games" / "ford-racing-2"


def a16(n):
    return (n + 15) & ~15


def tree(leading_pad=0):
    """Smallest valid name tree: pool 'A\\0B\\0' ends at 24, so the next section starts at 32."""
    return struct.pack("<5I", 24, 1, 20, 1, 22) + b"A\0B\0" + bytes(8 + leading_pad)


def tex_field(w, h):
    return ((w.bit_length() - 1) << 15) | ((h.bit_length() - 1) << 19)


def item(name, fmt, w, h, palette=0, mips=0, flags=0x100, pixels=None):
    return {"name": name, "fmt": fmt, "w": w, "h": h, "palette": palette, "mips": mips, "flags": flags, "pixels": pixels}


def plane(it, level):
    w, h = it["w"] >> level, it["h"] >> level
    size = {1: w * h * 4, 2: w * h * 2, 3: w * h, 4: w * h // 2}.get(it["fmt"], w * h)
    return it["pixels"][level] if it["pixels"] else bytes((i * 7 + level) & 0xFF for i in range(size))


def container(items, a=2, b=1, c=1, tail_count=3, clut_fill=None):
    """Tree + texture section + the next section's record count, in the layout the executable's parser reads."""
    out = bytearray(tree())
    total = a + b + c
    out += struct.pack("<3I", a, b, c) + bytes(12 * total)
    out += bytes(-len(out) % 16)
    blocks = [bytes([(i * 3 + 1) & 0xFF]) * 0x400 for i in range(a)] + [bytes(0x40)] * b + [bytes([(i + 9) & 0xFF]) * 0x400 for i in range(c)]
    if clut_fill:
        blocks = clut_fill
    for blk in blocks:
        out += blk
    out += struct.pack("<2I", len(items), 201)
    structs = []
    for it in items:
        name = it["name"].encode() + b"\0"
        out += struct.pack("<2I", it["flags"], len(name)) + name
        out += bytes(-len(out) % 16)
        st = bytearray(0x40)
        struct.pack_into("<I", st, 0, it["palette"])
        st[0x34], st[0x35] = it["fmt"], it["mips"]
        struct.pack_into("<Q", st, 0x38, tex_field(it["w"], it["h"]))
        out += st + bytes(0x10 * it["mips"])
        structs.append(it)
    for it in structs:
        for level in range(it["mips"] + 1):
            out += bytes(-len(out) % 16)
            out += plane(it, level)
    out += bytes(-len(out) % 16)
    out += struct.pack("<I", tail_count) + bytes(52 * tail_count)
    return bytes(out)


class Parser(unittest.TestCase):
    def test_walks_header_palettes_names_and_image_planes(self):
        its = [item("CAR_512", 3, 32, 16, palette=1), item("LAMP", 1, 8, 8, palette=0), item("MIPPED", 3, 16, 16, palette=2, mips=2)]
        data = container(its)
        result = ps2_container.parse(data)
        tex = result["textures"]
        self.assertEqual([t["name"] for t in tex["items"]], ["CAR_512", "LAMP", "MIPPED"])
        self.assertEqual((tex["palette_blocks"], tex["image_count"]), ((2, 1, 1), 3))
        first = tex["items"][0]
        self.assertEqual((first["format"], first["width"], first["height"], first["palette_index"]), (3, 32, 16, 1))
        self.assertEqual(len(tex["items"][2]["levels"]), 3)
        self.assertEqual([lv["size"] for lv in tex["items"][2]["levels"]], [256, 64, 16])
        self.assertEqual(result["next_section"]["record_count"], 3)
        self.assertEqual(result["next_section"]["offset"], tex["section_end"])
        self.assertEqual(result["next_section"]["offset"] % 16, 0)

    def test_image_planes_are_consecutive_and_aligned(self):
        data = container([item("A", 3, 16, 16), item("B", 1, 8, 8)])
        levels = [lv for t in ps2_container.parse(data)["textures"]["items"] for lv in t["levels"]]
        self.assertTrue(all(lv["offset"] % 16 == 0 for lv in levels))
        self.assertEqual(levels[1]["offset"], (levels[0]["offset"] + levels[0]["size"] + 15) & ~15)

    def test_decode_format3_applies_the_gs_block_layout_and_raw_palette(self):
        w = h = 16
        palette = b"".join(bytes([i, 255 - i, 7, 0x80]) for i in range(256))
        its = [item("P", 3, w, h, palette=0)]
        data = container(its, clut_fill=[palette, bytes(0x400), bytes(0x40), bytes(0x400)], a=2, b=1, c=1)
        item0 = ps2_container.parse(data)["textures"]["items"][0]
        rgba = ps2_container.decode_rgba(data, item0)
        self.assertEqual(len(rgba), w * h * 4)
        raw = data[item0["levels"][0]["offset"] : item0["levels"][0]["offset"] + w * h]
        # a known cell of the 8-bit block layout: pixel (0, 0) comes from byte 0 of the plane
        self.assertEqual(rgba[:4], palette[raw[0] * 4 : raw[0] * 4 + 4])
        self.assertEqual(sorted(raw), sorted(ps2_container.unswizzle8(raw, w, h)))  # a permutation, no data lost

    def test_decode_format1_is_linear_rgba(self):
        pixels = bytes(range(8 * 8 * 4))
        data = container([item("L", 1, 8, 8, pixels=[pixels])])
        item0 = ps2_container.parse(data)["textures"]["items"][0]
        self.assertEqual(ps2_container.decode_rgba(data, item0), pixels)

    def test_format4_pixels_are_not_decoded(self):
        data = container([item("N", 4, 16, 16)])
        item0 = ps2_container.parse(data)["textures"]["items"][0]
        with self.assertRaises(ps2_container.Unsupported):
            ps2_container.decode_rgba(data, item0)

    def test_truncated_inputs_are_rejected(self):
        good = container([item("A", 3, 16, 16)])
        for label, blob in (("inside the image data", good[: len(good) - 300]), ("inside the header", good[:40]), ("empty", b"")):
            with self.assertRaises(Invalid, msg=label):
                ps2_container.parse(blob)

    def test_palette_index_and_format_and_dimensions_are_validated(self):
        for label, bad in (
            ("palette index outside the table", item("A", 3, 16, 16, palette=99)),
            ("unknown format", item("A", 7, 16, 16)),
            ("image dimensions outside the profile", item("A", 3, 16384, 16)),
        ):
            with self.assertRaises(Invalid, msg=label):
                ps2_container.parse(container([bad]))

    def test_items_without_image_data_are_outside_the_measured_profile(self):
        with self.assertRaises(Invalid):
            ps2_container.parse(container([item("A", 3, 16, 16, flags=0x101)]))

    def test_hostile_counts_are_bounded(self):
        data = bytearray(container([item("A", 3, 16, 16)]))
        struct.pack_into("<I", data, 32, 0x7FFFFFFF)  # palette-block count
        with self.assertRaises(Invalid):
            ps2_container.parse(bytes(data))


    def test_mutated_and_truncated_containers_only_raise_invalid_or_unsupported(self):
        import random

        base = container([item("CAR", 3, 32, 16, palette=1), item("LAMP", 1, 8, 8), item("NET", 4, 16, 16, mips=1)])
        rng = random.Random(7)
        rejected = 0
        for n in range(400):
            data = bytearray(base)
            if n % 2:
                del data[rng.randrange(len(data)) :]
            else:
                for _ in range(rng.randint(1, 6)):
                    data[rng.randrange(len(data))] = rng.randrange(256)
            try:
                for it in ps2_container.parse(bytes(data))["textures"]["items"]:
                    try:
                        ps2_container.decode_rgba(bytes(data), it)
                    except ps2_container.Unsupported:
                        pass
            except Invalid:
                rejected += 1
        self.assertGreater(rejected, 100)  # the mutations are not all harmless


class Cli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def command(self, *args, timeout=None):
        out = self.root / "results"
        p = subprocess.run(
            [sys.executable, str(TOOLS / "verify_textures.py"), *map(str, args), "--output", str(out)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda r: r.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        self.assertTrue(reports[-1].with_name("report.md").exists())
        return p.returncode, json.loads(reports[-1].read_text())

    def write(self, data, name="m.ps2"):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_valid_file_reports_textures_hashes_and_unresolved_items(self):
        data = container([item("CAR", 3, 16, 16), item("LAMP", 1, 8, 8), item("NET", 4, 16, 16)])
        code, result = self.command("file", self.write(data))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        d = result["details"]
        self.assertEqual(d["texture_count"], 3)
        self.assertEqual(d["formats"], {"1": 1, "3": 1, "4": 1})
        decoded = {t["name"]: t for t in d["textures"]}
        self.assertEqual(len(decoded["CAR"]["rgba_sha256"]), 64)
        self.assertEqual(len(decoded["LAMP"]["rgba_sha256"]), 64)
        self.assertIn("not decoded", decoded["NET"]["decode"])
        self.assertTrue(any("4-bit" in u for u in d["unresolved"]), d["unresolved"])

    def test_malformed_file_fails_and_missing_is_incomplete(self):
        code, result = self.command("file", self.write(container([item("A", 3, 16, 16)])[:-300]))
        self.assertEqual((code, result["status"]), (1, "fail"))
        code, result = self.command("file", self.root / "absent.ps2")
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_corpus_real_integration(self):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus integration; absent corpus is `incomplete` for the milestone")
        code, result = self.command("corpus", GAME)
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"][:5])
        d = result["details"]
        self.assertEqual(d["models"], 56)
        self.assertEqual(d["formats"], {"1": 350, "3": 1551, "4": 469})
        self.assertEqual(d["texture_count"], 2370)
        self.assertEqual(d["next_section_records_fit"], 56)
        self.assertEqual(d["decoded_level0_images"], 1856)
        files = {f["path"]: f for f in d["file_results"]}
        undecoded = [t for f in files.values() for t in f["textures"] if "rgba_sha256" not in t and t["format"] in (1, 3)]
        self.assertEqual((len(undecoded), {t["format"] for t in undecoded}, all(min(t["width"], t["height"]) < 16 for t in undecoded)), (45, {3}, True))
        # Regression pins for two images checked by eye: the 1949 coupe body atlas and a wheel image.
        coupe = files["3DDATA/CARS/49COUPE.PS2;1"]["textures"][0]
        self.assertEqual((coupe["name"], coupe["width"], coupe["height"], coupe["format"]), ("COUPE49_512", 512, 256, 3))
        self.assertEqual(coupe["rgba_sha256"], "0c8c47244ab3f51de208a3a6334f305196a2c69803e7b8fc2d61240a71b9ea16")
        wheel = next(t for t in files["3DDATA/CARS/COBRA.PS2;1"]["textures"] if t["name"] == "COBRAWHEELBLUR")
        self.assertEqual((wheel["width"], wheel["height"], wheel["format"]), (64, 64, 1))
        self.assertEqual(wheel["rgba_sha256"], "70eac234489ce9166650f69bc926e0d7a612f724a0e120a551731fb83a324306")


if __name__ == "__main__":
    unittest.main()
