import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from evidence_common import Incomplete, Invalid
from test_code_inventory import fixture as raw_fixture
from verify_recompilation import audit


REPORT = """Functions discovered: 1
Functions processed: 1, recompiled: 1, stubs: 0, skipped: 0, decode failures: 0
Generated functions: 1
Unhandled instructions: 0
Warnings: 0, errors: 0
"""


def fixture():
    raw, static = raw_fixture()
    data = bytearray(raw + bytes(80))
    struct.pack_into("<H", data, 16, 2)
    struct.pack_into("<I", data, 32, 96)
    struct.pack_into("<H", data, 48, 2)
    struct.pack_into("<10I", data, 136, 0, 1, 6, 0x1000, 84, 12, 0, 0, 4, 0)
    static["executable_sha256"] = hashlib.sha256(data).hexdigest()
    source = "// Address: 0x1000 - 0x100c\n"
    source += "".join(f"// 0x{0x1000+i:x}: 0x{int.from_bytes(data[84+i:88+i], 'little'):x} nop\n" for i in (0, 4, 8))
    source += "void generated() {}\n"
    return bytes(data), static, source


class RecompilationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data, self.static, self.source = fixture()
        self.path = self.root / "sub_00001000_0x1000.cpp"
        self.path.write_text(self.source)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, report=REPORT):
        return audit(self.root, self.data, self.static, report)

    def test_exact_comments_bind_artifact_without_semantic_claim(self):
        result = self.check()
        self.assertEqual(result["unique_commented_instructions"], 3)
        self.assertEqual(result["generated_function_count"], 1)
        self.assertFalse(result["whole_game_decompiled"])
        # The fixture has an empty C++ body: comment checking does not certify it.
        self.assertIn("operation semantics remain unverified", result["claim_limits"][0])

    def test_corrupt_word_cannot_pass(self):
        self.path.write_text(self.source.replace("0x0 nop", "0x1 nop", 1))
        with self.assertRaisesRegex(Invalid, "differs from original"):
            self.check()

    def test_missing_entry_cannot_count(self):
        self.path.write_text(self.source.replace("// 0x1000: 0x0 nop\n", ""))
        with self.assertRaisesRegex(Invalid, "entry is absent"):
            self.check()

    def test_quoted_comments_do_not_count_as_evidence(self):
        self.path.write_text(self.source.replace("// 0x1000: 0x0 nop", 'const char* fake = "// 0x1000: 0x0 nop";'))
        with self.assertRaisesRegex(Invalid, "entry is absent"):
            self.check()

    def test_raw_string_forged_comments_cannot_count(self):
        for prefix in ("R", "u8R", "uR", "UR", "LR"):
            self.path.write_text('auto fake = ' + prefix + '"tag(";\n' + self.source + '\n)tag";\n')
            with self.assertRaisesRegex(Invalid, "one address range"):
                self.check()

    def test_shared_comment_scanner_ignores_raw_payload_but_preserves_real_comments(self):
        from verify_decompilation import _c_comments
        source = 'auto fake = R"tag("; /* WARNING fake */ // forged\n)tag";\n// real\n'
        self.assertEqual(list(_c_comments(source)), ["// real"])
        self.assertEqual(list(_c_comments('R"tag(unterminated /* fake */')), [])

    def test_filename_and_range_must_agree(self):
        self.path.write_text(self.source.replace("Address: 0x1000", "Address: 0x1004"))
        with self.assertRaisesRegex(Invalid, "filename and aligned"):
            self.check()

    def test_instruction_must_be_aligned_in_range(self):
        for source in (self.source.replace("0x1008:", "0x100a:"), self.source.replace("0x1008:", "0x100c:")):
            self.path.write_text(source)
            with self.assertRaisesRegex(Invalid, "unaligned or outside"):
                self.check()

    def test_section_and_load_mapping_must_agree(self):
        changed = bytearray(self.data)
        struct.pack_into("<I", changed, 136 + 16, 88)
        self.data = bytes(changed)
        self.static["executable_sha256"] = hashlib.sha256(changed).hexdigest()
        with self.assertRaisesRegex(Invalid, "mapping"):
            self.check()

    def test_report_counters_must_match_artifacts(self):
        for report in (REPORT.replace("Generated functions: 1", "Generated functions: 2"),
                       REPORT + "Generated functions: 1\n",
                       REPORT.replace("recompiled: 1", "recompiled: 0")):
            with self.assertRaises(Invalid):
                self.check(report)

    def test_missing_or_stubbed_report_is_not_complete(self):
        with self.assertRaises(Incomplete):
            self.check(REPORT.replace("stubs: 0", "stubs: 1"))
        with self.assertRaises(Invalid):
            self.check("success!")

    def test_report_errors_fail_and_unhandled_is_incomplete(self):
        with self.assertRaises(Invalid):
            self.check(REPORT.replace("errors: 0", "errors: 1"))
        with self.assertRaises(Incomplete):
            self.check(REPORT.replace("Unhandled instructions: 0", "Unhandled instructions: 1"))

    def test_wrong_static_identity_cannot_be_comparison_oracle(self):
        self.static["executable_sha256"] = "wrong"
        with self.assertRaisesRegex(Invalid, "SHA-256"):
            self.check()

    def test_symlink_cannot_escape_source_root(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / self.path.name
            target.write_text(self.source)
            self.path.unlink()
            self.path.symlink_to(target)
            with self.assertRaisesRegex(Invalid, "symlink"):
                self.check()

    def test_partial_comments_report_gaps_without_certifying_translation(self):
        self.path.write_text(self.source.replace("// 0x1008: 0x0 nop\n", ""))
        result = self.check()
        self.assertEqual(result["saved_instructions_absent_from_comments"], 1)
        self.assertFalse(result["whole_game_decompiled"])


if __name__ == "__main__":
    unittest.main()
