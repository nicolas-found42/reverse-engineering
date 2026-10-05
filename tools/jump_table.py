#!/usr/bin/env python3
"""Recognise the compiler's switch jump through a table, from the instruction words before a `jr`.

GCC for this target bounds the index with `sltiu`, branches to the default case, scales the index with `sll rd,idx,2`,
adds it to a `lui` (and optional `addiu`) table address, loads the word with `lw` and jumps through it. The table address
and the case count come straight from those words, so the table can be read from the executable and checked. Anything that
differs from this shape is refused. The result is evidence about a computed jump's possible targets, not about what the
code means. No game code is run.
"""
import struct

from evidence_common import Invalid
from ps2_executables import parse_elf

WINDOW = 14
MAX_CASES = 256
JR_FN, SLL_FN, ADDU_FN = 0x08, 0x00, 0x21
OP_BEQ, OP_BNE, OP_ADDIU, OP_SLTIU, OP_LUI, OP_LW = 0x04, 0x05, 0x09, 0x0B, 0x0F, 0x23
NON_WRITING_FUNCTIONS = {0x08, 0x0C, 0x0D, 0x18, 0x19, 0x1A, 0x1B, 0x11, 0x13}
INTEGER_FUNCTIONS = {0, 2, 3, 4, 6, 7, 10, 11, 16, 18, 20, 22, 23,
                     32, 33, 34, 35, 36, 37, 38, 39, 42, 43, 44, 45, 46, 47,
                     56, 58, 59, 60, 62, 63}


def _signed(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def _destination(word: int) -> int | None:
    op = word >> 26
    if op == 0:
        if word == 0 or word & 0x3F in NON_WRITING_FUNCTIONS:
            return None
        return (word >> 11 & 31 or None) if word & 0x3F in INTEGER_FUNCTIONS else -1
    if 0x08 <= op <= 0x0F or 0x20 <= op <= 0x27:
        return word >> 16 & 31 or None
    if op in (OP_BEQ, OP_BNE, 0x28, 0x29, 0x2B, 0x2C, 0x2D, 0x2E, 0x3F):
        return None
    # An unmodelled instruction must not hide a register clobber.
    return -1


def _first_write(get, register: int, before: int, floor: int):
    if register == 0:
        return None
    pc = before - 4
    while pc >= floor and before - pc <= WINDOW * 4:
        word = get(pc)
        if _destination(word) == -1:
            return None
        if _destination(word) == register:
            return pc, word
        pc -= 4
    return None


def recognize(get, site: int, floor: int) -> dict | None:
    """Infer the bounded dispatch profile; get reads instruction words, floor limits look-back.

    This local pattern alone does not establish that all incoming CFG paths pass
    the bound. Callers must check the dispatch region's incoming edges separately.
    """
    if site % 4 or floor % 4 or site < floor:
        return None
    floor = max(floor, site - WINDOW * 4)
    jump = get(site)
    if jump >> 26 != 0 or jump & 0x1FFFFF != JR_FN or jump >> 21 & 31 in (0, 31):
        return None
    jump_register = jump >> 21 & 31
    pc = site - 4
    while pc >= floor and get(pc) == 0:
        pc -= 4
    if pc < floor:
        return None
    load = get(pc)
    if load >> 26 != OP_LW or load >> 16 & 31 != jump_register:
        return None
    base_register, offset = load >> 21 & 31, _signed(load & 0xFFFF)
    add = _first_write(get, base_register, pc, floor)
    if add is None or add[1] >> 26 != 0 or add[1] & 0x7FF != ADDU_FN:
        return None
    add_pc, add_word = add
    operands = (add_word >> 21 & 31, add_word >> 16 & 31)
    table = index_register = None
    for first, second in (operands, operands[::-1]):
        high = _first_write(get, first, add_pc, floor)
        scale = _first_write(get, second, add_pc, floor)
        if high is None or scale is None:
            continue
        constant = 0
        high_pc, high_word = high
        if high_word >> 26 == OP_ADDIU and high_word >> 21 & 31 == first:
            constant = _signed(high_word & 0xFFFF)
            lui = _first_write(get, first, high_pc, floor)
            if lui is None:
                continue
            high_pc, high_word = lui
        if high_word >> 26 != OP_LUI or high_word >> 21 & 31:
            continue
        scale_pc, scale_word = scale
        if scale_word >> 26 != 0 or scale_word & 0x3F != SLL_FN or scale_word >> 6 & 31 != 2 or scale_word >> 21 & 31:
            continue
        table = ((high_word & 0xFFFF) << 16) + constant + offset
        index_register = scale_word >> 16 & 31
        break
    if table is None:
        return None
    guard = None
    scan = add_pc - 4
    while scan >= floor and add_pc - scan <= WINDOW * 4:
        word = get(scan)
        if word >> 26 == OP_SLTIU and word >> 21 & 31 == index_register:
            guard = (scan, word)
            break
        scan -= 4
    if guard is None:
        return None
    guard_pc, guard_word = guard
    if guard_pc >= scale_pc or high_pc <= guard_pc:
        return None
    flag = guard_word >> 16 & 31
    if any(_destination(get(p)) == -1 or (get(p) >> 26 == 0 and get(p) & 63 in (8, 9, 12, 13))
           for p in range(guard_pc + 4, site, 4)):
        return None
    if not flag or not index_register or flag == index_register:
        return None
    if any(_destination(get(p)) in (index_register, -1) for p in range(guard_pc + 4, scale_pc, 4)):
        return None
    # Supported profile: zero means out of range, and BEQ must bypass the JR
    # and its delay word. BNE needs a different path proof and is refused.
    branches = [p for p in range(guard_pc + 4, site, 4) if get(p) >> 26 in (OP_BEQ, OP_BNE)]
    branched = len(branches) == 1 and any(get(p) >> 26 == OP_BEQ and
                   p < scale_pc and
                   set((get(p) >> 21 & 31, get(p) >> 16 & 31)) == {flag, 0} and
                   not any(_destination(get(q)) in (flag, -1) for q in range(guard_pc + 4, p, 4)) and
                   p + 4 + 4 * _signed(get(p) & 0xFFFF) > site + 4
                   for p in branches)
    count = guard_word & 0xFFFF
    if not branched or not 1 <= count <= MAX_CASES:
        return None
    return {'site': site, 'table': table & 0xFFFFFFFF, 'count': count, 'index_register': index_register,
            'guard_site': guard_pc}


def table_targets(read_word, table: int, count: int) -> list[int]:
    return [read_word(table + 4 * i) for i in range(count)]


def read_table(data: bytes, table: int, count: int) -> list[int]:
    """Read one bounded table from a unique allocated, file-backed data section."""
    if table % 4 or not 1 <= count <= MAX_CASES:
        raise Invalid('unaligned table or unsupported case count')
    size = 4 * count
    sections = [s for s in parse_elf(data)['sections']
                if s['type'] == 1 and s['flags'] & 2 and not s['flags'] & 4
                and s['address'] <= table and table + size <= s['address'] + s['size']]
    if len(sections) != 1:
        raise Invalid('table must fit one unique allocated PROGBITS data section')
    section = sections[0]
    offset = section['offset'] + table - section['address']
    return list(struct.unpack_from(f'<{count}I', data, offset))
