"""Public CLI tests for fixed, corpus-pinned asset consumer evidence."""

import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
CLI = TOOLS / "verify_asset_contracts.py"
MANIFEST = REPO / "notes/asset-consumer-contracts.json"


def archive(files):
    """Build a one-directory archive with chunk-aligned file records."""
    header = bytearray(struct.pack("<I", 1) + struct.pack("<II", len(files), 0) + struct.pack("<I", len(files)))
    records, data = bytearray(), bytearray()
    for name, payload, compressed in files:
        while len(data) % 2048:
            data.append(0)
        stored = struct.pack("<I", len(payload)) + zlib.compress(payload) if compressed else payload
        offset = len(data)
        data += stored
        records += name.encode().ljust(16, b"\0") + struct.pack("<III", 0xFFFFFFFF, offset // 2048, len(stored))
    return bytes(header + records), bytes(data)


class AssetContractCli(unittest.TestCase):
    def test_caller_cannot_change_structure_evidence_or_limits(self):
        for field in ("structure_evidence", "limits"):
            with self.subTest(field=field):
                manifest = json.loads(MANIFEST.read_text())
                self.update_contract(manifest, "configuration-cfg", **{field: ["invented claim"]})
                code, result = self.run_cli(manifest, output=self.root / field)
                self.assertEqual((code, result["status"]), (1, "fail"))
                self.assertIn(field + " differs from the fixed registry", " ".join(result["diagnostics"]))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, manifest=None, files=None, cli=CLI, output=None):
        hdr, dat = archive(files or [("UI.PTG;1", b"tile", False), ("MODEL.PS2;1", b"model", True)])
        hp, dp = self.root / "FILES.HDR", self.root / "FILES.DAT"
        hp.write_bytes(hdr)
        dp.write_bytes(dat)
        cp = self.root / "contracts.json"
        cp.write_text(json.dumps(manifest or json.loads(MANIFEST.read_text())))
        out = output or self.root / "out"
        proc = subprocess.run([sys.executable, str(cli), "archive", str(hp), str(dp), "--contracts", str(cp), "--output", str(out)], capture_output=True, text=True)
        reports = list(out.glob("*/result.json"))
        self.assertTrue(reports, proc.stderr)
        return proc.returncode, json.loads(reports[-1].read_text())

    @staticmethod
    def update_contract(manifest, contract_id, **changes):
        contract = next(row for row in manifest["contracts"] if row["id"] == contract_id)
        contract.update(changes)
        return manifest

    def test_valid_catalog_reports_fixed_candidates_and_remains_incomplete(self):
        code, result = self.run_cli()
        self.assertEqual((code, result["status"]), (2, "incomplete"), result["diagnostics"])
        details = result["details"]
        self.assertEqual(details["catalog"][".ptg"]["storage_encodings"], {"raw": 1})
        self.assertEqual(details["catalog"][".ps2"]["storage_encodings"], {"zlib": 1})
        model = next(item for item in details["contracts"] if item["id"] == "model-ps2")
        binding = next(item for item in model["loader_bindings"] if item["id"] == "model-name-tree-relocation")
        self.assertEqual(binding["evidence_disposition"], "accepted_static_contract")
        self.assertNotIn("model-name-tree-relocation", [item["id"] for item in details["candidate_loader_bindings"]])
        self.assertFalse(details["complete"])
        self.assertTrue(details["unresolved_logical_profiles"])

    def test_caller_cannot_promote_candidate_contract_to_complete(self):
        manifest = json.loads(MANIFEST.read_text())
        self.update_contract(manifest, "model-ps2", status="complete")
        code, result = self.run_cli(manifest)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("status differs from the fixed registry" in item for item in result["diagnostics"]))

    def test_unrelated_loader_note_cannot_be_supplied_as_authority(self):
        manifest = json.loads(MANIFEST.read_text())
        self.update_contract(manifest, "sprite-ptg", binding_ids=["model-name-tree-relocation"],
                             loader_evidence=[{"function": "FUN_00123908", "source": "notes/evidence/fr2-continuation/jev/d031-decide-mesh-method.json"}])
        code, result = self.run_cli(manifest)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("non-authoritative fields" in item for item in result["diagnostics"]))

    def test_caller_cannot_forge_a_binding_id(self):
        manifest = json.loads(MANIFEST.read_text())
        self.update_contract(manifest, "sprite-ptg", binding_ids=["FUN_00123908"])
        code, result = self.run_cli(manifest)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("binding_ids differ from the fixed registry" in item for item in result["diagnostics"]))

    def test_pinned_source_hash_change_fails_even_when_function_token_remains(self):
        repo = self.root / "repo"
        registry = json.loads((REPO / "notes/asset-loader-registry.json").read_text())
        relative_paths = {
            "tools/verify_asset_contracts.py", "tools/evidence_common.py", "tools/format_contracts.py",
            "tools/corpus_contract.py", "tools/corpus_binding.py", "tools/config_contracts.py",
            "notes/asset-loader-registry.json",
        }
        relative_paths.update(item["path"] for item in registry["corpus_profile"]["evidence_sources"])
        relative_paths.update(item["source"] for item in registry["loader_bindings"])
        for relative in relative_paths:
            source, destination = REPO / relative, repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        target = repo / "notes/evidence/fr2-continuation/jev/d031-decide-mesh-method.json"
        target.write_text(target.read_text() + "\nUnrelated sentence still mentions FUN_00123908.\n")
        code, result = self.run_cli(cli=repo / "tools/verify_asset_contracts.py", output=self.root / "copied-run")
        self.assertEqual((code, result["status"]), (1, "fail"), result["diagnostics"])
        self.assertTrue(any("SHA-256 mismatch" in item for item in result["diagnostics"]))

    def test_manifest_cannot_drop_registry_contracts(self):
        manifest = {"schema_version": 1, "registry": "notes/asset-loader-registry.json", "contracts": []}
        code, result = self.run_cli(manifest)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("every registry contract" in item for item in result["diagnostics"]))

    def test_registry_contracts_are_split_by_asset_type(self):
        code, result = self.run_cli()
        self.assertEqual((code, result["status"]), (2, "incomplete"), result["diagnostics"])
        model = next(row for row in result["details"]["contracts"] if row["id"] == "model-ps2")
        types = [item["asset_type"] for item in model["consumer_contracts"]]
        self.assertEqual(set(types), {"model name tree", "model geometry", "texture library"})
        self.assertEqual(len(types), len(set(types)))
        geometry = next(item for item in model["consumer_contracts"] if item["asset_type"] == "model geometry")
        self.assertIn("FUN_0011ed90", geometry["consumer"])
        self.assertTrue(geometry["unknowns"])
        self.assertIn("Variable plane semantics", geometry["unknowns"])

    def test_unbound_asset_type_cannot_be_hidden_in_an_aggregate_contract(self):
        code, result = self.run_cli()
        self.assertEqual((code, result["status"]), (2, "incomplete"), result["diagnostics"])
        registry = result["details"]
        types = [item["asset_type"] for contract in registry["contracts"] for item in contract["consumer_contracts"]]
        self.assertIn("UI/interface data", types)
        self.assertTrue(any(item["asset_type"] == "UI/interface data" and item["consumer"] == "unresolved"
                            for contract in registry["contracts"] for item in contract["consumer_contracts"]))

    def test_caller_cannot_promote_unbound_type_to_a_consumer(self):
        manifest = json.loads(MANIFEST.read_text())
        ui = next(row for row in manifest["contracts"] if row["id"] == "interface-ui")
        ui["consumer_contract_ids"] = ["guessed-from-ui-extension"]
        code, result = self.run_cli(manifest)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("consumer_contract_ids differ from the fixed registry" in item
                            for item in result["diagnostics"]))


if __name__ == "__main__":
    unittest.main()
