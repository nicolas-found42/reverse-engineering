"""Source guards and bounded native checks for pinned EE multiply emitters."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from tools.recomp import verify_integer_multiply as verifier

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".scratch/mesh/codex-root/PS2Recomp"
DEPENDENCY = ROOT / ".scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src"
INVENTORY = ROOT / ".scratch/evidence/static-export.json"


class MultiplyGuards(unittest.TestCase):
    def test_nonzero_native_status_is_rejected_even_with_valid_json_output(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = Path(td) / "run.json"
            failed = subprocess.CompletedProcess(["synthetic-probe"], 7, '{}', '')
            with patch.object(verifier.subprocess, "run", return_value=failed):
                with self.assertRaisesRegex(ValueError, "exit status"):
                    verifier._run_probe(["synthetic-probe"], receipt)
            self.assertTrue(receipt.is_file())

    def test_changed_source_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in verifier.SOURCE_HASHES:
                source = root / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("// changed source\n")
            output = root / "out"
            fake = SimpleNamespace(stdout=verifier.COMMIT)
            with patch.object(verifier.subprocess, "run", return_value=fake):
                with self.assertRaisesRegex(ValueError, "source SHA-256 differs"):
                    verifier.verify(root, root / "inventory.json", output, root)
            self.assertFalse(output.exists())

    def test_wrong_commit_fails_before_source_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = SimpleNamespace(stdout="different-commit")
            with patch.object(verifier.subprocess, "run", return_value=fake):
                with self.assertRaisesRegex(ValueError, "commit differs"):
                    verifier.pinned_sources(root)

    def test_existing_output_is_preserved_before_source_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "out"
            output.mkdir()
            keep = output / "keep.txt"
            keep.write_text("preserve")
            with self.assertRaisesRegex(ValueError, "must be fresh"):
                verifier.verify(root / "missing", root / "inventory", output, root)
            self.assertEqual(keep.read_text(), "preserve")

    def test_missing_case_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "multiply translator case absent"):
            verifier.extract_returns("", "SPECIAL_MULT", ["rs", "rt", "rd"])

    def test_inventory_summary_pins_order_and_cardinality(self):
        first = {"MULT": ["0010", "0020", "0030"]}
        self.assertEqual(verifier.inventory_summary(first)["MULT"]["count"], 3)
        self.assertNotEqual(
            verifier.inventory_summary(first)["MULT"]["ordered_addresses_sha256"],
            verifier.inventory_summary({"MULT": ["0030", "0020", "0010"]})
            ["MULT"]["ordered_addresses_sha256"],
        )

    def test_pinned_inventory_rejects_mutated_export(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "export.json"
            path.write_text("{}")
            with self.assertRaisesRegex(ValueError, "static export SHA-256 differs"):
                verifier.pinned_inventory(path)


@unittest.skipUnless((UPSTREAM / verifier.SPECIAL).is_file()
                     and (DEPENDENCY / "sse2neon.h").is_file()
                     and INVENTORY.is_file(),
                     "private pinned source/dependency/inventory is unavailable")
class MultiplyPinnedTest(unittest.TestCase):
    def test_actual_emitters_cover_signed_unsigned_both_banks_and_rd_zero(self):
        header, templates, wrappers = verifier.extracted_header(verifier.pinned_sources(UPSTREAM))
        self.assertEqual(tuple(templates), verifier.OPERATION_NAMES)
        self.assertEqual(tuple(wrappers), verifier.OPERATION_NAMES)
        self.assertIn("GPR_S32", header)
        self.assertIn("GPR_U32", header)
        self.assertIn("Ps2HiLoToU64(ctx->hi, ctx->lo)", templates["MADD_RD"])
        self.assertIn("ctx->lo1", templates["MULT1_RD"])
        self.assertNotIn("SET_GPR_S32", templates["MULT_R0"])
        self.assertNotIn("SET_GPR_S32", templates["MULT1_R0"])
        self.assertNotIn("SET_GPR_S32", templates["MADD_R0"])

    def test_each_extracted_branch_has_the_expected_arithmetic_and_result_bank(self):
        _, templates, _ = verifier.extracted_header(verifier.pinned_sources(UPSTREAM))
        for name in ("MULT_RD", "MULT_R0", "MULT1_RD", "MULT1_R0", "MADD_RD", "MADD_R0"):
            self.assertIn("GPR_S32(ctx, rs)", templates[name], name)
            self.assertIn("GPR_S32(ctx, rt)", templates[name], name)
        for name in ("MULTU_RD", "MULTU_R0"):
            self.assertIn("GPR_U32(ctx, rs)", templates[name], name)
            self.assertIn("GPR_U32(ctx, rt)", templates[name], name)
        for name in ("MULT_RD", "MULT_R0", "MULTU_RD", "MULTU_R0"):
            self.assertIn("ctx->lo =", templates[name], name)
            self.assertIn("ctx->hi =", templates[name], name)
            self.assertNotIn("ctx->lo1", templates[name], name)
        for name in ("MULT1_RD", "MULT1_R0"):
            self.assertIn("ctx->lo1 =", templates[name], name)
            self.assertIn("ctx->hi1 =", templates[name], name)
        for name in ("MADD_RD", "MADD_R0"):
            self.assertIn("Ps2HiLoToU64(ctx->hi, ctx->lo)", templates[name], name)
            self.assertIn("ctx->lo = Ps2SignExt32ToU64", templates[name], name)
            self.assertIn("ctx->hi = Ps2SignExt32ToU64", templates[name], name)

    def test_dependency_drift_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sse2neon.h").write_text("changed\n")
            output = root / "out"
            with self.assertRaisesRegex(ValueError, "sse2neon SHA-256 differs"):
                verifier.verify(UPSTREAM, INVENTORY, output, root)
            self.assertFalse(output.exists())

    def test_actual_template_probe_and_corrupted_output_bit_mutant(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "out"
            result = verifier.verify(UPSTREAM, INVENTORY, output, DEPENDENCY)
            expected = [201440] * len(verifier.OPERATION_NAMES)
            self.assertEqual(result["details"]["checks"], expected)
            self.assertEqual(result["details"]["mismatches"], [0] * len(expected))
            self.assertEqual(result["mutant"]["checks"], expected)
            self.assertEqual(result["mutant"]["mismatches"], expected)
            self.assertEqual(result["manual"]["pdf_sha256"], verifier.MANUAL_PDF_HASH)
            self.assertEqual(result["static_export"]["counts"], verifier.INVENTORY_COUNTS)
            self.assertNotIn("instruction_addresses", result["static_export"])


if __name__ == "__main__":
    unittest.main()
