"""Falsifiers for the six endpoint words consumed from 0x34-byte records."""
import math
import struct
import unittest

import verify_geometry_bounds as bounds
from evidence_common import Invalid
from test_ps2_sections import fixture


def geometry_model(values=(-1.0, 1.0, -2.0, 2.0, -3.0, 3.0)):
    from ps2_sections import parse

    original = fixture()
    geo = parse(original)["geometry"]
    data = bytearray(original[:geo["section_start"]])
    data += struct.pack("<I", 1) + bytes(52)
    data += bytes(-len(data) % 16)
    data += original[geo["section_end"]:]
    table = parse(bytes(data))["geometry"]["table"]
    struct.pack_into("<6f", data, table["offset"] + 4, *values)
    return bytes(data)


class GeometryBounds(unittest.TestCase):
    def test_three_adjacent_pairs_are_ordered_and_finite(self):
        result = bounds.check_model(geometry_model())
        self.assertEqual(result["records_checked"], 1)
        self.assertEqual(result["words_checked"], 6)
        self.assertEqual(result["source_pairs"], [[4, 8], [12, 16], [20, 24]])
        self.assertEqual(result["nonfinite_words"], 0)
        self.assertEqual(result["inverted_pairs"], 0)
        self.assertFalse(result["failures"])

    def test_each_endpoint_rejects_nan_and_both_infinities(self):
        for index in range(6):
            for bad in (math.nan, math.inf, -math.inf):
                with self.subTest(index=index, bad=bad):
                    values = [-1., 1., -2., 2., -3., 3.]
                    values[index] = bad
                    result = bounds.check_model(geometry_model(values))
                    self.assertEqual(result["nonfinite_words"], 1)
                    self.assertTrue(result["failures"])

    def test_each_pair_rejects_reversed_endpoints(self):
        for index in range(3):
            values = [-1., 1., -2., 2., -3., 3.]
            values[index * 2:index * 2 + 2] = [2., -2.]
            result = bounds.check_model(geometry_model(values))
            self.assertEqual(result["inverted_pairs"], 1)
            self.assertTrue(result["failures"])

    def test_zero_and_degenerate_pairs_are_valid(self):
        for values in ((0.,) * 6, (-0., 0., 2., 2., -3., -3.)):
            self.assertFalse(bounds.check_model(geometry_model(values))["failures"])

    def test_table_shape_and_input_bounds_are_guarded(self):
        for table in (
            {"offset": 0, "count": 1, "stride": 36, "size": 36, "end": 36},
            {"offset": 0, "count": 2, "stride": 52, "size": 52, "end": 52},
            {"offset": 4, "count": 1, "stride": 52, "size": 52, "end": 56},
        ):
            with self.subTest(table=table), self.assertRaises(Invalid):
                bounds.inspect_table(bytes(52), table)


if __name__ == "__main__":
    unittest.main()
