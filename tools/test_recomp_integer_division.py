"""Division source guards and native matrix checks, using synthetic inputs."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from tools.recomp import verify_integer_division as verifier

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".scratch/mesh/codex-root/PS2Recomp"
DEPENDENCY = ROOT / ".scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src"


class DivisionGuards(unittest.TestCase):
    def test_changed_source_fails_before_compilation_or_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in verifier.SOURCE_HASHES:
                source = root / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("// deliberately changed source")
            output = root / "out"
            with patch.object(verifier.subprocess, "run", return_value=SimpleNamespace(stdout=verifier.COMMIT)):
                with self.assertRaisesRegex(ValueError, "source SHA-256 differs"):
                    verifier.verify(root, output, root)
            self.assertFalse(output.exists())

    def test_wrong_commit_fails_before_source_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(verifier.subprocess, "run", return_value=SimpleNamespace(stdout="wrong")):
                with self.assertRaisesRegex(ValueError, "commit differs"):
                    verifier.pinned_sources(root)

    def test_missing_case_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "division case absent"):
            verifier.extract_case("", "SPECIAL_DIV", ["rt", "rs"])

    def test_existing_output_survives_before_source_is_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            keep = root / "keep"
            keep.write_text("preserve")
            with self.assertRaisesRegex(ValueError, "must be fresh"):
                verifier.verify(root / "missing", root, root / "missing")
            self.assertEqual(keep.read_text(), "preserve")

    def test_missing_checkout_never_creates_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "out"
            with self.assertRaisesRegex(ValueError, "checkout is unavailable"):
                verifier.verify(root / "missing", output, root)
            self.assertFalse(output.exists())


@unittest.skipUnless((UPSTREAM / verifier.SPECIAL).is_file()
                     and (DEPENDENCY / "sse2neon.h").is_file(),
                     "private pinned source/dependency is unavailable")
class DivisionPinnedTest(unittest.TestCase):
    def test_extraction_uses_actual_register_reads_and_both_banks(self):
        header, templates = verifier.extracted_header(verifier.pinned_sources(UPSTREAM))
        self.assertEqual(tuple(templates), verifier.OPERATIONS)
        self.assertIn("#define GPR_S32", header)
        self.assertIn("Ps2ExtractEpi32", header)
        self.assertIn("ctx->lo1", templates["DIV1"])
        self.assertIn("divisor == -1 && dividend == INT32_MIN", templates["DIV"])

    def test_dependency_drift_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sse2neon.h").write_text("mutation")
            output = root / "out"
            with self.assertRaisesRegex(ValueError, "dependency"):
                verifier.verify(UPSTREAM, output, root)
            self.assertFalse(output.exists())

    def test_synthetic_matrix_and_corrupted_quotients(self):
        with tempfile.TemporaryDirectory() as td:
            result = verifier.verify(UPSTREAM, Path(td) / "out", DEPENDENCY)
            self.assertEqual(result["details"]["mismatches"], [0] * 4)
            self.assertEqual(result["negative_control"]["mismatches"], [600600] * 4)


if __name__ == "__main__":
    unittest.main()
