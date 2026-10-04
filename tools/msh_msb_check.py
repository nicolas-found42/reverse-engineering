#!/usr/bin/env python3
"""Verify .msh/.msb pair relationship + .mib/.mih pair relationship.

.msh hypothesis: 64-byte header (0x40, X, N, ...) then N x 16-byte descriptors
(0, start, ?, size) whose start/size chain to the .msb file size.
Checks every pair: does start[0]+? ... final start+size == .msb size?
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def find(name: str) -> Path | None:
    hits = list(FILES.rglob(name))
    return hits[0] if hits else None


def main() -> None:
    msbs = sorted(FILES.rglob("*.msb;1"))
    print(f"{len(msbs)} .msb files; checking .msh pairs")
    print(f"{'pair':18s} {'msb_size':>9} {'msh_size':>8} {'n':>2} {'chain_ok':>8} {'final':>9} {'sizes':>40}")
    all_ok = 0
    for msb in msbs:
        msh = find(msb.name.replace(".msb;1", ".msh;1"))
        if msh is None:
            print(f"{msb.name:18s} NO .msh")
            continue
        data = msh.read_bytes()
        h = struct.unpack_from("<4I", data, 0)
        n = h[2]
        # descriptors: try (0, start, samples, size) 16-byte records from 0x10
        descs = []
        for i in range(n):
            off = 0x10 + 16 * i
            if off + 16 > len(data):
                break
            a, b, c, d = struct.unpack_from("<4I", data, off)
            descs.append((a, b, c, d))
        # chain test: start[i+1] == start[i] + size[i-1]? (shifted) OR start[i]+size[i]
        starts = [d[1] for d in descs]
        sizes = [d[3] for d in descs]
        chain_shift = all(starts[i + 1] == starts[i] + sizes[i - 1] for i in range(1, n - 1)) if n >= 3 else None
        final = starts[-1] + sizes[-1]
        msb_size = msb.stat().st_size
        ok = final == msb_size
        # Also: chain where size of entry i connects start i to start i+1 using size[i]
        chain_direct = all(starts[i + 1] == starts[i] + sizes[i] for i in range(n - 1)) if n >= 2 else None
        all_ok += bool(ok)
        print(
            f"{msb.name:18s} {msb_size:>9} {len(data):>8} {n:>2} {str(ok):>8} {final:>9} "
            f"{starts} sz={sizes} direct={chain_direct} shift={chain_shift}"
        )
    print(f"\nchain-to-msb-size holds: {all_ok}/{len(msbs)}")

    # .mib/.mih
    print()
    mibs = sorted(FILES.rglob("*.mib;1"))
    print(f"{len(mibs)} .mib files")
    for mib in mibs[:8]:
        mih = find(mib.name.replace(".mib;1", ".mih;1"))
        if not mih:
            print(f"{mib.name}: no .mih")
            continue
        h = struct.unpack_from("<8I", mih.read_bytes(), 0)
        sz = mib.stat().st_size
        print(f"  {mib.name:16s} mib={sz:>9} mih={[hex(x) for x in h]}  mib/16={sz/16:.0f} samples@hdr[?]={h[1]} bytes/sample={sz/h[1] if h[1] else 0:.3f}")


if __name__ == "__main__":
    main()
