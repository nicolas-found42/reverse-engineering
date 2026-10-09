#!/usr/bin/env python3
"""Compile handwritten misc3d loader source and compare its fixed raw instruction ranges."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compiler_probe_recipe import build, run
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from matching_sections import sections
from misc3d_loader_recipe import source_build as terminal_recipe

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'reconstruction/ee/app3d/misc3d_loader.c'
HEADER = SOURCE.with_suffix('.h')
TERMINAL_SOURCE = SOURCE.with_name('misc3d_loader_terminal.c')
LINK = Path(__file__).with_name('loader.ld')
DECISION = ROOT/'notes/evidence/fr2-misc3d-loader/decision.json'
FLAGS = ['-G8', '-O2']
MAIN_RANGES = ((0x1d1408, 0x1d143c), (0x1d1440, 0x1d157c), (0x1d1580, 0x1d15b4),
               (0x1d15b8, 0x1d15cc), (0x1d15d0, 0x1d1628))
VALIDATION_INPUTS = terminal_recipe.VALIDATION_INPUTS


def provenance(game: Path, tool_root: Path) -> dict:
    missing = []
    executable = game/'extracted/SLES_517.05'
    if executable.is_file():
        if sha256(executable.read_bytes()) != EE_CORPUS_SHA256:
            raise Invalid('loader build executable identity differs')
    else:
        missing.append('required loader retail executable is absent')
    if not tool_root.is_dir():
        missing.append('required loader tool root is absent')
    decision = json.loads(DECISION.read_text()) if DECISION.is_file() else None
    if decision is None:
        missing.append('required loader build decision is absent')
    elif decision.get('corpus_sha256') != EE_CORPUS_SHA256:
        raise Invalid('loader build decision corpus identity differs')
    for name, path in [('source', SOURCE), ('header', HEADER), ('terminal_source', TERMINAL_SOURCE),
                       ('loader_link', LINK), ('loader_recipe', Path(__file__))]:
        if not path.is_file():
            missing.append('required loader build input is absent: ' + name)
        elif decision is not None:
            recorded = decision.get('inputs', {}).get(name)
            if recorded is None:
                missing.append('required loader build identity is absent: ' + name)
            elif identity(path) != recorded:
                raise Invalid('loader source/recipe identity differs: ' + name)
    if missing:
        raise Incomplete('; '.join(missing))
    return {'decision': identity(DECISION), 'source': identity(SOURCE), 'header': identity(HEADER),
            'terminal_source': identity(TERMINAL_SOURCE), 'link_script': identity(LINK),
            'validation_inputs': {str(path): identity(path) for path in VALIDATION_INPUTS}}


def compare(retail: bytes, linked: bytes) -> dict:
    original, candidate = sections(retail), sections(linked)
    text = original.get('.text')
    main = candidate.get('.text.fr2_misc3d_loader_main')
    if text is None or main is None:
        raise Incomplete('loader retail or candidate main section is absent')
    if main.address != 0x1d1408 or main.size != 544 or len(main.data) != 544:
        raise Invalid('loader candidate main address/size differs')
    results = []
    for start, end in MAIN_RANGES:
        if start < text.address or end > text.address + text.size:
            raise Incomplete('required retail loader range is absent')
        reference = text.data[start - text.address:end - text.address]
        rebuilt = main.data[start - main.address:end - main.address]
        if rebuilt != reference:
            raise Invalid(f'loader candidate raw range bytes differ: {start:08x}')
        results.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}', 'bytes': end - start,
                        'reference_sha256': sha256(reference), 'comparison_sha256': sha256(rebuilt)})
    terminal = terminal_recipe.compare(retail, linked)
    return {'main_ranges': results, 'main_instruction_bytes': sum(r['bytes'] for r in results),
            'main_envelope_bytes': 544, 'excluded_main_hole_bytes': 16,
            'terminal': terminal, 'candidate_byte_identical_bytes': 536,
            'new_attributed_match_bytes': 0,
            'claim_limit': 'Instruction comparison only; main and external leaf ownership remain mixed. Holes are excluded; this comparison grants no matching credit.'}


def source_build(game: Path, tool_root: Path, source: Path = SOURCE, header: Path = HEADER) -> dict:
    game, tool_root, source, header = game.resolve(), tool_root.resolve(), source.resolve(), header.resolve()
    if sha256((game/'extracted/SLES_517.05').read_bytes()) != EE_CORPUS_SHA256:
        raise Invalid('loader build requires the pinned executable')
    if not tool_root.is_dir():
        raise Incomplete('required loader tool root is absent')
    stage = Path(tempfile.mkdtemp(prefix='misc3d-loader-main-', dir=tool_root))
    manifest_path, _ = build.prepare(game, tool_root, stage)
    run.validate_manifest_runtimes(manifest_path, tool_root)
    runtimes = run.validate_runtime_images()
    manifest = json.loads(manifest_path.read_text())
    candidate = next(c for c in manifest['candidates'] if c['id'] == 'ee-gcc2.96')
    missing_tools = [path for path in (candidate['compiler_executable'], *candidate['tool_files'].values()) if not Path(path).is_file()]
    if missing_tools:
        raise Incomplete('required loader compiler/tool binaries are absent', {'paths': missing_tools})
    staged = stage/'loader.c'
    staged_header = stage/'misc3d_loader.h'
    staged_terminal = stage/'terminal.c'
    shutil.copyfile(source, staged)
    shutil.copyfile(header, staged_header)
    shutil.copyfile(TERMINAL_SOURCE, staged_terminal)
    shutil.copyfile(LINK, stage/'loader.ld')
    commands = []
    artifacts = [('source', staged), ('header', staged_header), ('terminal_source', staged_terminal),
                 ('link_script', stage/'loader.ld'), ('manifest', manifest_path)]
    objects = []
    for stem in ('loader', 'terminal'):
        obj, prepared = stage/(stem + '.o'), stage/(stem + '.prepared.o')
        commands.extend([[*candidate['compile'], *FLAGS, '-c', stem + '.c', '-o', str(obj)],
                         [*candidate['prepare_object'][:-2], str(obj), str(prepared)]])
        objects.append(prepared)
        artifacts.extend([(stem + '_object', obj), (stem + '_prepared', prepared)])
    linked = stage/'loader.elf'
    commands.append([*candidate['link'][:4], '-m', 'elf32ltsmip', '-T', str(stage/'loader.ld'),
                     '-o', str(linked), *map(str, objects)])
    for argv in commands:
        try:
            completed = subprocess.run(argv, cwd=stage, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise Incomplete('loader source tool execution unavailable', {'argv': argv, 'reason': str(error)}) from error
        if completed.returncode:
            raise Invalid('loader source build failed', {'argv': argv, 'stderr': completed.stderr})
    artifacts.append(('linked', linked))
    candidate_sections = sections(linked.read_bytes())
    main_section = candidate_sections.get('.text.fr2_misc3d_loader_main')
    if main_section is not None:
        for start, end in MAIN_RANGES:
            comparison = stage/f'{start:08x}.comparison.bin'
            comparison.write_bytes(main_section.data[start - main_section.address:end - main_section.address])
            artifacts.append((f'comparison_{start:08x}', comparison))
    terminal_section = candidate_sections.get('.text.fr2_misc3d_loader_terminal')
    if terminal_section is not None:
        comparison = stage/'terminal.comparison.bin'
        comparison.write_bytes(terminal_section.data)
        artifacts.append(('terminal_comparison', comparison))
    receipt = {'commands': commands, 'working_directory': str(stage), 'runtime_identity': runtimes,
               'artifacts': {name: {'path': str(path), **identity(path)} for name, path in artifacts},
               'compiler': {'id': 'ee-gcc2.96', 'flags': FLAGS,
                            'executable': identity(Path(candidate['compiler_executable'])),
                            'tool_files': {name: identity(Path(path)) for name, path in candidate['tool_files'].items()}},
               'scope': 'Five main-loader instruction ranges and separate external leaf; holes and leaf ownership excluded.',
               'historical_compiler_status': 'incomplete'}
    try:
        receipt['comparison'] = compare((game/'extracted/SLES_517.05').read_bytes(), linked.read_bytes())
    except (Incomplete, Invalid) as error:
        error.details.update(receipt)
        raise
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def action():
        fixed_provenance = provenance(args.game, args.tool_root)
        result = source_build(args.game, args.tool_root)
        result['provenance'] = fixed_provenance
        return result

    return write_result(args.output, 'misc3d-loader-main-source', action,
                        [path for path in (Path(__file__), SOURCE, HEADER, TERMINAL_SOURCE, LINK, DECISION,
                                           args.game/'extracted/SLES_517.05', *VALIDATION_INPUTS) if path.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
