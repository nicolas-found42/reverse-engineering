#!/usr/bin/env python3
"""Audit PS2Recomp function artifacts and their instruction comments.

The checked comments bind generated artifacts to file-backed EE instruction
words. They do not validate the translated C++ operations, discover original
function boundaries, or establish behavioral equivalence.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from evidence_common import Incomplete, Invalid, write_result
from ps2_executables import parse_elf
from verify_code_inventory import inspect as inspect_static
from verify_decompilation import _c_comments

FILE = re.compile(r"sub_([0-9A-F]{8})_0x([0-9a-f]+)\.cpp")
RANGE = re.compile(r"// Address: 0x([0-9a-f]+) - 0x([0-9a-f]+)\s*")
WORD = re.compile(r"// 0x([0-9a-f]+): 0x([0-9a-f]+)\s+.*")
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_FUNCTIONS = 100000


def audit(root: Path, executable: bytes, static: dict, report: str) -> dict:
    """Return artifact integrity and comparison metadata, never an equivalence claim."""
    # Validate the comparison oracle's byte identity before using its ownership.
    try:
        static_result = inspect_static(executable, static)
    except Incomplete as exc:
        if not exc.details.get("unique_instruction_count"):
            raise
        static_result = exc.details
    elf = parse_elf(executable)
    if elf["type"] != 2:
        raise Incomplete("artifact profile supports only an executable EE ELF")
    root = root.resolve()
    paths = sorted(root.glob("sub_*.cpp"))
    if not paths:
        raise Incomplete("no PS2Recomp function artifacts exist")
    if len(paths) > MAX_FUNCTIONS:
        raise Incomplete("artifact count exceeds bounded profile")
    expected = {int(row["entry"], 16) for row in static["functions"]}
    owned = {int(row["address"], 16) for fn in static["functions"] for row in fn["instructions"]}
    loads = [row for row in elf["programs"] if row["type"] == 1]
    ee_sections = [row for row in elf["sections"] if row["flags"] & 4
                   and row["type"] not in (0, 8, 0x7FFFF421)
                   and not row.get("name", "").startswith(".vutext")]
    if not ee_sections:
        raise Incomplete("EE executable section classification is unavailable")
    rows, seen, entries = [], {}, set()
    for path in paths:
        match = FILE.fullmatch(path.name)
        if not match or int(match[1], 16) != int(match[2], 16):
            raise Invalid("unexpected PS2Recomp artifact filename")
        if not path.resolve().is_relative_to(root):
            raise Invalid("artifact symlink escapes source directory")
        if path.stat().st_size > MAX_SOURCE_BYTES:
            raise Incomplete("source artifact exceeds bounded profile")
        raw_source = path.read_bytes()
        try:
            source = raw_source.decode("utf-8")
        except UnicodeError as exc:
            raise Invalid("source artifact is not UTF-8") from exc
        comments = list(_c_comments(source))
        ranges = [RANGE.fullmatch(comment) for comment in comments if RANGE.fullmatch(comment)]
        if len(ranges) != 1:
            raise Invalid("function artifact must contain one address range comment")
        span = ranges[0]
        assert span is not None
        start, end = int(span[1], 16), int(span[2], 16)
        if start != int(match[1], 16) or start % 4 or end % 4 or not 0 <= start < end <= 0x100000000:
            raise Invalid("artifact filename and aligned address range disagree")
        if start in entries:
            raise Invalid("duplicate generated function entry")
        entries.add(start)
        words = {}
        for comment in comments:
            item = WORD.fullmatch(comment)
            if not item:
                continue
            address, word = int(item[1], 16), int(item[2], 16)
            if address % 4 or not start <= address < end or not 0 <= word <= 0xFFFFFFFF:
                raise Invalid("instruction comment is unaligned or outside its function range")
            sections = [row for row in ee_sections if row["address"] <= address
                        and address + 4 <= row["address"] + row["size"]]
            if len(sections) != 1:
                raise Invalid("instruction comment is outside or ambiguously in EE executable sections")
            section = sections[0]
            offset = section["offset"] + address - section["address"]
            mapped = [row for row in loads if row["virtual_address"] <= address
                      and address + 4 <= row["virtual_address"] + row["file_size"]
                      and offset == row["offset"] + address - row["virtual_address"]]
            if len(mapped) != 1:
                raise Invalid("instruction section and ELF LOAD mappings disagree")
            if int.from_bytes(executable[offset:offset + 4], "little") != word:
                raise Invalid(f"instruction comment differs from original ELF at {address:#x}")
            if address in seen and seen[address] != word:
                raise Invalid("instruction comments disagree between artifacts")
            words[address] = word
            seen[address] = word
        if start not in words:
            raise Invalid("function entry is absent from validated instruction comments")
        rows.append({"entry": f"{start:08x}", "end": f"{end:08x}", "path": path.name,
                     "bytes": len(raw_source), "sha256": hashlib.sha256(raw_source).hexdigest(),
                     "commented_instruction_count": len(words),
                     "saved_entry": start in expected, "saved_owned_entry": start in owned,
                     "comments_outside_saved_inventory": len(set(words) - owned)})
    counts = {}
    for label in ("Functions discovered", "Generated functions", "Unhandled instructions"):
        values = re.findall(r"^" + re.escape(label) + r": (\d+)\s*$", report, re.M)
        if len(values) != 1:
            raise Invalid(f"report must contain exactly one {label} counter")
        counts[label] = int(values[0])
    processed = re.findall(r"^Functions processed: (\d+), recompiled: (\d+), stubs: (\d+), skipped: (\d+), decode failures: (\d+)\s*$", report, re.M)
    if len(processed) != 1:
        raise Invalid("report processing counters are missing or ambiguous")
    processed_counts = list(map(int, processed[0]))
    if any(counts[label] != len(paths) for label in ("Functions discovered", "Generated functions")) or processed_counts[:2] != [len(paths)] * 2:
        raise Invalid("report function counters disagree with generated artifacts")
    if any(processed_counts[2:]) or counts["Unhandled instructions"]:
        raise Incomplete("stubs, skips, decode failures, or unhandled instructions remain")
    warning_counts = re.findall(r"^Warnings: (\d+), errors: (\d+)\s*$", report, re.M)
    if len(warning_counts) != 1:
        raise Invalid("report warning/error counters are missing or ambiguous")
    warnings, errors = map(int, warning_counts[0])
    if errors:
        raise Invalid("generator report contains errors")
    new = [row for row in rows if not row["saved_entry"]]
    classes = Counter("owned_interior" if row["saved_owned_entry"] else "unowned" for row in new)
    return {"executable_sha256": elf["sha256"], "saved_inventory_count": len(expected),
            "generated_function_count": len(rows), "report_warning_count": warnings,
            "unique_commented_instructions": len(seen), "new_commented_instructions": len(set(seen) - owned),
            "saved_instructions_absent_from_comments": len(owned - set(seen)),
            "new_entry_count": len(new), "new_entry_classes": dict(classes),
            "saved_entries_absent_from_generated_starts": [f"{x:08x}" for x in sorted(expected - entries)],
            "static_inventory_unlisted_bytes": static_result.get("unlisted_executable_bytes", 0),
            "functions": rows, "whole_game_decompiled": False,
            "claim_limits": ["Instruction comments match the original ELF; translated operation semantics remain unverified.",
                             "Generated function boundaries and fallback entries are heuristic candidates.",
                             "Compilation, linking, runtime support, original source, and behavior need separate evidence."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--static-export", type=Path, required=True)
    parser.add_argument("--generator-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/recompilation"))
    args = parser.parse_args()
    return write_result(args.output, "recompilation-artifacts",
                        lambda: audit(args.source, args.executable.read_bytes(),
                                      json.loads(args.static_export.read_text()), args.generator_report.read_text()),
                        [args.executable, args.static_export, args.generator_report])


if __name__ == "__main__":
    raise SystemExit(main())
