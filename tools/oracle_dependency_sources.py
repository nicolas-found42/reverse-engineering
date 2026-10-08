#!/usr/bin/env python3
"""Audit fixed Qt source records and PCSX2 release members without execution.

This bounded inventory does not qualify the strict runtime profile, complete
dependency licensing, or bind a locally reproduced dependency build.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import tarfile

from evidence_common import Incomplete, Invalid, identity, write_result
from headless_oracle import PCSX2_SHA256, QT_RUNTIME_LIBRARIES, QT_SDK_ARCHIVE_SHA256

ARCHIVES = {
    'pcsx2-v2.6.3-macos-Qt.tar.xz': 'cb7b9e6330f1abf0cf92c94065f7eb983d0fa8affcfe6b0ccb9c2a4ebf067f1a',
    'qtbase-everywhere-src-6.10.1.tar.xz': '5a6226f7e23db51fdc3223121eba53f3f5447cf0cc4d6cb82a3a2df7a65d265d',
    'KDDockWidgets-2.4.0.tar.gz': '51dbf24fe72e43dd7cb9a289d3cab47112010f1a2ed69b6fc8ac0dff31991ed2',
    'build-dependencies.sh': 'ebc925a91219548efc62c4592ae5fe99490627895bb8d66e1260c668d8d44add',
}
SOURCE_RECORD = 'sbom/qtbase-6.10.1.source.spdx'
SOURCE_RECORD_SHA256 = '752bd3cfb0be50592437aa5b7fcaac6287618033f210032048e17b9734a0e825'
RELEASE_MEMBERS = {'Contents/MacOS/PCSX2': PCSX2_SHA256,
                   **{'Contents/Frameworks/' + name: digest
                      for name, digest in QT_RUNTIME_LIBRARIES.items()}}


def verify_source_records(record: bytes, source: Path) -> dict:
    """Compare every SPDX source SHA1; caller omissions cannot shrink the set."""
    entries = record.decode('utf-8').split('FileName: ')[1:]
    if not entries:
        raise Invalid('source SPDX has no file records')
    seen, checked, changed, missing = set(), 0, [], []
    root = source.resolve()
    for entry in entries:
        name = entry.splitlines()[0].removeprefix('./')
        checksum = re.search(r'^FileChecksum: SHA1: ([0-9a-f]{40})$', entry, re.MULTILINE)
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or '..' in path.parts or name in seen
                or checksum is None):
            raise Invalid('duplicate, malformed or escaping source SPDX record: ' + name)
        seen.add(name)
        candidate = root / name
        if not candidate.is_file():
            missing.append(name)
            continue
        if root not in candidate.resolve().parents:
            raise Invalid('source SPDX file escapes its declared root: ' + name)
        observed = hashlib.sha1(candidate.read_bytes()).hexdigest()
        checked += 1
        if observed != checksum.group(1):
            changed.append({'path': name, 'expected_sha1': checksum.group(1), 'observed_sha1': observed})
    details = {'required_files': len(seen), 'checked_files': checked,
               'changed': changed, 'missing': missing, 'matched_bytes': 0,
               'claim_limit': 'SPDX source-file inventory only; no dependency build or guest execution.'}
    if changed:
        raise Invalid('available source files differ from the fixed SDK source record', details)
    if missing:
        raise Incomplete('required SDK source records are absent', details)
    return details


def verify_release_members(archive: Path, app: Path) -> dict:
    observed, missing, changed = {}, [], []
    with tarfile.open(archive, 'r|xz') as package:
        for member in package:
            if not member.isfile() or 'Contents/' not in member.name:
                continue
            name = member.name[member.name.index('Contents/'):]
            if name not in RELEASE_MEMBERS:
                continue
            if name in observed:
                raise Invalid('duplicate required PCSX2 release member: ' + name)
            stream = package.extractfile(member)
            if stream is None:
                raise Invalid('required PCSX2 release member is unreadable: ' + name)
            digest = hashlib.sha256(stream.read()).hexdigest()
            installed = app / name
            actual = identity(installed) if installed.is_file() else None
            observed[name] = {'release_sha256': digest, 'installed': actual}
            if digest != RELEASE_MEMBERS[name] or (actual and actual['sha256'] != digest):
                changed.append(name)
            if actual is None:
                missing.append('installed ' + name)
    missing.extend('release ' + name for name in RELEASE_MEMBERS if name not in observed)
    details = {'members': observed, 'missing': missing, 'changed': changed}
    if changed:
        raise Invalid('available installed/release dependency identity differs', details)
    if missing:
        raise Incomplete('required installed/release dependency member is absent', details)
    return details


def check(evidence: Path, sdk: Path, sdk_archive: Path, app: Path) -> dict:
    pins = {**{evidence / name: digest for name, digest in ARCHIVES.items()},
            sdk / SOURCE_RECORD: SOURCE_RECORD_SHA256, sdk_archive: QT_SDK_ARCHIVE_SHA256,
            **{app / name: digest for name, digest in RELEASE_MEMBERS.items()}}
    missing, changed, identities = [], [], {}
    for path, digest in pins.items():
        if not path.is_file():
            missing.append(str(path))
            continue
        identities[str(path)] = identity(path)
        if identities[str(path)]['sha256'] != digest:
            changed.append(str(path))
    details = {'identities': identities, 'missing': missing, 'changed': changed}
    if changed:
        raise Invalid('available fixed dependency input identity differs', details)
    # Missing prerequisites in one inventory cannot suppress a contradiction
    # in another admitted, independently pinned inventory.
    branches = [
        ('release_binding', evidence / 'pcsx2-v2.6.3-macos-Qt.tar.xz',
         lambda: verify_release_members(evidence / 'pcsx2-v2.6.3-macos-Qt.tar.xz', app)),
        ('sdk_source_inventory', sdk / SOURCE_RECORD,
         lambda: verify_source_records((sdk / SOURCE_RECORD).read_bytes(), evidence / 'qtbase-git')),
    ]
    failures = []
    for name, prerequisite, action in branches:
        if not prerequisite.is_file():
            continue
        try:
            details[name] = action()
        except (Incomplete, Invalid) as exc:
            details[name] = exc.details
            if isinstance(exc, Invalid):
                failures.append(str(exc))
            else:
                missing.append(str(exc))
    if failures:
        raise Invalid('; '.join(failures), details)
    if missing:
        raise Incomplete('required fixed dependency input is absent', details)
    details.update(issue22_status='incomplete', matched_bytes=0,
                   scope='Pinned source record and official release-member inventory only',
                   remaining=['Complete installed dependency closure and component notices.',
                              'Bind exact dependency build provenance; no local dependency rebuild here.',
                              'Qualify strict window/display/audio/focus lifecycle separately.'])
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence_root', type=Path)
    parser.add_argument('sdk_root', type=Path)
    parser.add_argument('sdk_archive', type=Path)
    parser.add_argument('--app', type=Path, default=Path('/Applications/PCSX2.app'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    return write_result(args.output, 'oracle-dependency-source-inventory',
                        lambda: check(args.evidence_root, args.sdk_root, args.sdk_archive, args.app),
                        [Path(__file__), Path(__file__).with_name('headless_oracle.py'),
                         Path(__file__).with_name('evidence_common.py')])


if __name__ == '__main__':
    raise SystemExit(main())
