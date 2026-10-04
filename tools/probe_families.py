#!/usr/bin/env python3
"""Deep probes for the jev-flagged families: .ps2, .ptg, .msb/.msh, .mib/.mih.

Prints structure hypotheses with measurements, not guesses:
- .ps2: offset/pointer tables, look for 0x10-stride tables, chunk boundaries
- .ptg: header field pattern across many files, pixel-data test
- .msb/.msh: strings census + entropy + cross-refs (do names match .PS2 or samples?)
- .mib/.mih: entropy, autocorrelation-ish zero runs, byte histogram (ADPCM vs PCM)
"""
import math
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def find_one(pattern: str) -> Path:
    hits = sorted(FILES.rglob(pattern))
    assert hits, f"no file matching {pattern}"
    return hits[0]


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def ascii_strings(data: bytes, min_len: int = 4, limit: int = 40):
    out = []
    cur = bytearray()
    start = 0
    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not cur:
                start = i
            cur.append(b)
        else:
            if len(cur) >= min_len:
                out.append((start, bytes(cur).decode()))
            cur = bytearray()
        if len(out) >= limit:
            break
    return out


def probe_ps2() -> None:
    print("=" * 78)
    print("PROBE: .ps2 (assumed 3D asset container)")
    for name in ("FORDGT.PS2;1", "BayA.PS2;1", "COBRA.PS2;1", "misc.ps2;1"):
        p = find_one(name)
        data = p.read_bytes()
        print(f"\n--- {p.name} size={len(data)} entropy={entropy(data[:65536]):.3f}")
        head = data[:0x120]
        for o in range(0, 0x120, 16):
            chunk = head[o : o + 16]
            if len(chunk) < 16:
                break
            u = struct.unpack("<4I", chunk)
            f = struct.unpack("<4f", chunk)
            print(f"  {o:04x}: u32={[hex(x) for x in u]}  f32={[round(x,2) for x in f]}")
        # strings in first 64KB
        strs = ascii_strings(data[:65536], 6, 15)
        print(f"  strings(first 64KB): {strs[:10]}")


def probe_ptg() -> None:
    print("=" * 78)
    print("PROBE: .ptg (jeV: texture_graphics 0.80 review)")
    ptgs = sorted((p for p in FILES.rglob("*.ptg;1")), key=lambda p: p.stat().st_size)
    print(f"{len(ptgs)} ptg files; sizes {ptgs[0].stat().st_size}..{ptgs[-1].stat().st_size}")
    # header pattern across sample
    import random

    random.seed(1)
    sample = random.sample(ptgs, min(12, len(ptgs)))
    for p in sample:
        data = p.read_bytes()
        h = data[:0x30]
        u = struct.unpack("<12I", h)
        print(f"  {p.name:24s} {p.stat().st_size:>8}  u32={[hex(x) for x in u[:8]]}")
    # look at one mid file fully
    p = ptgs[len(ptgs) // 2]
    data = p.read_bytes()
    print(f"\n  full head of {p.name} ({len(data)}B):")
    for o in range(0, 0x80, 16):
        chunk = data[o : o + 16]
        u = struct.unpack("<4I", chunk)
        print(f"    {o:04x}: {chunk.hex(' ')}  u32={[hex(x) for x in u]}")
    # count how many ptg files start with same first u32
    firsts = Counter(struct.unpack("<I", p.read_bytes()[:4])[0] for p in ptgs)
    print(f"  first-u32 distribution (top10): {[(hex(k), v) for k, v in firsts.most_common(10)]}")


def probe_msb_msh() -> None:
    print("=" * 78)
    print("PROBE: .msb/.msh (jeV conflict: 3d vs audio)")
    for name in ("baya.msb;1", "baya.msh;1", "car1_snd.msb;1", "car1_snd.msh;1", "junga.msh;1", "house1.mih;1"):
        try:
            p = find_one(name)
        except AssertionError:
            print(f"  {name} not found")
            continue
        data = p.read_bytes()
        print(f"\n--- {p.name} size={len(data)} entropy={entropy(data[:65536]):.3f}")
        for o in range(0, min(0x60, len(data)), 16):
            chunk = data[o : o + 16]
            u = struct.unpack(f"<{len(chunk)//4}I", chunk[: len(chunk) // 4 * 4])
            print(f"  {o:04x}: {chunk.hex(' ')}  u32={[hex(x) for x in u]}")
        strs = ascii_strings(data[:262144], 5, 20)
        if strs:
            print(f"  strings(first 256KB): {strs[:15]}")


def probe_mib_mih() -> None:
    print("=" * 78)
    print("PROBE: .mib/.mih (music) + .msb audio-sample test")
    p = find_one("house1.mib;1")
    data = p.read_bytes()
    print(f"--- {p.name} size={len(data)} ent(full)={entropy(data[:1<<20]):.3f} ent(head 64KB)={entropy(data[:65536]):.3f}")
    for o in range(0, 0x60, 16):
        chunk = data[o : o + 16]
        u = struct.unpack("<4I", chunk)
        print(f"  {o:04x}: {chunk.hex(' ')}  u32={[hex(x) for x in u]}")
    # zero-run stats on next 200KB
    body = data[0x40 : 0x40 + 200_000]
    zeros = sum(1 for b in body if b == 0)
    print(f"  body zero fraction: {zeros/len(body):.3f}")
    # unique byte values in body
    print(f"  body distinct byte values: {len(set(body))}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["ps2", "ptg", "msb", "mib"]
    if "ps2" in which:
        probe_ps2()
    if "ptg" in which:
        probe_ptg()
    if "msb" in which:
        probe_msb_msh()
    if "mib" in which:
        probe_mib_mih()
