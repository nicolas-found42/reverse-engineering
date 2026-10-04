#!/usr/bin/env python3
"""Corrected .ps2 tree parse. Layout:

  u32 M        (leading field; semantics unresolved)
  u32 R        (number of root names)
  R x u32      root name offsets
  then repeated: [u32 count][count x u32 name offsets]  (child/group lists; count may be 0)
  the list region terminates exactly when the next word would be the first string in the pool
  (i.e. 4 * pos == min offset among all name offsets).

Validation per file: parse to terminator; check 4*pos == min(name offsets); report groups.
"""
from pathlib import Path

from evidence_common import Invalid
from format_contracts import model

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def main() -> int:
    ps2s = sorted(FILES.rglob("*.PS2;1")) + sorted(FILES.rglob("*.ps2;1"))
    good_n = 0
    for p in ps2s:
        try:
            parsed = model(p.read_bytes())
        except Invalid as exc:
            print(f'{p.name}: fail: {exc}')
            continue
        good_n += 1
        print(f"{p.name:20s} leading={parsed['leading_count']} R={len(parsed['roots'])} "
              f"groups={len(parsed['groups'])} names={len(parsed['names'])} "
              f"pool=0x{parsed['string_pool_start']:x} term=True geometry=not-decoded")
    print(f"\nterminator-verified: {good_n}/{len(ps2s)}")

    return 0 if ps2s and good_n == len(ps2s) else 1


if __name__ == "__main__":
    raise SystemExit(main())
