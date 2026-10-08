#!/usr/bin/env python3
"""Run real misc3d build, layout mutation and missing-provenance controls."""
import argparse
import json
from pathlib import Path
import struct
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import misc3d_contract as contract
from evidence_common import identity, write_result
from ps2_executables import parse_elf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/misc3d-controls'))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = []
    positive = output / 'positive'
    exit_code = write_result(positive, 'misc3d-contract',
                             lambda: contract.check(args.game, args.tool_root), [Path(__file__)])
    receipt = next(positive.glob('*/result.json'))
    results.append({'control': 'real_source_build', 'expected_exit': 0, 'exit': exit_code,
                    'receipt': str(receipt), **identity(receipt)})
    if exit_code == 0:
        built = json.loads(receipt.read_text())
        linked_path = Path(built['details']['artifacts']['linked_output']['path'])
        linked = bytearray(linked_path.read_bytes())
        elf = parse_elf(bytes(linked))
        index = next(i for i, s in enumerate(elf['sections'])
                     if s.get('name') == '.sbss.fr2_misc3d_db_id')
        struct.pack_into('<I', linked, elf['section_offset'] + index * 40 + 12, 0x290ac8)
        mutated = output / 'changed-layout.elf'
        mutated.write_bytes(linked)
        negative = output / 'layout-negative'
        exit_code = write_result(negative, 'misc3d-layout-control',
                                 lambda: contract.verify_outputs(
                                     (args.game / 'extracted/SLES_517.05').read_bytes(),
                                     mutated.read_bytes()), [mutated, Path(__file__)])
        receipt = next(negative.glob('*/result.json'))
        results.append({'control': 'cell_address_shifted_four_bytes', 'expected_exit': 1,
                        'exit': exit_code, 'receipt': str(receipt), **identity(receipt)})
    missing = output / 'missing-provenance'
    with patch.object(contract, 'OBSERVATION', output / 'absent-observation.json'):
        exit_code = write_result(missing, 'misc3d-provenance-control', contract.provenance, [Path(__file__)])
    receipt = next(missing.glob('*/result.json'))
    results.append({'control': 'missing_observation', 'expected_exit': 2,
                    'exit': exit_code, 'receipt': str(receipt), **identity(receipt)})
    passed = len(results) == 3 and all(r['exit'] == r['expected_exit'] for r in results)
    summary = {'status': 'pass' if passed else 'fail', 'command': sys.argv,
               'controls': results, 'claim_limit': 'Controls for this bounded child only; #24 remains incomplete.'}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
