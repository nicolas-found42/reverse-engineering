#!/usr/bin/env python3
"""Run the existing portable checks and tests on a working tree or exact Git snapshot."""
from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from pre_push import materialize

ROOT = Path(__file__).resolve().parent.parent


def snapshot_tree(root: Path, revision: str | None, staged: bool) -> str:
    if staged:
        return subprocess.check_output(['git', '-C', str(root), 'write-tree'], text=True).strip()
    return subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--verify',
                                    '--end-of-options', revision + '^{tree}'], text=True).strip()


def checks(root: Path, output: Path, *, portable: bool, tests: bool = True) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if portable:
        env['CI'] = '1'
    commands = [('ip', [sys.executable, 'tools/ip_rails.py', '--tree']),
                ('hygiene', [sys.executable, 'tools/repository_hygiene.py', 'check']),
                ('lint', ['ruff', 'check', 'tools/'])]
    if tests:
        commands.append(('tests', [sys.executable, 'tools/run_tests.py', '--summary', str(output / 'tests.json')]))
    results = []
    for name, command in commands:
        with (output / (name + '.log')).open('w') as log:
            try:
                run = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
                code = run.returncode
            except OSError as error:
                log.write(str(error) + '\n')
                code = 2
        result = {'check': name, 'exit_code': code, 'log': str(output / (name + '.log'))}
        results.append(result)
        print(('PASS' if code == 0 else 'FAIL') + ' ' + name + ': ' + result['log'], flush=True)
    return {'schema': 'fr2-validation/v1', 'portable': portable,
            'successful': all(x['exit_code'] == 0 for x in results), 'checks': results}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument('--revision', help='Validate the exact tracked tree of a commit or ref')
    scope.add_argument('--staged', action='store_true', help='Validate the current Git index')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quick', action='store_true', help='Run IP, hygiene and lint; omit the test suite')
    args = parser.parse_args(argv)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = (args.output or ROOT / '.scratch/validation' / stamp).resolve()
    tree = None
    if args.staged or args.revision:
        tree = snapshot_tree(ROOT, args.revision, args.staged)
        with tempfile.TemporaryDirectory(prefix='fr2-validation-') as directory:
            snapshot = Path(directory)
            materialize(tree, snapshot)
            report = checks(snapshot, output, portable=True, tests=not args.quick)
    else:
        report = checks(ROOT, output, portable=False, tests=not args.quick)
    report.update(tree=tree, scope='staged' if args.staged else args.revision or 'working-tree')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'successful': report['successful'], 'scope': report['scope'],
                      'tree': tree, 'report': str(output / 'result.json')}))
    return 0 if report['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
