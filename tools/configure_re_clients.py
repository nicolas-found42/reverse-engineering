#!/usr/bin/env python3
"""Register shared RE launchers; preserve unrelated client entries and settings.

The native Claude/Codex commands own their configuration updates. OMP's native
JSON format has no noninteractive add command, so its document is updated
atomically. No provider key is resolved, logged, or placed in these entries.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SERVERS = {'ghidra': 'ghidra', 'rea': 'rea', 'radare2': 'r2'}


def atomic_json(path: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        name = stream.name
    os.chmod(name, path.stat().st_mode & 0o777)
    os.replace(name, path)


def main() -> None:
    launcher = str(ROOT / 'tools/re_mcp.py')
    python = sys.executable
    for name, mode in SERVERS.items():
        # Remove/re-add only our known entries; removal of an absent entry is harmless.
        subprocess.run(['claude', 'mcp', 'remove', name, '--scope', 'user'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['claude', 'mcp', 'add', '--scope', 'user', name,
                        '--', python, launcher, mode], check=True)
        subprocess.run(['codex', 'mcp', 'add', name, '--', python, launcher, mode], check=True)
    path = Path.home() / '.omp/agent/mcp.json'
    document = json.loads(path.read_text())
    for name, mode in SERVERS.items():
        document.setdefault('mcpServers', {})[name] = {
            'command': python, 'args': [launcher, mode], 'timeout': 120000}
    atomic_json(path, document)
    # The native Codex add operation has no persistent timeout flag.
    path = Path.home() / '.codex/config.toml'
    text = path.read_text()
    for name in SERVERS:
        pattern = r'(\[mcp_servers\.' + re.escape(name) + r'\]\n)(.*?)(?=\n\[|\Z)'
        def change(match):
            body = re.sub(r'^(?:startup_timeout_sec|tool_timeout_sec)\s*=.*\n?', '',
                          match.group(2), flags=re.M)
            return match.group(1) + body.rstrip() + '\nstartup_timeout_sec = 120\ntool_timeout_sec = 120\n'
        text, count = re.subn(pattern, change, text, flags=re.S)
        if count != 1:
            raise RuntimeError('Expected exactly one native Codex entry: ' + name)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        stream.write(text)
        temporary = stream.name
    os.chmod(temporary, path.stat().st_mode & 0o777)
    os.replace(temporary, path)
    print('Registered Ghidra, REA and read-only radare2 in Claude Code, OMP and Codex')


if __name__ == '__main__':
    main()
