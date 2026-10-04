"""Literal candidate links between observed, base-zero IOP IRX modules.

The input is parsed from ELF bytes, never from asserted symbol names. This is
an offline crosswalk, not a loader or a runtime binding decision.
"""
from __future__ import annotations

from collections.abc import Iterable
import argparse
import hashlib
from pathlib import Path

from evidence_common import Invalid, write_result
from ps2_irx import parse_irx
from verify_irx import verify_corpus


def crosswalk(inputs: Iterable[tuple[str, bytes]]) -> dict:
    modules: dict[str, dict] = {}
    for key, payload in inputs:
        if not isinstance(key, str) or not key or key in modules:
            raise Invalid("observed modules require unique nonempty source keys")
        if not isinstance(payload, bytes):
            raise Invalid("observed modules must be supplied as immutable ELF bytes")
        parsed = parse_irx(payload, source=key)
        if parsed["text"]["address"] != 0:
            raise Invalid("observed crosswalk profile requires base-zero .text")
        modules[key] = parsed

    providers: dict[tuple[str, int, int], list[dict]] = {}
    export_tables = export_entries = 0
    for key, parsed in sorted(modules.items()):
        for table in parsed["exports"]:
            export_tables += 1
            for ordinal, link in enumerate(table["links"]):
                target = link["offset"]
                if target % 4 or not 0 <= target < parsed["text"]["size"]:
                    raise Invalid(f"observed export target outside aligned .text: {key}@{target:#x}")
                export_entries += 1
                candidate = {
                    "module_key": key, "module_sha256": parsed["sha256"],
                    "export_table_text_offset": table["table_text_offset"],
                    "ordinal": ordinal, "relative_target": target,
                }
                identity = (table["library"], table["version"], ordinal)
                providers.setdefault(identity, []).append(candidate)

    counts = {"unique_candidate": 0, "ambiguous_candidates": 0, "no_candidate": 0}
    edges = []
    for key, parsed in sorted(modules.items()):
        for table in parsed["imports"]:
            for link in table["links"]:
                identity = (table["library"], table["version"], link["index"])
                candidates = providers.get(identity, [])
                status = ("no_candidate" if not candidates else
                          "unique_candidate" if len(candidates) == 1 else "ambiguous_candidates")
                counts[status] += 1
                edges.append({
                    "importer": key, "importer_sha256": parsed["sha256"],
                    "library": identity[0], "version": identity[1], "ordinal": identity[2],
                    "stub_text_offset": link["stub_text_offset"], "status": status,
                    "candidates": candidates, "runtime_binding_verified": False,
                })
    return {
        "schema_version": 1, "module_count": len(modules), "import_stubs": len(edges),
        "export_tables": export_tables, "export_entries": export_entries,
        "counts": counts, "edges": edges,
        "policy": "exact observed library/full-version/positional-ordinal tuple only",
        "claim_limits": [
            "Candidate matches do not prove library registration, load order, or runtime binding.",
            "Aligned export targets inside .text do not prove callable entries or reachability.",
            "No relocations, API names, version compatibility, or missing providers are inferred.",
        ],
    }


def corpus(root: Path, inventory: Path, boundaries: Path) -> dict:
    """Reuse the exact 24-module provenance verifier before reading candidates."""
    inventory_bytes, boundary_bytes = inventory.read_bytes(), boundaries.read_bytes()
    verified = verify_corpus(root, inventory, boundaries)
    inputs = []
    for row in verified["modules"]:
        source = (root / row["source"]).resolve()
        if not source.is_relative_to(root.resolve()):
            raise Invalid("verified module path escaped the extracted root")
        payload = source.read_bytes()[row["offset"]:row["offset"] + row["bytes"]]
        if len(payload) != row["bytes"] or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise Invalid("verified module slice changed before crosswalk")
        inputs.append((f"{row['source']}@0x{row['offset']:x}", payload))
    result = crosswalk(inputs)
    if inventory.read_bytes() != inventory_bytes or boundaries.read_bytes() != boundary_bytes:
        raise Invalid("input inventories changed during crosswalk")
    result["input_inventory_sha256"] = hashlib.sha256(inventory_bytes).hexdigest()
    result["input_boundaries_sha256"] = hashlib.sha256(boundary_bytes).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--boundaries", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    return write_result(args.out, "IRX observed export crosswalk",
                        lambda: corpus(args.root, args.inventory, args.boundaries),
                        [args.inventory, args.boundaries])


if __name__ == "__main__":
    raise SystemExit(main())
