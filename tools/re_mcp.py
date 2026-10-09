#!/usr/bin/env python3
"""Launch the local, pinned RE MCP servers using ignored machine configuration.

No token is stored in client JSON/TOML or passed on a command line. Ghidra uses
an authenticated loopback backend; r2mcp uses sandboxed read-only stdio. This
launcher does not open a corpus, execute a target, or install a login service.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / '.scratch/re-setup'
SCOPE_PATCH_SHA256 = '57759d2350f3b2cd98725339cb905daf7ea5c76e37ba6abba44d6189880df9fb'


def config() -> dict:
    return json.loads((LOCAL / 'config.json').read_text())


def token() -> str:
    path = LOCAL / 'ghidra-token'
    if path.stat().st_mode & 0o077:
        raise RuntimeError('Ghidra token file must be private (mode 0600)')
    value = path.read_text().strip()
    if len(value) < 32:
        raise RuntimeError('Ghidra token is missing or malformed')
    return value


def backend_env(settings: dict) -> dict:
    env = dict(os.environ)
    env.update(JAVA_HOME=settings['java_home'], GHIDRA_INSTALL_DIR=settings['ghidra'],
               GHIDRA_MCP_AUTH_TOKEN=token(), GHIDRA_MCP_ALLOW_SCRIPTS='0',
               GHIDRA_MCP_FILE_ROOT=settings['file_root'], GHIDRA_MCP_PROJECT_FOLDER='/',
               GHIDRA_MCP_REQUIRE_PROGRAM_SELECTORS='1', GHIDRA_MCP_URL=settings['url'])
    env['PATH'] = settings['java_home'] + '/bin:' + env.get('PATH', '')
    return env


def request(path: str, *, authenticated: bool = True) -> bytes:
    settings = config()
    headers = {'Authorization': 'Bearer ' + token()} if authenticated else {}
    req = urllib.request.Request(settings['url'] + path, headers=headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.read()


def health() -> bool:
    try:
        return b'Headless' in request('/check_connection')
    except (OSError, urllib.error.URLError):
        return False


def validate_runtime(settings: dict) -> None:
    patch = ROOT / 'tools/patches/ghidra-mcp-6.0.0-file-scope.patch'
    if hashlib.sha256(patch.read_bytes()).hexdigest() != SCOPE_PATCH_SHA256:
        raise RuntimeError('Reviewed Ghidra file-scope patch identity changed')
    if not settings.get('extension_jar') or not settings.get('extension_sha256'):
        raise RuntimeError('Installed scoped Ghidra extension identity is missing')
    jar = Path(settings['extension_jar'])
    if not jar.is_file() or hashlib.sha256(jar.read_bytes()).hexdigest() != settings['extension_sha256']:
        raise RuntimeError('Installed scoped Ghidra extension identity changed')


def start() -> None:
    settings = config()
    validate_runtime(settings)
    LOCAL.mkdir(parents=True, exist_ok=True)
    with (LOCAL / 'backend.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if health():
            # Health is exempt from upstream authentication, so test schema too.
            request('/mcp/schema')
            try:
                request('/mcp/schema', authenticated=False)
            except urllib.error.HTTPError as error:
                if error.code == 401:
                    return
                raise
            raise RuntimeError('Existing backend does not enforce token authentication')
        with (LOCAL / 'backend.log').open('a') as log:
            proc = subprocess.Popen([
                str(Path(settings['ghidra']) / 'support/launch.sh'), 'fg', 'jdk',
                'GhidraMCP', '4G', '-Djava.awt.headless=true',
                'com.xebyte.headless.GhidraMCPHeadlessServer', '--bind', '127.0.0.1',
                '--port', str(settings['port'])], cwd=settings['bridge_root'],
                env=backend_env(settings), stdin=subprocess.DEVNULL, stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True)
        (LOCAL / 'backend.pid').write_text(str(proc.pid))
        for _ in range(90):
            if proc.poll() is not None:
                raise RuntimeError('Ghidra backend exited; inspect ignored backend.log')
            if health():
                request('/mcp/schema')
                return
            time.sleep(1)
        raise RuntimeError('Ghidra backend startup timed out')


def stop() -> None:
    with (LOCAL / 'backend.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        pid_file = LOCAL / 'backend.pid'
        if not pid_file.exists():
            return
        pid = int(pid_file.read_text())
        args = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'args='],
                              capture_output=True, text=True, check=True).stdout
        if 'GhidraMCPHeadlessServer' not in args or 'launch.sh' not in args:
            raise RuntimeError('Saved backend PID does not identify our launcher')
        os.killpg(pid, signal.SIGTERM)
        pid_file.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('server', choices=('ghidra', 'rea', 'r2', 'status', 'stop'))
    args = parser.parse_args()
    settings = config()
    if args.server == 'status':
        print(json.dumps({'healthy': health(), 'url': settings['url'],
                          'ghidra': settings['ghidra'], 'scripts_allowed': False}))
        return
    if args.server == 'stop':
        stop()
        return
    if args.server == 'ghidra':
        start()
        executable = settings['bridge']
        os.execve(executable, [executable, '--transport', 'stdio', '--no-lazy'],
                  backend_env(settings))
    if args.server == 'rea':
        # REA starts its own static providers; it does not need the Ghidra MCP token.
        env = dict(os.environ, JAVA_HOME=settings['java_home'],
                   GHIDRA_INSTALL_DIR=settings['ghidra'])
        os.execve(settings['npx'], [settings['npx'], '-y', 'rea-agents@' + settings['rea_version'], 'mcp'], env)
    env = dict(os.environ)
    env['PATH'] = str(Path(settings['r2mcp']).parent) + ':' + env.get('PATH', '')
    env['DYLD_LIBRARY_PATH'] = str(Path(settings['r2mcp']).parent.parent / 'lib')
    executable = settings['r2mcp']
    os.execve(executable, [executable, '-n', '-N', '-R', '-s', settings['file_root']], env)


if __name__ == '__main__':
    main()
