#!/usr/bin/env python3
"""Verify a Ghidra pseudocode export against a static function inventory.

This checks export provenance, address coverage, artifact integrity, and
decompiler output comments. It does not establish whole-game code discovery,
original-source recovery, or behavioral equivalence.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from evidence_common import Incomplete, Invalid, identity, write_result

CHECK = "decompilation"
WARNING_TOKEN = re.compile(r"\bWARNING\b", re.IGNORECASE)
MAX_MISSING_SAMPLE = 20
WARNING_CATEGORIES = (
    ("subroutine does not return", re.compile(r"subroutine does not return", re.I)),
    ("overlapping global symbols", re.compile(r"globals starting with .+ overlap smaller symbols", re.I)),
    ("unreachable block", re.compile(r"removing unreachable block", re.I)),
    ("infinite-loop do-nothing block", re.compile(r"do nothing block with infinite loop", re.I)),
    ("type propagation did not settle", re.compile(r"type propagation algorithm not settling", re.I)),
    ("decompiler restart limit", re.compile(r"exceeded maximum restarts", re.I)),
    ("decompiler restarted for space", re.compile(r"restarted to delay deadcode elimination", re.I)),
    ("case-label calculation failed", re.compile(r"calculation of case label failed", re.I)),
    ("heritage after dead-code removal", re.compile(r"heritage after dead removal", re.I)),
    ("possible position-independent-code construction", re.compile(r"possible pic construction", re.I)),
    ("overlapping instruction decode", re.compile(r"instruction .+ overlaps instruction", re.I)),
    ("jump-table recovery failed", re.compile(r"could not recover jumptable", re.I)),
    ("indirect jump treated as a call", re.compile(r"treating indirect jump as call", re.I)),
)


def _read_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f"cannot read {label}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise Invalid(f"{label} must be a JSON object")
    return value


def _c_comments(source: str):
    """Yield C comments while skipping string and character literal contents."""
    i, size = 0, len(source)
    while i < size:
        if source.startswith("//", i):
            end = source.find("\n", i + 2)
            if end < 0:
                end = size
            yield source[i:end]
            i = end
        elif source.startswith("/*", i):
            end = source.find("*/", i + 2)
            if end < 0:
                yield source[i:]
                return
            end += 2
            yield source[i:end]
            i = end
        elif source[i] in {"'", '"'}:
            quote = source[i]
            i += 1
            while i < size:
                if source[i] == "\\":
                    i += 2
                elif source[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
        else:
            i += 1


def _warning_category(comment: str) -> str:
    for label, pattern in WARNING_CATEGORIES:
        if pattern.search(comment):
            return label
    return "other warning"
def _entry(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{8}", value):
        raise Invalid(f"{label} is not an eight-digit function address")
    return value.lower()


def _count(value, label):
    if type(value) is not int or value < 0:
        raise Invalid(f"{label} must be a non-negative integer")
    return value


def _artifact_path(manifest_path: Path, relative: str, entry: str) -> Path:
    expected = f"functions/{entry}.c"
    if relative != expected:
        raise Invalid(f"unexpected pseudocode path for {entry}: {relative!r}")
    root = manifest_path.parent.resolve()
    artifact = (manifest_path.parent / relative).resolve()
    if not artifact.is_relative_to(root):
        raise Invalid(f"pseudocode path escapes export directory: {relative!r}")
    return artifact


def verify(manifest_path: Path, static_path: Path, executable_path: Path) -> dict:
    """Verify one export. Raises Invalid for contradictions and Incomplete for gaps."""
    manifest = _read_json(manifest_path, "decompilation manifest")
    static = _read_json(static_path, "static function inventory")
    if type(manifest.get("schema_version")) is not int or type(static.get("schema_version")) is not int or manifest["schema_version"] != 1 or static["schema_version"] != 1:
        raise Invalid("unsupported decompilation or static-export schema version")

    actual_executable = identity(executable_path)
    for label, value in (
        ("manifest program", manifest.get("program")),
        ("manifest language", manifest.get("language")),
        ("static program", static.get("program")),
        ("static language", static.get("language")),
    ):
        if not isinstance(value, str) or not value:
            raise Invalid(f"{label} must be non-empty text")
    if not (
        isinstance(manifest.get("executable_sha256"), str)
        and manifest["executable_sha256"] == static.get("executable_sha256")
        and manifest["executable_sha256"] == actual_executable["sha256"]
    ):
        raise Invalid("decompilation manifest, static inventory, and executable identities differ")
    if manifest.get("program") != static.get("program") or manifest.get("language") != static.get("language"):
        raise Invalid("decompilation manifest and static inventory program identity differ")

    static_rows = static.get("functions")
    if not isinstance(static_rows, list):
        raise Invalid("static inventory functions must be an array")
    expected = [_entry(row.get("entry"), "static function entry") for row in static_rows if isinstance(row, dict)]
    if len(expected) != len(static_rows):
        raise Invalid("static inventory contains a malformed function row")
    if len(set(expected)) != len(expected):
        raise Invalid("static inventory contains duplicate function addresses")
    if _count(static.get("inventory_count"), "static inventory_count") != len(expected) or not expected:
        raise Invalid("static inventory claimed count does not match its function rows")

    if _count(manifest.get("inventory_count"), "manifest inventory_count") != len(expected):
        raise Invalid("decompilation manifest claimed inventory_count differs from static inventory")
    scope = manifest.get("scope")
    if not isinstance(scope, str) or scope not in {"all saved functions", "selected entry addresses"}:
        raise Invalid("unknown decompilation scope")
    rows = manifest.get("functions")
    if not isinstance(rows, list):
        raise Invalid("decompilation functions must be an array")
    if _count(manifest.get("processed"), "manifest processed") != len(rows):
        raise Invalid("manifest processed count differs from function rows")
    if len(rows) > len(expected):
        raise Invalid("decompilation function rows exceed static inventory")

    entries = []
    status_counts = {"generated": 0, "failed": 0}
    generated_entries = set()
    failures = []
    warnings = []
    warning_category_counts = Counter()
    warning_category_entries = defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            raise Invalid("decompilation manifest contains a malformed function row")
        entry = _entry(row.get("entry"), "decompilation entry")
        entries.append(entry)
        if entry not in set(expected):
            raise Invalid(f"decompilation function address is absent from static inventory: {entry}")
        status = row.get("status")
        if not isinstance(status, str) or status not in status_counts:
            raise Invalid(f"unknown decompilation row status for {entry}: {status!r}")
        status_counts[status] += 1
        message = row.get("message", "")
        if not isinstance(message, str):
            raise Invalid(f"decompiler message for {entry} must be text")
        if status == "failed":
            failures.append({"entry": entry, "message": message})
            continue

        relative = row.get("path")
        if not isinstance(relative, str):
            raise Invalid(f"generated function {entry} has no artifact path")
        artifact = _artifact_path(manifest_path, relative, entry)
        try:
            data = artifact.read_bytes()
        except OSError as exc:
            raise Invalid(f"generated pseudocode is missing or unreadable for {entry}: {exc}") from exc
        digest = hashlib.sha256(data).hexdigest()
        if row.get("bytes") != len(data) or row.get("sha256") != digest:
            raise Invalid(f"generated pseudocode bytes or SHA-256 differ for {entry}")
        try:
            source = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Invalid(f"generated pseudocode is not UTF-8 for {entry}") from exc
        generated_entries.add(entry)
        for comment in _c_comments(source):
            if WARNING_TOKEN.search(comment):
                category = _warning_category(comment)
                warning_category_counts[category] += 1
                warning_category_entries[category].add(entry)
                warnings.append({"entry": entry, "text": comment})

    if len(set(entries)) != len(entries):
        raise Invalid("decompilation manifest contains duplicate function addresses")
    if _count(manifest.get("generated"), "manifest generated") != status_counts["generated"]:
        raise Invalid("manifest generated count differs from generated function rows")
    if _count(manifest.get("failed"), "manifest failed") != status_counts["failed"]:
        raise Invalid("manifest failed count differs from failed function rows")
    if len(generated_entries) != status_counts["generated"]:
        raise Invalid("generated address coverage does not match generated count")

    function_root = manifest_path.parent / "functions"
    recorded_paths = {
        _artifact_path(manifest_path, row["path"], _entry(row["entry"], "decompilation entry"))
        for row in rows
        if isinstance(row, dict) and row.get("status") == "generated" and isinstance(row.get("path"), str)
    }
    if function_root.exists():
        unlisted = [
            p for p in function_root.rglob("*.c")
            if p.resolve() not in recorded_paths
        ]
        if unlisted:
            raise Invalid(f"unlisted pseudocode artifacts found: {len(unlisted)}")

    actual_entries = set(entries)
    expected_entries = set(expected)
    missing = sorted(expected_entries - actual_entries) if scope == "all saved functions" else []
    if "missing_selected_entries" not in manifest:
        raise Invalid("manifest is missing missing_selected_entries")
    missing_selected = manifest["missing_selected_entries"]
    if not isinstance(missing_selected, list):
        raise Invalid("missing_selected_entries must be an array")
    normalized_selected_missing = [_entry(value, "missing selected entry") for value in missing_selected]
    if len(set(normalized_selected_missing)) != len(normalized_selected_missing):
        raise Invalid("missing_selected_entries contains duplicate addresses")
    if set(normalized_selected_missing) & actual_entries:
        raise Invalid("missing selected entries overlap processed function rows")

    terminal_reason = manifest.get("terminal_reason")
    manifest_status = manifest.get("status")
    if not isinstance(terminal_reason, str) or not terminal_reason:
        raise Invalid("manifest terminal_reason must be non-empty text")
    if manifest_status not in {"generated", "incomplete"}:
        raise Invalid("unknown manifest terminal status")
    internally_complete = (
        status_counts["failed"] == 0
        and not normalized_selected_missing
        and terminal_reason == "function iteration finished"
        and (scope != "all saved functions" or set(entries) == expected_entries)
    )
    expected_manifest_status = "generated" if internally_complete else "incomplete"
    if manifest_status != expected_manifest_status:
        raise Invalid("manifest status disagrees with failures, missing entries, or terminal reason")

    details = {
        "program": manifest["program"],
        "language": manifest["language"],
        "executable_sha256": actual_executable["sha256"],
        "static_inventory_sha256": identity(static_path)["sha256"],
        "manifest_sha256": identity(manifest_path)["sha256"],
        "inventory_count": len(expected),
        "processed_count": len(rows),
        "generated_count": status_counts["generated"],
        "failed_count": status_counts["failed"],
        "decompile_failures": failures,
        "failed_functions": failures,
        "missing_inventory_entry_count": len(missing),
        "missing_inventory_entry_sample": missing[:MAX_MISSING_SAMPLE],
        "missing_selected_entries": normalized_selected_missing,
        "warning_comment_count": len(warnings),
        "warning_comments": warnings,
        "warning_categories": [
            {
                "category": category,
                "count": count,
                "affected_function_count": len(warning_category_entries[category]),
                "entries": sorted(warning_category_entries[category]),
            }
            for category, count in sorted(
                warning_category_counts.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        "scope": scope,
        "terminal_reason": terminal_reason,
        "claim_limit": "Function inventory coverage is limited to the supplied static export; this check does not prove whole-game code discovery, original-source recovery, or behavioral equivalence.",
    }
    gaps = []
    if status_counts["failed"]:
        gaps.append(f"{status_counts['failed']} decompilation failures")
    if normalized_selected_missing:
        gaps.append(f"{len(normalized_selected_missing)} requested functions missing")
    if missing:
        gaps.append(f"{len(missing)} static inventory functions not present in export")
    if scope != "all saved functions":
        gaps.append("export scope is selected functions, not the full static inventory")
    if manifest_status != "generated":
        gaps.append("export manifest is incomplete")
    if gaps:
        details["status"] = "incomplete"
        details["failures"] = []
        raise Incomplete("; ".join(gaps), details)
    details["status"] = "pass"
    details["failures"] = []
    return details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--static-export", type=Path, default=Path(".scratch/evidence/static-export.json"))
    parser.add_argument("--executable", type=Path, default=Path("games/ford-racing-2/extracted/SLES_517.05"))
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/decompilation"))
    args = parser.parse_args()
    return write_result(
        args.output,
        CHECK,
        lambda: verify(args.manifest, args.static_export, args.executable),
        [args.manifest, args.static_export, args.executable],
    )


if __name__ == "__main__":
    raise SystemExit(main())
