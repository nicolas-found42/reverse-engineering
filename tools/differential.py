#!/usr/bin/env python3
"""Differential analysis of FILES.HDR string/record layout + FILES.DAT zlib chain.

Writes notes/hdr-strings.tsv with every string run and its stride analysis,
and tries to decode the DAT as a chain of [u32 size][zlib stream] blobs.
"""
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
HDR = EX / "FILES.HDR"
DAT = EX / "FILES.DAT"
NOTES = ROOT / "notes"


def hdr_strings() -> None:
    data = HDR.read_bytes()
    runs = [(m.start(), m.end(), m.group()) for m in re.finditer(rb"[\x20-\x7e]{3,}", data)]
    print(f"HDR: {len(runs)} string runs (>=3 chars)")
    rows = []
    for i, (s, e, txt) in enumerate(runs):
        nxt = runs[i + 1][0] if i + 1 < len(runs) else len(data)
        stride = nxt - s
        namelen = e - s
        # bytes after string up to next string
        tail = data[e:nxt]
        rows.append((s, e, namelen, stride, txt, tail))
    # stride distribution
    from collections import Counter

    c = Counter(r[3] - r[2] for r in rows)
    print("stride-namelen distribution (top 15):", c.most_common(15))
    # print full detail for first 50
    for s, e, namelen, stride, txt, tail in rows[:50]:
        gap = stride - namelen
        print(f"@{s:05x} len={namelen:3d} stride={stride:3d} gap_after={gap:3d} {txt.decode()!r:26s} tail={tail[:8].hex(' ')}")
    with (NOTES / "hdr-strings.tsv").open("w") as fh:
        fh.write("offset\tend\tnamelen\tstride\tname\ttail_hex\n")
        for s, e, namelen, stride, txt, tail in rows:
            fh.write(f"0x{s:x}\t0x{e:x}\t{namelen}\t{stride}\t{txt.decode('ascii','replace')}\t{tail.hex()}\n")
    print(f"written {NOTES/'hdr-strings.tsv'}")


def dat_chain(max_entries: int = 200) -> None:
    """Try interpreting DAT as chain of [u32 size][zlib stream]."""
    print("\n=== DAT zlib chain test ===")
    with DAT.open("rb") as fh:
        off = 0
        entries = []
        for i in range(max_entries):
            fh.seek(off)
            hdr = fh.read(4)
            if len(hdr) < 4:
                break
            (size,) = struct.unpack("<I", hdr)
            magic = fh.read(2)
            is_zlib = magic[0] == 0x78 and magic[1] in (0x01, 0x5E, 0x9C, 0xDA)
            entries.append((off, size, is_zlib, magic.hex()))
            if not is_zlib:
                print(f"  entry[{i}] @0x{off:x}: size={size} NOT zlib (magic={magic.hex()}) — stop")
                break
            # decompress fully
            fh.seek(off + 4)
            d = zlib.decompressobj()
            total = 0
            consumed = 0
            while True:
                b = fh.read(1 << 20)
                if not b:
                    break
                consumed += len(b)
                out = d.decompress(b)
                total += len(out)
                if d.eof:
                    break
            consumed -= len(d.unused_data)
            if i < 40 or i % 25 == 0:
                print(f"  entry[{i}] @0x{off:x}: size_hdr={size:<10d} decompressed={total:<10d} comp_len={consumed}")
            off = off + 4 + consumed
            if total != size:
                print(f"    !! size mismatch: hdr {size} vs actual {total}")
            if off >= DAT.stat().st_size:
                break
        print(f"chain ended at 0x{off:x} after {len(entries)} entries (DAT size 0x{DAT.stat().st_size:x})")


def elf_strings() -> None:
    print("\n=== ELF strings: loader clues ===")
    data = (EX / "SLES_517.05").read_bytes()
    needles = [b"FILES.HDR", b"FILES.DAT", b"files.hdr", b"hdr", b"zlib", b"inflate", b"deflate", b"uncompress", b"ps2;1", b"TRACKS", b"stream", b"STREAM", b"libr", b"LZ", b"cdrom0"]
    for needle in needles:
        count = data.count(needle)
        if count:
            idxs = []
            p = 0
            while len(idxs) < 5:
                j = data.find(needle, p)
                if j < 0:
                    break
                idxs.append(j)
                p = j + 1
            print(f"  {needle!r}: count={count} first@{[hex(x) for x in idxs]}")


if __name__ == "__main__":
    hdr_strings()
    elf_strings()
    dat_chain()
