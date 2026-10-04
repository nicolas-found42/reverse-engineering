#!/usr/bin/env python3
"""Validate the .ps2 layout across all 56 files:

  u32[0] = end offset of the string pool (names_end, bytes)
  u32[1] = root count R; then R x u32 root-name offsets  (the roots list)
  then repeated: [u32 count][count x u32 name offsets]   (child lists, count may be 0)
  Parse must terminate exactly at the string pool start: 4 * pos == min(name offsets)

Reports: parsed pairs, zero/nonzero counts, terminator check, and whether
names_end equals the max string end in the pool.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def main() -> None:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    n_ok = 0
    for p in ps2s:
        data = p.read_bytes()
        size = len(data)
        nw = min(size // 4, 400000)
        w = struct.unpack_from(f"<{nw}I", data, 0)

        def s_at(off):
            if off <= 0 or off >= size:
                return None
            e = data.find(b"\x00", off)
            if e < 0 or not (2 <= e - off <= 60):
                return None
            seg = data[off:e]
            if not all(32 <= b < 127 for b in seg):
                return None
            return seg.decode("ascii")

        names_end = w[0]
        R = w[1]
        pos = 1
        pairs = []
        names = 0
        ok = True
        # first pair: R roots
        if pos + R > len(w) or not all(s_at(w[pos + k]) for k in range(R)):
            ok = False
        else:
            roots = [s_at(w[pos + k]) for k in range(R)]
            pos += R
            names += R
            pairs.append(("roots", R, roots[:3]))
            while ok and pos < len(w):
                c = w[pos]
                if c > 2000 or pos + 1 + c > len(w):
                    ok = False
                    break
                okn = all(s_at(w[pos + 1 + k]) for k in range(c))
                if not okn:
                    ok = False
                    break
                pairs.append((len(pairs), c, [s_at(w[pos + 1 + k]) for k in range(min(c, 3))]))
                pos += 1 + c
                names += c
                # terminator: reached string pool start
                min_name = min(v for v in w[2 : pos + 1] if s_at(v)) if pos > 2 else None
                if min_name and 4 * (pos) >= min_name:
                    break
        term = None
        if pos < len(w):
            min_name = min((v for v in w[2:pos+1] if s_at(v)), default=None)
            term = (4 * pos, min_name, 4 * pos == min_name) if min_name else (4 * pos, None, False)
        good = ok and term and term[2]
        n_ok += bool(good)
        zeros = sum(1 for pr in pairs if isinstance(pr[0], int) and pr[1] == 0)
        print(
            f"{p.name:20s} names_end={names_end:>7} R={R:>5} pairs={len(pairs):>5} names={names:>6} "
            f"zero_pairs={zeros:>4} term={term} good={good}"
        )
    print(f"\nterminator-verified: {n_ok}/{len(ps2s)}")


if __name__ == "__main__":
    main()
