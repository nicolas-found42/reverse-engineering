#!/usr/bin/env python3
"""Find Sony SDK library version stamps in the executable and IOP modules.

Sony SDK libraries embed `PsII`, an eight-character library name padded with
spaces and four decimal digits (for example `PsIIlibkernl2550`). The stamps
date the SDK libraries a file was linked with; they do not identify the game's
own compiler and are not symbols for any function. Nothing is executed.
"""
import argparse
import hashlib
import re
from pathlib import Path

from evidence_common import Incomplete, write_result

STAMP = re.compile(rb'PsII([a-z0-9 ]{8})([0-9]{4})')


def find_stamps(data: bytes) -> list[dict]:
    return [{'offset': m.start(), 'library': m[1].decode().strip(), 'version': m[2].decode()}
            for m in STAMP.finditer(data)]


def scan_files(paths: list[Path]) -> dict:
    files, libraries = [], {}
    for path in paths:
        data = path.read_bytes()
        stamps = find_stamps(data)
        files.append({'path': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                      'stamps': stamps})
        for stamp in stamps:
            versions = libraries.setdefault(stamp['library'], [])
            if stamp['version'] not in versions:
                versions.append(stamp['version'])
    return {'files_scanned': len(files), 'files_with_stamps': sum(bool(f['stamps']) for f in files),
            'libraries': {k: sorted(v) for k, v in sorted(libraries.items())}, 'files': files,
            'claim_limits': ['Stamps date SDK libraries, not the game compiler or any function identity.',
                             'A file without a stamp is not shown to lack the library.',
                             'The mapping from a stamp to a named SDK release is community knowledge, not established here.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/sdk-stamps'))
    args = parser.parse_args()

    def action() -> dict:
        result = scan_files(args.files)
        if not result['files_with_stamps']:
            raise Incomplete('no SDK stamp was found in the supplied files', result)
        return result
    return write_result(args.output, 'sdk-stamps', action, args.files)


if __name__ == '__main__':
    raise SystemExit(main())
