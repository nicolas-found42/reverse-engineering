#!/usr/bin/env python3
"""Scan FILES.DAT for zlib stream headers (78 01/5e/9c/da) and try decompressing from each.

Also test: does the data region for a file start right after the previous file's
claimed size (u2) boundary? Dump the region boundaries implied by the HDR records
for the first ~30 file records and show what's at each boundary.
"""
import mmap
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
DAT = EX / "FILES.DAT"


def scan_zlib_positions(limit: int = 60) -> list[int]:
    positions = []
    with DAT.open("rb") as fh:
        mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        # scan for 78 9c / 78 01 / 78 5e / 78 da
        pat = [b"\x78\x9c", b"\x78\x01", b"\x78\x5e", b"\x78\xda"]
        pos = 0
        n = len(mm)
        while pos < n and len(positions) < limit:
            hit = -1
            for p in pat:
                j = mm.find(p, pos)
                if j >= 0 and (hit < 0 or j < hit):
                    hit = j
            if hit < 0:
                break
            positions.append(hit)
            pos = hit + 2
        mm.close()
    return positions


def try_inflate_at(off: int, max_out: int = 1 << 22) -> tuple[int, int] | None:
    """Return (decompressed_size, compressed_size) or None."""
    with DAT.open("rb") as fh:
        fh.seek(off)
        d = zlib.decompressobj()
        total = 0
        consumed = 0
        try:
            while total < max_out:
                b = fh.read(1 << 20)
                if not b:
                    return None
                consumed += len(b)
                out = d.decompress(b)
                total += len(out)
                if d.eof:
                    consumed -= len(d.unused_data)
                    return total, consumed
        except zlib.error:
            return None
    return None


def main() -> None:
    poss = scan_zlib_positions(400)
    print(f"zlib-looking offsets (first {len(poss)}): {[hex(p) for p in poss[:40]]}")
    # check first 200: which inflate cleanly
    good = []
    for off in poss[:200]:
        r = try_inflate_at(off, 1 << 24)
        if r:
            good.append((off, r[0], r[1]))
    print(f"cleanly inflating streams: {len(good)}")
    for off, total, comp in good[:60]:
        print(f"  @0x{off:08x} decompressed={total:<10d} compressed={comp:<10d}")

    # region boundaries from HDR file records (first region)
    print("\n=== first region pair table (28-byte records idx 0..47) ===")
    hdr = (EX / "FILES.HDR").read_bytes()
    # print pairs 4..0x188 again but as (a,b) raw
    off = 4
    i = 0
    while off + 8 <= 0x188:
        a, b = struct.unpack_from("<II", hdr, off)
        print(f"  pair[{i:2d}] a={a:8d} b={b:8d}")
        off += 8
        i += 1


if __name__ == "__main__":
    main()
