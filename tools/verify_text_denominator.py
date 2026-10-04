#!/usr/bin/env python3
"""Classify the executable bytes that no saved function owns.

The saved export owns some executable bytes; the rest ("unlisted") is the
denominator that any claim of full code coverage has to account for. This check
splits the unlisted bytes into structural classes using only the executable and
the export. A class says what a span looks like, not what it is: no reachability,
identity or behavior is established. No game code is run.
"""
import argparse
import json
from pathlib import Path

from evidence_common import Incomplete, Invalid, write_result
from ps2_executables import parse_elf
from r5900_shape import is_plausible
from verify_code_inventory import inspect

WORD = 4
JR_RA = 0x03E00008
POINTER_SHARE = 0.6
MIN_NONZERO = 2
CONTROL_SHARE = 0.999
SHF_ALLOC, SHF_EXEC = 2, 4


def _unlisted(data: bytes, static: dict) -> dict:
    try:
        return inspect(data, static)
    except Incomplete as exc:
        if not exc.details:
            raise
        return exc.details


def _words(data: bytes, region: dict, offset: int, size: int) -> list[int]:
    start = region['offset'] + offset
    return [int.from_bytes(data[at:at + WORD], 'little') for at in range(start, start + size, WORD)]


def _kind(words: list[int], targets: list[tuple[int, int]]) -> str:
    nonzero = [w for w in words if w]
    if not nonzero:
        return 'zero_fill'
    if len(nonzero) < MIN_NONZERO:
        return 'sparse_nonzero'
    pointers = sum(1 for w in nonzero if w % WORD == 0 and any(lo <= w < hi for lo, hi in targets))
    if pointers >= POINTER_SHARE * len(nonzero):
        return 'code_pointer_table'
    if all(is_plausible(w) for w in nonzero):
        return 'code_shaped'
    return 'other_nonzero'


def _segments(start: int, size: int, overlays: list[tuple[int, int]]):
    """Split [start, start+size) into (offset, bytes, is_overlay) pieces in file order."""
    pieces, cursor, end = [], start, start + size
    for lo, hi in sorted(overlays):
        lo, hi = max(lo, start), min(hi, end)
        if lo >= hi:
            continue
        if cursor < lo:
            pieces.append((cursor, lo - cursor, False))
        pieces.append((lo, hi - lo, True))
        cursor = hi
    if cursor < end:
        pieces.append((cursor, end - cursor, False))
    return pieces


def _rate(words: list[int]) -> dict:
    nonzero = [w for w in words if w]
    return {'nonzero_words': len(nonzero), 'plausible': sum(is_plausible(w) for w in nonzero)}


def _cross_check(details: dict, coverage: dict) -> dict:
    blocks = {b.get('name'): b for b in coverage.get('blocks', []) if isinstance(b, dict)}
    checked = {}
    for region in details['regions']:
        block = blocks.get(region['name'])
        if block is None:
            continue
        expected = sum(block.get(k, 0) for k in ('unowned_instruction_bytes', 'undefined_bytes', 'defined_data_bytes'))
        if expected != region['unlisted_bytes']:
            raise Invalid(f"coverage and inventory disagree on unlisted bytes of {region['name']}",
                          {'coverage': expected, 'inventory': region['unlisted_bytes']})
        checked[region['name']] = expected
    return checked


def classify_unlisted(data: bytes, static: dict, coverage: dict | None = None) -> dict:
    details = _unlisted(data, static)
    targets = [(r['address'], r['address'] + r['bytes']) for r in details['regions']]
    overlays = [(r['source_offset'], r['source_offset'] + r['bytes']) for r in details['synthetic_regions']]
    owned = [int.from_bytes(bytes.fromhex(row['bytes']), 'little')
             for function in static['functions'] for row in function['instructions']]
    controls = {'owned': _rate(owned), 'data': _rate([
        word for section in parse_elf(data)['sections']
        if section['flags'] & SHF_ALLOC and not section['flags'] & SHF_EXEC
        and section['type'] not in (0, 8) and section['size'] and not section['size'] % WORD
        for word in _words(data, {'offset': 0}, section['offset'], section['size'])])}
    if controls['owned']['plausible'] < CONTROL_SHARE * controls['owned']['nonzero_words']:
        raise Incomplete('shape filter rejects function-owned words; it cannot classify unlisted spans', controls)
    classes: dict[str, dict] = {}
    for region in details['regions']:
        for span in region['unlisted_spans']:
            if span['offset'] % WORD or span['bytes'] % WORD:
                raise Invalid('unlisted span is not word aligned')
            for at, size, overlay in _segments(region['offset'] + span['offset'], span['bytes'], overlays):
                words = _words(data, {'offset': 0}, at, size)
                row = classes.setdefault('vu_microcode' if overlay else _kind(words, targets),
                                         {'bytes': 0, 'spans': 0, 'zero_words': 0, 'with_return': 0})
                row['bytes'] += size
                row['spans'] += 1
                row['zero_words'] += words.count(0)
                row['with_return'] += JR_RA in words
    result = {'executable_sha256': details['executable_sha256'],
              'mapped_executable_bytes': details['mapped_executable_bytes'],
              'function_owned_bytes': details['listed_instruction_bytes'],
              'classes': classes, 'controls': controls,
              'whole_game_decompiled': False,
              'claim_limits': [
                  'Classes describe byte structure only; reachability, identity and behavior are not established.',
                  'code_shaped means every nonzero word passes a field-level R5900 filter that data words often pass; see controls.data.',
                  'zero_fill words may be real nops inside code or alignment padding.',
                  'vu_microcode bytes are the DVP overlay sources; VU semantics are separate.']}
    if coverage is not None:
        result['coverage_cross_check'] = _cross_check(details, coverage)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--coverage', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/text-denominator'))
    args = parser.parse_args()
    inputs = [args.static_export, args.executable] + ([args.coverage] if args.coverage else [])
    return write_result(
        args.output, 'text-denominator',
        lambda: classify_unlisted(args.executable.read_bytes(), json.loads(args.static_export.read_text()),
                                  json.loads(args.coverage.read_text()) if args.coverage else None),
        inputs)


if __name__ == '__main__':
    raise SystemExit(main())
