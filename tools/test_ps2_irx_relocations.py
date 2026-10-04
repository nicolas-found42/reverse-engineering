"""Synthetic checks for the measured static IOP IRX load/relocation model."""
from __future__ import annotations

import hashlib
import struct
import unittest

from evidence_common import Invalid
import ps2_irx
import ps2_irx_relocations as subject


def build_irx(*, words=None, text_relocations=None, bss_relocations=None,
              elf_type=0xFF80, program_count=2, load_vaddr=0, load_memory_size=32,
              module_id=8, module_gp=24, module_text=16, module_data=0, module_bss=16) -> bytes:
    """Build one tiny measured-profile IRX entirely from synthetic words."""
    if words is None:
        words = (0x00000100, 0x08000040, 0x3C081234, 0x24847800)
    if text_relocations is None:
        text_relocations = ((0, 2), (4, 4), (8, 5), (12, 6))
    if bss_relocations is None:
        bss_relocations = ((16, 2),)

    ident = b"\x7fELF\x01\x01\x01" + bytes(9)
    data = bytearray(52)
    data[:16] = ident
    program_offset = 52
    data.extend(bytes(64))
    metadata_offset = len(data)
    module = struct.pack("<IIIIIIH", module_id, 4, module_gp, module_text, module_data, module_bss, 0x0101) + b"test\0"
    assert len(module) == 31
    data.extend(module)
    while len(data) < 160:
        data.append(0)
    load_offset = len(data)
    load = struct.pack("<4I", *words)
    data.extend(load)
    text_rel_offset = len(data)
    data.extend(b"".join(struct.pack("<II", off, typ) for off, typ in text_relocations))
    bss_rel_offset = len(data)
    data.extend(b"".join(struct.pack("<II", off, typ) for off, typ in bss_relocations))
    symtab_offset = len(data)
    strtab_offset = symtab_offset
    strtab = b"\0"
    data.extend(strtab)
    shstr = b"\0.iopmod\0.text\0.bss\0.rel.text\0.rel.bss\0.symtab\0.strtab\0.shstrtab\0"
    shstr_offset = len(data)
    data.extend(shstr)
    section_offset = (len(data) + 3) & ~3
    data.extend(bytes(section_offset - len(data)))

    names = {name: shstr.index(name.encode()) for name in (
        ".iopmod", ".text", ".bss", ".rel.text", ".rel.bss", ".symtab", ".strtab", ".shstrtab")}
    # 0=null, 1=.iopmod, 2=.text, 3=.bss, 4=.rel.text, 5=.rel.bss,
    # 6=.symtab, 7=.strtab, 8=.shstrtab.
    data.extend(bytes(9 * 40))
    def sh(index, name, kind, flags, address, offset, size, link=0, info=0, align=4, entsize=0):
        struct.pack_into("<10I", data, section_offset + index * 40,
                         names[name] if name else 0, kind, flags, address, offset, size,
                         link, info, align, entsize)
    sh(1, ".iopmod", ps2_irx.SHT_IOPMOD, 0, 0, metadata_offset, len(module), align=4)
    sh(2, ".text", 1, 6, 0, load_offset, len(load), align=16)
    sh(3, ".bss", 8, 3, 16, 0, 16, align=16)
    sh(4, ".rel.text", 9, 0, 0, text_rel_offset, 8 * len(text_relocations), link=6, info=2, entsize=8)
    sh(5, ".rel.bss", 9, 0, 0, bss_rel_offset, 8 * len(bss_relocations), link=6, info=3, entsize=8)
    sh(6, ".symtab", 2, 0, 0, symtab_offset, 0, link=7, info=1, align=4, entsize=16)
    sh(7, ".strtab", 3, 0, 0, strtab_offset, len(strtab), align=1)
    sh(8, ".shstrtab", 3, 0, 0, shstr_offset, len(shstr), align=1)

    struct.pack_into("<8I", data, program_offset,
                     subject.PT_IOPMOD, metadata_offset, 0, 0, len(module), 0, 4, 4)
    struct.pack_into("<8I", data, program_offset + 32,
                     subject.PT_LOAD, load_offset, load_vaddr, 0, len(load),
                     load_memory_size, 7, 16)
    struct.pack_into("<HHIIIIIHHHHHH", data, 16,
                     elf_type, 8, 1, 0, program_offset, section_offset, 0,
                     52, 32, program_count, 40, 9, 8)
    return bytes(data)


def rel_info(kind: int, symbol: int = 0) -> int:
    return (symbol << 8) | kind


def with_relocation(*, text_relocations=None, bss_relocations=None, **kwargs) -> bytes:
    def encode(rows):
        encoded = []
        for row in rows or ():
            off, kind, *tail = row
            encoded.append((off, rel_info(kind, tail[0] if tail else 0)))
        return tuple(encoded)
    if text_relocations is not None:
        text_relocations = encode(text_relocations)
    if bss_relocations is not None:
        bss_relocations = encode(bss_relocations)
    return build_irx(text_relocations=text_relocations, bss_relocations=bss_relocations, **kwargs)


class IopRelocationModelTests(unittest.TestCase):
    def test_copy_zero_relocate_and_translate_metadata(self):
        result = subject.load_iop_irx(build_irx(), load_base=0x1000)
        image = result["image"]
        self.assertEqual(len(image), 32)
        self.assertEqual(struct.unpack_from("<I", image, 0)[0], 0x1100)  # R_MIPS_32
        self.assertEqual(struct.unpack_from("<I", image, 4)[0], 0x08000440)  # R_MIPS_26
        self.assertEqual(struct.unpack_from("<I", image, 8)[0], 0x3C081235)  # HI16 carry
        self.assertEqual(struct.unpack_from("<I", image, 12)[0], 0x24848800)  # LO16
        self.assertEqual(struct.unpack_from("<I", image, 16)[0], 0x1000)  # relocated BSS
        self.assertEqual(image[20:32], bytes(12))
        self.assertEqual(result["entry_address"], 0x1004)
        self.assertEqual(result["module_id_address"], 0x1008)
        self.assertEqual(result["gp_address"], 0x1018)
        self.assertEqual(result["relocation_counts"], {"2": 2, "4": 1, "5": 1, "6": 1})

    def test_negative_lo16_is_sign_extended_for_hi16(self):
        payload = build_irx(words=(0, 0, 0x3C081234, 0x24848000),
                            text_relocations=((8, 5), (12, 6)), bss_relocations=())
        image = subject.load_iop_irx(payload, load_base=0x1000)["image"]
        self.assertEqual(struct.unpack_from("<I", image, 8)[0], 0x3C081234)
        self.assertEqual(struct.unpack_from("<I", image, 12)[0], 0x24849000)

    def test_32_bit_addend_wraps_as_iop_word_arithmetic(self):
        payload = build_irx(words=(0xFFFFF000, 0, 0, 0),
                            text_relocations=((0, 2),), bss_relocations=())
        image = subject.load_iop_irx(payload, load_base=0x1000)["image"]
        self.assertEqual(struct.unpack_from("<I", image, 0)[0], 0)

    def test_iopmod_gp_field_has_explicit_name_and_legacy_alias(self):
        parsed = ps2_irx.parse_irx(build_irx())
        self.assertEqual(parsed["module"]["gp_offset"], 24)
        self.assertEqual(parsed["module"]["unknown"], parsed["module"]["gp_offset"])
        outside_image = subject.load_iop_irx(build_irx(module_gp=40), load_base=0x1000)
        # loadcore adds the image base to GP metadata without requiring GP to
        # point inside the PT_LOAD extent (LGDEV has this same shape).
        self.assertEqual(outside_image["gp_address"], 0x1028)

    def test_module_id_sentinel_and_last_valid_ram_placement(self):
        payload = build_irx(module_id=0xFFFFFFFF)
        result = subject.load_iop_irx(payload, load_base=subject.IOP_RAM_BYTES - 32)
        self.assertIsNone(result["module_id_address"])
        self.assertEqual(result["entry_address"], subject.IOP_RAM_BYTES - 28)
        with self.assertRaises(Invalid):
            subject.load_iop_irx(payload, load_base=subject.IOP_RAM_BYTES - 28)

    def test_invalid_profile_and_synthetic_memory_extents_fail_closed(self):
        cases = (
            (build_irx(elf_type=2), 0x1000),
            (build_irx(program_count=1), 0x1000),
            (build_irx(load_vaddr=4), 0x1000),
            (build_irx(load_memory_size=0x200000), 0x1000),
            (build_irx(), 0x200000),
            (build_irx(module_data=4, module_bss=12), 0x1000),  # file_size != text + data
            (build_irx(load_memory_size=30), 0x1000),
        )
        for payload, base in cases:
            with self.subTest(base=base), self.assertRaises(Invalid):
                subject.load_iop_irx(payload, load_base=base)

    def test_allocated_text_must_map_to_its_pt_load_file_offset(self):
        payload = bytearray(build_irx())
        elf = ps2_irx.parse_elf(bytes(payload))["elf"]
        text_index = next(i for i, section in enumerate(elf["sections"])
                          if section.get("name") == ".text")
        text_header = elf["section_offset"] + text_index * 40
        text_section = elf["sections"][text_index]
        # Keep the section bounded and parseable, but contradict the zero-VMA
        # PT_LOAD file mapping by shifting .text's file offset only.
        struct.pack_into("<I", payload, text_header + 16, text_section["offset"] + 4)
        with self.assertRaisesRegex(Invalid, "PT_LOAD file offset|zero-based PT_LOAD"):
            subject.load_iop_irx(bytes(payload), load_base=0x1000)

    def test_allocated_progbits_must_be_file_backed_and_map_to_load(self):
        valid = build_irx()
        elf = ps2_irx.parse_elf(valid)["elf"]
        bss_index = next(i for i, section in enumerate(elf["sections"])
                         if section.get("name") == ".bss")
        section_header = elf["section_offset"] + bss_index * 40
        load_offset = elf["programs"][1]["offset"]

        # Reclassify the synthetic NOBITS section as allocated PROGBITS with
        # a span beyond filesz while remaining inside PT_LOAD memsz.
        beyond_file = bytearray(valid)
        struct.pack_into("<I", beyond_file, section_header + 4, subject.SHT_PROGBITS)
        with self.assertRaisesRegex(Invalid, "exceeds PT_LOAD file bytes"):
            subject.load_iop_irx(bytes(beyond_file), load_base=0x1000)

        # A second mutation stays within filesz but points at the wrong bytes.
        wrong_mapping = bytearray(valid)
        struct.pack_into("<I", wrong_mapping, section_header + 4, subject.SHT_PROGBITS)
        struct.pack_into("<I", wrong_mapping, section_header + 12, 8)  # section address
        struct.pack_into("<I", wrong_mapping, section_header + 16, load_offset + 12)
        struct.pack_into("<I", wrong_mapping, section_header + 20, 4)  # section size
        with self.assertRaisesRegex(Invalid, "does not map to its PT_LOAD file offset"):
            subject.load_iop_irx(bytes(wrong_mapping), load_base=0x1000)

    def test_pt_load_file_size_must_match_iopmod_text_and_data_sizes(self):
        # Keep text + data + BSS equal to PT_LOAD memory, while making the
        # file-backed text + data total inconsistent with PT_LOAD filesz.
        payload = build_irx(module_data=4, module_bss=12)
        with self.assertRaisesRegex(Invalid, "text/data sizes do not sum"):
            subject.load_iop_irx(payload, load_base=0x1000)

    def test_unsupported_type_nonzero_symbol_and_bad_sites_are_rejected(self):
        cases = (
            with_relocation(text_relocations=((0, 1),), bss_relocations=()),
            with_relocation(text_relocations=((0, 2, 1),), bss_relocations=()),
            with_relocation(text_relocations=((2, 2),), bss_relocations=()),
            with_relocation(text_relocations=((32, 2),), bss_relocations=()),
        )
        for payload in cases:
            with self.subTest(payload_hash=hashlib.sha256(payload).hexdigest()), self.assertRaises(Invalid):
                subject.load_iop_irx(payload, load_base=0x1000)

    def test_hi16_requires_an_adjacent_lo16_and_lo16_requires_hi16(self):
        cases = (
            with_relocation(text_relocations=((8, 5),), bss_relocations=()),
            with_relocation(text_relocations=((8, 6),), bss_relocations=()),
            with_relocation(text_relocations=((8, 5), (0, 2), (12, 6)), bss_relocations=()),
        )
        for payload in cases:
            with self.assertRaises(Invalid):
                subject.load_iop_irx(payload, load_base=0x1000)

    def test_relocation_section_metadata_and_duplicate_sites_are_checked(self):
        valid = build_irx()
        base = ps2_irx.parse_elf(valid)["elf"]
        rel_index = next(i for i, row in enumerate(base["sections"]) if row["type"] == 9 and row["size"])
        mutations = []
        bad_entsize = bytearray(valid)
        struct.pack_into("<I", bad_entsize, base["section_offset"] + rel_index * 40 + 36, 4)
        mutations.append(bytes(bad_entsize))
        bad_link = bytearray(valid)
        struct.pack_into("<I", bad_link, base["section_offset"] + rel_index * 40 + 24, 7)
        mutations.append(bytes(bad_link))
        bad_target = bytearray(valid)
        struct.pack_into("<I", bad_target, base["section_offset"] + rel_index * 40 + 28, 99)
        mutations.append(bytes(bad_target))
        bad_alloc = bytearray(valid)
        text_index = next(i for i, row in enumerate(base["sections"]) if row.get("name") == ".text")
        struct.pack_into("<I", bad_alloc, base["section_offset"] + text_index * 40 + 8, 0)
        mutations.append(bytes(bad_alloc))
        mutations.append(with_relocation(text_relocations=((0, 2), (0, 4)), bss_relocations=()))
        for payload in mutations:
            with self.subTest(payload_hash=hashlib.sha256(payload).hexdigest()), self.assertRaises(Invalid):
                subject.load_iop_irx(payload, load_base=0x1000)


if __name__ == "__main__":
    unittest.main()
