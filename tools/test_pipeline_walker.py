import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ghidra/experimental/pipeline"))
import seedlib

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
