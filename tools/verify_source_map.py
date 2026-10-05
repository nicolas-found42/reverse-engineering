#!/usr/bin/env python3
"""Map saved functions to the source files named by strings their code references.

Many functions pass a `__FILE__` string and a `__LINE__` immediate to a report
routine. The strings and their references come from the saved export. For each
source path this records the functions that reference it and the line numbers
loaded next to the call, then tests two layout predictions that a real source
map should satisfy for .c/.cpp units: functions of one file sit close together,
and their line numbers rise with address. Headers can be inlined anywhere, so
they are listed but left out of both tests. The line-order test is compared with a shuffled
control. A reference shows that a function mentions a path, not that the
function was written in that file. No game code is run.
"""
import argparse
import collections
import json
import random
import re
from bisect import bisect_right
from itertools import pairwise
from pathlib import Path

from evidence_common import Incomplete, write_result

ADDRESS = re.compile(r'[0-9a-f]{8}')
SOURCE = re.compile(r'\.(?:c|cc|cpp|h|hpp)$')
HEADER = re.compile(r'\.(?:h|hpp)$')
LINE_IMMEDIATE = re.compile(r'^_?(?:li|addiu|ori)\s+a1,(?:zero,)?(-?0x[0-9a-f]+|-?[0-9]+)$')
CALL_WINDOW = 10
LINE_LOOKBACK = 6


def _line_near(instructions: list[dict], at: int) -> int | None:
    call = next((q for q in range(at, min(at + CALL_WINDOW, len(instructions)))
                 if instructions[q]['text'].lstrip('_').startswith('jal ')), None)
    if call is None:
        return None
    line = None
    for q in range(max(0, at - LINE_LOOKBACK), min(call + 2, len(instructions))):
        match = LINE_IMMEDIATE.match(instructions[q]['text'])
        if match:
            line = int(match[1], 0)
    return line


def _inversion_counts(files: dict[str, dict[int, int]]) -> tuple[int, int]:
    pairs = inversions = 0
    for by_function in files.values():
        sequence = [by_function[entry] for entry in sorted(by_function)]
        pairs += max(len(sequence) - 1, 0)
        inversions += sum(later < earlier for earlier, later in pairwise(sequence))
    return pairs, inversions


def _string_attribution(static: dict, per_file: dict[str, dict[str, list[int]]]) -> dict:
    """Attribute functions to units by where the strings they use sit relative to each unit's path string."""
    strings = [s for s in static.get('strings', []) if ADDRESS.fullmatch(s['address'])]
    first: dict[str, int] = {}
    for string in strings:
        first[string['value']] = min(first.get(string['value'], 1 << 40), int(string['address'], 16))
    anchors = sorted((first[path], path) for path in per_file if path in first and not HEADER.search(path))
    starts = [address for address, _ in anchors]
    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for string in strings:
        if SOURCE.search(string['value']):
            continue
        at = bisect_right(starts, int(string['address'], 16)) - 1
        if at < 0:
            continue
        for reference in string.get('references', []):
            if reference.get('function'):
                votes[reference['function']][anchors[at][1]] += 1
    known: dict[str, set[str]] = {}
    for path, by_function in per_file.items():
        if not HEADER.search(path):
            for entry in by_function:
                known.setdefault(entry, set()).add(path)
    agree = disagree = ties = silent = 0
    attributed = []
    for entry, counter in sorted(votes.items()):
        ranked = counter.most_common()
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            ties += entry in known
            continue
        if entry in known:
            agree += ranked[0][0] in known[entry]
            disagree += ranked[0][0] not in known[entry]
        else:
            attributed.append({'entry': entry, 'unit': ranked[0][0], 'votes': ranked[0][1]})
    silent = sum(entry not in votes for entry in known)
    return {'agree': agree, 'disagree': disagree, 'ties': ties, 'known_without_other_strings': silent,
            'functions': attributed}


def build_source_map(static: dict, control_trials: int = 200, seed: int = 1) -> dict:
    functions = {f['entry']: f for f in static['functions']}
    position = {int(i['address'], 16): (f['entry'], k)
                for f in static['functions'] for k, i in enumerate(f['instructions'])}
    per_file: dict[str, dict[str, list[int]]] = {}
    with_line = without_line = 0
    for string in static.get('strings', []):
        if not SOURCE.search(string['value']):
            continue
        for reference in string.get('references', []):
            where = position.get(int(reference['from'], 16))
            if where is None:
                continue
            entry, at = where
            line = _line_near(functions[entry]['instructions'], at)
            bucket = per_file.setdefault(string['value'], {}).setdefault(entry, [])
            if line is None:
                without_line += 1
            else:
                with_line += 1
                bucket.append(line)
    entries = sorted(int(e, 16) for e in functions)
    blocks = [(b['name'], int(b['start'], 16), int(b['end'], 16)) for b in static.get('memory', [])
              if ADDRESS.fullmatch(b['start']) and ADDRESS.fullmatch(b['end'])] or [('all', 0, 0xFFFFFFFF)]

    def block_of(address: int) -> str:
        return next((name for name, lo, hi in blocks if lo <= address <= hi), 'unmapped')
    files = []
    for path, by_function in per_file.items():
        grouped: dict[str, list[int]] = {}
        for entry in by_function:
            grouped.setdefault(block_of(int(entry, 16)), []).append(int(entry, 16))
        ranges = []
        for block, members in sorted(grouped.items(), key=lambda kv: min(kv[1])):
            first, last = min(members), max(members)
            ranges.append({'block': block, 'first': f'{first:08x}', 'last': f'{last:08x}',
                           'referencing_functions': len(members),
                           'functions_in_range': sum(first <= e <= last for e in entries)})
        files.append({'path': path, 'kind': 'header' if HEADER.search(path) else 'unit', 'ranges': ranges,
                      'functions': [{'entry': e, 'lines': sorted(set(by_function[e]))} for e in sorted(by_function)]})
    files.sort(key=lambda f: (f['ranges'][0]['first'], f['path']))
    lowest = {path: {int(e, 16): min(lines) for e, lines in by_function.items() if lines}
              for path, by_function in per_file.items() if not HEADER.search(path)}
    pairs, inversions = _inversion_counts(lowest)
    rng = random.Random(seed)
    rates = []
    for _ in range(control_trials):
        shuffled = {}
        for path, by_function in lowest.items():
            values = list(by_function.values())
            rng.shuffle(values)
            shuffled[path] = dict(zip(sorted(by_function), values))
        control_pairs, control_inversions = _inversion_counts(shuffled)
        rates.append(control_inversions / control_pairs if control_pairs else 0.0)
    spans = [(f['path'], r['block'], int(r['first'], 16), int(r['last'], 16)) for f in files if f['kind'] == 'unit' for r in f['ranges']]
    overlapping = len({(min(p1, p2), max(p1, p2)) for i, (p1, k1, a1, b1) in enumerate(spans)
                       for p2, k2, a2, b2 in spans[i + 1:] if p1 != p2 and k1 == k2 and a1 <= b2 and a2 <= b1})
    return {'files': files,
            'summary': {'files': len(files), 'referencing_functions': len({e for v in per_file.values() for e in v}),
                        'call_sites_with_line': with_line, 'references_without_line': without_line,
                        'overlapping_file_pairs': overlapping,
                        'translation_units': sum(f['kind'] == 'unit' for f in files),
                        'headers': sum(f['kind'] == 'header' for f in files)},
            'string_attribution': _string_attribution(static, per_file),
            'line_order': {'pairs': pairs, 'inversions': inversions,
                           'inversion_rate': inversions / pairs if pairs else None,
                           'shuffled_inversion_rate': sum(rates) / len(rates) if rates else None,
                           'control_trials': control_trials, 'seed': seed},
            'whole_game_decompiled': False,
            'claim_limits': [
                'A reference shows a function mentions a source path; it does not prove the function was written in that file.',
                'Line numbers are the immediate loaded into a1 near the call; other call shapes are counted as without a line.',
                'Functions never referencing a path are unmapped; their file is not inferred here.',
                'Source paths are strings from the game; they say nothing about code behavior or original function names.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/source-map'))
    args = parser.parse_args()

    def action() -> dict:
        result = build_source_map(json.loads(args.static_export.read_text()))
        if not result['files']:
            raise Incomplete('no source file strings with code references were found', result)
        return result
    return write_result(args.output, 'source-map', action, [args.static_export])


if __name__ == '__main__':
    raise SystemExit(main())
