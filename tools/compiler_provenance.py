#!/usr/bin/env python3
"""Inventory an exact public source candidate; never infer package permission.

The fixed CLI decision describes the investigated source snapshot. A matching
version string and license filename are observations, not source/binary binding.
No caller-supplied source decision can clear historical acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import zipfile

from compiler_probe_recipe.build import DISTRIBUTIONS
from evidence_common import Incomplete, Invalid, identity, sha256, write_result


TARGET_VERSION = "2.96-ee-001003-1"
TARGET_CANDIDATE = "ee-gcc2.96"
DECISION = Path(__file__).resolve().parents[1] / "notes/evidence/fr2-compiler-provenance-continuation/source-candidate.json"


def inspect_source(archive: Path, decision: dict) -> dict:
    """Return measured inventory and independent reasons binding is incomplete."""
    details = {
        "target_version": TARGET_VERSION,
        "source_archive": identity(archive) if archive.is_file() else None,
        "inventory_status": "incomplete",
        "source_version": None,
        "version_relation": "unresolved",
        "members": {},
        "missing": [],
        "changed": [],
        "historical_binding_status": "incomplete",
        "redistribution_disposition": "unresolved",
        "matched_bytes": 0,
        "binding_reasons": ["No recorded distributor/source-build relation binds this source to the selected package."],
        "limitations": [
            "A version-compatible source and notice inventory do not bind a historical binary.",
            "This audit grants no package permission or ownership/matching credit.",
            "No source candidate was built and no game code was executed by this audit.",
        ],
    }
    if details["source_archive"] is None:
        details["missing"].append("source archive")
        return details
    if details["source_archive"] != decision["archive"]:
        details["changed"].append("source archive")
    try:
        with zipfile.ZipFile(archive) as package:
            names = package.namelist()
            for member, expected in decision["members"].items():
                name = decision["root"] + member
                if names.count(name) == 0:
                    details["missing"].append(member)
                    continue
                if names.count(name) != 1:
                    details["changed"].append(f"duplicate archive member: {member}")
                    continue
                data = package.read(name)
                observed = {"bytes": len(data), "sha256": sha256(data)}
                details["members"][member] = observed
                if observed != expected:
                    details["changed"].append(member)
                if member == decision["version_member"]:
                    # Exact bounded declaration; comments and extra declarations cannot
                    # supply a competing source version.
                    match = re.fullmatch(rb'\s*char\s*\*\s*version_string\s*=\s*"([^"\r\n]+)"\s*;\s*', data)
                    if match:
                        version = match.group(1).decode("ascii")
                        details["source_version"] = version
                        details["version_relation"] = "equal" if version == TARGET_VERSION else "mismatch"
            details["notice_inventory"] = {
                name: "present" if name in details["members"] else "missing"
                for name in decision["notice_members"]
            }
    except (zipfile.BadZipFile, RuntimeError, UnicodeError, OSError) as exc:
        details["changed"].append(f"source archive unreadable: {type(exc).__name__}")
    if not details["missing"] and not details["changed"]:
        details["inventory_status"] = "pass"
    if details["version_relation"] == "mismatch":
        details["binding_reasons"].append("Source version differs from the selected historical package.")
    elif details["version_relation"] == "unresolved":
        details["binding_reasons"].append("Source version declaration is missing or malformed.")
    if details["inventory_status"] != "pass":
        details["binding_reasons"].append("Source candidate identity or required material is missing or changed.")
    return details


def audit(tool_root: Path, source_archive: Path) -> dict:
    decision = json.loads(DECISION.read_text())
    details = inspect_source(source_archive, decision)
    archive_name, expected_hash = DISTRIBUTIONS[TARGET_CANDIDATE]
    binary_archive = tool_root / archive_name
    observed = identity(binary_archive) if binary_archive.is_file() else None
    details["selected_package"] = {
        "candidate": TARGET_CANDIDATE,
        "archive": archive_name,
        "expected_sha256": expected_hash,
        "observed": observed,
        "identity_status": "pass" if observed and observed["sha256"] == expected_hash else "incomplete",
    }
    if details["selected_package"]["identity_status"] != "pass":
        details["binding_reasons"].append("Selected compiler archive is missing or differs from its recorded pin.")
    if observed and observed["sha256"] != expected_hash:
        # A changed accepted tool input is a contradiction. Inventory the source
        # first so absence of that independent prerequisite cannot hide it.
        details["selected_package"]["identity_status"] = "fail"
        raise Invalid("selected compiler archive differs from its recorded pin", details)
    if details["changed"]:
        # The CLI uses an accepted fixed source snapshot. Changed pin/member
        # observations are contradictions, independently of absent package or
        # corresponding-source evidence. A historical version mismatch alone
        # is retained as incomplete because the source was not bound to it.
        raise Invalid("fixed source candidate differs from its recorded pin", details)
    raise Incomplete("historical compiler package/source binding remains unresolved", details)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool_root", type=Path)
    parser.add_argument("source_archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-provenance"))
    args = parser.parse_args(argv)
    # Missing/changing source and package inputs are accounted in details; they
    # must not hide one another by failing before the source inventory runs.
    return write_result(args.output, "compiler-provenance", lambda: audit(args.tool_root, args.source_archive),
                        [DECISION, Path(__file__)])


if __name__ == "__main__":
    sys.exit(main())
