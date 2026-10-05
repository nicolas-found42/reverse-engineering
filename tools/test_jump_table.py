import struct
import unittest

from evidence_common import Invalid
from jump_table import read_table, recognize, table_targets

def r(op, rs, rt, imm):
    return op << 26 | rs << 21 | rt << 16 | (imm & 0xFFFF)


def lui(rt, imm):
    return r(0x0F, 0, rt, imm)


def addiu(rt, rs, imm):
    return r(0x09, rs, rt, imm)


def sltiu(rt, rs, imm):
    return r(0x0B, rs, rt, imm)


def lw(rt, off, base):
    return r(0x23, base, rt, off)


def addu(rd, rs, rt):
    return rs << 21 | rt << 16 | rd << 11 | 0x21


def sll(rd, rt, sa):
    return rt << 16 | rd << 11 | sa << 6


def beq(rs, rt, off):
    return r(0x04, rs, rt, off)


def jr(rs):
    return rs << 21 | 0x08


NOP = 0
V0, V1, AT = 2, 3, 1
BASE = 0x100000


def code(*words):
    memory = {BASE + 4 * i: w for i, w in enumerate(words)}
    return (lambda pc: memory.get(pc, 0)), BASE + 4 * (len(words) - 2)   # site is the jr (delay slot follows)


# Switch on v0 with 8 cases; table at 0x24f900 + 0x10.
CANONICAL = (sltiu(V1, V0, 8), beq(V1, 0, 20), sll(V1, V0, 2), lui(AT, 0x0025), addu(AT, AT, V1), lw(V0, -0x06F0, AT), NOP, jr(V0), NOP)


class RecognizeTest(unittest.TestCase):
    def test_a_write_to_register_zero_cannot_define_a_table_address(self):
        words = CANONICAL[:3] + (lui(0, 0x25), addu(AT, 0, V1)) + CANONICAL[5:]
        get, site = code(*words)
        self.assertIsNone(recognize(get, site, floor=BASE))

    def test_jumping_through_register_zero_is_not_a_table_dispatch(self):
        words = CANONICAL[:5] + (lw(0, -0x06F0, AT), NOP, jr(0), NOP)
        get, site = code(*words)
        self.assertIsNone(recognize(get, site, floor=BASE))

    def test_the_supported_profile_branches_before_scaling(self):
        words = (sltiu(V1, V0, 8), sll(4, V0, 2), beq(V1, 0, 20), NOP,
                 lui(AT, 0x25), addu(AT, AT, 4), lw(V0, -0x06F0, AT), NOP, jr(V0), NOP)
        get, site = code(*words)
        self.assertIsNone(recognize(get, site, floor=BASE))

    def test_reserved_fields_cannot_masquerade_as_the_dispatch_profile(self):
        for index, reserved in ((2, 1 << 21), (3, 1 << 21), (4, 1 << 6), (7, 1 << 16)):
            words = list(CANONICAL)
            words[index] |= reserved
            get, site = code(*words)
            with self.subTest(index=index):
                self.assertIsNone(recognize(get, site, floor=BASE))

    def test_a_branch_that_selects_the_table_for_out_of_range_values_is_refused(self):
        words = CANONICAL[:1] + (r(0x05, V1, 0, 20),) + CANONICAL[2:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 28, floor=BASE))

    def test_overwriting_the_bounded_index_before_scaling_is_refused(self):
        words = CANONICAL[:2] + (addiu(V0, V0, 1),) + CANONICAL[2:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 32, floor=BASE))

    def test_a_control_transfer_inside_the_pattern_is_refused(self):
        words = CANONICAL[:3] + (0x0000000C,) + CANONICAL[3:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 32, floor=BASE))

    def test_an_out_of_range_branch_back_into_the_dispatch_is_refused(self):
        words = CANONICAL[:1] + (beq(V1, 0, 3),) + CANONICAL[2:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 28, floor=BASE))

    def test_a_clobbered_bounds_flag_is_refused(self):
        words = CANONICAL[:1] + (addiu(V1, 0, 1),) + CANONICAL[1:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 32, floor=BASE))

    def test_an_unmodelled_gpr_write_is_refused(self):
        # LQ v0,0(sp) changes the bounded index, outside this profile.
        words = CANONICAL[:2] + (r(0x1E, 29, V0, 0),) + CANONICAL[2:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 32, floor=BASE))

    def test_the_bound_must_precede_an_in_place_scaling_shift(self):
        words = (sll(V0, V0, 2), sltiu(V1, V0, 8), beq(V1, 0, 20), lui(AT, 0x25),
                 addu(AT, AT, V0), lw(V0, -0x06F0, AT), NOP, jr(V0), NOP)
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 28, floor=BASE))

    def test_the_canonical_gcc_sequence_gives_table_and_count(self):
        get, _ = code(*CANONICAL)
        site = BASE + 4 * 7
        found = recognize(get, site, floor=BASE)
        self.assertEqual(found, {"site": site, "table": 0x250000 - 0x06F0, "count": 8, "index_register": V0, "guard_site": BASE})

    def test_the_addiu_variant_with_a_zero_load_offset(self):
        words = (sltiu(V1, V0, 4), beq(V1, 0, 9), sll(V1, V0, 2), lui(AT, 0x0025), addiu(AT, AT, 0x100), addu(AT, AT, V1),
                 lw(V0, 0, AT), NOP, jr(V0), NOP)
        get, _ = code(*words)
        found = recognize(get, BASE + 4 * 8, floor=BASE)
        self.assertEqual((found["table"], found["count"]), (0x250100, 4))

    def test_the_scaling_shift_may_sit_in_the_branch_delay_slot(self):
        # CANONICAL already has sll right after beq (its delay slot); the same sequence with a nop between must also work
        words = (sltiu(V1, V0, 8), beq(V1, 0, 20), NOP, sll(V1, V0, 2), lui(AT, 0x0025), addu(AT, AT, V1),
                 lw(V0, -0x06F0, AT), NOP, jr(V0), NOP)
        get, _ = code(*words)
        self.assertIsNotNone(recognize(get, BASE + 4 * 8, floor=BASE))

    def test_no_bounds_check_means_no_table(self):
        words = CANONICAL[1:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 4 * 6, floor=BASE))

    def test_a_load_into_another_register_is_not_a_switch(self):
        words = CANONICAL[:5] + (lw(V1, -0x06F0, AT), NOP, jr(V0), NOP)
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 4 * 7, floor=BASE))

    def test_a_return_is_not_a_switch(self):
        get, _ = code(jr(31), NOP)
        self.assertIsNone(recognize(get, BASE, floor=BASE))

    def test_an_implausibly_large_count_is_refused(self):
        words = (sltiu(V1, V0, 4000),) + CANONICAL[1:]
        get, _ = code(*words)
        self.assertIsNone(recognize(get, BASE + 4 * 7, floor=BASE))

    def test_the_window_stops_at_the_floor(self):
        get, _ = code(*CANONICAL)
        self.assertIsNone(recognize(get, BASE + 4 * 7, floor=BASE + 4))


class TableTargetsTest(unittest.TestCase):
    def elf_table(self):
        data = bytearray(256)
        data[:16] = b'\x7fELF\x01\x01\x01' + bytes(9)
        struct.pack_into('<HHIIIIIHHHHHH', data, 16, 2, 8, 1, BASE, 0, 52, 0, 52, 32, 0, 40, 2, 0)
        struct.pack_into('<10I', data, 92, 0, 1, 2, 0x250000, 200, 12, 0, 0, 4, 0)
        struct.pack_into('<3I', data, 200, 0x100010, 0x100020, 0x100010)
        return data

    def test_words_are_read_in_order(self):
        memory = {0x250000: 0x100010, 0x250004: 0x100020, 0x250008: 0x100010}
        self.assertEqual(table_targets(lambda a: memory[a], 0x250000, 3), [0x100010, 0x100020, 0x100010])

    def test_table_is_mapped_through_the_file_backed_elf_section(self):
        self.assertEqual(read_table(bytes(self.elf_table()), 0x250000, 3), [0x100010, 0x100020, 0x100010])

    def test_an_interior_table_address_maps_to_the_corresponding_file_words(self):
        self.assertEqual(read_table(bytes(self.elf_table()), 0x250004, 2), [0x100020, 0x100010])

    def test_invalid_alignment_count_and_extent_are_refused(self):
        for address, count in ((0x250001, 1), (0x250000, 0), (0x250000, 257), (0x250004, 3), (0x249FFC, 1)):
            with self.subTest(address=address, count=count), self.assertRaises(Invalid):
                read_table(bytes(self.elf_table()), address, count)

    def test_bss_executable_and_unallocated_sections_are_refused(self):
        for kind, flags in ((8, 2), (1, 6), (1, 0)):
            data = self.elf_table()
            struct.pack_into('<II', data, 96, kind, flags)
            with self.subTest(kind=kind, flags=flags), self.assertRaises(Invalid):
                read_table(bytes(data), 0x250000, 3)

    def test_ambiguous_section_mapping_is_refused(self):
        data = self.elf_table()
        struct.pack_into('<H', data, 48, 3)
        data[132:172] = data[92:132]
        with self.assertRaises(Invalid):
            read_table(bytes(data), 0x250000, 3)

    def test_truncated_file_backed_payload_is_refused(self):
        with self.assertRaises(Invalid):
            read_table(bytes(self.elf_table()[:211]), 0x250000, 3)


if __name__ == "__main__":
    unittest.main()
