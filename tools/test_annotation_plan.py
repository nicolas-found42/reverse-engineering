import unittest

from annotation_plan import build_plan

SOURCE_MAP = {"files": [
    {"path": "../m/a.c", "kind": "unit", "functions": [{"entry": "00001000", "lines": [12, 40]}, {"entry": "00001100", "lines": []}]},
    {"path": "../m/h.h", "kind": "header", "functions": [{"entry": "00001000", "lines": [3]}]}],
    "string_attribution": {"functions": [{"entry": "00001200", "unit": "../m/b.c", "votes": 3}]}}
STUBS = {"stubs": [
    {"address": "00002000", "number": 60, "names": ["SetupThread", "RFU060"], "ownership": "saved_function"},
    {"address": "00002010", "number": 2, "names": ["SetGsCrt"], "ownership": "saved_function"},
    {"address": "00002020", "number": 9, "names": ["RFU009"], "ownership": "saved_function"},
    {"address": "00002030", "number": 99, "names": [], "ownership": "saved_function"},
    {"address": "00002040", "number": 5, "names": ["Foo"], "ownership": "unowned"}]}
SHA = "ab" * 32


class PlanTest(unittest.TestCase):
    def plan(self):
        return {e["entry"]: e for e in build_plan(SOURCE_MAP, STUBS, SHA)["entries"]}

    def test_direct_source_functions_get_path_and_lines_in_a_labelled_comment(self):
        entry = self.plan()["00001000"]
        self.assertIn("../m/a.c", entry["comment"])
        self.assertIn("12, 40", entry["comment"])
        self.assertIn("direct reference", entry["comment"])
        self.assertNotIn("h.h", entry["comment"])
        self.assertNotIn("rename", entry)

    def test_direct_function_without_a_line_still_gets_the_path(self):
        self.assertIn("../m/a.c", self.plan()["00001100"]["comment"])

    def test_string_attributed_functions_are_labelled_as_lower_evidence(self):
        comment = self.plan()["00001200"]["comment"]
        self.assertIn("../m/b.c", comment)
        self.assertIn("string position", comment)

    def test_only_stubs_with_one_meaningful_sdk_name_are_renamed(self):
        plan = self.plan()
        self.assertEqual(plan["00002010"]["rename"], "ps2sdk_SetGsCrt")
        for entry in ("00002000", "00002020"):
            self.assertNotIn("rename", plan[entry])
        self.assertNotIn("00002030", plan)
        self.assertIn("SetupThread", plan["00002000"]["comment"])
        self.assertIn("RFU060", plan["00002000"]["comment"])
        self.assertIn("not a verified original", plan["00002010"]["comment"])

    def test_unowned_stubs_are_not_in_the_plan_and_the_plan_pins_the_executable(self):
        plan = build_plan(SOURCE_MAP, STUBS, SHA)
        self.assertNotIn("00002040", {e["entry"] for e in plan["entries"]})
        self.assertEqual(plan["executable_sha256"], SHA)
        self.assertEqual(plan["counts"], {"entries": 6, "renames": 1, "comments": 6})

    def test_function_with_both_source_and_stub_evidence_keeps_both_lines(self):
        stubs = {"stubs": [{"address": "00001000", "number": 2, "names": ["SetGsCrt"], "ownership": "saved_function"}]}
        entry = {e["entry"]: e for e in build_plan(SOURCE_MAP, stubs, SHA)["entries"]}["00001000"]
        self.assertIn("../m/a.c", entry["comment"])
        self.assertIn("SetGsCrt", entry["comment"])


class DuplicateStubTest(unittest.TestCase):
    def test_two_stubs_with_the_same_sdk_name_are_not_renamed_so_names_stay_unique(self):
        stubs = {"stubs": [
            {"address": "00002000", "number": 2, "names": ["SetGsCrt"], "ownership": "saved_function"},
            {"address": "00002100", "number": 2, "names": ["SetGsCrt"], "ownership": "saved_function"},
            {"address": "00002200", "number": 3, "names": ["Other"], "ownership": "saved_function"}]}
        plan = {e["entry"]: e for e in build_plan({"files": [], "string_attribution": {"functions": []}}, stubs, SHA)["entries"]}
        self.assertNotIn("rename", plan["00002000"])
        self.assertNotIn("rename", plan["00002100"])
        self.assertIn("SetGsCrt", plan["00002100"]["comment"])
        self.assertEqual(plan["00002200"]["rename"], "ps2sdk_Other")
