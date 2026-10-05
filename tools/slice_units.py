#!/usr/bin/env python3
"""Write the retail section bytes as rebuilt units: the control inputs for the byte-diff gate.

    python3.14 tools/slice_units.py games/ford-racing-2 DIR                  # identical units: gate passes
    python3.14 tools/slice_units.py games/ford-racing-2 DIR --corrupt .text:0x1234   # one word changed: gate fails there

Writes `<section>.bin` for every byte-bearing section the gate scores (not metadata). Then run
`python3.14 tools/matching_diff.py games/ford-racing-2 DIR`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from evidence_common import Invalid
from matching_diff import Scope, scope_of
from matching_sections import Section, pinned_executable, sections


def slice_units(found: dict[str, Section], target: Path, corrupt: str | None = None) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, section in sorted(found.items()):
        if section.has_bytes and scope_of(name) is not Scope.EXCLUDED:
            (target / (name + ".bin")).write_bytes(section.data)
            written.append(name)
    if corrupt:
        name, _, offset = corrupt.rpartition(":")
        at = int(offset, 0)
        if name not in written or at + 4 > found[name].size:
            raise Invalid(f"--corrupt {corrupt} names no scored section byte range")
        unit = bytearray(found[name].data)
        unit[at:at + 4] = b"\xde\xad\xbe\xef"
        (target / (name + ".bin")).write_bytes(bytes(unit))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--corrupt", help="SECTION:OFFSET, replace four bytes with deadbeef")
    args = parser.parse_args()
    data, _ = pinned_executable(args.game)
    print(f"wrote {len(slice_units(sections(data), args.target, args.corrupt))} units to {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
