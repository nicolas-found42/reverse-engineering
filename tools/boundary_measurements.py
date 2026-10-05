#!/usr/bin/env python3
"""Derive the measurements ADR-0005 cites: source-path strings and Sony SDK stamps per section.

    python3.14 tools/boundary_measurements.py games/ford-racing-2 --output notes/evidence/fr2-matching-harness/results

A path counts once, only when it starts a NUL-terminated string (`../<root>/….c|cpp|s`), so
duplicates and mid-string fragments are not counted. Nothing here places an address range on
the game or SDK side: it counts strings and the section that holds each one.
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from evidence_common import write_result
from matching_sections import pinned_executable, sections

PATH = re.compile(rb"(?<![\x20-\x7e])\.\./([\x20-\x7e]{3,90}?)\.(?:c|cpp|s|S)\x00")
STAMP = re.compile(rb"PsII([a-z0-9 ]{8})[0-9]{4}")


def _section_of(found: dict, offset: int) -> str | None:
    for name, section in found.items():
        if section.has_bytes and section.offset <= offset < section.offset + section.size:
            return name
    return None


def measure(data: bytes) -> dict:
    found = sections(data)
    seen, by_prefix, path_sections = set(), Counter(), Counter()
    for match in PATH.finditer(data):
        text = match.group(0).decode("ascii")
        if text in seen:
            continue
        seen.add(text)
        by_prefix[text.split("/")[1]] += 1
        path_sections[_section_of(found, match.start())] += 1
    stamp_sections, libraries, total = Counter(), set(), 0
    for match in STAMP.finditer(data):
        total += 1
        stamp_sections[_section_of(found, match.start())] += 1
        libraries.add(match.group(1).decode().strip())
    return {"source_paths": {"distinct": len(seen), "by_prefix": dict(by_prefix),
                             "by_section": dict(path_sections)},
            "sdk_stamps": {"total": total, "by_section": dict(stamp_sections),
                           "libraries": sorted(libraries)},
            "reproduce": "python3.14 tools/boundary_measurements.py <corpus> --output <dir>",
            "claim_limits": ["Counts strings and the section holding each; no address range is "
                             "attributed to the game or the SDK."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/boundary"))
    args = parser.parse_args()

    def run() -> dict:
        data, provenance = pinned_executable(args.game)
        return {"provenance": provenance, **measure(data)}

    return write_result(args.output, "boundary-measurements", run, [])


if __name__ == "__main__":
    raise SystemExit(main())
