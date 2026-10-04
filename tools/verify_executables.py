#!/usr/bin/env python3
"""Inventory bounded ELF/ROMDIR headers in a local extracted PS2 disc tree."""
import argparse
import hashlib
import mmap
from pathlib import Path

from evidence_common import Incomplete, write_result
from ps2_executables import parse_elf, parse_romdir


def inventory(root: Path) -> dict:
    if not root.is_dir():
        raise Incomplete(f'extracted root is missing: {root}')
    files, executables, unknown = [], [], []
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        digest = hashlib.sha256()
        size = path.stat().st_size
        offsets = []
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
            if size:
                with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
                    start = 0
                    while True:
                        at = mapped.find(b'\x7fELF', start)
                        if at < 0:
                            break
                        offsets.append(at)
                        start = at + 4
        relative = path.relative_to(root).as_posix()
        file_info = {'path': relative, 'bytes': size, 'sha256': digest.hexdigest(),
                     'elf_magic_offsets': offsets}
        files.append(file_info)
        if not offsets:
            continue
        with path.open('rb') as stream:
            prefix = stream.read(16)
        if prefix.startswith(b'RESET\0'):
            container = parse_romdir(path.read_bytes())
            known = [row['offset'] for row in container['modules']]
            executables.extend({'container': relative, **row} for row in container['modules'])
        elif prefix.startswith(b'\x7fELF'):
            executables.append({'container': relative, 'name': path.name, 'offset': 0,
                                'bytes': size, 'sha256': digest.hexdigest(),
                                'elf': parse_elf(path.read_bytes())})
            known = [0]
        else:
            known = []
        unknown.extend({'path': relative, 'offset': at}
                       for at in offsets if at not in known)
    details = {'file_count': len(files), 'files': files, 'executable_count': len(executables),
               'executables': executables, 'unclassified_elf_magic': unknown,
               'claim_limits': ['ELF/ROMDIR header and payload bounds only.',
                                'Raw overlays, packed code and VU programs are not discovered by ELF magic.',
                                'No relocation, function discovery or behavioral equivalence is established.']}
    if unknown:
        raise Incomplete('ELF magic candidates remain unclassified', details)
    if not executables:
        raise Incomplete('no supported ELF executables were found', details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    return write_result(args.output, 'executables', lambda: inventory(args.root), [])


if __name__ == '__main__':
    raise SystemExit(main())
