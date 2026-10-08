#!/usr/bin/env python3
"""Rigorous FILES.HDR structure analysis — exact offsets, hypothesis testing.

Hypothesis H: sequence of records = [name NUL-terminated, padded to 4-alignment
relative to name start][16-byte payload: 4 x u32].
Test H by parsing from the first name and reporting where it breaks.
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
HDR = EX / "FILES.HDR"


def align4(x: int) -> int:
    return (x + 3) & ~3


def main() -> None:
    data = HDR.read_bytes()
    print(f"file size 0x{len(data):x} ({len(data)})")

    # --- region A: words 0..: count + pairs
    w0 = struct.unpack_from("<I", data, 0)[0]
    print(f"word0={w0} (0x{w0:x})")

    # chain test for pairs starting at 4
    pairs = []
    off = 4
    cum = 0
    while off + 8 <= 0x188:
        size, offv = struct.unpack_from("<II", data, off)
        pairs.append((off, size, offv))
        off += 8
        if size == 0xFFFFFFFF:
            break
    print(f"pairs from 0x4: {len(pairs)} (region ends 0x188)")
    # print all pairs with computed expectation
    cum = 0
    for i, (poff, size, offv) in enumerate(pairs[:48]):
        mark = "OK" if offv == cum else f"BREAK(got {offv}, exp {cum}, delta {offv-cum})"
        print(f"  pair[{i:2d}] @0x{poff:03x} size={size:6d} (0x{size:x}) off={offv:6d} (0x{offv:x}) {mark}")
        cum = offv + size

    # --- region B: names. Find first name offset.
    # first ASCII name is "3DDATA" — find it
    i = data.find(b"3DDATA")
    print(f"\nfirst name '3DDATA' at 0x{i:x}")
    # --- hypothesis: records = name + pad-to-4 + 16 bytes
    pos = i
    count = 0
    records = []
    while pos < len(data):
        # name = printable run until NUL
        j = pos
        while j < len(data) and data[j] != 0:
            j += 1
        name = data[pos:j]
        try:
            namestr = name.decode("ascii")
        except UnicodeDecodeError:
            print(f"  @0x{pos:x}: non-ascii name, stop")
            break
        # heuristics: name should be printable ascii
        if not all(32 <= b < 127 for b in name) or len(name) == 0:
            print(f"  @0x{pos:x}: bad name {name[:40]!r}, stop")
            break
        rec_start = align4(pos + len(name) + 1)
        rec = data[rec_start : rec_start + 16]
        if len(rec) < 16:
            break
        f = struct.unpack("<4I", rec)
        records.append((pos, namestr, rec_start, f))
        count += 1
        pos = rec_start + 16
        if count <= 60:
            print(f"  @0x{pos:04x}-record: name={namestr!r:24s} rec@0x{rec_start:04x} fields={[hex(x) for x in f]}")
            if namestr == "WHEELS" or count >= 60:
                pass
    print(f"\nparsed records: {count}, stopped at 0x{pos:x} (file 0x{len(data):x})")

    # where did the NEXT thing start; check what remains
    print(f"remaining bytes: {len(data)-pos}")

    # print last parsed records
    for pos_, namestr, rec_start, f in records[-10:]:
        print(f"  last: @0x{pos_:04x} name={namestr!r} fields={[hex(x) for x in f]}")

    # Save full records to a file
    out = ROOT / "notes/hdr-records.tsv"
    with out.open("w") as fh:
        fh.write("name_offset\tname\trec_offset\tf0\tf1\tf2\tf3\n")
        for pos_, namestr, rec_start, f in records:
            fh.write(f"0x{pos_:x}\t{namestr}\t0x{rec_start:x}\t" + "\t".join(hex(x) for x in f) + "\n")
    print(f"written {out}")


if __name__ == "__main__":
    main()
