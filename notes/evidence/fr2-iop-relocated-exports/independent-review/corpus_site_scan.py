"""Summarize relocation types at loaded export-link sites for pinned 24-module IRX corpus."""
from __future__ import annotations

import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tools"))
from ps2_irx import parse_elf, parse_irx, parse_tables
from ps2_irx_relocations import SHT_REL, load_iop_irx
from verify_irx import verify_corpus

root = REPO / "games/ford-racing-2/extracted"
inventory = REPO / ".scratch/mesh/codex-root/executable-inventory-01.json"
boundaries = REPO / ".scratch/mesh/codex-root/executable-boundaries-01.json"
verified = verify_corpus(root, inventory, boundaries)
type_counts: collections.Counter[tuple[int, int, int]] = collections.Counter()
text_indexes: collections.Counter[int] = collections.Counter()
missing_r32 = []
modules = []
for row in verified["modules"]:
    source = (root / row["source"]).resolve()
    container = source.read_bytes()
    payload = container[row["offset"]:row["offset"] + row["bytes"]]
    irx = parse_irx(payload)
    elf = parse_elf(payload)["elf"]
    text_index = next(i for i, section in enumerate(elf["sections"])
                      if section.get("name") == ".text")
    text_indexes[text_index] += 1
    loaded = load_iop_irx(payload, load_base=0x1000)
    text = loaded["image"][:irx["text"]["size"]]
    _, exports = parse_tables(text)
    sites: dict[int, list[tuple[int, int, int]]] = {}
    for section in elf["sections"]:
        if section["type"] == SHT_REL and section["size"]:
            for at in range(section["offset"], section["offset"] + section["size"], 8):
                site, r_info = struct.unpack_from("<II", payload, at)
                site_types = (r_info & 0xFF, r_info >> 8, section["info"])
                sites.setdefault(site, []).append(site_types)
    row_counts: collections.Counter[str] = collections.Counter()
    for table in exports:
        for ordinal, _ in enumerate(table["links"]):
            site = table["table_text_offset"] + 20 + ordinal * 4
            site_types = sites.get(site, [])
            if not any(rel_type == 2 and symbol_index == 0 and target_section == text_index
                       for rel_type, symbol_index, target_section in site_types):
                missing_r32.append({"module": row["name"], "site": site,
                                    "types_and_target_sections": site_types,
                                    "text_section_index": text_index})
            for rel_type, symbol_index, target_section in site_types:
                type_counts[(rel_type, symbol_index, target_section, text_index)] += 1
                row_counts[f"type={rel_type},symbol={symbol_index},target_section={target_section}"] += 1
    modules.append({"name": row["name"], "source": row["source"],
                    "source_slice_sha256": row["sha256"], "text_section_index": text_index,
                    "loaded_export_entries": sum(t["link_count"] for t in exports),
                    "pointer_relocation_site_counts": dict(sorted(row_counts.items()))})

result = {
    "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
    "boundaries_sha256": hashlib.sha256(boundaries.read_bytes()).hexdigest(),
    "ps2sdk_commit": "ac92a9f657d2e531dd8f060250b07f2a5ac6dea5",
    "module_count": len(modules),
    "text_section_indexes": dict(sorted(text_indexes.items())),
    "loaded_export_entries": sum(m["loaded_export_entries"] for m in modules),
    "relocation_site_type_target_text_counts": [
        {"type": k[0], "symbol_index": k[1], "relocation_target_section": k[2], "text_section_index": k[3], "count": value}
        for k, value in sorted(type_counts.items())],
    "missing_zero_symbol_r_mips_32_sites": missing_r32,
    "modules": modules,
    "claim_limit": "Static byte counts for the pinned 24-module corpus; no module code or game runtime was executed."
}
print(json.dumps(result, indent=2))
