#!/usr/bin/env python3
"""Reconcile all scoped incoming references and expand bounded alias searches."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf
from misc3d_loader_recipe import conditional_aliases
from misc3d_loader_recipe import constructor_aliases, ui_aliases

RELATED_INCOMING = conditional_aliases.RELATED_INCOMING

GP = 0x295d70
DOMAINS = ((0x12c218, 0x12c220), (0x1d1408, 0x1d143c),
           (0x1d1440, 0x1d157c), (0x1d1580, 0x1d15b4),
           (0x1d15b8, 0x1d15cc), (0x1d15d0, 0x1d1628), (0x1d1628, 0x1d17a8),
           (0x1d17a8, 0x1d183c), (0x1d1840, 0x1d1880),
           (0x1d1880, 0x1d18c0), (0x1d18c0, 0x1d1900),
           (0x290ac4, 0x290ad8))
MEMORY_WIDTHS = {32: 1, 33: 2, 35: 4, 36: 1, 37: 2, 39: 4,
                 40: 1, 41: 2, 43: 4, 49: 4, 55: 8, 57: 4, 63: 8,
                 30: 16, 31: 16}


def scoped(address: int) -> bool:
    return any(start <= address < end for start, end in DOMAINS)


def transfer(site: int, word: int) -> tuple[int, str] | None:
    """Decode direct R5900 jumps and ordinary, likely and coprocessor branches."""
    op, rs, rt = word >> 26, (word >> 21) & 31, (word >> 16) & 31
    if op in (2, 3):
        return (((site + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2),
                'UNCONDITIONAL_CALL' if op == 3 else 'UNCONDITIONAL_JUMP')
    displacement = (word & 0xffff) - (0x10000 if word & 0x8000 else 0)
    if op in (4, 5, 6, 7, 20, 21, 22, 23) or (op == 1 and rt in (0, 1, 2, 3, 16, 17, 18, 19)) \
            or (op in (16, 17, 18) and rs == 8 and rt <= 3):
        kind = 'CONDITIONAL_CALL' if op == 1 and rt >= 16 else 'CONDITIONAL_JUMP'
        if op == 4 and rs == rt:
            kind = 'UNCONDITIONAL_JUMP'
        return ((site + 4 + displacement * 4) & 0xffffffff, kind)
    return None



def observe(data: bytes, isolated: dict | None) -> dict:
    """A scoped reference pass never stands for computed or dynamic alias closure."""
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('misc3d alias observation requires the unchanged recorded executable')
    missing = []
    if isolated is None:
        missing.append('required isolated incoming-reference evidence is absent')
    elif isolated.get('executable_sha256') != EE_CORPUS_SHA256 \
            or isolated.get('language') != 'r5900:LE:32:default':
        raise Invalid('misc3d isolated incoming identity differs')
    sections = [s for s in parse_elf(data)['sections'] if s['type'] != 8 and s['flags'] & 2]
    direct, related_direct, literals, gp_sums, gp_addresses, materializations, memory = [], [], [], [], [], [], []
    file_bytes, executable_words = 0, 0
    for section in sections:
        payload = data[section['offset']:section['offset'] + section['size']]
        if len(payload) != section['size']:
            raise Invalid('allocated alias-search storage is truncated')
        file_bytes += len(payload)
        # Include unaligned pointers and interior targets, rather than entries only.
        for offset in range(len(payload) - 3):
            value = struct.unpack_from('<I', payload, offset)[0]
            if scoped(value):
                site = section['address'] + offset
                literals.append({'site': f'{site:08x}', 'to': f'{value:08x}',
                                 'aligned': site % 4 == 0,
                                 'word_sha256': sha256(payload[offset:offset + 4])})
        if not section['flags'] & 4:
            continue
        # Conservative straight-line constant observations, cut at transfers and
        # calls. This does not claim a CFG fixed point or interprocedural analysis.
        registers: dict[int, int] = {0: 0, 28: GP}
        reset_after_delay = False
        for offset in range(0, len(payload) - 3, 4):
            site = section['address'] + offset
            raw = payload[offset:offset + 4]
            word = struct.unpack('<I', raw)[0]
            op, rs, rt, rd = word >> 26, (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
            displacement = (word & 0xffff) - (0x10000 if word & 0x8000 else 0)
            executable_words += 1
            branch = transfer(site, word)
            if branch is not None and scoped(branch[0]):
                direct.append({'site': f'{site:08x}', 'to': f'{branch[0]:08x}',
                               'type': branch[1], 'word_sha256': sha256(raw)})
            if branch is not None and f'{branch[0]:08x}' in RELATED_INCOMING:
                related_direct.append((f'{site:08x}', f'{branch[0]:08x}', branch[1]))
            if op in MEMORY_WIDTHS and rs in registers:
                address = (registers[rs] + displacement) & 0xffffffff
                if address < 0x290ad8 and address + MEMORY_WIDTHS[op] > 0x290ac4:
                    memory.append({'site': f'{site:08x}', 'address': f'{address:08x}',
                                   'base_register': rs, 'width': MEMORY_WIDTHS[op],
                                   'opcode': op, 'word_sha256': sha256(raw)})
            if op == 0 and word & 63 in (32, 33, 44, 45) and (rs == 28 or rt == 28) \
                    and rd != 0:
                other = rt if rs == 28 else rs
                row = {'site': f'{site:08x}', 'destination_register': rd,
                       'index_register': other, 'word_sha256': sha256(raw)}
                if other in registers:
                    row['local_index_value'] = registers[other]
                consumer_raw = payload[offset + 4:offset + 8]
                if len(consumer_raw) != 4:
                    missing.append(f'GP sum lacks a complete immediate consumer at {site:08x}')
                else:
                    consumer_word = struct.unpack('<I', consumer_raw)[0]
                    consumer_op, consumer_base = consumer_word >> 26, (consumer_word >> 21) & 31
                    if consumer_op not in MEMORY_WIDTHS or consumer_base != rd:
                        missing.append(f'GP sum requires a nonlocal consumer disposition at {site:08x}')
                    else:
                        delta = (consumer_word & 0xffff) - (0x10000 if consumer_word & 0x8000 else 0)
                        width = MEMORY_WIDTHS[consumer_op]
                        conditions = []
                        for cell in range(0x290ac4, 0x290ad8, 4):
                            starts = [address for address in range(cell - width + 1, cell + 4)
                                      if address % width == 0]
                            conditions.append({'cell': f'{cell:08x}',
                                               'index_register_low_word': [(address - GP - delta) & 0xffffffff
                                                                          for address in starts]})
                        row['consumer'] = {'site': f'{site + 4:08x}', 'opcode': consumer_op,
                                           'width': width, 'displacement': delta,
                                           'word_sha256': sha256(consumer_raw),
                                           'effective_low_word': f'(0x00295d70 + index + ({delta})) mod 2^32',
                                           'naturally_aligned_overlap_conditions': conditions}
                        row['disposition'] = 'Conditional may-alias under the recorded index equation; numeric input bounds and execution are not asserted.'
                gp_sums.append(row)
            destination, value = None, None
            if op == 15 and rs == 0:
                destination, value = rt, (word & 0xffff) << 16
            elif op in (8, 9, 24, 25) and rs in registers:
                destination, value = rt, (registers[rs] + displacement) & 0xffffffff
                if rs == 28:
                    gp_addresses.append({'site': f'{site:08x}', 'address': f'{value:08x}',
                                         'word_sha256': sha256(raw)})
            elif op == 13 and rs in registers:
                destination, value = rt, registers[rs] | (word & 0xffff)
            elif op == 0:
                destination = rd
                function = word & 63
                if function in (32, 33, 44, 45) and rs in registers and rt in registers:
                    value = (registers[rs] + registers[rt]) & 0xffffffff
                elif function in (36, 37) and rs in registers and rt in registers:
                    value = (registers[rs] & registers[rt]) if function == 36 else (registers[rs] | registers[rt])
                elif function == 0 and rs == 0 and rt in registers:
                    value = (registers[rt] << ((word >> 6) & 31)) & 0xffffffff
            elif op in (8, 9, 10, 11, 12, 13, 14, 24, 25, 26, 27,
                        32, 33, 34, 35, 36, 37, 38, 39, 48, 52, 55):
                destination = rt
            else:
                # Unsupported raw operations are barriers, not preserved facts.
                registers = {0: 0, 28: GP}
            if destination not in (None, 0, 28):
                registers.pop(destination, None)
                if value is not None:
                    registers[destination] = value
                    if scoped(value):
                        materializations.append({'site': f'{site:08x}', 'address': f'{value:08x}',
                                                 'register': destination, 'word_sha256': sha256(raw)})
            if reset_after_delay:
                registers = {0: 0, 28: GP}
                reset_after_delay = False
            if branch is not None or op == 0 and word & 63 in (8, 9):
                reset_after_delay = True
    if isolated is not None:
        domains = isolated.get('domains', [])
        expected = [(f'{start:08x}', f'{end:08x}') for start, end in DOMAINS]
        if [(row.get('start'), row.get('end_exclusive')) for row in domains] != expected:
            raise Invalid('isolated incoming-reference domain differs from the fixed byte ranges')
        saved = [ref for row in domains for ref in row.get('incoming', [])]
        direct_kinds = ('UNCONDITIONAL_CALL', 'CONDITIONAL_CALL', 'UNCONDITIONAL_JUMP', 'CONDITIONAL_JUMP')
        observed = sorted((r['site'], r['to'], r['type']) for r in direct)
        raw_by_site = {r['site']: r for r in direct}
        retained = sorted((r['from'], r['to'],
                           'UNCONDITIONAL_JUMP' if r['type'] == 'UNCONDITIONAL_CALL'
                           and raw_by_site.get(r['from'], {}).get('type') == 'UNCONDITIONAL_JUMP'
                           else r['type']) for r in saved if r['type'] in direct_kinds)
        if observed != retained:
            raise Invalid('saved all-byte incoming transfers differ from the raw direct domain')
        for ref in saved:
            if ref['type'] not in direct_kinds:
                missing.append('non-direct saved reference requires disposition: ' + str(ref))
        related = isolated.get('related_entry_incoming')
        if related is None:
            missing.append('required related callback incoming domain is absent')
        else:
            actual = {row['entry']: sorted((r['from'], r['type']) for r in row['incoming']) for row in related}
            if actual != {entry: sorted(refs) for entry, refs in RELATED_INCOMING.items()}:
                raise Invalid('related callback incoming domain differs from the fixed disposition')
            retained_related = sorted((site, entry, kind) for entry, refs in actual.items()
                                      for site, kind in refs if kind in direct_kinds)
            if retained_related != sorted(related_direct):
                raise Invalid('related saved direct callers differ from the raw incoming domain')
        contexts = isolated.get('gp_sum_saved_context')
        if contexts is None:
            missing.append('required GP sum saved context is absent')
        else:
            if sorted(row['site'] for row in contexts) != sorted(row['site'] for row in gp_sums):
                raise Invalid('isolated GP sum domain differs from the complete raw candidate domain')
            by_site = {row['site']: row for row in contexts}
            for row in gp_sums:
                row['saved_context'] = by_site[row['site']]
                if 'saved_owner' not in by_site[row['site']]:
                    row['disposition'] += ' No saved function owns the site; the equation is conditional on execution of its raw instruction shape.'
    result = {'incoming_domain_status': 'incomplete' if missing else 'pass',
              'searched_allocated_file_bytes': file_bytes, 'searched_executable_words': executable_words,
              'domains': [{'start': f'{start:08x}', 'end_exclusive': f'{end:08x}'} for start, end in DOMAINS],
              'direct_transfers': direct, 'all_byte_pointer_literals': literals,
              'local_materializations': materializations, 'gp_address_constructor_candidates': gp_addresses,
              'gp_register_sum_candidates': gp_sums, 'locally_resolved_memory_candidates': memory,
              'computed_alias_status': 'conditional_static',
              'new_attributed_match_bytes': 0,
              'search_boundary': 'Every allocated file byte for pointers; aligned executable J/JAL/branch words to every scoped byte; conservative straight-line constant observations.',
              'parent_required_unknown': ['external-script-index-bounds', 'open-world-indirect-and-runtime-addresses'],
              'limits': ['No fixed-point CFG or interprocedural constant/alias closure.',
                         'Raw executable opcode candidates do not establish instruction ownership or reachability.',
                         'Locally unknown GP indexes are candidates, not observed accesses to the misc3d cells.',
                         'No external direct sibling caller does not establish runtime unreachability.']}
    result['conditional_gp_aliases'] = conditional_aliases.conditional_gp_contract(data, sections)
    if result['conditional_gp_aliases']['status'] != 'pass':
        missing.append('required conditional alias/consumer instruction sites are absent')
    result['constructor_ui_aliases'] = ui_aliases.known_ui_table_contract(data, sections)
    if result['constructor_ui_aliases']['status'] != 'pass':
        missing.append('required constructor-derived UI instruction sites are absent')
    try:
        result['constructor_aliases'] = constructor_aliases.observe(
            data, sections, isolated.get('gp_constructor_saved_context') if isolated is not None else None)
    except Incomplete as error:
        missing.append(str(error))
        result['constructor_aliases'] = error.details
    if missing:
        raise Incomplete('; '.join(missing), result)
    result['bounded_static_status'] = 'pass'
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('isolated', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    executable = args.game/'extracted/SLES_517.05'

    def action():
        isolated = json.loads(args.isolated.read_text()) if args.isolated.is_file() else None
        if isolated is not None and isolated.get('executable_sha256') != EE_CORPUS_SHA256:
            raise Invalid('misc3d isolated incoming identity differs')
        if not executable.is_file():
            raise Incomplete('required misc3d alias executable is absent')
        return observe(executable.read_bytes(), isolated)

    return write_result(args.output, 'misc3d-aliases', action,
                        [p for p in (Path(__file__), Path(conditional_aliases.__file__),
                                     Path(constructor_aliases.__file__), Path(ui_aliases.__file__),
                                     executable, args.isolated) if p.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
