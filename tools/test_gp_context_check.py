import json
import tempfile
import unittest
from pathlib import Path

from gp_context_check import GP, compare_exports, gp_names, predicted_address


def write_export(root: Path, functions: dict, pseudocode: dict):
    (root / "decompilation" / "functions").mkdir(parents=True)
    (root / "inventory.json").write_text(json.dumps({"inventory_count": len(functions), "functions": list(functions.values())}))
    (root / "decompilation" / "manifest.json").write_text(
        json.dumps({"failed": 0, "generated": len(functions), "inventory_count": len(functions)}))
    for entry, text in pseudocode.items():
        (root / "decompilation" / "functions" / f"{entry}.c").write_text(text)


def func(entry, text="addiu v0,v0,0x1"):
    return {"entry": entry, "name": f"FUN_{entry}", "size": 4, "blocks": [],
            "instructions": [{"address": entry, "text": text, "bytes": "00000000", "references": []}]}


class PredictionTest(unittest.TestCase):
    def test_negative_offset_is_added_to_gp_modulo_32_bits(self):
        self.assertEqual(GP, 0x295D70)
        self.assertEqual(predicted_address(0xFFFF9118), 0x28EE88)

    def test_positive_offset(self):
        self.assertEqual(predicted_address(0x10), 0x295D80)

    def test_names_cover_both_decompiler_spellings(self):
        text = "x = uGpffff9118; y = (&gp0xffffa920)[i]; z = pcGp00000010;"
        self.assertEqual(sorted(gp_names(text)), [0x10, 0xFFFF9118, 0xFFFFA920])


class CompareTest(unittest.TestCase):
    def run_compare(self, old_code, new_code, old_fn=None, new_fn=None):
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp) / "old", Path(tmp) / "new"
            fns = old_fn or {"00100000": func("00100000"), "00100100": func("00100100")}
            write_export(old, fns, old_code)
            write_export(new, new_fn or fns, new_code)
            return compare_exports(old, new)

    def checks(self, result):
        return {c["check"]: c["passed"] for c in result["checks"]}

    OLD = {"00100000": "x = uGpffff9118;\n", "00100100": "return 1;\n"}

    def test_resolved_names_with_the_predicted_address_pass(self):
        result = self.run_compare(self.OLD, {"00100000": "x = DAT_0028ee88;\n", "00100100": "return 1;\n"})
        self.assertEqual(result["status"], "pass", result["checks"])
        self.assertEqual(result["gp_names_before"], 1)
        self.assertEqual(result["gp_names_after"], 0)

    def test_names_left_behind_fail(self):
        result = self.run_compare(self.OLD, {"00100000": "x = uGpffff9118;\n", "00100100": "return 1;\n"})
        self.assertFalse(self.checks(result)["no gp-relative names remain"])

    def test_a_function_without_gp_names_must_not_change(self):
        result = self.run_compare(self.OLD, {"00100000": "x = DAT_0028ee88;\n", "00100100": "return 2;\n"})
        self.assertFalse(self.checks(result)["functions without gp names keep identical pseudocode"])

    def test_wrong_resolved_address_fails_the_prediction_check(self):
        result = self.run_compare(self.OLD, {"00100000": "x = DAT_00290000;\n", "00100100": "return 1;\n"})
        self.assertFalse(self.checks(result)["resolved addresses match the gp prediction"])

    def test_inventory_drift_fails(self):
        drifted = {"00100000": func("00100000", "addiu v0,v0,0x2"), "00100100": func("00100100")}
        result = self.run_compare(self.OLD, {"00100000": "x = DAT_0028ee88;\n", "00100100": "return 1;\n"}, new_fn=drifted)
        self.assertFalse(self.checks(result)["every function keeps size, blocks and instructions"])


if __name__ == "__main__":
    unittest.main()
