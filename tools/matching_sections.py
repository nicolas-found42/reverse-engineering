#!/usr/bin/env python3
"""Corpus-pinned section extraction for the matching-decompilation harness.

Extracts every named section of the pinned retail EE ELF as exact bytes with its
virtual address, file offset, size and SHA-256, so a rebuilt unit can be compared
against the retail bytes it must reproduce. The corpus identity gate is the one
already used by the batch guard (`corpus_contract.corpus_identity`): there is no
second identity mechanism.

Reading section boundaries only. No disassembly, no function discovery, no
assembly or linking, and no claim that any section is game-owned or SDK code.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, sha256, write_result
from ps2_executables import parse_elf

EXECUTABLE = "extracted/SLES_517.05"
MAX_SECTIONS = 4096
NOBITS = 8


@dataclass(frozen=True)
class Section:
    name: str
    address: int
    offset: int
    size: int
    data: bytes
    sha256: str

    @property
    def has_bytes(self) -> bool:
        return bool(self.data)

    def as_dict(self) -> dict:
        return {"section": self.name, "address": f"{self.address:08x}",
                "file_offset": f"{self.offset:08x}", "bytes": self.size,
                "has_file_bytes": self.has_bytes,
                "sha256": self.sha256}


def pinned_executable(game: Path) -> tuple[bytes, dict]:
    """Read the retail EE executable behind the corpus identity gate."""
    provenance = corpus_identity(game)
    path = game / EXECUTABLE
    if not path.is_file():
        raise Incomplete(f"pinned executable is missing: {path}")
    return path.read_bytes(), provenance


def sections(data: bytes) -> dict[str, Section]:
    """Every named section as exact bytes. Raises Incomplete when the ELF has no named section."""
    elf = parse_elf(data)
    found: dict[str, Section] = {}
    rows = elf["sections"]
    if len(rows) > MAX_SECTIONS:
        raise Invalid(f"section table exceeds the bounded profile of {MAX_SECTIONS}")
    for row in rows:
        name = row.get("name", "")
        if not name:
            continue
        if name in found:
            raise Invalid(f"duplicate section name in the section table: {name}")
        if row["type"] == NOBITS:
            payload = b""
        elif row["offset"] + row["size"] > len(data):
            raise Invalid(f"section {name} payload exceeds the file")
        else:
            payload = data[row["offset"]:row["offset"] + row["size"]]
        found[name] = Section(name, row["address"], row["offset"], row["size"],
                              payload, sha256(payload))
    if not found:
        raise Incomplete("the ELF carries no named sections")
    return found


def inventory(data: bytes) -> dict:
    found = sections(data)
    rows = [found[name].as_dict() for name in sorted(found)]
    measured = sum(row["bytes"] for row in rows if row["has_file_bytes"])
    return {"executable_sha256": sha256(data), "section_count": len(rows),
            "sections": rows, "file_backed_section_bytes": measured,
            "claim_limits": ["Section boundaries, bytes and hashes only.",
                             "Nothing here classifies a section as game-owned or SDK code.",
                             "Nothing here compiles, links or executes anything."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="corpus root containing the pinned executable")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/matching-sections"))
    args = parser.parse_args()

    def run() -> dict:
        data, provenance = pinned_executable(args.game)
        return {"provenance": provenance, **inventory(data)}

    return write_result(args.output, "matching-sections", run, [])


if __name__ == "__main__":
    raise SystemExit(main())