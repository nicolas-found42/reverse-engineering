"""Bounds-checked parser for Sony PS2 IOP IRX metadata and link tables.

This records the literal numeric import indices and export offsets. It does not
apply IRX relocations or resolve function names from an API catalog.
"""
from __future__ import annotations

import hashlib
import re
import struct

from evidence_common import Invalid
from ps2_executables import parse_elf as parse_elf_base

IMPORT_MAGIC = 0x41E00000
EXPORT_MAGIC = 0x41C00000
SHT_IOPMOD = 0x70000080
MAX_LIBRARIES = 4096
MAX_LINKS = 65536
LIBRARY_NAME = re.compile(rb"[A-Za-z0-9_]{1,8}")


def _library_name(raw: bytes) -> str:
    name = raw.split(b"\0", 1)[0]
    if not LIBRARY_NAME.fullmatch(name) or any(raw[len(name) + 1 :]):
        raise Invalid("IOP library name is not a terminated 1-8 character identifier")
    return name.decode("ascii")


def parse_tables(text: bytes) -> tuple[list[dict], list[dict]]:
    """Read aligned import/export headers from a bounded `.text` payload."""
    scan_size = len(text) & ~3
    imports: list[dict] = []
    exports: list[dict] = []
    cursor = 0
    while cursor + 4 <= scan_size:
        word = struct.unpack_from("<I", text, cursor)[0]
        if word not in (IMPORT_MAGIC, EXPORT_MAGIC):
            cursor += 4
            continue
        if cursor + 20 > scan_size:
            raise Invalid("IOP library header is truncated at end of .text")
        reserved, version = struct.unpack_from("<II", text, cursor + 4)
        if reserved != 0:
            raise Invalid(f"IOP library header has nonzero reserved word at .text+{cursor:#x}")
        name = _library_name(text[cursor + 12 : cursor + 20])
        if version >> 16:
            raise Invalid(f"IOP library version word has nonzero reserved high bits for {name!r}")
        target = imports if word == IMPORT_MAGIC else exports
        if len(imports) + len(exports) >= MAX_LIBRARIES:
            raise Invalid("IOP text contains too many library records")
        record = {
            "library": name,
            "version": version & 0xFFFF,
            "table_text_offset": cursor,
            "links": [],
        }
        link_cursor = cursor + 20
        if word == IMPORT_MAGIC:
            terminated = False
            while link_cursor + 8 <= scan_size and len(record["links"]) < MAX_LINKS:
                jr_word, li_word = struct.unpack_from("<II", text, link_cursor)
                opcode = li_word >> 26
                if jr_word == 0 and li_word == 0:
                    terminated = True
                    link_cursor += 8
                    break
                if jr_word != 0x03E00008:
                    raise Invalid(f"invalid IOP import stub JR instruction {jr_word:#010x} for {name!r}")
                if opcode != 9 or (li_word >> 21) & 0x1F or (li_word >> 16) & 0x1F:
                    raise Invalid(f"invalid IOP import stub LI encoding {li_word:#010x} for {name!r}")
                record["links"].append({
                    "index": li_word & 0xFFFF,
                    "stub_text_offset": link_cursor,
                    "jr_word": f"0x{jr_word:08x}",
                    "li_word": f"0x{li_word:08x}",
                    "li_opcode": opcode,
                    "name_status": "unresolved; requires library/version/index catalog",
                })
                link_cursor += 8
            if not terminated:
                raise Invalid(f"unterminated or oversized IOP import table for {name!r}")
        else:
            terminated = False
            while link_cursor + 4 <= scan_size and len(record["links"]) < MAX_LINKS:
                offset = struct.unpack_from("<I", text, link_cursor)[0]
                if offset == 0:
                    terminated = True
                    link_cursor += 4
                    break
                record["links"].append({"offset": offset})
                link_cursor += 4
            if not terminated:
                raise Invalid(f"unterminated or oversized IOP export table for {name!r}")
        record["link_count"] = len(record["links"])
        target.append(record)
        cursor = link_cursor
    return imports, exports


def parse_elf(data: bytes) -> dict:
    """Validate one ELF32LE MIPS IRX and expose named sections safely."""
    elf = parse_elf_base(data)
    if elf["type"] != 0xFF80 or elf["machine"] != 8:
        raise Invalid("ELF is not a Sony IOP relocatable MIPS module (ET=0xff80, EM_MIPS)")
    sections: dict[str, dict] = {}
    iopmod_rows = []
    for section in elf["sections"]:
        name = section.get("name")
        if name in (".text", ".iopmod"):
            if name in sections:
                raise Invalid(f"duplicate required IRX section {name}")
            sections[name] = section
        if section["type"] == SHT_IOPMOD:
            iopmod_rows.append(section)
    if ".text" not in sections or ".iopmod" not in sections:
        raise Invalid("IRX is missing its .text or .iopmod section")
    if sections[".text"]["type"] != 1 or not sections[".text"]["flags"] & 4:
        raise Invalid("IRX .text is not a file-backed executable PROGBITS section")
    if sections[".iopmod"]["type"] != SHT_IOPMOD:
        raise Invalid("IRX .iopmod section does not use SHT_IOPMOD")
    if len(iopmod_rows) != 1:
        raise Invalid("IRX must have exactly one SHT_IOPMOD section")
    if iopmod_rows[0]["name"] != ".iopmod":
        raise Invalid("SHT_IOPMOD section is not named .iopmod")
    return {"elf": elf, "sections": sections, "iopmod_section": iopmod_rows[0]}


def parse_irx(data: bytes, *, source: str | None = None) -> dict:
    parsed = parse_elf(data)
    text_section = parsed["sections"][".text"]
    mod_section = parsed["sections"][".iopmod"]
    if text_section["size"] % 4:
        raise Invalid("IRX .text size is not four-byte aligned")
    if mod_section["size"] < 27:
        raise Invalid("IRX .iopmod section is too short for fixed metadata and name")
    mod_data = data[mod_section["offset"] : mod_section["offset"] + mod_section["size"]]
    id_address, entry_address, unknown, text_bytes, data_bytes, bss_bytes, version = struct.unpack_from(
        "<IIIIIIH", mod_data
    )
    raw_name = mod_data[26:]
    if b"\0" not in raw_name:
        raise Invalid("IRX module name is not NUL terminated in .iopmod")
    name_bytes = raw_name.split(b"\0", 1)[0]
    if not name_bytes or len(name_bytes) > 64 or any(byte < 0x20 or byte > 0x7E for byte in name_bytes):
        raise Invalid("IRX module name is not a bounded printable ASCII string")
    if text_bytes != text_section["size"]:
        raise Invalid(".iopmod declared text size differs from the .text section")
    text_start = text_section["offset"]
    text = data[text_start : text_start + text_section["size"]]
    imports, exports = parse_tables(text)
    result = {
        "source": source,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "elf_type": "0xff80",
        "machine": 8,
        "text": {"address": text_section["address"], "offset": text_start,
                 "size": text_section["size"]},
        "iopmod_section_type": f"0x{parsed['iopmod_section']['type']:08x}",
        "module": {"id_address": id_address, "entry_address": entry_address,
                   "gp_offset": unknown, "unknown": unknown, "text_bytes": text_bytes,
                   "data_bytes": data_bytes, "bss_bytes": bss_bytes,
                   "version": version, "name": name_bytes.decode("ascii")},
        "imports": imports,
        "exports": exports,
        "counts": {"import_libraries": len(imports),
                   "import_stubs": sum(x["link_count"] for x in imports),
                   "export_libraries": len(exports),
                   "export_links": sum(x["link_count"] for x in exports)},
        "claim_limits": [
            "Numeric import indices require a matching library/version/index catalog for function names.",
            "Export offsets are recorded, not resolved to verified callable function semantics.",
            "No IRX relocations are applied or validated by this parser.",
        ],
    }
    # Keep `unknown` as a compatibility alias for consumers of earlier receipts.
    return result
