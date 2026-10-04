"""Static, bounded model of the measured PS2 IOP ET 0xff80 relocation profile.

The profile and instruction arithmetic follow ps2sdk loadcore.c at commit
ac92a9f657d2e531dd8f060250b07f2a5ac6dea5. This module models bytes in memory;
it never calls, emulates, or executes a module entry point.
"""
from __future__ import annotations

import hashlib
import struct

from evidence_common import Invalid
import ps2_irx

ET_SCE_IOPRELEXEC = 0xFF80
EM_MIPS = 8
PT_LOAD = 1
PT_IOPMOD = 0x70000080
SHT_NULL = 0
SHT_SYMTAB = 2
SHT_RELA = 4
SHT_NOBITS = 8
SHT_REL = 9
SHF_ALLOC = 0x2
R_MIPS_32 = 2
R_MIPS_26 = 4
R_MIPS_HI16 = 5
R_MIPS_LO16 = 6
IOP_RAM_BYTES = 2 * 1024 * 1024
UINT32_MASK = 0xFFFFFFFF
SHT_PROGBITS = 1


def _u32(value: int) -> int:
    return value & UINT32_MASK


def _span(data: bytes, offset: int, size: int, label: str) -> bytes:
    if offset < 0 or size < 0 or offset > len(data) or size > len(data) - offset:
        raise Invalid(f"{label} span exceeds input")
    return data[offset : offset + size]


def _word(image: bytearray, offset: int) -> int:
    if offset % 4:
        raise Invalid(f"relocation site is not word aligned: {offset:#x}")
    if offset < 0 or offset > len(image) - 4:
        raise Invalid(f"relocation site is outside loaded image: {offset:#x}")
    return struct.unpack_from("<I", image, offset)[0]


def _put_word(image: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", image, offset, _u32(value))


def load_iop_irx(data: bytes, *, load_base: int) -> dict:
    """Create a relocated byte image for the measured IOP IRX loader profile.

    `load_base` is supplied explicitly and must place the whole PT_LOAD memory
    extent inside a synthetic 2 MiB IOP RAM window. Returned `image` is a new
    bytes object containing copied file data, zero-filled BSS, and relocation
    writes. Metadata addresses are the source loader's base-plus-offset values.
    """
    if type(data) is not bytes:
        raise TypeError("data must be bytes")
    if type(load_base) is not int or not 0 <= load_base < IOP_RAM_BYTES or load_base % 4:
        raise Invalid("load base must be a word-aligned address inside 2 MiB IOP RAM")

    parsed = ps2_irx.parse_irx(data)
    elf_result = ps2_irx.parse_elf(data)
    elf = elf_result["elf"]
    if elf["type"] != ET_SCE_IOPRELEXEC or elf["machine"] != EM_MIPS:
        raise Invalid("only ET_SCE_IOPRELEXEC ELF32LE MIPS modules are supported")
    if elf["program_count"] != 2 or elf["program_stride"] != 32:
        raise Invalid("profile requires exactly two 32-byte program headers")
    metadata_ph, load_ph = elf["programs"]
    if metadata_ph["type"] != PT_IOPMOD or load_ph["type"] != PT_LOAD:
        raise Invalid("profile requires IOPMOD metadata then one PT_LOAD program header")
    if metadata_ph["virtual_address"] != 0 or metadata_ph["physical_address"] != 0:
        raise Invalid("IOPMOD metadata program header must have zero virtual/physical addresses")
    if metadata_ph["alignment"] != 4 or metadata_ph["flags"] != 4 or metadata_ph["memory_size"] != 0:
        raise Invalid("IOPMOD metadata program header differs from the measured profile")
    if load_ph["virtual_address"] != 0 or load_ph["physical_address"] != 0:
        raise Invalid("PT_LOAD must be based at virtual and physical address zero")
    if load_ph["flags"] != 7 or load_ph["alignment"] != 16:
        raise Invalid("PT_LOAD flags/alignment differ from the measured profile")
    file_size, memory_size = load_ph["file_size"], load_ph["memory_size"]
    if file_size % 4 or memory_size % 4 or file_size > memory_size:
        raise Invalid("PT_LOAD file and memory sizes must be ordered word-aligned extents")
    if memory_size <= 0 or load_base + memory_size > IOP_RAM_BYTES:
        raise Invalid("synthetic load image does not fit inside 2 MiB IOP RAM")

    iopmod = elf_result["iopmod_section"]
    if (iopmod["offset"] != metadata_ph["offset"] or iopmod["size"] != metadata_ph["file_size"]
            or iopmod["address"] != 0 or iopmod["type"] != ps2_irx.SHT_IOPMOD):
        raise Invalid("IOPMOD section and first program header do not describe the same metadata")
    if metadata_ph["file_size"] < 27:
        raise Invalid("IOPMOD metadata is shorter than fixed fields plus module name")

    module = parsed["module"]
    if module["text_bytes"] % 4 or module["data_bytes"] % 4 or module["bss_bytes"] % 4:
        raise Invalid("IOPMOD text/data/BSS sizes must be word aligned")
    if module["text_bytes"] + module["data_bytes"] + module["bss_bytes"] != memory_size:
        raise Invalid("IOPMOD text/data/BSS sizes do not sum to PT_LOAD memory size")
    if module["text_bytes"] + module["data_bytes"] != file_size:
        raise Invalid("IOPMOD text/data sizes do not sum to PT_LOAD file size")
    entry_offset = module["entry_address"]
    module_id_offset = module["id_address"]
    gp_offset = module["gp_offset"]
    if entry_offset >= memory_size:
        raise Invalid("IOPMOD entry offset lies outside PT_LOAD memory")
    if module_id_offset != UINT32_MASK and module_id_offset >= memory_size:
        raise Invalid("IOPMOD module-ID offset lies outside PT_LOAD memory")
    if load_base + gp_offset > UINT32_MASK:
        raise Invalid("translated IOPMOD GP value overflows uint32")

    sections = elf["sections"]
    for idx, section in enumerate(sections):
        if section["flags"] & SHF_ALLOC:
            if section["address"] + section["size"] > memory_size:
                raise Invalid(f"allocated section {idx} exceeds PT_LOAD memory")
            if section["type"] == SHT_PROGBITS:
                if section["address"] + section["size"] > file_size:
                    raise Invalid(f"allocated PROGBITS section {idx} exceeds PT_LOAD file bytes")
                expected_offset = load_ph["offset"] + section["address"]
                if section["offset"] != expected_offset:
                    raise Invalid(f"allocated PROGBITS section {idx} does not map to its PT_LOAD file offset")
    text_section = elf_result["sections"][".text"]
    if text_section["address"] != 0 or text_section["offset"] != load_ph["offset"]:
        raise Invalid(".text must begin at the zero-based PT_LOAD file mapping")
    image = bytearray(memory_size)
    payload = _span(data, load_ph["offset"], file_size, "PT_LOAD file image")
    image[:file_size] = payload

    relocation_counts: dict[int, int] = {}
    relocation_total = 0
    all_relocation_sites: set[int] = set()
    for rel_index, rel_section in enumerate(sections):
        if rel_section["type"] == SHT_RELA and rel_section["size"]:
            raise Invalid("SHT_RELA sections are outside the measured IOP profile")
        if rel_section["type"] != SHT_REL or not rel_section["size"]:
            continue
        if rel_section["entry_size"] != 8 or rel_section["size"] % 8:
            raise Invalid(f"SHT_REL section {rel_index} must contain 8-byte entries")
        if rel_section["link"] >= len(sections) or sections[rel_section["link"]]["type"] != SHT_SYMTAB:
            raise Invalid(f"SHT_REL section {rel_index} does not link to a symbol table")
        if rel_section["info"] >= len(sections):
            raise Invalid(f"SHT_REL section {rel_index} target section index is invalid")
        target_section = sections[rel_section["info"]]
        if not target_section["flags"] & SHF_ALLOC:
            raise Invalid(f"SHT_REL section {rel_index} targets a non-allocated section")
        rel_bytes = _span(data, rel_section["offset"], rel_section["size"], f"SHT_REL section {rel_index}")
        entries = [struct.unpack_from("<II", rel_bytes, at) for at in range(0, len(rel_bytes), 8)]
        if len({offset for offset, _ in entries}) != len(entries):
            raise Invalid(f"SHT_REL section {rel_index} contains duplicate relocation sites")
        sites: set[int] = set()
        types: list[int] = []
        for offset, info in entries:
            symbol_index, reloc_type = info >> 8, info & 0xFF
            if symbol_index != 0:
                raise Invalid(f"relocation references unsupported symbol index {symbol_index}")
            if reloc_type not in (R_MIPS_32, R_MIPS_26, R_MIPS_HI16, R_MIPS_LO16):
                raise Invalid(f"unsupported MIPS relocation type {reloc_type}")
            if offset % 4:
                raise Invalid(f"relocation site is not word aligned: {offset:#x}")
            if offset > memory_size - 4:
                raise Invalid(f"relocation site is outside PT_LOAD memory: {offset:#x}")
            if not target_section["address"] <= offset <= target_section["address"] + target_section["size"] - 4:
                raise Invalid(f"relocation site {offset:#x} is outside its target section")
            if offset in sites:
                raise Invalid(f"duplicate relocation site {offset:#x}")
            if offset in all_relocation_sites:
                raise Invalid(f"relocation site is repeated across SHT_REL sections: {offset:#x}")
            sites.add(offset)
            all_relocation_sites.add(offset)
            types.append(reloc_type)
            relocation_counts[reloc_type] = relocation_counts.get(reloc_type, 0) + 1
        for idx, reloc_type in enumerate(types):
            if reloc_type == R_MIPS_HI16 and (idx + 1 >= len(types) or types[idx + 1] != R_MIPS_LO16):
                raise Invalid(f"HI16 relocation in section {rel_index} is not immediately followed by LO16")
            if reloc_type == R_MIPS_LO16 and (idx == 0 or types[idx - 1] != R_MIPS_HI16):
                raise Invalid(f"LO16 relocation in section {rel_index} is not immediately preceded by HI16")
        relocation_total += len(entries)

        for idx, (offset, info) in enumerate(entries):
            reloc_type = info & 0xFF
            original = _word(image, offset)
            if reloc_type == R_MIPS_32:
                _put_word(image, offset, original + load_base)
            elif reloc_type == R_MIPS_26:
                target = _u32(load_base + ((offset & 0xF0000000) | (4 * (original & 0x03FFFFFF))))
                _put_word(image, offset, (original & 0xFC000000) | ((target >> 2) & 0x03FFFFFF))
            elif reloc_type == R_MIPS_HI16:
                next_offset, _ = entries[idx + 1]
                low_word = _word(image, next_offset)
                low_signed = low_word & 0xFFFF
                if low_signed & 0x8000:
                    low_signed -= 0x10000
                combined = _u32(load_base + (original << 16) + low_signed)
                adjusted_high = (((combined >> 15) + 1) >> 1) & 0xFFFF
                _put_word(image, offset, (original & 0xFFFF0000) | adjusted_high)
            elif reloc_type == R_MIPS_LO16:
                _put_word(image, offset, (original & 0xFFFF0000) | ((load_base + original) & 0xFFFF))

    result_image = bytes(image)
    return {
        "profile": "measured-iop-et-ff80-single-load-zero-based-v1",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "load_base": load_base,
        "file_size": file_size,
        "memory_size": memory_size,
        "entry_offset": entry_offset,
        "entry_address": load_base + entry_offset,
        "module_id_offset": module_id_offset,
        "module_id_address": None if module_id_offset == UINT32_MASK else load_base + module_id_offset,
        "gp_offset": gp_offset,
        "gp_address": load_base + gp_offset,
        "relocation_counts": {str(k): relocation_counts[k] for k in sorted(relocation_counts)},
        "relocation_total": relocation_total,
        "load_image_sha256": hashlib.sha256(result_image).hexdigest(),
        "image": result_image,
        "claim_limits": "Static byte model only. It does not execute module code, resolve nonzero symbols, allocate real IOP memory, establish runtime loading order, or prove OS integration.",
    }
