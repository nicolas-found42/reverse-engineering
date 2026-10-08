#!/usr/bin/env python3
"""Deep probe of .ps2 (3D asset container) — validate the name-group offset-table layout.

FORDGT structure found: u32[0]=643 (name group count?), u32[1]=1, then [name][count][count x offsets]
from offset 8. Validate across all .ps2: parse (name, count, offsets) triples; measure:
- how many well-formed
- what u32[0] and u32[1] correlate with
- min/max of offset values, and whether (min_offset - table_end) tells where data starts
Also verify offsets stay in-bounds and monotonically increasing within a group.
"""
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def is_printable(b: int) -> bool:
    return 32 <= b < 127


def main() -> None:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    print(f"{len(ps2s)} files")
    summary = Counter()
    for p in ps2s:
        data = p.read_bytes()
        size = len(data)
        u0, u1 = struct.unpack_from("<2I", data, 0)
        pos = 8
        groups = []
        bad = False
        while pos < size:
            # expect a name here
            end = data.find(b"\x00", pos)
            if end < 0 or not (2 <= end - pos <= 40) or not all(is_printable(b) for b in data[pos:end]):
                break
            name = data[pos:end]
            # pad to 4
            pos2 = (end + 4) & ~3
            if pos2 + 4 > size:
                bad = True
                break
            (cnt,) = struct.unpack_from("<I", data, pos2)
            offs = []
            o = pos2 + 4
            for _ in range(cnt):
                if o + 4 > size:
                    bad = True
                    break
                (v,) = struct.unpack_from("<I", data, o)
                offs.append(v)
                o += 4
            groups.append((name.decode("ascii", "replace"), cnt, offs))
            pos = o
            if cnt == 0 and pos - pos2 > 1000:
                break
        data_start = min((min(g[2]) for g in groups if g[2]), default=None)
        ok = len(groups) >= 1 and not bad
        summary["files"] += 1
        summary["groups_total"] += len(groups)
        summary["ok"] += ok
        if len(groups) >= 3:
            mono = all(all(g[2][i] <= g[2][i + 1] for i in range(len(g[2]) - 1)) for g in groups if len(g[2]) > 1)
            summary["monotonic"] += mono
        if p.name in ("FORDGT.PS2;1", "COBRA.PS2;1", "debug.ps2;1", "misc.ps2;1", "BayA.PS2;1"):
            print(f"\n--- {p.name} size={size} u0={u0} u1={u1} groups={len(groups)} data_start={data_start}")
            for name, cnt, offs in groups[:12]:
                print(f"    {name!r:24s} cnt={cnt:4d} offs[0..4]={[hex(x) for x in offs[:4]]}")
            # how many bytes consumed by the table part?
            print(f"    table_end(pos)=0x{pos:x}  first_data_min={hex(data_start) if data_start else None}")
    print("\nsummary:", dict(summary))
    print("u1 distribution:", Counter(struct.unpack_from('<2I', p.read_bytes(), 0)[1] for p in ps2s).most_common(8))


if __name__ == "__main__":
    main()
