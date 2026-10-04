from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "recomp" / "verify_translator_semantics.py"
spec = importlib.util.spec_from_file_location("verify_translator_semantics", SCRIPT)
assert spec and spec.loader
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class TranslatorSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("PS2RECOMP_SOURCE_ROOT")
        if not configured:
            raise unittest.SkipTest("set PS2RECOMP_SOURCE_ROOT to the pinned checkout for source-dependent tests")
        cls.source_root = Path(configured).resolve()
        if not cls.source_root.is_dir():
            raise unittest.SkipTest("PS2RECOMP_SOURCE_ROOT does not exist")

    def test_pinned_checkout_commit_and_input_hashes(self) -> None:
        verify.verify_commit(self.source_root)
        verify.verify_source_file_hashes(self.source_root)

    def test_pinned_caller_exception_propagation_sources(self) -> None:
        verify.verify_exception_propagation_sources(self.source_root)

    def test_wrong_input_sha_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="translator-sha-negative-") as directory:
            root = Path(directory)
            for relative in verify.SOURCE_HASHES:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((self.source_root / relative).read_bytes())
            verify.verify_source_file_hashes(root)
            target = root / next(iter(verify.SOURCE_HASHES))
            target.write_bytes(target.read_bytes() + b"\n// deliberately changed for SHA negative control\n")
            with self.assertRaisesRegex(ValueError, "wrong input SHA-256"):
                verify.verify_source_file_hashes(root)

    def test_patch_stages_only_and_reproduces_candidate_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="translator-patch-stage-") as directory:
            stage = verify.stage_and_patch(self.source_root, Path(directory))
            self.assertEqual(
                {str(path.relative_to(stage)) for path in stage.rglob("*") if path.is_file()},
                set(verify.SOURCE_HASHES),
            )
            for relative, expected in verify.CANDIDATE_HASHES.items():
                self.assertEqual(verify.sha256(stage / relative), expected)
            generated = verify.generated_harness(stage)
            control_blocks = generated.count("{Context c{};")
            self.assertEqual(control_blocks, 10)
            self.assertIn(f"{control_blocks} normal/overflow/delay-slot/caller controls", generated)

    def test_template_formatter_fails_unexpected_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "unexpected fmt field"):
            verify.format_template("value={:x}", [1])
        with self.assertRaisesRegex(ValueError, "not enough values"):
            verify.format_template("{} {}", [1])

    def test_cli_requires_explicit_source_root(self) -> None:
        result = subprocess.run([str(SCRIPT)], check=False, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--source-root", result.stderr)

    def test_compiler_failure_has_structured_diagnostic(self) -> None:
        error = subprocess.CalledProcessError(1, ["clang++"], output="compiler stdout", stderr="compiler stderr")
        captured = io.StringIO()
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--source-root", "/explicit/source"]), \
             mock.patch.object(verify, "run_verification", side_effect=error), \
             contextlib.redirect_stderr(captured):
            result = verify.main()
        self.assertEqual(result, 1)
        payload = json.loads(captured.getvalue())
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["returncode"], 1)
        self.assertEqual(payload["stdout"], "compiler stdout")
        self.assertEqual(payload["stderr"], "compiler stderr")


if __name__ == "__main__":
    unittest.main()
