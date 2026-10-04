import unittest

from holdout_gap_method import (
    choose_holdout,
    contiguous_functions,
    holdout_coverage,
    holdout_static,
    score_candidates,
)


def fn(entry, words):
    rows = [{"address": f"{entry + 4 * i:08x}", "bytes": "00000000"} for i in range(words)]
    return {"entry": f"{entry:08x}", "instructions": rows}


def static_of(*functions):
    return {"schema_version": 1, "inventory_count": len(functions), "functions": list(functions)}


class ContiguousFunctionsTest(unittest.TestCase):
    def test_only_functions_with_gap_free_bodies_are_ground_truth(self):
        gappy = fn(0x2000, 4)
        del gappy["instructions"][1]
        found = contiguous_functions(static_of(fn(0x1000, 3), gappy))
        self.assertEqual(found, [(0x1000, 0x100C)])


class CallerFilterTest(unittest.TestCase):
    def test_functions_with_direct_callers_can_be_left_out_of_the_ground_truth(self):
        called, orphan = fn(0x1000, 3), fn(0x2000, 3)
        called["callers"], orphan["callers"] = ["00003000"], []
        static = static_of(called, orphan)
        self.assertEqual(contiguous_functions(static), [(0x1000, 0x100C), (0x2000, 0x200C)])
        self.assertEqual(contiguous_functions(static, without_callers=True), [(0x2000, 0x200C)])


class HoldoutTest(unittest.TestCase):
    def test_choice_is_deterministic_and_sized_by_fraction(self):
        truth = [(0x1000 + 0x100 * i, 0x1010 + 0x100 * i) for i in range(20)]
        first = choose_holdout(truth, 0.25, seed=7)
        self.assertEqual(first, choose_holdout(truth, 0.25, seed=7))
        self.assertEqual(len(first), 5)
        self.assertNotEqual(first, choose_holdout(truth, 0.25, seed=8))

    def test_held_functions_leave_the_export_and_their_bytes_become_undefined(self):
        static = static_of(fn(0x1000, 3), fn(0x2000, 2))
        reduced = holdout_static(static, [(0x2000, 0x2008)])
        self.assertEqual([f["entry"] for f in reduced["functions"]], ["00001000"])
        self.assertEqual(reduced["inventory_count"], 1)
        self.assertEqual(len(static["functions"]), 2)
        coverage = {"blocks": [{"name": ".text", "start": "00001000", "end": "00004fff", "instruction_bytes": 20, "undefined_bytes": 4, "undefined_ranges": [
            {"start": "00003000", "end": "00003003", "bytes": 4}], "function_instruction_bytes": 20}]}
        changed = holdout_coverage(coverage, [(0x2000, 0x2008)])
        block = changed["blocks"][0]
        self.assertEqual(block["undefined_bytes"], 12)
        self.assertEqual(block["function_instruction_bytes"], 12)
        self.assertIn({"start": "00002000", "end": "00002007", "bytes": 8}, block["undefined_ranges"])
        self.assertEqual(coverage["blocks"][0]["undefined_bytes"], 4)


class ScoreTest(unittest.TestCase):
    def rows(self, *spans):
        return [{"entry": f"{a:08x}", "start": f"{a:08x}", "end": f"{b:08x}"} for a, b in spans]

    def test_recall_and_precision_are_counted_against_held_out_truth(self):
        held = [(0x1000, 0x1010), (0x2000, 0x2020), (0x3000, 0x3008)]
        rows = self.rows((0x1000, 0x1010),      # exact
                         (0x2000, 0x2010),      # right start, wrong end
                         (0x2010, 0x2020),      # starts inside a held function: false
                         (0x9000, 0x9010))      # outside every held span: not scored
        score = score_candidates(held, rows, tier_of={"00001000": "A", "00002000": "B"})
        self.assertEqual(score["held_out"], 3)
        self.assertEqual(score["recovered"], {"exact": 1, "start_only": 1, "missed": 1})
        self.assertEqual(score["inside_held_spans"], {"candidates": 3, "exact": 1, "start_only": 1, "false_start": 1})
        self.assertEqual(score["by_tier"]["A"], {"candidates": 1, "exact": 1, "start_only": 0, "false_start": 0})
        self.assertAlmostEqual(score["exact_precision"], 1 / 3)
        self.assertAlmostEqual(score["exact_recall"], 1 / 3)


class DetailScoreTest(unittest.TestCase):
    def test_precision_is_split_by_evidence_classes_and_frame_category(self):
        held = [(0x1000, 0x1010), (0x2000, 0x2020)]
        rows = [{"entry": "00001000", "start": "00001000", "end": "00001010"},
                {"entry": "00002000", "start": "00002000", "end": "00002010"}]
        detail = {"00001000": {"evidence_classes": ["frame", "layout"], "frame": "frame_consistent"},
                  "00002000": {"evidence_classes": ["frame"], "frame": "no_return"}}
        score = score_candidates(held, rows, detail_of=detail)
        self.assertEqual(score["by_evidence"]["frame+layout"]["exact"], 1)
        self.assertEqual(score["by_evidence"]["frame"]["start_only"], 1)
        self.assertEqual(score["by_frame"]["no_return"]["candidates"], 1)
