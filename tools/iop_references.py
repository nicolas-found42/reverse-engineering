#!/usr/bin/env python3
"""Exact code and data reference sites of an IOP IRX, read from its relocation tables.

An IRX is linked at address zero and relocated by the loader. Each REL entry marks a word that holds an
address: a plain pointer (R_MIPS_32), a jump target (R_MIPS_26), or the high half of a `lui` and low half
of an `addiu`/`lw`/`sw` pair (R_MIPS_HI16 followed by R_MIPS_LO16). The module-relative target is therefore
given by the instruction words themselves, with no data-flow guess. The file must first pass the measured
load profile of `ps2_irx_relocations`. No module code is run.
"""
import struct

import ps2_irx
import ps2_irx_relocations as profile

KINDS = {profile.R_MIPS_32: 'word', profile.R_MIPS_26: 'jump', profile.R_MIPS_HI16: 'hi_lo'}


def _original(data: bytes, load_offset: int, file_size: int, site: int) -> int:
    return struct.unpack_from('<I', data, load_offset + site)[0] if site < file_size else 0


def _signed16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def reference_sites(data: bytes) -> list[dict]:
    profile.load_iop_irx(data, load_base=0)
    elf = ps2_irx.parse_elf(data)['elf']
    load = elf['programs'][1]
    sections = elf['sections']
    found = []
    for section in sections:
        if section['type'] != profile.SHT_REL or not section['size']:
            continue
        entries = [struct.unpack_from('<II', data, section['offset'] + at) for at in range(0, section['size'], 8)]
        for index, (site, info) in enumerate(entries):
            kind = KINDS.get(info & 0xFF)
            if kind is None:
                continue
            word = _original(data, load['offset'], load['file_size'], site)
            if kind == 'word':
                found.append({'site': site, 'kind': kind, 'target': word})
            elif kind == 'jump':
                found.append({'site': site, 'kind': kind, 'target': 4 * (word & 0x03FFFFFF)})
            else:
                lo_site = entries[index + 1][0]
                low = _original(data, load['offset'], load['file_size'], lo_site)
                target = ((word & 0xFFFF) << 16) + _signed16(low & 0xFFFF)
                found.append({'site': site, 'kind': kind, 'lo_site': lo_site, 'target': target & 0xFFFFFFFF})
    return sorted(found, key=lambda s: s['site'])
