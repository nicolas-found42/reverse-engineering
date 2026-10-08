#!/usr/bin/env python3
"""Retain the fixed PAL RPC candidate frontier; parent stays incomplete."""
import argparse
import json
from pathlib import Path

from check_rpc_contracts import EE_TARGETS, PARENT_GAPS, PROFILE, scan_calls
from evidence_common import Incomplete, Invalid, sha256, write_result
from ps2_executables import parse_romdir
from ps2_irx import parse_irx

PINS_PATH = Path(__file__).resolve().parents[1] / 'notes/evidence/fr2-iop-export-recovery/index.json'


def inventory_handoffs(extracted: Path) -> dict:
    missing, payloads = [], {}
    ee_path = extracted / 'SLES_517.05'
    ee = None
    if ee_path.is_file():
        ee = ee_path.read_bytes()
        if sha256(ee) != PROFILE['ee_sha256']:
            raise Invalid('EE profile identity mismatch')
    else:
        missing.append('required EE image is absent: ' + str(ee_path))
    pins = {r['program']: r['sha256'] for r in json.loads(PINS_PATH.read_text())['input_modules']}
    rom_path = extracted / 'IRX/IOPRP255.IMG'
    if rom_path.is_file():
        image = rom_path.read_bytes()
        try:
            payloads = {r['name'] + '.irx': image[r['offset']:r['offset'] + r['bytes']]
                        for r in parse_romdir(image)['modules']}
        except Incomplete as exc:
            missing.append(str(exc))
    else:
        missing.append('required ROM image is absent: ' + str(rom_path))
    for name, digest in pins.items():
        path = extracted / 'IRX' / name
        if path.is_file():
            data = path.read_bytes()
            if sha256(data) != digest:
                raise Invalid(name + ' exact static identity mismatch')
            payloads.setdefault(name, data)
        if name not in payloads:
            missing.append('required pinned module is absent: ' + name)
    rows = []
    for name, digest in sorted(pins.items()):
        if name not in payloads:
            continue
        data = payloads[name]
        if sha256(data) != digest:
            raise Invalid(name + ' exact static identity mismatch')
        try:
            module = parse_irx(data)
        except Incomplete as exc:
            missing.append(name + ': ' + str(exc))
            continue
        targets = {}
        tables = []
        for table in module['imports']:
            if table['library'] in ('sifcmd', 'sifman'):
                tables.append({'library': table['library'], 'version': table['version'],
                               'ordinals': [{'ordinal': link['index'], 'stub': link['stub_text_offset']}
                                            for link in table['links']]})
                targets.update({link['stub_text_offset']: table['library'] + '/' + str(link['index'])
                                for link in table['links']})
        rows.append({'module': name, 'sha256': digest, 'sif_tables': tables,
                     'candidates': scan_calls(data, targets),
                     'handler_status': 'unresolved except committed STREAM volume child'})
    ee_candidates = {}
    if ee is not None:
        try:
            ee_candidates = scan_calls(ee, EE_TARGETS)
        except Incomplete as exc:
            missing.append(str(exc))
    if missing:
        raise Incomplete('; '.join(missing), {'ee': ee_candidates, 'modules': rows,
                                             'parent_status': 'incomplete'})
    return {'scope': 'all fixed 24 modules and aligned EE executable words',
            'ee': ee_candidates, 'modules': rows, 'parent_status': 'incomplete',
            'gaps': PARENT_GAPS, 'runtime_registration': 'unobserved',
            'claim_limits': 'Numeric exact-version imports and JAL/JALR-shaped words are candidates; neither handlers nor complete decoded control flow.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extracted', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def action():
        result = inventory_handoffs(args.extracted)
        raise Incomplete('required parent handoff inventory is not yet reconciled', result)

    pins = json.loads(PINS_PATH.read_text())['input_modules']
    inputs = [args.extracted / 'SLES_517.05', args.extracted / 'IRX/IOPRP255.IMG',
              *[args.extracted / 'IRX' / row['program'] for row in pins], PINS_PATH, *[Path(__file__).with_name(name) for name in
                         ('inventory_rpc_handoffs.py', 'check_rpc_contracts.py', 'rpc_contracts.py',
                          'rpc_profile.json', 'iop_symbols.py', 'ps2_executables.py',
                          'ps2_irx.py', 'evidence_common.py')]]
    return write_result(args.output, 'PAL RPC handoff frontier', action,
                        [path for path in inputs if path.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
