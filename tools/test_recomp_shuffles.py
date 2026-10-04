"""Guard and synthetic-regression checks for pinned packed-register fixes."""
from pathlib import Path
import tempfile
import unittest

from tools.recomp import verify_shuffles as verifier

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".scratch/mesh/codex-root/PS2Recomp"


class ShuffleSourceGuardTest(unittest.TestCase):
    def test_rejects_wrong_source_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            header = base / "upstream" / verifier.HEADER_PATH
            header.parent.mkdir(parents=True)
            header.write_text("// Wrong source is never compiled.\n")
            output = base / "output"
            with self.assertRaisesRegex(ValueError, "pinned source SHA-256 mismatch"):
                verifier.verify(base / "upstream", output)
            self.assertFalse(output.exists())

    def test_changed_or_missing_sse2neon_header_is_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            output = base / "output"
            (base / "dep").mkdir()
            with self.assertRaisesRegex(ValueError, "pinned sse2neon dependency SHA-256 mismatch"):
                verifier.verify(base / "upstream", output, sse2neon=base / "dep")
            (base / "dep" / "sse2neon.h").write_text("// mutation")
            with self.assertRaisesRegex(ValueError, "pinned sse2neon dependency SHA-256 mismatch"):
                verifier.verify(base / "upstream", output, sse2neon=base / "dep")
            self.assertFalse(output.exists())


@unittest.skipUnless((UPSTREAM / verifier.MMI_PATH).is_file(),
                     "private pinned tool checkout is unavailable")
class ShufflePinnedSourceTest(unittest.TestCase):
    def test_pinned_patch_constructs_exact_candidate_sources(self):
        candidate = verifier.corrected_sources(verifier.pinned_sources(UPSTREAM))
        for name, expected in verifier.CANDIDATE_HASHES.items():
            self.assertEqual(verifier.digest(candidate[name].encode()), expected)

    def test_rejects_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "output directory must be fresh"):
                verifier.verify(UPSTREAM, Path(temporary))

    def test_missing_or_changed_translation_template_is_rejected(self):
        sources = verifier.pinned_sources(UPSTREAM)
        changed = {**sources, verifier.MMI_PATH: sources[verifier.MMI_PATH].replace(
            "CodeGenerator::translatePEXEW", "CodeGenerator::changedPEXEW")}
        with self.assertRaisesRegex(ValueError, "production translation template is absent: PEXEW"):
            verifier.extracted_header(changed)


if __name__ == "__main__":
    unittest.main()
