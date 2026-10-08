"""Public controls for source inventory without historical package permission."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile

from compiler_provenance import inspect_source
from compiler_provenance_iop import validate_comparison
from evidence_common import Invalid


class CompilerProvenanceTests(unittest.TestCase):
    def source(self, root, version, *, notice=True):
        archive = root / "source.zip"
        files = {"gcc/version.c": version}
        if notice:
            files["gcc/COPYING"] = b"Public synthetic notice fixture.\n"
        with zipfile.ZipFile(archive, "w") as package:
            for name, data in files.items():
                package.writestr("fixture/" + name, data)
        decision = {
            "archive": {"bytes": archive.stat().st_size,
                        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
            "root": "fixture/",
            "members": {name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                        for name, data in files.items()},
            "version_member": "gcc/version.c",
            "notice_members": ["gcc/COPYING"],
        }
        return archive, decision

    def test_matching_source_inventory_does_not_bind_historical_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.zip"
            version = b'char *version_string = "2.96-ee-001003-1";\n'
            notice = b"Public synthetic notice fixture, not an applicable license.\n"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr("fixture/gcc/version.c", version)
                package.writestr("fixture/gcc/COPYING", notice)
            decision = {
                "archive": {"bytes": archive.stat().st_size,
                            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
                "root": "fixture/",
                "members": {name: {"bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest()}
                            for name, data in [("gcc/version.c", version), ("gcc/COPYING", notice)]},
                "version_member": "gcc/version.c",
                "notice_members": ["gcc/COPYING"],
            }
            result = inspect_source(archive, decision)
            self.assertEqual(result["inventory_status"], "pass")
            self.assertEqual(result["version_relation"], "equal")
            self.assertEqual(result["historical_binding_status"], "incomplete")
            self.assertEqual(result["redistribution_disposition"], "unresolved")

    def test_wrong_version_stays_incomplete_even_when_notice_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, decision = self.source(Path(directory), b'char *version_string = "2.9-ee-991111";\n', notice=False)
            # The required member stays required when it is absent in the input.
            decision["members"]["gcc/COPYING"] = {"bytes": 31, "sha256": "0" * 64}
            result = inspect_source(archive, decision)
            self.assertEqual(result["version_relation"], "mismatch")
            self.assertEqual(result["missing"], ["gcc/COPYING"])
            self.assertEqual(result["inventory_status"], "incomplete")
            self.assertIn("Source version differs from the selected historical package.", result["binding_reasons"])

    def test_changed_source_and_malformed_version_cannot_match(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, decision = self.source(Path(directory), b'/* char *version_string = "2.96-ee-001003-1"; */\n')
            decision["members"]["gcc/version.c"]["sha256"] = "0" * 64
            result = inspect_source(archive, decision)
            self.assertEqual(result["version_relation"], "unresolved")
            self.assertEqual(result["changed"], ["gcc/version.c"])
            self.assertEqual(result["historical_binding_status"], "incomplete")

    def test_missing_archive_is_explicit_and_grants_no_permission(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, decision = self.source(Path(directory), b'char *version_string = "2.96-ee-001003-1";\n')
            archive.unlink()
            result = inspect_source(archive, decision)
            self.assertEqual(result["missing"], ["source archive"])
            self.assertEqual(result["inventory_status"], "incomplete")
            self.assertEqual(result["redistribution_disposition"], "unresolved")

    def test_version_compatible_repacked_archive_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, decision = self.source(Path(directory), b'char *version_string = "2.96-ee-001003-1";\n')
            with zipfile.ZipFile(archive, "a") as package:
                package.writestr("fixture/unrecorded-source.c", b"int changed_source;\n")
            result = inspect_source(archive, decision)
            self.assertEqual(result["version_relation"], "equal")
            self.assertEqual(result["changed"], ["source archive"])
            self.assertEqual(result["inventory_status"], "incomplete")

    def test_cli_changed_selected_package_fails_despite_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ee-gcc2.96.tar.xz").write_bytes(b"public negative fixture: changed selected package")
            command = [sys.executable, str(Path(__file__).with_name("compiler_provenance.py")),
                       str(root), str(root / "missing-source.zip"), "--output", str(root / "receipts")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 1, process.stderr + process.stdout)
            result = json.loads(Path(json.loads(process.stdout)["result"]).read_text())
            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["details"]["selected_package"]["identity_status"], "fail")
            self.assertEqual(result["details"]["missing"], ["source archive"])
            self.assertIn("selected compiler archive differs", result["diagnostics"][0])

    def test_cli_missing_package_and_source_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = [sys.executable, str(Path(__file__).with_name("compiler_provenance.py")),
                       str(root), str(root / "missing-source.zip"), "--output", str(root / "receipts")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 2, process.stderr + process.stdout)
            result = json.loads(Path(json.loads(process.stdout)["result"]).read_text())
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["details"]["selected_package"]["identity_status"], "incomplete")
            self.assertEqual(result["details"]["missing"], ["source archive"])

    def test_cli_changed_fixed_source_fails_despite_missing_selected_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "changed-source.zip"
            with zipfile.ZipFile(archive, "w") as source:
                source.writestr("fixture/changed.c", b"public negative fixture: altered fixed source candidate")
            command = [sys.executable, str(Path(__file__).with_name("compiler_provenance.py")),
                       str(root), str(archive), "--output", str(root / "receipts")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 1, process.stderr + process.stdout)
            result = json.loads(Path(json.loads(process.stdout)["result"]).read_text())
            self.assertEqual(result["status"], "fail")
            self.assertIn("source archive", result["details"]["changed"])
            self.assertEqual(result["details"]["selected_package"]["identity_status"], "incomplete")
            self.assertIsNone(result["details"]["selected_package"]["observed"])
            self.assertIn("fixed source candidate", result["diagnostics"][0])

    def test_iop_cli_changed_source_snapshot_fails_before_missing_downloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "changed-source.zip"
            with zipfile.ZipFile(archive, "w") as source:
                source.writestr("fixture/changed.c", b"public negative fixture")
            command = [sys.executable, str(Path(__file__).with_name("compiler_provenance_iop.py")),
                       str(archive), str(root), "--output", str(root / "receipts")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 1, process.stderr + process.stdout)
            result = json.loads(Path(json.loads(process.stdout)["result"]).read_text())
            self.assertEqual(result["status"], "fail")
            self.assertIn("source candidate archive differs", result["diagnostics"][0])

    def test_iop_cli_missing_source_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = [sys.executable, str(Path(__file__).with_name("compiler_provenance_iop.py")),
                       str(root / "missing-source.zip"), str(root), "--output", str(root / "receipts")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 2, process.stderr + process.stdout)
            result = json.loads(Path(json.loads(process.stdout)["result"]).read_text())
            self.assertEqual(result["status"], "incomplete")

    def test_iop_recorded_tree_differences_pass_and_extra_difference_fails(self):
        receipt = Path(__file__).resolve().parents[1] / "notes/evidence/fr2-compiler-provenance-continuation/iop-source-reconciliation/result.json"
        results = json.loads(receipt.read_text())["details"]
        validate_comparison(results)
        results["comparison"]["binutils-2.9.1"]["missing"].append("gas/config/tc-mips.c")
        with self.assertRaisesRegex(Invalid, "derived source tree differs"):
            validate_comparison(results)


if __name__ == "__main__":
    unittest.main()
