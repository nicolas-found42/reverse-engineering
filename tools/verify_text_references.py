#!/usr/bin/env python3
"""Find what points at the code-shaped bytes that no saved function owns.

Takes the code-shaped spans from verify_text_denominator and records every
static reference into them: direct jumps, calls and branches and lui+addiu/ori
address constants in function-owned code, aligned pointers in data sections,
and direct jumps between spans. A span with an owned-code or data reference is
anchored; one reached only through an anchored span is reachable from it; the
rest has no static reference at all. A reference is evidence of a candidate
entry address, not of a function boundary, identity or runtime reachability.
No game code is run.
"""
import argparse
import json
from bisect import bisect_right
from pathlib import Path

from evidence_common import write_result
from ps2_executables import parse_elf
from verify_text_denominator import (
    SHF_ALLOC,
    SHF_EXEC,
    WORD,
    _controls,
    _unlisted,
    _words,
    segments,
)

J, JAL, ADDIU, ORI, LUI = 2, 3, 9, 0x0D, 0x0F
BRANCH_OPS = {4, 5, 6, 7, 0x14, 0x15, 0x16, 0x17}
COP_BRANCH_OPS = {0x10, 0x11, 0x12}
REGIMM_BRANCH = {0, 1, 2, 3, 0x10, 0x11, 0x12, 0x13}
CONSTANT_WINDOW = 4


def _signed16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def _direct_target(word: int, pc: int) -> int | None:
    op = word >> 26
    if op in (J, JAL):
        return ((pc + 4) & 0xF0000000) | ((word & 0x3FFFFFF) << 2)
    is_branch = (op in BRANCH_OPS or (op == 1 and (word >> 16) & 0x1F in REGIMM_BRANCH)
                 or (op in COP_BRANCH_OPS and (word >> 21) & 0x1F == 8))
    if is_branch:
        return (pc + 4 + (_signed16(word & 0xFFFF) << 2)) & 0xFFFFFFFF
    return None


def _address_constants(rows: list[tuple[int, int]]):
    """Yield (pc, value) for lui rt followed within a short window by addiu/ori rs=rt."""
    for index, (pc, word) in enumerate(rows):
        if word >> 26 != LUI:
            continue
        register, high = (word >> 16) & 0x1F, word & 0xFFFF
        for _, later in rows[index + 1:index + 1 + CONSTANT_WINDOW]:
            if later >> 26 in (ADDIU, ORI) and (later >> 21) & 0x1F == register:
                low = later & 0xFFFF
                yield pc, ((high << 16) + _signed16(low) if later >> 26 == ADDIU else (high << 16) | low) & 0xFFFFFFFF
                break


class _Spans:
    def __init__(self, pieces: list[dict]):
        self.pieces = sorted((p for p in pieces if p['kind'] == 'code_shaped'), key=lambda p: p['address'])
        self.starts = [p['address'] for p in self.pieces]

    def find(self, address: int) -> int | None:
        index = bisect_right(self.starts, address) - 1
        if index >= 0 and address < self.pieces[index]['address'] + self.pieces[index]['bytes'] and address % WORD == 0:
            return index
        return None


def find_span_references(data: bytes, static: dict) -> dict:
    details = _unlisted(data, static)
    controls = _controls(data, static)
    spans = _Spans(segments(data, details))
    incoming: list[dict[str, int]] = [{} for _ in spans.pieces]
    targets: list[set[int]] = [set() for _ in spans.pieces]
    edges: list[set[int]] = [set() for _ in spans.pieces]

    def note(kind: str, address: int, source_span: int | None = None) -> None:
        hit = spans.find(address)
        if hit is None or hit == source_span:
            return
        incoming[hit][kind] = incoming[hit].get(kind, 0) + 1
        targets[hit].add(address)
        if source_span is not None:
            edges[source_span].add(hit)

    entries = {int(f['entry'], 16) for f in static['functions']}
    for function in static['functions']:
        rows = [(int(r['address'], 16), int.from_bytes(bytes.fromhex(r['bytes']), 'little'))
                for r in function['instructions']]
        for pc, word in rows:
            target = _direct_target(word, pc)
            if target is not None:
                note('owned_direct', target)
        for _, value in _address_constants(rows):
            note('owned_address_constant', value)
    for index, piece in enumerate(spans.pieces):
        for offset, word in enumerate(piece['words']):
            target = _direct_target(word, piece['address'] + offset * WORD)
            if target is not None:
                note('span_direct', target, index)

    ranges = [(r['address'], r['address'] + r['bytes']) for r in details['regions']]
    aligned = misaligned = at_entries = 0
    for section in parse_elf(data)['sections']:
        if (section['flags'] & SHF_ALLOC and not section['flags'] & SHF_EXEC and section['type'] not in (0, 8)
                and section['size'] and not section['size'] % WORD):
            for word in _words(data, {'offset': 0}, section['offset'], section['size']):
                if any(lo <= word < hi for lo, hi in ranges):
                    aligned += word % WORD == 0
                    misaligned += word % WORD != 0
                    at_entries += word in entries
                    if word % WORD == 0:
                        note('data_pointer', word)
    controls['data_words_in_executable_range'] = {'aligned': aligned, 'misaligned': misaligned}
    controls['data_words_at_function_entries'] = at_entries

    anchored = [bool(set(row) & {'owned_direct', 'owned_address_constant', 'data_pointer'}) for row in incoming]
    queue = [i for i, a in enumerate(anchored) if a]
    reached = set(queue)
    while queue:
        for nxt in edges[queue.pop()]:
            if nxt not in reached:
                reached.add(nxt)
                queue.append(nxt)
    rows, summary = [], {k: {'spans': 0, 'bytes': 0} for k in ('anchored', 'reached_via_spans_only', 'unreferenced')}
    for index, piece in enumerate(spans.pieces):
        group = 'anchored' if anchored[index] else 'reached_via_spans_only' if index in reached else 'unreferenced'
        summary[group]['spans'] += 1
        summary[group]['bytes'] += piece['bytes']
        rows.append({'address': f"{piece['address']:08x}", 'bytes': piece['bytes'], 'region': piece['region'],
                     'incoming': incoming[index], 'targets': [f'{t:08x}' for t in sorted(targets[index])],
                     'anchored': anchored[index], 'reached': index in reached})
    return {'executable_sha256': details['executable_sha256'], 'spans': rows, 'summary': summary,
            'controls': controls, 'whole_game_decompiled': False,
            'claim_limits': [
                'A reference is a candidate entry address, not a function boundary, identity or runtime reachability.',
                'lui+addiu/ori pairs are matched by register within a short window and can be false positives.',
                'Data pointers are aligned words in non-executable sections; see controls for the misaligned baseline.',
                'Spans with no static reference may still be reached by computed jumps or be dead code.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/text-references'))
    args = parser.parse_args()
    return write_result(
        args.output, 'text-references',
        lambda: find_span_references(args.executable.read_bytes(), json.loads(args.static_export.read_text())),
        [args.static_export, args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
