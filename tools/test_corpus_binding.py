"""Corpus-mode verifiers derive the expected files and hashes from the pinned archive baseline."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import corpus_binding
from evidence_common import Incomplete, Invalid, sha256

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games" / "ford-racing-2"
COMMANDS = {"verify_audio.py": ".msb;1", "verify_ptg.py": ".ptg;1", "verify_model.py": ".ps2;1"}


def fake_baseline(root, listing):
    """A Baseline over a synthetic archive listing {archive path: bytes}; files are written under root."""
    baseline = object.__new__(corpus_binding.Baseline)
    baseline.files_root = root
    baseline._files = []
    for path, data in listing.items():
        target = root / path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        baseline._files.append({"path": path, "output_bytes": len(data), "output_sha256": sha256(data)})
    return baseline


class BindingUnits(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_size_is_compared_before_the_file_is_read(self):
        entry = corpus_binding.Entry("/A/x.ptg;1", self.root / "x", 3, sha256(b"abc"))
        (self.root / "x").write_bytes(b"abcdef")
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("read before size check")):
            with self.assertRaises(Invalid) as caught:
                entry.load()
        self.assertEqual(str(caught.exception).count("x.ptg;1"), 0, "the caller adds the name; the message must not repeat it")
        self.assertIn("archive baseline", str(caught.exception))

    def test_matching_content_loads(self):
        entry = corpus_binding.Entry("/A/x.ptg;1", self.root / "x", 3, sha256(b"abc"))
        (self.root / "x").write_bytes(b"abc")
        self.assertEqual(entry.load(), b"abc")

    def test_pairs_reports_headers_and_payloads_with_no_partner_in_the_archive(self):
        base = fake_baseline(self.root, {"/S/a.msh;1": b"1", "/S/a.msb;1": b"2", "/S/lonely.msh;1": b"3", "/S/orphan.msb;1": b"4"})
        pairs, unpaired = base.pairs(".msh;1", ".msb;1")
        self.assertEqual([(h.path, p.path) for h, p in pairs], [("/S/a.msh;1", "/S/a.msb;1")])
        self.assertEqual(unpaired, ["/S/lonely.msh;1", "/S/orphan.msb;1"])

    def test_archive_paths_differing_only_by_case_are_rejected(self):
        base = fake_baseline(self.root, {"/S/a.msh;1": b"1", "/S/A.msh;1": b"2", "/S/a.msb;1": b"3"})
        with self.assertRaises(Invalid) as caught:
            base.pairs(".msh;1", ".msb;1")
        self.assertIn("differ only by case", str(caught.exception))

    def test_missing_expected_files_are_incomplete(self):
        base = fake_baseline(self.root, {"/S/a.ptg;1": b"1"})
        (self.root / "S" / "a.ptg;1").unlink()
        with self.assertRaises(Incomplete):
            base.entries(".ptg;1")


@unittest.skipUnless((GAME / "extracted" / "FILES.HDR").exists(), "real corpus integration; absent corpus is `incomplete`")
class CorpusBinding(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mirror = self.root / "mirror"
        self.mirror.mkdir()
        for path in GAME.rglob("*"):
            target = self.mirror / path.relative_to(GAME)
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif path.name != ".DS_Store":
                target.symlink_to(path)

    def files(self):
        return self.mirror / "extracted" / "files"

    def run_command(self, script, *args):
        out = self.root / "results"
        p = subprocess.run(
            [sys.executable, str(TOOLS / script), "corpus", str(self.mirror), *args, "--output", str(out)],
            capture_output=True,
            text=True,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda r: r.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        return p.returncode, json.loads(reports[-1].read_text())

    def named(self, suffix):
        return [p for p in sorted(self.files().rglob("*")) if p.name.lower().endswith(suffix)]

    def test_removed_files_make_the_run_incomplete(self):
        for script, suffix in (("verify_ptg.py", ".ptg;1"), ("verify_model.py", ".ps2;1"), ("verify_audio.py", ".mib;1")):
            victim = self.named(suffix)[0]
            victim.unlink()
            code, result = self.run_command(script)
            self.assertEqual((code, result["status"]), (2, "incomplete"), script)
            self.assertTrue(any(victim.name in d for d in result["diagnostics"]), (script, result["diagnostics"]))
            victim.symlink_to(GAME / "extracted" / "files" / victim.relative_to(self.files()))

    def test_altered_file_content_fails_against_the_archive_hash(self):
        victim = self.named(".ptg;1")[0]
        original = victim.read_bytes()
        victim.unlink()
        victim.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
        code, result = self.run_command("verify_ptg.py")
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertTrue(any(victim.name in d and "archive" in d for d in result["diagnostics"]), result["diagnostics"])
        self.assertTrue(all(d.count(victim.name) == 1 for d in result["diagnostics"] if victim.name in d), result["diagnostics"])

    def test_unpaired_header_or_payload_in_the_archive_baseline_is_reported(self):
        victim = self.named(".mih;1")[0]
        victim.unlink()
        code, result = self.run_command("verify_audio.py")
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        self.assertTrue(any(victim.name in d for d in result["diagnostics"]), result["diagnostics"])

    def test_altered_baseline_input_is_not_accepted(self):
        hdr = self.mirror / "extracted" / "FILES.HDR"
        data = hdr.read_bytes()
        hdr.unlink()
        hdr.write_bytes(data + b"\0")
        for script in COMMANDS:
            code, result = self.run_command(script)
            self.assertNotEqual(result["status"], "pass", script)
            self.assertNotEqual(code, 0, script)


if __name__ == "__main__":
    unittest.main()
