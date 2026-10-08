#!/usr/bin/env python3
"""Run the PAL reconstruction checks and retain an honest AC01–AC32 ledger.

There are no scope, skip, threshold, receipt-import or denominator switches.
Required checks without implementations/evidence remain incomplete. Behavior is
reported separately and cannot supply matching credit. This command does not
yet implement a reconstruction build.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import (ADR0005, BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY,
                             SOURCE_MAP, UNIT_SOURCE, UNIT_SOURCE_SHA256,
                             boundary_provenance)

TOOLS = Path(__file__).resolve().parent
CRITERIA = (
    ('Identity and inventory', 'Pin every EE/IOP/VU/archive input to this corpus.'),
    ('Aggregate result contract', 'Full passing reconstruction and handoff remain unimplemented.'),
    ('Non-steerable scope', 'Full build/receipt negative controls remain unimplemented.'),
    ('Complete attribution', 'Measure and record game/SDK/excluded ranges under ADR-0005.'),
    ('Compiler probe', 'Run distinguishing EE/IOP compile-and-diff probes with permitted pinned tools.'),
    ('Linker and layout', 'Pin GNU linker and prove placement/relocation/zero-fill layout.'),
    ('First matching reconstruction', 'Build and byte-match a nonempty evidenced game-owned unit.'),
    ('Full EE matching', 'Rebuild every attributed game-owned EE range from source.'),
    ('Source integrity and interfaces', 'Resolve required source, ABI, types and reference contracts.'),
    ('Discovery reconciliation', 'Reconcile every required unlisted span and computed dispatch.'),
    ('Substitute outputs', 'Build pinned permitted substitutes with documented interfaces.'),
    ('Complete build', 'Clean source builds must produce EE and all 24 module outputs.'),
    ('IOP matching', 'Attribute and rebuild all game-owned IOP ranges.'),
    ('IOP linking contracts', 'Check complete import/export/relocation and provider contracts.'),
    ('EE/IOP handoffs', 'Bind required RPC/shared-buffer callers and handlers with ownership/state.'),
    ('VU encoding', 'Reassemble and byte-compare all eight mnemonic programs.'),
    ('VU entry and state maps', 'Map every required caller, entry, overlay and VIF/VU state contract.'),
    ('Archive completeness', 'Independently traverse and compare every record/payload/gap.'),
    ('Audio contracts', 'Complete loading/upload/playback/looping contracts for all variants.'),
    ('PTG contracts', 'Complete every body/tile/palette/descriptor consumer contract.'),
    ('Models and geometry', 'Complete name-tree/texture/geometry/payload/VU handoffs.'),
    ('Texture coverage', 'Complete all formats, small images, palettes and mip contracts.'),
    ('Remaining asset grammars', 'Complete UI/text/config and remaining archive-derived profiles.'),
    ('Contract evidence', 'Bind every required interface claim to current consumer/profile evidence.'),
    ('Headless oracle interface', 'Prove a bounded windowless/audio-free/focus-free lifecycle.'),
    ('Behavioral observations', 'Compare original and rebuilt observations with identical inputs.'),
    ('Falsifiable gates', 'Run positive/negative/incomplete controls for every extended gate.'),
    ('Reproducibility', 'Compare two clean source builds in separate fresh work directories.'),
    ('Honest progress ledger', 'Establish a nonempty owned denominator and complete rebuild ledger.'),
    ('Evidence and unresolved list', 'Retain current reproducible evidence and falsifiers for every criterion.'),
    ('Public artifacts and licensing', 'Retain current whole-suite/IP/dependency licence acceptance.'),
    ('Final handoff', 'Pass a real aggregate reconstruction run and link final ticket/map receipts.'),
)


def reconstruction_status(criteria: list[dict], ledger: dict, *, authority: str) -> str:
    """The report seam: fixed criteria, mismatch precedence, no vacuous match."""
    expected = [f'AC{n:02d}' for n in range(1, 33)]
    if [row.get('id') for row in criteria] != expected:
        raise Invalid('criterion ledger must contain AC01–AC32 exactly once in recorded order')
    required = [row for row in criteria if row['id'] not in ('AC25', 'AC26')]
    if any(row.get('status') not in ('pass', 'fail', 'incomplete') for row in criteria):
        raise Invalid('criterion has an invalid status')
    if any(row['status'] == 'fail' for row in required):
        return 'fail'
    if (authority != 'real_corpus' or any(row['status'] != 'pass' for row in required)
            or any(not row.get('evidence') for row in required)
            or ledger.get('game_owned_bytes', 0) <= 0 or ledger.get('unresolved_bytes', 0) != 0
            or ledger.get('matched_bytes', 0) != ledger.get('game_owned_bytes')):
        return 'incomplete'
    return 'pass'


def run_child(name: str, arguments: list[str], output: Path) -> tuple[dict, dict]:
    """Run our own independent command in a fresh directory, never import receipts."""
    output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, str(TOOLS / name), *arguments, '--output', str(output)]
    try:
        if not (TOOLS / name).is_file():
            raise FileNotFoundError(name)
        process = subprocess.run(command, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        # Retain an ordinary incomplete child receipt even when launch is unavailable.
        reason = f'child did not finish: {type(exc).__name__}'
        def unavailable():
            raise Incomplete(reason)
        write_result(output, name + ':unavailable', unavailable, [])
        process = None
    if process is not None:
        (output / 'stdout.txt').write_text(process.stdout)
        (output / 'stderr.txt').write_text(process.stderr)
    paths = list(output.glob('*/result.json'))
    if len(paths) != 1:
        raise Invalid(f'{name} did not produce exactly one immutable receipt')
    receipt = paths[0]
    result = json.loads(receipt.read_text())
    status = result.get('status')
    if status not in ('pass', 'fail', 'incomplete') or (process is not None
            and process.returncode != {'pass': 0, 'fail': 1, 'incomplete': 2}[status]):
        raise Invalid(f'{name} exit status contradicts its receipt')
    report = receipt.with_name('report.md')
    if identity(report) != result.get('artifacts', {}).get('report.md'):
        raise Invalid(f'{name} report hash does not match its receipt')
    return {'command': command, 'receipt': str(receipt), **identity(receipt),
            'status': status, 'diagnostics': result.get('diagnostics', [])}, result


def source_unit_credit(game: Path, range_child: dict, range_result: dict,
                       compiler_child: dict, compiler_result: dict) -> int:
    """Validate fresh child/source/ADR bindings before aggregate match credit."""
    source, adr = UNIT_SOURCE, ADR0005
    expected = {'section': '.text', 'vaddr': '001d1800', 'file_offset': '000d2800',
                'bytes': 60, 'sha256': '1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e',
                'scope': 'game_owned'}
    if range_child.get('status') != 'pass' or range_result.get('status') != 'pass':
        return 0
    try:
        def fresh_bound_child(child: dict, value: dict, script: Path) -> bool:
            receipt = Path(child['receipt']).resolve(strict=True)
            if identity(receipt) != {k: child[k] for k in ('bytes', 'sha256')}:
                return False
            if json.loads(receipt.read_text()) != value:
                return False
            command = value.get('command', [])
            if len(command) < 4 or Path(command[0]).resolve() != script.resolve():
                return False
            output_at = command.index('--output') + 1
            return receipt.parent.parent.resolve() == Path(command[output_at]).resolve()

        if not fresh_bound_child(range_child, range_result, TOOLS / 'matching_ranges.py'):
            return 0
        if not fresh_bound_child(compiler_child, compiler_result,
                                 TOOLS / 'compiler_probe_recipe/run.py'):
            return 0
        if range_result['details']['provenance'].get('sources', {}).get(
                'extracted/SLES_517.05') != identity(game / 'extracted/SLES_517.05'):
            return 0
        ee = next(row for row in range_result['details']['artifacts'] if row['artifact'] == 'EE')
        row, = [r for r in ee['ranges'] if r.get('unit') == 'misc3d_db_id']
        source_hash, adr_hash = sha256(source.read_bytes()), sha256(adr.read_bytes())
        evidence = boundary_provenance()
        if evidence is None:
            return 0
        row_identity = (row.get('section'), f"{row['address']:08x}", row['file_offset'],
                        row['length'], row.get('sha256'), row.get('classification'),
                        row.get('reconstruction_source_sha256'),
                        row.get('candidate_source_sha256'), row.get('decision_sha256'),
                        row.get('evidence_inputs'))
        expected_identity = (expected['section'], expected['vaddr'], int(expected['file_offset'], 16),
                             expected['bytes'], expected['sha256'], 'game_owned', UNIT_SOURCE_SHA256,
                             source_hash,
                             adr_hash, evidence)
        if row_identity != expected_identity:
            return 0
        if (compiler_child.get('status') != 'pass' or compiler_result.get('status') != 'pass'
                or compiler_result.get('details', {}).get('ac07_status') != 'pass'
                or compiler_result.get('details', {}).get('ac05_status') != 'incomplete'):
            return 0
        ac07 = compiler_result['details'].get('ac07_evidence', {})
        if (ac07.get('range') != expected or ac07.get('source_sha256') != source_hash
                or ac07.get('decision_sha256') != adr_hash
                or ac07.get('evidence_inputs') != evidence):
            return 0
        inputs = compiler_result.get('inputs', {})
        if inputs.get(str(source.resolve())) != identity(source) \
                or inputs.get(str(adr.resolve())) != identity(adr) \
                or inputs.get(str(SOURCE_MAP.resolve())) != evidence['source_map'] \
                or inputs.get(str(BOUNDARY_METADATA.resolve())) != evidence['metadata'] \
                or inputs.get(str(SAVED_FUNCTION_INVENTORY)) != evidence['saved_function_inventory']:
            return 0
        matches = [c for c in compiler_result['details'].get('candidates', [])
                   if c.get('status') == 'pass' and c.get('gate', {}).get('status') == 'pass']
        if len(matches) != 1:
            return 0
        candidate = matches[0]
        gate = candidate.get('gate', {})
        if (gate.get('matched_bytes') != 60 or gate.get('scope') != 'game_owned'
                or candidate.get('actual_bytes') != 60
                or candidate.get('actual_sha256') != expected['sha256']
                or candidate.get('reference_sha256') != expected['sha256']
                or any(candidate.get(key) != 0 for key in
                       ('compile_returncode', 'link_returncode', 'objcopy_returncode'))):
            return 0
        return 60
    except (KeyError, OSError, TypeError, ValueError, StopIteration):
        return 0


def aggregate_ledger(range_details: dict, credited: int) -> dict:
    """Conserve every initialized/zero-fill byte; matches are owned-byte subsets."""
    keys = ('file_backed_bytes', 'zero_fill_bytes', 'unresolved_bytes',
            'game_owned_bytes', 'substitute_bytes')
    ledger = {key: range_details.get(key, 0) for key in keys}
    total = ledger['file_backed_bytes'] + ledger['zero_fill_bytes']
    expected_unresolved = total - ledger['game_owned_bytes'] - ledger['substitute_bytes']
    if expected_unresolved < 0 or ledger['unresolved_bytes'] != expected_unresolved:
        raise Invalid('range ledger does not conserve initialized and zero-fill bytes', {
            'total_bytes': total, 'game_owned_bytes': ledger['game_owned_bytes'],
            'substitute_bytes': ledger['substitute_bytes'],
            'reported_unresolved_bytes': ledger['unresolved_bytes'],
            'expected_unresolved_bytes': expected_unresolved})
    if credited < 0 or credited > ledger['game_owned_bytes']:
        raise Invalid('matched-byte credit exceeds the attributed game-owned scope', {
            'credited_bytes': credited, 'game_owned_bytes': ledger['game_owned_bytes']})
    ledger['matched_bytes'] = credited
    ledger['substitute_disposition'] = range_details.get(
        'substitute_disposition', 'no ranges attributed as substitute')
    ledger.update(matched_fraction=(credited / ledger['game_owned_bytes']
                                    if ledger['game_owned_bytes'] else 0.0),
                  matched_fraction_scope='attributed_game_owned_bytes',
                  function_owned_bytes=None,
                  function_owned_disposition='Discovery accounting is not matching credit.')
    return ledger


def check(game: Path, output: Path, assembler: Path | None, objdump: Path | None,
          compiler_tools: Path) -> dict:
    children_root = output / ('children-' + uuid.uuid4().hex)
    jobs = [('ranges', 'matching_ranges.py', ['corpus', str(game)]),
            ('archive', 'verify_formats.py', ['corpus', str(game)])]
    vu_arguments = [str(game / 'extracted/SLES_517.05')]
    if assembler is not None:
        vu_arguments += ['--assembler', str(assembler)]
    if objdump is not None:
        vu_arguments += ['--objdump', str(objdump)]
    jobs.append(('vu', 'verify_vu.py', vu_arguments))
    jobs.append(('assets', 'verify_asset_contracts.py',
                 ['archive', str(game / 'extracted/FILES.HDR'), str(game / 'extracted/FILES.DAT')]))
    jobs.append(('compiler', 'compiler_probe_recipe/run.py', [str(game), str(compiler_tools)]))
    children, results = [], {}
    for key, tool, arguments in jobs:
        child, result = run_child(tool, arguments, children_root / key)
        children.append(child)
        results[key] = result
    criteria = [{'id': f'AC{index:02d}', 'name': title, 'status': 'incomplete',
                 'scope': 'behavioral' if index in (25, 26) else 'reconstruction',
                 'reason': blocker, 'evidence': [], 'falsifier': blocker}
                for index, (title, blocker) in enumerate(CRITERIA, 1)]
    def record(index: int, status: str, reason: str, keys: list[int]):
        criteria[index - 1].update(status=status, reason=reason,
                                  evidence=[children[k] for k in keys])
    ranges, archive, vu = (results[key] for key in ('ranges', 'archive', 'vu'))
    identities = [ranges['status'], archive['status']]
    record(1, 'fail' if 'fail' in identities else 'pass' if identities == ['pass', 'pass']
           else 'incomplete', 'Pinned load images, all VU identities, and archive/extracted inventory.', [0, 1])
    record(4, 'fail' if ranges['status'] == 'fail' else 'incomplete',
           'Load-image inventory retained; all but the locally measured range remain unresolved.', [0])
    compiler = results['compiler']
    record(5, 'fail' if compiler['status'] == 'fail' else 'incomplete',
           'Exploratory candidate comparison retained; independent ownership and additional '
           'EE/IOP distinguishing probes are still required.', [4])
    credited = source_unit_credit(game, children[0], ranges, children[4], compiler)
    source_identity_valid = sha256(UNIT_SOURCE.read_bytes()) == UNIT_SOURCE_SHA256
    record(7, 'pass' if credited == 60 else 'fail'
           if compiler['status'] == 'fail' or not source_identity_valid else 'incomplete',
           'One hand-written EE source unit has a fresh, source/decision-bound exact byte build.',
           [0, 4])
    record(18, archive['status'], 'Independent archive/extracted comparison; format support is separate.', [1])
    vu_details = vu['details']
    encoding = vu_details.get('exact_roundtrip_overlays') == 8 and all(
        row.get('byte_gate', {}).get('status') == 'pass' for row in vu_details.get('overlays', []))
    record(16, 'pass' if encoding and ranges['status'] == 'pass' else
           'fail' if vu['status'] == 'fail' else 'incomplete',
           'Eight exact mnemonic comparisons required; entry/state contracts are separate.', [0, 2])
    record(17, 'fail' if vu['status'] == 'fail' else 'incomplete',
           'Required entry/state interfaces remain unresolved.', [2])
    assets = results['assets']
    for index in range(19, 25):
        record(index, 'fail' if assets['status'] == 'fail' else 'incomplete',
               'Archive-derived contract catalog retained; required body/consumer/state semantics '
               'have not been proven by documentation coverage.', [1, 3])
    record(27, 'incomplete',
           'The current positive, mutation and placement controls cover one source unit only; '
           'controls for remaining acceptance gates are not complete.', [0, 4])
    range_details = ranges['details']
    ledger = aggregate_ledger(range_details, credited)
    record(29, 'incomplete',
           'The current partition conserves all load-image bytes, but only one 60-byte owned '
           'range is attributed and matched.', [0, 4])
    record(30, 'incomplete',
           'These current child receipts support the bounded results above; required evidence '
           'and falsifiers for the remaining criteria are still incomplete.', [0, 1, 2, 3, 4])
    record(31, 'incomplete',
           'The exploratory compiler receipt records package provenance; redistribution terms '
           'remain unresolved and no compiler binaries are redistributed.', [4])
    record(32, 'incomplete',
           'Current child receipts and the aggregate are retained, but required final acceptance '
           'and handoff evidence remains incomplete.', [0, 1, 2, 3, 4])
    status = reconstruction_status(criteria, ledger, authority='real_corpus')
    details = {
        'spec': 'https://github.com/nicolas-found42/reverse-engineering/issues/5',
        'criteria': criteria, 'children': children, 'ledger': ledger,
        'reconstruction_status': status,
        'asset_coverage': assets['details'],
        'vu_coverage': {'exact_overlays': vu_details.get('exact_roundtrip_overlays', 0),
                        'entry_map': vu_details.get('entry_map', {}),
                        'interfaces': vu_details.get('interface_status', 'incomplete')},
        'compiler_coverage': compiler['details'],
        'behavioral': {'status': 'incomplete', 'readiness': 'incomplete', 'observations': [],
                       'reason': 'No verified headless original/rebuilt runner or observations.'},
        'real_corpus_completion': status == 'pass',
        'headline': 'Reconstruction ' + status + '; behavior remains unverified.',
        'unresolved': [row for row in criteria if row['status'] == 'incomplete'],
        'claim_limits': ['Only a fresh source/ADR-bound 60-byte EE source unit is credited.',
                         'A structural or encoding child pass is not whole-game completion.',
                         'AC25/AC26 are reported separately as behavioral criteria.'],
    }
    revision = subprocess.run(['git', '-C', str(TOOLS.parent), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, timeout=5)
    dirty = subprocess.run(['git', '-C', str(TOOLS.parent), 'status', '--porcelain',
                            '--untracked-files=no'], capture_output=True, text=True, timeout=5)
    details['source_revision'] = revision.stdout.strip() if revision.returncode == 0 else None
    details['source_working_tree_dirty'] = bool(dirty.stdout) if dirty.returncode == 0 else None
    if status == 'fail':
        raise Invalid('Required reconstruction check failed', details)
    if status == 'incomplete':
        raise Incomplete('Required reconstruction work remains incomplete', details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--assembler', type=Path)
    parser.add_argument('--objdump', type=Path)
    parser.add_argument('--compiler-tools', type=Path,
                        default=TOOLS.parent / '.scratch/compiler-probe-tools')
    args = parser.parse_args()
    compiler_recipe = TOOLS / 'compiler_probe_recipe'
    return write_result(args.output, 'fr2-completion',
                        lambda: check(args.game, args.output, args.assembler, args.objdump,
                                      args.compiler_tools),
                        [Path(__file__), *(TOOLS / name for name in
                          ('matching_ranges.py', 'verify_formats.py', 'verify_vu.py',
                           'verify_asset_contracts.py', 'corpus_contract.py',
                           'compiler_probe.py', 'matching_diff.py', 'matching_sections.py',
                           'ps2_executables.py', 'evidence_common.py')),
                         TOOLS.parent / 'reconstruction/ee/app3d/misc3d_db_id.c',
                         TOOLS.parent / 'docs/adr/0005-game-owned-sdk-boundary.md',
                         SOURCE_MAP,
                         *(p for p in (BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY) if p.is_file()),
                         *(compiler_recipe / name for name in
                          ('run.py', 'build.py', 'candidate.ld',
                            'manifest.template.json', 'docker-linux-exec.sh',
                            'docker-wine-exec.sh'))])


if __name__ == '__main__':
    raise SystemExit(main())
