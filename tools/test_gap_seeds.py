import unittest

from gap_seeds import gap_seeds
from test_text_denominator import ADDIU_SP, JR_RA, LW_RA, NOP
from test_text_references import addr, jal, scenario

BODY = [ADDIU_SP, LW_RA, JR_RA, NOP]


class GapSeedsTest(unittest.TestCase):
    def test_span_start_with_a_stack_prologue_is_a_seed_by_two_rules(self):
        data, static = scenario([JR_RA, NOP] + BODY, owned=range(2))
        rules = gap_seeds(data, static)
        self.assertEqual(rules["span_start_prologue"], {addr(2)})
        self.assertEqual(rules["span_start_any"], {addr(2)})

    def test_word_after_a_return_and_delay_slot_inside_a_span_is_a_seed(self):
        data, static = scenario([JR_RA, NOP] + BODY + BODY, owned=range(2))
        rules = gap_seeds(data, static)
        self.assertEqual(rules["after_return_in_span"], {addr(6)})
        self.assertEqual(rules["after_return_prologue"], {addr(6)})
        self.assertEqual(rules["prologue_anywhere"], {addr(2), addr(6)})

    def test_reference_targets_are_seeds(self):
        data, static = scenario([jal(addr(5)), NOP, JR_RA, NOP] + [NOP] + BODY, owned=range(4))
        self.assertEqual(gap_seeds(data, static)["reference_target"], {addr(5)})

    def test_zero_words_do_not_start_a_seed(self):
        data, static = scenario([JR_RA, NOP, NOP] + BODY, owned=range(2))
        self.assertNotIn(addr(2), gap_seeds(data, static)["span_start_any"])
