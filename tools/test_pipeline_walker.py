import sys
import hashlib
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "ghidra/experimental/pipeline"))
import seedlib
from test_jump_table import BASE, V0, V1, AT, sltiu, beq, sll, lui, addu, lw, jr, NOP

PC = 0x1000


class WalkerDecodeTest(unittest.TestCase):
    def test_syscall_continues_to_the_next_word(self):
        self.assertEqual(seedlib.dec(PC, 0x0000000C), ("linear", None, PC + 4))

    def test_break_and_conditional_traps_still_stop_the_walk(self):
        for word in (0x0000000D, 0x00000034, 0x04080000):  # break, teq, tgei
            self.assertEqual(seedlib.dec(PC, word)[0], "trap", hex(word))

    def test_return_computed_jump_and_call_keep_their_kinds(self):
        self.assertEqual(seedlib.dec(PC, 0x03E00008)[0], "return")
        self.assertEqual(seedlib.dec(PC, 0x00600008)[0], "computed_jump")  # jr v1
        self.assertEqual(seedlib.dec(PC, 0x0C000400), ("call", 0x1000, PC + 8))  # jal 0x1000


class SwitchWalkerTest(unittest.TestCase):
    def words(self):
        return [sltiu(V1, V0, 2), beq(V1, 0, 9), sll(V1, V0, 2), lui(AT, 0x25),
                addu(AT, AT, V1), lw(V0, 0, AT), NOP, jr(V0), NOP, jr(31), NOP, jr(31), NOP]

    def fixture(self, targets=None, words=None, owned=None):
        words = words or self.words()
        targets = targets or [BASE + 36, BASE + 44]
        data = bytearray(0x1400)
        data[:16] = b'\x7fELF\x01\x01\x01' + bytes(9)
        struct.pack_into('<HHIIIIIHHHHHH', data, 16, 2, 8, 1, BASE, 52, 116, 0, 52, 32, 2, 40, 3, 0)
        struct.pack_into('<8I', data, 52, 1, 0x1000, BASE, BASE, 0x400, 0x400, 5, 4)
        struct.pack_into('<8I', data, 84, 1, 0x1200, 0x250000, 0x250000, 8, 8, 4, 4)
        struct.pack_into('<10I', data, 156, 0, 1, 6, BASE, 0x1000, 0x100, 0, 0, 4, 0)
        struct.pack_into('<10I', data, 196, 0, 1, 2, 0x250000, 0x1200, 8, 0, 0, 4, 0)
        struct.pack_into(f'<{len(words)}I', data, 0x1000, *words)
        struct.pack_into('<2I', data, 0x1200, *targets)
        state = {'elf':bytes(data), 'owned':owned or {}, 'entries':set(), 'undef':set(range(BASE, BASE+0x100)),
                 'unowned':set(), 'get':lambda pc:struct.unpack_from('<I', data, 0x1000+pc-BASE)[0]}
        return patch.multiple(seedlib, create=True, **state)

    def test_switch_walk_reaches_every_case_and_pins_table_words(self):
        with self.fixture():
            result = seedlib.walk(f'{BASE:08x}')
        self.assertEqual(result['rejects'], [])
        self.assertEqual(result['span']['end_exclusive'], '00100034')
        self.assertEqual(result['reachable_count'], 13)
        self.assertEqual(result['jump_tables'], [{'site':'0010001c', 'table':'00250000', 'count':2,
                                               'targets':['00100024','0010002c'], 'guard_site':'00100000',
                                               'table_sha256':hashlib.sha256(bytes.fromhex('240010002c001000')).hexdigest()}])
        self.assertEqual(result['edge_counts']['switch'], 1)

    def test_duplicate_table_targets_remain_pinned_in_order(self):
        with self.fixture(targets=[BASE+36, BASE+36]):
            result = seedlib.walk(f'{BASE:08x}')
        self.assertFalse(result['rejects'])
        self.assertEqual(result['jump_tables'][0]['targets'], ['00100024','00100024'])

    def test_a_switch_target_outside_the_allowed_region_keeps_the_jump_rejected(self):
        for target, owned in ((BASE+0x3000,{}), (BASE+37,{}), (BASE+36,{BASE+36:'00100024'})):
            with self.subTest(target=target), self.fixture(targets=[target, BASE+44], owned=owned):
                result = seedlib.walk(f'{BASE:08x}')
            self.assertIn('computed_jump', [r['why'] for r in result['rejects']])
            self.assertEqual(result['jump_tables'], [])

    def test_a_table_target_cannot_bypass_the_dispatch_bound(self):
        with self.fixture(targets=[BASE+12, BASE+44]):
            result = seedlib.walk(f'{BASE:08x}')
        self.assertIn('flow bypasses switch bounds', [r['why'] for r in result['rejects']])

    def test_an_entry_jump_into_the_dispatch_cannot_use_unreachable_bounds(self):
        words = [2 << 26 | ((BASE+20) >> 2), NOP] + self.words()
        with self.fixture(words=words, targets=[BASE+44, BASE+52]):
            result = seedlib.walk(f'{BASE:08x}')
        self.assertIn('switch bounds region is not fully reached', [r['why'] for r in result['rejects']])
        self.assertIn('flow bypasses switch bounds', [r['why'] for r in result['rejects']])

    def test_a_path_cannot_skip_the_table_base_definition_before_the_bound(self):
        words=[beq(V0,V1,2),NOP,lui(AT,0x25),sltiu(V1,V0,2),beq(V1,0,6),sll(V1,V0,2),
               addu(AT,AT,V1),lw(V0,0,AT),NOP,jr(V0),NOP,jr(31),NOP]
        with self.fixture(words=words,targets=[BASE+44,BASE+44]):
            result=seedlib.walk(f'{BASE:08x}')
        self.assertTrue(result['rejects'])
