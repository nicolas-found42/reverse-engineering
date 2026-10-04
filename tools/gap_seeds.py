#!/usr/bin/env python3
"""Derive candidate function entry seeds from the unowned code-shaped spans.

Each rule is deterministic and names why an address might start a function:
the start of a span, the word after a return and its delay slot, a stack-frame
prologue, or a static reference target. Seeds are inputs to the batch guard
walk, which decides whether a closed body exists; a seed is not evidence of a
function by itself. No game code is run.
"""
import argparse
import json
from pathlib import Path

from evidence_common import Invalid, write_result
from verify_text_denominator import JR_RA, WORD, _unlisted, segments
from verify_text_references import find_span_references

SP_PUSH = 0x27BD
SIGN_BIT = 0x8000


def _prologue(word: int) -> bool:
    return word >> 16 == SP_PUSH and bool(word & SIGN_BIT)


def gap_seeds(data: bytes, static: dict, region: str | None = None) -> dict[str, set[int]]:
    rules: dict[str, set[int]] = {k: set() for k in (
        'span_start_prologue', 'span_start_any', 'reference_target', 'after_return_in_span',
        'after_return_prologue', 'prologue_anywhere')}
    for piece in segments(data, _unlisted(data, static)):
        if piece['kind'] != 'code_shaped' or region not in (None, piece['region']):
            continue
        words, base = piece['words'], piece['address']
        for index, word in enumerate(words):
            at = base + index * WORD
            if _prologue(word):
                rules['prologue_anywhere'].add(at)
                if index == 0:
                    rules['span_start_prologue'].add(at)
            if index == 0 and word:
                rules['span_start_any'].add(at)
            if index >= 2 and words[index - 2] == JR_RA and word:
                rules['after_return_in_span'].add(at)
                if _prologue(word):
                    rules['after_return_prologue'].add(at)
    for span in find_span_references(data, static)['spans']:
        if region in (None, span['region']):
            rules['reference_target'].update(int(t, 16) for t in span['targets'])
    return rules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--region', default='.text')
    parser.add_argument('--seeds-out', type=Path, required=True, help='JSON list of hex entries (union of all rules)')
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/gap-seeds'))
    args = parser.parse_args()

    def action() -> dict:
        rules = gap_seeds(args.executable.read_bytes(), json.loads(args.static_export.read_text()), args.region)
        union = sorted(set().union(*rules.values()))
        if not union:
            raise Invalid('no seeds were derived')
        args.seeds_out.parent.mkdir(parents=True, exist_ok=True)
        args.seeds_out.write_text(json.dumps([f'{a:08x}' for a in union]) + '\n')
        return {'rules': {k: len(v) for k, v in rules.items()}, 'union': len(union),
                'claim_limits': ['Seeds are candidates for the guard walk, not functions.']}
    return write_result(args.output, 'gap-seeds', action, [args.static_export, args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
