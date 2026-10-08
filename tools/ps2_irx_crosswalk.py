"""Literal candidate links between observed, base-zero IOP IRX modules.

The input is parsed from ELF bytes, never from asserted symbol names. This is
an offline crosswalk, not a loader or a runtime binding decision.
"""
from __future__ import annotations

from collections.abc import Iterable
import argparse
import hashlib
from pathlib import Path
import struct

from evidence_common import Invalid, write_result
from ps2_irx import parse_elf, parse_irx, parse_tables
from ps2_irx_relocations import load_iop_irx
from verify_irx import verify_corpus


def crosswalk(inputs: Iterable[tuple[str, bytes]], *, synthetic_load_base: int | None = None) -> dict:
    if synthetic_load_base is not None and (
            type(synthetic_load_base) is not int or synthetic_load_base <= 0):
        raise Invalid("relocation-aware view requires an explicit nonzero synthetic load base")
    modules: dict[str, dict] = {}
    relocation_views = []
    for key, payload in inputs:
        if not isinstance(key, str) or not key or key in modules:
            raise Invalid("observed modules require unique nonempty source keys")
        if not isinstance(payload, bytes):
            raise Invalid("observed modules must be supplied as immutable ELF bytes")
        parsed = parse_irx(payload, source=key)
        if parsed["text"]["address"] != 0:
            raise Invalid("observed crosswalk profile requires base-zero .text")
        if synthetic_load_base is not None:
            # Validate pointers visible in the literal view before relocation.
            # This rejects wraparound addends that could become a false zero.
            for table in parsed["exports"]:
                for link in table["links"]:
                    if link["offset"] % 4 or not 0 <= link["offset"] < parsed["text"]["size"]:
                        raise Invalid("literal export addend is outside aligned .text")
            loaded = load_iop_irx(payload, load_base=synthetic_load_base)
            imports, exports = parse_tables(loaded["image"][:parsed["text"]["size"]])
            identity = lambda tables: [(t["table_text_offset"], t["library"], t["version"]) for t in tables]
            if imports != parsed["imports"] or identity(exports) != identity(parsed["exports"]):
                raise Invalid("relocation changed import stubs or library header identities")
            sites: set[int] = set()
            for section in parse_elf(payload)["elf"]["sections"]:
                if section["type"] == 9:
                    for at in range(section["offset"], section["offset"] + section["size"], 8):
                        site, info = struct.unpack_from("<II", payload, at)
                        if info == 2:
                            sites.add(site)
            zeros = []
            for table in exports:
                terminator_site = table["table_text_offset"] + 20 + table["link_count"] * 4
                if terminator_site in sites:
                    raise Invalid("relocated export pointer wrapped into a false null terminator")
                for ordinal, link in enumerate(table["links"]):
                    site = table["table_text_offset"] + 20 + ordinal * 4
                    if site not in sites:
                        raise Invalid("observed export pointer lacks its R_MIPS_32 relocation")
                    raw_offset = struct.unpack_from("<I", payload, parsed["text"]["offset"] + site)[0]
                    if link["offset"] != raw_offset + synthetic_load_base:
                        raise Invalid("export pointer differs from the base-plus-addend model")
                    link["offset"] = raw_offset
                    if raw_offset == 0:
                        zeros.append(site)
            relocation_views.append({
                "module_key": key, "module_sha256": parsed["sha256"],
                "load_image_sha256": loaded["load_image_sha256"],
                "relocation_total": loaded["relocation_total"],
                "literal_export_entries": parsed["counts"]["export_links"],
                "relocated_export_entries": sum(t["link_count"] for t in exports),
                "relocated_zero_export_pointer_sites": zeros,
            })
            parsed["exports"] = exports
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
                    "pointer_relocation_verified": synthetic_load_base is not None,
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
    result = {
        "schema_version": 1, "module_count": len(modules), "import_stubs": len(edges),
        "export_tables": export_tables, "export_entries": export_entries,
        "counts": counts, "edges": edges,
        "runtime_state": {
            "status": "unobserved", "actual_load_bases": None,
            "registration_order": None,
            "reason": "Static module files do not establish loader allocation or registration order.",
        },
        "policy": "exact observed library/full-version/positional-ordinal tuple only",
        "claim_limits": [
            "Candidate matches do not prove library registration, load order, or runtime binding.",
            "Aligned export targets inside .text do not prove callable entries or reachability.",
            "No API names, version compatibility, or missing providers are inferred.",
        ],
    }
    if synthetic_load_base is not None:
        result["synthetic_load_base"] = synthetic_load_base
        result["relocation_views"] = sorted(relocation_views, key=lambda row: row["module_key"])
        result["claim_limits"].append(
            "Relocation uses an explicit synthetic base, not an observed runtime allocation; zero-pointer recovery relies on the measured IRX relocation profile.")
    return result


def corpus(root: Path, inventory: Path, boundaries: Path, *, synthetic_load_base: int | None = None) -> dict:
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
    result = crosswalk(inputs, synthetic_load_base=synthetic_load_base)
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
    parser.add_argument("--synthetic-load-base", type=lambda text: int(text, 0),
                        help="opt into the measured relocation view at an explicit nonzero synthetic base")
    args = parser.parse_args()
    return write_result(args.out, "IRX observed export crosswalk",
                        lambda: corpus(args.root, args.inventory, args.boundaries,
                                       synthetic_load_base=args.synthetic_load_base),
                        [args.inventory, args.boundaries])


if __name__ == "__main__":
    raise SystemExit(main())
