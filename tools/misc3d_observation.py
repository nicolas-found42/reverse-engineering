#!/usr/bin/env python3
"""Bind a saved-project inventory to retail words and retain misc3d metadata only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf

CELL = 0x290AC4
GP = 0x295D70


def observe(data: bytes, inventory: dict) -> dict:
    if inventory.get('executable_sha256') != sha256(data):
        raise Invalid('saved-project executable identity differs')
    elf = parse_elf(data)
    sections = [s for s in elf['sections'] if s['type'] != 8 and s['size']]

    def payload(start: int, size: int) -> bytes:
        owners = [s for s in sections if s['address'] <= start
                  and start + size <= s['address'] + s['size']]
        if len(owners) != 1:
            raise Invalid(f'nonunique file-backed span at {start:08x}')
        offset = owners[0]['offset'] + start - owners[0]['address']
        return data[offset:offset + size]

    owners: dict[int, list[str]] = {}
    functions = inventory.get('functions')
    if not isinstance(functions, list) or not functions:
        raise Incomplete('saved-project function inventory is missing')
    # Check actual words before retaining any function ownership or call metadata.
    for function in functions:
        for instruction in function['instructions']:
            site = int(instruction['address'], 16)
            if bytes.fromhex(instruction['bytes']) != payload(site, 4):
                raise Invalid(f'saved instruction differs from retail at {site:08x}')
            owners.setdefault(site, []).append(function['entry'])

    accesses, address_materializations, pointers = [], [], []
    for section in sections:
        if not section['flags'] & 2:
            continue
        for offset in range(0, section['size'] - 3, 4):
            site = section['address'] + offset
            word = struct.unpack_from('<I', data, section['offset'] + offset)[0]
            if word == CELL:
                pointers.append(f'{site:08x}')
            if not section['flags'] & 4:
                continue
            opcode, base = word >> 26, (word >> 21) & 31
            if base == 28 and word & 0xffff == (CELL - GP) & 0xffff:
                if opcode not in (0x23, 0x2b):
                    address_materializations.append(f'{site:08x}')
                else:
                    accesses.append({'site': f'{site:08x}',
                                     'kind': 'load' if opcode == 0x23 else 'store',
                                     'width': 4, 'register': (word >> 16) & 31,
                                     'saved_owners': owners.get(site, []),
                                     'word_sha256': sha256(payload(site, 4))})
    callers = []
    for function in functions:
        for instruction in function['instructions']:
            if any(r['to'] == '001d1800' and r['type'] == 'UNCONDITIONAL_CALL'
                   for r in instruction['references']):
                site = int(instruction['address'], 16)
                word = int.from_bytes(payload(site, 4), 'little')
                if word >> 26 != 3 or ((site + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2) != 0x1d1800:
                    raise Invalid('accessor caller reference differs from raw JAL')
                callers.append({'entry': function['entry'], 'site': f'{site:08x}',
                                'window_sha256': sha256(payload(site, 24))})
    spans = {}
    for name, start, end in (
        ('startup_zero_and_gp', 0x10011c, 0x100174),
        ('reset', 0x1d17a8, 0x1d17c4), ('release', 0x1d17c8, 0x1d1800),
        ('accessor', 0x1d1800, 0x1d183c), ('helper', 0x105888, 0x105ac4),
        ('reset_before_load', 0x1ccc3c, 0x1ccc54),
        ('load_store', 0x1d1440, 0x1d1464),
    ):
        spans[name] = {'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                       'bytes': end - start, 'sha256': sha256(payload(start, end - start))}
    return {'executable_sha256': sha256(data),
            'language': inventory.get('language'), 'ghidra_version': inventory.get('ghidra_version'),
            'gp': f'{GP:08x}', 'cell': f'{CELL:08x}',
            'cell_accesses': accesses, 'gp_address_materializations': address_materializations,
            'aligned_literal_pointers': pointers, 'accessor_callers': callers, 'spans': spans,
            'search_boundary': 'All aligned file-backed SHF_ALLOC words; GP displacement scan in SHF_EXECINSTR sections. Saved instruction bytes rechecked against ELF.',
            'limitations': ['Not an alias analysis; computed pointers and unaligned literals are not exhaustively resolved.',
                            'Saved boundaries remain provisional. The unowned load at 001d1840 is retained.',
                            'Static instructions establish paths, not runtime reachability or thread safety.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/misc3d-observation'))
    args = parser.parse_args()

    def action():
        corpus_identity(args.game)
        data = (args.game / 'extracted/SLES_517.05').read_bytes()
        if sha256(data) != EE_CORPUS_SHA256:
            raise Invalid('misc3d observation requires the recorded executable')
        result = observe(data, json.loads(args.inventory.read_text()))
        result['saved_inventory'] = identity(args.inventory)
        return result

    return write_result(args.output, 'misc3d-observation', action,
                        [args.inventory, Path(__file__), args.game / 'extracted/SLES_517.05'])


if __name__ == '__main__':
    raise SystemExit(main())
