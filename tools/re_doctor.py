#!/usr/bin/env python3
"""Reproduce synthetic analysis and authority controls on an isolated static RE backend."""
from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile

import re_mcp
from re_rpc import Rpc

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def call(session, name, args):
    result, text = session.tool(name, args)
    require(not result.get('isError'), 'Synthetic tool failed: ' + name)
    if text.lstrip().startswith('{'):
        value = json.loads(text)
        require(not value.get('error') and value.get('success') is not False, 'Synthetic tool rejected: ' + name)
    return text


def rejected(session, name, args, pattern):
    _, text = session.tool(name, args)
    require(re.search(pattern, text, re.I) is not None, 'Control did not reject as required: ' + name)


def measured(records, name, action):
    try:
        action()
    except Exception as error:
        records.append({'check': name, 'successful': False, 'error': str(error)})
        raise
    records.append({'check': name, 'successful': True})


def exercise(session, project_root: Path, outside: Path, probe: Path, records):
    call(session, 'create_project', {'parentDir': str(project_root), 'name': 'synthetic'})
    call(session, 'load_program', {'file': str(probe)})
    call(session, 'run_analysis', {'program': probe.name})
    functions = call(session, 'list_functions', {'program': probe.name})
    match = re.search(r're_setup_probe at ([0-9a-fA-F]+)', functions)
    require(match is not None, 'Synthetic function is absent')
    text = call(session, 'decompile_function', {'program': probe.name, 'address': match.group(1)})
    require(re.search(r'\*\s*3\s*\+\s*7', text) is not None, 'Synthetic decompilation differs')
    records.append({'check': 'synthetic_decompilation', 'successful': True})
    for name, tool, arguments, pattern in [
        ('required_selector', 'get_metadata', {}, r'program.*(?:required|selector)|(?:required|selector).*program'),
        ('disabled_scripts', 'run_script_inline', {'program': probe.name, 'code': 'synthetic invalid Java'},
         r'script execution disabled'),
        ('create_scope', 'create_project', {'parentDir': str(outside), 'name': 'denied'}, r'outside|denied'),
        ('open_scope', 'open_project', {'path': str(outside / 'denied.gpr')}, r'outside|denied'),
        ('restore_input_scope', 'restore_project', {'gar_path': str(outside / 'denied.gar'),
         'parent_dir': str(project_root), 'project_name': 'denied-input'}, r'outside|denied'),
        ('restore_output_scope', 'restore_project', {'gar_path': str(project_root / 'absent.gar'),
         'parent_dir': str(outside), 'project_name': 'denied-output'}, r'outside|denied')]:
        measured(records, name, lambda: rejected(session, tool, arguments, pattern))


def isolated(settings: dict, output: Path, records):
    file_root = Path(settings['file_root']).resolve()
    # Ghidra rejects dot-prefixed project directories. Keep the project outside .scratch.
    projects = file_root / 'RE-Toolchain' / 'doctor'
    projects.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='run-', dir=projects) as directory, \
            tempfile.TemporaryDirectory(prefix='re-doctor-outside-') as denied:
        project = Path(directory)
        require(not Path(denied).resolve().is_relative_to(file_root), 'No out-of-root negative fixture available')
        profile = output / 'backend'
        profile.mkdir(mode=0o700)
        private = profile / 'ghidra-token'
        private.touch(mode=0o600)
        private.write_text(re_mcp.token())
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        settings = dict(settings, port=port, url='http://127.0.0.1:' + str(port))
        (profile / 'config.json').write_text(json.dumps(settings))
        (profile / 'config.json').chmod(0o600)
        env = dict(os.environ, RE_SETUP_HOME=str(profile))
        probe = project / 'probe'
        source = project / 'probe.c'
        source.write_text('int re_setup_probe(int value) { return value * 3 + 7; }\nint main(void) { return 0; }\n')
        subprocess.run(['clang', '-O0', '-g', str(source), '-o', str(probe)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            with Rpc([sys.executable, str(ROOT / 'tools/re_mcp.py'), 'ghidra'], output / 'ghidra.log', env=env) as rpc:
                rpc.initialize()
                exercise(rpc, project, Path(denied), probe, records)
                with (output / 'status.log').open('w') as log:
                    run = subprocess.run([sys.executable, str(ROOT / 'tools/re_mcp.py'), 'status'],
                                         env=env, stdout=log, stderr=subprocess.STDOUT)
                measured(records, 'authentication_and_identity',
                         lambda: require(run.returncode == 0, 'Isolated authentication/identity check failed'))
                call(rpc, 'close_project', {})
            python = str(Path(settings['ghidra']).parent / 'python/bin/python')
            command = [python, '-I', str(ROOT / 'tools/re_static_probe.py'), str(project)]
            if settings.get('settings_dir'):
                command += ['--settings-dir', settings['settings_dir']]
            utility_env = dict(env, JAVA_HOME=settings['java_home'], GHIDRA_INSTALL_DIR=settings['ghidra'])
            utility_env['PATH'] = settings['java_home'] + '/bin:' + utility_env.get('PATH', '')
            with (output / 'ee-rabbitizer.log').open('w') as log:
                run = subprocess.run(command, env=utility_env, stdout=log, stderr=subprocess.STDOUT, timeout=120)
            measured(records, 'pyghidra_ee_pcode',
                     lambda: require(run.returncode == 0, 'EE/rabbitizer control failed; inspect ee-rabbitizer.log'))
            records.append({'check': 'rabbitizer_r5900', 'successful': True})
        finally:
            with (output / 'stop.log').open('w') as log:
                subprocess.run([sys.executable, str(ROOT / 'tools/re_mcp.py'), 'stop'], env=env,
                               stdout=log, stderr=subprocess.STDOUT)
            private.unlink(missing_ok=True)


def discovery(output: Path) -> list[dict]:
    # Inspect only our three native registrations, never unrelated provider credentials.
    records = []
    for server, mode in [('ghidra', 'ghidra'), ('rea', 'rea'), ('radare2', 'r2')]:
        with Rpc([sys.executable, str(ROOT / 'tools/re_mcp.py'), mode], output / (server + '-discovery.log')) as rpc:
            rpc.initialize()
            tools = rpc.call('tools/list', {})['tools']
            require(bool(tools), 'Empty tool catalog: ' + server)
            records.append({'server': server, 'transport': 'shared stdio launcher', 'tool_count': len(tools),
                            'successful': True, 'native_client_discovery': 'not tested by this transport check'})
    return records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--discovery', action='store_true', help='Also initialize all three shared stdio launchers')
    args = parser.parse_args(argv)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = (args.output or ROOT / '.scratch/re-doctor' / stamp).resolve()
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    report = {'schema': 'fr2-re-doctor/v1', 'model_calls': 0, 'corpus_required': False,
              'backend': 'isolated synthetic project', 'controls': [], 'discovery': []}
    try:
        settings = re_mcp.config()
        re_mcp.validate_runtime(settings)
        require(shutil.which('clang') is not None, 'clang is required for the synthetic probe')
        isolated(settings, output, report['controls'])
        if args.discovery:
            report['discovery'] = discovery(output)
        report['successful'] = True
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        report.update(successful=False, error=str(error))
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'successful': report['successful'], 'controls': len(report['controls']),
                      'discovery': len(report['discovery']), 'report': str(output / 'result.json'),
                      'error': report.get('error')}))
    return 0 if report['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
