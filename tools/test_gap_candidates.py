import hashlib
import unittest

from evidence_common import Invalid
from test_text_denominator import JR_RA, NOP, elf_with, elf_with_data
from test_text_references import addr, static_owning
from verify_gap_candidates import assess_candidates

POP_32 = 0x27BD0020   # addiu sp,sp,32
POP_16 = 0x27BD0010
PUSH_32 = 0x27BDFFE0  # addiu sp,sp,-32 (same word as ADDIU_SP)
SW_RA = 0xAFBF0010
LW_RA = 0x8FBF0010
ADDU_V0 = 0x00851021  # addu v0,a0,a1

OWNED_FN = [PUSH_32, SW_RA, LW_RA, JR_RA, POP_32]   # indices 0-4, ends in jr ra + delay slot


def row(data, first, count, **extra):
    start, end = addr(first), addr(first + count)
    window = data[84 + 4 * first:84 + 4 * (first + count)]
    base = {"entry": f"{start:08x}", "start": f"{start:08x}", "end": f"{end:08x}",
            "window_sha256": hashlib.sha256(window).hexdigest(), "next_state": "undefined"}
    return {**base, **extra}


def build(candidate_words, data_words=None, **row_extra):
    words = OWNED_FN + candidate_words
    data = elf_with_data(words, data_words) if data_words else elf_with(words)
    static = static_owning(data, range(len(OWNED_FN)))
    return data, static, {"seeds": [row(data, len(OWNED_FN), len(candidate_words), **row_extra)]}


def only(result):
    return result["candidates"][0]


class GapCandidatesTest(unittest.TestCase):
    def test_framed_candidate_that_restores_its_frame_is_frame_consistent(self):
        data, static, config = build([PUSH_32, SW_RA, LW_RA, JR_RA, POP_32])
        self.assertEqual(only(assess_candidates(data, static, config))["frame"], "frame_consistent")

    def test_leaf_candidate_without_stack_use_is_leaf_consistent(self):
        data, static, config = build([ADDU_V0, JR_RA, NOP])
        self.assertEqual(only(assess_candidates(data, static, config))["frame"], "leaf_consistent")

    def test_candidate_that_pops_a_different_frame_is_frame_inconsistent(self):
        data, static, config = build([PUSH_32, SW_RA, JR_RA, POP_16])
        self.assertEqual(only(assess_candidates(data, static, config))["frame"], "frame_inconsistent")

    def test_candidate_after_an_owned_return_and_delay_slot_is_after_boundary(self):
        data, static, config = build([ADDU_V0, JR_RA, NOP])
        self.assertTrue(only(assess_candidates(data, static, config))["after_boundary"])

    def test_candidate_not_preceded_by_a_return_is_not_after_boundary(self):
        data = elf_with([NOP, ADDU_V0, ADDU_V0, JR_RA, NOP])
        static = static_owning(data, [0])
        config = {"seeds": [row(data, 1, 4)]}
        self.assertFalse(only(assess_candidates(data, static, config))["after_boundary"])

    def test_end_boundary_comes_from_the_guard_next_state(self):
        for state, expected in (("function_entry", True), ("batch_entry", True), ("undefined", False)):
            data, static, config = build([ADDU_V0, JR_RA, NOP], next_state=state)
            self.assertEqual(only(assess_candidates(data, static, config))["ends_at_boundary"], expected)

    def test_static_reference_to_the_entry_is_recorded(self):
        entry = addr(len(OWNED_FN))
        data, static, config = build([ADDU_V0, JR_RA, NOP], data_words=[entry, 0])
        self.assertTrue(only(assess_candidates(data, static, config))["referenced"])
        data, static, config = build([ADDU_V0, JR_RA, NOP])
        self.assertFalse(only(assess_candidates(data, static, config))["referenced"])

    def test_window_hash_that_differs_from_the_executable_is_invalid(self):
        data, static, config = build([ADDU_V0, JR_RA, NOP])
        config["seeds"][0]["window_sha256"] = "0" * 64
        with self.assertRaises(Invalid):
            assess_candidates(data, static, config)

    def test_tiers_count_independent_evidence_classes_and_controls_use_saved_functions(self):
        data, static, config = build([ADDU_V0, JR_RA, NOP], next_state="function_entry")
        result = assess_candidates(data, static, config)
        self.assertEqual(only(result)["evidence_classes"], ["frame", "layout"])
        self.assertEqual(result["summary"]["tiers"], {"A": 1, "B": 0, "C": 0})
        self.assertEqual(result["controls"]["saved_functions"], {"frame_consistent": 1})
        self.assertFalse(result["whole_game_decompiled"])

    def test_candidate_missing_a_frame_pass_is_a_lower_tier(self):
        data, static, config = build([PUSH_32, SW_RA, JR_RA, POP_16], next_state="function_entry")
        result = assess_candidates(data, static, config)
        self.assertEqual(only(result)["evidence_classes"], ["layout"])
        self.assertEqual(result["summary"]["tiers"], {"A": 0, "B": 0, "C": 1})
