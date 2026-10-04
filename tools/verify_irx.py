#!/usr/bin/env python3
"""Verify exact IRX slices from the pinned ELF inventory and ROMDIR boundaries."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evidence_common import Incomplete, Invalid, write_result
from ps2_executables import parse_romdir
from ps2_irx import parse_irx


def _json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Incomplete(f"required {label} is missing: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f"cannot read {label}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise Invalid(f"{label} must be a JSON object")
    return value


def _local_path(root: Path, listed: str) -> Path:
    path = Path(listed)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root.resolve())
        except ValueError as exc:
            raise Invalid(f"inventory source path escapes extracted root: {listed}") from exc
    parts = path.parts
    if "extracted" in parts:
        parts = parts[parts.index("extracted") + 1 :]
    result = (root / Path(*parts)).resolve()
    if not result.is_relative_to(root.resolve()):
        raise Invalid(f"inventory source path escapes extracted root: {listed}")
    return result


def verify_corpus(root: Path, inventory_path: Path, boundaries_path: Path) -> dict:
    """Check every IRX candidate against its exact local source bytes and parse it."""
    if not root.is_dir():
        raise Incomplete(f"extracted root is missing: {root}")
    inventory = _json(inventory_path, "ELF inventory")
    boundaries = _json(boundaries_path, "ROMDIR boundary inventory")
    if not isinstance(inventory.get("elf_magic_candidates"), list):
        raise Invalid("ELF inventory is missing elf_magic_candidates")
    if not isinstance(boundaries.get("standalone"), list) or not isinstance(boundaries.get("modules"), list):
        raise Invalid("boundary inventory is missing standalone or embedded module lists")
    expected_root = inventory.get("root")
    if isinstance(expected_root, str) and Path(expected_root).resolve() != root.resolve():
        raise Invalid("requested extracted root differs from the root recorded in ELF inventory")

    candidates = [row for row in inventory["elf_magic_candidates"]
                  if isinstance(row, dict) and row.get("type") == 0xFF80]
    if len(candidates) != 24:
        raise Invalid(f"pinned inventory must contain 24 ET 0xff80 candidates, got {len(candidates)}")
    candidate_keys = set()
    candidates_by_source: dict[str, list[dict]] = {}
    for row in candidates:
        file_name = row.get("file")
        offset = row.get("offset")
        if not isinstance(file_name, str) or type(offset) is not int or offset < 0:
            raise Invalid("IRX candidate has an invalid source path or offset")
        if row.get("machine") != 8 or not row.get("valid_header"):
            raise Invalid(f"IRX candidate header is not valid MIPS: {file_name}@{offset:#x}")
        key = (file_name, offset)
        if key in candidate_keys:
            raise Invalid(f"duplicate IRX candidate in inventory: {file_name}@{offset:#x}")
        candidate_keys.add(key)
        candidates_by_source.setdefault(file_name, []).append(row)

    standalone_paths = {row.get("path") for row in boundaries["standalone"] if isinstance(row, dict)}
    standalone_candidates = [row for row in candidates if row.get("offset") == 0]
    if len(standalone_candidates) != 9:
        raise Invalid(f"pinned inventory must contain nine standalone IRX candidates, got {len(standalone_candidates)}")
    for row in standalone_candidates:
        if row["file"] not in standalone_paths:
            raise Invalid(f"standalone IRX is absent from boundary inventory: {row['file']}")
        boundary_row = next(item for item in boundaries["standalone"]
                            if isinstance(item, dict) and item.get("path") == row["file"])
        elf = boundary_row.get("elf")
        if (not isinstance(elf, dict) or elf.get("type") != 0xFF80
                or elf.get("machine") != 8 or elf.get("bytes") != row.get("file_bytes")
                or elf.get("sha256") != row.get("sha256")):
            raise Invalid(f"standalone IRX identity differs from boundary inventory: {row['file']}")

    embedded = boundaries["modules"]
    if len(embedded) != 15:
        raise Invalid(f"pinned ROMDIR boundary inventory must contain 15 modules, got {len(embedded)}")
    image_path = (root / "IRX" / "IOPRP255.IMG").resolve()
    if not image_path.is_file():
        raise Incomplete(f"embedded IRX image is missing: {image_path}")
    image_data = image_path.read_bytes()
    boundary_digest = hashlib.sha256(image_data).hexdigest()
    if (boundaries.get("bytes") != len(image_data)
            or boundaries.get("sha256") != boundary_digest):
        raise Invalid("IOPRP255.IMG identity differs from pinned ROMDIR boundary inventory")
    romdir = parse_romdir(image_data)
    actual_romdir = [(row["name"], row["offset"], row["bytes"], row["sha256"])
                     for row in romdir["modules"]]
    expected_romdir = [(row.get("name"), row.get("offset"), row.get("bytes"), row.get("sha256"))
                       for row in embedded]
    if actual_romdir != expected_romdir:
        raise Invalid("ROMDIR-derived module bounds differ from pinned boundary inventory")

    image_candidate_file = next((key[0] for key in candidate_keys if key[0].endswith("IOPRP255.IMG")), None)
    if not image_candidate_file:
        raise Invalid("ELF inventory has no IOPRP255.IMG IRX candidates")
    embedded_candidates = candidates_by_source.get(image_candidate_file, [])
    if len(embedded_candidates) != 15:
        raise Invalid(f"ELF inventory must list 15 embedded IRX candidates, got {len(embedded_candidates)}")
    expected_pairs = {(row["offset"], row["bytes"]) for row in embedded}
    actual_pairs = set()
    for row in embedded_candidates:
        match = next((item for item in embedded if item["offset"] == row["offset"]), None)
        if match is None:
            raise Invalid(f"embedded ELF candidate is absent from ROMDIR boundaries at {row['offset']:#x}")
        actual_pairs.add((row["offset"], match["bytes"]))
        if row.get("machine") != 8 or not row.get("valid_header"):
            raise Invalid(f"embedded IRX candidate header is not valid MIPS: {row['offset']:#x}")
    if actual_pairs != expected_pairs:
        raise Invalid("embedded ELF candidates do not cover exact ROMDIR module bounds")

    modules = []
    origin_paths: set[Path] = {image_path}
    for candidate in sorted(candidates, key=lambda row: (row["file"], row["offset"])):
        source = _local_path(root, candidate["file"])
        source = source if source.is_absolute() else (root / source).resolve()
        if not source.is_file():
            raise Incomplete(f"IRX candidate source is missing: {source}")
        source_data = source.read_bytes()
        if hashlib.sha256(source_data).hexdigest() != candidate.get("sha256"):
            raise Invalid(f"IRX candidate source file identity changed: {source}")
        if candidate.get("file_bytes") != len(source_data):
            raise Invalid(f"IRX candidate source byte count changed: {source}")
        origin_paths.add(source)
        offset = candidate["offset"]
        if source == image_path:
            boundary = next(row for row in embedded if row["offset"] == offset)
            size = boundary["bytes"]
            payload = source_data[offset : offset + size]
            name = boundary["name"]
            expected_digest = boundary["sha256"]
        else:
            if offset != 0:
                raise Invalid(f"standalone IRX candidate has nonzero offset: {source}@{offset:#x}")
            size = len(source_data)
            payload = source_data
            name = source.name
            expected_digest = candidate["sha256"]
        actual_digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != size or actual_digest != expected_digest:
            raise Invalid(f"IRX slice bounds/hash differ from pinned metadata: {source}@{offset:#x}")
        parsed = parse_irx(payload, source=str(source.relative_to(root.resolve())) + f"@0x{offset:x}")
        if parsed["sha256"] != actual_digest:
            raise Invalid(f"parsed IRX identity differs from exact source slice: {name}")
        modules.append({"name": name, "source": str(source.relative_to(root.resolve())),
                        "offset": offset, "bytes": size, "sha256": actual_digest,
                        "elf_type": parsed["elf_type"], "machine": parsed["machine"],
                        "iopmod_name": parsed["module"]["name"],
                        "iopmod_entry": parsed["module"]["entry_address"],
                        "counts": parsed["counts"]})

    if len(modules) != 24:
        raise Invalid(f"parsed IRX module count differs from pinned candidate count: {len(modules)}")
    totals = {key: sum(module["counts"][key] for module in modules)
              for key in ("import_libraries", "import_stubs", "export_libraries", "export_links")}
    return {
        "module_count": len(modules),
        "standalone_count": len(standalone_candidates),
        "romdir_module_count": len(embedded),
        "modules": modules,
        "totals": totals,
        "claim_limits": [
            "This inventory covers only the 24 ELF32LE MIPS ET 0xff80 IRX candidates in the pinned inventory.",
            "IRX import indices are numeric; function names need a matching IOP library/version/index catalog.",
            "Export offsets are recorded but not proven to be callable function entries.",
            "The parser does not apply Sony ET 0xff80 relocations or verify runtime GP values.",
            "IRX coverage does not establish whole-game code coverage or recovered source.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="exact extracted game root recorded by the inventory")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--boundaries", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = [args.inventory, args.boundaries]
    # write_result records the full hashes of every source container used by the check.
    if args.root.is_dir():
        inputs.extend(sorted({p for p in args.root.rglob("*") if p.is_file()
                              and (p.name == "IOPRP255.IMG" or p.suffix.upper() == ".IRX")}))
    return write_result(args.output, "iop-irx", lambda: verify_corpus(args.root, args.inventory, args.boundaries), inputs)


if __name__ == "__main__":
    raise SystemExit(main())
