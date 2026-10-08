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
    ee = (extracted / 'SLES_517.05').read_bytes()
    if sha256(ee) != PROFILE['ee_sha256']:
        raise Invalid('EE profile identity mismatch')
    pins = {r['program']: r['sha256'] for r in json.loads(PINS_PATH.read_text())['input_modules']}
    image = (extracted / 'IRX/IOPRP255.IMG').read_bytes()
    payloads = {r['name'] + '.irx': image[r['offset']:r['offset'] + r['bytes']]
                for r in parse_romdir(image)['modules']}
    for name in pins:
        if name not in payloads:
            payloads[name] = (extracted / 'IRX' / name).read_bytes()
    rows = []
    for name, digest in sorted(pins.items()):
        data = payloads[name]
        if sha256(data) != digest:
            raise Invalid(name + ' exact static identity mismatch')
        module = parse_irx(data)
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
    return {'scope': 'all fixed 24 modules and aligned EE executable words',
            'ee': scan_calls(ee, EE_TARGETS), 'modules': rows, 'parent_status': 'incomplete',
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

    return write_result(args.output, 'PAL RPC handoff frontier', action,
                        [PINS_PATH, *[Path(__file__).with_name(name) for name in
                         ('inventory_rpc_handoffs.py', 'check_rpc_contracts.py', 'rpc_contracts.py',
                          'rpc_profile.json', 'iop_symbols.py', 'ps2_executables.py',
                          'ps2_irx.py', 'evidence_common.py')]])


if __name__ == '__main__':
    raise SystemExit(main())
