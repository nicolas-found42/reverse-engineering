#!/usr/bin/env python3
"""Report EE kernel syscall stubs and their candidate PS2SDK names.

Scans the executable for the four-word syscall stub shape, reads the number
table from the pinned PS2SDK `syscallnr.h`, and says which stubs are already
saved functions. Names are candidates from the public SDK; no original symbol,
BIOS behavior or game library version is established. No game code is run.
"""
import argparse
import json
from pathlib import Path

from evidence_common import write_result
from ps2_syscall_stubs import SDK_COMMIT, read_pinned_header, scan_stubs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--sdk-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/syscall-stubs'))
    args = parser.parse_args()

    def action() -> dict:
        header, sha = read_pinned_header(args.sdk_root)
        result = scan_stubs(args.executable.read_bytes(), json.loads(args.static_export.read_text()), header)
        return {**result, 'sdk': {'commit': SDK_COMMIT, 'header_sha256': sha}}
    return write_result(args.output, 'syscall-stubs', action, [args.static_export, args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
