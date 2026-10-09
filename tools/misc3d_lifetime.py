#!/usr/bin/env python3
"""Reconcile the fixed misc3d dependency producer/use/release contract to raw code."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT/'notes/evidence/fr2-misc3d-loader/lifetime-contract.json'


def check(data: bytes, inventory_path: Path) -> dict:
    """Bind the recorded interpretation to complete raw ranges and direct transfers."""
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('misc3d lifetime requires the unchanged recorded executable')
    if not CONTRACT.is_file():
        raise Incomplete('misc3d lifetime recorded contract is absent')
    contract = json.loads(CONTRACT.read_text())
    if contract['schema'] != 'fr2-misc3d-lifetime/v1' or contract['corpus_sha256'] != EE_CORPUS_SHA256:
        raise Invalid('misc3d lifetime contract has a different schema or corpus')
    sections = [s for s in parse_elf(data)['sections'] if s['type'] != 8 and s['flags'] & 6 == 6]
    missing = []

    def read(start: int, size: int) -> bytes | None:
        owners = [s for s in sections if s['address'] <= start and start + size <= s['address'] + s['size']]
        if not owners:
            missing.append(f'required lifetime code absent: {start:08x}+{size}')
            return None
        if len(owners) != 1:
            raise Invalid(f'lifetime code has ambiguous storage: {start:08x}')
        offset = owners[0]['offset'] + start - owners[0]['address']
        raw = data[offset:offset + size]
        if len(raw) != size:
            raise Invalid(f'lifetime code storage is truncated: {start:08x}')
        return raw

    for function in contract['functions']:
        for span in function['ranges']:
            start, end = int(span['start'], 16), int(span['end_exclusive'], 16)
            if end <= start or end - start != span['bytes']:
                raise Invalid('lifetime contract range has invalid extent')
            raw = read(start, end - start)
            if raw is not None and sha256(raw) != span['sha256']:
                raise Invalid(f'lifetime raw range contradicts recorded contract: {start:08x}')
    for call in contract['direct_calls']:
        site = int(call['site'], 16)
        raw = read(site, 4)
        if raw is None:
            continue
        word = struct.unpack('<I', raw)[0]
        target = ((site + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
        if sha256(raw) != call['word_sha256'] or word >> 26 != 3 or target != int(call['target'], 16):
            raise Invalid(f'lifetime direct transfer contradicts contract: {site:08x}')

    if not inventory_path.is_file():
        missing.append('required lifetime raw inventory is absent')
    else:
        if identity(inventory_path) != contract['inventory_identity']:
            raise Invalid('lifetime inventory identity differs from recorded contract')
        inventory = json.loads(inventory_path.read_text())
        if inventory['executable_sha256'] != EE_CORPUS_SHA256:
            raise Invalid('lifetime inventory records another executable')
        functions = {f['entry']: f for f in inventory['functions']}
        for recorded in contract['functions']:
            function = functions.get(recorded['entry'])
            if function is None:
                missing.append('required lifetime saved function is absent: ' + recorded['entry'])
                continue
            if set(function['callers']) != set(recorded['saved_callers']):
                raise Invalid('lifetime saved caller set differs: ' + recorded['entry'])
            expected = {site for span in recorded['ranges']
                        for site in range(int(span['start'], 16), int(span['end_exclusive'], 16), 4)}
            observed = set()
            for instruction in function['instructions']:
                site = int(instruction['address'], 16)
                if site in observed:
                    raise Invalid('duplicate lifetime inventory instruction')
                observed.add(site)
                raw = read(site, 4)
                if raw is not None and raw != bytes.fromhex(instruction['bytes']):
                    raise Invalid(f'lifetime saved instruction differs from executable: {site:08x}')
            if observed != expected:
                raise Invalid('lifetime saved instruction set differs: ' + recorded['entry'])
    result = dict(contract['observed_contract'])
    result.update(checked_functions=len(contract['functions']), checked_direct_calls=len(contract['direct_calls']),
                  raw_ranges=contract['functions'], contract_identity=identity(CONTRACT))
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
            raise Incomplete('required misc3d lifetime executable is absent')
        return check(executable.read_bytes(), args.inventory)

    return write_result(args.output, 'misc3d-lifetime', action,
                        [p for p in (Path(__file__), CONTRACT, executable, args.inventory) if p.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
