"""Synthetic controls for the serialized object-row float verifier."""
import struct
import unittest

import ps2_sections
import verify_object_floats
from evidence_common import Invalid
from test_ps2_sections import fixture, record


def one_row_model() -> bytes:
    """Build a complete parser fixture with one serialized 32-byte row."""
    serialized_record = bytearray(record())
    struct.pack_into("<I", serialized_record, 36, 1)  # signed-halfword row count
    serialized_record[40:40] = bytes(32)
    return fixture(bytes(serialized_record), {3: 1})


class ObjectFloats(unittest.TestCase):
    def test_parser_derived_row_checks_exactly_four_mapped_binary32_fields(self):
        data = bytearray(one_row_model())
        row_offset = ps2_sections.parse(bytes(data))["later"]["records"][0]["expanded_24"]["offset"]
        expected_bits = (0x80000000, 0x00000001, 0x3F800000, 0xBF800000)
        for relative, bits in zip((4, 8, 12, 16), expected_bits):
            struct.pack_into("<I", data, row_offset + relative, bits)

        result = verify_object_floats.check_model(bytes(data))
        self.assertTrue(result["exact_eof"])
        self.assertEqual((result["rows"], result["fields_checked"], result["finite"], result["nonfinite"]),
                         (1, 4, 4, 0))
        self.assertEqual([field["source_offset"] for field in result["fields"]], [4, 8, 12, 16])
        # A NaN-shaped word in an adjacent, unmapped row slot is outside this claim.
        struct.pack_into("<I", data, row_offset + 20, 0x7FC00000)
        self.assertEqual(verify_object_floats.check_model(bytes(data))["nonfinite"], 0)

    def test_nan_and_both_infinities_are_detected_at_each_mapped_field(self):
        offsets = (4, 8, 12, 16)
        bad_values = ((0x7FC00001, "nan"), (0x7F800000, "positive_infinity"),
                      (0xFF800000, "negative_infinity"))
        for relative in offsets:
            for bits, category in bad_values:
                with self.subTest(relative=relative, bits=hex(bits)):
                    data = bytearray(one_row_model())
                    row_offset = ps2_sections.parse(bytes(data))["later"]["records"][0]["expanded_24"]["offset"]
                    struct.pack_into("<I", data, row_offset + relative, bits)
                    result = verify_object_floats.check_model(bytes(data))
                    self.assertEqual(result["nonfinite"], 1)
                    self.assertEqual(result["failures"], [
                        f"1 non-finite mapped float fields in serialized row span at {row_offset:#x}"
                    ])
                    self.assertEqual(sum(f[category] for f in result["fields"]), 1)

    def test_malformed_or_out_of_bounds_row_spans_are_rejected(self):
        data = one_row_model()
        parsed = ps2_sections.parse(data)
        span = parsed["later"]["records"][0]["expanded_24"]
        bad_spans = (
            {**span, "offset": len(data) - 4, "end": len(data) + 28},
            {**span, "count": 2},
            {**span, "stride": 36},
            {**span, "end": span["end"] - 1},
        )
        for bad in bad_spans:
            with self.subTest(span=bad), self.assertRaises(Invalid):
                verify_object_floats.inspect_span(data, bad)

    def test_real_corpus_result_is_archive_bound_and_reports_every_model(self):
        from pathlib import Path

        game = Path(__file__).resolve().parent.parent / "games/ford-racing-2"
        if not (game / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus absent; parser-derived corpus verifier is not run")
        result = verify_object_floats.check_corpus(game)
        self.assertEqual((result["models_expected"], result["models_checked"], result["models_exact_eof"]),
                         (56, 56, 56))
        self.assertFalse(result["unsupported"])
        self.assertFalse(result["failures"])
        self.assertGreater(result["rows"], 0)
        self.assertEqual(result["fields_checked"], result["rows"] * 4)
        self.assertEqual(result["finite"], result["fields_checked"])
        self.assertEqual(result["nonfinite"], 0)
        self.assertTrue(all(model["exact_eof"] for model in result["file_results"]))


if __name__ == "__main__":
    unittest.main()
