#!/usr/bin/env python3
"""Build the function annotation plan from measured evidence.

Each entry is a plate comment for one saved function and, for kernel syscall
stubs with exactly one meaningful SDK name, a candidate rename. Comments say
how the evidence was obtained and that it is not proof; a renamed function
keeps the `ps2sdk_` prefix so a candidate name is never mistaken for an
original symbol. The plan is data for a guarded Ghidra transaction; nothing is
applied here and no game code is run.
"""
import argparse
import collections
import json
import re
from pathlib import Path

PLACEHOLDER = re.compile(r'RFU[0-9]+$')
PREFIX = 'ps2sdk_'


def build_plan(source_map: dict, stubs: dict, executable_sha256: str) -> dict:
    comments: dict[str, list[str]] = {}
    renames: dict[str, str] = {}
    for file in source_map['files']:
        if file['kind'] != 'unit':
            continue
        for function in file['functions']:
            lines = ', '.join(str(n) for n in function['lines'])
            where = f"{file['path']}:{lines}" if lines else file['path']
            comments.setdefault(function['entry'], []).append(
                f'source file (direct reference to its __FILE__ string, not proof of authorship): {where}')
    for row in source_map['string_attribution']['functions']:
        comments.setdefault(row['entry'], []).append(
            f"source file (string position, lower evidence than a direct reference): {row['unit']}")
    for stub in stubs['stubs']:
        if stub['ownership'] != 'saved_function' or not stub['names']:
            continue
        entry = stub['address']
        names = stub['names']
        comments.setdefault(entry, []).append(
            f"SDK syscall candidate (PS2SDK syscallnr.h, number {stub['number']}): {' / '.join(names)}; "
            'not a verified original symbol.')
        if len(names) == 1 and not PLACEHOLDER.match(names[0]):
            renames[entry] = PREFIX + names[0]
    taken = collections.Counter(renames.values())
    renames = {entry: name for entry, name in renames.items() if taken[name] == 1}
    entries = []
    for entry in sorted(comments):
        row = {'entry': entry, 'comment': '\n'.join(comments[entry])}
        if entry in renames:
            row['rename'] = renames[entry]
        entries.append(row)
    return {'schema_version': 1, 'executable_sha256': executable_sha256, 'entries': entries,
            'counts': {'entries': len(entries), 'renames': len(renames), 'comments': len(entries)},
            'claim_limits': ['Comments and names are candidates from references, string positions and public SDK tables.',
                             'No original function name, identity or behavior is claimed.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-map', type=Path, required=True, help='verify_source_map result.json')
    parser.add_argument('--syscall-stubs', type=Path, required=True, help='verify_syscall_stubs result.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source_map = json.loads(args.source_map.read_text())
    stubs = json.loads(args.syscall_stubs.read_text())
    plan = build_plan(source_map['details'], stubs['details'], stubs['details']['executable_sha256'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=1) + '\n')
    print(json.dumps(plan['counts']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
