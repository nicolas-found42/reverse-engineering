#!/usr/bin/env python3
"""Recheck fixed loader static/source contracts without granting missing ownership."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf

ROOT = Path(__file__).resolve().parent.parent
DECISION = ROOT / 'notes/evidence/fr2-misc3d-loader/decision.json'
SOURCE = ROOT / 'reconstruction/ee/app3d/misc3d_loader.c'
HEADER = SOURCE.with_suffix('.h')
TERMINAL_SOURCE = SOURCE.with_name('misc3d_loader_terminal.c')
HARNESS = ROOT / 'tools/misc3d_loader_recipe/host_contract.c'
SCRIPT = ROOT / 'tools/misc3d_loader_recipe/InspectMisc3dLoader.java'
GP = 0x295d70
CELLS = tuple(range(0x290ac4, 0x290ad8, 4))
TARGETS = (0x1d1408, 0x11ed90, 0x124f58, 0x125068)
LOADER_RANGES = ((0x12c218, 0x12c220), (0x1d1408, 0x1d143c),
                 (0x1d1440, 0x1d157c), (0x1d1580, 0x1d15b4),
                 (0x1d15b8, 0x1d15cc), (0x1d15d0, 0x1d1628))
REQUIRED_UNKNOWN = ('computed-alias-closure', 'sibling-consumer-use',
                    'new-range-ownership', 'retail-loader-source-output')


def ranges(addresses: list[int]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for address in sorted(addresses):
        if result and result[-1][1] == address:
            result[-1] = (result[-1][0], address + 4)
        else:
            result.append((address, address + 4))
    return result


def observe(data: bytes, inventory: dict, isolated: dict) -> dict:
    """Exact saved-body reconciliation; absence in the scan is bounded."""
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('loader observation requires the unchanged recorded executable')
    if any(record.get('executable_sha256') != EE_CORPUS_SHA256
           or record.get('language') != 'r5900:LE:32:default'
           for record in (inventory, isolated)):
        raise Invalid('saved or isolated executable/language identity differs')
    sections = [s for s in parse_elf(data)['sections'] if s['type'] != 8 and s['flags'] & 2]

    def payload(start: int, size: int) -> bytes:
        owners = [s for s in sections if s['address'] <= start
                  and start + size <= s['address'] + s['size']]
        if len(owners) != 1:
            raise Invalid('loader span lacks unique allocated file storage')
        offset = owners[0]['offset'] + start - owners[0]['address']
        return data[offset:offset + size]

    functions = {f['entry']: f for f in inventory.get('functions', [])}
    isolated_functions = {f['entry']: f for f in isolated.get('functions', [])}
    missing, spans = [], {}
    for entry in TARGETS:
        name = f'{entry:08x}'
        function, fresh = functions.get(name), isolated_functions.get(name)
        if function is None or fresh is None:
            missing.append('required saved/isolated function missing: ' + name)
            continue
        addresses = []
        for instruction in function['instructions']:
            site = int(instruction['address'], 16)
            if bytes.fromhex(instruction['bytes']) != payload(site, 4):
                raise Invalid(f'saved loader/dependency instruction differs at {site:08x}')
            addresses.append(site)
        body = ranges(addresses)
        if len(set(addresses)) != len(addresses):
            raise Invalid('saved function has duplicate instruction ownership')
        saved_ranges = [{'start': f'{a:08x}', 'end_exclusive': f'{b:08x}'} for a, b in body]
        if fresh['ranges'] != saved_ranges or fresh['bytes'] != function['size'] or function['size'] != len(addresses) * 4:
            raise Invalid('isolated function body differs from retained exact instructions')
        if entry == 0x1d1408 and tuple(body) != LOADER_RANGES:
            raise Invalid('loader complete noncontiguous body differs')
        spans[name] = [{'start': f'{a:08x}', 'end_exclusive': f'{b:08x}', 'bytes': b-a,
                        'sha256': sha256(payload(a, b-a))} for a, b in body]
        raw_calls = []
        for section in sections:
            if not section['flags'] & 4:
                continue
            for offset in range(0, section['size'] - 3, 4):
                site = section['address'] + offset
                word = struct.unpack_from('<I', data, section['offset'] + offset)[0]
                target = ((site+4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
                if word >> 26 == 3 and target == entry:
                    raw_calls.append(f'{site:08x}')
        observed_calls = [r['from'] for r in fresh['incoming'] if r['type'] == 'UNCONDITIONAL_CALL']
        if sorted(raw_calls) != sorted(observed_calls):
            raise Invalid('saved incoming calls differ from raw allocated executable JAL domain')
        for row in fresh['incoming']:
            if row['type'] != 'UNCONDITIONAL_CALL':
                missing.append('unresolved saved non-JAL incoming reference: ' + str(row))
    accesses, materializations, literals = [], [], []
    for section in sections:
        for offset in range(0, section['size'] - 3, 4):
            site = section['address'] + offset
            word = struct.unpack_from('<I', data, section['offset'] + offset)[0]
            if word in CELLS:
                literals.append({'site': f'{site:08x}', 'cell': f'{word:08x}'})
            if not section['flags'] & 4:
                continue
            op, base = word >> 26, (word >> 21) & 31
            displacement = (word & 0xffff) - (0x10000 if word & 0x8000 else 0)
            cell = GP + displacement
            if base == 28 and cell in CELLS:
                row = {'site': f'{site:08x}', 'cell': f'{cell:08x}', 'opcode': op,
                       'register': (word >> 16) & 31, 'word_sha256': sha256(payload(site, 4))}
                if op in (0x23, 0x2b):
                    row['kind'] = 'load' if op == 0x23 else 'store'
                    accesses.append(row)
                else:
                    materializations.append(row)
    loader_stores = [row for row in accesses if row['kind'] == 'store'
                     and any(a <= int(row['site'], 16) < b for a, b in LOADER_RANGES)]
    expected_stores = [('001d1460', '00290ac4'), ('001d14a4', '00290acc'),
                       ('001d14b8', '00290ac8'), ('001d14cc', '00290ad0'),
                       ('001d14d4', '00290ad4')]
    if [(row['site'], row['cell']) for row in loader_stores] != expected_stores:
        raise Invalid('loader five-cell result stores differ from fixed call/dataflow contract')
    result = {'bounded_static_status': 'pass', 'body_ranges': spans,
              'isolated_incoming': {name: row['incoming'] for name, row in isolated_functions.items()},
              'cell_accesses': accesses, 'gp_materializations': materializations, 'aligned_literals': literals,
              'dependency_abi': {'entry': '0011ed90', 'input': 'A0 name pointer preserved in S0 at 0011ed98.',
                                 'return': 'V0 low word is stored to GP id cell at 001205d0 and returned at 001205d4; loader consumes low word at 001d1460.',
                                 'original_declaration': 'unknown; decompiler void is not a return-value proof'},
              'remote_terminal': {'start': '0012c218', 'bytes': 8, 'effect': 'Return with A0 stored to GP-relative cell 0028f23c in delay slot.', 'ownership': 'unresolved'},
              'new_attributed_match_bytes': 0, 'matched_nobits_file_bytes': 0,
              'search_boundary': 'All aligned SHF_ALLOC file words; direct JAL incoming domain; fixed-GP-offset LW/SW and other opcode candidates. No computed-alias closure or execution.'}
    if missing:
        raise Incomplete('; '.join(missing), result)
    return result


def source_contract(output: Path, source: Path = SOURCE) -> dict:
    """Diagnostic seam; alternate source only for real negative controls."""
    compiler = shutil.which('clang')
    if compiler is None:
        raise Incomplete('host source contract requires installed clang')
    output.mkdir(parents=True, exist_ok=True)
    binary = output / 'loader-host-contract'
    argv = [compiler, '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(HEADER.parent),
            str(source), str(TERMINAL_SOURCE), str(HARNESS), '-o', str(binary)]
    try:
        compiled = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Incomplete('host compiler execution unavailable', {'argv':argv, 'reason':str(error)}) from error
    if compiled.returncode:
        raise Invalid('host source contract compilation failed', {'argv': argv, 'stderr': compiled.stderr})
    try:
        executed = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Incomplete('host contract execution unavailable', {'reason':str(error)}) from error
    record = {'scope': 'Synthetic services executing hand-written source; no retail execution/byte equivalence.',
              'argv': argv, 'compiler': identity(Path(compiler)), 'source': identity(source),
              'header': identity(HEADER), 'terminal_source': identity(TERMINAL_SOURCE), 'harness': identity(HARNESS), 'binary': identity(binary),
              'exit_code': executed.returncode, 'stdout': executed.stdout, 'stderr': executed.stderr}
    if executed.returncode:
        raise Invalid('host source call/state contract failed', record)
    return record


def check(game: Path, inventory_path: Path, isolated_path: Path, output: Path) -> dict:
    """Available contradictions outrank missing provenance and required gaps."""
    missing, result = [], {}
    executable = game / 'extracted/SLES_517.05'
    data = executable.read_bytes() if executable.is_file() else None
    if data is not None and sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('loader child executable identity differs')
    if data is None:
        missing.append('required retail executable is absent')
    inputs = {'inventory': inventory_path, 'isolated': isolated_path,
              'source': SOURCE, 'header': HEADER, 'terminal_source': TERMINAL_SOURCE,
              'harness': HARNESS, 'script': SCRIPT}
    if not DECISION.is_file():
        missing.append('loader recorded decision is absent')
        decision = None
    else:
        decision = json.loads(DECISION.read_text())
        if decision.get('corpus_sha256') != EE_CORPUS_SHA256:
            raise Invalid('loader decision corpus differs')
        if decision.get('required_unknown') != list(REQUIRED_UNKNOWN):
            raise Invalid('loader required frontier differs from fixed checker scope')
    for name, path in inputs.items():
        if not path.is_file():
            missing.append('required loader input absent: ' + name)
        elif decision is not None and identity(path) != decision['inputs'][name]:
            raise Invalid('loader input identity differs from recorded decision: ' + name)
    if data is not None and inventory_path.is_file() and isolated_path.is_file():
        try:
            result['observation'] = observe(data, json.loads(inventory_path.read_text()), json.loads(isolated_path.read_text()))
        except Incomplete as error:
            missing.append(str(error))
            result['observation'] = error.details
    if all(path.is_file() for path in (SOURCE, HEADER, TERMINAL_SOURCE, HARNESS)):
        result['source_contract'] = source_contract(output)
    result.update({'issue37_status': 'incomplete', 'issue35_status': 'incomplete',
                   'issue24_status': 'incomplete', 'required_unknown': list(REQUIRED_UNKNOWN),
                   'new_attributed_match_bytes': 0})
    raise Incomplete('; '.join(missing + ['required loader/alias frontier remains unresolved']), result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('isolated', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    temp = tempfile.mkdtemp(prefix='private-source-', dir=args.output)
    return write_result(args.output, 'misc3d-loader',
                            lambda: check(args.game, args.inventory, args.isolated, Path(temp)),
                            [p for p in (Path(__file__), DECISION, SOURCE, HEADER, TERMINAL_SOURCE, HARNESS, SCRIPT,
                                         args.inventory, args.isolated, args.game/'extracted/SLES_517.05') if p.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
