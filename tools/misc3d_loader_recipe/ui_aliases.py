"""Fixed arithmetic and caller-predicate evidence for the indexed UI table."""
from __future__ import annotations

import struct

from evidence_common import Invalid, sha256
from misc3d_loader_recipe.constructor_aliases import CELLS

KNOWN_UI_FIELDS = (
    (0x181f4c, (0, 0, 0, 18, 0, 45)),
    (0x181fe0, (9, 18, 17, 1)),
    (0x181ff4, (0, 0, 18, 16, 2, 0)),
    (0x18200c, (9, 28, 1, 44176)),
    (0x182010, (0, 1, 16, 16, 0, 33)),
    (0x182028, (43, 16, 2, 0)),
    (0x18203c, (0, 17, 0, 18, 0, 45)),
    (0x182078, (10, 18, 2, 2)),
    (0x18207c, (21, 2, 0, 65498)),
    (0x182d08, (0, 4, 0, 18, 0, 45)),
    (0x182d10, (0, 0, 18, 20, 2, 0)),
    (0x182d18, (9, 28, 16, 44176)),
    (0x182d1c, (0, 16, 20, 16, 0, 33)),
    (0x182d3c, (35, 16, 4, 0)),
    (0x182bdc, (0, 0, 0, 16, 0, 45)),
    (0x182c34, (35, 18, 2, 24)),
    (0x182c38, (6, 2, 0, 17)),
    (0x182c44, (9, 28, 17, 44176)),
    (0x182c48, (35, 17, 4, 0)),
    (0x182c50, (9, 17, 17, 4)),
    (0x182c6c, (9, 16, 16, 1)),
    (0x182c70, (35, 18, 2, 24)),
    (0x182c74, (0, 16, 2, 2, 0, 42)),
    (0x182c78, (21, 2, 0, 65525)),
    (0x182c7c, (35, 17, 4, 0)),
)


def known_ui_table_contract(data: bytes, sections: list[dict]) -> dict:
    """Bind the actual indexed and walking use paths, including their local predicates."""
    checked, missing = [], []
    for address, expected in KNOWN_UI_FIELDS:
        owners = [section for section in sections if section['type'] != 8 and section['flags'] & 4
                  and section['address'] <= address and address + 4 <= section['address'] + section['size']]
        if not owners:
            missing.append(f'{address:08x}')
            continue
        if len(owners) != 1:
            raise Invalid('GP derived UI instruction storage is ambiguous')
        section = owners[0]
        offset = section['offset'] + address - section['address']
        raw = data[offset:offset + 4]
        if len(raw) != 4:
            raise Invalid('GP derived UI instruction storage is truncated')
        word = struct.unpack('<I', raw)[0]
        fields = (word >> 26, (word >> 21) & 31, (word >> 16) & 31)
        fields += (((word >> 11) & 31, (word >> 6) & 31, word & 63)
                   if word >> 26 == 0 else (word & 0xffff,))
        if fields != expected:
            raise Invalid(f'GP derived UI equation/predicate differs at {address:08x}')
        checked.append({'site': f'{address:08x}', 'word_sha256': sha256(raw)})
    return {'status': 'incomplete' if missing else 'pass', 'missing_sites': missing,
            'checked_sites': checked, 'base': '00290a00', 'pointer_stride': 4,
            'conditional_indexes': [{'cell': f'{cell:08x}', 'index_low_word': (cell - 0x290a00) // 4}
                                    for cell in CELLS],
            'forms': [
                {'constructor': '0018200c', 'sum': '00182010', 'store': '00182028',
                 'index': 'S2 shifted left two at00181ff4',
                 'local_domain': 'S2 starts0 at00181f4c, increments throughS1 at00181fe0/0018203c, loop testsS2<2 at00182078.',
                 'precondition': 'Intervening calls preserve saved S0/S1/S2. The observed loop domain0/1 is disjoint; malformed register/input state is not excluded.'},
                {'constructor': '00182d18', 'sum': '00182d1c', 'first_load': '00182d3c',
                 'index': 'Incoming A0 preserved inS2 and shifted left two intoS4 at00182d08/00182d10.',
                 'precondition': 'Incoming index0/1 is disjoint; unrestricted incoming index49..53 conditionally accesses the five cells.'},
                {'constructor': '00182c44', 'first_load': '00182c48', 'increment': '00182c50',
                 'index': 'Walking pointer, advancing four bytes; contextual count read at00182c70 controls00182c74/00182c78.',
                 'precondition': 'Context count<=2 is disjoint. If the loop is entered and count>=50, its walk can conditionally reach cell290ac4 at index49; later cells require counts51..54. Calls must preserve the saved pointer/counter.'}],
            'claim_limit': 'Observed arithmetic and predicates with explicit input/call-preservation preconditions; no successful execution or universal input bound.'}
