#!/usr/bin/env python3
"""The harness's per-unit byte-diff gate: the single seam of the matching rebuild.

Given a rebuilt unit (the bytes a toolchain produced for one section, module or
overlay) and the pinned corpus section it must reproduce, this reports

* **pass** — the bytes are identical,
* **fail** — they differ, with the located first difference (virtual address, file
  offset, word index, expected and actual words) or a length mismatch, or
* **incomplete** — a required input is missing (no section, no unit, no bytes).

The matched ledger counts only bytes of **game-owned** sections that actually
passed, so nothing approximately matched can ever be counted as matched. SDK
regions built from ps2sdk are `substitute region`s: reported, never counted.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from evidence_common import Incomplete, Invalid, sha256, write_result
from matching_sections import Section, pinned_executable, sections

MAX_UNIT_BYTES = 64 * 1024 * 1024


class Scope(str, Enum):
    """How a section is treated by the byte gate, from ADR-0005."""

    GAME_OWNED = "game_owned"
    MIXED = "mixed"  # game and SDK bytes interleave; reported, never counted as matched
    SUBSTITUTE_REGION = "substitute_region"
    EXCLUDED = "excluded"


# ADR-0005: no measurement places a whole section on one side of the boundary, so every
# loadable code/data section is mixed and the game-owned set is empty until a range-level
# attribution exists. Scope is recorded here, never declared by the caller of the gate.
METADATA = (".shstrtab", ".mdebug", ".reginfo", ".DVP.ovlytab", ".DVP.ovlystrtab")


def scope_of(name: str) -> Scope:
    if name in METADATA or name.startswith(".mdebug"):
        return Scope.EXCLUDED
    return Scope.MIXED


@dataclass(frozen=True)
class Verdict:
    status: str  # pass | fail | incomplete
    section: str | None
    scope: str | None
    matched_bytes: int
    section_bytes: int
    reason: str | None = None
    first_difference: dict | None = None

    def as_dict(self) -> dict:
        row = {"section": self.section, "scope": self.scope, "status": self.status,
               "reason": self.reason, "matched_bytes": self.matched_bytes,
               "section_bytes": self.section_bytes}
        if self.first_difference:
            row["first_difference"] = self.first_difference
        return row


def _incomplete(reason: str, section: str | None = None, scope: str | None = None,
                matched_bytes: int = 0, section_bytes: int = 0) -> Verdict:
    return Verdict("incomplete", section, scope, matched_bytes, section_bytes, reason)


def compare(section: Section | None, unit: bytes | None) -> Verdict:
    """Byte-diff one rebuilt unit against its pinned section."""
    if section is None:
        return _incomplete("no section for this unit")
    scope_value = scope_of(section.name).value
    if not section.has_bytes:
        return _incomplete("section has no file bytes (NOBITS)", section.name, scope_value,
                           section_bytes=section.size)
    if not unit:
        return _incomplete("no rebuilt unit", section.name, scope_value,
                           section_bytes=section.size)
    if len(unit) > MAX_UNIT_BYTES:
        raise Invalid(f"unit exceeds the {MAX_UNIT_BYTES} byte bound")
    shared = min(len(unit), section.size)
    if unit[:shared] == section.data[:shared]:
        if len(unit) == section.size:
            return Verdict("pass", section.name, scope_value, shared, section.size)
        return _fail(section, unit, scope_value, shared, shared, "length")
    matched = 0
    for at in range(0, shared, 4):
        if unit[at:at + 4] != section.data[at:at + 4]:
            return _fail(section, unit, scope_value, at, matched, "bytes")
        matched += len(section.data[at:at + 4])
    raise AssertionError("unreachable: prefix differs, so a word differs")


def compare_unit(name: str, address: int, file_offset: int, expected: bytes,
                 unit: bytes | None) -> Verdict:
    """Byte-diff one independently rebuilt unit against its pinned byte span.

    Overlay code is stored in the executable's load section rather than in its
    synthetic ELF overlay section, so callers provide the already validated
    source span and its location. Scope remains mixed until range attribution.
    """
    section = Section(name, address, file_offset, len(expected), expected,
                      sha256(expected))
    return compare(section, unit)


def _fail(section: Section, unit: bytes, scope: str, offset: int, matched: int,
          reason: str) -> Verdict:
    difference = {
        "offset": offset,
        "address": f"{section.address + offset:08x}",
        "file_offset": f"{section.offset + offset:08x}",
        "word": offset // 4,
        "expected": section.data[offset:offset + 4].hex(),
        "actual": unit[offset:offset + 4].hex(),
    }
    if reason == "length":
        difference.update(section_bytes=section.size, unit_bytes=len(unit))
    return Verdict("fail", section.name, scope, matched, section.size, reason, difference)


def ledger(results: dict[str, list[dict]]) -> dict:
    """Matched-byte accounting over game-owned sections only."""
    matched = owned = substitute = mixed = mixed_passed = 0
    for status, rows in results.items():
        for row in rows:
            scope = row["scope"]
            if scope == Scope.SUBSTITUTE_REGION.value:
                substitute += row["bytes"]
                continue
            if scope == Scope.MIXED.value:
                mixed += row["bytes"]
                mixed_passed += row["bytes"] if status == "passed" else 0
                continue
            if scope != Scope.GAME_OWNED.value:
                continue
            owned += row["bytes"]
            if status == "passed":
                matched += row["bytes"]
    return {"game_owned_bytes": owned, "matched_bytes": matched,
            "substitute_region_bytes": substitute,
            "substitute_disposition": ("substitute, not matched" if substitute
                                       else "no ranges attributed as substitute"),
            "mixed_bytes": mixed, "mixed_bytes_identical": mixed_passed,
            "matched_fraction": (matched / owned) if owned else 0.0}


def check(game: Path, units: Path) -> dict:
    """Run the gate over a directory of rebuilt units laid out as ``<section>.bin``."""
    data, provenance = pinned_executable(game)
    found = sections(data)
    verdicts, unrebuilt, no_file_bytes = [], [], []
    for name, section in sorted(found.items()):
        scope = scope_of(name)
        if scope is Scope.EXCLUDED:
            continue
        if not section.has_bytes:  # NOBITS or empty: nothing to byte-diff, listed not hidden
            no_file_bytes.append({"section": name, "scope": scope.value, "bytes": section.size})
            continue
        if "/" in name:
            raise Invalid(f"unsafe section name for a unit path: {name!r}")
        unit_path = units / (name + ".bin")
        if not unit_path.is_file():
            unrebuilt.append({"section": name, "scope": scope.value, "bytes": section.size})
            continue
        if unit_path.stat().st_size > MAX_UNIT_BYTES:
            raise Invalid(f"unit {unit_path.name} exceeds the {MAX_UNIT_BYTES} byte bound")
        verdicts.append(compare(section, unit_path.read_bytes()))
    grouped = {"passed": [], "failed": [], "incomplete": []}
    for verdict in verdicts:
        key = {"pass": "passed", "fail": "failed", "incomplete": "incomplete"}[verdict.status]
        grouped[key].append({"section": verdict.section, "scope": verdict.scope,
                             "bytes": verdict.section_bytes})
    details = {"provenance": provenance, "executable_sha256": sha256(data),
               "units_directory": str(units), "verdicts": [v.as_dict() for v in verdicts],
               "accounting": grouped, "ledger": ledger(grouped),
               "sections_without_a_unit": unrebuilt,
               "sections_without_file_bytes": no_file_bytes,
               "claim_limits": ["A pass means the rebuilt unit is byte-identical to the pinned section.",
                                "Mixed sections interleave game and SDK bytes (ADR-0005): identical bytes are "
                                "reported but never counted as matched.",
                                "A substitute region is reported and never counted as matched.",
                                "No compilation, linking or execution is performed by this gate."]}
    if not details["ledger"]["matched_bytes"]:
        details["note"] = ("status reflects byte identity of the supplied units only; matched_bytes is 0 "
                           "because no section is game-owned yet (ADR-0005)")
    if grouped["failed"]:
        raise Invalid(f"{len(grouped['failed'])} rebuilt units differ from the retail bytes", details)
    if not verdicts:
        raise Incomplete("no rebuilt unit was supplied", details)
    if grouped["incomplete"] or unrebuilt:
        raise Incomplete(f"{len(unrebuilt)} sections have no rebuilt unit and "
                         f"{len(grouped['incomplete'])} units are incomplete", details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="corpus root containing the pinned executable")
    parser.add_argument("units", type=Path, help="directory of rebuilt <section>.bin units")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/matching-gate"))
    args = parser.parse_args()
    return write_result(args.output, "matching-byte-gate",
                        lambda: check(args.game, args.units), [])


if __name__ == "__main__":
    raise SystemExit(main())
