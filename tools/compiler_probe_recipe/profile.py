#!/usr/bin/env python3
"""Run the fixed independent EE compiler panel; retain bounded profile evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from corpus_contract import corpus_identity  # noqa: E402
from compiler_probe import run_probe  # noqa: E402
from compiler_probe_recipe.packages import bind_packages  # noqa: E402
from compiler_probe_recipe import build, run  # noqa: E402
from evidence_common import Incomplete, Invalid, identity, write_result  # noqa: E402
from matching_sections import sections  # noqa: E402

ROOT = TOOLS.parent
DECISION = ROOT / 'notes/evidence/fr2-compiler-probe/profile-units.json'
TEMPLATE = Path(__file__).with_name('manifest.template.json')
CANDIDATE_IDS = tuple(c['id'] for c in json.loads(TEMPLATE.read_text())['candidates'])
UNIT_IDS = ('accessor', 'misc3d_reset', 'entity_set_first', 'parser_lookup')


def summarize(probes: list[dict]) -> dict:
    """Intersect exact linked and pre-link diagnostic results across the fixed panel."""
    if sorted(p.get('unit', '') for p in probes) != sorted(UNIT_IDS):
        raise Incomplete('independent compiler panel is missing or duplicates a required unit')
    surviving = set(CANDIDATE_IDS)
    operational = []
    outcomes = []
    for probe in probes:
        candidates = probe.get('candidates', [])
        if sorted(c.get('id', '') for c in candidates) != sorted(CANDIDATE_IDS):
            raise Incomplete('compiler panel candidate identities differ from the recorded set')
        matches = []
        for candidate in candidates:
            if candidate['status'] not in ('pass', 'fail') or candidate.get('compiler_output', {}).get('status') not in ('pass', 'fail'):
                operational.append({'unit': probe['unit'], 'candidate': candidate['id'],
                                    'reason': candidate.get('reason', candidate.get('compiler_output', {}).get('reason', 'missing compiler diagnostic'))})
            elif candidate['status'] == 'pass' and candidate['compiler_output']['status'] == 'pass':
                matches.append(candidate['id'])
        surviving &= set(matches)
        outcomes.append({'unit': probe['unit'], 'matches': matches})
    status = 'incomplete' if operational or len(surviving) > 1 else ('pass' if surviving else 'fail')
    return {'profile_status': status, 'selected_id': next(iter(surviving)) if status == 'pass' else None,
            'surviving_candidates': sorted(surviving), 'unit_outcomes': outcomes,
            'operational_gaps': operational, 'matched_bytes': 0,
            'ac05_status': 'incomplete',
            'ac05_reason': 'The EE panel bounds a matching profile only. Source forms are inferred/explored, exact historical source/package binding remains #21, and relevant game-owned IOP probes are outside this panel.',
            'claim_limits': ['No original-source identity or full-image compiler claim.',
                             'Pre-link diagnostics exclude relocation fields; exact linked comparisons retain them.',
                             'GNU ld 2.40 placement is a substitution, whose full contract remains #9.',
                             'No ownership change or additional matched-byte credit.',
                             'A byte match establishes no package permission.']}


def execute(game: Path, tool_root: Path) -> dict:
    corpus_identity(game)
    decision = json.loads(DECISION.read_text())
    units = decision['units']
    if [u['id'] for u in units] != list(UNIT_IDS[1:]):
        raise Incomplete('compiler panel unit decision differs from the fixed scope')
    for unit in units:
        source = ROOT / unit['source']
        if not source.is_file() or identity(source)['sha256'] != unit['source_sha256']:
            raise Incomplete(f"independent source identity differs: {unit['id']}")
    source_map = decision['evidence_inputs']['source_map']
    if identity(ROOT / source_map['path'])['sha256'] != source_map['sha256']:
        raise Incomplete('independent source-map identity differs')
    tool_root = tool_root.resolve(strict=True)
    # Keep local generated objects for reproducibility; never publish them.
    staging = Path(tempfile.mkdtemp(prefix='compiler-profile-', dir=tool_root))
    runtime = run.validate_runtime_images()
    text = sections((game / 'extracted/SLES_517.05').read_bytes())['.text']
    probes = []
    for unit in [None, *units]:
        name = unit['id'] if unit else 'accessor'
        output = staging / name
        manifest_path, reference = build.prepare(game, tool_root, output)
        manifest = json.loads(manifest_path.read_text())
        manifest['compiler_diagnostic'] = True
        if unit:
            address, size = int(unit['vaddr'], 16), unit['bytes']
            offset = address - text.address
            if offset < 0 or offset + size > len(text.data):
                raise Invalid(f"independent reference outside .text: {name}")
            payload = text.data[offset:offset + size]
            if hashlib.sha256(payload).hexdigest() != unit['sha256']:
                raise Invalid(f"independent reference identity differs: {name}")
            reference.write_bytes(payload)
            shutil.copyfile(ROOT / unit['source'], output / 'candidate.c')
            symbol = manifest['symbol'] = unit['symbol']
            (output / 'candidate.ld').write_text(
                f'OUTPUT_ARCH(mips)\nSECTIONS {{ .text.{symbol} 0x{address:08x} : {{ *(.text.{symbol}) }} }}\n')
            manifest['evidence']['reference_range'] = {
                'section': '.text', 'vaddr': unit['vaddr'], 'bytes': size,
                'file_offset': f'{text.offset + offset:08x}', 'sha256': unit['sha256'], 'scope': 'mixed'}
            manifest['evidence']['independent_unit'] = unit
            for candidate in manifest['candidates']:
                candidate['link'] = [arg for arg in candidate['link'] if not arg.startswith('--defsym=')]
                candidate['link'] += [f'--defsym={key}=0x{value}' for key, value in
                                     {**unit['definitions'], '_gp': '00295d70'}.items()]
        for candidate in manifest['candidates']:
            candidate['flags'].append('-v')  # driver prints actual cc1/assembler argv
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        run.validate_manifest_runtimes(manifest_path, tool_root)
        packages = bind_packages(manifest, tool_root)
        probe = run_probe(manifest_path, output / 'objects')
        probe['unit'] = name
        probe['package_members'] = packages
        probe['package_identity_status'] = 'pass' if all(d['available_locally'] for d in
            probe['evidence']['tool_distributions']) else 'incomplete'
        probes.append(probe)
    result = summarize(probes)
    if any(p['package_identity_status'] != 'pass' for p in probes):
        result.update(profile_status='incomplete', selected_id=None)
        result['operational_gaps'].append({'reason': 'one or more pinned package archives are missing'})
    result.update(probes=probes, runtime_identity=runtime, decision=identity(DECISION),
                  local_work=str(staging), historical_identity_status=decision['historical_identity_status'])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/compiler-profile'))
    args = parser.parse_args(argv)

    def action():
        result = execute(args.game, args.tool_root)
        if result['profile_status'] == 'incomplete':
            raise Incomplete('independent compiler profile is ambiguous or missing evidence', result)
        if result['profile_status'] == 'fail':
            raise Invalid('independent compiler units contradict a single matching profile', result)
        return result

    inputs = [args.game / 'extracted/SLES_517.05', Path(__file__), DECISION, TEMPLATE,
              Path(build.__file__), Path(run.__file__), Path(__file__).with_name('packages.py'), TOOLS / 'compiler_probe.py',
              TOOLS / 'compiler_output.py', TOOLS / 'ps2_executables.py', TOOLS / 'matching_sections.py',
              TOOLS / 'matching_diff.py', TOOLS / 'corpus_contract.py', TOOLS / 'evidence_common.py',
              build.RECONSTRUCTION_SOURCE, ROOT / 'notes/evidence/fr2-source-map/source-map-result.json',
              *(Path(__file__).with_name(name) for name in
                ('candidate.ld', 'docker-linux-exec.sh', 'docker-wine-exec.sh',
                 'misc3d_reset.c', 'entity_set_first.c', 'parser_lookup.c'))]
    return write_result(args.output, 'compiler-profile-independent', action, inputs)


if __name__ == '__main__':
    raise SystemExit(main())
