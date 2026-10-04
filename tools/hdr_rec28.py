#!/usr/bin/env python3
"""Parse FILES.HDR as 1037 fixed 28-byte records: [16B slot][3 x u32].

Validates: slot starts with printable name+NUL for all records; u32 patterns.
Outputs notes/hdr-records.tsv.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HDR = ROOT / "games/ford-racing-2/extracted/FILES.HDR"

NAME_START = 0x188
REC = 28


def main() -> None:
    data = HDR.read_bytes()
    remain = len(data) - NAME_START
    n = remain // REC
    print(f"data after 0x{NAME_START:x}: {remain} bytes = {n} records of {REC} (remainder {remain % REC})")

    recs = []
    for i in range(n):
        base = NAME_START + i * REC
        rec = data[base : base + REC]
        slot = rec[:16]
        u = struct.unpack("<3I", rec[16:28])
        nul = slot.find(b"\x00")
        name = slot[:nul] if nul >= 0 else slot
        ok = all(32 <= b < 127 for b in name) and len(name) > 0
        recs.append({"idx": i, "base": base, "slot": slot, "name": name, "u": u, "ok": ok})

    bad = [r for r in recs if not r["ok"]]
    print(f"records with non-printable/non-NUL name: {len(bad)}")
    for r in bad[:10]:
        print(f"  @0x{r['base']:x} slot={r['slot'].hex(' ')}")

    print("\n=== first 60 records ===")
    for r in recs[:60]:
        nm = r["name"].decode("ascii", "replace")
        tail = r["slot"][len(r["name"]) + 1 :]
        u = [hex(x) for x in r["u"]]
        print(f"[{r['idx']:4d}] @0x{r['base']:05x} {nm!r:20s} tail={tail.hex(' '):24s} u={u}")

    print("\n=== last 15 records ===")
    for r in recs[-15:]:
        nm = r["name"].decode("ascii", "replace")
        tail = r["slot"][len(r["name"]) + 1 :]
        u = [hex(x) for x in r["u"]]
        print(f"[{r['idx']:4d}] @0x{r['base']:05x} {nm!r:20s} tail={tail.hex(' '):24s} u={u}")

    # stats on u32 fields
    u0 = Counter(r["u"][0] for r in recs)
    print(f"\nu[0] distribution: top 10 = {[(hex(k), v) for k, v in u0.most_common(10)]}")
    u1 = Counter(r["u"][1] for r in recs)
    print(f"u[1] top 10 = {[(hex(k), v) for k, v in u1.most_common(10)]}")
    u2 = Counter(r["u"][2] for r in recs)
    print(f"u[2] top 10 = {[(hex(k), v) for k, v in u2.most_common(10)]}")

    # slot tail stats
    tails = Counter(r["slot"][len(r["name"]) + 1 :].hex() for r in recs)
    print(f"\nslot-tail top 10: {tails.most_common(10)}")

    # write tsv
    out = ROOT / "notes/hdr-records.tsv"
    with out.open("w") as fh:
        fh.write("idx\tbase\tname\tslot_tail_hex\tu0\tu1\tu2\n")
        for r in recs:
            nm = r["name"].decode("ascii", "replace")
            tail = r["slot"][len(r["name"]) + 1 :].hex()
            fh.write(f"{r['idx']}\t0x{r['base']:x}\t{nm}\t{tail}\t" + "\t".join(hex(x) for x in r["u"]) + "\n")
    print(f"written {out}")


if __name__ == "__main__":
    main()
