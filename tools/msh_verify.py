#!/usr/bin/env python3
"""Verify .msh layout hypothesis across all pairs:

  header (12 bytes): [u32 self_size][u32 unk (0x24?)][u32 n]
  then n x 16-byte records: [u32 len][u32 unk][u32 start][u32 rate]
  Invariants: start[0]==0; start[i+1]==start[i]+len[i]; sum(len)==.msb size; start[n-1]+len[n-1]==msb size.
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
    n_ok = 0
    for msb in msbs:
        msh = find(msb.name.replace(".msb;1", ".msh;1"))
        if msh is None:
            print(f"{msb.name}: no .msh")
            continue
        data = msh.read_bytes()
        self_size, unk0, n = struct.unpack_from("<3I", data, 0)
        recs = []
        for i in range(n):
            off = 0x0C + 16 * i
            if off + 16 > len(data):
                recs.append(None)
                break
            recs.append(struct.unpack_from("<4I", data, off))
        starts = [r[2] for r in recs if r]
        lens = [r[0] for r in recs if r]
        rates = [r[3] for r in recs if r]
        starts_ok = starts[0] == 0 and all(starts[i + 1] == starts[i] + lens[i] for i in range(len(starts) - 1))
        end_ok = starts[-1] + lens[-1] == msb.stat().st_size
        size_echo_ok = self_size == len(data)
        rate_ok = all(r in (8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000) for r in rates)
        ok = starts_ok and end_ok
        n_ok += ok
        print(
            f"{msb.name:16s} msh={len(data):>5} self={self_size:>5} n={n:>3} chain={starts_ok} end={end_ok} "
            f"size_echo={size_echo_ok} rates_ok={rate_ok} rates={sorted(set(rates))[:6]} msb={msb.stat().st_size}"
        )
    print(f"\nchain+end verified: {n_ok}/{len(msbs)}")

    # .mih full dump for two files
    for name in ("house1.mih;1", "svnties1.mih;1", "ui.mih;1"):
        p = find(name)
        if not p:
            print(name, "not found")
            continue
        raw = p.read_bytes()
        u = struct.unpack(f"<{len(raw)//4}I", raw)
        print(f"\n{name} ({len(raw)}B): {[hex(x) for x in u]}")
        print(f"   as ints: {list(u)}")


if __name__ == "__main__":
    main()
