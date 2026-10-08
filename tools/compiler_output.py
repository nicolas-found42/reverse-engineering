"""Bounded ELF32/MIPS compiler diagnostics, without matching byte credit.

Compare pre-link function instructions with retail, ignoring ONLY fields named
by supported ELF relocations. This is a code-generation diagnostic, not a byte
match: relocation addends, symbol binding and placement still need the exact
linked gate. Unsupported relocations leave the diagnostic incomplete.
"""
from __future__ import annotations

import hashlib
import struct

from evidence_common import Incomplete, Invalid
from ps2_executables import parse_elf

# R_MIPS_26, HI16, LO16, GPREL16. No caller-provided masks.
RELOCATION_MASKS = {4: 0x03FFFFFF, 5: 0xFFFF, 6: 0xFFFF, 7: 0xFFFF}


def compare_object(data: bytes, symbol: str, reference: bytes) -> dict:
    elf = parse_elf(data)
    if elf['type'] != 1:
        raise Incomplete('compiler diagnostic requires an ET_REL object')
    sections = elf['sections']
    named = [(i, s) for i, s in enumerate(sections) if s.get('name') == f'.text.{symbol}']
    if len(named) != 1:
        raise Incomplete('compiler object must contain exactly one function section')
    index, text = named[0]
    actual = data[text['offset']:text['offset'] + text['size']]
    if len(actual) % 4 or len(reference) % 4:
        raise Incomplete('compiler diagnostic requires whole instruction words')
    relocations = []
    masks = {}
    for section in sections:
        if section['info'] != index or section['type'] not in (4, 9):
            continue
        stride = 12 if section['type'] == 4 else 8
        if section['entry_size'] != stride or section['size'] % stride:
            raise Invalid('compiler relocation table has an invalid entry stride')
        payload = data[section['offset']:section['offset'] + section['size']]
        for entry in struct.iter_unpack('<IIi' if stride == 12 else '<II', payload):
            offset, info = entry[:2]
            kind = info & 0xFF
            if kind not in RELOCATION_MASKS:
                raise Incomplete(f'unsupported compiler relocation type {kind}')
            if offset % 4 or offset + 4 > len(actual) or offset in masks:
                raise Invalid('compiler relocation site is duplicate, unaligned or outside function')
            masks[offset] = RELOCATION_MASKS[kind]
            relocations.append({'offset': offset, 'type': kind, 'symbol_index': info >> 8,
                                'mask': f'{masks[offset]:08x}'})
            if stride == 12:
                relocations[-1]['addend'] = entry[2]
    row = {'status': 'pass', 'matched_bytes': 0, 'object_sha256': hashlib.sha256(data).hexdigest(),
           'text_sha256': hashlib.sha256(actual).hexdigest(), 'text_bytes': len(actual),
           'relocations': relocations,
           'claim_limit': 'Non-relocated instruction bits only; no relocation, placement or byte-match proof.'}
    if len(actual) != len(reference):
        row.update(status='fail', first_difference={'offset': min(len(actual), len(reference)),
                    'reason': 'function length differs', 'expected_bytes': len(reference),
                    'actual_bytes': len(actual)})
        return row
    for at in range(0, len(actual), 4):
        expected = struct.unpack_from('<I', reference, at)[0]
        observed = struct.unpack_from('<I', actual, at)[0]
        mask = masks.get(at, 0)
        if (expected ^ observed) & (~mask & 0xFFFFFFFF):
            row.update(status='fail', first_difference={'offset': at, 'word_index': at // 4,
                       'expected': f'{expected:08x}', 'actual': f'{observed:08x}',
                       'relocation_mask': f'{mask:08x}'})
            break
    return row
