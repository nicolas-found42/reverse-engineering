#!/usr/bin/env python3
"""Run installed static utilities without adding dependencies to repository tools."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tool', choices=('objdiff', 'stdump', 'r2', 'python', 'pyghidra', 'rea'))
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    remaining = args.arguments
    settings = json.loads((ROOT / '.scratch/re-setup/config.json').read_text())
    install = Path(settings['ghidra']).parent
    env = dict(os.environ, JAVA_HOME=settings['java_home'], GHIDRA_INSTALL_DIR=settings['ghidra'])
    if args.tool == 'rea':
        binary = settings['npx']
        argv = [binary, '-y', 'rea-agents@' + settings['rea_version'], *remaining]
    else:
        binaries = {'objdiff': install / 'objdiff-cli', 'stdump': install / 'ccc/build/stdump',
                    'r2': install / 'r2-install/bin/r2', 'python': install / 'python/bin/python',
                    'pyghidra': install / 'python/bin/pyghidra'}
        binary = str(binaries[args.tool])
        argv = [binary, *remaining]
    os.execve(binary, argv, env)


if __name__ == '__main__':
    main()
