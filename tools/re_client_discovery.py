#!/usr/bin/env python3
"""Check native RE client discovery separately, using isolated model-free Codex/omp profiles."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from re_rpc import Rpc

ROOT = Path(__file__).resolve().parent.parent
MODES = {'ghidra': 'ghidra', 'rea': 'rea', 'radare2': 'r2'}


def environment():
    return {key: os.environ[key] for key in ['HOME', 'PATH', 'LANG', 'TERM', 'TMPDIR'] if key in os.environ}


def entries():
    return {name: {'command': sys.executable, 'args': [str(ROOT / 'tools/re_mcp.py'), mode], 'timeout': 120000}
            for name, mode in MODES.items()}


def verify(output: Path):
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    records = []
    for name in MODES:
        run = subprocess.run(['claude', 'mcp', 'get', name], capture_output=True, text=True, env=environment())
        (output / ('claude-' + name + '.log')).write_text(run.stdout + run.stderr)
        if run.returncode or 'Connected' not in run.stdout or str(ROOT / 'tools/re_mcp.py') not in run.stdout:
            raise RuntimeError('Native Claude registration/connection failed: ' + name)
        records.append({'client': 'claude', 'server': name, 'successful': True, 'registration': 'existing user entry'})
    codex_home = output / 'codex'
    codex_home.mkdir(exist_ok=True)
    text = ''
    for name, entry in entries().items():
        text += '\n[mcp_servers.' + name + ']\ncommand = ' + json.dumps(entry['command'])
        text += '\nargs = ' + json.dumps(entry['args']) + '\nstartup_timeout_sec = 120\ntool_timeout_sec = 120\n'
    (codex_home / 'config.toml').write_text(text)
    bundled = Path('/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')
    executable = str(bundled) if bundled.exists() else shutil.which('codex')
    if not executable:
        raise RuntimeError('Native Codex executable is missing')
    env = dict(environment(), CODEX_HOME=str(codex_home))
    with Rpc([executable, 'app-server', '--stdio'], output / 'codex.log', env=env, cwd=ROOT, mcp=False) as rpc:
        rpc.call('initialize', {'clientInfo': {'name': 're-doctor', 'version': '1.0.0'},
                               'capabilities': {'experimentalApi': True}})
        rpc.send({'method': 'initialized'})
        thread = rpc.call('thread/start', {'cwd': str(ROOT), 'ephemeral': True})['thread']['id']
        for name in MODES:
            result = rpc.call('mcpServerStatus/list', {'serverName': name, 'threadId': thread})
            server = next(x for x in result['data'] if x['name'] == name)
            count = len(server['tools'])
            if not count:
                raise RuntimeError('Native Codex catalog is empty: ' + name)
            records.append({'client': 'codex', 'server': name, 'tool_count': count, 'successful': True,
                            'registration': 'isolated shared-launcher profile'})
    omp_home = output / 'omp'
    agent = omp_home / 'agent'
    agent.mkdir(parents=True, exist_ok=True)
    (agent / 'mcp.json').write_text(json.dumps({'mcpServers': entries()}))
    (agent / 'config.yml').write_text('mcp:\n  enabled: true\n')
    env = dict(environment(), PI_CONFIG_DIR=os.path.relpath(omp_home, Path.home()), PI_CODING_AGENT_DIR=str(agent))
    command = ['omp', '--mode', 'rpc', '--no-ui', '--no-session', '--no-extensions', '--no-skills',
               '--no-rules', '--no-title', '--no-lsp', '--no-pty', '--model', 'openai/gpt-5.2',
               '--api-key', 'unused-native-verification-placeholder', '--cwd', str(ROOT)]
    with Rpc(command, output / 'omp.log', env=env, cwd=ROOT, mcp=False) as rpc:
        for name in MODES:
            result = rpc.exchange({'type': 'prompt', 'message': '/mcp test ' + name})
            local = result.get('success') and result.get('data', {}).get('agentInvoked') is False
            text = '\n'.join(x.get('text', '') for x in rpc.events if x.get('type') == 'command_output')
            if not local or not re.search(r'connected|tools', text, re.I):
                raise RuntimeError('Native omp local MCP test failed: ' + name)
            records.append({'client': 'omp', 'server': name, 'successful': True, 'agentInvoked': False,
                            'registration': 'isolated shared-launcher profile'})
    return {'schema': 'fr2-native-discovery/v1', 'model_calls': 0, 'results': records,
            'limits': ['Codex/omp checks exercise isolated profiles; they do not assert the live global registration.',
                       'Discovery is separate from the isolated doctor analysis and rejection controls.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.output.resolve())
    (args.output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'successful': True, 'native_connections': len(report['results']),
                      'model_calls': 0, 'report': str(args.output / 'result.json')}))


if __name__ == '__main__':
    main()
