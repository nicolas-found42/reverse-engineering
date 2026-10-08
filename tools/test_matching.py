import hashlib
import unittest

from elf_fixture import Spec, build_elf
from matching_diff import Scope, compare, ledger, scope_of
from matching_sections import Section, pinned_executable, sections

BASE = 0x100000
TEXT = bytes.fromhex("27bdffe8afbe0004") + bytes(8)
RODATA = b"abcd" * 4


def retail() -> bytes:
    """An EE ELF carrying .text, .rodata and a NOBITS .sbss, like the pinned corpus."""
    return build_elf([Spec(".text", TEXT, flags=6, address=BASE + 0x100),
                      Spec(".rodata", RODATA, address=BASE + 0x200),
                      Spec(".sbss", b"", kind=8, flags=3, address=BASE + 0x300)])


class SectionExtractionTest(unittest.TestCase):
    def test_a_named_section_yields_exact_bytes_address_size_and_hash(self):
        found = sections(retail())
        self.assertEqual(found[".text"].data, TEXT)
        self.assertEqual(found[".text"].address, BASE + 0x100)
        self.assertEqual(retail()[found[".text"].offset:][:len(TEXT)], TEXT)
        self.assertEqual(found[".text"].size, len(TEXT))
        self.assertEqual(found[".text"].sha256, hashlib.sha256(TEXT).hexdigest())

    def test_a_nobits_section_carries_no_file_bytes(self):
        found = sections(retail())
        self.assertEqual(found[".sbss"].data, b"")
        self.assertEqual(found[".sbss"].size, 0)

    def test_the_unnamed_null_section_is_never_extracted(self):
        self.assertEqual(sorted(sections(retail())), [".rodata", ".sbss", ".shstrtab", ".text"])

    def test_an_unknown_section_name_is_incomplete_and_a_file_without_elf_is_too(self):
        with self.assertRaises(Exception) as unknown:
            _ = sections(retail())[".nope"]
        self.assertIn(".nope", str(unknown.exception))
        with self.assertRaises(Exception):
            pinned_executable(__import__("pathlib").Path("/nonexistent/fr2"))


class ByteDiffTest(unittest.TestCase):
    def setUp(self):
        self.text = sections(retail())[".text"]

    def test_a_unit_with_identical_bytes_passes(self):
        verdict = compare(self.text, TEXT)
        self.assertEqual(verdict.status, "pass")
        self.assertIsNone(verdict.first_difference)
        self.assertEqual(verdict.matched_bytes, len(TEXT))

    def test_one_changed_word_fails_at_its_located_first_difference(self):
        rebuilt = bytearray(TEXT)
        rebuilt[12:16] = b"\xde\xad\xbe\xef"
        verdict = compare(self.text, bytes(rebuilt))
        self.assertEqual(verdict.status, "fail")
        self.assertEqual(verdict.reason, "bytes")
        self.assertEqual(verdict.matched_bytes, 12)
        difference = verdict.first_difference
        self.assertEqual(difference["offset"], 12)
        self.assertEqual(difference["address"], f"{BASE + 0x100 + 12:08x}")
        self.assertEqual(difference["file_offset"], f"{self.text.offset + 12:08x}")
        self.assertEqual(difference["word"], 3)
        self.assertEqual(difference["expected"], "00000000")
        self.assertEqual(difference["actual"], "deadbeef")

    def test_a_short_unit_fails_as_a_length_mismatch_at_the_first_missing_byte(self):
        verdict = compare(self.text, TEXT[:-4])
        self.assertEqual(verdict.status, "fail")
        self.assertEqual(verdict.reason, "length")
        self.assertEqual(verdict.matched_bytes, len(TEXT) - 4)
        self.assertEqual(verdict.first_difference["offset"], len(TEXT) - 4)

    def test_trailing_padding_or_a_partial_word_is_a_length_mismatch_not_a_pass(self):
        for unit in (TEXT + b"\0" * 4, TEXT + b"\0", TEXT[:-1]):
            verdict = compare(self.text, unit)
            self.assertEqual((verdict.status, verdict.reason), ("fail", "length"), unit)
            self.assertEqual(verdict.matched_bytes, min(len(unit), len(TEXT)))

    def test_a_missing_unit_or_section_is_incomplete_not_a_pass(self):
        self.assertEqual(compare(self.text, None).status, "incomplete")
        self.assertEqual(compare(self.text, b"").status, "incomplete")
        self.assertEqual(compare(None, TEXT).status, "incomplete")


class LedgerTest(unittest.TestCase):
    def test_only_bytes_of_game_owned_sections_can_count_as_matched(self):
        found = sections(retail())
        rows = ledger({"passed": [{"section": ".text", "scope": Scope.GAME_OWNED, "bytes": len(TEXT)}],
                       "failed": [], "incomplete": [],
                       "not_attempted": [{"section": ".rodata", "scope": Scope.GAME_OWNED,
                                          "bytes": len(RODATA)}]})
        self.assertEqual(rows["game_owned_bytes"], len(TEXT) + len(RODATA))
        self.assertEqual(rows["matched_bytes"], len(TEXT))
        self.assertEqual(rows["substitute_region_bytes"], 0)
        self.assertEqual(found[".text"].size, len(TEXT))

    def test_a_substitute_region_never_inflates_the_matched_fraction(self):
        rows = ledger({"passed": [{"section": ".rodata", "scope": Scope.SUBSTITUTE_REGION,
                                   "bytes": len(RODATA)}], "failed": [], "incomplete": []})
        self.assertEqual(rows["matched_bytes"], 0)
        self.assertEqual(rows["substitute_region_bytes"], len(RODATA))
        self.assertEqual(rows["matched_fraction"], 0.0)
        self.assertEqual(rows["substitute_disposition"], "substitute, not matched")

    def test_a_failed_substitute_stays_out_of_the_matched_denominator(self):
        rows = ledger({"passed": [], "failed": [{"section": ".rodata",
                                                  "scope": Scope.SUBSTITUTE_REGION,
                                                  "bytes": len(RODATA)}],
                       "incomplete": []})
        self.assertEqual(rows["substitute_region_bytes"], len(RODATA))
        self.assertEqual(rows["game_owned_bytes"], 0)
        self.assertEqual(rows["matched_bytes"], 0)
        self.assertEqual(rows["matched_fraction"], 0.0)
        self.assertEqual(rows["substitute_disposition"], "substitute, not matched")

    def test_a_section_outside_the_scope_is_not_counted_at_all(self):
        rows = ledger({"passed": [{"section": ".shstrtab", "scope": Scope.EXCLUDED, "bytes": 8}],
                       "failed": [], "incomplete": []})
        self.assertEqual(rows["game_owned_bytes"], 0)
        self.assertEqual(rows["matched_bytes"], 0)

    def test_the_ledger_is_false_when_nothing_game_owned_is_matched(self):
        rows = ledger({"passed": [], "failed": [{"section": ".text", "scope": Scope.GAME_OWNED,
                                                "bytes": len(TEXT)}], "incomplete": []})
        self.assertEqual(rows["matched_fraction"] == 0.0, True)


class OverlayNameTest(unittest.TestCase):
    def test_real_overlay_section_names_with_dots_are_valid_unit_names(self):
        name = ".DVP.overlay..0x0.4149910390.48.0"
        self.assertNotIn("/", name)
        self.assertEqual(scope_of(name), Scope.MIXED)


class ScopeTest(unittest.TestCase):
    def test_code_and_data_sections_are_mixed_and_metadata_is_excluded(self):
        for name in (".text", ".rodata", ".sdata", ".lit4", ".user_section3", ".DVP.overlay..0x0.4149910390.48.0"):
            self.assertEqual(scope_of(name), Scope.MIXED, name)
        for name in (".shstrtab", ".reginfo", ".DVP.ovlytab", ".mdebug.eabi64"):
            self.assertEqual(scope_of(name), Scope.EXCLUDED, name)

    def test_an_identical_mixed_section_passes_but_is_not_counted_as_matched(self):
        verdict = compare(sections(retail())[".text"], TEXT)
        self.assertEqual((verdict.status, verdict.scope), ("pass", "mixed"))
        rows = ledger({"passed": [{"section": ".text", "scope": verdict.scope, "bytes": len(TEXT)}],
                       "failed": [], "incomplete": []})
        self.assertEqual((rows["matched_bytes"], rows["game_owned_bytes"]), (0, 0))
        self.assertEqual((rows["mixed_bytes"], rows["mixed_bytes_identical"]), (len(TEXT), len(TEXT)))

    def test_only_the_recorded_misc3d_code_span_is_game_owned(self):
        from matching_diff import scope_of_range

        self.assertEqual(scope_of_range(".text", 0x001D1800, 60), Scope.GAME_OWNED)
        self.assertEqual(scope_of_range(".text", 0x001D1800, 64), Scope.MIXED)
        self.assertEqual(scope_of_range(".text", 0x001D17FC, 60), Scope.MIXED)
        self.assertEqual(scope_of_range(".rodata", 0x001D1800, 60), Scope.MIXED)


if __name__ == "__main__":
    unittest.main()
