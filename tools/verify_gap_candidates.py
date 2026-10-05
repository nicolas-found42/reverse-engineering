#!/usr/bin/env python3
"""Tier gap-fill function candidates by independent static evidence.

A candidate is a seed whose raw-word control-flow walk closed inside bytes no
saved function owns (the batch guard of tools/ghidra/experimental/pipeline).
This check adds evidence that does not depend on that walk: whether the stack
frame it pushes is the one it pops, whether it sits right after a return and
delay slot or ends at a known entry, and whether anything points at its entry.
The same frame test runs on the saved functions as a control. A tier is a
count of independent evidence classes, not a claim of identity, behavior or
runtime reachability. No game code is run.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

from evidence_common import Invalid, write_result
from verify_text_denominator import JR_RA, WORD, _unlisted
from verify_text_references import find_span_references

SP_FRAME = 0x27BD
FRAME_PASSES = {'frame_consistent', 'leaf_consistent', 'no_return'}
RETURN_LOOKBACK = 5


def _signed16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def _sp_adjust(word: int) -> int | None:
    return _signed16(word & 0xFFFF) if word >> 16 == SP_FRAME else None


def frame_category(words: list[int]) -> str:
    """Whether the stack frame pushed at entry is the one popped at each return."""
    returns = [i for i, w in enumerate(words) if w == JR_RA]
    if not returns:
        return 'no_return'
    first = _sp_adjust(words[0])
    if first is None or first >= 0:
        return 'leaf_with_sp_use' if any(_sp_adjust(w) for w in words) else 'leaf_consistent'
    for index in returns:
        window = words[max(0, index + 1 - RETURN_LOOKBACK + 1):index + 2]
        if -first not in [_sp_adjust(w) for w in window]:
            return 'frame_inconsistent'
    return 'frame_consistent'


class _Image:
    def __init__(self, details: dict, data: bytes):
        self.data, self.regions = data, details['regions']

    def word(self, address: int) -> int | None:
        for region in self.regions:
            if region['address'] <= address < region['address'] + region['bytes']:
                at = region['offset'] + address - region['address']
                return int.from_bytes(self.data[at:at + WORD], 'little')
        return None

    def window(self, start: int, end: int) -> list[int]:
        words = [self.word(a) for a in range(start, end, WORD)]
        if None in words:
            raise Invalid('candidate window leaves the executable regions')
        return words


def _tier(classes: list[str]) -> str:
    if len(classes) >= 2:
        return 'A'
    return 'B' if classes and classes != ['layout'] else 'C'


def assess_candidates(data: bytes, static: dict, config: dict) -> dict:
    details = _unlisted(data, static)
    image = _Image(details, data)
    referenced = {int(t, 16) for span in find_span_references(data, static)['spans'] for t in span['targets']}
    rows, tiers, frames = [], collections.Counter(), collections.Counter()
    for seed in config['seeds']:
        start, end = int(seed['start'], 16), int(seed['end'], 16)
        words = image.window(start, end)
        digest = hashlib.sha256(b''.join(w.to_bytes(WORD, 'little') for w in words)).hexdigest()
        if digest != seed['window_sha256']:
            raise Invalid(f"candidate {seed['entry']} window differs from the executable")
        frame = frame_category(words)
        after = image.word(start - 8) == JR_RA
        ends = seed.get('next_state') in ('function_entry', 'batch_entry')
        refs = int(seed['entry'], 16) in referenced
        classes = (['frame'] if frame in FRAME_PASSES else []) + (['layout'] if after or ends else []) \
            + (['reference'] if refs else [])
        tier = _tier(classes)
        tiers[tier] += 1
        frames[frame] += 1
        rows.append({'entry': seed['entry'], 'bytes': end - start, 'frame': frame, 'after_boundary': after,
                     'ends_at_boundary': ends, 'referenced': refs, 'evidence_classes': classes, 'tier': tier})
    control = collections.Counter()
    for function in static['functions']:
        addresses = sorted(int(r['address'], 16) for r in function['instructions'])
        if addresses and addresses[-1] - addresses[0] + WORD == len(addresses) * WORD:
            control[frame_category(image.window(addresses[0], addresses[-1] + WORD))] += 1
    return {'executable_sha256': details['executable_sha256'], 'candidates': rows,
            'summary': {'candidates': len(rows), 'bytes': sum(r['bytes'] for r in rows),
                        'tiers': {k: tiers.get(k, 0) for k in 'ABC'}, 'frames': dict(frames)},
            'controls': {'saved_functions': dict(control)},
            'whole_game_decompiled': False,
            'claim_limits': [
                'A tier counts independent static evidence classes; it is not identity, behavior or runtime reachability.',
                'The frame test passes for leaf code with no stack use and cannot confirm a boundary alone.',
                'Layout evidence (after a return, ends at an entry) partly overlaps how seeds are generated.',
                'Compare candidate frame shares with controls.saved_functions before trusting a tier.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True, help='batch guard config (make_batch_config.py output)')
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/gap-candidates'))
    args = parser.parse_args()
    return write_result(
        args.output, 'gap-candidates',
        lambda: assess_candidates(args.executable.read_bytes(), json.loads(args.static_export.read_text()),
                                  json.loads(args.config.read_text())),
        [args.static_export, args.executable, args.config])


if __name__ == '__main__':
    raise SystemExit(main())
