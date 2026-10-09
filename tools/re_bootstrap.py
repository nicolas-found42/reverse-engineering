#!/usr/bin/env python3
"""Build the pinned macOS ARM static toolchain beside the active installation, then verify before activation."""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import urllib.request
import zipfile

import re_mcp

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'tools/re_install_manifest.json'


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def unpack(archive: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as stream:
        for member in stream.infolist():
            path = destination / member.filename
            mode = member.external_attr >> 16
            if not path.resolve().is_relative_to(destination.resolve()) or mode & 0o170000 == 0o120000:
                raise ValueError('Unsafe extension/archive member')
            stream.extract(member, destination)
            if path.is_file() and mode & 0o111:
                path.chmod(0o755)


def fetch(asset: dict, destination: Path, cache: Path | None):
    path = destination / asset['file']
    cached = cache / asset['file'] if cache else None
    if not path.exists():
        if cached and cached.is_file():
            shutil.copyfile(cached, path)
        else:
            with urllib.request.urlopen(asset['url'], timeout=60) as source, path.open('wb') as target:
                shutil.copyfileobj(source, target)
    if digest(path) != asset['sha256']:
        raise ValueError('Distribution identity mismatch: ' + asset['file'])


class Build:
    def __init__(self, destination: Path, java_home: Path):
        self.root = destination
        self.env = dict(os.environ, JAVA_HOME=str(java_home))
        for key in ['DESTDIR', 'PREFIX', 'EPREFIX', 'SPREFIX', 'BINDIR', 'LIBDIR', 'INCLUDEDIR']:
            self.env.pop(key, None)
        self.env['PATH'] = str(java_home / 'bin') + ':' + self.env.get('PATH', '')
        self.number = 0

    def run(self, command, cwd=None):
        if command[0] == 'make' and 'install' in command:
            prefixes = [Path(str(x).split('=', 1)[1]).resolve() for x in command if str(x).startswith('PREFIX=')]
            if len(prefixes) != 1 or not prefixes[0].is_relative_to(self.root.resolve()):
                raise ValueError('Make installation requires an explicit candidate prefix')
        self.number += 1
        log = self.root / f'build-{self.number:03}.log'
        print('Build step ' + str(self.number) + ': ' + Path(command[0]).name, flush=True)
        with log.open('w') as stream:
            subprocess.run([str(x) for x in command], cwd=cwd or self.root, env=self.env,
                           stdout=stream, stderr=subprocess.STDOUT, check=True)


def prerequisites(java_home: Path | None):
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise ValueError('This pinned profile supports macOS ARM64 only')
    missing = [x for x in ['git', 'clang', 'cmake', 'make', 'mvn', 'pkg-config', 'uv', 'npx'] if not shutil.which(x)]
    if missing:
        raise ValueError('Missing build prerequisites: ' + ', '.join(missing))
    if java_home is None:
        prefix = subprocess.check_output(['brew', '--prefix', 'openjdk@21'], text=True).strip()
        java_home = Path(prefix) / 'libexec/openjdk.jdk/Contents/Home'
    result = subprocess.run([str(java_home / 'bin/java'), '-version'], capture_output=True, text=True, check=True)
    if not re.search(r'version "21\.', result.stderr):
        raise ValueError('Build requires Java 21; ambient newer Java is not selected')
    return java_home.resolve()


def clone(build: Build, name: str, source: dict, cache: Path | None):
    path = build.root / name
    cached = cache / name if cache else None
    # Existing source is cloned into a new checkout, never modified in place.
    remote = str(cached) if cached and (cached / '.git').exists() else source['url']
    build.run(['git', 'clone', '--no-hardlinks', remote, str(path)])
    build.run(['git', 'checkout', '--detach', source['commit']], cwd=path)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != source['commit']:
        raise ValueError('Source identity mismatch: ' + name)
    return path


def install(build: Build, manifest: dict, cache: Path | None):
    root = build.root
    for asset in manifest['assets']:
        fetch(asset, root, cache)
    unpack(root / 'ghidra.zip', root)
    ghidra = root / ('ghidra_' + manifest['versions']['ghidra'] + '_PUBLIC')
    for path in (ghidra / 'support').iterdir():
        if path.is_file() and (path.suffix == '.sh' or path.suffix == ''):
            path.chmod(0o755)
    build.run(['sh', './gradlew', 'buildNatives'], cwd=ghidra / 'support/gradle')
    extensions = ghidra / 'Ghidra/Extensions'
    unpack(root / 'ee.zip', extensions)
    sources = {name: clone(build, name, spec, cache) for name, spec in manifest['sources'].items()}
    bridge = sources['ghidra-mcp']
    patch = ROOT / 'tools/patches/ghidra-mcp-6.0.0-file-scope.patch'
    if digest(patch) != manifest['scope_patch_sha256']:
        raise ValueError('Reviewed scope patch changed')
    # Upstream uses CRLF; normalize only the patched file for the LF patch.
    java = bridge / 'src/main/java/com/xebyte/headless/HeadlessManagementService.java'
    java.write_bytes(java.read_bytes().replace(b'\r\n', b'\n'))
    build.run(['git', 'apply', '--check', str(patch)], cwd=bridge)
    build.run(['git', 'apply', str(patch)], cwd=bridge)
    setup = ast.parse((bridge / 'tools/setup/ghidra.py').read_text())
    jars = next(ast.literal_eval(x.value) for x in setup.body
                if isinstance(x, ast.AnnAssign) and isinstance(x.target, ast.Name) and x.target.id == 'REQUIRED_GHIDRA_JARS')
    for artifact, relative in jars:
        build.run(['mvn', '-B', '-q', 'install:install-file', '-Dfile=' + str(ghidra / relative),
                   '-DgroupId=ghidra', '-DartifactId=' + artifact, '-Dversion=' + manifest['versions']['ghidra'],
                   '-Dpackaging=jar', '-DgeneratePom=true'], cwd=bridge)
    build.run(['mvn', '-B', 'clean', 'package', 'assembly:single', '-DskipTests',
               '-Dghidra.version=' + manifest['versions']['ghidra']], cwd=bridge)
    unpack(bridge / 'target/GhidraMCP-6.0.0.zip', extensions)
    build.run(['uv', 'venv', '--python', sys.executable, str(root / 'python')])
    wheels = list((ghidra / 'Ghidra/Features/PyGhidra/pypkg/dist').glob('pyghidra-*.whl'))
    if len(wheels) != 1:
        raise ValueError('Expected one bundled PyGhidra wheel')
    build.run(['uv', 'pip', 'install', '--python', str(root / 'python/bin/python'),
               *manifest['python_packages'], str(wheels[0]), str(bridge)])
    ccc = sources['ccc']
    build.run(['cmake', '-S', str(ccc), '-B', str(ccc / 'build'), '-DCMAKE_BUILD_TYPE=Release'])
    build.run(['cmake', '--build', str(ccc / 'build'), '--parallel', '4'])
    build.run(['ctest', '--test-dir', str(ccc / 'build'), '--output-on-failure'])
    prefix = root / 'r2-install'
    for name in ['radare2', 'radare2-mcp']:
        path = sources[name]
        build.env['PKG_CONFIG_PATH'] = str(prefix / 'lib/pkgconfig')
        build.env['PATH'] = str(prefix / 'bin') + ':' + build.env['PATH']
        build.run(['./configure', '--prefix=' + str(prefix)], cwd=path)
        build.run(['make', '-j4'], cwd=path)
        # r2mcp's recursive Makefiles do not consume configure's prefix.
        build.run(['make', 'PREFIX=' + str(prefix), 'install'], cwd=path)
    (root / 'objdiff-cli').chmod(0o755)
    build.run([str(root / 'objdiff-cli'), '--version'])
    build.run([str(prefix / 'bin/r2'), '-n', '-N', '-v'])
    jar = extensions / 'GhidraMCP/lib/GhidraMCP-6.0.0.jar'
    return {'java_home': build.env['JAVA_HOME'], 'ghidra': str(ghidra),
            'bridge_root': str(bridge), 'bridge': str(root / 'python/bin/bridge-mcp-ghidra'),
            'npx': shutil.which('npx'), 'rea_version': manifest['versions']['rea'],
            'r2mcp': str(prefix / 'bin/r2mcp'), 'extension_jar': str(jar), 'extension_sha256': digest(jar),
            'settings_dir': str(root / 'runtime-settings'), 'file_root': str(Path.home() / 'Documents'),
            'port': 8090, 'url': 'http://127.0.0.1:8090', 'install_manifest_sha256': digest(MANIFEST)}


def private_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.new')
    with open(temporary, 'w', opener=lambda p, flags: os.open(p, flags, 0o600)) as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    temporary.chmod(0o600)
    os.replace(temporary, path)


def wrappers(directory: Path) -> dict[Path, str]:
    tools = {'objdiff-cli': 'objdiff', 'stdump': 'stdump', 'r2': 'r2', 'radare2': 'r2',
             're-python': 'python', 'pyghidra': 'pyghidra', 'rea': 'rea'}
    result = {}
    for name, tool in tools.items():
        command = [sys.executable, str(ROOT / 'tools/re_tool.py'), tool]
        result[directory / name] = '#!/bin/sh\n# Managed static RE utility wrapper\nexec ' + shlex.join(command) + ' "$@"\n'
    for name, script, arguments in [('re-doctor', 're_doctor.py', []),
                                    ('r2mcp', 're_mcp.py', ['r2'])]:
        result[directory / name] = '#!/bin/sh\n# Managed static RE utility wrapper\nexec ' + shlex.join(
            [sys.executable, str(ROOT / 'tools' / script), *arguments]) + ' "$@"\n'
    for path in result:
        if path.exists() and str(ROOT / 'tools/') not in path.read_text():
            raise ValueError('Refusing to replace an unrelated utility wrapper: ' + str(path))
    return result


def activate(settings: dict):
    local = ROOT / '.scratch/re-setup'
    config = local / 'config.json'
    old = json.loads(config.read_text()) if config.exists() else None
    if old and (local / 'backend.pid').exists():
        raise ValueError('Managed active backend is running; activation refuses to interrupt its project. Stop it after saving analysis.')
    managed_wrappers = wrappers(Path.home() / '.local/bin')
    if old:
        private_json(local / 'rollback-config.json', old)
    private_json(config, settings)
    try:
        re_mcp.validate_runtime(settings)
        subprocess.run([sys.executable, str(ROOT / 'tools/configure_re_clients.py')], check=True)
        for path, text in managed_wrappers.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + '.new')
            temporary.write_text(text)
            temporary.chmod(0o755)
            os.replace(temporary, path)
    except Exception:
        if old:
            private_json(config, old)
        else:
            config.unlink()
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Build a new candidate; default prints the plan')
    parser.add_argument('--activate', action='store_true', help='Switch shared config only after successful doctor')
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--cache', type=Path, help='Reuse verified downloads and clone source caches')
    parser.add_argument('--java-home', type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads(MANIFEST.read_text())
    if args.activate and not args.apply:
        parser.error('--activate requires --apply')
    if not args.apply:
        print(json.dumps({'manifest_sha256': digest(MANIFEST), 'profile': manifest['platform'],
                          'versions': manifest['versions'], 'steps': ['check prerequisites', 'verify distributions and sources',
                          'build native components and scoped bridge', 'build isolated utilities', 'run synthetic doctor',
                          'optional activation with rollback configuration']}, indent=2))
        return 0
    java_home = prerequisites(args.java_home)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    destination = (args.destination or ROOT / '.scratch/re-installs' / stamp).resolve()
    if destination.exists():
        raise ValueError('Build destination already exists; previous installations are retained')
    destination.mkdir(parents=True)
    report = {'schema': 'fr2-bootstrap/v1', 'manifest_sha256': digest(MANIFEST), 'successful': False, 'activated': False}
    try:
        settings = install(Build(destination, java_home), manifest, args.cache.resolve() if args.cache else None)
        profile = destination / 'candidate'
        private_json(profile / 'config.json', settings)
        token = profile / 'ghidra-token'
        token.touch(mode=0o600)
        token.write_text(re_mcp.token() if (re_mcp.LOCAL / 'ghidra-token').exists() else secrets.token_urlsafe(48))
        env = dict(os.environ, RE_SETUP_HOME=str(profile))
        subprocess.run([sys.executable, str(ROOT / 'tools/re_doctor.py'), '--discovery',
                        '--output', str(destination / 'doctor')], env=env, check=True)
        report['successful'] = True
        if args.activate:
            local = ROOT / '.scratch/re-setup'
            if not (local / 'ghidra-token').exists():
                local.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(token, local / 'ghidra-token')
                (local / 'ghidra-token').chmod(0o600)
            activate(settings)
            report['activated'] = True
        token.unlink()
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        report.update(successful=False, error=str(error))
    finally:
        (destination / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(report, installation=str(destination))))
    return 0 if report['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
