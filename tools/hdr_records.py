#!/usr/bin/env python3
"""Systematic FILES.HDR name-region parser.

Finds NUL-terminated printable names, treats consecutive name offsets as record
spans, splits each span into [name+NUL pad4][payload], then reports payload
length + content statistics per record class.
"""
import re
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HDR = ROOT / "games/ford-racing-2/extracted/FILES.HDR"


def main() -> None:
    data = HDR.read_bytes()
    names = [(m.start(), m.end(), m.group()[:-1]) for m in re.finditer(rb"[\x21-\x7e]{2,}\x00", data)]
    # filter: keep names whose start >= 0x188 (real name region) — actually check all
    print(f"total NUL-terminated names: {len(names)}")

    # record spans between consecutive names
    recs = []
    for i, (s, e, name) in enumerate(names):
        nxt = names[i + 1][0] if i + 1 < len(names) else len(data)
        name_pad_end = (e + 3) & ~3  # pad name+NUL to 4
        payload = data[name_pad_end:nxt]
        recs.append((s, e, name, name_pad_end, nxt, payload))

    # payload length histogram
    lens = Counter(len(r[5]) for r in recs)
    print("payload length histogram:", lens.most_common(20))

    # print first 70 records: name, paylen, payload hex
    for s, e, name, pe, nxt, payload in recs[:70]:
        try:
            nm = name.decode()
        except UnicodeDecodeError:
            nm = name.hex()
        print(f"@{s:05x} name={nm!r:20s} pay@{pe:05x} paylen={len(payload):3d} hex={payload.hex(' ')} span={nxt-s}")

    # group by payload length and check patterns
    print("\n=== per-paylen sample payloads ===")
    by_len = {}
    for r in recs:
        by_len.setdefault(len(r[5]), []).append(r)
    for L, rs in sorted(by_len.items()):
        print(f"paylen={L}: {len(rs)} records; samples:")
        for r in rs[:6]:
            print(f"    {r[2]!r:24s} {r[5].hex(' ')}")

    with (ROOT / "notes/hdr-records.tsv").open("w") as fh:
        fh.write("offset\tname\tpayload_offset\tpayload_len\tpayload_hex\n")
        for s, e, name, pe, nxt, payload in recs:
            nm = name.decode("ascii", "replace")
            fh.write(f"0x{s:x}\t{nm}\t0x{pe:x}\t{len(payload)}\t{payload.hex()}\n")
    print(f"\nwritten {ROOT/'notes/hdr-records.tsv'} ({len(recs)} records)")


if __name__ == "__main__":
    main()
