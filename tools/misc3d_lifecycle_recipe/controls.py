#!/usr/bin/env python3
"""Real source-output controls; public synthetic fixtures remain separate."""
import argparse
import json
from pathlib import Path
import struct
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import misc3d_lifecycle as contract
from evidence_common import identity, write_result
from ps2_executables import parse_elf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = []

    def retain(name, expected, action):
        root = output / name
        exit_code = write_result(root, 'misc3d-lifecycle-control', action, [Path(__file__)])
        receipt = next(root.glob('*/result.json'))
        records.append({'control': name, 'expected_exit': expected, 'exit': exit_code,
                        'receipt': str(receipt), **identity(receipt)})
        return json.loads(receipt.read_text())

    positive = retain('real_source_build', 0, lambda: contract.check(args.game, args.tool_root))
    if positive['status'] == 'pass':
        source = output / 'changed-lifecycle.c'
        original = contract.SOURCES['lifecycle'].read_text()
        changed = original.replace('if (misc3d_db_id != -1)', 'if (misc3d_db_id == -1)')
        if changed == original:
            raise ValueError('fixed source mutation no longer applies')
        source.write_text(changed)
        selected = {**contract.SOURCES, 'lifecycle': source}
        # A true changed C build, followed by the same fixed output comparison.
        retain('changed_source_build', 1,
               lambda: contract.build_and_compare(args.game, args.tool_root, selected))
        linked_path = Path(positive['details']['artifacts']['linked_output']['path'])
        linked = bytearray(linked_path.read_bytes())
        elf = parse_elf(bytes(linked))
        index = next(i for i, section in enumerate(elf['sections'])
                     if section['name'] == '.sbss.fr2_misc3d_state_cc')
        struct.pack_into('<I', linked, elf['section_offset'] + index * 40 + 12, 0x290ad0)
        mutated = output / 'changed-layout.elf'
        mutated.write_bytes(linked)
        retail = (args.game / 'extracted/SLES_517.05').read_bytes()

        def layout():
            try:
                return contract.verify_outputs(retail, mutated.read_bytes())
            except (contract.Invalid, contract.Incomplete) as exc:
                exc.details['mutated_output'] = {'path': str(mutated), **identity(mutated)}
                exc.details['positive_linked_output'] = identity(linked_path)
                raise

        retain('changed_layout', 1, layout)
    with patch.object(contract, 'OBSERVATION', output / 'absent-observation.json'):
        retain('missing_provenance', 2, lambda: contract.check(args.game, args.tool_root))
    summary = {'schema_version': 1, 'controls': records,
               'status': 'pass' if len(records) == 4 and all(r['exit'] == r['expected_exit']
                         for r in records) else 'fail',
               'claim_limit': 'Real child controls only. Positive does not complete ownership, aliases, loader or whole corpus. Layout negative mutates ELF metadata; source negative recompiles changed C.'}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))
    return 0 if summary['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
