#!/usr/bin/env python3
"""Independent FR2 audio structure check; exits 0=pass, 1=fail, 2=incomplete.

Separate from verify_formats.py: it checks that bank sample spans and music streams obey the
hardware ADPCM block structure and that a reference decoder yields sane PCM. It makes no
playback or in-game correctness claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

import spu_adpcm as adpcm
from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result
from format_contracts import bank

CLAIM_LIMITS = (
    "Structure and reference-decoder sanity only; no playback, loop-behavior or in-game "
    "correctness claim. Samples are hashed as little-endian int16."
)
MUSIC_DECODE_BLOCKS = 8192  # bounded excerpt decoded per music channel


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size > adpcm.MAX_BYTES:
        raise Invalid(f"{path.name}: {size} bytes exceeds the {adpcm.MAX_BYTES} byte processing bound")
    return path.read_bytes()


class FfmpegOracle:
    """Independent software decoder (ffmpeg adpcm_psx via a VAGp container); not a hardware oracle."""

    def __init__(self):
        exe = shutil.which("ffmpeg")
        if exe is None:
            raise Incomplete("--oracle ffmpeg requested but ffmpeg is not on PATH")
        self.exe: str = exe
        banner = subprocess.run([self.exe, "-version"], capture_output=True, text=True).stdout
        self.version = banner.splitlines()[0] if banner else "unknown"
        self.counts = {"span": [0, 0], "music": [0, 0]}  # [compared, equal]
        self.mismatches: list[str] = []
        self.skipped: list[str] = []

    def decode(self, blob: bytes, rate: int) -> list[int]:
        head = (
            b"VAGp" + struct.pack(">II", 3, 0) + struct.pack(">II", len(blob), rate or 22050)
            + bytes(12) + b"oracle".ljust(16, b"\0")
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "span.vag"
            path.write_bytes(head + blob)
            try:
                run = subprocess.run(
                    [self.exe, "-v", "error", "-nostdin", "-i", str(path), "-f", "s16le", "-acodec", "pcm_s16le", "-"],
                    capture_output=True,
                    timeout=60,
                )
            except subprocess.TimeoutExpired as exc:
                raise Invalid("ffmpeg did not finish decoding a span within 60 seconds") from exc
        if run.returncode:
            raise Invalid(f"ffmpeg could not decode the span: {run.stderr.decode(errors='replace')[:200]}")
        return list(struct.unpack(f"<{len(run.stdout) // 2}h", run.stdout))

    def compare(self, kind: str, label: str, blob: bytes, rate: int, mine: list[int]):
        self.counts[kind][0] += 1
        theirs = self.decode(blob, rate)
        if mine == theirs:
            self.counts[kind][1] += 1
        else:
            first = next((k for k, (a, b) in enumerate(zip(mine, theirs)) if a != b), min(len(mine), len(theirs)))
            self.mismatches.append(f"{label}: differs from ffmpeg (first difference at sample {first}; lengths {len(mine)}/{len(theirs)})")

    def summary(self) -> dict:
        return {
            "tool": "ffmpeg",
            "version": self.version,
            "spans_compared": self.counts["span"][0],
            "exact_equal": self.counts["span"][1],
            "music_excerpts_compared": self.counts["music"][0],
            "music_excerpts_equal": self.counts["music"][1],
            "spans_skipped_over_decode_bound": self.skipped,
        }

    def finish(self, details: dict) -> dict:
        details["oracle"] = self.summary()
        details["failures"] = [*details["failures"], *self.mismatches]
        return details


def pcm_digest(samples: list[int]) -> str:
    return sha256(b"".join(v.to_bytes(2, "little", signed=True) for v in samples))


def violations(s: adpcm.Structure) -> list[str]:
    found = []
    if s.invalid_filter:
        found.append(f"{s.invalid_filter} of {s.blocks} blocks have a filter nibble above 4")
    if s.invalid_shift:
        found.append(f"{s.invalid_shift} of {s.blocks} blocks have a shift above 12")
    if s.invalid_flags:
        found.append(f"{s.invalid_flags} of {s.blocks} blocks have flag bits above 7")
    return found


MARKER_FILLER = bytes([0x77]) * 14


def end_blocks(span: bytes) -> list[int]:
    return [i for i in range(len(span) // adpcm.BLOCK) if span[i * adpcm.BLOCK + 1] & adpcm.FLAG_END]


def terminator(span: bytes) -> str | None:
    """The measured terminator class, or None. Only these two classes occur in the corpus:
    a single final end-bit block flagged 3, or a flag-1 block followed by a flag-7 end marker with 0x77 filler."""
    blocks = len(span) // adpcm.BLOCK
    flags = [span[i * adpcm.BLOCK + 1] for i in range(blocks)]
    ends = end_blocks(span)
    if ends == [blocks - 1] and flags[-1] == 3:
        return "3"
    if blocks >= 2 and ends == [blocks - 2, blocks - 1] and flags[-2:] == [1, 7] and span[-14:] == MARKER_FILLER:
        return "1,7"
    return None


def check_bank(msh: bytes, msb: bytes, oracle: FfmpegOracle | None = None, label: str = "") -> dict:
    parsed = bank(msh, msb)
    failures, spans = [], []
    for i, d in enumerate(parsed["descriptors"]):
        start, end = d["sample_span"]
        span = msb[start:end]
        try:
            s = adpcm.structure(span)
        except adpcm.AdpcmError as exc:
            failures.append(f"descriptor {i}: sample span length {len(span)}: {exc} (multiple of 16 required)")
            continue
        problems = violations(s)
        kind = terminator(span)
        if kind is None:
            problems.append(
                f"end flags outside the measured terminator classes (final flag 3, or a flag-1 block then a flag-7 "
                f"marker with 0x77 filler); end bits at blocks {end_blocks(span)[:4]} of {s.blocks}, final block flags {s.last_flags}"
            )
        if not s.first_block_zero:
            problems.append("first block is not all zero")
        entry = {
            "index": i,
            "sample_span": d["sample_span"],
            "rate": d["rate"],
            "blocks": s.blocks,
            "last_flags": s.last_flags,
            "terminator": kind,
        }
        if problems:
            failures.extend(f"descriptor {i}: {p}" for p in problems)
        elif len(span) > adpcm.MAX_DECODE_BYTES:
            entry["decode_skipped"] = f"span of {len(span)} bytes exceeds the {adpcm.MAX_DECODE_BYTES} byte decode bound; structure checked only"
            if oracle:
                oracle.skipped.append(f"{label}descriptor {i}")
        else:
            pcm = adpcm.decode(span)
            if oracle:
                oracle.compare("span", f"{label}descriptor {i}", span, d["rate"], pcm)
            entry |= {
                "pcm_sha256": pcm_digest(pcm),
                "clip_fraction": adpcm.clip_fraction(pcm),
                "seconds": len(pcm) / d["rate"] if d["rate"] else None,
            }
        spans.append(entry)
    return {
        "descriptors": spans,
        "decode_skipped_spans": sum("decode_skipped" in entry for entry in spans),
        "payload_codec_evidence": "PS-ADPCM block structure",
        "claim_limits": CLAIM_LIMITS,
        "failures": failures,
    }


def check_stream(header: bytes, payload: bytes, oracle: FfmpegOracle | None = None, label: str = "") -> dict:
    fields = adpcm.mih_fields(header)
    channels, interleave = fields["channels"], fields["interleave"]
    failures, details = [], {"mih": fields, "claim_limits": CLAIM_LIMITS}
    try:
        adpcm.validate_layout(channels, interleave)
    except adpcm.AdpcmError as exc:
        details["failures"] = [f"stream parameters: {exc}"]
        return details
    try:
        streams = adpcm.deinterleave(payload, channels, interleave)
    except adpcm.AdpcmError as exc:
        details["failures"] = [f"stream is not whole interleave turns: {exc}"]
        return details
    turns = len(payload) // (channels * interleave)
    details["turns"] = turns
    if fields["words"][5] != turns:
        failures.append(f"mih turn count {fields['words'][5]} differs from observed {turns}")
    blocks, flag_values, excerpt = [], set(), []
    for ch, stream in enumerate(streams):
        s = adpcm.structure(stream)
        blocks.append(s.blocks)
        flag_values |= {stream[i * 16 + 1] for i in range(s.blocks)}
        failures.extend(f"channel {ch}: {p}" for p in violations(s))
        if not violations(s):
            window = stream[: adpcm.BLOCK * MUSIC_DECODE_BLOCKS]
            pcm = adpcm.decode(window)
            if oracle:
                oracle.compare("music", f"{label}channel {ch} excerpt", window, fields["rate"], pcm)
            excerpt.append({"channel": ch, "pcm_sha256": pcm_digest(pcm), "clip_fraction": adpcm.clip_fraction(pcm)})
    if len(set(blocks)) > 1:
        failures.append(f"channels differ in block count: {blocks}")
    details |= {
        "channel_blocks": blocks,
        "flag_values": sorted(flag_values),
        "decoded_excerpt_blocks": MUSIC_DECODE_BLOCKS,
        "decoded_excerpt": excerpt,
        "seconds": blocks[0] * adpcm.SAMPLES_PER_BLOCK / fields["rate"] if fields["rate"] else None,
        "failures": failures,
    }
    return details


def check_corpus(game: Path, oracle: FfmpegOracle | None = None) -> dict:
    baseline = Baseline(game)
    bank_pairs, unpaired_banks = baseline.pairs(".msh;1", ".msb;1")
    stream_pairs, unpaired_streams = baseline.pairs(".mih;1", ".mib;1")
    if not bank_pairs and not stream_pairs:
        raise Incomplete("no .msb/.mib audio found in the archive baseline")
    banks, streams, classes = [], [], {}
    failures = [f"{path}: no partner in the archive baseline" for path in unpaired_banks + unpaired_streams]
    for msh, msb in bank_pairs:
        try:
            header, payload = msh.load(), msb.load()
            result = check_bank(header, payload, oracle, msb.name + " ")
        except Invalid as exc:
            failures.append(f"{msb.name}: {exc}")
            continue
        failures.extend(f"{msb.name}: {f}" for f in result["failures"])
        for d in result["descriptors"]:
            if d["terminator"]:
                classes[d["terminator"]] = classes.get(d["terminator"], 0) + 1
        banks.append({"path": msb.path.lstrip("/"), "descriptors": result["descriptors"]})
    for mih, mib in stream_pairs:
        try:
            header, payload = mih.load(), mib.load()
            result = check_stream(header, payload, oracle, mib.name + " ")
        except Invalid as exc:
            failures.append(f"{mib.name}: {exc}")
            continue
        failures.extend(f"{mib.name}: {f}" for f in result["failures"])
        streams.append({"path": mib.path.lstrip("/"), **{k: v for k, v in result.items() if k != "failures"}})
    clips = [d["clip_fraction"] for b in banks for d in b["descriptors"] if "clip_fraction" in d]
    details = {
        "provenance": baseline.provenance,
        "banks": len(banks),
        "bank_descriptors": sum(len(b["descriptors"]) for b in banks),
        "streams": len(streams),
        "terminator_classes": dict(sorted(classes.items())),
        "decode_skipped_spans": sum(sum("decode_skipped" in d for d in b["descriptors"]) for b in banks),
        "max_bank_clip_fraction": max(clips, default=0.0),
        "bank_results": banks,
        "stream_results": streams,
        "claim_limits": CLAIM_LIMITS,
        "failures": failures,
    }
    return oracle.finish(details) if oracle else details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["bank", "stream", "corpus"])
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/audio"))
    parser.add_argument(
        "--oracle",
        choices=["ffmpeg"],
        help="also require exact sample equality with an independent software decoder",
    )
    args = parser.parse_args()
    expected = 1 if args.family == "corpus" else 2

    def run():
        if len(args.inputs) < expected:
            raise Incomplete(f"{args.family} needs {expected} inputs; supplied {len(args.inputs)}")
        if len(args.inputs) > expected:
            raise Invalid(f"{args.family} needs exactly {expected} inputs")
        oracle = FfmpegOracle() if args.oracle else None
        if args.family == "corpus":
            return check_corpus(args.inputs[0], oracle)
        first, second = (read_bounded(p) for p in args.inputs)
        details = (check_bank if args.family == "bank" else check_stream)(first, second, oracle)
        return oracle.finish(details) if oracle else details

    inputs = [] if args.family == "corpus" else args.inputs
    return write_result(args.output, "audio:" + args.family, run, inputs)


if __name__ == "__main__":
    raise SystemExit(main())
