#!/usr/bin/env python3
"""Corrected .ps2 tree parse. Layout:

  u32 M        (count of objects/records described later in the file)
  u32 R        (number of root names)
  R x u32      root name offsets
  then repeated: [u32 count][count x u32 name offsets]  (child/group lists; count may be 0)
  the list region terminates exactly when the next word would be the first string in the pool
  (i.e. 4 * pos == min offset among all name offsets).

Validation per file: parse to terminator; check 4*pos == min(name offsets); report groups.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def main() -> None:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    good_n = 0
    for p in ps2s:
        data = p.read_bytes()
        size = len(data)
        nw = min(size // 4, 400000)
        w = struct.unpack_from(f"<{nw}I", data, 0)

        def s_at(off):
            if off <= 0 or off >= size:
                return None
            e = data.find(b"\x00", off)
            if e < 0 or not (1 <= e - off <= 60):
                return None
            seg = data[off:e]
            if not all(32 <= b < 127 for b in seg):
                return None
            return seg.decode("ascii")

        M, R = w[0], w[1]
        pos = 2
        name_offsets = []
        roots = []
        ok = True
        for _ in range(R):
            if pos >= len(w) or s_at(w[pos]) is None:
                ok = False
                break
            roots.append(w[pos])
            name_offsets.append(w[pos])
            pos += 1
        groups = 0
        while ok and pos < len(w):
            cnt = w[pos]
            if cnt > 5000 or pos + 1 + cnt > len(w):
                ok = False
                break
            seg_ok = True
            for k in range(cnt):
                v = w[pos + 1 + k]
                if s_at(v) is None:
                    seg_ok = False
                    break
                name_offsets.append(v)
            if not seg_ok:
                ok = False
                break
            pos += 1 + cnt
            groups += 1
            if name_offsets and 4 * pos == min(name_offsets):
                break  # exact terminator
        min_name = min(name_offsets) if name_offsets else None
        term = (4 * pos == min_name) if min_name else False
        n_missing = max(name_offsets) if name_offsets else 0
        # sanity: min_name should equal byte offset of first string in pool; verify
        # also check that bytes between 4*pos and min_name are zero padding
        pad_ok = True
        if min_name and 4 * pos < min_name:
            pad = data[4 * pos : min_name]
            pad_ok = all(b == 0 for b in pad)
        good = ok and term
        good_n += good
        print(
            f"{p.name:20s} M={M:>6} R={R:>5} groups={groups:>5} names={len(name_offsets):>6} "
            f"pos_end_word={pos:>6} 4*pos=0x{4*pos:x} min_name=0x{min_name or 0:x} term={term} pad_ok={pad_ok} good={good}"
        )
    print(f"\nterminator-verified: {good_n}/{len(ps2s)}")


if __name__ == "__main__":
    main()
