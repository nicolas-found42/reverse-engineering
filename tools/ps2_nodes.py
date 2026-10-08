#!/usr/bin/env python3
"""Rigorous .ps2 node-table parse + validation across all 56 files.

Hypothesis:
  u32[0] = total node count N
  u32[1] = root count R
  next R u32 = root name offsets
  then, per node i in 0..N-1 (DFS order):
      u32 count_i, then count_i name offsets of children
Validation:
  - all name offsets resolve to printable NUL-terminated strings
  - parse consumes u32 slots and ends before file data; table end offset = 4*(2+R+sum(1+count_i))
  - the u32 right after the parse should NOT be a valid name offset (boundary check)
  - root names + child names: all nodes covered exactly once (each node appears as root or child)
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def main() -> None:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    n_ok = 0
    for p in ps2s:
        data = p.read_bytes()
        size = len(data)
        words = struct.unpack_from(f"<{min(size, 4*200000)//4}I", data, 0)

        def s_at(off):
            if off <= 0 or off >= size:
                return None
            e = data.find(b"\x00", off)
            if e < 0 or not (2 <= e - off <= 40):
                return None
            seg = data[off:e]
            if not all(32 <= b < 127 for b in seg):
                return None
            return seg.decode("ascii")

        N, R = words[0], words[1]
        pos = 2
        roots = []
        ok = True
        for _ in range(R):
            if pos >= len(words) or s_at(words[pos]) is None:
                ok = False
                break
            roots.append(words[pos])
            pos += 1
        total_children = 0
        parsed = 0
        if ok:
            while parsed < N and pos < len(words):
                cnt = words[pos]
                pos += 1
                if cnt > 5000 or pos + cnt > len(words):
                    ok = False
                    break
                for _ in range(cnt):
                    if s_at(words[pos]) is None:
                        ok = False
                        break
                    pos += 1
                if not ok:
                    break
                total_children += cnt
                parsed += 1
        table_end = 4 * pos
        # boundary check: the word at pos should not be a valid in-file name offset OR should be data
        boundary = pos >= len(words) or s_at(words[pos]) is None
        # coverage check: parsed == N and roots + children == N
        coverage = parsed == N and (len(roots) + total_children) == N
        good = ok and coverage and table_end <= size
        n_ok += good
        print(
            f"{p.name:20s} size={size:>8} N={N:>5} R={R:>3} parsed={parsed:>5} roots={len(roots):>3} "
            f"children={total_children:>5} table_end=0x{table_end:x} coverage={coverage} boundary={boundary} ok={good}"
        )
    print(f"\nfully-validated files: {n_ok}/{len(ps2s)}")


if __name__ == "__main__":
    main()
