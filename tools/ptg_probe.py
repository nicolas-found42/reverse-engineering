#!/usr/bin/env python3
"""Deep probe of .ptg: dump small file fully, look for sub-block structure.

Hypothesis: header [u32 a][u32 b][u32 c][u32 0x20][u32 0x20][u32 d][u32 e][u32 1]
where d,e may be pixel dims. Then sub-blocks with 1.0 floats and pointers.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def dump(path: Path, limit: int = 0x200) -> None:
    data = path.read_bytes()
    print(f"\n=== {path.name} size={len(data)} ===")
    n = min(limit, len(data))
    for o in range(0, n, 16):
        chunk = data[o : o + 16]
        if len(chunk) == 16:
            u = struct.unpack("<4I", chunk)
            f = struct.unpack("<4f", chunk)
            fs = " ".join(f"{x:7.2f}" if abs(x) < 1e5 else "  ~~~~~" for x in f)
        else:
            u, fs = (), ""
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {o:05x}: {chunk.hex(' ')}  {asc}  u={[hex(x) for x in u]} f=[{fs}]")


def main() -> None:
    # smallest ptg
    ptgs = sorted((p for p in FILES.rglob("*.ptg;1")), key=lambda p: p.stat().st_size)
    print(f"{len(ptgs)} ptg files, sizes: min={ptgs[0].stat().st_size} max={ptgs[-1].stat().st_size}")

    # dump three small/medium
    for p in ptgs[:2]:
        dump(p, 0x180)
    mid = ptgs[len(ptgs) // 2]
    dump(mid, 0x100)

    # Look at where 1.0f floats cluster in Desert_C.ptg
    p = list(FILES.rglob("Desert_C.ptg;1"))[0]
    data = p.read_bytes()
    import re
    ones = [m.start() for m in re.finditer(b"\x00\x00\x80\x3f", data)]
    print(f"\nDesert_C.ptg: 1.0f occurrences: {len(ones)} at {[hex(x) for x in ones[:20]]}")
    # check 0xDD 0xDD runs
    dd = [m.start() for m in re.finditer(b"\xdd\xdd\xdd\xdd", data)]
    print(f"  0xDDDDDDDD occurrences: {len(dd)} first few {[hex(x) for x in dd[:10]]}")
    # find where 0xDD runs end / other content begins
    # print bytes around first 1.0f cluster
    if ones:
        o = ones[0]
        print(f"  around first 1.0f @0x{o:x}:")
        seg = data[max(0, o - 32) : o + 64]
        for i in range(0, len(seg), 16):
            print(f"    {max(0,o-32)+i:05x}: {seg[i:i+16].hex(' ')}")

    # scan all ptg: distribution of header u32s
    print("\n=== header stats across all ptg ===")
    h1 = {}
    dims = []
    for p in ptgs:
        d = p.read_bytes()
        if len(d) < 32:
            continue
        u = struct.unpack_from("<8I", d, 0)
        key = (u[3], u[4])
        h1[key] = h1.get(key, 0) + 1
        dims.append((p.name, u[0], u[1], u[2], u[5], u[6], p.stat().st_size))
    print("(u[3],u[4]) distribution:", {f"0x{k[0]:x},0x{k[1]:x}": v for k, v in sorted(h1.items(), key=lambda kv: -kv[1])[:10]})
    print("\nFirst 30: name, u0, u1, u2, u5, u6, file_size, u5*u6, size/(u5*u6)")
    for name, u0, u1, u2, u5, u6, sz in dims[:30]:
        area = u5 * u6
        print(f"  {name:22s} u0={u0:4d} u1={u1:3d} u2={u2:3d} dims={u5}x{u6} size={sz:>7} area={area:>7} ratio={sz/area if area else 0:.2f}")


if __name__ == "__main__":
    main()
