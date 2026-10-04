import tempfile
import unittest
from pathlib import Path

from verify_decompilation_quality import measure_directory

TWO_ARGS = """
int FUN_00100000(int param_1,undefined8 param_2)

{
  return param_1;
}
"""
CALLER = """
void FUN_00100100(void)

{
  FUN_00100000(1,2);
  FUN_00100000(1);
  FUN_00100200(&gp0xffffa8a8,*(int *)(&gp0xffffa8c8 + iGpffffa8c0 * 4));
  return;
}
"""
WARNED = """
/* WARNING: Subroutine does not return */
void FUN_00100200(undefined4 param_1,
                 undefined8 param_2,long param_3)

{
  /* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
  undefined4 local_10;
  return;
}
"""
NAMED = """
void ps2sdk_SetupThread(void)

{
  return;
}
"""


def write(directory, files):
    root = Path(directory)
    for name, text in files.items():
        (root / name).write_text(text)


class QualityTest(unittest.TestCase):
    def measure(self, files):
        with tempfile.TemporaryDirectory() as directory:
            write(directory, files)
            return measure_directory(Path(directory))

    def test_types_gp_tokens_and_warning_classes_are_counted(self):
        result = self.measure({"00100000.c": TWO_ARGS, "00100100.c": CALLER, "00100200.c": WARNED})
        self.assertEqual(result["functions"], 3)
        self.assertEqual(result["undefined_type_tokens"], 4)
        self.assertEqual(result["gp_unresolved"], {"tokens": 2, "functions": 1})
        self.assertEqual(result["warnings"], {"Subroutine does not return": 1, "Globals starting with": 1})

    def test_call_arity_is_compared_with_the_callee_header(self):
        result = self.measure({"00100000.c": TWO_ARGS, "00100100.c": CALLER, "00100200.c": WARNED})
        arity = result["call_arity"]
        self.assertEqual((arity["match"], arity["mismatch"], arity["unknown_callee"]), (1, 2, 0))
        self.assertEqual(arity["mismatch_by_difference"], {"-1": 2})

    def test_unnamed_and_named_functions_are_separated(self):
        result = self.measure({"00100000.c": TWO_ARGS, "00100300.c": NAMED})
        self.assertEqual(result["named_functions"], 1)

    def test_headers_that_cannot_be_parsed_are_reported_not_hidden(self):
        result = self.measure({"00100000.c": "this is not a function\n"})
        self.assertEqual(result["header_parse_failures"], 1)
        self.assertTrue(any("regular expressions" in limit for limit in result["claim_limits"]))
