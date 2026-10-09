"""Controls for the recorded substitute-region map and substitute byte gate."""

import unittest

from matching_diff import Scope, compare_unit


STUB_SECTION = ".text"
STUB_ADDRESS = 0x001EADE0
STUB_OFFSET = 0x000EBDE0
STUB_BYTES = bytes.fromhex("640003240c0000000800e00300000000")
SEMA_SECTION = ".text"
SEMA_ADDRESS = 0x001EAB80
SEMA_OFFSET = 0x000EBB80
SEMA_BYTES = bytes.fromhex("420003240c0000000800e00300000000")


class SignalSemaScopeTest(unittest.TestCase):
    def test_recorded_signalsema_range_reports_substitute_never_matched_scope(self):
        verdict = compare_unit(
            SEMA_SECTION, SEMA_ADDRESS, SEMA_OFFSET, SEMA_BYTES, SEMA_BYTES
        )
        self.assertEqual(verdict.status, "pass")
        self.assertEqual(verdict.scope, Scope.SUBSTITUTE_REGION.value)

    def test_bytes_adjacent_to_the_signalsema_range_stay_mixed(self):
        adjacent = compare_unit(
            SEMA_SECTION,
            SEMA_ADDRESS + len(SEMA_BYTES),
            SEMA_OFFSET + len(SEMA_BYTES),
            b"s" * 16,
            b"s" * 16,
        )
        self.assertEqual(adjacent.scope, Scope.MIXED.value)


class SubstituteScopeTest(unittest.TestCase):
    def test_recorded_substitute_range_reports_substitute_never_matched_scope(self):
        verdict = compare_unit(
            STUB_SECTION, STUB_ADDRESS, STUB_OFFSET, STUB_BYTES, STUB_BYTES
        )
        self.assertEqual(verdict.status, "pass")
        self.assertEqual(verdict.scope, Scope.SUBSTITUTE_REGION.value)

    def test_bytes_adjacent_to_the_substitute_range_stay_mixed(self):
        adjacent = compare_unit(
            STUB_SECTION,
            STUB_ADDRESS + len(STUB_BYTES),
            STUB_OFFSET + len(STUB_BYTES),
            b"r" * 16,
            b"r" * 16,
        )
        self.assertEqual(adjacent.scope, Scope.MIXED.value)

    def test_a_span_covering_substitute_and_mixed_bytes_stays_mixed(self):
        spanning = compare_unit(
            STUB_SECTION,
            STUB_ADDRESS + len(STUB_BYTES) - 8,
            STUB_OFFSET + len(STUB_BYTES) - 8,
            b"r" * 16,
            b"r" * 16,
        )
        self.assertEqual(spanning.scope, Scope.MIXED.value)

    def test_game_owned_range_still_reports_game_owned(self):
        owned = compare_unit(".text", 0x1D1800, 0x0D2800, b"r" * 60, b"r" * 60)
        self.assertEqual(owned.scope, Scope.GAME_OWNED.value)


if __name__ == "__main__":
    unittest.main()
