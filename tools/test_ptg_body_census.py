"""Corpus census guard for the PTG body-variant contract (issue #28, AC20).

Seam: the pinned census in notes/evidence/fr2-ptg-body-contracts/variant-census.json
must equal an independent re-measurement of the unchanged PAL corpus. Every .ptg
file keeps its header relations AND lands in exactly one body variant, so no
header-only file can disappear from coverage. Gear sprite pins (gear0=R, gear1=N)
are re-checked through format_contracts.sprite().

Skips cleanly when the local corpus is absent (public CI has no corpus).
"""

import json
import struct
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from corpus_binding import Baseline  # noqa: E402
from corpus_contract import corpus_identity  # noqa: E402
from format_contracts import sprite  # noqa: E402
from ptg_profile import DD, classify, f32_bits  # noqa: E402

CENSUS_PATH = REPO / "notes/evidence/fr2-ptg-body-contracts/variant-census.json"
GAME = REPO / "games/ford-racing-2"

PAD_WORDS = (2, 3, 4, 5, 6, 7, 8, 9, 11, 15)


def tiled_variant(data: bytes, header: dict) -> str:
    """Independent variant decision from measured spans and descriptor words."""
    count, cell = header["count"], header["cell"]
    base, pixels = 80 + 16 * count, 80 + 80 * count
    if len(data) < pixels:
        raise AssertionError(f"truncated tiled body: {len(data)} < {pixels}")
    word0 = struct.unpack_from("<I", data, base)[0]
    word12 = struct.unpack_from("<I", data, base + 48)[0]
    pixel_bytes = len(data) - pixels
    nonzero = word0 != 0
    if (
        cell == 32
        and not nonzero
        and word12 == 0xD0410010
        and pixel_bytes == 4096 * count
    ):
        return "tiled4096"
    if (
        cell == 32
        and nonzero
        and word12 == 0xD0820004
        and pixel_bytes == 1024 * count + 1040
    ):
        return "tiled1024"
    if (
        cell == 16
        and not nonzero
        and word12 == 0xD0410004
        and pixel_bytes == 1024 * count
    ):
        return "tiled1024c16"
    if (
        cell == 16
        and nonzero
        and word12 == 0xD0820001
        and pixel_bytes == 256 * count + 1040
    ):
        return "tiled256"
    if (
        cell == 16
        and not nonzero
        and word12 == 0xD0410002
        and pixel_bytes == 512 * count
    ):
        return "barsub512"
    raise AssertionError(
        f"no variant: cell={cell} word0={word0:#x} word12={word12:#x} pixel_bytes={pixel_bytes}"
    )


def check_tiled_skeleton(data: bytes, header: dict, path: str) -> None:
    """Universal skeleton shared by all 532 non-sprite files."""
    count, columns, cell = header["count"], header["columns"], header["cell"]
    width, height = header["width"], header["height"]
    prefix = struct.unpack_from("<12I", data, 32)
    for index, word in enumerate(prefix):
        if index == 9:
            continue
        assert word == DD, f"{path}: prefix word {index} is not 0xDDDDDDDD"
    assert prefix[9] % 16 == 0 and prefix[9] >= len(data), (
        f"{path}: prefix address out of bounds"
    )
    base = 80 + 16 * count
    constants = None
    for tile in range(count):
        extent_u, extent_v, pointer, pad = struct.unpack_from(
            "<4I", data, 80 + 16 * tile
        )
        want_u = f32_bits(min(cell, width - (tile % columns) * cell) / cell)
        want_v = f32_bits(min(cell, height - (tile // columns) * cell) / cell)
        assert (extent_u, extent_v) == (want_u, want_v), f"{path}: tile {tile} extent"
        assert pad == DD, f"{path}: tile {tile} record pad"
        assert pointer % 16 == 0 and pointer >= len(data), (
            f"{path}: tile {tile} pointer"
        )
        words = struct.unpack_from("<16I", data, base + 64 * tile)
        assert all(words[j] == DD for j in PAD_WORDS), (
            f"{path}: descriptor {tile} padding"
        )
        assert words[1] == 0, f"{path}: descriptor {tile} word1"
        address = words[10]
        assert address % 16 == 0 and address >= len(data), (
            f"{path}: descriptor {tile} address"
        )
        current = (words[0], words[1], words[12], words[13], words[14])
        if constants is None:
            constants = current
        assert current == constants, f"{path}: descriptor {tile} constancy"
    word0 = struct.unpack_from("<I", data, base)[0]
    if word0:
        assert word0 % 16 == 0 and word0 >= len(data), f"{path}: descriptor word0"


class PtgBodyCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (GAME / "extracted" / "FILES.HDR").is_file():
            raise unittest.SkipTest("local PAL corpus is absent")
        cls.census = json.loads(CENSUS_PATH.read_bytes())
        cls.baseline = Baseline(GAME)

    def test_pins_match_tool_sources(self):
        tools = self.census["tool_sources"]
        import hashlib

        for name, pinned in tools.items():
            observed = hashlib.sha256((TOOLS / name).read_bytes()).hexdigest()
            self.assertEqual(observed, pinned, name)

    def test_every_file_has_header_and_variant(self):
        entries = self.baseline.entries(".ptg;1")
        self.assertEqual(len(entries), self.census["files"])
        counts = dict.fromkeys(self.census["variants"], 0)
        for entry in entries:
            data = entry.load()
            result = classify(data)  # header relations raise on violation
            header = result["header"]
            if result["profile"] == "sprite":
                variant = "sprite"
                parsed = sprite(data)
                self.assertEqual(parsed["width"], header["width"])
                self.assertEqual(parsed["height"], header["height"])
            else:
                check_tiled_skeleton(data, header, entry.path)
                variant = tiled_variant(data, header)
            counts[variant] += 1
        for variant, expected in self.census["variants"].items():
            self.assertEqual(counts[variant], expected["files"], variant)
        # No header-only disappearances: every file is counted exactly once.
        self.assertEqual(sum(counts.values()), self.census["files"])

    def test_descriptor_words_match_pins(self):
        entries = self.baseline.entries(".ptg;1")
        for entry in entries:
            data = entry.load()
            result = classify(data)
            if result["profile"] == "sprite":
                continue
            count = result["header"]["count"]
            base = 80 + 16 * count
            words = struct.unpack_from("<16I", data, base)
            variant = tiled_variant(data, result["header"])
            pinned = self.census["variants"][variant]
            self.assertEqual(
                f"{words[12]:08x}", pinned["descriptor_word12"], entry.path
            )
            self.assertEqual(
                f"{words[13]:08x}", pinned["descriptor_word13"], entry.path
            )
            self.assertEqual(
                f"{words[14]:08x}", pinned["descriptor_word14"], entry.path
            )
            self.assertEqual(
                words[0] != 0, pinned["descriptor_word0_nonzero"], entry.path
            )

    def test_gear_sprite_regressions(self):
        gears = json.loads((TOOLS / "gear_pixels.json").read_text())
        by_name = {entry.name: entry for entry in self.baseline.entries(".ptg;1")}
        self.assertEqual(
            {name for name in by_name if name in gears},
            set(gears),
            "all gear files present",
        )
        for name, expected in gears.items():
            parsed = sprite(by_name[name].load())
            for key in ("width", "height", "pixel_sha256"):
                self.assertEqual(parsed[key], expected[key], f"{name}:{key}")
        self.assertEqual(gears["gear0.ptg;1"]["meaning"], "uppercase R")
        self.assertEqual(gears["gear1.ptg;1"]["meaning"], "uppercase N")
        self.assertEqual(
            corpus_identity(GAME)["profile"], self.census["corpus_profile"]
        )


if __name__ == "__main__":
    unittest.main()
