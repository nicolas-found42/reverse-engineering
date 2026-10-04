#!/usr/bin/env python3
"""Measure the gap-fill method against known function boundaries.

A random share of saved functions is removed from the export as if the
decompiler had never found them; their bytes become undefined. The same seed
rules, batch guard walk and evidence tiers then run on the reduced export, and
the candidates they produce are compared with the removed functions. Recall is
how many removed functions come back with the exact start and end; precision is
how many candidates inside the removed bodies are exact. Saved functions are
themselves provisional, so this measures agreement with them, not with the
original program. No game code is run.
"""
import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

from evidence_common import Invalid, write_result
from gap_seeds import gap_seeds
from verify_gap_candidates import assess_candidates

WORD = 4
PIPELINE = Path(__file__).resolve().parent / 'ghidra/experimental/pipeline'


def contiguous_functions(static: dict, without_callers: bool = False) -> list[tuple[int, int]]:
    """(entry, end) of saved functions whose instruction words fill one gap-free range.

    without_callers keeps only functions the export lists no direct caller for, the population
    that gap-fill candidates come from."""
    found = []
    for function in static['functions']:
        if without_callers and function.get('callers'):
            continue
        addresses = sorted(int(row['address'], 16) for row in function['instructions'])
        if addresses and addresses[-1] - addresses[0] + WORD == len(addresses) * WORD \
                and addresses[0] == int(function['entry'], 16):
            found.append((addresses[0], addresses[-1] + WORD))
    return sorted(found)


def choose_holdout(truth: list[tuple[int, int]], fraction: float, seed: int) -> list[tuple[int, int]]:
    if not 0 < fraction < 1:
        raise Invalid('hold-out fraction must be between 0 and 1')
    return sorted(random.Random(seed).sample(truth, round(len(truth) * fraction)))


def holdout_static(static: dict, held: list[tuple[int, int]]) -> dict:
    entries = {f'{start:08x}' for start, _ in held}
    kept = [f for f in static['functions'] if f['entry'] not in entries]
    return {**static, 'functions': kept, 'inventory_count': len(kept)}


def holdout_coverage(coverage: dict, held: list[tuple[int, int]]) -> dict:
    blocks = []
    for block in coverage['blocks']:
        if block.get('name') != '.text':
            blocks.append(block)
            continue
        inside = [(a, b) for a, b in held if int(block['start'], 16) <= a and b - 1 <= int(block['end'], 16)]
        added = sum(b - a for a, b in inside)
        ranges = list(block['undefined_ranges']) + [
            {'start': f'{a:08x}', 'end': f'{b - 1:08x}', 'bytes': b - a} for a, b in inside]
        blocks.append({**block, 'undefined_ranges': sorted(ranges, key=lambda r: r['start']),
                       'undefined_bytes': block['undefined_bytes'] + added,
                       'function_instruction_bytes': block['function_instruction_bytes'] - added,
                       'instruction_bytes': block['instruction_bytes']})
    return {**coverage, 'blocks': blocks}


def score_candidates(held: list[tuple[int, int]], rows: list[dict], tier_of: dict[str, str] | None = None) -> dict:
    tier_of = tier_of or {}
    truth = {(a, b) for a, b in held}
    starts = {a for a, _ in held}
    exact_truth, start_truth = set(), set()
    inside = {'candidates': 0, 'exact': 0, 'start_only': 0, 'false_start': 0}
    tiers: dict[str, dict] = {}
    straddling = 0
    for row in rows:
        a, b = int(row['start'], 16), int(row['end'], 16)
        owner = next(((x, y) for x, y in held if x <= a and b <= y), None)
        if owner is None:
            straddling += any(a < y and x < b for x, y in held)
            continue
        kind = 'exact' if (a, b) in truth else 'start_only' if a in starts else 'false_start'
        if kind == 'exact':
            exact_truth.add((a, b))
        elif kind == 'start_only':
            start_truth.add(a)
        inside['candidates'] += 1
        inside[kind] += 1
        tier = tiers.setdefault(tier_of.get(row['entry'], '?'),
                                {'candidates': 0, 'exact': 0, 'start_only': 0, 'false_start': 0})
        tier['candidates'] += 1
        tier[kind] += 1
    exact_starts = {a for a, _ in exact_truth}
    recovered = {'exact': len(exact_truth), 'start_only': len(start_truth - exact_starts)}
    recovered['missed'] = len(held) - recovered['exact'] - recovered['start_only']
    return {'held_out': len(held), 'recovered': recovered, 'inside_held_spans': inside, 'straddling': straddling,
            'by_tier': tiers,
            'exact_precision': inside['exact'] / inside['candidates'] if inside['candidates'] else None,
            'exact_recall': recovered['exact'] / len(held) if held else None}


def run_holdout(data: bytes, static: dict, coverage: dict, manifest: Path, *, fraction: float, seed: int,
                work: Path, without_callers: bool = False) -> dict:
    held = choose_holdout(contiguous_functions(static, without_callers), fraction, seed)
    reduced = holdout_static(static, held)
    work.mkdir(parents=True, exist_ok=True)
    (work / 'decompilation').mkdir(exist_ok=True)
    shutil.copy(manifest, work / 'decompilation/manifest.json')
    (work / 'inventory.json').write_text(json.dumps(reduced))
    (work / 'coverage.json').write_text(json.dumps(holdout_coverage(coverage, held)))
    rules = gap_seeds(data, reduced, '.text')
    seeds = sorted(set().union(*rules.values()))
    (work / 'seeds.json').write_text(json.dumps([f'{a:08x}' for a in seeds]))
    subprocess.run([sys.executable, str(PIPELINE / 'make_batch_config.py'), str(work), str(work / 'config.json'),
                    str(work / 'seeds.json'), str(work / 'report.json')], check=True, capture_output=True)
    config = json.loads((work / 'config.json').read_text())
    assessed = assess_candidates(data, reduced, config)
    score = score_candidates(held, config['seeds'], {c['entry']: c['tier'] for c in assessed['candidates']})
    return {'fraction': fraction, 'seed': seed, 'without_callers': without_callers, 'seeds_generated': len(seeds), 'guard_accepted': len(config['seeds']),
            'tiers_all_candidates': assessed['summary']['tiers'], 'score': score,
            'claim_limits': ['Ground truth is the saved functions, themselves provisional structural candidates.',
                             'Only contiguous saved functions can be held out; split bodies are not tested.',
                             'Held-out bytes are marked undefined; real gaps are partly decoded unowned instructions.',
                             'Recall and precision measure agreement with saved functions, not original boundaries.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-dir', type=Path, required=True, help='export with inventory.json, coverage.json, decompilation/manifest.json (relative to the repository root)')
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--fraction', type=float, default=0.2)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--without-callers', action='store_true', help='hold out only functions with no listed direct caller')
    parser.add_argument('--work-dir', type=Path, required=True, help='scratch directory relative to the repository root')
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/holdout-gap-method'))
    args = parser.parse_args()
    return write_result(
        args.output, 'holdout-gap-method',
        lambda: run_holdout(args.executable.read_bytes(), json.loads((args.export_dir / 'inventory.json').read_text()),
                            json.loads((args.export_dir / 'coverage.json').read_text()),
                            args.export_dir / 'decompilation/manifest.json',
                            fraction=args.fraction, seed=args.seed, work=args.work_dir,
                            without_callers=args.without_callers),
        [args.export_dir / 'inventory.json', args.export_dir / 'coverage.json', args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
