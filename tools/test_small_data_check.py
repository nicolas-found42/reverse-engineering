import json
import tempfile
import unittest
from pathlib import Path

from small_data_check import compare_exports, pool_tokens

PLAN = {"entries": [{"address": "0028dde0", "type": "float", "size": 4, "functions": ["00100000"]}],
        "constant_pool": {"name": ".lit4", "start": "0028dd80", "end": "0028ebc3"}}


def func(entry, text="addiu v0,v0,0x1"):
    return {"entry": entry, "name": f"FUN_{entry}", "size": 4, "blocks": [],
            "instructions": [{"address": entry, "text": text, "bytes": "00000000", "references": []}]}


def write_export(root: Path, functions: dict, pseudocode: dict):
    (root / "decompilation" / "functions").mkdir(parents=True)
    (root / "inventory.json").write_text(json.dumps({"inventory_count": len(functions), "functions": list(functions.values())}))
    (root / "decompilation" / "manifest.json").write_text(
        json.dumps({"failed": 0, "generated": len(functions), "inventory_count": len(functions)}))
    for entry, text in pseudocode.items():
        (root / "decompilation" / "functions" / f"{entry}.c").write_text(text)


class TokenTest(unittest.TestCase):
    def test_tokens_in_the_pool_range_are_counted_by_address(self):
        text = "a = fRam0028dde0 * _DAT_0028dd80; b = uRam0028ebc0; c = DAT_0028dde4; d = uRam0028ec00; e = FLOAT_0028dde8;"
        self.assertEqual(pool_tokens(text, 0x28DD80, 0x28EBC3), 5)


class CompareTest(unittest.TestCase):
    FUNCTIONS = {"00100000": func("00100000"), "00100100": func("00100100")}
    OLD = {"00100000": "x = fRam0028dde0 * 2.0;\n", "00100100": "return 1;\n"}

    def run_compare(self, new_code, new_fn=None):
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp) / "old", Path(tmp) / "new"
            write_export(old, self.FUNCTIONS, self.OLD)
            write_export(new, new_fn or self.FUNCTIONS, new_code)
            return compare_exports(PLAN, old, new)

    def checks(self, result):
        return {c["check"]: c["passed"] for c in result["checks"]}

    def test_a_touching_function_may_change_and_pool_names_disappear(self):
        result = self.run_compare({"00100000": "x = 0.5 * 2.0;\n", "00100100": "return 1;\n"})
        self.assertEqual(result["status"], "pass", result["checks"])
        self.assertEqual(result["pool_tokens_before"], 1)
        self.assertEqual(result["pool_tokens_after"], 0)

    def test_a_function_that_touches_no_planned_address_must_not_change(self):
        result = self.run_compare({"00100000": "x = 0.5 * 2.0;\n", "00100100": "return 2;\n"})
        self.assertFalse(self.checks(result)["functions that touch no planned address keep identical pseudocode"])

    def test_a_function_missing_from_the_plan_list_may_change_when_its_old_text_names_a_planned_address(self):
        old = {"00100000": "return 1;\n", "00100100": "x = fRam0028dde0;\n"}
        with tempfile.TemporaryDirectory() as tmp:
            root_old, root_new = Path(tmp) / "old", Path(tmp) / "new"
            write_export(root_old, self.FUNCTIONS, old)
            write_export(root_new, self.FUNCTIONS, {"00100000": "return 1;\n", "00100100": "x = 0.5;\n"})
            result = compare_exports(PLAN, root_old, root_new)
        self.assertEqual(result["status"], "pass", result["checks"])
        self.assertEqual(result["unlisted_functions_naming_a_planned_address"], 1)

    def test_a_mention_inside_a_planned_span_counts(self):
        old = {"00100000": "return 1;\n", "00100100": "x = uRam0028dde2;\n"}
        with tempfile.TemporaryDirectory() as tmp:
            root_old, root_new = Path(tmp) / "old", Path(tmp) / "new"
            write_export(root_old, self.FUNCTIONS, old)
            write_export(root_new, self.FUNCTIONS, {"00100000": "return 1;\n", "00100100": "x = 7;\n"})
            result = compare_exports(PLAN, root_old, root_new)
        self.assertEqual(result["unlisted_functions_naming_a_planned_address"], 1)

    def test_a_renamed_pool_global_is_not_an_inlined_constant(self):
        result = self.run_compare({"00100000": "x = FLOAT_0028dde0 * 2.0;\n", "00100100": "return 1;\n"})
        self.assertFalse(self.checks(result)["literal-pool reads become numeric constants"])

    def test_pool_names_left_behind_fail(self):
        result = self.run_compare({"00100000": "x = fRam0028dde0 * 2.0;\n", "00100100": "return 1;\n"})
        self.assertFalse(self.checks(result)["literal-pool reads become numeric constants"])

    def test_listing_drift_fails(self):
        drift = {"00100000": func("00100000", "addiu v0,v0,0x2"), "00100100": func("00100100")}
        result = self.run_compare({"00100000": "x = 0.5;\n", "00100100": "return 1;\n"}, new_fn=drift)
        self.assertFalse(self.checks(result)["every function keeps size, blocks and instructions"])


if __name__ == "__main__":
    unittest.main()
