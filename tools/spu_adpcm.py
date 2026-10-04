#!/usr/bin/env python3
"""Offline PS-ADPCM structure checks and reference decoder for the FR2 sound banks and music streams.

Block format (ADPCM used by the SPU): 16 bytes = shift/filter byte, flag byte, 14 data bytes
holding 28 4-bit samples (low nibble first). Filter coefficients are the published table.

Decoder arithmetic is the one measured to match ffmpeg's `adpcm_psx` sample for sample on all 305
FR2 bank spans: the feedback term truncates toward zero and has no rounding constant, and a block
with flag 7 is an end marker whose filler data decodes to silence, and the filter history keeps
unclipped values while the output is clamped (clipped history disagreed on the 18 spans that reach
full scale). A rounding variant,
`(acc + 32) >> 6`, was tried first and disagreed with ffmpeg on 304 of those spans. No hardware
oracle exists locally, so this is software-reference agreement, not a bit-exact SPU claim.
Everything here is offline, read-only and bounded; it makes no playback claim.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

BLOCK = 16
SAMPLES_PER_BLOCK = 28
FLAG_END, FLAG_REPEAT, FLAG_LOOP_START = 1, 2, 4
FLAG_END_MARKER = 7
# (k0, k1) in 1/64 units
FILTERS = ((0, 0), (60, 0), (115, -52), (98, -55), (122, -60))
MAX_BYTES = 128 * 1024 * 1024


class AdpcmError(ValueError):
    pass


@dataclass(frozen=True)
class Structure:
    blocks: int
    invalid_filter: int
    invalid_shift: int
    invalid_flags: int
    end_blocks: int
    first_block_zero: bool
    last_flags: int


def structure(buf: bytes) -> Structure:
    """Count rule violations; a real stream has none, unrelated data violates them in most blocks."""
    if len(buf) % BLOCK:
        raise AdpcmError(f"length {len(buf)} is not a multiple of {BLOCK}")
    if not buf:
        raise AdpcmError("empty stream")
    if len(buf) > MAX_BYTES:
        raise AdpcmError("stream exceeds bounded size")
    n = len(buf) // BLOCK
    invalid_filter = invalid_shift = invalid_flags = ends = 0
    for i in range(n):
        head, flags = buf[i * BLOCK], buf[i * BLOCK + 1]
        invalid_filter += (head >> 4) >= len(FILTERS)
        invalid_shift += (head & 0xF) > 12
        invalid_flags += flags > 7
        ends += flags & FLAG_END
    return Structure(
        n,
        invalid_filter,
        invalid_shift,
        invalid_flags,
        ends,
        buf[:BLOCK] == bytes(BLOCK),
        buf[-BLOCK + 1],
    )


def decode(buf: bytes) -> list[int]:
    """Decode one mono ADPCM stream to signed 16-bit samples (reference algorithm, not tuned)."""
    s = structure(buf)
    if s.invalid_filter or s.invalid_shift:
        raise AdpcmError("filter/shift outside the ADPCM range")
    out: list[int] = []
    p1 = p2 = 0
    for i in range(s.blocks):
        head = buf[i * BLOCK]
        if buf[i * BLOCK + 1] == FLAG_END_MARKER:
            out.extend([0] * SAMPLES_PER_BLOCK)
            p1 = p2 = 0
            continue
        shift, filt = head & 0xF, head >> 4
        k0, k1 = FILTERS[filt]
        data = buf[i * BLOCK + 2 : (i + 1) * BLOCK]
        for byte in data:
            for nib in (byte & 0xF, byte >> 4):
                raw = nib - 16 if nib >= 8 else nib
                v = (raw << 12) >> shift
                feedback = p1 * k0 + p2 * k1
                v = v + (feedback // 64 if feedback >= 0 else -(-feedback // 64))
                out.append(max(-32768, min(32767, v)))
                p2, p1 = p1, v  # history keeps the unclipped value, as ffmpeg does
    return out


def deinterleave(buf: bytes, channels: int, interleave: int) -> list[bytes]:
    """Split interleaved channel blocks (`interleave` bytes per channel turn)."""
    if channels < 1 or interleave < BLOCK or interleave % BLOCK:
        raise AdpcmError("bad channel/interleave parameters")
    turn = channels * interleave
    if len(buf) % turn:
        raise AdpcmError(f"length {len(buf)} not a whole number of {turn}-byte interleave turns")
    streams = [bytearray() for _ in range(channels)]
    for off in range(0, len(buf), turn):
        for ch in range(channels):
            streams[ch] += buf[off + ch * interleave : off + (ch + 1) * interleave]
    return [bytes(s) for s in streams]


def clip_fraction(samples: list[int]) -> float:
    return sum(abs(v) >= 32767 for v in samples) / len(samples) if samples else 0.0


def mih_fields(header: bytes) -> dict:
    if len(header) < 24 or len(header) % 4:
        raise AdpcmError("mih header too short or unaligned")
    words = struct.unpack(f"<{len(header) // 4}I", header)
    return {"words": list(words), "channels": words[2], "rate": words[3], "interleave": words[4]}
