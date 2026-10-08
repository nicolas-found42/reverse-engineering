import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import compiler_probe
from compiler_probe import run_probe


class CompilerProbeTest(unittest.TestCase):
    def test_unresolved_launcher_cannot_be_hashed_as_the_compiler_or_objcopy(self):
        for phase, command in (("compile", ["/bin/bash", str(self.compiler)]),
                               ("compile", ["/usr/bin/env", str(self.compiler)]),
                               ("objcopy", ["/bin/bash", str(self.objcopy)])):
            with self.subTest(phase=phase, command=command):
                manifest = self.manifest()
                body = json.loads(manifest.read_text())
                body["candidates"][0][phase] = command
                manifest.write_text(json.dumps(body))
                with patch("compiler_probe.subprocess.run") as launched:
                    result = run_probe(manifest, self.root / "out")
                self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
                launched.assert_not_called()

    def test_declared_compiler_and_objcopy_must_identify_the_invoked_tool(self):
        for field in ("compiler_executable", "objcopy_executable"):
            with self.subTest(field=field):
                manifest = self.manifest()
                body = json.loads(manifest.read_text())
                body["candidates"][0][field] = str(self.linker)
                manifest.write_text(json.dumps(body))
                with patch("compiler_probe.subprocess.run") as launched:
                    result = run_probe(manifest, self.root / "out")
                self.assertEqual(result["status"], "incomplete")
                self.assertIn("differs from the invoked", result["candidates"][0]["reason"])
                launched.assert_not_called()

    def test_probe_receipt_paths_and_command_inputs_survive_the_run(self):
        result = run_probe(self.manifest(), self.root / "out")
        for key in ("manifest", "source", "reference"):
            self.assertTrue(Path(result[key]["path"]).is_file())
        self.assertTrue(list((self.root / "out").glob("fr2-compiler-probe-*/candidate.o")))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "probe.c"
        self.source.write_text("int probe(void) { return 7; }\n")
        self.reference = self.root / "retail-function.bin"
        self.reference.write_bytes(bytes.fromhex("01020304"))
        self.compiler = self.root / "fake-cc"
        self.compiler.write_text("#!/bin/bash\ncp \"$FAKE_OBJECT\" \"${@: -1}\"\n")
        self.compiler.chmod(0o755)
        self.objcopy = self.root / "fake-objcopy"
        self.objcopy.write_text("""#!/usr/bin/env python3
import os, pathlib, sys
target = sys.argv[sys.argv.index('--dump-section') + 1].split('=', 1)[1]
pathlib.Path(target).write_bytes(pathlib.Path(sys.argv[-1]).read_bytes())
""")
        self.objcopy.chmod(0o755)
        self.linker = self.root / "fake-ld"
        self.linker.write_text("#!/bin/bash\ncp \"$1\" \"$2\"\n")
        self.linker.chmod(0o755)
        self.object = self.root / "object.bin"
        self.object.write_bytes(bytes.fromhex("01020304"))
        import os
        self.old_env = os.environ.get("FAKE_OBJECT")
        os.environ["FAKE_OBJECT"] = str(self.object)

    def tearDown(self):
        import os
        if self.old_env is None:
            os.environ.pop("FAKE_OBJECT", None)
        else:
            os.environ["FAKE_OBJECT"] = self.old_env
        self.temp.cleanup()

    def manifest(self, candidate="gcc-test"):
        path = self.root / "manifest.json"
        path.write_text(json.dumps({
            "source": str(self.source), "symbol": "probe",
            "reference": str(self.reference),
            "candidates": [{"id": candidate, "compile": [str(self.compiler)],
                            "objcopy": [str(self.objcopy)]}]}))
        return path

    def test_a_candidate_whose_compiled_function_matches_is_selected(self):
        result = run_probe(self.manifest(), self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("pass", "gcc-test"))
        self.assertEqual(result["candidates"][0]["actual_sha256"], result["reference"]["sha256"])
        self.assertEqual(Path(result["manifest"]["path"]), self.manifest().resolve())

    def test_a_caller_manifest_cannot_assign_game_owned_credit(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["evidence"] = {"reference_range": {"section": ".text",
                                                "vaddr": "001d1800",
                                                "file_offset": "00000000"}}
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["candidates"][0]["gate"]["scope"], "mixed")
        self.assertEqual(result["candidates"][0]["gate"]["matched_bytes"], 4)

    def test_a_nonmatching_candidate_is_a_failure_not_silently_skipped(self):
        self.object.write_bytes(bytes.fromhex("01020305"))
        result = run_probe(self.manifest(), self.root / "out")
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["failures"], ["gcc-test"])
        self.assertEqual(result["candidates"][0]["gate"]["first_difference"]["offset"], 0)

    def test_unavailable_candidate_is_incomplete_and_cannot_be_selected(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["compile"] = [str(self.root / "missing-ee-gcc")]
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["incomplete"], ["gcc-test"])

    def test_multiple_matching_candidates_remain_ambiguous(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"].append({"id": "other-gcc", "compile": [str(self.compiler)],
                                    "objcopy": [str(self.objcopy)]})
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["matches"], ["gcc-test", "other-gcc"])

    def test_a_byte_match_plus_a_compile_error_cannot_select_a_candidate(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"].append({"id": "broken-gcc", "compile": ["/usr/bin/false"],
                                    "objcopy": [str(self.objcopy)]})
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["errors"], ["broken-gcc"])

    def test_multiple_matches_plus_a_nonmatching_candidate_stays_ambiguous(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"].extend([
            {"id": "other-gcc", "compile": [str(self.compiler)], "objcopy": [str(self.objcopy)]},
            {"id": "nonmatching-gcc", "compile": [str(self.root / "mismatch-cc")],
             "objcopy": [str(self.objcopy)]},
        ])
        mismatch_compiler = self.root / "mismatch-cc"
        mismatch_compiler.write_text("#!/bin/bash\ncp \"$MISMATCH_OBJECT\" \"${@: -1}\"\n")
        mismatch_compiler.chmod(0o755)
        import os
        old = os.environ.get("MISMATCH_OBJECT")
        os.environ["MISMATCH_OBJECT"] = str(self.root / "mismatch.bin")
        (self.root / "mismatch.bin").write_bytes(bytes.fromhex("05060708"))
        try:
            manifest.write_text(json.dumps(body))
            result = run_probe(manifest, self.root / "out")
        finally:
            if old is None:
                os.environ.pop("MISMATCH_OBJECT", None)
            else:
                os.environ["MISMATCH_OBJECT"] = old
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["matches"], ["gcc-test", "other-gcc"])
        self.assertEqual(result["failures"], ["nonmatching-gcc"])

    def test_compiler_timeout_is_an_operational_error_and_blocks_selection(self):
        manifest = self.manifest()
        with patch("compiler_probe.subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("fake", 120)):
            result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["errors"], ["gcc-test"])

    def test_compiler_oserror_is_an_operational_error_and_blocks_selection(self):
        manifest = self.manifest()
        with patch("compiler_probe.subprocess.run", side_effect=OSError("launcher unavailable")):
            result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["errors"], ["gcc-test"])
        self.assertIn("launcher unavailable", result["candidates"][0]["reason"])

    def test_launcher_can_be_pinned_separately_from_container_compiler_binary(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["compiler_executable"] = str(self.compiler)
        body["candidates"][0]["objcopy_executable"] = str(self.objcopy)
        body["candidates"][0]["runtime"] = {"image": "test-image@sha256:abc"}
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        candidate = result["candidates"][0]
        self.assertEqual(result["status"], "pass")
        expected_hash = hashlib.sha256(self.compiler.read_bytes()).hexdigest()
        self.assertEqual(candidate["compiler_sha256"], expected_hash)
        self.assertEqual(candidate["runtime"], {"image": "test-image@sha256:abc"})

    def test_candidate_supporting_tools_are_hash_pinned(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["tool_files"] = {"cc1": str(self.compiler)}
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["candidates"][0]["tool_files"]["cc1"]["sha256"],
                         hashlib.sha256(self.compiler.read_bytes()).hexdigest())

    def test_candidate_can_link_before_the_byte_gate(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["link"] = [str(self.linker), "{object}", "{linked_object}"]
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        candidate = result["candidates"][0]
        self.assertEqual(result["status"], "pass")
        self.assertEqual(candidate["link_returncode"], 0)

    def test_link_error_blocks_selection_and_is_not_a_byte_mismatch(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["link"] = ["/usr/bin/false", "{object}", "{linked_object}"]
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["errors"], ["gcc-test"])

    def test_missing_manifest_has_an_incomplete_receipt_not_a_traceback(self):
        import contextlib
        import io
        import sys
        output = io.StringIO()
        with patch.object(sys, "argv", ["compiler_probe.py", str(self.root / "missing.json"),
                                         "--output", str(self.root / "evidence")]):
            with contextlib.redirect_stdout(output):
                code = compiler_probe.main()
        self.assertEqual(code, 2)
        receipt = next((self.root / "evidence").glob("*/result.json"))
        saved = json.loads(receipt.read_text())
        self.assertEqual(saved["status"], "incomplete")
        self.assertTrue(next(receipt.parent.glob("report.md")).is_file())


if __name__ == "__main__":
    unittest.main()
