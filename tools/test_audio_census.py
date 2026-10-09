"""Corpus census guard for the audio bank/music-variant contract (issue #27, AC19).

Seam: the pinned census in notes/evidence/fr2-audio-contracts/variant-census.json
must equal an independent re-measurement of the unchanged PAL corpus. Every bank
pair, music pair, and playlist keeps its structural relations AND lands in
exactly one variant, so no audio file can disappear from coverage. EE registry
counts are re-checked against measured descriptor/line counts.

Skips cleanly when the local corpus is absent (public CI has no corpus).
"""

import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from audio_profile import (  # noqa: E402
    REGISTRY,
    classify_bank,
    classify_playlist,
    classify_stream,
    playlist_lines,
)
from corpus_binding import Baseline  # noqa: E402
from corpus_contract import corpus_identity  # noqa: E402
from format_contracts import bank  # noqa: E402
from verify_audio import end_blocks, terminator  # noqa: E402
import spu_adpcm as adpcm  # noqa: E402

CENSUS_PATH = REPO / "notes/evidence/fr2-audio-contracts/variant-census.json"
GAME = REPO / "games/ford-racing-2"


def check_bank_variant(msh: bytes, msb: bytes, path: str) -> str:
    """Independent variant decision from descriptor/flag measurements."""
    parsed = bank(msh, msb)
    kinds = set()
    for d in parsed["descriptors"]:
        span = msb[d["sample_span"][0] : d["sample_span"][1]]
        kind = terminator(span)
        assert kind is not None, f"{path}: span outside measured terminator classes"
        kinds.add(kind)
    assert len(kinds) == 1, f"{path}: mixed terminator classes {kinds}"
    return "speech-marker" if kinds == {"1,7"} else "loop-repeat"


class AudioCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            raise unittest.SkipTest("real corpus integration; absent corpus skips")
        cls.census = json.loads(CENSUS_PATH.read_text())
        cls.baseline = Baseline(GAME)

    def test_corpus_identity_matches_pin(self):
        self.assertEqual(
            corpus_identity(GAME)["corpus_id"],
            self.census["corpus_id"],
        )

    def test_every_bank_pair_lands_in_one_variant(self):
        pairs, unpaired = self.baseline.pairs(".msh;1", ".msb;1")
        self.assertEqual(unpaired, [])
        seen = {}
        for msh, msb in pairs:
            header, payload = msh.load(), msb.load()
            mine = check_bank_variant(header, payload, msb.path)
            theirs = classify_bank(header, payload)["variant"]
            self.assertEqual(mine, theirs, msb.path)
            seen[theirs] = seen.get(theirs, 0) + 1
        self.assertEqual(
            seen, {k: v["banks"] for k, v in self.census["variants"]["bank"].items()}
        )

    def test_every_stream_pair_lands_in_one_variant(self):
        pairs, unpaired = self.baseline.pairs(".mih;1", ".mib;1")
        self.assertEqual(unpaired, [])
        seen = {}
        for mih, mib in pairs:
            header, payload = mih.load(), mib.load()
            fields = adpcm.mih_fields(header)
            self.assertEqual(
                (fields["channels"], fields["interleave"]), (2, 32768), mib.path
            )
            streams = adpcm.deinterleave(payload, 2, 32768)
            for stream in streams:
                self.assertEqual(end_blocks(stream), [], mib.path)
            theirs = classify_stream(header, payload)["variant"]
            self.assertEqual(theirs, "stereo-32k")
            seen[theirs] = seen.get(theirs, 0) + 1
        self.assertEqual(
            seen,
            {k: v["streams"] for k, v in self.census["variants"]["stream"].items()},
        )

    def test_every_playlist_resolves_and_counts_match(self):
        playlists = self.baseline.entries(".mbf;1") + self.baseline.entries(".sbf;1")
        self.assertEqual(len(playlists), 6)
        stems = {
            e.path.rsplit("/", 1)[-1].split(".")[0].lower()
            for e in self.baseline.entries(".mih;1")
        }
        lines_total = 0
        for entry in playlists:
            lines = playlist_lines(entry.load())
            self.assertGreater(lines, [])
            lines_total += len(lines)
            variant = classify_playlist(entry.load(), entry.name)["variant"]
            self.assertEqual(
                variant,
                "music-list" if entry.name.endswith(".mbf;1") else "speech-list",
                entry.path,
            )
            if entry.name.endswith(".mbf;1"):
                for line in lines:
                    self.assertIn(line.rsplit("\\", 1)[-1].lower(), stems, entry.path)
        pinned = self.census["variants"]["playlist"]
        self.assertEqual(lines_total, sum(v["lines"] for v in pinned.values()))

    def test_registry_counts_match_measured_corpus(self):
        bank_pairs, _ = self.baseline.pairs(".msh;1", ".msb;1")
        measured = {}
        for msh, msb in bank_pairs:
            stem = msb.name.split(".")[0].lower()
            measured[stem] = bank(msh.load(), msb.load())["count"]
        for stem, record in REGISTRY["banks"].items():
            self.assertEqual(measured.get(stem), record["count"], stem)
        playlists = {
            e.name.split(".")[0].lower(): e for e in self.baseline.entries(".mbf;1")
        }
        for stem, record in REGISTRY["music"].items():
            self.assertEqual(
                len(playlist_lines(playlists[stem].load())), record["count"], stem
            )
        sbf = self.baseline.entries(".sbf;1")[0]
        self.assertEqual(len(playlist_lines(sbf.load())), REGISTRY["speech"]["count"])

    def test_pinned_tool_sources_match(self):
        for name, pinned in self.census["tool_sources"].items():
            import hashlib

            self.assertEqual(
                hashlib.sha256((TOOLS / name).read_bytes()).hexdigest(), pinned, name
            )


if __name__ == "__main__":
    unittest.main()
