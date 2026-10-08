#!/usr/bin/env python3
"""Compile the inferred loader terminal seam and compare its eight retail bytes."""
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

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'reconstruction/ee/app3d/misc3d_loader_terminal.c'
LINK = Path(__file__).with_name('terminal.ld')
DECISION = ROOT/'notes/evidence/fr2-misc3d-loader/decision.json'
VALIDATION_INPUTS = [ROOT/'tools'/name for name in (
    'compiler_probe_recipe/build.py', 'compiler_probe_recipe/run.py',
    'compiler_probe_recipe/manifest.template.json', 'compiler_probe_recipe/docker-linux-exec.sh',
    'compiler_probe_recipe/docker-wine-exec.sh', 'evidence_common.py', 'matching_ranges.py',
    'matching_sections.py', 'matching_diff.py', 'ps2_executables.py', 'corpus_contract.py',
    'compiler_probe.py', 'compiler_output.py')]


def provenance(game: Path, tool_root: Path) -> dict:
    missing = []
    executable = game/'extracted/SLES_517.05'
    if executable.is_file():
        if sha256(executable.read_bytes()) != EE_CORPUS_SHA256:
            raise Invalid('terminal child executable identity differs')
    else:
        missing.append('required terminal retail executable is absent')
    if not tool_root.is_dir():
        missing.append('required terminal tool root is absent')
    decision = json.loads(DECISION.read_text()) if DECISION.is_file() else None
    if decision is None:
        missing.append('required terminal provenance decision is absent')
    elif decision.get('corpus_sha256') != EE_CORPUS_SHA256:
        raise Invalid('terminal decision corpus identity differs')
    for name,path in [('terminal_source',SOURCE),('terminal_link',LINK),('terminal_recipe',Path(__file__))]:
        if not path.is_file():
            missing.append('required terminal input is absent: '+name)
        elif decision is not None and identity(path) != decision['inputs'][name]:
            raise Invalid('terminal source/recipe identity differs: '+name)
    if missing:
        raise Incomplete('; '.join(missing))
    return {'decision':identity(DECISION), 'source':identity(SOURCE), 'link_script':identity(LINK),
            'validation_inputs':{str(path):identity(path) for path in VALIDATION_INPUTS}}


def compare(retail: bytes, linked: bytes) -> dict:
    original, candidate = sections(retail), sections(linked)
    text = original.get('.text')
    terminal = candidate.get('.text.fr2_misc3d_loader_terminal')
    if text is None or terminal is None:
        raise Incomplete('terminal retail or candidate section is absent')
    reference = text.data[0x12c218-text.address:0x12c220-text.address]
    if terminal.address != 0x12c218 or terminal.size != 8 or terminal.data != reference:
        raise Invalid('terminal candidate address/size/bytes differ')
    return {'address': '0012c218', 'bytes': 8, 'reference_sha256': sha256(reference),
            'comparison_sha256': terminal.sha256, 'candidate_byte_identical_bytes': 8,
            'new_attributed_match_bytes': 0}


def source_build(game: Path, tool_root: Path, source: Path = SOURCE) -> dict:
    if sha256((game/'extracted/SLES_517.05').read_bytes()) != EE_CORPUS_SHA256:
        raise Invalid('terminal build requires the pinned executable')
    if not tool_root.is_dir():
        raise Incomplete('required terminal tool root is absent')
    stage = Path(tempfile.mkdtemp(prefix='misc3d-loader-terminal-', dir=tool_root))
    manifest_path, _ = build.prepare(game, tool_root, stage)
    run.validate_manifest_runtimes(manifest_path, tool_root)
    runtimes = run.validate_runtime_images()
    manifest = json.loads(manifest_path.read_text())
    candidate = next(c for c in manifest['candidates'] if c['id']=='ee-gcc2.96')
    missing_tools=[path for path in (candidate['compiler_executable'],*candidate['tool_files'].values()) if not Path(path).is_file()]
    if missing_tools:
        raise Incomplete('required terminal compiler/tool binaries are absent', {'paths':missing_tools})
    staged, obj, prepared, linked = [stage/name for name in ('terminal.c','terminal.o','prepared.o','terminal.elf')]
    shutil.copyfile(source, staged)
    shutil.copyfile(LINK, stage/'terminal.ld')
    commands = [[*candidate['compile'], *candidate['flags'], '-c', str(staged), '-o', str(obj)],
                [*candidate['prepare_object'][:-2], str(obj), str(prepared)],
                [*candidate['link'][:4], '-m', 'elf32ltsmip', '-T', str(stage/'terminal.ld'),
                 '--defsym=misc3d_optional_object=0x0028f23c', '--defsym=_gp=0x00295d70',
                 '-o', str(linked), str(prepared)]]
    for argv in commands:
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise Incomplete('terminal source tool execution unavailable', {'argv':argv, 'reason':str(error)}) from error
        if completed.returncode:
            raise Invalid('terminal source build failed', {'argv': argv, 'stderr': completed.stderr})
    comparison = stage/'terminal.comparison.bin'
    comparison.write_bytes(sections(linked.read_bytes())['.text.fr2_misc3d_loader_terminal'].data)
    receipt = {'commands': commands, 'runtime_identity': runtimes,
               'artifacts': {name:{'path':str(path),**identity(path)} for name,path in
                             [('source',staged),('object',obj),('prepared',prepared),('linked',linked),
                              ('comparison',comparison),('link_script',stage/'terminal.ld'),('manifest',manifest_path)]},
               'compiler': {'id':'ee-gcc2.96','flags':candidate['flags'],
                            'executable':identity(Path(candidate['compiler_executable'])),
                            'tool_files':{name:identity(Path(path)) for name,path in candidate['tool_files'].items()}},
               'scope': 'Eight-byte remote terminal candidate; no new ownership or complete loader byte match.',
               'issue37_status':'incomplete','historical_compiler_status':'incomplete'}
    try:
        receipt['comparison'] = compare((game/'extracted/SLES_517.05').read_bytes(),linked.read_bytes())
    except (Incomplete, Invalid) as error:
        error.details.update(receipt)
        raise
    return receipt


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game',type=Path)
    parser.add_argument('tool_root',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    def action():
        fixed_provenance=provenance(args.game,args.tool_root)
        result=source_build(args.game,args.tool_root)
        result['provenance']=fixed_provenance
        return result
    return write_result(args.output,'misc3d-loader-terminal-source',action,
                        [path for path in (Path(__file__),SOURCE,LINK,DECISION,
                                           args.game/'extracted/SLES_517.05',*VALIDATION_INPUTS) if path.is_file()])


if __name__=='__main__':
    raise SystemExit(main())
