import struct
import unittest

from evidence_common import Invalid
from iop_symbols import frame_agreement, link_procedures, read_symbols, stub_names


def elf_with_symbols(symbols):
    """Minimal ELF32LE: null, .symtab, .strtab, .shstrtab. symbols: (name, value, size, type, bind)."""
    strtab = b"\0"
    entries = struct.pack("<IIIBBH", 0, 0, 0, 0, 0, 0)
    for name, value, size, kind, bind in symbols:
        entries += struct.pack("<IIIBBH", len(strtab), value, size, (bind << 4) | kind, 0, 1)
        strtab += name.encode() + b"\0"
    shstr = b"\0.symtab\0.strtab\0.shstrtab\0"
    header = bytearray(52)
    header[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    body = bytes(header)
    sym_off = len(body)
    body += entries
    str_off = len(body)
    body += strtab
    shstr_off = len(body)
    body += shstr
    sh_off = (len(body) + 3) & ~3
    body += bytes(sh_off - len(body))
    sections = [struct.pack("<10I", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                struct.pack("<10I", 1, 2, 0, 0, sym_off, len(entries), 2, 0, 4, 16),
                struct.pack("<10I", 9, 3, 0, 0, str_off, len(strtab), 0, 0, 1, 0),
                struct.pack("<10I", 17, 3, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0)]
    body += b"".join(sections)
    out = bytearray(body)
    struct.pack_into("<HHIIIIIHHHHHH", out, 16, 0xFF80, 8, 1, 0, 0, sh_off, 0, 52, 0, 0, 40, 4, 3)
    return bytes(out)


class ReadSymbolsTest(unittest.TestCase):
    def test_names_values_sizes_types_and_binds(self):
        data = elf_with_symbols([("main", 0x100, 0x40, 2, 1), ("table", 0x200, 8, 1, 1)])
        symbols = read_symbols(data)
        self.assertEqual(symbols[0], {"name": "main", "value": 0x100, "size": 0x40, "type": 2, "bind": 1})
        self.assertEqual(symbols[1]["name"], "table")

    def test_the_null_symbol_is_skipped(self):
        self.assertEqual(len(read_symbols(elf_with_symbols([("a", 1, 1, 2, 1)]))), 1)


PROCS = [{"name": "a", "address": 0x10, "file": "x.c", "size": 8},
         {"name": "b", "address": 0x30, "file": "x.c", "size": 4},
         {"name": "s", "address": 0x0, "file": "y.s", "size": 12}]
SYMS = [{"name": "a", "value": 0x250, "size": 8, "type": 2, "bind": 1},
        {"name": "b", "value": 0x270, "size": 4, "type": 2, "bind": 1},
        {"name": "s", "value": 0x100, "size": 12, "type": 2, "bind": 1}]


class LinkTest(unittest.TestCase):
    def test_each_file_has_one_constant_offset(self):
        result = link_procedures(PROCS, SYMS)
        self.assertEqual(result["file_offsets"], {"x.c": 0x240, "y.s": 0x100})
        self.assertEqual({p["name"]: p["linked_address"] for p in result["procedures"]}, {"a": 0x250, "b": 0x270, "s": 0x100})
        self.assertEqual(result["size_disagreements"], [])

    def test_a_non_constant_offset_in_one_file_is_rejected(self):
        syms = [dict(s) for s in SYMS]
        syms[1]["value"] = 0x290
        with self.assertRaises(Invalid):
            link_procedures(PROCS, syms)

    def test_a_procedure_without_a_function_symbol_is_rejected(self):
        with self.assertRaises(Invalid):
            link_procedures(PROCS, SYMS[:2])

    def test_size_disagreements_are_listed_not_raised(self):
        syms = [dict(s) for s in SYMS]
        syms[0]["size"] = 12
        self.assertEqual(link_procedures(PROCS, syms)["size_disagreements"], ["a"])


class StubTest(unittest.TestCase):
    def test_a_symbol_at_the_stub_address_names_the_stub(self):
        symbols = [{"name": "sceSdInit", "value": 0x8000, "size": 8, "type": 1, "bind": 1},
                   {"name": "other", "value": 0x9000, "size": 0, "type": 1, "bind": 1}]
        self.assertEqual(stub_names([0x8000, 0x8008], symbols), {0x8000: "sceSdInit"})

    def test_section_and_file_symbols_do_not_name_stubs(self):
        symbols = [{"name": ".text", "value": 0x8000, "size": 0, "type": 3, "bind": 0},
                   {"name": "f.c", "value": 0x8000, "size": 0, "type": 4, "bind": 0}]
        self.assertEqual(stub_names([0x8000], symbols), {})


def words(*values):
    return b"".join(struct.pack("<I", v) for v in values)


ADDIU_SP_M32 = 0x27BDFFE0   # addiu sp,sp,-32
NOP = 0


class FrameTest(unittest.TestCase):
    def test_frame_bytes_match_the_prologue_stack_adjustment(self):
        text = words(ADDIU_SP_M32, NOP, NOP, NOP, NOP, NOP)
        result = frame_agreement([{"name": "f", "linked_address": 0, "frame_bytes": 32}], text)
        self.assertEqual((result["agree"], result["disagree"], result["no_adjustment"]), (1, 0, 0))

    def test_a_different_frame_is_listed(self):
        text = words(ADDIU_SP_M32, NOP, NOP, NOP, NOP, NOP)
        result = frame_agreement([{"name": "f", "linked_address": 0, "frame_bytes": 16}], text)
        self.assertEqual(result["disagree"], 1)
        self.assertEqual(result["disagreements"], [{"name": "f", "prologue": 32, "debug": 16}])

    def test_a_procedure_without_a_stack_adjustment_is_counted_apart(self):
        text = words(NOP, NOP, NOP, NOP, NOP, NOP)
        result = frame_agreement([{"name": "f", "linked_address": 0, "frame_bytes": 0}], text)
        self.assertEqual(result["no_adjustment"], 1)

    def test_a_procedure_outside_the_text_is_counted_apart(self):
        result = frame_agreement([{"name": "f", "linked_address": 0x1000, "frame_bytes": 8}], words(NOP))
        self.assertEqual(result["outside_text"], 1)


if __name__ == "__main__":
    unittest.main()
