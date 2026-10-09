#!/usr/bin/env python3
"""Execute real main-loader source, layout, provenance and independent-build controls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence_common import Invalid, identity, write_result
from misc3d_loader_recipe import loader_build
from ps2_executables import parse_elf


def controls(game: Path, tool_root: Path, output: Path) -> dict:
    results = {}
    provenance_inputs = [loader_build.SOURCE, loader_build.HEADER, loader_build.TERMINAL_SOURCE,
                         loader_build.LINK, Path(loader_build.__file__), loader_build.DECISION]

    def record(name, action):
        directory = output/name
        code = write_result(directory, 'misc3d-loader-main-control-' + name, action,
                            [path for path in provenance_inputs if path.is_file()])
        receipt = next(directory.glob('*/result.json'))
        results[name] = {'exit_code': code, 'receipt': {'path': str(receipt), **identity(receipt)}}
        return json.loads(receipt.read_text())['details']

    first = record('source_positive', lambda: loader_build.source_build(game, tool_root))
    changed = output/'changed-loader.c'
    source = loader_build.SOURCE.read_text()
    needle = 'flag_object->flags |= 2ULL;'
    if source.count(needle) != 1:
        raise Invalid('loader source mutation site is absent or ambiguous')
    changed.write_text(source.replace(needle, 'flag_object->flags |= 1ULL;'))
    record('changed_source', lambda: loader_build.source_build(game, tool_root, source=changed))

    def shifted_layout():
        path = Path(first['artifacts']['linked']['path'])
        data = bytearray(path.read_bytes())
        rows = parse_elf(bytes(data))['sections']
        index = next(i for i, row in enumerate(rows) if row['name'] == '.text.fr2_misc3d_loader_main')
        table = struct.unpack_from('<I', data, 32)[0]
        stride = struct.unpack_from('<H', data, 46)[0]
        struct.pack_into('<I', data, table + index * stride + 12, 0x1d140c)
        changed_path = output/'shifted-main.elf'
        changed_path.write_bytes(data)
        return loader_build.compare((game/'extracted/SLES_517.05').read_bytes(), bytes(data))

    record('changed_layout', shifted_layout)
    with patch.object(loader_build, 'DECISION', output/'missing-decision.json'):
        record('missing_provenance', lambda: loader_build.provenance(game, tool_root))
    stale = json.loads(loader_build.DECISION.read_text())
    stale['inputs']['source']['sha256'] = '0' * 64
    stale_path = output/'stale-decision.json'
    stale_path.write_text(json.dumps(stale))
    with patch.object(loader_build, 'DECISION', stale_path):
        record('stale_provenance', lambda: loader_build.provenance(game, tool_root))
        record('contradiction_over_missing', lambda: loader_build.provenance(game, output/'absent-tool-root'))

    def reproducibility():
        second = loader_build.source_build(game, tool_root)
        names = ['loader_object', 'loader_prepared', 'terminal_object', 'terminal_prepared', 'linked',
                 'terminal_comparison', *(f'comparison_{start:08x}' for start, _ in loader_build.MAIN_RANGES)]
        compared = {name: {'first': first['artifacts'][name], 'second': second['artifacts'][name],
                           'identical': (first['artifacts'][name]['sha256'], first['artifacts'][name]['bytes'])
                           == (second['artifacts'][name]['sha256'], second['artifacts'][name]['bytes'])}
                    for name in names}
        if any(not result['identical'] for result in compared.values()):
            raise Invalid('two independent loader builds differ', {'artifacts': compared})
        return {'artifacts': compared, 'directories': [first['working_directory'], second['working_directory']],
                'scope': 'Recorded main-loader candidate and external leaf under pinned exploratory tools.'}

    record('reproducibility', reproducibility)
    expected = {'source_positive': 0, 'changed_source': 1, 'changed_layout': 1,
                'missing_provenance': 2, 'stale_provenance': 1, 'contradiction_over_missing': 1,
                'reproducibility': 0}
    failures = [name for name, code in expected.items() if results[name]['exit_code'] != code]
    return {'results': results, 'expected_exit_codes': expected, 'failures': failures,
            'scope': 'Actual handwritten source builds; no guest execution or historical compiler claim.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    return write_result(args.output/'summary', 'misc3d-loader-main-controls',
                        lambda: controls(args.game.resolve(), args.tool_root.resolve(), args.output.resolve()),
                        [Path(__file__), Path(loader_build.__file__), loader_build.SOURCE, loader_build.HEADER,
                         loader_build.TERMINAL_SOURCE, loader_build.LINK])


if __name__ == '__main__':
    raise SystemExit(main())
