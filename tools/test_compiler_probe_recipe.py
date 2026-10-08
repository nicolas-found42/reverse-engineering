import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from compiler_probe_recipe import build


class BuildRecipeTests(unittest.TestCase):
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
            section = type("Text", (), {"address": 0x100000, "data": bytes(payload)})()
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
            self.assertTrue(manifest["candidates"][0]["compile"][0].startswith(str(tool_root.resolve())))
            self.assertEqual(manifest["evidence"]["corpus"]["corpus_id"], "fixture")

    def test_rejects_changed_reference_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            executable = game / "extracted/SLES_517.05"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"ELF placeholder")
            with patch.object(build, "corpus_identity", return_value={"corpus_id": "fixture"}), \
                 patch.object(build, "sections", return_value={".text": type("Text", (), {"address": 0x100000, "data": b"x" * 0xE0000})()}):
                with self.assertRaisesRegex(ValueError, "pinned range identity"):
                    build.prepare(game, root / "tools", root / "out")


if __name__ == "__main__":
    unittest.main()
