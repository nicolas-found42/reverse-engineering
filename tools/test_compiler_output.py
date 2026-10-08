"""Compiler-versus-linker diagnostics at the probe's object evidence seam."""
import struct
import unittest

from elf_fixture import Spec, build_elf
from compiler_output import compare_object


def fixture(word=0x0C000000, reloc=4):
    data = build_elf([Spec('.text.probe', struct.pack('<II', word, 0x24020007), flags=6),
                      Spec('.rel.text.probe', struct.pack('<II', 0, reloc), kind=9, flags=0)])
    result = bytearray(data)
    table = struct.unpack_from('<I', data, 32)[0]
    struct.pack_into('<I', result, table + 2 * 40 + 28, 1)  # sh_info: target
    struct.pack_into('<I', result, table + 2 * 40 + 36, 8)
    struct.pack_into('<H', result, 16, 1)  # ET_REL
    return bytes(result)


class CompilerOutputTests(unittest.TestCase):
    def test_link_address_is_separate_from_compiler_instruction_bits(self):
        result = compare_object(fixture(), 'probe', struct.pack('<II', 0x0C041622, 0x24020007))
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['relocations'], [{'offset': 0, 'type': 4, 'symbol_index': 0,
                                                 'mask': '03ffffff'}])
        self.assertEqual(result['matched_bytes'], 0)

    def test_changed_opcode_or_nonrelocated_word_is_located(self):
        for expected, offset in [((0x08041622, 0x24020007), 0), ((0x0C041622, 0x24020008), 4)]:
            with self.subTest(expected=expected):
                result = compare_object(fixture(), 'probe', struct.pack('<II', *expected))
                self.assertEqual(result['status'], 'fail')
                self.assertEqual(result['first_difference']['offset'], offset)

    def test_unknown_relocation_is_incomplete(self):
        from evidence_common import Incomplete
        with self.assertRaisesRegex(Incomplete, 'unsupported compiler relocation'):
            compare_object(fixture(reloc=99), 'probe', struct.pack('<II', 0x0C041622, 0x24020007))

    def test_length_mismatch_is_not_hidden_by_relocations(self):
        result = compare_object(fixture(), 'probe', struct.pack('<I', 0x0C041622))
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['first_difference']['expected_bytes'], 4)

    def test_missing_function_is_incomplete(self):
        from evidence_common import Incomplete
        with self.assertRaisesRegex(Incomplete, 'exactly one function section'):
            compare_object(fixture(), 'absent', bytes(8))

    def test_explicit_addends_are_retained_separately_from_instruction_bits(self):
        data = bytearray(build_elf([
            Spec('.text.probe', struct.pack('<II', 0x0C000000, 0x24020007), flags=6),
            Spec('.rela.text.probe', struct.pack('<IIi', 0, 4, 16), kind=4, flags=0)]))
        table = struct.unpack_from('<I', data, 32)[0]
        struct.pack_into('<I', data, table + 2 * 40 + 28, 1)
        struct.pack_into('<I', data, table + 2 * 40 + 36, 12)
        struct.pack_into('<H', data, 16, 1)
        result = compare_object(bytes(data), 'probe', struct.pack('<II', 0x0C041626, 0x24020007))
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['relocations'][0]['addend'], 16)
