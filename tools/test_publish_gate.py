#!/usr/bin/env python3
"""Tests for tools/publish_gate.py: positive, negative and incomplete controls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish_gate  # noqa: E402


class PublishGateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fr2-publish-gate-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # A self-contained Git repository: the gate must not depend on the caller
        # being a checkout (validate.py materializes trees outside any repository).
        self.repository = self.root / "repository"
        self.repository.mkdir()
        # Host git config is ignored so the fixture cannot depend on it; the
        # identity is carried in the environment instead, because a checkout on
        # CI has no user or committer configured.
        environment = dict(
            os.environ,
            GIT_CONFIG_GLOBAL="/dev/null",
            GIT_CONFIG_SYSTEM="/dev/null",
            GIT_AUTHOR_NAME="gate",
            GIT_AUTHOR_EMAIL="gate@example.invalid",
            GIT_COMMITTER_NAME="gate",
            GIT_COMMITTER_EMAIL="gate@example.invalid",
            GIT_AUTHOR_DATE="2026-01-01T00:00:00Z",
            GIT_COMMITTER_DATE="2026-01-01T00:00:00Z",
        )
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            timeout=60,
            capture_output=True,
            env=environment,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repository),
                "commit",
                "-q",
                "--allow-empty",
                "-m",
                "synthetic",
            ],
            check=True,
            timeout=60,
            capture_output=True,
            env=environment,
        )
        self.revision = subprocess.check_output(
            ["git", "-C", str(self.repository), "rev-parse", "HEAD"], text=True
        ).strip()

    def body(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text)
        return path

    def gate(self, argv: list[str]) -> tuple[int, dict]:
        completed = subprocess.run(
            [sys.executable, str(Path(publish_gate.__file__)), *argv],
            capture_output=True,
            text=True,
            timeout=300,
        )
        return completed.returncode, json.loads(completed.stdout or "{}")

    def cli(self, argv: list[str]) -> tuple[int, dict]:
        """Run the command line against the synthetic repository."""
        return self.gate(["--root", str(self.repository), *argv])

    def test_local_reference_control_passes(self):
        """Positive fixture: a resolvable revision and no stale claim passes locally."""
        path = self.body(
            "good.md", f"Measured at `{self.revision}` on accepted main.\n"
        )
        code, report = self.cli(["--body", str(path), "--offline"])
        self.assertEqual(code, 0, report)
        self.assertEqual(report["results"][0]["status"], "pass")

    def test_tree_identifier_passes(self):
        """A cited tree id resolves; only commits are not the sole accepted form."""
        tree = subprocess.check_output(
            ["git", "-C", str(self.repository), "rev-parse", "HEAD^{tree}"], text=True
        ).strip()
        path = self.body("tree.md", f"Validated against tree `{tree}`.\n")
        code, report = self.cli(["--body", str(path), "--offline"])
        self.assertEqual(code, 0, report)
        self.assertEqual(report["results"][0]["status"], "pass")

    def test_unresolved_revision_fails(self):
        """Negative control: a cited revision that does not exist must fail."""
        dead = "0" * 40
        path = self.body(
            "dead-revision.md", f"Measured at `{dead}` on accepted main.\n"
        )
        code, report = self.cli(["--body", str(path), "--offline"])
        self.assertEqual(code, 1, report)
        finding = report["results"][0]["findings"][0]
        self.assertEqual(finding["kind"], "unresolved_revision")

    def test_stale_merge_claim_fails(self):
        """Negative control: an unmerged assertion against a merged PR must fail."""
        path = self.body(
            "stale-merge.md",
            "PR #42 checks pass; PR #42 is not merged or included in this baseline.\n",
        )
        result = publish_gate.check_body(
            path,
            publish_gate.ROOT,
            offline=False,
            pr_lookup=lambda _root, _number: "MERGED",
        )
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["findings"][0]["kind"], "stale_merge_claim")

    def test_stale_merge_claim_is_not_reported_for_open_pull(self):
        """A truthful unmerged assertion against an open PR stays a pass."""
        path = self.body(
            "open-merge.md", "PR #42 is not merged or included in this baseline.\n"
        )
        result = publish_gate.check_body(
            path,
            publish_gate.ROOT,
            offline=False,
            pr_lookup=lambda root, number: "OPEN",
        )
        self.assertEqual(result["status"], "pass", result)

    def test_absent_body_is_incomplete(self):
        """Incomplete fixture: a missing draft body is not a pass and not a fail."""
        code, report = self.gate(["--body", str(self.root / "absent.md"), "--offline"])
        self.assertEqual(code, 2, report)
        self.assertEqual(report["results"][0]["status"], "incomplete")

    def test_unknown_pull_state_is_recorded_not_silently_passed(self):
        """A tracker lookup that cannot answer must be reported, not assumed truthful."""
        path = self.body(
            "unknown-merge.md", "PR #42 is not merged or included in this baseline.\n"
        )
        result = publish_gate.check_body(
            path,
            publish_gate.ROOT,
            offline=False,
            pr_lookup=lambda root, number: "unknown",
        )
        self.assertEqual(result["status"], "pass")
        self.assertIn("pull_request_state_check:42", result["skipped"])


if __name__ == "__main__":
    unittest.main()
