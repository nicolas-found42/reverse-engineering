#!/usr/bin/env python3
"""Deep analysis of FILES.HDR: chain runs, 0xFFFFFFFF census, ASCII strings."""
import struct
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HDR = ROOT / "games/ford-racing-2/extracted/FILES.HDR"


def main() -> None:
    data = HDR.read_bytes()
    print(f"HDR size {len(data)}, (size-4)/8 = {(len(data)-4)/8}, (size-4)%8 = {(len(data)-4)%8}")

    n = (len(data) - 4) // 8
    pairs = [struct.unpack("<II", data[4 + 8 * i : 12 + 8 * i]) for i in range(n)]

    # maximal chaining runs
    runs = []
    start = 0
    for i in range(len(pairs) - 1):
        size_i, off_i = pairs[i]
        size_j, off_j = pairs[i + 1]
        ok = size_i != 0xFFFFFFFF and size_j != 0xFFFFFFFF and off_j == off_i + size_i
        if ok and i > start:
            continue
        # hmm this logic is wrong; recompute below
    # proper run detection
    runs = []
    run_start = 0
    for i in range(1, len(pairs)):
        size_prev, off_prev = pairs[i - 1]
        size_cur, off_cur = pairs[i]
        chains = (size_prev != 0xFFFFFFFF and size_cur != 0xFFFFFFFF and off_cur == off_prev + size_prev)
        if not chains:
            if i - run_start >= 3:
                runs.append((run_start, i, pairs[run_start], pairs[i - 1]))
            run_start = i

    print(f"runs of >=3 chaining pairs: {len(runs)}")
    for rs, re_, p0, p1 in runs[:40]:
        span = p1[1] + p1[0] - p0[1]
        print(f"  run[{rs:5d}:{re_:5d}] len={re_-rs:5d} start=({p0[0]},{p0[1]}) end=({p1[0]},{p1[1]}) span={span}")

    ffff = sum(1 for s, o in pairs if s == 0xFFFFFFFF or o == 0xFFFFFFFF)
    print(f"pairs containing 0xFFFFFFFF: {ffff}")

    # zero-size pairs adjacent to nonzero (possible separators/delimiters)
    zz = sum(1 for s, o in pairs if s == 0 and o == 0)
    print(f"pairs equal (0,0): {zz}")

    # is the whole file maybe: u32 count; then count (size,offset) pairs; then more tables?
    print("word0 =", struct.unpack('<I', data[:4])[0])
    w = struct.unpack('<' + 'I'*(len(data)//4), data[:len(data)//4*4])
    print("first 64 words:", [hex(x) for x in w[:64]])

    # ASCII strings in header
    strs = [(m.start(), m.group().decode()) for m in re.finditer(rb"[\x20-\x7e]{6,}", data)]
    print(f"ascii strings >=6: {len(strs)}")
    for off, s in strs[:40]:
        print(f"  0x{off:06x} {s}")


if __name__ == "__main__":
    main()
