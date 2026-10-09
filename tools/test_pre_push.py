"""Controls for pushed-object selection and safe snapshot materialization."""
import io
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pre_push import introduced_commits, materialize


class PrePushTests(unittest.TestCase):
    def repository(self, root):
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        (root / 'example.txt').write_text('committed snapshot\n')
        subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], check=True)
        return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()

    def test_new_ref_snapshot_ignores_working_tree_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            commit = self.repository(root)
            commits = introduced_commits([f'refs/heads/test {commit} refs/heads/test {"0" * 40}'], root)
            self.assertEqual(commits, [commit])
            (root / 'example.txt').write_text('uncommitted mutation\n')
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            materialize(commit, snapshot, root)
            self.assertEqual((snapshot / 'example.txt').read_text(), 'committed snapshot\n')

    def test_snapshot_keeps_previously_tracked_ignored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            self.repository(root)
            (root / '.gitignore').write_text('example.txt\n')
            subprocess.run(['git', '-C', str(root), 'add', '.gitignore'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'ignore already tracked file'], check=True)
            commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            materialize(commit, snapshot, root)
            files = subprocess.check_output(['git', '-C', str(snapshot), 'ls-files'], text=True).splitlines()
            self.assertIn('example.txt', files)

    def test_ref_deletion_introduces_nothing(self):
        self.assertEqual(introduced_commits([f'refs/heads/test {"0" * 40} refs/heads/test {"1" * 40}']), [])

    def test_export_ignore_cannot_silently_drop_a_tracked_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            self.repository(root)
            (root / '.gitattributes').write_text('example.txt export-ignore\n')
            subprocess.run(['git', '-C', str(root), 'add', '.gitattributes'], check=True)
            tree = subprocess.check_output(['git', '-C', str(root), 'write-tree'], text=True).strip()
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            with self.assertRaisesRegex(ValueError, 'exact tracked'):
                materialize(tree, snapshot, root)

    def test_export_substitution_cannot_change_tracked_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            self.repository(root)
            (root / 'example.txt').write_text('$Format:%H$\n')
            (root / '.gitattributes').write_text('example.txt export-subst\n')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'substitution fixture'], check=True)
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            with self.assertRaisesRegex(ValueError, 'tracked bytes'):
                materialize('HEAD', snapshot, root)

    def test_malformed_object_identity_fails(self):
        with self.assertRaisesRegex(ValueError, 'object identity'):
            introduced_commits(['refs/heads/test --all refs/heads/test ' + '0' * 40])

    def test_symlink_archive_is_rejected(self):
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode='w') as stream:
            member = tarfile.TarInfo('escape')
            member.type = tarfile.SYMTYPE
            member.linkname = '/tmp'
            stream.addfile(member)
        with tempfile.TemporaryDirectory() as directory, patch('pre_push.subprocess.check_output', return_value=data.getvalue()):
            with self.assertRaisesRegex(ValueError, 'unsupported or escaping'):
                materialize('1' * 40, Path(directory))


if __name__ == '__main__':
    unittest.main()
