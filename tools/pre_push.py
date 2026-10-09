#!/usr/bin/env python3
"""Validate newly pushed commit snapshots, independent of working-tree contents."""
from __future__ import annotations

import io
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SHA = re.compile(r'(?:[0-9a-f]{40}|[0-9a-f]{64})\Z')


def introduced_commits(lines: list[str], root: Path = ROOT) -> list[str]:
    commits = set()
    for line in lines:
        local_ref, local_sha, remote_ref, remote_sha = line.split()
        if not SHA.fullmatch(local_sha) or not SHA.fullmatch(remote_sha):
            raise ValueError('invalid push object identity')
        if set(local_sha) == {'0'}:
            continue  # Ref deletion introduces no source tree.
        args = ['git', '-C', str(root), 'rev-list', local_sha, '--not', '--remotes']
        if set(remote_sha) != {'0'}:
            args.append(remote_sha)
        output = subprocess.check_output(args, text=True)
        commits.update(output.splitlines())
    return sorted(commits)


def materialize(commit: str, target: Path, root: Path = ROOT) -> None:
    archive = subprocess.check_output(['git', '-C', str(root), 'archive', '--format=tar', commit])
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            path = target / member.name
            if not path.resolve().is_relative_to(target.resolve()) or not (member.isfile() or member.isdir()):
                raise ValueError('unsupported or escaping archive member: ' + member.name)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                content = stream.extractfile(member)
                if content is None:
                    raise ValueError('archive member has no content')
                path.write_bytes(content.read())
                path.chmod(member.mode & 0o777)
    subprocess.run(['git', 'init', '-q', str(target)], check=True)
    subprocess.run(['git', '-C', str(target), 'add', '--force', '--all'], check=True)


def main() -> int:
    try:
        commits = introduced_commits(sys.stdin.read().splitlines())
        for commit in commits:
            with tempfile.TemporaryDirectory(prefix='fr2-push-') as directory:
                snapshot = Path(directory)
                materialize(commit, snapshot)
                for script, args in (('ip_rails.py', ['--tree']), ('repository_hygiene.py', ['check'])):
                    path = snapshot / 'tools' / script
                    if not path.is_file():
                        raise ValueError('pushed revision lacks required check: ' + script)
                    subprocess.run([sys.executable, str(path), *args], cwd=snapshot, check=True)
                print('PASS pushed revision ' + commit)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('pre-push refused: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
