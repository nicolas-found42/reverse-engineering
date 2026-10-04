import unittest

from r5900_shape import is_plausible


class R5900ShapeTest(unittest.TestCase):
    def test_known_instructions_are_plausible(self):
        for word in (0x00000000, 0x03E00008, 0x27BDFFE0, 0x8FBF0010, 0xAFBF0010,
                     0x7BBF0000,  # lq
                     0x70000000 | (0x28 << 0),  # MMI class
                     0x0C000400, 0x10400003, 0x3C081234, 0x46000006):
            self.assertTrue(is_plausible(word), hex(word))

    def test_encodings_absent_from_the_r5900_are_implausible(self):
        for word in (0x4C000000,    # COP3
                     0x74000000,    # opcode 0x1d
                     0xC0000000,    # LL
                     0xE0000000,    # SC
                     0x00000005,    # SPECIAL funct 0x05
                     0x0000003D,    # SPECIAL funct 0x3d
                     0x04040000):   # REGIMM rt 4
            self.assertFalse(is_plausible(word), hex(word))
