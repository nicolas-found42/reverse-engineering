"""Focused source-guard tests for the packed MMI verifier."""
from pathlib import Path
import tempfile
import unittest

from tools.recomp import verify_mmi_packed as verifier

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".scratch/mesh/codex-root/PS2Recomp"
SSE2NEON = ROOT / ".scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src"


class PackedMmiPureGuardTest(unittest.TestCase):
    def test_rejects_changed_source_bytes_before_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative in verifier.SOURCE_HASHES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("// deliberately unpinned fixture\n")
            output = root / "must-not-exist"
            with self.assertRaisesRegex(ValueError, "upstream is not a readable Git checkout"):
                verifier.verify(root, output, root)
            self.assertFalse(output.exists())

    def test_rejects_missing_template_in_mutated_source(self):
        sources = {verifier.HEADER_PATH: "", verifier.MMI_PATH: ""}
        with self.assertRaisesRegex(ValueError, "production translation method is absent: PCPYLD"):
            verifier.extracted_header(sources)

    def test_operation_inventory_is_explicit(self):
        self.assertEqual(len(verifier.OPERATIONS), 13)
        self.assertEqual(len(set(verifier.OPERATIONS)), 13)


@unittest.skipUnless((UPSTREAM / verifier.MMI_PATH).is_file() and
                     (SSE2NEON / "sse2neon.h").is_file(),
                     "private pinned upstream/dependency checkout is unavailable")
class PackedMmiPinnedProbeTest(unittest.TestCase):
    def test_templates_extract_and_match_source_inventory(self):
        sources = verifier.pinned_sources(UPSTREAM)
        header, templates = verifier.extracted_header(sources)
        self.assertEqual(tuple(templates), verifier.OPERATIONS)
        self.assertIn("#define GPR_VEC(", header)
        self.assertIn("#define SET_GPR_VEC(", header)
        self.assertIn("generated_PCPYH", header)

    def test_existing_output_is_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "existing"
            output.mkdir()
            marker = output / "keep"
            marker.write_text("preserve")
            with self.assertRaisesRegex(ValueError, "fresh output directory already exists"):
                verifier.verify(UPSTREAM, output, SSE2NEON)
            self.assertEqual(marker.read_text(), "preserve")

    def test_changed_dependency_is_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            (fake / "sse2neon.h").write_text("// mutation")
            output = fake / "out"
            with self.assertRaisesRegex(ValueError, "pinned sse2neon dependency SHA-256 mismatch"):
                verifier.verify(UPSTREAM, output, fake)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
