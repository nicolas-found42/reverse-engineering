#!/usr/bin/env python3
"""Reproduce a bounded static coverage crosswalk for the FR2 EE export.

This reads the saved Ghidra inventory/coverage, pinned PS2Recomp-generated
source comments, and the original ELF bytes. It never runs guest code and only
prints bounded metadata; generated source bodies are not copied to the result.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".scratch/mesh/codex-root"
ELF = ROOT / "games/ford-racing-2/extracted/SLES_517.05"
INVENTORY = SCRATCH / "decompile-combined-3838-01/inventory.json"
COVERAGE = SCRATCH / "decompile-combined-3838-01/coverage.json"
GENERATED = SCRATCH / "recomp-fpu-01"
TARGET_CLUSTER = (0x001FBFB8, 0x001FC278)
TARGET_STARTS = (0x001FBFB8, 0x001FC0D0, 0x001FC118)
EXPECTED = {
    "elf_sha256": "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95",
    "inventory_sha256": "15488c325db2c87f6e5b08a93b07fe92daff9feb711dc12b4451d39a86dc98be",
    "coverage_sha256": "8b0041278f3a1f090bd30b668473f1daac08d90e60cdabbdac6142f88ff3dc2e",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_elf(path: Path) -> tuple[bytes, list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if data[:6] != b"\x7fELF\x01\x01":
        raise ValueError("input is not a 32-bit little-endian ELF")
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", data, 0)
    phoff, phentsize, phnum = header[5], header[9], header[10]
    segments = []
    for index in range(phnum):
        p_type, p_offset, p_vaddr, _paddr, p_filesz, _memsz, _flags, _align = struct.unpack_from(
            "<IIIIIIII", data, phoff + index * phentsize
        )
        if p_type == 1 and p_filesz:
            segments.append((p_vaddr, p_vaddr + p_filesz, p_offset))
    return data, segments


def bytes_at(data: bytes, segments: list[tuple[int, int, int]], address: int, size: int) -> bytes:
    for start, end, offset in segments:
        if start <= address and address + size <= end:
            file_offset = offset + address - start
            return data[file_offset : file_offset + size]
    raise ValueError(f"virtual address is not file-backed: 0x{address:08x}")


def main() -> None:
    for name, path in (("elf_sha256", ELF), ("inventory_sha256", INVENTORY), ("coverage_sha256", COVERAGE)):
        actual = sha256(path)
        if actual != EXPECTED[name]:
            raise SystemExit(f"input pin mismatch for {name}: {actual}")

    inventory = json.loads(INVENTORY.read_text())
    coverage = json.loads(COVERAGE.read_text())
    elf, segments = load_elf(ELF)

    generated_files = sorted(GENERATED.glob("sub_*.cpp"))
    generated_ranges: dict[int, tuple[int, int, str]] = {}
    generated_raw: dict[int, int] = {}
    comment_multiplicity: Counter[int] = Counter()
    range_pattern = re.compile(r"^// Address: 0x([0-9a-fA-F]+) - 0x([0-9a-fA-F]+)$")
    instruction_pattern = re.compile(r"^\s*// 0x([0-9a-fA-F]+): 0x([0-9a-fA-F]+)(?:\s|$)")
    call_pattern = re.compile(r"jal\s+func_([0-9a-fA-F]+)")
    generated_calls: dict[int, list[int]] = {}

    for path in generated_files:
        prefix = path.name.split("_")[1]
        start = int(prefix, 16)
        first_range: tuple[int, int] | None = None
        calls: set[int] = set()
        with path.open("r", errors="replace") as source:
            for line in source:
                match = range_pattern.match(line.rstrip("\n"))
                if match and first_range is None:
                    first_range = (int(match.group(1), 16), int(match.group(2), 16))
                match = instruction_pattern.match(line)
                if match:
                    address, raw = int(match.group(1), 16), int(match.group(2), 16)
                    generated_raw.setdefault(address, raw)
                    comment_multiplicity[address] += 1
                calls.update(int(target, 16) for target in call_pattern.findall(line))
        if first_range:
            generated_ranges[start] = (first_range[0], first_range[1], path.name)
            generated_calls[start] = sorted(calls)

    sorted_ranges = sorted((start, end) for start, end, _name in generated_ranges.values())
    range_starts = [start for start, _end in sorted_ranges]

    def generated_interval_contains(address: int) -> bool:
        index = bisect.bisect_right(range_starts, address) - 1
        return index >= 0 and sorted_ranges[index][0] <= address < sorted_ranges[index][1]

    inventory_functions = inventory["functions"]
    function_entries = {int(function["entry"], 16): function for function in inventory_functions}
    inventory_instructions = {
        int(instruction["address"], 16): {
            "raw": int.from_bytes(bytes.fromhex(instruction["bytes"]), "little"),
            "text": instruction["text"],
        }
        for function in inventory_functions
        for instruction in function["instructions"]
    }
    inventory_address_set = set(inventory_instructions)
    generated_address_set = set(generated_raw)
    missing_inventory_addresses = sorted(inventory_address_set - generated_address_set)
    mismatched_inventory_raw = [
        address
        for address in sorted(inventory_address_set & generated_address_set)
        if inventory_instructions[address]["raw"] != generated_raw[address]
    ]

    text = next(block for block in coverage["blocks"] if block["name"] == ".text")
    undefined_ranges = [
        (int(item["start"], 16), int(item["end"], 16))
        for item in text["undefined_ranges"]
        if "::" not in item["start"]
    ]
    undefined_starts = [start for start, _end in undefined_ranges]

    def is_undefined(address: int) -> bool:
        index = bisect.bisect_right(undefined_starts, address) - 1
        return index >= 0 and undefined_ranges[index][0] <= address <= undefined_ranges[index][1]

    call_sites: dict[int, list[dict[str, str]]] = defaultdict(list)
    for function in inventory_functions:
        for instruction in function["instructions"]:
            for reference in instruction.get("references", []):
                if reference.get("type") == "UNCONDITIONAL_CALL":
                    target = int(reference["to"], 16)
                    if is_undefined(target) and target in generated_ranges:
                        call_sites[target].append(
                            {
                                "caller": function["entry"],
                                "site": instruction["address"],
                                "text": instruction["text"],
                            }
                        )

    cluster = []
    for start in TARGET_STARTS:
        if start not in generated_ranges:
            raise SystemExit(f"expected generated function start missing: 0x{start:08x}")
        begin, end, filename = generated_ranges[start]
        if begin != start:
            raise SystemExit(f"generated header start mismatch for {filename}")
        instruction_addresses = sorted(
            address for address in generated_raw if begin <= address < end
        )
        expected_addresses = list(range(begin, end, 4))
        if any(address not in expected_addresses for address in instruction_addresses):
            raise SystemExit(f"generated instruction comment escapes the function range for {filename}")
        omitted_addresses = sorted(set(expected_addresses) - set(instruction_addresses))
        if any(int.from_bytes(bytes_at(elf, segments, address, 4), "little") != 0 for address in omitted_addresses):
            raise SystemExit(f"nonzero source word omitted from generated comments in {filename}")
        mismatches = [
            address
            for address in instruction_addresses
            if int.from_bytes(bytes_at(elf, segments, address, 4), "little") != generated_raw[address]
        ]
        if mismatches:
            raise SystemExit(f"raw instruction mismatch in {filename} at {mismatches[:4]}")
        cluster.append(
            {
                "entry": f"{start:08x}",
                "end_exclusive": f"{end:08x}",
                "bytes": end - begin,
                "instruction_words": len(expected_addresses),
                "nonzero_instruction_comments": len(instruction_addresses),
                "zero_words_without_instruction_comments": len(omitted_addresses),
                "omitted_zero_word_addresses": [f"{address:08x}" for address in omitted_addresses],
                "generated_file": filename,
                "generated_file_sha256": sha256(GENERATED / filename),
                "file_bytes": (GENERATED / filename).stat().st_size,
                "raw_words_match_original_elf": True,
                "direct_generated_call_targets_in_cluster": [
                    f"{target:08x}" for target in generated_calls.get(start, []) if TARGET_CLUSTER[0] <= target < TARGET_CLUSTER[1]
                ],
            }
        )

    if (cluster[0]["entry"], cluster[0]["end_exclusive"]) != ("001fbfb8", "001fc0d0"):
        raise SystemExit("unexpected first generated interval in candidate cluster")
    if (cluster[1]["entry"], cluster[1]["end_exclusive"]) != ("001fc0d0", "001fc118"):
        raise SystemExit("unexpected direct-call target interval in candidate cluster")
    if (cluster[2]["entry"], cluster[2]["end_exclusive"]) != ("001fc118", "001fc278"):
        raise SystemExit("unexpected last generated interval in candidate cluster")
    cluster_bytes = bytes_at(elf, segments, TARGET_CLUSTER[0], TARGET_CLUSTER[1] - TARGET_CLUSTER[0])

    unowned_ranges = text["unowned_instruction_ranges"]
    uncovered_unowned = []
    for item in unowned_ranges:
        start, end = int(item["start"], 16), int(item["end"], 16)
        uncovered_unowned.extend(address for address in range(start, end + 1, 4) if address not in generated_raw)
    uncovered_unowned_nonzero = [
        address
        for address in uncovered_unowned
        if int.from_bytes(bytes_at(elf, segments, address, 4), "little") != 0
    ]
    candidate = function_entries.get(0x0022A180)
    code_comments_raw_nonzero = Counter(
        "zero_nop" if inventory_instructions[address]["raw"] == 0 else "nonzero"
        for address in missing_inventory_addresses
        if address in inventory_instructions
    )
    opcode_fields: dict[str, Counter[int]] = defaultdict(Counter)
    vu_calls: Counter[int] = Counter()
    vu_waitq = 0
    for instruction in inventory_instructions.values():
        mnemonic = instruction["text"].split(" ", 1)[0].lower()
        raw = instruction["raw"]
        if mnemonic in {"mfc0", "mtc0", "cfc2", "ctc2"}:
            opcode_fields[mnemonic][(raw >> 11) & 0x1F] += 1
        elif mnemonic == "vcallms":
            vu_calls[(raw >> 6) & 0x1FF] += 1
        elif mnemonic == "vwaitq":
            vu_waitq += 1

    generated_marker_counts = Counter()
    marker_tokens = ("unhandled", "unsupported", "unimplemented", "not implemented", "todo_named", "throw std::runtime_error")
    for path in generated_files:
        content = path.read_text(errors="replace").lower()
        for marker in marker_tokens:
            generated_marker_counts[marker] += content.count(marker)

    result = {
        "schema_version": 1,
        "result": "PASS_BOUNDED_STATIC_AUDIT",
        "scope": "Static inventory/source crosswalk only; not semantic equivalence, runtime reachability proof, or whole-game completeness.",
        "provenance": {
            "executable": str(ELF.relative_to(ROOT)),
            "executable_bytes": len(elf),
            "executable_sha256": sha256(ELF),
            "ghidra_inventory": str(INVENTORY.relative_to(ROOT)),
            "ghidra_inventory_sha256": sha256(INVENTORY),
            "ghidra_coverage": str(COVERAGE.relative_to(ROOT)),
            "ghidra_coverage_sha256": sha256(COVERAGE),
            "generated_source_directory": str(GENERATED.relative_to(ROOT)),
            "generated_cpp_function_files": len(generated_files),
            "PS2Recomp_revision": "c5a9d02573410a2085a4b4b831b0b68ba3515440",
            "Ghidra_language": inventory["language"],
            "Ghidra_version": inventory["ghidra_version"],
        },
        "generated_crosswalk": {
            "ghidra_inventory_function_entries": len(function_entries),
            "function_entries_inside_generated_function_intervals": sum(
                generated_interval_contains(address) for address in function_entries
            ),
            "ghidra_instruction_addresses": len(inventory_address_set),
            "inventory_instruction_addresses_in_generated_comments": len(inventory_address_set & generated_address_set),
            "raw_word_mismatches_at_shared_addresses": len(mismatched_inventory_raw),
            "inventory_instruction_addresses_without_generated_comment": len(missing_inventory_addresses),
            "missing_inventory_instruction_categories": dict(code_comments_raw_nonzero),
            "text_unowned_instruction_ranges": len(unowned_ranges),
            "text_unowned_instruction_bytes": text["unowned_instruction_bytes"],
            "unowned_word_addresses_without_generated_comments": len(uncovered_unowned),
            "unowned_missing_comment_addresses_with_nonzero_raw_word": len(uncovered_unowned_nonzero),
            "generated_failure_or_unimplemented_marker_counts": dict(generated_marker_counts),
        },
        "measured_exceptional_opcode_fields": {
            "control_register_operand_counts": {name: {str(register): count for register, count in sorted(counts.items())} for name, counts in sorted(opcode_fields.items())},
            "vu0_vcallms_instruction_count": sum(vu_calls.values()),
            "vu0_vcallms_instruction_index_counts": {str(index): count for index, count in sorted(vu_calls.items())},
            "vu0_vcallmsr_instruction_count": sum(1 for item in inventory_instructions.values() if item["text"].split(" ", 1)[0].lower() == "vcallmsr"),
            "vu0_vwaitq_instruction_count": vu_waitq,
        },
        "undefined_called_generated_candidate": {
            "address": "001fc0d0",
            "ghidra_function_entry_present": "001fc0d0" in {f"{address:08x}" for address in function_entries},
            "containing_ghidra_undefined_range": {"start": "001fbfb8", "end_inclusive": "001fc277", "bytes": 704},
            "original_elf_window_sha256": hashlib.sha256(cluster_bytes).hexdigest(),
            "saved_unconditional_call_references": call_sites.get(0x001FC0D0, []),
            "generated_functions_exactly_covering_undefined_range": cluster,
            "cluster_total_bytes": sum(item["bytes"] for item in cluster),
            "cluster_total_instruction_words": sum(item["instruction_words"] for item in cluster),
        },
        "residual_executable_block_examples": {
            "text_defined_but_unowned_instructions": text["unowned_instruction_count"],
            "text_undefined_bytes": text["undefined_bytes"],
            "vutext_start": next(b["start"] for b in coverage["blocks"] if b["name"] == ".vutext"),
            "vutext_bytes": next(b["bytes"] for b in coverage["blocks"] if b["name"] == ".vutext"),
            "vutext_ee_instruction_count": next(b["instruction_count"] for b in coverage["blocks"] if b["name"] == ".vutext"),
            "note": "Unowned/undefined bytes and the VU-specific block need separate bounded analysis; their counts are not proof of omitted EE code.",
        },
        "candidate_leaf_not_in_generated_function_ranges": {
            "entry": "0022a180",
            "saved_inventory_name": candidate["name"] if candidate else None,
            "saved_inventory_size": candidate["size"] if candidate else None,
            "saved_callers": candidate["callers"] if candidate else None,
            "classification": "separate provisional Ghidra leaf; no inbound callers in saved inventory; lower priority than the direct-call gap",
        },
    }

    if mismatched_inventory_raw or uncovered_unowned_nonzero:
        result["result"] = "FAIL_MEASURED_MISMATCH"
        result["mismatched_inventory_raw_addresses"] = [f"{address:08x}" for address in mismatched_inventory_raw[:20]]
        result["uncovered_unowned_nonzero_addresses"] = [f"{address:08x}" for address in uncovered_unowned_nonzero[:20]]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
