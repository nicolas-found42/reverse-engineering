"""Fixed conditional GP alias, caller and sibling-value contracts."""
from __future__ import annotations

import struct

from evidence_common import Invalid, sha256


RELATED_INCOMING = {
    '00108bf0': [('0010b3d4', 'UNCONDITIONAL_CALL'), ('0010c738', 'UNCONDITIONAL_CALL'),
                 ('0010cf38', 'UNCONDITIONAL_CALL'), ('00167270', 'UNCONDITIONAL_CALL'),
                 ('00167288', 'UNCONDITIONAL_CALL'), ('001763cc', 'UNCONDITIONAL_CALL'),
                 ('001763f8', 'UNCONDITIONAL_CALL'), ('001cc04c', 'UNCONDITIONAL_CALL')],
    '00108d5c': [], '00108de4': [], '00108efc': [],
    '0010cdc8': [('001081b8', 'UNCONDITIONAL_CALL'), ('001081e0', 'UNCONDITIONAL_CALL'),
                 ('0010c380', 'UNCONDITIONAL_CALL')],
    '00175788': [('00175594', 'PARAM')], '00176300': [('001755b8', 'PARAM')],
    '001763a0': [('0017584c', 'PARAM')], '00178650': [('001782d4', 'DATA')],
    '0017f700': [('0017f598', 'PARAM')],
    '001cc018': [('001cb598', 'PARAM'), ('001cb5cc', 'PARAM')],
}

def conditional_gp_contract(data: bytes, sections: list[dict]) -> dict:
    """Retain real conditional aliases, separating raw equations from input bounds."""
    missing, sites = [], []

    def require(site: int, fields: tuple[int, ...], register_form: bool) -> None:
        owners = [s for s in sections if s['flags'] & 4 and s['address'] <= site
                  and site + 4 <= s['address'] + s['size']]
        if not owners:
            missing.append(f'{site:08x}')
            return
        if len(owners) != 1:
            raise Invalid('conditional GP instruction has ambiguous storage')
        offset = owners[0]['offset'] + site - owners[0]['address']
        raw = data[offset:offset + 4]
        word = struct.unpack('<I', raw)[0]
        decoded = (word >> 26, (word >> 21) & 31, (word >> 16) & 31)
        decoded += (((word >> 11) & 31, (word >> 6) & 31, word & 63)
                    if register_form else (word & 0xffff,))
        if decoded != fields:
            raise Invalid(f'conditional GP alias equation differs at {site:08x}')
        sites.append({'site': f'{site:08x}', 'word_sha256': sha256(raw)})

    require(0x108bf0, (0, 0, 4, 4, 2, 0), True)
    forms = ((0x108bf0, 0x108bf4, 0x108bf8, 2, 4),
             (0x108d5c, 0x108d60, 0x108d64, 7, 1),
             (0x108de4, 0x108de8, 0x108dec, 3, 1),
             (0x108efc, 0x108f00, 0x108f04, 3, 1))
    aliases = []
    for entry, addition, load, register, stride in forms:
        require(addition, (0, 4, 28, register, 0, 33), True)
        require(load, (35, register, register, 0xa8c0), False)
        conditions = [{'cell': f'{cell:08x}', 'ordinary_nonnegative_input': (cell - 0x290630) // stride}
                      for cell in range(0x290ac4, 0x290ad8, 4)]
        aliases.append({'entry': f'{entry:08x}', 'input_register': 'A0', 'input_stride': stride,
                        'effective_low_word': f'(0x00290630 + {stride} * input) mod 2^32',
                        'conditions': conditions,
                        'disposition': 'Conditional out-of-bounds alias of a different GP table; no observed misc3d address escape or executed alias.',
                        'valid_index_domain': 'Input index 0/1 (or byte offset 0/4 for unscaled forms) is disjoint from all five cells.',
                        'limit': 'Conditions list ordinary nonnegative inputs; the low-word equation also describes arithmetic wrap, without asserting a valid virtual address.'})
    # Actual mapping initialization and swap: the first two slots contain 0/1.
    for site, fields in (
            (0x1083a4, (9, 28, 5, 0xa8c0)), (0x1083a8, (9, 0, 4, 1)),
            (0x1083ac, (9, 5, 2, 4)), (0x1083b8, (43, 5, 0, 0)),
            (0x1083bc, (43, 6, 4, 0)), (0x108478, (9, 28, 3, 0xa8c0)),
            (0x10847c, (9, 0, 2, 1)), (0x108480, (43, 3, 2, 0)),
            (0x108488, (43, 3, 0, 4))):
        require(site, fields, False)
    require(0x1083b4, (0, 2, 0, 6, 0, 45), True)
    # Bind actual callback address constructions, argument transfers and local
    # loop predicates. Dynamic callback/config values remain explicit below.
    for site, fields in (
            (0x175594, (9, 5, 5, 0x5788)), (0x1755b8, (9, 5, 5, 0x6300)),
            (0x17584c, (9, 4, 4, 0x63a0)), (0x178268, (15, 0, 12, 0x18)),
            (0x178274, (9, 12, 12, 0x8650)), (0x1782d4, (43, 29, 12, 0x28)),
            (0x17f598, (9, 5, 5, 0xf700)), (0x1cb598, (9, 22, 6, 0xc018)),
            (0x1cb5cc, (9, 22, 6, 0xc018)), (0x10cdc4, (43, 28, 4, 0x8fd0)),
            (0x10cdc8, (35, 28, 2, 0x8fd0)), (0x1081e4, (9, 0, 5, 1)),
            (0x10b8ac, (9, 18, 18, 1)), (0x10b8b4, (10, 18, 2, 2)),
            (0x10c744, (9, 17, 17, 1)), (0x10c74c, (10, 17, 2, 2)),
            (0x1d1794, (35, 28, 4, 0xad5c)), (0x1d1798, (35, 28, 5, 0xad60))):
        require(site, fields, False)
    for site, fields in (
            (0x1763a8, (0, 5, 0, 16, 0, 45)), (0x10cdd8, (0, 2, 0, 31, 0, 9)),
            (0x1081bc, (0, 0, 0, 5, 0, 45)), (0x10c384, (0, 17, 0, 5, 0, 45)),
            (0x10c06c, (0, 4, 0, 17, 0, 45)), (0x10b094, (0, 0, 0, 18, 0, 45)),
            (0x10b098, (0, 18, 0, 4, 0, 45)), (0x10b3d8, (0, 18, 0, 4, 0, 45)),
            (0x10c6a8, (0, 0, 0, 17, 0, 45)), (0x10c73c, (0, 17, 0, 4, 0, 45))):
        require(site, fields, True)
    for site, opcode, target in ((0x1d3d64, 3, 0x1d1628), (0x1d17a0, 2, 0x1318a0),
                                 (0x10b09c, 3, 0x10c060), (0x175854, 3, 0x10cdc0)):
        encoded_target = target >> 2
        require(site, (opcode, (encoded_target >> 21) & 31,
                       (encoded_target >> 16) & 31, encoded_target & 0xffff), False)
    return {'status': 'incomplete' if missing else 'pass', 'checked_sites': sites,
            'missing_sites': missing, 'forms': aliases,
            'two_slot_mapping': {'base': '00290630', 'slot_bytes': 4, 'slots': 2,
                                 'observed_initial_values': [0, 1], 'observed_swap_values': [1, 0]},
            'caller_dispositions': [
                {'sites': ['0010b3d4', '0010c738'], 'input': 'Local loop index 0/1.',
                 'precondition': 'Intervening calls preserve the observed saved index register.',
                 'disposition': 'Disjoint under the recorded local control-flow and register-preservation contract.'},
                {'sites': ['001763cc', '001763f8'],
                 'input': 'Callback A1, preserved in S0; registered at0017584c via0010cdc0.',
                 'incoming': '0010cdc8 forwards A1; its callers001081b8/001081e0 supply0/1, while0010c380 forwards the0/1 loop input from0010b09c.',
                 'disposition': 'Recorded callback invocation paths use the two-slot input domain.'},
                {'sites': ['0010cf38', '00167270', '00167288', '001cc04c'],
                 'input': 'Incoming selector, selected-context/script value, or registered object record field.',
                 'disposition': 'Conditional may-alias for malformed/unbounded input; do not assert numeric bounds or runtime impossibility.'}],
            'sibling_consumer': {'entry': '001d1628', 'caller_site': '001d3d64',
                                 'reads': [{'site': '001d1794', 'cell': '00290acc', 'argument': 'A0'},
                                           {'site': '001d1798', 'cell': '00290ad0', 'argument': 'A1'}],
                                 'tail_target': '001318a0',
                                 'disposition': 'Direct cell-value consumer; neither instruction passes a cell address.'},
            'remaining_input_domain': 'Externally supplied/script-derived indexes need their own input precondition or bounds disposition; valid two-slot paths do not alias misc3d.'}
