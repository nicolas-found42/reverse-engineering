"""Public CLI tests for archive-derived asset consumer contract coverage."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

TOOLS = Path(__file__).resolve().parent
CLI = TOOLS / "verify_asset_contracts.py"
TERMS = {"consumer": "unresolved", "bounds": "unresolved", "field_effects": "unresolved",
         "transformations": "unresolved", "allocation_lifetime": "unresolved",
         "handoffs": "unresolved", "unknowns": ["consumer evidence not found"]}
COMPLETE_TERMS = {"consumer": "FUN_00123908 model loader", "bounds": "bounded fixture bytes",
                  "field_effects": "all fixture fields covered", "transformations": "none",
                  "allocation_lifetime": "bounded fixture lifetime", "handoffs": "none", "unknowns": []}


def archive(files):
    """Build a one-directory archive with chunk-aligned file records."""
    header = bytearray(struct.pack("<I", 1) + struct.pack("<II", len(files), 0) + struct.pack("<I", len(files)))
    records = bytearray()
    dat = bytearray()
    for name, payload, compressed in files:
        while len(dat) % 2048:
            dat.append(0)
        stored = struct.pack("<I", len(payload)) + zlib.compress(payload) if compressed else payload
        offset = len(dat)
        dat += stored
        typ = 0xFFFFFFFF
        records += name.encode().ljust(16, b"\0") + struct.pack("<III", typ, offset // 2048, len(stored))
    return bytes(header + records), bytes(dat)


class AssetContractCli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, contracts, files=None):
        hdr, dat = archive(files or [("UI.PTG;1", b"tile", False), ("MODEL.PS2;1", b"model", True)])
        hp, dp = self.root / "FILES.HDR", self.root / "FILES.DAT"
        cp, out = self.root / "contracts.json", self.root / "out"
        hp.write_bytes(hdr)
        dp.write_bytes(dat)
        cp.write_text(json.dumps(contracts))
        proc = subprocess.run([sys.executable, str(CLI), "archive", str(hp), str(dp), "--contracts", str(cp), "--output", str(out)], capture_output=True, text=True)
        reports = list(out.glob("*/result.json"))
        self.assertTrue(reports, proc.stderr)
        return proc.returncode, json.loads(reports[0].read_text())

    def test_archive_variants_are_derived_and_unresolved_contracts_stay_incomplete(self):
        code, result = self.run_cli({
            "schema_version": 1,
            "contracts": [
                {"id": "ptg", "asset_types": ["PTG sprite"], "extensions": [".ptg"], "status": "unresolved", "variant_dispositions": {"raw": "unresolved"}, "loader_evidence": [], "consumer_contract": TERMS, "limits": ["consumer not identified"]},
                {"id": "model", "asset_types": ["model"], "extensions": [".ps2"], "status": "partial", "variant_dispositions": {"zlib": "covered"}, "loader_evidence": [{"function": "FUN_00123908", "source": "notes/evidence/fr2-continuation/next-phase.md"}], "consumer_contract": {**TERMS, "consumer": "FUN_00123908 model loader"}, "limits": ["geometry and texture levels unresolved"]},
            ],
        })
        self.assertEqual((code, result["status"]), (2, "incomplete"), result["diagnostics"])
        catalog = result["details"]["catalog"]
        self.assertEqual(catalog[".ptg"]["variants"], {"raw": 1})
        self.assertEqual(catalog[".ps2"]["variants"], {"zlib": 1})
        self.assertEqual(result["details"]["unresolved_contracts"], ["ptg", "model"])

    def test_supported_claim_without_a_real_loader_reference_fails(self):
        code, result = self.run_cli({
            "schema_version": 1,
            "contracts": [{"id": "ptg", "asset_types": ["PTG sprite"], "extensions": [".ptg"], "status": "complete", "variant_dispositions": {"raw": "covered"}, "loader_evidence": [], "consumer_contract": TERMS, "limits": []}],
        })
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("loader evidence" in item.lower() for item in result["diagnostics"]))

    def test_complete_model_contract_with_bound_loader_and_exact_variant_passes(self):
        code, result = self.run_cli({
            "schema_version": 1,
            "contracts": [{
                "id": "model", "asset_types": ["model"], "extensions": [".ps2"], "status": "complete",
                "variant_dispositions": {"zlib": "covered"},
                "loader_evidence": [{"function": "FUN_00123908", "source": "notes/evidence/fr2-continuation/next-phase.md"}],
                "consumer_contract": COMPLETE_TERMS,
                "limits": ["Fixture only"],
            }],
        }, [("MODEL.PS2;1", b"model", True)])
        self.assertEqual((code, result["status"]), (0, "pass"), result["diagnostics"])

    def test_complete_contract_cannot_invent_an_archive_variant(self):
        code, result = self.run_cli({
            "schema_version": 1,
            "contracts": [{
                "id": "ptg", "asset_types": ["PTG sprite"], "extensions": [".ptg"], "status": "complete",
                "variant_dispositions": {"raw": "covered", "made_up": "covered"},
                "loader_evidence": [{"function": "FUN_00123908", "source": "notes/evidence/fr2-continuation/next-phase.md"}],
                "consumer_contract": {**TERMS, "consumer": "FUN_00123908 synthetic contract fixture"},
                "limits": ["Fixture only"],
            }],
        })
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("absent from the archive" in item for item in result["diagnostics"]))

    def test_known_loader_and_covered_header_do_not_hide_consumer_unknowns(self):
        code, result = self.run_cli({
            "schema_version": 1,
            "contracts": [{
                "id": "model", "asset_types": ["model"], "extensions": [".ps2"], "status": "complete",
                "variant_dispositions": {"zlib": "covered"},
                "loader_evidence": [{"function": "FUN_00123908", "source": "notes/evidence/fr2-continuation/next-phase.md"}],
                "consumer_contract": {**COMPLETE_TERMS, "unknowns": ["geometry body meaning remains unresolved"]},
                "limits": ["Fixture only"],
            }],
        }, [("MODEL.PS2;1", b"model", True)])
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any("retains unknowns" in item for item in result["diagnostics"]))

    def test_missing_extension_contract_fails_instead_of_disappearing(self):
        code, result = self.run_cli({"schema_version": 1, "contracts": []})
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any(".ptg" in item and ".ps2" in item for item in result["diagnostics"]))


if __name__ == "__main__":
    unittest.main()
