"""Tests at the verify_audio.py CLI boundary and the spu_adpcm public functions."""

import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

import spu_adpcm

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games" / "ford-racing-2"


def block(head=0x0C, flags=0, fill=0x11):
    return bytes([head, flags]) + bytes([fill]) * 14


def sample(blocks=3, tail_flags=3):
    """Zero first block, data blocks, flagged final block: the structure seen in the corpus."""
    body = [bytes(16)] + [block() for _ in range(blocks - 2)] + [block(flags=tail_flags)]
    return b"".join(body)


def marker_sample(blocks=5):
    """Zero first block, data, a flag-1 block, then the flag-7 end marker with 0x77 filler."""
    body = [bytes(16)] + [block() for _ in range(blocks - 3)] + [block(flags=1), bytes([0, 7]) + bytes([0x77]) * 14]
    return b"".join(body)


def bank_files(samples, rate=22050):
    descriptors, start = b"", 0
    for s in samples:
        descriptors += struct.pack("<IIII", len(s), 0, start, rate)
        start += len(s)
    size = 12 + len(descriptors)
    return struct.pack("<III", size, 36, len(samples)) + descriptors, b"".join(samples)


def mih(channels=2, interleave=32, turns=2):
    words = [64, 1234, channels, 44100, interleave, turns] + [0] * 10
    return struct.pack("<16I", *words)


class AudioVerifier(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def command(self, *args, env=None):
        out = self.root / "results"
        p = subprocess.run(
            [sys.executable, str(TOOLS / "verify_audio.py"), *map(str, args), "--output", str(out)],
            capture_output=True,
            text=True,
            env=env,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda r: r.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        self.assertTrue(reports[-1].with_name("report.md").exists())
        return p.returncode, json.loads(reports[-1].read_text())

    def bank(self, samples):
        msh, msb = bank_files(samples)
        return self.write("b.msh", msh), self.write("b.msb", msb)

    def test_valid_bank_passes_and_reports_each_span(self):
        code, result = self.command("bank", *self.bank([sample(4), marker_sample(6)]))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        spans = result["details"]["descriptors"]
        self.assertEqual([s["blocks"] for s in spans], [4, 6])
        self.assertEqual([s["last_flags"] for s in spans], [3, 7])
        self.assertEqual([s["terminator"] for s in spans], ["3", "1,7"])
        self.assertTrue(all(len(s["pcm_sha256"]) == 64 for s in spans))
        self.assertIn("no playback", result["details"]["claim_limits"])

    def test_invalid_filter_nibble_fails(self):
        bad = sample(4)[:16] + block(head=0x5C) + sample(4)[32:]
        code, result = self.command("bank", *self.bank([bad]))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("filter" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_span_without_end_flag_fails(self):
        code, result = self.command("bank", *self.bank([sample(4, tail_flags=0)]))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("end flag" in d for d in result["diagnostics"]))

    def test_end_flags_outside_the_measured_classes_fail(self):
        mid = bytearray(sample(6))
        mid[16 * 2 + 1] = 1  # end flag on a middle block
        lone7 = sample(4, tail_flags=7)  # final flag 7 without a preceding flag-1 block
        lone1 = sample(4, tail_flags=1)
        bad_filler = bytearray(marker_sample(6))
        bad_filler[-1] = 0x00  # marker data is no longer the constant 0x77 filler
        for label, span in (("mid", bytes(mid)), ("lone7", lone7), ("lone1", lone1), ("filler", bytes(bad_filler))):
            code, result = self.command("bank", *self.bank([span]))
            self.assertEqual((code, result["status"]), (1, "fail"), label)
            self.assertTrue(any("measured terminator classes" in d for d in result["diagnostics"]), (label, result["diagnostics"]))
        self.assertTrue(any("end bits at blocks" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_span_above_the_decode_bound_is_checked_but_decoding_is_skipped_visibly(self):
        blocks = spu_adpcm.MAX_DECODE_BYTES // 16 + 1
        big = bytes(16) + block() * (blocks - 2) + block(flags=3)
        code, result = self.command("bank", *self.bank([big]))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        span = result["details"]["descriptors"][0]
        self.assertIn("decode bound", span["decode_skipped"])
        self.assertEqual(result["details"]["decode_skipped_spans"], 1)
        self.assertNotIn("pcm_sha256", span)

    def test_hostile_stream_headers_fail_cleanly(self):
        cases = (
            (5_000_000, 32, b"", "stream parameters"),
            (0, 32, block() * 4, "stream parameters"),
            (2, 0, block() * 4, "stream parameters"),
            (2, 24, block() * 4, "stream parameters"),
            (2, 32, b"", "empty payload"),
        )
        for channels, interleave, payload, wanted in cases:
            header = struct.pack("<16I", 64, 0, channels, 44100, interleave, 1, *([0] * 10))
            code, result = self.command("stream", self.write("h.mih", header), self.write("h.mib", payload))
            self.assertEqual((code, result["status"]), (1, "fail"), (channels, interleave))
            self.assertTrue(any(wanted in d for d in result["diagnostics"]), (channels, interleave, result["diagnostics"]))
            self.assertFalse(any("not whole interleave turns: channel" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_oracle_disagreement_fails(self):
        fake = self.root / "bin"
        fake.mkdir()
        script = fake / "ffmpeg"
        script.write_text(
            f"#!{sys.executable}\nimport sys\n"
            "if '-version' in sys.argv:\n    print('ffmpeg version fake'); raise SystemExit(0)\n"
            "sys.stdout.buffer.write((1).to_bytes(2, 'little', signed=True) * 28 * 3)\n"
        )
        script.chmod(0o755)
        code, result = self.command("bank", *self.bank([sample(4)]), "--oracle", "ffmpeg", env={"PATH": str(fake)})
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("differs from ffmpeg" in d for d in result["diagnostics"]), result["diagnostics"])
        self.assertEqual(result["details"]["oracle"]["exact_equal"], 0)

    def test_span_not_multiple_of_block_fails(self):
        code, result = self.command("bank", *self.bank([sample(4) + b"\0" * 5]))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("multiple of 16" in d for d in result["diagnostics"]))

    def test_non_adpcm_payload_is_rejected_with_violation_rate(self):
        noise = bytes((i * 37 + 11) & 0xFF for i in range(16 * 64))
        code, result = self.command("bank", *self.bank([noise]))
        self.assertEqual((code, result["status"]), (1, "fail"))

    def test_stream_two_channels_matches_interleave_turn_count(self):
        # two turns of 32 bytes per channel: channel 0 then channel 1 within each turn
        data = (bytes(16) + block()) * 2 + (block() + block()) * 2
        self.assertEqual(len(data), 128)
        code, result = self.command("stream", self.write("m.mih", mih(turns=2)), self.write("m.mib", data))
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        self.assertEqual(result["details"]["turns"], 2)
        self.assertEqual(result["details"]["channel_blocks"], [4, 4])

    def test_stream_turn_count_mismatch_fails(self):
        data = (bytes(16) + block()) * 2 + (block() + block()) * 2
        code, result = self.command("stream", self.write("m.mih", mih(turns=3)), self.write("m.mib", data))
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("turn count" in d for d in result["diagnostics"]))

    def test_stream_partial_final_turn_fails(self):
        data = (bytes(16) + block()) * 2 + (block() + block()) * 2 + b"\0" * 16
        code, result = self.command("stream", self.write("m.mih", mih(turns=2)), self.write("m.mib", data))
        self.assertEqual((code, result["status"]), (1, "fail"))

    def test_bank_oracle_requires_exact_ffmpeg_agreement(self):
        if shutil.which("ffmpeg") is None:
            self.skipTest("ffmpeg adpcm_psx oracle unavailable")
        spans = [sample(6, tail_flags=3), bytes(16) + block(head=0x3A) * 4 + block(flags=1) + bytes([0, 7]) + bytes([0x77]) * 14]
        code, result = self.command("bank", *self.bank(spans), "--oracle", "ffmpeg")
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        oracle = result["details"]["oracle"]
        self.assertEqual((oracle["tool"], oracle["spans_compared"], oracle["exact_equal"]), ("ffmpeg", 2, 2))
        self.assertTrue(oracle["version"].startswith("ffmpeg version"))

    def test_oracle_unavailable_is_incomplete_not_pass(self):
        env = {"PATH": str(self.root)}  # no ffmpeg reachable
        code, result = self.command("bank", *self.bank([sample(4)]), "--oracle", "ffmpeg", env=env)
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        self.assertTrue(any("ffmpeg" in d for d in result["diagnostics"]))

    def test_oversized_input_is_rejected(self):
        msh, _ = bank_files([sample(4)])
        huge = self.root / "huge.msb"
        with huge.open("wb") as stream:  # sparse: occupies no real disk space
            stream.truncate(spu_adpcm.MAX_BYTES + 1)
        code, result = self.command("bank", self.write("b.msh", msh), huge)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("exceeds" in d for d in result["diagnostics"]), result["diagnostics"])

    def test_missing_input_is_incomplete(self):
        code, result = self.command("stream", self.root / "absent.mih", self.root / "absent.mib")
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_corpus_audio_real_integration(self):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus integration; absent corpus is `incomplete` for the milestone")
        args = ["--oracle", "ffmpeg"] if shutil.which("ffmpeg") else []
        code, result = self.command("corpus", GAME, *args)
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])
        details = result["details"]
        if args:
            self.assertEqual(details["oracle"]["spans_compared"], 305)
            self.assertEqual(details["oracle"]["exact_equal"], 305)
            self.assertEqual(details["oracle"]["music_excerpts_compared"], details["oracle"]["music_excerpts_equal"])
        self.assertEqual((details["banks"], details["bank_descriptors"], details["streams"]), (27, 305, 20))
        self.assertEqual(details["terminator_classes"], {"3": 206, "1,7": 99})


def ffmpeg_decode(blob, rate=22050):
    """Independent software oracle: ffmpeg adpcm_psx through a VAGp container; None if unavailable."""
    if shutil.which("ffmpeg") is None:
        return None
    head = b"VAGp" + struct.pack(">II", 3, 0) + struct.pack(">II", len(blob), rate) + bytes(12) + b"oracle".ljust(16, b"\0")
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "x.vag"
        path.write_bytes(head + blob)
        out = subprocess.run(
            ["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-f", "s16le", "-acodec", "pcm_s16le", "-"],
            capture_output=True,
        )
    return list(struct.unpack(f"<{len(out.stdout) // 2}h", out.stdout)) if out.returncode == 0 else None


class SpuAdpcm(unittest.TestCase):
    def test_matches_ffmpeg_on_every_filter_and_shift(self):
        blob = bytearray(bytes(16))
        for filt in range(5):
            for shift in range(13):
                payload = bytes((i * 29 + filt * 7 + shift * 3 + 5) & 0xFF for i in range(14))
                blob += bytes([filt << 4 | shift, 0]) + payload
        blob += bytes([0, 3]) + bytes(14)
        expected = ffmpeg_decode(bytes(blob))
        if expected is None:
            self.skipTest("ffmpeg adpcm_psx oracle unavailable")
        self.assertEqual(spu_adpcm.decode(bytes(blob)), expected)

    def test_matches_ffmpeg_on_the_flag7_end_marker(self):
        blob = bytes(16) + block(head=0x2C) + block(flags=1, head=0x1C) + bytes([0, 7]) + bytes([0x77]) * 14
        expected = ffmpeg_decode(blob)
        if expected is None:
            self.skipTest("ffmpeg adpcm_psx oracle unavailable")
        self.assertEqual(spu_adpcm.decode(blob), expected)

    def test_zero_blocks_decode_to_silence(self):
        self.assertEqual(spu_adpcm.decode(bytes(32)), [0] * 56)

    def test_known_vector_filter0_shift12(self):
        pcm = spu_adpcm.decode(bytes([0x0C, 0]) + bytes([0x21]) + bytes(13))
        self.assertEqual(pcm[:3], [1, 2, 0])

    def test_filter1_feedback_truncates_toward_zero_without_rounding_term(self):
        # nibble 4 -> 4; next sample is 0 + int(4 * 60 / 64) = 3 (floor+32 rounding would give 4)
        pcm = spu_adpcm.decode(bytes([0x1C, 0, 0x04]) + bytes(13))
        self.assertEqual(pcm[:2], [4, 3])
        # nibble 0xC = -4 -> -4; next is int(-4 * 60 / 64) = -3 (floor would give -4)
        pcm = spu_adpcm.decode(bytes([0x1C, 0, 0x0C]) + bytes(13))
        self.assertEqual(pcm[:2], [-4, -3])

    def test_flag7_end_marker_block_decodes_to_silence(self):
        marker = bytes([0x00, 0x07]) + bytes([0x77]) * 14
        self.assertEqual(spu_adpcm.decode(bytes(16) + marker), [0] * 56)

    def test_output_is_clamped_to_int16(self):
        pcm = spu_adpcm.decode(bytes([0x00, 0, 0x07]) + bytes(13))
        self.assertEqual(pcm[0], 7 << 12)
        pcm = spu_adpcm.decode(bytes([0x40, 0]) + bytes([0x77] * 14))
        self.assertTrue(all(-32768 <= v <= 32767 for v in pcm))

    def test_rejects_unaligned_empty_and_invalid(self):
        for blob in (b"", bytes(15), bytes([0x50, 0]) + bytes(14)):
            with self.assertRaises(spu_adpcm.AdpcmError):
                spu_adpcm.decode(blob)

    def test_deinterleave_rejects_empty_payload_and_unbounded_channels(self):
        with self.assertRaises(spu_adpcm.AdpcmError):
            spu_adpcm.deinterleave(b"", 2, 16)
        with self.assertRaises(spu_adpcm.AdpcmError):
            spu_adpcm.deinterleave(bytes(32), spu_adpcm.MAX_CHANNELS + 1, 16)

    def test_deinterleave_splits_channels_by_turn(self):
        a, b = bytes([1]) * 16, bytes([2]) * 16
        self.assertEqual(spu_adpcm.deinterleave(a + b + a + b, 2, 16), [a + a, b + b])
        with self.assertRaises(spu_adpcm.AdpcmError):
            spu_adpcm.deinterleave(a + b + a, 2, 16)
        with self.assertRaises(spu_adpcm.AdpcmError):
            spu_adpcm.deinterleave(a + b, 2, 24)


if __name__ == "__main__":
    unittest.main()
