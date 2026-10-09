"""Conservative per-constructor GP address use and escape dispositions."""
from __future__ import annotations

import struct

from evidence_common import Incomplete, Invalid, sha256

GP = 0x295d70
CELLS = tuple(range(0x290ac4, 0x290ad8, 4))
MEMORY_WIDTHS = {26: 8, 27: 8, 30: 16, 31: 16, 32: 1, 33: 2, 34: 4, 35: 4,
                 36: 1, 37: 2, 38: 4, 39: 4, 40: 1, 41: 2, 42: 4, 43: 4,
                 44: 8, 45: 8, 46: 4, 48: 4, 49: 4, 52: 8, 54: 16, 55: 8,
                 56: 4, 57: 4, 60: 8, 62: 16, 63: 8}
STORES = {31, 40, 41, 42, 43, 44, 45, 46, 56, 57, 60, 62, 63}
GPR_STORES = {31, 40, 41, 42, 43, 44, 45, 46, 56, 60, 63}
MERGE_MEMORY = {26, 27, 34, 38, 42, 44, 45, 46}
GPR_LOADS = {26, 27, 30, 32, 33, 34, 35, 36, 37, 38, 39, 48, 52, 55, 56, 60}


def overlap_conditions(base: int, displacement: int, width: int, merge: bool = False) -> list[dict]:
    """Conditions on the additive downstream delta; modular low-word candidates only."""
    rows = []
    for cell in CELLS:
        starts = range(cell - width + 1, cell + 4)
        if merge:
            # The containing aligned word is a conservative footprint for a
            # merge load/store; actual partial-byte effects can be narrower.
            starts = range(cell // width * width, (cell + 3) // width * width + width)
        rows.append({'cell': f'{cell:08x}',
                     'delta_low_word_candidates': sorted({(address - base - displacement) & 0xffffffff for address in starts})})
    return rows


def observe(data: bytes, sections: list[dict], saved_context: dict | None = None) -> dict:
    """Account for every raw constructor; do not turn local tracing into global closure."""
    if saved_context is None:
        raise Incomplete('required GP constructor saved-instruction context is absent')
    context = saved_context
    unowned = set(context.get('unowned_sites', []))
    unlisted = set(context.get('unlisted_sites', []))
    ledger = []
    for section in sections:
        if section['type'] == 8 or not section['flags'] & 4:
            continue
        payload = data[section['offset']:section['offset'] + section['size']]
        if len(payload) != section['size']:
            raise Invalid('GP constructor executable storage is truncated')
        for offset in range(0, len(payload) - 3, 4):
            word = struct.unpack_from('<I', payload, offset)[0]
            op, rs, rt = word >> 26, (word >> 21) & 31, (word >> 16) & 31
            if op not in (8, 9, 24, 25) or rs != 28:
                continue
            site = section['address'] + offset
            displacement = (word & 0xffff) - (0x10000 if word & 0x8000 else 0)
            base = (GP + displacement) & 0xffffffff
            saved_owned = bool(saved_context) and f'{site:08x}' not in unowned | unlisted
            row = {'site': f'{site:08x}', 'destination_register': rt, 'initial_address': f'{base:08x}',
                   'word_sha256': sha256(payload[offset:offset + 4]),
                   'saved_instruction': saved_owned,
                   'instruction_status': 'saved instruction per isolated context' if saved_owned else 'raw candidate, conditional if executed',
                   'initial_address_is_scoped': 0x290ac4 <= base < 0x290ad8,
                   'uses': [], 'escapes': [], 'trace_sites': []}
            # Track possible provenance, not one promised value: a derived value
            # is initial_address + delta. Delta starts at zero, additions and
            # copies preserve it; unknown arithmetic makes delta unconstrained.
            tracked = {rt: {'constant': base, 'delta': '0'}} if rt else {}
            pending_stop = None
            stop = 'end of executable section'
            for cursor in range(offset + 4, len(payload) - 3, 4):
                at = section['address'] + cursor
                raw = payload[cursor:cursor + 4]
                instruction = struct.unpack_from('<I', raw)[0]
                operation, left, right, dest = instruction >> 26, (instruction >> 21) & 31, (instruction >> 16) & 31, (instruction >> 11) & 31
                function = instruction & 63
                immediate = (instruction & 0xffff) - (0x10000 if instruction & 0x8000 else 0)
                fact = {'site': f'{at:08x}', 'word_sha256': sha256(raw)}
                row['trace_sites'].append(fact)
                if operation in MEMORY_WIDTHS:
                    if left in tracked:
                        expression = tracked[left]
                        width = MEMORY_WIDTHS[operation]
                        use = {**fact, 'kind': 'memory-address', 'opcode': operation, 'base_register': left,
                               'width': width, 'displacement': immediate,
                               'base_constant': f"{expression['constant']:08x}", 'delta': expression['delta'],
                               'conditions': overlap_conditions(expression['constant'], immediate, width, operation in MERGE_MEMORY),
                               'effect': 'store' if operation in STORES else 'load',
                               'footprint': 'containing aligned word, conservative merge footprint' if operation in MERGE_MEMORY else 'contiguous byte overlap'}
                        row['uses'].append(use)
                    if operation in GPR_STORES and right in tracked:
                        row['escapes'].append({**fact, 'kind': 'stored-derived-value', 'register': right,
                                               'disposition': 'May alias through a later use of the stored value; no interprocedural or memory fixed point claimed.'})
                    if operation in GPR_LOADS:
                        tracked.pop(right, None)
                elif operation in (8, 9, 24, 25):
                    previous = tracked.get(left)
                    tracked.pop(right, None)
                    if previous and right:
                        tracked[right] = {'constant': (previous['constant'] + immediate) & 0xffffffff,
                                          'delta': previous['delta']}
                        row['uses'].append({**fact, 'kind': 'constant-offset-propagation', 'destination_register': right,
                                            'displacement': immediate, 'address_constant': f"{tracked[right]['constant']:08x}"})
                elif operation == 0 and function in (32, 33, 44, 45):
                    a, b = tracked.get(left), tracked.get(right)
                    tracked.pop(dest, None)
                    if dest and (a or b):
                        prior = a or b
                        assert prior is not None
                        other = right if a else left
                        delta = prior['delta'] if other == 0 else f"({prior['delta']} + register_{other}_low_word_at_{at:08x}) mod 2^32"
                        if a and b:
                            delta = 'unconstrained downstream arithmetic delta'
                        tracked[dest] = {'constant': prior['constant'], 'delta': delta}
                        row['uses'].append({**fact, 'kind': 'register-add-propagation', 'destination_register': dest,
                                            'other_register': other, 'address_constant': f"{prior['constant']:08x}", 'delta': delta})
                elif operation in (2, 3) or operation == 0 and function in (8, 9) or operation in (1, 4, 5, 6, 7, 20, 21, 22, 23) or operation in (16, 17, 18) and left == 8:
                    # The branch/call delay slot remains part of this prefix.
                    pending_stop = 'control transfer after its delay slot'
                    row['escapes'].append({**fact, 'kind': 'control-or-call-boundary', 'registers': sorted(tracked),
                                           'disposition': 'Live derived values may flow to a callee or another block. Their downstream effective-address delta is unconstrained here.'})
                    continue
                elif operation == 0 and function in (16, 17, 18, 19, 24, 25, 26, 27):
                    stop = 'unresolved HI/LO register effects'
                    row['escapes'].append({**fact, 'kind': 'unsupported-register-effects', 'registers': sorted(tracked),
                                           'disposition': 'May alias through unresolved HI/LO propagation.'})
                    break
                elif operation == 0 and function in (10, 11):
                    if dest and any(register in tracked for register in (left, right, dest)):
                        tracked[dest] = {'constant': 0, 'delta': f'unconstrained conditional move at {at:08x}'}
                        row['uses'].append({**fact, 'kind': 'conditional-derived-value', 'destination_register': dest,
                                            'disposition': 'Either prior destination or moved source can survive the unresolved predicate.'})
                elif operation == 0 and function in (0, 2, 3, 4, 6, 7, 20, 22, 36, 37, 38, 39, 42, 43, 56, 58, 59, 60, 62, 63):
                    source = tracked.get(left) or tracked.get(right)
                    tracked.pop(dest, None)
                    if source and dest:
                        tracked[dest] = {'constant': 0, 'delta': f'unconstrained transformed address at {at:08x}'}
                        row['uses'].append({**fact, 'kind': 'transformed-derived-value', 'destination_register': dest,
                                            'disposition': 'Conservative may-alias; arithmetic transformation requires an additional input predicate.'})
                elif operation in (10, 11, 12, 13, 14, 15):
                    source = tracked.get(left)
                    tracked.pop(right, None)
                    if source and right:
                        tracked[right] = {'constant': 0, 'delta': f'unconstrained transformed address at {at:08x}'}
                        row['uses'].append({**fact, 'kind': 'transformed-derived-value', 'destination_register': right,
                                            'disposition': 'Conservative may-alias after non-additive immediate arithmetic.'})
                elif operation in (16, 17, 18, 28):
                    stop = 'unsupported coprocessor/MMI register effects'
                    row['escapes'].append({**fact, 'kind': 'unsupported-register-effects', 'registers': sorted(tracked),
                                           'disposition': 'May alias after unresolved register/representation propagation.'})
                    break
                else:
                    stop = 'unsupported register effects'
                    row['escapes'].append({**fact, 'kind': 'unsupported-register-effects', 'registers': sorted(tracked),
                                           'disposition': 'May alias after unresolved downstream propagation.'})
                    break
                if pending_stop:
                    stop = pending_stop
                    break
                if not tracked:
                    stop = 'all local derived registers overwritten'
                    break
            row['prefix_stop'] = stop
            row['downstream_conditions'] = overlap_conditions(base, 0, 16)
            row['disposition'] = 'Conservative conditional may-alias through recorded derived uses or downstream delta; a non-scoped initial address is not an absence proof.'
            row['condition_limit'] = 'Downstream delta denotes the entire subsequent address change, including index, displacement or memory/call propagation. Low-word equality is necessary; executed instruction, path predicate, alignment and valid virtual address remain required.'
            ledger.append(row)
    if saved_context and context.get('candidate_count') != len(ledger):
        raise Invalid('saved GP constructor candidate denominator differs')
    observed_sites = {row['site'] for row in ledger}
    if not unowned | unlisted <= observed_sites:
        raise Invalid('saved GP constructor sites are outside raw candidate domain')
    return {'status': 'pass', 'raw_constructor_count': len(ledger), 'constructors': ledger,
            'saved_owned_count': sum(row['saved_instruction'] for row in ledger),
            'raw_unowned_count': sum(not row['saved_instruction'] for row in ledger),
            'meaning_of_pass': 'Every scanned raw GP immediate-address constructor has an explicit conservative use/escape disposition; no universal computed-alias closure or runtime exclusion is claimed.',
            'parent_required_unknown': ['interprocedural-memory-and-CFG-address-fixed-point', 'external-script-index-bounds', 'open-world-indirect-and-runtime-addresses'],
            'boundary': 'Aligned executable GP immediate-add constructors, actual straight-line def/use prefixes including delay slots. Isolated saved-instruction membership, when supplied, does not grant authorship. GP equals the recorded00295d70; unsupported and interprocedural continuations remain explicit conditional may-alias.'}
