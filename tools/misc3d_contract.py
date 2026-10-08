#!/usr/bin/env python3
"""Build the fixed misc3d accessor/cell scope and check its evidence and NOBITS layout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from compiler_probe import run_probe
from compiler_probe_recipe import build, run
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256, boundary_provenance
from matching_sections import sections
from ps2_executables import parse_elf

ROOT = Path(__file__).resolve().parent.parent
CELL_SOURCE = ROOT / 'reconstruction/ee/app3d/misc3d_db_id_cell.c'
LINK_SCRIPT = ROOT / 'tools/misc3d_recipe/candidate.ld'
DECISION = ROOT / 'notes/evidence/fr2-misc3d-cell/decision.json'
OBSERVATION = ROOT / 'notes/evidence/fr2-misc3d-cell/observation.json'


def verify_cell_object(data: bytes) -> dict:
    """ee-gcc emits this tentative definition as SHN_MIPS_SCOMMON, with no payload."""
    elf = parse_elf(data)
    rows = elf['sections']
    found = []
    for table in rows:
        if table['type'] != 2:
            continue
        if (table['entry_size'] != 16 or table['size'] % 16
                or not 0 < table['link'] < len(rows)
                or rows[table['link']]['type'] != 3):
            raise Invalid('cell object symbol table is malformed')
        strings = rows[table['link']]
        names = data[strings['offset']:strings['offset'] + strings['size']]
        for offset in range(table['offset'], table['offset'] + table['size'], 16):
            name, value, size, info, _, section = struct.unpack_from('<IIIBBH', data, offset)
            end = names.find(b'\0', name)
            if name >= len(names) or end < 0:
                raise Invalid('cell object symbol name is malformed')
            if names[name:end] == b'misc3d_db_id':
                found.append((value, size, info, section))
    if len(found) != 1 or found[0] not in ((4, 4, 17, 0xff03), (4, 4, 17, 0xfff2)):
        raise Invalid('cell object must define one uninitialized four-byte common object, aligned four')
    if any(s['flags'] & 2 and s['type'] != 8 and s['size']
           and s['name'] not in ('.reginfo',) for s in rows):
        raise Invalid('cell object has unexpected allocated file bytes')
    return {'symbol': 'misc3d_db_id', 'bytes': 4, 'alignment': 4,
            'storage': 'common', 'has_file_bytes': False}


def verify_outputs(retail: bytes, linked: bytes) -> dict:
    """Public ELF output seam. Corpus/provenance binding is enforced by the CLI."""
    original, candidate = sections(retail), sections(linked)
    code_name = '.text.fr2_misc3d_get_database_id'
    cell_name = '.sbss.fr2_misc3d_db_id'
    if code_name not in candidate or cell_name not in candidate:
        raise Incomplete('accessor or cell section is missing from linked output')
    if '.text' not in original or '.sbss' not in original:
        raise Incomplete('retail text or sbss section is missing')
    code = candidate[code_name]
    offset = build.FUNCTION_VADDR - original['.text'].address
    expected = original['.text'].data[offset:offset + build.FUNCTION_SIZE]
    if (offset < 0 or len(expected) != 60 or code.address != build.FUNCTION_VADDR
            or code.size != 60 or code.data != expected):
        raise Invalid('accessor bytes differ or its address/size changed')
    rows = parse_elf(linked)['sections']
    cells = [s for s in rows if s.get('name') == cell_name]
    cell = cells[0]
    retail_cell = original['.sbss']
    if (cell['type'] != 8 or cell['address'] != 0x290ac4 or cell['size'] != 4
            or cell['flags'] & 3 != 3 or cell['flags'] & 4
            or cell['alignment'] < 4 or cell['alignment'] & (cell['alignment'] - 1)
            or cell['address'] % cell['alignment']
            or not retail_cell.address <= cell['address']
            or cell['address'] + 4 > retail_cell.address + retail_cell.size
            or retail_cell.has_bytes):
        raise Invalid('cell layout differs from the recorded NOBITS address/size/alignment')
    return {'accessor': {'status': 'pass', 'address': '001d1800', 'bytes': 60,
                         'reference_sha256': sha256(expected), 'comparison_sha256': code.sha256},
            'cell': {'section': cell_name, 'address': '00290ac4', 'bytes': 4,
                     'alignment': cell['alignment'], 'type': 'NOBITS',
                     'has_file_bytes': False, 'matched_file_bytes': 0}}


def provenance() -> dict:
    """The caller selects installed inputs, never the recorded decision or scope."""
    previous = boundary_provenance()
    for path in (DECISION, OBSERVATION, CELL_SOURCE, LINK_SCRIPT):
        if not path.is_file():
            raise Incomplete(f'misc3d provenance missing: {path}')
    decision = json.loads(DECISION.read_text())
    for name, path in (('observation', OBSERVATION), ('cell_source', CELL_SOURCE),
                       ('link_script', LINK_SCRIPT)):
        if identity(path)['sha256'] != decision['inputs'][name]['sha256']:
            raise Invalid(f'misc3d {name} identity differs from the recorded decision')
    if identity(build.RECONSTRUCTION_SOURCE)['sha256'] != decision['inputs']['accessor_source']['sha256']:
        raise Invalid('misc3d accessor source identity differs from the recorded decision')
    observation = json.loads(OBSERVATION.read_text())
    if observation.get('status') != 'pass':
        raise Incomplete('misc3d saved-project observation is incomplete')
    if (decision.get('corpus_sha256') != EE_CORPUS_SHA256
            or observation.get('details', {}).get('executable_sha256') != EE_CORPUS_SHA256):
        raise Invalid('misc3d observation/decision executable identity differs')
    return {'first_unit': previous, 'decision': identity(DECISION),
            'observation': identity(OBSERVATION)}


def check(game: Path, tool_root: Path) -> dict:
    evidence = provenance()
    tool_root = tool_root.resolve(strict=True)
    staging = Path(tempfile.mkdtemp(prefix='misc3d-contract-', dir=tool_root))
    manifest_path, _ = build.prepare(game, tool_root, staging)
    run.validate_manifest_runtimes(manifest_path, tool_root)
    runtime = run.validate_runtime_images()
    manifest = json.loads(manifest_path.read_text())
    candidate = next(c for c in manifest['candidates'] if c['id'] == 'ee-gcc2.96')
    staged_cell = staging / CELL_SOURCE.name
    shutil.copyfile(CELL_SOURCE, staged_cell)
    cell_object = staging / 'cell.o'
    cell_prepared = staging / 'cell-prepared.o'
    commands = [
        [*candidate['compile'], *candidate['flags'], '-c', str(staged_cell), '-o', str(cell_object)],
        [*candidate['prepare_object'][:-2], str(cell_object), str(cell_prepared)],
    ]
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Incomplete(f'misc3d cell build unavailable: {exc}') from exc
        if result.returncode:
            raise Invalid('misc3d cell compilation/preparation failed',
                          {'argv': command, 'stderr': result.stderr[-2000:]})
    cell_definition = verify_cell_object(cell_object.read_bytes())
    shutil.copyfile(LINK_SCRIPT, staging / 'candidate.ld')
    candidate['link'] = [arg for arg in candidate['link']
                         if not arg.startswith('--defsym=misc3d_db_id=')]
    candidate['link'].append(str(cell_prepared))
    manifest['candidates'] = [candidate]
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    result = run_probe(manifest_path, staging / 'probe', range_scoped=True)
    if result['status'] == 'incomplete':
        raise Incomplete('misc3d accessor build is incomplete', result)
    if result['status'] != 'pass':
        raise Invalid('misc3d accessor no longer matches', result)
    linked = Path(result['candidates'][0]['link_argv'][
        result['candidates'][0]['link_argv'].index('-o') + 1])
    layout = verify_outputs((game / 'extracted/SLES_517.05').read_bytes(), linked.read_bytes())
    artifacts = {'cell_source': staged_cell, 'cell_object': cell_object,
                 'cell_prepared_object': cell_prepared, 'linked_output': linked,
                 'accessor_object': linked.parent / 'candidate.o',
                 'accessor_prepared_object': linked.parent / 'prepared.o',
                 'comparison': linked.parent / 'function.bin', 'link_script': staging / 'candidate.ld'}
    return {'scope': 'misc3d accessor and four-byte cell only', 'provenance': evidence,
            'runtime_identity': runtime, 'outputs': layout, 'build': result,
            'artifacts': {name: {'path': str(path), **identity(path)} for name, path in artifacts.items()},
            'cell_build_commands': commands, 'cell_definition': cell_definition, 'ac05_status': 'incomplete',
            'issue24_status': 'incomplete',
            'unresolved_dependencies': json.loads(DECISION.read_text())['unresolved'],
            'claim_limits': ['Exploratory ee-gcc2.96/GNU binutils 2.40 profile; not historical toolchain identification.',
                             'NOBITS layout is checked without comparing invented file bytes.',
                             'Loader, reset, release, sibling accessors and helper implementations are outside this source-built scope.',
                             'Whole-image AC08/AC09 and the parent remain incomplete.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/misc3d-contract'))
    args = parser.parse_args()
    return write_result(args.output, 'misc3d-contract', lambda: check(args.game, args.tool_root),
                        [Path(__file__), CELL_SOURCE, LINK_SCRIPT])


if __name__ == '__main__':
    raise SystemExit(main())
