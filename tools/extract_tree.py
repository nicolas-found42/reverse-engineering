#!/usr/bin/env python3
"""Extract FILES.HDR/FILES.DAT into a full directory tree.

Tree semantics (measured):
  - HDR: u32 nseg; nseg x (u32 count, u32 first); records[first:first+count] = segment.
  - Record: 28 bytes = [16B NUL-padded name][u32 type][u32 u1][u32 u2].
  - type != 0xFFFFFFFF: the record is a DIRECTORY whose children are exactly the
    records in segment[type]. Names in segment 0 are the filesystem roots.
  - type == 0xFFFFFFFF: a FILE; u1 = start chunk (offset = u1*2048); u2 = stored bytes.
    Stored blob = raw bytes, or [u32 decompressed_len][zlib stream] when byte 4..5
    are a zlib header.
"""
import hashlib
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
OUT = EX / "files"
MANIFEST = ROOT / "notes/extracted-manifest.tsv"
TREE = ROOT / "notes/fs-tree.txt"

NAME_START = 0x188
REC = 28
CHUNK = 2048
DIRTYPE = 0xFFFFFFFF


def parse_hdr(data: bytes):
    nseg = struct.unpack_from("<I", data, 0)[0]
    segs = [struct.unpack_from("<II", data, 4 + 8 * i) for i in range(nseg)]
    recs = []
    n = (len(data) - NAME_START) // REC
    for i in range(n):
        base = NAME_START + i * REC
        rec = data[base : base + REC]
        nul = rec.find(b"\x00")
        name = rec[:nul].decode("ascii", "replace")
        t, u1, u2 = struct.unpack("<3I", rec[16:28])
        recs.append({"idx": i, "name": name, "type": t, "u1": u1, "u2": u2})
    return nseg, segs, recs


def build_paths(nseg, segs, recs):
    """Assign a full path to every record. Returns dict idx -> path."""
    # dir_for_segment: segment index -> dir record idx (dir whose type == seg)
    dir_for_seg = {}
    for r in recs:
        if r["type"] != DIRTYPE:
            dir_for_seg[r["type"]] = r["idx"]

    paths = {}

    def walk_segment(seg_idx: int, prefix: str):
        first, count = segs[seg_idx][0], segs[seg_idx][1]
        # note: stored as (first, count)? measured: pair=(count, first) → (segs[i][0]=count?)
        # Determine at runtime: our parser stored (a,b) as unpacked from 8 bytes where a=count, b=first
        # (verified: pair[0]=(11,0) → 11 records from 0). Keep that order.
        count, first = segs[seg_idx]
        for i in range(first, first + count):
            if i >= len(recs):
                continue
            r = recs[i]
            path = f"{prefix}/{r['name']}"
            paths[i] = path
            if r["type"] != DIRTYPE:
                walk_segment(r["type"], path)

    walk_segment(0, "")
    return paths, dir_for_seg


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
    ZMAGIC = {0x01, 0x5E, 0x9C, 0xDA}
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
        out = b""
        status = "?"
        if len(blob) >= 6 and blob[4] == 0x78 and blob[5] in ZMAGIC:
            (dlen,) = struct.unpack("<I", blob[:4])
            try:
                d = zlib.decompressobj()
                out = d.decompress(blob[4:]) + d.flush()
                status = "ok(zlib)" if (d.eof and len(out) == dlen) else f"size-mismatch(got={len(out)} want={dlen})"
            except zlib.error as exc:
                status = f"zlib-error: {exc}"
        else:
            out = blob
            status = "ok(raw)"
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
