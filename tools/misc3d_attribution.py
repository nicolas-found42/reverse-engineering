#!/usr/bin/env python3
"""Revalidate bounded misc3d main-range, independent caller and external-leaf evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT/'notes/evidence/fr2-misc3d-loader/loader-attribution-candidate.json'
MAIN_RANGES = ((0x1d1408, 0x1d143c), (0x1d1440, 0x1d157c), (0x1d1580, 0x1d15b4),
               (0x1d15b8, 0x1d15cc), (0x1d15d0, 0x1d1628))


def check(data: bytes, inventory_path: Path) -> dict:
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('misc3d attribution requires the unchanged recorded executable')
    if not CONTRACT.is_file():
        raise Incomplete('misc3d attribution recorded evidence is absent')
    contract = json.loads(CONTRACT.read_text())
    if contract['corpus_sha256'] != EE_CORPUS_SHA256:
        raise Invalid('misc3d attribution evidence records another corpus')
    ranges = contract['candidate_main_ranges']
    if tuple((int(r['start'], 16), int(r['end_exclusive'], 16)) for r in ranges) != MAIN_RANGES:
        raise Invalid('misc3d main-range evidence changes the fixed boundary')
    sections = [s for s in parse_elf(data)['sections'] if s['type'] != 8 and s['flags'] & 2]
    missing = []

    def raw(address: int, size: int) -> bytes | None:
        owners = [s for s in sections if s['address'] <= address and address + size <= s['address'] + s['size']]
        if not owners:
            missing.append(f'required attribution storage absent: {address:08x}')
            return None
        if len(owners) != 1:
            raise Invalid(f'attribution storage ambiguous: {address:08x}')
        offset = owners[0]['offset'] + address - owners[0]['address']
        value = data[offset:offset + size]
        if len(value) != size:
            raise Invalid('attribution storage truncated')
        return value

    def bound_word(address: str, digest: str) -> int | None:
        value = raw(int(address, 16), 4)
        if value is None:
            return None
        if sha256(value) != digest:
            raise Invalid('attribution instruction contradicts recorded identity: ' + address)
        return struct.unpack('<I', value)[0]

    for span in ranges + [contract['remote_terminal']['range']]:
        start, end = int(span['start'], 16), int(span['end_exclusive'], 16)
        value = raw(start, end - start)
        if end - start != span['bytes'] or value is not None and sha256(value) != span['sha256']:
            raise Invalid('attribution range contradicts recorded identity: ' + span['start'])
    for source in contract['direct_source_evidence']:
        value = raw(int(source['source_string_address'], 16), len(source['source_path'].encode()) + 1)
        if value is not None and (value != source['source_path'].encode() + b'\0'
                                  or sha256(value) != source['source_string_sha256']):
            raise Invalid('attribution source string differs')
        lower = bound_word(source['site'], source['word_sha256'])
        upper = bound_word(source['upper_address_site'], source['upper_word_sha256'])
        transfer = bound_word(source['diagnostic_transfer_site'], source['diagnostic_word_sha256'])
        if lower is not None and upper is not None:
            immediate = (lower & 0xffff) - (0x10000 if lower & 0x8000 else 0)
            address = ((upper & 0xffff) << 16) + immediate
            if upper >> 16 != (15 << 10 | 4) or lower >> 16 != (9 << 10 | 4 << 5 | 4) or address != int(source['source_string_address'], 16):
                raise Invalid('attribution A0 source-path construction differs')
        if transfer is not None and (transfer >> 26 not in (2, 3) or (transfer & 0x3ffffff) << 2 != 0x105888):
            raise Invalid('attribution source diagnostic transfer differs')
    for call in contract['independent_startup_calls']:
        word = bound_word(call['site'], call['word_sha256'])
        if word is not None and (word >> 26 != 3 or (word & 0x3ffffff) << 2 != int(call['target'], 16)):
            raise Invalid('independent startup transfer differs')
    terminal = contract['remote_terminal']
    word = bound_word(terminal['call_site'], terminal['call_word_sha256'])
    if word is not None and (word >> 26 != 2 or (word & 0x3ffffff) << 2 != 0x12c218):
        raise Invalid('external leaf tail transfer differs')
    for site in terminal['entry_restore_sites']:
        bound_word(site['site'], site['word_sha256'])

    if not inventory_path.is_file():
        missing.append('required attribution raw inventory is absent')
    else:
        if identity(inventory_path) != contract['inventory_identity']:
            raise Invalid('attribution raw inventory identity differs')
        inventory = json.loads(inventory_path.read_text())
        functions = {f['entry']: f for f in inventory['functions']}
        for source in contract['direct_source_evidence']:
            function = functions.get(source['saved_function'])
            if function is None:
                missing.append('required source-attributed saved function absent')
                continue
            instruction = next((i for i in function['instructions'] if i['address'] == source['site']), None)
            if instruction is None or not any(r['to'] == source['source_string_address'] for r in instruction['references']):
                raise Invalid('saved diagnostic source reference differs')
        for call in contract['independent_startup_calls']:
            function = functions.get(call['saved_caller'])
            if function is None:
                missing.append('required independent saved caller absent')
                continue
            instruction = next((i for i in function['instructions'] if i['address'] == call['site']), None)
            if instruction is None or not any(r['to'] == call['target'] for r in instruction['references']):
                raise Invalid('independent saved caller reference differs')
    result = {'scope': 'Fixed raw main-loader corroboration only; main ownership remains mixed pending an independent ADR split.',
              'main_ranges': ranges, 'main_bytes': sum(r['bytes'] for r in ranges),
              'independent_game_anchor': '../fr2/source/backrend/backrend.c',
              'external_leaf': terminal, 'shared_dependency_ownership': 'excluded',
              'direct_source_evidence': contract['direct_source_evidence'],
              'startup_calls': contract['independent_startup_calls'],
              'new_attributed_match_bytes': 0, 'contract_identity': identity(CONTRACT)}
    if missing:
        raise Incomplete('; '.join(missing), result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    executable = args.game/'extracted/SLES_517.05'

    def action():
        if not executable.is_file():
            raise Incomplete('required misc3d attribution executable is absent')
        return check(executable.read_bytes(), args.inventory)

    return write_result(args.output, 'misc3d-attribution', action,
                        [p for p in (Path(__file__), CONTRACT, executable, args.inventory) if p.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
