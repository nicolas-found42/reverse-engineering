import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from compiler_probe_recipe import build, run
from evidence_common import Incomplete


class BuildRecipeTests(unittest.TestCase):
    def test_first_unit_is_staged_from_reconstruction_source_tree(self):
        source = build.RECONSTRUCTION_SOURCE
        self.assertTrue(source.is_file())
        self.assertIn("misc3d_db_id", source.read_text())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            executable = game / "extracted/SLES_517.05"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"ELF placeholder")
            payload = bytearray(0xE0000)
            start = build.FUNCTION_VADDR - 0x100000
            payload[start:start + build.FUNCTION_SIZE] = b"r" * build.FUNCTION_SIZE
            section = type("Text", (), {"address": 0x100000, "offset": 0x400, "data": bytes(payload)})()
            digest = hashlib.sha256(b"r" * build.FUNCTION_SIZE).hexdigest()
            with patch.object(build, "FUNCTION_SHA256", digest), \
                 patch.object(build, "corpus_identity", return_value={"corpus_id": "fixture"}), \
                 patch.object(build, "sections", return_value={".text": section}):
                manifest_path, _ = build.prepare(game, root / "tools", root / "out")

            staged = manifest_path.parent / "candidate.c"
            self.assertEqual(staged.read_bytes(), source.read_bytes())

    def test_prepares_corpus_range_and_relocates_tool_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            game.mkdir()
            executable = game / "extracted/SLES_517.05"
            executable.parent.mkdir()
            executable.write_bytes(b"ELF placeholder")
            tool_root = root / "tools"
            output = root / "out"
            payload = bytearray(0xE0000)
            start = build.FUNCTION_VADDR - 0x100000
            payload[start:start + build.FUNCTION_SIZE] = b"r" * build.FUNCTION_SIZE
            section = type("Text", (), {"address": 0x100000, "offset": 0x400,
                                         "data": bytes(payload)})()
            digest = hashlib.sha256(b"r" * build.FUNCTION_SIZE).hexdigest()
            with patch.object(build, "FUNCTION_SHA256", digest), \
                 patch.object(build, "corpus_identity", return_value={"corpus_id": "fixture"}), \
                 patch.object(build, "sections", return_value={".text": section}):
                manifest_path, reference_path = build.prepare(game, tool_root, output)

            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(reference_path.read_bytes(), b"r" * build.FUNCTION_SIZE)
            self.assertEqual(manifest["reference"], str(reference_path.resolve()))
            self.assertEqual(manifest["source"], str((output / "candidate.c").resolve()))
            self.assertIn(str((output / "candidate.ld").resolve()), manifest["candidates"][0]["link"])
            self.assertEqual(manifest["candidates"][0]["compile"][0], "/bin/bash")
            self.assertIn("docker-linux-exec.sh", manifest["candidates"][0]["compile"][1])
            self.assertEqual(manifest["candidates"][0]["compile"][2], str(tool_root.resolve()))
            self.assertEqual(manifest["evidence"]["corpus"]["corpus_id"], "fixture")
            run.validate_manifest_runtimes(manifest_path, tool_root)
            manifest["candidates"][0]["runtime"]["image_id"] = "sha256:replacement"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(Incomplete, "declares a different runtime image"):
                run.validate_manifest_runtimes(manifest_path, tool_root)

    def test_rejects_changed_reference_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            executable = game / "extracted/SLES_517.05"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"ELF placeholder")
            with patch.object(build, "corpus_identity", return_value={"corpus_id": "fixture"}), \
                 patch.object(build, "sections", return_value={".text": type("Text", (), {"address": 0x100000, "offset": 0x400, "data": b"x" * 0xE0000})()}):
                with self.assertRaisesRegex(ValueError, "pinned range identity"):
                    build.prepare(game, root / "tools", root / "out")


class RunnerCliTests(unittest.TestCase):
    def run_fake_probe(self, tmp: Path, probe_result: dict) -> tuple[int, dict]:
        game = tmp / "game"
        executable = game / "extracted/SLES_517.05"
        executable.parent.mkdir(parents=True)
        executable.write_bytes(b"fixture corpus executable")
        tool_root = tmp / "tool-root"
        tool_root.mkdir()
        manifest = tool_root / "manifest.json"
        manifest.write_text(json.dumps({"evidence": {"reference_range": {
            "section": ".text", "vaddr": "001d1800", "file_offset": "000d2800",
            "bytes": 60, "sha256": build.FUNCTION_SHA256, "scope": "game_owned"}}}) + "\n")
        output = tmp / "receipts"

        def prepare_fake(_game: Path, _tool_root: Path, _staging: Path) -> tuple[Path, None]:
            return manifest, None

        with patch.object(run, "prepare", side_effect=prepare_fake), \
             patch.object(run, "validate_manifest_runtimes"), \
             patch.object(run, "validate_runtime_images", return_value={"linux-tools": {}, "wine-compiler": {}}), \
             patch.object(run, "run_probe", return_value=probe_result):
            code = run.main([str(game), str(tool_root), "--output", str(output)])
        receipt_paths = list(output.glob("*/result.json"))
        self.assertEqual(len(receipt_paths), 1)
        return code, json.loads(receipt_paths[0].read_text())

    def test_unique_match_is_successful_probe_but_ac05_stays_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = {"status": "pass", "selected_id": "candidate-a", "matches": ["candidate-a"],
                      "failures": ["candidate-b"], "errors": [], "incomplete": [],
                      "claim_limits": [], "candidates": [{"id": "candidate-a", "status": "pass",
                          "gate": {"status": "pass", "matched_bytes": 60}}]}
            code, receipt = self.run_fake_probe(Path(tmp), result)
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["details"]["probe_status"], "pass")
        self.assertEqual(receipt["details"]["ac05_status"], "incomplete")
        self.assertEqual(receipt["details"]["ac07_status"], "pass")
        self.assertEqual(receipt["details"]["ac07_evidence"]["range"]["scope"], "game_owned")
        self.assertEqual(receipt["details"]["candidates"][0]["gate"]["matched_bytes"], 60)
        self.assertEqual(set(receipt["details"]["runtime_identity"]), {"linux-tools", "wine-compiler"})
        self.assertTrue({Path(run.__file__).resolve(), Path(build.__file__).resolve(),
                         Path(run.TOOLS / "compiler_probe.py").resolve(),
                         Path(run.TOOLS / "matching_diff.py").resolve(),
                         Path(run.TOOLS / "matching_sections.py").resolve(),
                         Path(run.TOOLS / "corpus_contract.py").resolve(),
                         Path(run.TOOLS / "ps2_executables.py").resolve(),
                         Path(run.TOOLS / "evidence_common.py").resolve(),
                         build.RECONSTRUCTION_SOURCE.resolve(),
                         Path(run.__file__).with_name("candidate.ld").resolve(),
                         Path(run.__file__).with_name("manifest.template.json").resolve(),
                         Path(run.__file__).with_name("docker-linux-exec.sh").resolve(),
                         Path(run.__file__).with_name("docker-wine-exec.sh").resolve()}
                        <= {Path(path) for path in receipt["inputs"]})

    def test_zero_matches_produces_failed_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = {"status": "fail", "selected_id": None, "matches": [],
                      "failures": ["candidate-a", "candidate-b"], "errors": [],
                      "incomplete": [], "claim_limits": []}
            code, receipt = self.run_fake_probe(Path(tmp), result)
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "fail")
        self.assertEqual(receipt["details"]["probe_status"], "fail")
        self.assertEqual(receipt["details"]["nonmatching_candidates"], ["candidate-a", "candidate-b"])

    def test_unavailable_candidate_produces_incomplete_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = {"status": "incomplete", "selected_id": None, "matches": [],
                      "failures": [], "errors": [], "incomplete": ["candidate-a"],
                      "claim_limits": []}
            code, receipt = self.run_fake_probe(Path(tmp), result)
        self.assertEqual(code, 2)
        self.assertEqual(receipt["status"], "incomplete")
        self.assertEqual(receipt["details"]["probe_status"], "incomplete")

    def test_replaced_runtime_image_id_is_rejected(self):
        fake = type("Result", (), {"returncode": 0, "stdout": "sha256:replacement|linux/amd64\n",
                                   "stderr": ""})()
        with patch.object(run.subprocess, "run", return_value=fake):
            with self.assertRaisesRegex(Incomplete, "identity or platform differs"):
                run.validate_runtime_images()

    def test_symlinked_tool_root_uses_canonical_paths_for_mounted_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            executable = game / "extracted/SLES_517.05"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"fixture corpus executable")
            actual_tool_root = root / "real-tools"
            actual_tool_root.mkdir()
            linked_tool_root = root / "tools-link"
            linked_tool_root.symlink_to(actual_tool_root, target_is_directory=True)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"evidence": {"reference_range": {
                "section": ".text", "vaddr": "001d1800", "file_offset": "000d2800",
                "bytes": 60, "sha256": build.FUNCTION_SHA256, "scope": "game_owned"}}}) + "\n")
            observed = {}

            def prepare_spy(_game: Path, tool_root: Path, staging: Path):
                observed["prepare_tool_root"] = tool_root
                observed["staging"] = staging
                return manifest, None

            def probe_spy(_manifest: Path, work: Path):
                observed["work"] = work
                return {"status": "pass", "matches": ["candidate-a"], "failures": [],
                        "errors": [], "incomplete": [], "claim_limits": []}

            with patch.object(run, "prepare", side_effect=prepare_spy), \
                 patch.object(run, "validate_manifest_runtimes"), \
                 patch.object(run, "validate_runtime_images", return_value={"linux-tools": {}, "wine-compiler": {}}), \
                 patch.object(run, "run_probe", side_effect=probe_spy):
                code = run.main([str(game), str(linked_tool_root), "--output", str(root / "out")])

            self.assertEqual(code, 0)
            canonical_root = actual_tool_root.resolve()
            self.assertEqual(observed["prepare_tool_root"], canonical_root)
            self.assertEqual(observed["staging"].parent, canonical_root)
            self.assertEqual(observed["work"], observed["staging"] / "candidate-work")
            self.assertTrue(str(observed["work"]).startswith(str(canonical_root) + "/"))


if __name__ == "__main__":
    unittest.main()
