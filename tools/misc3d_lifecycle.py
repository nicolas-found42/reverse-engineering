#!/usr/bin/env python3
"""Compare the repository-recorded misc3d lifecycle scope, without crediting gaps."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from compiler_probe import run_probe
from compiler_probe_recipe import build, run
from evidence_common import identity, write_result
from misc3d_contract import provenance as previous_provenance, verify_cell_object

from matching_ranges import EE_CORPUS_SHA256
from matching_sections import sections
from ps2_executables import parse_elf
from evidence_common import Incomplete, Invalid, sha256

SPANS = (
    ('reset', 0x1d17a8, 28), ('release', 0x1d17c8, 56),
    ('get_database_id', 0x1d1800, 60), ('get_state_cc', 0x1d1840, 64),
    ('get_state_d4', 0x1d1880, 64), ('get_state_d0', 0x1d18c0, 64),
)


def verify_outputs(retail: bytes, linked: bytes) -> dict:
    original, candidate = sections(retail), sections(linked)
    if '.text' not in original:
        raise Incomplete('retail text is missing')
    text = original['.text']
    spans, missing = {}, []
    for name, address, size in SPANS:
        section = candidate.get('.text.fr2_misc3d_' + name)
        if section is None:
            missing.append(f'{name} linked section is missing')
            continue
        offset = address - text.address
        expected = text.data[offset:offset + size]
        if (offset < 0 or len(expected) != size or section.address != address
                or section.size != size or section.data != expected):
            raise Invalid(f'{name} bytes differ or address/size changed')
        spans[name] = {'status': 'pass', 'address': f'{address:08x}', 'bytes': size,
                       'reference_sha256': sha256(expected), 'comparison_sha256': section.sha256}
    rows = parse_elf(linked)['sections']
    cells = {}
    for name, address in (('db_id', 0x290ac4), ('state_c8', 0x290ac8),
                          ('state_cc', 0x290acc), ('state_d0', 0x290ad0), ('state_d4', 0x290ad4)):
        found = [row for row in rows if row['name'] == '.sbss.fr2_misc3d_' + name]
        if not found:
            missing.append(f'{name} linked cell is missing')
            continue
        cell = found[0]
        if (cell['type'] != 8 or cell['address'] != address or cell['size'] != 4
                or cell['flags'] != 3 or cell['alignment'] != 4):
            raise Invalid(f'{name} layout differs from the recorded four-byte NOBITS cell')
        if '.sbss' not in original:
            missing.append('retail sbss section is missing')
        elif (not original['.sbss'].address <= address
              or address + 4 > original['.sbss'].address + original['.sbss'].size
              or original['.sbss'].has_bytes):
            raise Invalid(f'{name} layout differs from retail NOBITS storage')
        cells[name] = {'address': f'{address:08x}', 'bytes': 4, 'alignment': 4,
                       'type': 'NOBITS', 'has_file_bytes': False, 'matched_file_bytes': 0}
    if missing:
        raise Incomplete('; '.join(missing))
    return {'spans': spans, 'cells': cells}

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {'lifecycle': ROOT / 'reconstruction/ee/app3d/misc3d_lifecycle.c',
           'siblings': ROOT / 'reconstruction/ee/app3d/misc3d_siblings.c',
           'db_id': ROOT / 'reconstruction/ee/app3d/misc3d_db_id_cell.c',
           **{f'state_{suffix}': ROOT / f'reconstruction/ee/app3d/misc3d_state_{suffix}.c'
              for suffix in ('c8', 'cc', 'd0', 'd4')}}
LINK_SCRIPT = ROOT / 'tools/misc3d_lifecycle_recipe/candidate.ld'
DECISION = ROOT / 'notes/evidence/fr2-misc3d-lifecycle/decision.json'
OBSERVATION = ROOT / 'notes/evidence/fr2-misc3d-lifecycle/observation.json'

VALIDATION_INPUTS = [ROOT / 'tools' / relative for relative in (
    'compiler_probe.py', 'compiler_probe_recipe/build.py', 'compiler_probe_recipe/run.py',
    'compiler_probe_recipe/manifest.template.json', 'compiler_probe_recipe/docker-linux-exec.sh',
    'compiler_probe_recipe/docker-wine-exec.sh', 'compiler_output.py', 'corpus_contract.py',
    'evidence_common.py', 'misc3d_contract.py', 'matching_ranges.py', 'matching_sections.py',
    'matching_diff.py', 'ps2_executables.py')]


def provenance() -> dict:
    missing, previous = [], {}
    try:
        previous = previous_provenance()
    except Incomplete as error:
        missing.append(str(error))
        previous = error.details
    paths = {'observation': OBSERVATION, 'link_script': LINK_SCRIPT, **SOURCES}
    if not DECISION.is_file():
        missing.append(f'lifecycle provenance missing: {DECISION}')
        raise Incomplete('; '.join(missing), {'previous_accessor_cell': previous})
    decision = json.loads(DECISION.read_text())
    if decision.get('corpus_sha256') != EE_CORPUS_SHA256:
        raise Invalid('lifecycle decision corpus differs')
    for name, path in paths.items():
        if not path.is_file():
            missing.append(f'lifecycle provenance missing: {path}')
            continue
        if identity(path) != decision['inputs'][name]:
            raise Invalid(f'lifecycle {name} identity differs from recorded decision')
    if OBSERVATION.is_file():
        observation = json.loads(OBSERVATION.read_text())
        if observation.get('status') != 'pass':
            missing.append('lifecycle saved-project observation is incomplete')
        else:
            for name, address, size in SPANS:
                expected = {'address': f'{address:08x}', 'bytes': size,
                            'sha256': observation['details']['spans'][name]['sha256']}
                if decision['spans'][name] != expected:
                    raise Invalid('lifecycle decision scope differs from saved-project observation')
    if missing:
        raise Incomplete('; '.join(missing), {'previous_accessor_cell': previous})
    return {'previous_accessor_cell': previous, 'decision': identity(DECISION),
            'observation': identity(OBSERVATION)}


def build_and_compare(game: Path, tool_root: Path, sources: dict[str, Path] | None = None) -> dict:
    """Diagnostic source/output seam. Ownership credit requires a separate decision.

    Controls may change source inputs here; the acceptance CLI always checks the
    fixed SOURCES through provenance() and never accepts an override.
    """
    if sha256((game / 'extracted/SLES_517.05').read_bytes()) != EE_CORPUS_SHA256:
        raise Invalid('lifecycle build requires the unchanged recorded executable')
    tool_root = tool_root.resolve(strict=True)
    stage = Path(tempfile.mkdtemp(prefix='misc3d-lifecycle-', dir=tool_root))
    manifest_path, _ = build.prepare(game, tool_root, stage)
    run.validate_manifest_runtimes(manifest_path, tool_root)
    runtime = run.validate_runtime_images()
    manifest = json.loads(manifest_path.read_text())
    candidate = next(c for c in manifest['candidates'] if c['id'] == 'ee-gcc2.96')
    artifacts, commands, definitions = {}, [], {}
    selected = SOURCES if sources is None else sources
    if set(selected) != set(SOURCES):
        raise Invalid('diagnostic source set differs from the fixed group')
    for name, source in selected.items():
        staged = stage / (name + '.c')
        obj, prepared = stage / (name + '.o'), stage / (name + '-prepared.o')
        shutil.copyfile(source, staged)
        flags = [*candidate['flags'], *(['-falign-labels=16'] if name == 'siblings' else [])]
        for command in ([*candidate['compile'], *flags, '-c', str(staged), '-o', str(obj)],
                        [*candidate['prepare_object'][:-2], str(obj), str(prepared)]):
            commands.append(command)
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise Incomplete(f'lifecycle source build unavailable: {exc}') from exc
            if result.returncode:
                raise Invalid('lifecycle source compilation/preparation failed',
                              {'argv': command, 'stderr': result.stderr[-2000:]})
        if name not in ('lifecycle', 'siblings'):
            definitions[name] = verify_cell_object(obj.read_bytes(), 'misc3d_' + name)
        artifacts.update({name + '_source': staged, name + '_object': obj,
                          name + '_prepared_object': prepared})
    shutil.copyfile(LINK_SCRIPT, stage / 'candidate.ld')
    candidate['link'] = [arg for arg in candidate['link']
                         if not arg.startswith('--defsym=misc3d_db_id=')]
    candidate['link'] += [str(stage / (name + '-prepared.o')) for name in selected]
    candidate['link'] += ['--defsym=release_database=0x00120aa8',
                          '--defsym=misc3d_source_file=0x002831a8']
    manifest['candidates'] = [candidate]
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    result = run_probe(manifest_path, stage / 'accessor-probe', range_scoped=True)
    if result['status'] == 'incomplete':
        raise Incomplete('lifecycle accessor build is incomplete', result)
    if result['status'] != 'pass':
        raise Invalid('lifecycle accessor bytes no longer match', result)
    argv = result['candidates'][0]['link_argv']
    linked = Path(argv[argv.index('-o') + 1])
    artifacts.update({'linked_output': linked, 'accessor_object': linked.parent / 'candidate.o',
                      'accessor_prepared_object': linked.parent / 'prepared.o',
                      'accessor_source': stage / 'candidate.c', 'comparison': linked.parent / 'function.bin',
                      'link_script': stage / 'candidate.ld', 'manifest': manifest_path})
    comparisons = {}
    for name, _, _ in SPANS:
        comparison = stage / (name + '.comparison.bin')
        comparison.write_bytes(sections(linked.read_bytes())['.text.fr2_misc3d_' + name].data)
        comparisons[name] = {'path': str(comparison), **identity(comparison)}
    try:
        outputs = verify_outputs((game / 'extracted/SLES_517.05').read_bytes(), linked.read_bytes())
    except (Invalid, Incomplete) as exc:
        exc.details.update({'commands': commands, 'accessor_build': result,
                            'artifacts': {name: {'path': str(path), **identity(path)}
                                          for name, path in artifacts.items()},
                            'comparisons': comparisons, 'runtime_identity': runtime})
        raise
    # Compare constants as real source outputs without attributing their ownership.
    original, candidate_sections = sections((game / 'extracted/SLES_517.05').read_bytes()), sections(linked.read_bytes())
    for name in ('.fr2_file', '.fr2_message', '.fr2_lifecycle_message'):
        candidate_section = candidate_sections.get(name)
        if candidate_section is None:
            raise Incomplete('lifecycle diagnostic string section missing')
        matches = [s for s in original.values() if s.has_bytes and s.address <= candidate_section.address
                   and candidate_section.address + candidate_section.size <= s.address + s.size]
        if len(matches) != 1:
            raise Invalid('lifecycle diagnostic string location is ambiguous')
        offset = candidate_section.address - matches[0].address
        if matches[0].data[offset:offset + candidate_section.size] != candidate_section.data:
            raise Invalid('lifecycle diagnostic string bytes differ')
    return {'scope': 'six fixed misc3d spans and five common/NOBITS cells',
            'outputs': outputs, 'comparisons': comparisons, 'runtime_identity': runtime,
            'commands': commands, 'accessor_build': result, 'common_definitions': definitions,
            'artifacts': {name: {'path': str(path), **identity(path)} for name, path in artifacts.items()},
            'source_revision': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                              capture_output=True, text=True, check=True).stdout.strip(),
            'source_tree_dirty': bool(subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT,
                                                       capture_output=True, text=True, check=True).stdout),
            'ownership_status': 'incomplete', 'existing_attributed_match_bytes': 60,
            'new_byte_identical_candidate_bytes': 276, 'new_attributed_match_bytes': 0,
            'issue24_status': 'incomplete', 'issue35_status': 'incomplete', 'ac05_status': 'incomplete',
            'claim_limits': ['Static byte comparisons only; no runtime observation.',
                             'New ownership, sibling caller use, computed aliases and loader contracts remain incomplete.',
                             'Historical compiler identification and whole-image acceptance remain incomplete.']}


def check(game: Path, tool_root: Path) -> dict:
    evidence = provenance()
    result = build_and_compare(game, tool_root)
    result['provenance'] = evidence
    result['unresolved'] = json.loads(DECISION.read_text())['unresolved']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    return write_result(args.output, 'misc3d-lifecycle', lambda: check(args.game, args.tool_root),
                        [path for path in (Path(__file__), DECISION, OBSERVATION, LINK_SCRIPT,
                                           *SOURCES.values(), *VALIDATION_INPUTS) if path.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
