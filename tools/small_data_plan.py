#!/usr/bin/env python3
"""Plan data types for gp-relative small-data globals from the widths and kinds of the accesses in saved functions.

Every instruction of the form `lw v0,-0x6ee8(gp)` reads or writes the global at gp+offset. The mnemonic fixes the access
width, and an FPU load or store shows a float; `lb` and `lbu` (or `lh` and `lhu`) show how the code extends a byte or half.
A global gets a type only when every access agrees and the address is not used as the base of an array or structure.
Integer words stay untyped because the code cannot tell an integer from a pointer. The plan is evidence about access
patterns, not original names or declared types. No game code is run.
"""
import argparse
import collections
import json
import re
from pathlib import Path

from evidence_common import Incomplete, sha256

ADDRESS = re.compile(r'[0-9a-f]{8}')
MEMORY_OP = re.compile(r'^(\w+)\s+\w+,(-?0x[0-9a-f]+|-?\d+)\((\w+)\)$')
ADDRESS_OP = re.compile(r'^addiu\s+\w+,gp,(-?0x[0-9a-f]+|-?\d+)$')
INDEX_OP = re.compile(r'^addu\s+(\w+),(?:\w+,gp|gp,\w+)$')
WIDTH = {'lb': 1, 'lbu': 1, 'sb': 1, 'lh': 2, 'lhu': 2, 'sh': 2, 'lw': 4, 'lwu': 4, 'sw': 4, 'lwc1': 4, 'swc1': 4,
         'ld': 8, 'sd': 8, 'lq': 16, 'sq': 16}
FLOAT_OPS = {'lwc1', 'swc1'}
UNALIGNED = {'lwl', 'lwr', 'swl', 'swr', 'ldl', 'ldr', 'sdl', 'sdr'}
SIGNED = {1: ('lb', 'lbu', 'char', 'uchar'), 2: ('lh', 'lhu', 'short', 'ushort')}
INDEX_LOOKAHEAD = 8
SMALL_DATA = ('.sdata', '.sbss')
LITERAL_POOL = '.lit4'
STORES = {'sb', 'sh', 'sw', 'sd', 'sq', 'swc1', 'swl', 'swr', 'sdl', 'sdr'}


def _signed(text: str) -> int:
    return int(text, 0)


def _scan(static: dict, gp: int) -> tuple[dict, set]:
    accesses: dict[int, dict] = {}
    taken: set[int] = set()
    for function in static['functions']:
        texts = [i['text'].lstrip('_') for i in function['instructions']]
        for at, text in enumerate(texts):
            match = MEMORY_OP.match(text)
            if match and match[3] == 'gp' and (match[1] in WIDTH or match[1] in UNALIGNED):
                slot = accesses.setdefault((gp + _signed(match[2])) & 0xFFFFFFFF, {'ops': collections.Counter(), 'functions': set()})
                slot['ops'][match[1]] += 1
                slot['functions'].add(function['entry'])
                continue
            address = ADDRESS_OP.match(text)
            if address:
                taken.add((gp + _signed(address[1])) & 0xFFFFFFFF)
                continue
            index = INDEX_OP.match(text)
            if index:
                for later in texts[at + 1:at + 1 + INDEX_LOOKAHEAD]:
                    use = MEMORY_OP.match(later)
                    if use and use[3] == index[1]:
                        taken.add((gp + _signed(use[2])) & 0xFFFFFFFF)
    return accesses, taken


def _classify(ops: collections.Counter) -> tuple[str | None, str | None]:
    if any(op in UNALIGNED for op in ops):
        return None, 'unaligned_access'
    widths = {WIDTH[op] for op in ops}
    if len(widths) > 1:
        return None, 'mixed_widths'
    width = widths.pop()
    if width == 4:
        return ('float', None) if any(op in FLOAT_OPS for op in ops) else (None, 'integer_or_pointer_word')
    if width in SIGNED:
        signed_op, unsigned_op, signed_type, unsigned_type = SIGNED[width]
        if signed_op in ops:
            return signed_type, None
        if unsigned_op in ops:
            return unsigned_type, None
        return None, 'no_sign_evidence'
    return None, 'wide_access'


def build_plan(static: dict, gp: int, inventory_sha: str) -> dict:
    named = {b['name']: (int(b['start'], 16), int(b['end'], 16)) for b in static.get('memory', []) if ADDRESS.fullmatch(b['start']) and ADDRESS.fullmatch(b['end'])}
    blocks = [named[n] for n in SMALL_DATA if n in named]
    pool = named.get(LITERAL_POOL)
    accesses, taken = _scan(static, gp)
    skipped: collections.Counter = collections.Counter()
    sizes = {a: max(WIDTH.get(op, 4) for op in slot['ops']) for a, slot in accesses.items()}
    starts = sorted(accesses)
    overlapping = set()
    for earlier, later in zip(starts, starts[1:]):
        if earlier + sizes[earlier] > later:
            overlapping.update((earlier, later))

    def in_pool(address: int) -> bool:
        return pool is not None and pool[0] <= address <= pool[1]
    constant_pool = None
    if pool is not None:
        in_block = [a for a in starts if in_pool(a)]
        writes = sum(n for a in in_block for op, n in accesses[a]['ops'].items() if op in STORES)
        reads = sum(n for a in in_block for op, n in accesses[a]['ops'].items() if op not in STORES)
        if in_block and not writes and not any(in_pool(a) for a in taken):
            constant_pool = {'name': LITERAL_POOL, 'start': f'{pool[0]:08x}', 'end': f'{pool[1]:08x}',
                             'addresses': len(in_block), 'reads': reads, 'writes': writes}
    entries = []
    for address in starts:
        slot = accesses[address]
        if in_pool(address) and any(op in STORES for op in slot['ops']):
            skipped['written_literal_pool'] += 1
        elif address in taken:
            skipped['address_taken'] += 1
        elif not (any(lo <= address <= hi for lo, hi in blocks) or in_pool(address)):
            skipped['outside_small_data'] += 1
        elif address in overlapping:
            skipped['overlaps_neighbour'] += 1
        else:
            type_name, reason = _classify(slot['ops'])
            if type_name is None:
                skipped[reason] += 1
            else:
                entry = {'address': f'{address:08x}', 'type': type_name, 'size': sizes[address],
                         'evidence': dict(sorted(slot['ops'].items())), 'functions': sorted(slot['functions'])}
                if constant_pool is not None and in_pool(address):
                    entry['mutability'] = 'constant'
                entries.append(entry)
    return {'schema_version': 1, 'gp_value': f'{gp:08x}', 'inventory_sha256': inventory_sha, 'entries': entries,
            'constant_pool': constant_pool,
            'accessed_addresses': len(accesses), 'skipped': dict(sorted(skipped.items())),
            'type_counts': dict(collections.Counter(e['type'] for e in entries)),
            'claim_limits': ['Types come from access widths and kinds; they are not original declarations or names.',
                             'Integer words are left untyped: an integer and a pointer use the same instructions.',
                             'Addresses used as array or structure bases are left untyped.',
                             'A constant mark rests on no write in the saved functions; unsaved code could still write.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--gp', type=lambda t: int(t, 0), default=0x295D70)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.static_export.read_bytes()
    plan = build_plan(json.loads(data), args.gp, sha256(data))
    if not plan['entries']:
        raise Incomplete('no typed small-data globals', plan)
    args.output.write_text(json.dumps(plan, indent=1) + '\n')
    print(len(plan['entries']), 'entries', plan['type_counts'], plan['skipped'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
