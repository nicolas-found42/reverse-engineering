#!/usr/bin/env python3
"""Extract FILES.HDR/FILES.DAT into a full directory tree.

Tree semantics (measured):
  - HDR: u32 nseg; nseg x (u32 count, u32 first); u32 record_count; records[first:first+count] = segment.
  - Record: 28 bytes = [16B bounded NUL-terminated name][u32 type][u32 u1][u32 u2].
  - type != 0xFFFFFFFF: the record is a DIRECTORY whose children are exactly the
    records in segment[type]. Names in segment 0 are the filesystem roots.
  - type == 0xFFFFFFFF: a FILE; u1 = start chunk (offset = u1*2048); u2 = stored bytes.
    Stored blob = raw bytes, or [u32 decompressed_len][zlib stream] when byte 4..5
    are a zlib header.
"""
import hashlib
from pathlib import Path

from format_contracts import archive_header, decode_payload, require

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
OUT = EX / "files"
MANIFEST = ROOT / "notes/extracted-manifest.tsv"
TREE = ROOT / "notes/fs-tree.txt"

CHUNK = 2048
DIRTYPE = 0xFFFFFFFF


def parse_hdr(data: bytes):
    parsed = archive_header(data)
    return len(parsed['segments']), parsed['segments'], parsed['records']


def build_paths(nseg, segs, recs):
    """Paths already passed the structured header's partition/cycle/bounds checks."""
    require(nseg == len(segs), 'segment count differs from parsed header')
    return ({r['idx']: r['path'] for r in recs},
            {r['type']: r['idx'] for r in recs if r['type'] != DIRTYPE})


def main() -> None:
    hdr = (EX / "FILES.HDR").read_bytes()
    nseg, segs, recs = parse_hdr(hdr)
    print(f"segments={nseg} records={len(recs)}")

    # sanity: segments must partition records
    covered = []
    for i, (count, first) in enumerate(segs):
        covered.extend(range(first, first + count))
    covered_sorted = sorted(covered)
    expected = list(range(len(recs)))
    print(f"segments partition all records: {covered_sorted == expected}")
    # note: some records may be claimed by 2 segments if overlap; check uniqueness
    print(f"unique covered: {len(set(covered))} of {len(covered)}")
    if covered_sorted != expected:
        missing = sorted(set(expected) - set(covered))
        dupes = [x for x in set(covered) if covered.count(x) > 1]
        print(f"  missing: {missing[:20]} dupe-claimed: {dupes[:20]}")

    paths, dir_for_seg = build_paths(nseg, segs, recs)
    print(f"assigned paths: {len(paths)}")

    # print the tree
    lines = []
    for i in sorted(paths):
        r = recs[i]
        kind = "D" if r["type"] != DIRTYPE else "F"
        lines.append(f"{kind} {paths[i]}")
    (TREE).write_text("\n".join(lines) + "\n")
    print(f"tree written: {TREE} ({len(lines)} lines)")
    for line in lines[:40]:
        print("  " + line)

    # extract
    OUT.mkdir(parents=True, exist_ok=True)
    dat = (EX / "FILES.DAT").open("rb")
    stats = {"ok(zlib)": 0, "ok(raw)": 0}
    rows = []
    for i in sorted(paths):
        r = recs[i]
        if r["type"] != DIRTYPE:
            continue
        path = paths[i].lstrip("/")
        off = r["u1"] * CHUNK
        stored = r["u2"]
        dat.seek(off)
        blob = dat.read(stored)
        require(len(blob) == stored, f'record {i}: short DAT read')
        classification, out, _ = decode_payload(blob)
        status = f'ok({classification})'
        stats[status] = stats.get(status, 0) + 1
        dest = OUT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(out)
        rows.append((i, paths[i], r["u1"], stored, status, len(out), hashlib.sha1(out).hexdigest()[:16]))
    dat.close()
    print(f"extracted: {stats}")

    with MANIFEST.open("w") as fh:
        fh.write("idx\tpath\tchunk\tstored_bytes\tstatus\tout_bytes\tsha1_16\n")
        for row in rows:
            fh.write("\t".join(str(x) for x in row) + "\n")
    print(f"manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
