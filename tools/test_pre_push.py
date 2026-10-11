"""Controls for pushed-object selection and safe snapshot materialization."""
import io
import os
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from pre_push import ROOT, introduced_commits, isolated_environment, materialize


def fixture_tree(root):
    """Tree for a known-valid fixture: the committed HEAD, never staged edits in a live index.

    Validation snapshots have an index but no HEAD commit; their index is the pushed tree.
    """
    head = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '--quiet', 'HEAD^{tree}'],
                          env=isolated_environment(), capture_output=True, text=True)
    if head.returncode == 0:
        return head.stdout.strip()
    return subprocess.check_output(['git', '-C', str(root), 'write-tree'],
                                   env=isolated_environment(), text=True).strip()


class PrePushTests(unittest.TestCase):
    def test_linked_worktree_environment_cannot_change_source_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            commit = self.repository(root)
            worktree = Path(directory) / 'worktree'
            subprocess.run(['git', '-C', str(root), 'worktree', 'add', '-qb', 'probe', str(worktree)], check=True)
            gitdir = subprocess.check_output(['git', '-C', str(worktree), 'rev-parse', '--absolute-git-dir'], text=True).strip()
            config = (root / '.git/config').read_bytes()
            index = Path(gitdir, 'index').read_bytes()
            snapshot = Path(directory) / 'snapshot'
            snapshot.mkdir()
            with patch.dict(os.environ, GIT_DIR=gitdir):
                materialize(commit, snapshot, worktree)
            self.assertEqual((root / '.git/config').read_bytes(), config)
            self.assertEqual(Path(gitdir, 'index').read_bytes(), index)
            self.assertTrue((snapshot / '.git/index').is_file())

    def source_state(self, root, worktree):
        gitdir = Path(subprocess.check_output(
            ['git', '-C', str(worktree), 'rev-parse', '--absolute-git-dir'], text=True).strip())
        files = {}
        for base in (root, worktree):
            for path in base.rglob('*'):
                if '.git' not in path.relative_to(base).parts and path.is_file():
                    files[str(path)] = (path.read_bytes(), path.stat().st_mode)
        return ((root / '.git/config').read_bytes(), (root / '.git/index').read_bytes(),
                (gitdir / 'index').read_bytes(),
                subprocess.check_output(['git', '-C', str(root), 'show-ref']), files,
                *(subprocess.check_output(['git', '-C', str(base), 'status', '--porcelain'])
                  for base in (root, worktree)))

    def test_repository_overrides_cannot_redirect_source_reads_or_snapshot_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            commit = self.repository(root)
            worktree = Path(directory) / 'worktree'
            subprocess.run(['git', '-C', str(root), 'worktree', 'add', '-qb', 'probe', str(worktree)], check=True)
            gitdir = subprocess.check_output(['git', '-C', str(worktree), 'rev-parse', '--absolute-git-dir'], text=True).strip()
            other = Path(directory) / 'other'
            other.mkdir()
            self.repository(other)
            (other / 'example.txt').write_text('unrelated repository\n')
            subprocess.run(['git', '-C', str(other), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(other), '-c', 'user.name=Fixture',
                            '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                            'commit', '-qm', 'unrelated snapshot'], check=True)
            before = self.source_state(root, worktree)
            other_config = (other / '.git/config').read_bytes()
            other_index = (other / '.git/index').read_bytes()
            contamination = {
                'GIT_DIR': str(other / '.git'), 'GIT_WORK_TREE': str(other),
                'GIT_COMMON_DIR': str(other / '.git'), 'GIT_INDEX_FILE': str(other / '.git/index'),
                'GIT_OBJECT_DIRECTORY': str(other / '.git/objects'),
                'GIT_ALTERNATE_OBJECT_DIRECTORIES': str(root / '.git/objects'),
            }
            # Test individual overrides as well as the combined redirected repository.
            for env in ({'GIT_DIR': gitdir}, *({k: v} for k, v in contamination.items()), contamination):
                with self.subTest(variables=sorted(env)), tempfile.TemporaryDirectory() as target:
                    with patch.dict(os.environ, env):
                        self.assertEqual(introduced_commits(
                            [f'refs/heads/probe {commit} refs/heads/probe {"0" * 40}'], worktree), [commit])
                        materialize(commit, Path(target), worktree)
                    self.assertEqual((Path(target) / 'example.txt').read_text(), 'committed snapshot\n')
                    self.assertTrue((Path(target) / '.git/index').is_file())
                    self.assertEqual(self.source_state(root, worktree), before)
                    self.assertEqual((other / '.git/config').read_bytes(), other_config)
                    self.assertEqual((other / '.git/index').read_bytes(), other_index)

    def push_fixture(self, base, failure=None):
        root = base / 'repo'
        root.mkdir()
        materialize(fixture_tree(ROOT), root, ROOT)
        # Run the current implementation with the repository's actual hook and checks.
        shutil.copy2(ROOT / 'tools/pre_push.py', root / 'tools/pre_push.py')
        if failure == 'ip':
            (root / 'forbidden.iso').write_bytes(b'synthetic forbidden payload\n')
        elif failure == 'hygiene':
            with (root / 'tools/README.md').open('a') as output:
                output.write('\nstale synthetic index\n')
        elif failure == 'missing':
            (root / 'tools/ip_rails.py').unlink()
        elif failure == 'cancel':
            (root / 'tools/ip_rails.py').write_text(
                'from pathlib import Path\nimport time\n'
                f'Path({str(base / "validator-started")!r}).write_text("started")\n'
                'time.sleep(60)\n')
        subprocess.run(['git', '-C', str(root), 'add', '--force', '--all'], check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'core.hooksPath=/dev/null',
                        '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'push fixture'], check=True)
        subprocess.run(['git', '-C', str(root), 'config', 'core.hooksPath', 'tools/hooks'], check=True)
        worktree = base / 'worktree'
        subprocess.run(['git', '-C', str(root), 'worktree', 'add', '-qb', 'probe', str(worktree)], check=True)
        remote = base / 'remote'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        # Preserve both staged and unstaged edits, plus an untracked file.
        for tree in (root, worktree):
            (tree / 'fixture.txt').write_text('staged fixture\n')
            subprocess.run(['git', '-C', str(tree), 'add', 'fixture.txt'], check=True)
            (tree / 'fixture.txt').write_text('unstaged fixture\n')
            (tree / 'untracked.txt').write_text('untracked fixture\n')
        return root, worktree, remote

    def test_real_push_runs_normal_hook_and_preserves_source_on_success_and_failure(self):
        for linked in (False, True):
            for failure in (None, 'ip', 'hygiene', 'missing'):
                with self.subTest(linked=linked, failure=failure), tempfile.TemporaryDirectory() as directory:
                    root, worktree, remote = self.push_fixture(Path(directory), failure)
                    before = self.source_state(root, worktree)
                    source = worktree if linked else root
                    result = subprocess.run(['git', '-C', str(source), 'push', str(remote), 'HEAD:refs/heads/probe'],
                                            env=isolated_environment(), capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    self.assertEqual(result.returncode == 0, failure is None, output)
                    expected = {None: 'PASS pushed revision', 'ip': 'refused forbidden.iso',
                                'hygiene': 'generated file is missing or stale: tools/README.md',
                                'missing': 'pushed revision lacks required check: ip_rails.py'}
                    self.assertIn(expected[failure], output)
                    self.assertEqual(self.source_state(root, worktree), before)
                    refs = subprocess.check_output(['git', '--git-dir', str(remote), 'for-each-ref'])
                    self.assertEqual(bool(refs), failure is None)

    def test_cancelled_real_linked_worktree_push_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, worktree, remote = self.push_fixture(base, 'cancel')
            before = self.source_state(root, worktree)
            with subprocess.Popen(['git', '-C', str(worktree), 'push', str(remote), 'HEAD:refs/heads/probe'],
                                  env=isolated_environment(), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, start_new_session=True) as process:
                try:
                    deadline = time.monotonic() + 10
                    while not (base / 'validator-started').exists() and process.poll() is None:
                        if time.monotonic() >= deadline:
                            self.fail('snapshot validator did not start')
                        time.sleep(0.02)
                    self.assertTrue((base / 'validator-started').exists())
                    os.killpg(process.pid, signal.SIGINT)
                    process.communicate(timeout=10)
                    self.assertNotEqual(process.returncode, 0)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate()
            self.assertEqual(self.source_state(root, worktree), before)
            self.assertEqual(subprocess.check_output(['git', '--git-dir', str(remote), 'for-each-ref']), b'')

    def repository(self, root):
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        (root / 'example.txt').write_text('committed snapshot\n')
        subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], check=True)
        return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()

    def test_fixture_tree_ignores_staged_edits_to_the_live_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            commit = self.repository(root)
            committed = subprocess.check_output(['git', '-C', str(root), 'rev-parse', commit + '^{tree}'],
                                                text=True).strip()
            (root / 'example.txt').write_text('staged local edit\n')
            subprocess.run(['git', '-C', str(root), 'add', 'example.txt'], check=True)
            self.assertEqual(fixture_tree(root), committed)

    def test_fixture_tree_uses_the_index_of_a_snapshot_without_a_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'snapshot'
            root.mkdir()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'example.txt').write_text('snapshot content\n')
            subprocess.run(['git', '-C', str(root), 'add', 'example.txt'], check=True)
            expected = subprocess.check_output(['git', '-C', str(root), 'write-tree'], text=True).strip()
            self.assertEqual(fixture_tree(root), expected)

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
