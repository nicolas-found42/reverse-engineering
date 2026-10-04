#!/usr/bin/env python3
"""Verify .msh layout hypothesis across all pairs:

  header (12 bytes): [u32 self_size][u32 unk (0x24?)][u32 n]
  then n x 16-byte records: [u32 len][u32 unk][u32 start][u32 rate]
  Invariants: start[0]==0; start[i+1]==start[i]+len[i]; sum(len)==.msb size; start[n-1]+len[n-1]==msb size.
"""
import struct
from pathlib import Path

from evidence_common import Invalid
from format_contracts import bank

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def find(name: str) -> Path | None:
    hits = list(FILES.rglob(name))
    return hits[0] if hits else None


def main() -> int:
    msbs = sorted(FILES.rglob("*.msb;1"))
    n_ok = 0
    for msb in msbs:
        msh = find(msb.name.replace(".msb;1", ".msh;1"))
        if msh is None:
            print(f"{msb.name}: no .msh")
            continue
        data = msh.read_bytes()
        try:
            parsed = bank(data, msb.read_bytes())
        except Invalid as exc:
            print(f'{msb.name}: fail: {exc}')
            continue
        self_size, n = parsed['self_size'], parsed['count']
        rates = [record['rate'] for record in parsed['descriptors']]
        starts_ok = end_ok = size_echo_ok = True
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

    return 0 if msbs and n_ok == len(msbs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
