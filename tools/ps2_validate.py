#!/usr/bin/env python3
"""Validate the .ps2 'string offset table' hypothesis across many files.

For each .ps2: walk u32s from offset 8; count entries that are plausible string
offsets (within file, printable ASCII start, preceded by NUL/0x00 or being the
first). Stop at first run of invalid. Report table sizes and the u32s before/after.
Also: count total NUL-terminated printable strings in the file.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def is_printable(b: int) -> bool:
    return 32 <= b < 127


def string_at(data: bytes, off: int) -> bytes | None:
    """NUL-terminated printable string starting at off (>=2 chars)."""
    if off >= len(data) or not is_printable(data[off]):
        return None
    end = data.find(b"\x00", off)
    if end < 0 or end - off < 2 or end - off > 40:
        return None
    if not all(is_printable(b) for b in data[off:end]):
        return None
    return data[off:end]


def count_strings(data: bytes) -> int:
    n = 0
    p = 0
    while True:
        i = data.find(b"\x00", p)
        if i < 0:
            break
        j = i
        while j > 0 and is_printable(data[j - 1]):
            j -= 1
        if i - j >= 4 and all(is_printable(b) for b in data[j:i]):
            n += 1
        p = i + 1
    return n


def main() -> None:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    print(f"{len(ps2s)} .ps2 files")
    print(f"{'file':28s} {'size':>9} {'u32[0]':>7} {'u32[1]':>7} {'tab_len':>7} {'str_cnt':>7} {'first_nonnumeric_after':>10}")
    results = []
    for p in ps2s:
        data = p.read_bytes()
        size = len(data)
        u0, u1 = struct.unpack_from("<2I", data, 0)
        # walk table from offset 8
        off = 8
        tab = []
        while off + 4 <= size:
            (v,) = struct.unpack_from("<I", data, off)
            s = string_at(data, v) if v < size else None
            if s is None:
                break
            tab.append((off, v, s))
            off += 4
        nstr = count_strings(data)
        results.append((p.name, size, u0, u1, len(tab), nstr, off))
        print(f"{p.name:28s} {size:>9} {u0:>7} {u1:>7} {len(tab):>7} {nstr:>7} 0x{off:x}")

    # stats
    ok = sum(1 for r in results if r[4] >= 10)
    print(f"\nfiles with >=10-entry string-offset table: {ok}/{len(results)}")
    # relation between u0/u1 and anything?
    print("\nu0 vs total strings (first 20):")
    for r in results[:20]:
        print(f"  {r[0]:28s} u0={r[2]:>8} u1={r[3]:>6} tab={r[4]:>5} strs={r[5]:>6}")

    # what does u1 mean? check distribution
    from collections import Counter

    print("\nu1 distribution:", Counter(r[3] for r in results).most_common(12))
    print("u0 distribution (top):", Counter(r[2] for r in results).most_common(12))


if __name__ == "__main__":
    main()
