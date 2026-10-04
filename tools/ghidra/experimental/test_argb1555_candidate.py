"""Synthetic arithmetic checks for the provisional 0x0022a180 model."""

import unittest

try:
    from .argb1555_candidate import uint32_to_argb1555_candidate
except ImportError:
    from argb1555_candidate import uint32_to_argb1555_candidate


class CandidatePackingTests(unittest.TestCase):
    def test_zero_and_all_max_channels(self):
        self.assertEqual(uint32_to_argb1555_candidate(0x00000000), 0x0000)
        self.assertEqual(uint32_to_argb1555_candidate(0xFFFFFFFF), 0xFFFF)

    def test_each_color_byte_occupies_its_own_five_bit_field(self):
        cases = (
            (0x000000FF, 0x7C00),  # byte 0 -> red bits 10..14
            (0x0000FF00, 0x03E0),  # byte 1 -> green bits 5..9
            (0x00FF0000, 0x001F),  # byte 2 -> blue bits 0..4
        )
        for source, expected in cases:
            with self.subTest(source=f"{source:#010x}"):
                self.assertEqual(uint32_to_argb1555_candidate(source), expected)

    def test_color_truncation_boundaries(self):
        # Values 0..7 shift to zero; 8 starts the least-significant 5-bit step.
        for channel_shift in (0, 8, 16):
            with self.subTest(channel_shift=channel_shift):
                self.assertEqual(uint32_to_argb1555_candidate(7 << channel_shift), 0)
                self.assertEqual(
                    uint32_to_argb1555_candidate(8 << channel_shift),
                    1 << (10 if channel_shift == 0 else 5 if channel_shift == 8 else 0),
                )
                self.assertEqual(
                    uint32_to_argb1555_candidate(248 << channel_shift),
                    31 << (10 if channel_shift == 0 else 5 if channel_shift == 8 else 0),
                )

    def test_alpha_is_a_nonzero_test_not_a_fifth_bit_truncation(self):
        self.assertEqual(uint32_to_argb1555_candidate(0x00000000), 0x0000)
        self.assertEqual(uint32_to_argb1555_candidate(0x01000000), 0x8000)
        self.assertEqual(uint32_to_argb1555_candidate(0xFF000000), 0x8000)

    def test_all_256_values_for_each_channel(self):
        color_layouts = ((0, 10), (8, 5), (16, 0))
        for input_shift, output_shift in color_layouts:
            for channel in range(256):
                source = channel << input_shift
                expected = (channel >> 3) << output_shift
                with self.subTest(input_shift=input_shift, channel=channel):
                    self.assertEqual(uint32_to_argb1555_candidate(source), expected)
        for alpha in range(256):
            with self.subTest(alpha=alpha):
                self.assertEqual(
                    uint32_to_argb1555_candidate(alpha << 24),
                    0x8000 if alpha else 0,
                )

    def test_combined_channels_do_not_carry_between_fields(self):
        self.assertEqual(uint32_to_argb1555_candidate(0xFFFFFFFF), 0xFFFF)
        self.assertEqual(uint32_to_argb1555_candidate(0xF8F8F8F8), 0xFFFF)
        self.assertEqual(uint32_to_argb1555_candidate(0x08080808), 0x8421)

    def test_input_domain_is_explicit(self):
        for invalid in (-1, 0x1_0000_0000):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                uint32_to_argb1555_candidate(invalid)
        for invalid in (True, 1.0, "1"):
            with self.subTest(value=invalid), self.assertRaises(TypeError):
                uint32_to_argb1555_candidate(invalid)


if __name__ == "__main__":
    unittest.main()
