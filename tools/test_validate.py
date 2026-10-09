"""Controls for exact staged/revision validation and failed portable checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

import validate
import test_pre_push


class ValidateTests(unittest.TestCase):
    def test_staged_snapshot_excludes_unstaged_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            test_pre_push.PrePushTests().repository(root)
            (root / 'example.txt').write_text('staged\n')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            tree = validate.snapshot_tree(root, None, True)
            (root / 'example.txt').write_text('unstaged\n')
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            validate.materialize(tree, snapshot, root)
            self.assertEqual((snapshot / 'example.txt').read_text(), 'staged\n')

    def test_revision_identity_is_resolved_by_git(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commit = test_pre_push.PrePushTests().repository(root)
            self.assertEqual(validate.snapshot_tree(root, commit, False),
                             validate.snapshot_tree(root, 'HEAD', False))
            with self.assertRaises(subprocess.CalledProcessError):
                validate.snapshot_tree(root, '--all', False)

    def test_missing_linter_makes_validation_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('validate.subprocess.run', side_effect=FileNotFoundError('missing check')):
                report = validate.checks(Path(directory), Path(directory) / 'logs', portable=True)
            self.assertFalse(report['successful'])
            self.assertEqual(len(report['checks']), 4)


if __name__ == '__main__':
    unittest.main()
