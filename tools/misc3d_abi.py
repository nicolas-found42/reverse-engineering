#!/usr/bin/env python3
"""Validate bounded misc3d dependency argument, packed-id and pointer-use paths."""
from __future__ import annotations

import argparse
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from ps2_executables import parse_elf


def check(data: bytes) -> dict:
    """Decode the required raw sites; missing sites cannot hide contradictions."""
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('misc3d ABI requires the unchanged recorded executable')
    sections = [s for s in parse_elf(data)['sections']
                if s['type'] != 8 and s['flags'] & 6 == 6]
    missing, sites = [], []

    def require(site, meaning, predicate):
        owners = [s for s in sections if s['address'] <= site
                  and site + 4 <= s['address'] + s['size']]
        if not owners:
            missing.append(f'required ABI instruction absent: {site:08x}')
            return
        if len(owners) != 1:
            raise Invalid(f'ABI instruction has ambiguous storage: {site:08x}')
        offset = owners[0]['offset'] + site - owners[0]['address']
        raw = data[offset:offset + 4]
        if len(raw) != 4:
            raise Invalid(f'ABI instruction storage is truncated: {site:08x}')
        word = struct.unpack('<I', raw)[0]
        if not predicate(word):
            raise Invalid(f'misc3d ABI contradiction at {site:08x}: {meaning}')
        sites.append({'site': f'{site:08x}', 'meaning': meaning, 'word_sha256': sha256(raw)})

    def immediate(site, op, base, register, value, meaning):
        require(site, meaning, lambda w: (w >> 26, (w >> 21) & 31,
                                         (w >> 16) & 31, w & 0xffff)
                == (op, base, register, value & 0xffff))

    def registers(site, left, right, destination, function, meaning):
        require(site, meaning, lambda w: (w >> 26, (w >> 21) & 31,
                                         (w >> 16) & 31, (w >> 11) & 31,
                                         (w >> 6) & 31, w & 63)
                == (0, left, right, destination, 0, function))

    def call(site, target, meaning):
        require(site, meaning, lambda w: w >> 26 == 3 and
                (((site + 4) & 0xf0000000) | ((w & 0x3ffffff) << 2)) == target)

    # Name pointer into the database dependency and V0 into the lookup + cell.
    immediate(0x1d1440, 15, 0, 4, 0x28, 'database name upper address')
    call(0x1d1448, 0x11ed90, 'database dependency call')
    immediate(0x1d144c, 9, 4, 4, 0x3208, 'database name argument in call delay slot')
    registers(0x11ed98, 4, 0, 16, 45, 'dependency preserves A0 in S0')
    registers(0x1d1454, 2, 0, 4, 45, 'dependency V0 becomes resource lookup A0')
    call(0x1d145c, 0x124f58, 'resource lookup consumes database result')
    immediate(0x1d1460, 43, 28, 2, -0x52ac, 'dependency V0 stored to misc3d database cell')

    # The dependency tags the database id, discards the resource index and
    # returns the same low word that it writes into its own id cell.
    immediate(0x120588, 35, 28, 2, -0x6c4c, 'load dependency id cell')
    immediate(0x12058c, 15, 0, 3, 0xfff0, 'database mask upper half')
    immediate(0x120590, 13, 3, 3, 0xffff, 'database mask lower half')
    immediate(0x120594, 15, 0, 5, 1, 'database tag upper half')
    registers(0x120598, 2, 3, 2, 36, 'clear database kind bits')
    immediate(0x12059c, 15, 0, 4, 0xffff, 'resource-index discard mask')
    registers(0x1205a0, 2, 5, 2, 37, 'set database kind tag')
    registers(0x1205ac, 2, 4, 2, 36, 'discard resource index')
    for site, register, offset in ((0x1205a4, 16, 0x240), (0x1205a8, 17, 0x248),
                                   (0x1205b0, 18, 0x250), (0x1205b4, 19, 0x258),
                                   (0x1205b8, 20, 0x260), (0x1205bc, 21, 0x268),
                                   (0x1205c0, 22, 0x270), (0x1205c4, 23, 0x278),
                                   (0x1205c8, 30, 0x280), (0x1205cc, 31, 0x288)):
        immediate(site, 55, 29, register, offset, 'frame restore preserves the returned V0')
    immediate(0x1205d0, 43, 28, 2, -0x6c4c, 'write returned id to dependency cell')
    registers(0x1205d4, 31, 0, 0, 8, 'normal dependency return')
    immediate(0x1205d8, 9, 29, 29, 0x290, 'return delay slot restores frame without changing V0')

    # The shared object helper treats -1 as null. For a non-sentinel resource,
    # the low 16 bits index a four-byte pointer table at context offset 236.
    immediate(0x12506c, 9, 0, 2, -1, 'resource sentinel')
    registers(0x125074, 4, 0, 16, 45, 'preserve resource argument')
    require(0x125078, 'sentinel branch to null return', lambda w:
            (w >> 26, (w >> 21) & 31, (w >> 16) & 31, w & 0xffff) == (4, 16, 2, 9))
    call(0x125080, 0x21b6e0, 'get shared resource context')
    immediate(0x125088, 12, 16, 3, 0xffff, 'resource low-word index')
    immediate(0x12508c, 35, 2, 4, 236, 'load object pointer table from context')
    require(0x125090, 'scale resource index by four', lambda w:
            (w >> 26, (w >> 21) & 31, (w >> 16) & 31,
             (w >> 11) & 31, (w >> 6) & 31, w & 63) == (0, 0, 3, 3, 2, 0))
    registers(0x125094, 3, 4, 3, 33, 'compute indexed pointer slot')
    immediate(0x125098, 4, 0, 0, 2, 'loaded path skips null result')
    immediate(0x12509c, 35, 3, 2, 0, 'load object pointer in branch delay slot')
    registers(0x1250a0, 0, 0, 2, 45, 'null result for sentinel')
    registers(0x1250ac, 31, 0, 0, 8, 'object helper returns V0')
    immediate(0x1250b0, 9, 29, 29, 16, 'object helper return delay slot')
    immediate(0x12507c, 63, 29, 31, 8, 'sentinel branch delay slot preserves resource and result')
    require(0x125084, 'context-call delay slot preserves resource', lambda w: w == 0)
    immediate(0x1250a4, 55, 29, 16, 0, 'object return restores S0 without changing V0')
    immediate(0x1250a8, 55, 29, 31, 8, 'object return restores RA without changing V0')

    result = {'scope': 'Required raw argument/return and indexed-pointer sites only; static observation.',
              'sites': sites, 'database_name_address': '00283208',
              'database_return_low_word': '(old_id & 0xfff00000) | 0x00010000',
              'dependency_id_cell': '0028f124', 'loader_id_cell': '00290ac4',
              'resource_object': {'sentinel': -1, 'sentinel_result': 'null',
                                  'context_table_offset': 236, 'index_mask': 65535,
                                  'pointer_stride': 4},
              'required_unknown': ['object-table-allocation-and-bounds', 'pointer-lifetime',
                                   'computed-alias-closure', 'original-declarations-and-ownership'],
              'new_attributed_match_bytes': 0}
    if missing:
        raise Incomplete('; '.join(missing), result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    executable = args.game/'extracted/SLES_517.05'

    def action():
        if not executable.is_file():
            raise Incomplete('required misc3d ABI executable is absent')
        return check(executable.read_bytes())

    return write_result(args.output, 'misc3d-abi', action,
                        [p for p in (Path(__file__), executable) if p.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
