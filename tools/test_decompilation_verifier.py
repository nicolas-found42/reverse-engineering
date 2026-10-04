"""Tests for the public decompilation export verifier boundary."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import verify_decompilation


class DecompilationVerifier(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.executable = self.root / "game.elf"
        self.executable.write_bytes(b"game executable")
        self.executable_sha256 = hashlib.sha256(b"game executable").hexdigest()
        self.static_path = self.root / "static-export.json"
        self.manifest_path = self.root / "manifest.json"
        self.functions = self.root / "functions"
        self.functions.mkdir()
        self.inventory = {
            "schema_version": 1,
            "program": "SLES_517.05",
            "language": "r5900:LE:32:default",
            "executable_sha256": self.executable_sha256,
            "inventory_count": 2,
            "functions": [
                {"entry": "00100000"},
                {"entry": "00100010"},
            ],
        }
        self.rows = []
        for entry, code in (
            ("00100000", "/* WARNING: example */\nvoid f(void) {}\n"),
            ("00100010", "void g(void) {}\n"),
        ):
            data = code.encode()
            (self.functions / f"{entry}.c").write_bytes(data)
            self.rows.append(
                {
                    "entry": entry,
                    "status": "generated",
                    "path": f"functions/{entry}.c",
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "message": "",
                }
            )
        self.manifest = {
            "schema_version": 1,
            "program": "SLES_517.05",
            "language": "r5900:LE:32:default",
            "executable_sha256": self.executable_sha256,
            "inventory_count": 2,
            "scope": "all saved functions",
            "status": "generated",
            "terminal_reason": "function iteration finished",
            "functions": self.rows,
            "processed": 2,
            "generated": 2,
            "failed": 0,
            "missing_selected_entries": [],
        }
        self.save()

    def rewrite_code(self, entry, code):
        data = code.encode()
        (self.functions / f"{entry}.c").write_bytes(data)
        row = next(row for row in self.rows if row["entry"] == entry)
        row["bytes"] = len(data)
        row["sha256"] = hashlib.sha256(data).hexdigest()

    def save(self):
        self.static_path.write_text(json.dumps(self.inventory))
        self.manifest_path.write_text(json.dumps(self.manifest))

    def test_complete_export_matches_static_inventory_and_artifacts(self):
        result = verify_decompilation.verify(
            self.manifest_path, self.static_path, self.executable
        )
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["inventory_count"], 2)
        self.assertEqual(result["generated_count"], 2)
        self.assertEqual(result["warning_comment_count"], 1)
        self.assertEqual(
            result["warning_categories"],
            [{
                "category": "other warning",
                "count": 1,
                "affected_function_count": 1,
                "entries": ["00100000"],
            }],
        )
        self.assertEqual(
            result["warning_comments"],
            [{"entry": "00100000", "text": "/* WARNING: example */"}],
        )
        self.assertEqual(result["decompile_failures"], [])

    def test_warning_comments_are_separate_from_decompiler_error_messages(self):
        self.rows[1]["message"] = "WARNING: decompiler reported a benign diagnostic"
        self.save()
        result = verify_decompilation.verify(
            self.manifest_path, self.static_path, self.executable
        )
        self.assertEqual(result["warning_comment_count"], 1)
        self.assertEqual(result["decompile_failures"], [])

    def test_warning_categories_keep_counts_and_affected_addresses(self):
        self.rewrite_code(
            "00100000", "/* WARNING: Subroutine does not return */\n"
        )
        self.rewrite_code(
            "00100010", "/* WARNING: Removing unreachable block (ram,0x00100050) */\n"
        )
        self.save()
        result = verify_decompilation.verify(
            self.manifest_path, self.static_path, self.executable
        )
        self.assertEqual(
            result["warning_categories"],
            [
                {
                    "category": "subroutine does not return",
                    "count": 1,
                    "affected_function_count": 1,
                    "entries": ["00100000"],
                },
                {
                    "category": "unreachable block",
                    "count": 1,
                    "affected_function_count": 1,
                    "entries": ["00100010"],
                },
            ],
        )

    def test_failed_function_is_incomplete_and_keeps_the_error_message(self):
        (self.functions / "00100010.c").unlink()
        self.rows[1] = {
            "entry": "00100010",
            "status": "failed",
            "message": "Low-level Error: Backward normalization not implemented",
        }
        self.manifest.update(
            {"status": "incomplete", "generated": 1, "failed": 1}
        )
        self.save()
        with self.assertRaises(verify_decompilation.Incomplete) as caught:
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )
        self.assertEqual(caught.exception.details["failed_count"], 1)
        self.assertEqual(
            caught.exception.details["decompile_failures"],
            [{"entry": "00100010", "message": "Low-level Error: Backward normalization not implemented"}],
        )

    def test_uncovered_static_functions_are_incomplete_not_a_pass(self):
        (self.functions / "00100010.c").unlink()
        self.rows.pop()
        self.manifest.update(
            {
                "status": "incomplete",
                "processed": 1,
                "generated": 1,
                "failed": 0,
            }
        )
        self.save()
        with self.assertRaises(verify_decompilation.Incomplete) as caught:
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )
        self.assertEqual(caught.exception.details["missing_inventory_entry_count"], 1)
        self.assertEqual(
            caught.exception.details["missing_inventory_entry_sample"], ["00100010"]
        )

    def test_selected_scope_never_claims_full_inventory_completion(self):
        (self.functions / "00100010.c").unlink()
        self.rows.pop()
        self.manifest.update(
            {
                "scope": "selected entry addresses",
                "processed": 1,
                "generated": 1,
            }
        )
        self.save()
        with self.assertRaises(verify_decompilation.Incomplete) as caught:
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )
        self.assertIn(
            "export scope is selected functions, not the full static inventory",
            str(caught.exception),
        )

    def test_executable_identity_must_match_all_three_inputs(self):
        self.manifest["executable_sha256"] = "0" * 64
        self.save()
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_duplicate_manifest_addresses_fail(self):
        self.rows[1]["entry"] = self.rows[0]["entry"]
        self.rows[1]["path"] = self.rows[0]["path"]
        self.save()
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_artifact_hash_and_claimed_counts_are_enforced(self):
        (self.functions / "00100000.c").write_bytes(b"changed")
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_status_must_agree_with_row_outcomes(self):
        self.rows[1]["status"] = "failed"
        self.manifest["failed"] = 1
        self.manifest["generated"] = 1
        # A failed row requires an incomplete manifest; claiming generated is a contradiction.
        self.save()
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_generated_artifact_path_cannot_escape_export_directory(self):
        self.rows[0]["path"] = "../outside.c"
        self.save()
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_unlisted_c_file_is_a_manifest_discrepancy(self):
        (self.functions / "00ffffff.c").write_text("void extra(void) {}\n")
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )
        self.rewrite_code("00100000", "void f(void) {}\n")
        self.manifest["generated"] = 1
        self.save()
        with self.assertRaises(verify_decompilation.Invalid):
            verify_decompilation.verify(
                self.manifest_path, self.static_path, self.executable
            )

    def test_string_literal_warning_is_not_treated_as_a_comment(self):
        self.rewrite_code("00100010", 'const char *s = "WARNING: text";\n')
        self.rows[1]["message"] = "WARNING: decompiler metadata"
        self.save()
        result = verify_decompilation.verify(
            self.manifest_path, self.static_path, self.executable
        )
        self.assertEqual(result["warning_comment_count"], 1)
        self.assertEqual(result["warning_comments"][0]["entry"], "00100000")

    def test_cli_uses_immutable_bundle_and_keeps_source_out_of_stdout(self):
        output = self.root / "results"
        command = [
            sys.executable,
            str(Path(verify_decompilation.__file__).resolve()),
            "--manifest", str(self.manifest_path),
            "--static-export", str(self.static_path),
            "--executable", str(self.executable),
            "--output", str(output),
        ]
        run = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn("WARNING: example", run.stdout)
        results = list(output.glob("*/result.json"))
        self.assertEqual(len(results), 1)
        saved = json.loads(results[0].read_text())
        self.assertEqual((saved["check"], saved["status"]), ("decompilation", "pass"))
        self.assertEqual(saved["details"]["warning_comment_count"], 1)


if __name__ == "__main__":
    unittest.main()
