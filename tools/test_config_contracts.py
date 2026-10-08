"""Falsifiable tests for the supported track-configuration profile."""

import struct
import unittest

from config_contracts import InvalidConfig, parse_track_config


class TrackConfigContracts(unittest.TestCase):
    def test_known_contract_decodes_numeric_fields_without_assigning_rendering_meaning(self):
        raw = (
            b"// retained comment\r\n"
            b"FOG: 0.5 11 22 33\r\n"
            b"CAR_HEADLIGHT_STRENGTH: 1.25\r\n"
            b"TRACK_WETNESS: 0.75\r\n"
            b"SUN_FLARE_SIZE: 2.0\r\n"
            b"HEAT_HAZE_STRENGTH: 0.125\r\n"
        )
        parsed = parse_track_config(raw)
        self.assertEqual(parsed["FOG"][1:], (11, 22, 33))
        self.assertEqual(parsed["CAR_HEADLIGHT_STRENGTH"], 1.25)
        self.assertEqual(struct.pack("<f", parsed["FOG"][0]), struct.pack("<f", 0.5))

    def test_unknown_active_key_is_rejected_as_outside_the_supported_profile(self):
        raw = b"FOG: 0.5 1 2 3\nUNKNOWN: 4\n"
        with self.assertRaisesRegex(InvalidConfig, "unsupported key"):
            parse_track_config(raw)

    def test_missing_required_key_is_incomplete(self):
        raw = (b"FOG: 0.5 1 2 3\nCAR_HEADLIGHT_STRENGTH: 1\n"
               b"TRACK_WETNESS: 1\nSUN_FLARE_SIZE: 1\n")
        with self.assertRaisesRegex(InvalidConfig, "missing required key"):
            parse_track_config(raw)

    def test_duplicate_key_and_wrong_arity_fail(self):
        with self.assertRaisesRegex(InvalidConfig, "duplicate key"):
            parse_track_config(b"FOG: 1 1 2 3\nFOG: 2 1 2 3\n")
        with self.assertRaisesRegex(InvalidConfig, "four numeric fields"):
            parse_track_config(b"FOG: 1 2 3\n")


if __name__ == "__main__":
    unittest.main()
