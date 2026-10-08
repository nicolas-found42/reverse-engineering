"""Bind the GNU substitution to exact Debian package members and source archives."""
from __future__ import annotations

import io
from pathlib import Path
import tarfile

from evidence_common import Incomplete, Invalid, identity, sha256


def ar_members(data: bytes) -> dict[str, bytes]:
    if not data.startswith(b'!<arch>\n'):
        raise Invalid('GNU tool package is not an ar archive')
    result = {}
    offset = 8
    while offset < len(data):
        header = data[offset:offset + 60]
        if len(header) != 60 or header[58:] != b'`\n':
            raise Invalid('GNU tool package ar header is malformed')
        try:
            size = int(header[48:58])
            name = header[:16].decode('ascii').strip().rstrip('/')
        except (ValueError, UnicodeDecodeError) as exc:
            raise Invalid('GNU tool package ar name/size is malformed') from exc
        if size < 0 or size > len(data) - offset - 60 or name in result:
            raise Invalid('GNU tool package ar member is truncated or duplicated')
        result[name] = data[offset + 60:offset + 60 + size]
        offset += 60 + size + (size % 2)
    if offset != len(data):
        raise Invalid('GNU tool package ar alignment is malformed')
    return result


def bind(tool_root: Path, decision: dict) -> dict:
    root = tool_root / 'gnu-linker-provenance'
    archives = {}
    missing = []
    for name, recorded in decision['archives'].items():
        path = root / name
        if not path.is_file():
            missing.append(name)
            continue
        if identity(path) != recorded['identity']:
            raise Invalid(f'GNU tool source/package archive identity differs: {name}')
        archives[name] = {'path': str(path), **recorded}
    if missing:
        raise Incomplete('GNU tool source/package archive is missing: ' + ', '.join(missing))
    package = root / decision['binary_package']
    members = ar_members(package.read_bytes())
    payloads = [v for k, v in members.items() if k.startswith('data.tar')]
    if len(payloads) != 1:
        raise Invalid('GNU tool binary package requires one data archive')
    payload = payloads[0]
    bindings = {}
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        for role, member in decision['package_members'].items():
            stream = archive.extractfile(member['path'])
            if stream is None:
                raise Invalid(f'GNU tool package member is missing: {role}')
            with stream:
                data = stream.read()
            observed = {'bytes': len(data), 'sha256': sha256(data)}
            if observed != member['identity']:
                raise Invalid(f'GNU tool package member identity differs: {role}')
            if role in decision['tool_files'] and observed != identity(tool_root / role):
                raise Invalid(f'GNU installed tool differs from package member: {role}')
            bindings[role] = {'member': member['path'], **observed}
    return {'archives': archives, 'package_members': bindings,
            'source_lineage': decision['source_lineage'],
            'build_disposition': 'Exact Debian binary/source binding; local rebuild of binutils was not executed.'}
