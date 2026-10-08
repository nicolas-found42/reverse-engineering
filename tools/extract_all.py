#!/usr/bin/env python3
"""Extract all files from FILES.HDR + FILES.DAT.

Format (validated against measured data):
  HDR: u32 nsegments; nsegments x (u32 count, u32 first); then 1037 records of 28 bytes:
       [16-byte NUL-padded name][u32 type][u32 u1][u32 u2]
       type  : 0xFFFFFFFF = file; other = directory (segment index)
       u1,u2 : file  -> u1 = chunk index (offset = u1*2048), u2 = stored bytes (=4+zlib_len)
               dir   -> (u1, u2) = (segment index, 0)  [tree semantics TBD]
  DAT: 163399 chunks of 2048 bytes. File at chunk c: [u32 decompressed_len][zlib stream].
"""
import hashlib
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"
OUT = EX / "files"
MANIFEST = ROOT / "notes/extracted-manifest.tsv"

NAME_START = 0x188
REC = 28
CHUNK = 2048


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


def main() -> None:
    hdr = (EX / "FILES.HDR").read_bytes()
    nseg, segs, recs = parse_hdr(hdr)
    print(f"segments: {nseg}; records: {len(recs)}")
    files = [r for r in recs if r["type"] == 0xFFFFFFFF]
    dirs = [r for r in recs if r["type"] != 0xFFFFFFFF]
    print(f"file records: {len(files)}; dir records: {len(dirs)}")

    dat_size = (EX / "FILES.DAT").stat().st_size
    print(f"DAT size {dat_size} = {dat_size/CHUNK} chunks exactly: {dat_size % CHUNK == 0}")

    OUT.mkdir(parents=True, exist_ok=True)
    dat = (EX / "FILES.DAT").open("rb")
    ok = raw_ok = bad = 0
    rows = []
    ZMAGIC = {0x01, 0x5E, 0x9C, 0xDA}
    for r in files:
        off = r["u1"] * CHUNK
        stored = r["u2"]
        name = r["name"]
        try:
            dat.seek(off)
            blob = dat.read(stored)
            out = b""
            status = "?"
            # compressed = [u32 decompressed_size][zlib stream]
            if len(blob) >= 6 and blob[4] == 0x78 and blob[5] in ZMAGIC:
                (dlen,) = struct.unpack("<I", blob[:4])
                try:
                    d = zlib.decompressobj()
                    out = d.decompress(blob[4:])
                    out += d.flush()
                    if d.eof and len(out) == dlen:
                        status = "ok(zlib)"
                    elif d.eof:
                        status = f"ok(zlib-size-mismatch got={len(out)} want={dlen})"
                    else:
                        status = f"zlib-incomplete(eof={d.eof} got={len(out)} want={dlen})"
                except zlib.error as exc:
                    status = f"zlib-error: {exc}"
            else:
                out = blob
                status = "ok(raw)"
        except Exception as exc:  # noqa: BLE001
            out = b""
            status = f"error: {exc}"
        safe = name.replace("/", "_").replace("\\", "_")
        if status == "ok(zlib)":
            ok += 1
            (OUT / safe).write_bytes(out)
        elif status == "ok(raw)":
            raw_ok += 1
            (OUT / safe).write_bytes(out)
        else:
            bad += 1
            (OUT / (safe + ".FAILED")).write_bytes(out)
        rows.append((r["idx"], name, r["u1"], r["u2"], status, len(out), hashlib.sha1(out).hexdigest()[:16]))
        if bad and status.startswith(("zlib-error", "error:")) and bad < 8:
            print(f"  FAIL {name!r} chunk={r['u1']} stored={stored} {status}")
    dat.close()
    print(f"extracted zlib={ok} raw={raw_ok} bad={bad}")

    with MANIFEST.open("w") as fh:
        fh.write("idx\tname\tchunk\tstored_bytes\tstatus\tout_bytes\tsha1_16\n")
        for row in rows:
            fh.write("\t".join(str(x) for x in row) + "\n")
    print(f"manifest: {MANIFEST}")

    # directory listing summary
    print("\ndirectory records (name, type=segment, u1, u2):")
    for r in dirs[:60]:
        seg = segs[r["u1"]] if r["u1"] < len(segs) else None
        print(f"  [{r['idx']:4d}] {r['name']!r:20s} type={r['type']:4d} seg={seg}")


if __name__ == "__main__":
    main()
