"""Source-guarded tests for the isolated, manual-derived FPU experiment."""
import importlib.util
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "tools/recomp/experimental"
SPEC = importlib.util.spec_from_file_location("verify_ee_fpu_experiment", EXPERIMENT / "verify_ee_fpu_experiment.py")
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
SOURCE_TREE = ROOT / ".scratch/mesh/codex-root/PS2Recomp"


class ExperimentalEeFpuTests(unittest.TestCase):
    def setUp(self):
        self.manifest = VERIFY.load_manifest()

    def test_wrong_checkout_and_source_drift_are_rejected(self):
        with self.assertRaisesRegex(VERIFY.VerificationError, "source commit mismatch"):
            VERIFY.extract_baseline(ROOT, 5.0)
        if not SOURCE_TREE.exists():
            self.skipTest("private pinned PS2Recomp checkout is not available")
        with tempfile.TemporaryDirectory(prefix="ee-fpu-mutated-source-") as td:
            mutated=Path(td)
            for rel in VERIFY.EXPECTED_SOURCES:
                dst=mutated/rel
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(SOURCE_TREE/rel,dst)
            drifted=mutated/"ps2xRuntime/include/ps2_runtime_macros.h"
            drifted.write_text(drifted.read_text()+"\n// deliberate drift\n")
            (mutated/".git").mkdir()
            fake_git=subprocess.CompletedProcess(["git"],0,VERIFY.EXPECTED_COMMIT+"\n","")
            with mock.patch.object(VERIFY,"run",return_value=fake_git):
                with self.assertRaisesRegex(VERIFY.VerificationError,"source hash mismatch"):
                    VERIFY.extract_baseline(mutated,5.0)

    def test_exact_baseline_and_candidate_templates_and_patch_hashes(self):
        if not SOURCE_TREE.exists():
            self.skipTest("private pinned PS2Recomp checkout is not available")
        baseline=VERIFY.extract_baseline(SOURCE_TREE,10.0)
        self.assertEqual(set(baseline["exact_baseline_templates"]),set(VERIFY.EXPECTED_BASELINE))
        validated=VERIFY.validate_patch(SOURCE_TREE,10.0,self.manifest)
        candidate=validated["patch"]["exact_experimental_templates"]
        self.assertEqual(set(candidate),set(VERIFY.EXPECTED_CANDIDATE))
        self.assertEqual(validated["patch"]["patched_file_sha256"],self.manifest["patch"]["applied_file_sha256"])
        self.assertEqual(validated["patch"]["patch_sha256"],self.manifest["patch"]["sha256"])

    @unittest.skipUnless(shutil.which("clang++"),"clang++ with UBSan is unavailable")
    def test_actual_template_probe_uses_baseline_and_patched_helper(self):
        if not SOURCE_TREE.exists():
            self.skipTest("private pinned PS2Recomp checkout is not available")
        validated=VERIFY.validate_patch(SOURCE_TREE,15.0,self.manifest)
        probe=VERIFY.compile_actual_template_probe(SOURCE_TREE,validated["source"],validated["patch"],"clang++",15.0,self.manifest)
        self.assertEqual(probe["compile_exit"],0)
        self.assertEqual(probe["run_exit"],0)
        self.assertEqual(probe["compiled_candidate_helper_sha256"],self.manifest["patch"]["applied_file_sha256"]["ps2xRuntime/include/ee_fpu_experimental_helpers.h"])
        self.assertIn("PASS: exact pristine/patched emitter templates",probe["stdout"])
        self.assertEqual(len(probe["baseline_templates_compiled"]),6)
        self.assertEqual(len(probe["candidate_templates_compiled"]),6)

    def test_patch_guard_rejects_modified_patch(self):
        if not SOURCE_TREE.exists():
            self.skipTest("private pinned PS2Recomp checkout is not available")
        original=VERIFY.PATCH
        with tempfile.TemporaryDirectory(prefix="ee-fpu-mutated-patch-") as td:
            altered=Path(td)/"altered.patch"
            altered.write_text(original.read_text()+"\n# drift\n")
            with mock.patch.object(VERIFY,"PATCH",altered):
                with self.assertRaisesRegex(VERIFY.VerificationError,"patch changed paths|patch hash mismatch"):
                    VERIFY.apply_patch_in_temp(SOURCE_TREE,10.0,self.manifest)

    def test_manifest_cannot_widen_changed_path_allowlist(self):
        altered=copy.deepcopy(self.manifest)
        altered["patch"]["changed_paths"].append("unreviewed/file.cpp")
        with self.assertRaisesRegex(VERIFY.VerificationError,"changed paths differ from verifier allowlist"):
            VERIFY.validate_patch(ROOT,5.0,altered)

    def test_compiler_version_guard_runs_before_template_compilation(self):
        stub={"source":{},"patch":{}}
        fake_version=subprocess.CompletedProcess(["clang++","--version"],0,"different compiler build\n","")
        with mock.patch.object(VERIFY,"validate_patch",return_value=stub), \
             mock.patch.object(VERIFY,"run",return_value=fake_version), \
             mock.patch.object(VERIFY,"compile_actual_template_probe") as compile_probe:
            with self.assertRaisesRegex(VERIFY.VerificationError,"compiler version mismatch"):
                VERIFY.build_result(SOURCE_TREE,"clang++",5.0)
            compile_probe.assert_not_called()

    def test_atomic_fresh_output_and_cli_refusal(self):
        with tempfile.TemporaryDirectory(prefix="ee-fpu-output-") as td:
            output=Path(td)/"result.json"
            command=["python3",str(EXPERIMENT/"verify_ee_fpu_experiment.py"),"--source-tree",str(SOURCE_TREE),"--timeout","15","--output",str(output)]
            first=subprocess.run(command,text=True,capture_output=True,timeout=20)
            self.assertEqual(first.returncode,0,first.stderr)
            self.assertEqual(json.loads(output.read_text())["status"],"pass")
            second=subprocess.run(command,text=True,capture_output=True,timeout=20)
            self.assertEqual(second.returncode,2)
            diagnostic=json.loads(second.stderr)
            self.assertEqual(diagnostic["status"],"error")
            self.assertEqual(diagnostic["error"]["stage"],"output")
            self.assertIn("refusing to overwrite",diagnostic["error"]["message"])
            self.assertEqual(json.loads(output.read_text())["status"],"pass")
            with self.assertRaisesRegex(VERIFY.VerificationError,"refusing to overwrite"):
                VERIFY.atomic_write_fresh(output,'{"status":"second"}\n')

    def test_timeout_has_structured_stage(self):
        with self.assertRaises(VERIFY.VerificationError) as caught:
            VERIFY.run(["python3","-c","import time; time.sleep(1)"],stage="probe_run",timeout=0.01)
        self.assertEqual(caught.exception.stage,"probe_run")
        self.assertIn("timed out",str(caught.exception))


if __name__ == "__main__":
    unittest.main()
