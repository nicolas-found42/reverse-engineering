#!/usr/bin/env python3
"""Bounds-checked reader for the ECOFF symbolic header (`.mdebug`) of a little-endian MIPS ELF.

The section holds files, procedure descriptors, local and external symbols with their string tables. This reads only
those records: procedure names, addresses, sizes, frame sizes and saved-register masks, file names and external symbols.
Offsets in the header are file offsets, so `file_base` is the file offset of the section data passed in. Sizes were
checked against the real section: the regions tile it exactly. No code is run.
"""
import struct

from evidence_common import Invalid

MAGIC = 0x7009
HEADER = struct.Struct('<HH23I')
SYMR = struct.Struct('<IIi')
PDR = struct.Struct('<IIIIIIIIiHHIII')
FDR = struct.Struct('<IIIIIIIIIIHHIIIIIII')
EXTR = 16
ST_PROC, ST_BLOCK, ST_END, ST_STATIC_PROC, ST_FILE = 6, 7, 8, 14, 11
HEADER_FIELDS = ('magic', 'vstamp', 'ilineMax', 'cbLine', 'cbLineOffset', 'idnMax', 'cbDnOffset', 'ipdMax', 'cbPdOffset',
                 'isymMax', 'cbSymOffset', 'ioptMax', 'cbOptOffset', 'iauxMax', 'cbAuxOffset', 'issMax', 'cbSsOffset',
                 'issExtMax', 'cbSsExtOffset', 'ifdMax', 'cbFdOffset', 'crfd', 'cbRfdOffset', 'iextMax', 'cbExtOffset')


def _region(data: bytes, base: int, offset: int, size: int, label: str) -> memoryview:
    start = offset - base
    if size and (start < 0 or start + size > len(data)):
        raise Invalid(f'{label} region lies outside the section')
    return memoryview(data)[start:start + size]


def _string(table: memoryview, offset: int, label: str) -> str:
    if not 0 <= offset < len(table):
        raise Invalid(f'{label} string offset is outside its table')
    raw = bytes(table[offset:])
    end = raw.find(b'\0')
    if end < 0:
        raise Invalid(f'{label} string is not terminated')
    return raw[:end].decode('latin-1')


def _symbols(block: memoryview, count: int) -> list[dict]:
    out = []
    for at in range(count):
        iss, value, bits = SYMR.unpack_from(block, at * SYMR.size)
        out.append({'iss': iss, 'value': value, 'symbol_type': bits & 0x3F, 'storage_class': (bits >> 6) & 0x1F,
                    'index': (bits >> 12) & 0xFFFFF})
    return out


def _size_of(symbols: list[dict], start: int) -> int | None:
    depth = 0
    for at in range(start, len(symbols)):
        kind = symbols[at]['symbol_type']
        if kind in (ST_PROC, ST_STATIC_PROC, ST_BLOCK):
            depth += 1
        elif kind == ST_END:
            depth -= 1
            if depth == 0:
                return symbols[at]['value']
    return None


def parse_mdebug(data: bytes, file_base: int = 0) -> dict:
    if len(data) < HEADER.size:
        raise Invalid('section is shorter than the symbolic header')
    header = dict(zip(HEADER_FIELDS, HEADER.unpack_from(data)))
    if header['magic'] != MAGIC:
        raise Invalid('symbolic header magic is not 0x7009')
    pdrs = _region(data, file_base, header['cbPdOffset'], header['ipdMax'] * PDR.size, 'procedure')
    syms = _region(data, file_base, header['cbSymOffset'], header['isymMax'] * SYMR.size, 'local symbol')
    local_ss = _region(data, file_base, header['cbSsOffset'], header['issMax'], 'local string')
    ext_ss = _region(data, file_base, header['cbSsExtOffset'], header['issExtMax'], 'external string')
    fds = _region(data, file_base, header['cbFdOffset'], header['ifdMax'] * FDR.size, 'file descriptor')
    exts = _region(data, file_base, header['cbExtOffset'], header['iextMax'] * EXTR, 'external symbol')
    all_symbols = _symbols(syms, header['isymMax'])
    files, procedures = [], []
    for index in range(header['ifdMax']):
        (adr, rss, iss_base, cb_ss, isym_base, csym, _il, _cl, _io, _co, ipd_first, cpd, *_rest) = FDR.unpack_from(fds, index * FDR.size)
        if isym_base + csym > len(all_symbols):
            raise Invalid('file symbols run past the local symbol table')
        if ipd_first + cpd > header['ipdMax']:
            raise Invalid('file procedures run past the procedure table')
        strings = local_ss[iss_base:iss_base + cb_ss]
        name = _string(strings, rss, 'file name')
        symbols = all_symbols[isym_base:isym_base + csym]
        files.append({'name': name, 'address': adr, 'symbols': csym, 'procedures': cpd})
        for number in range(ipd_first, ipd_first + cpd):
            (p_adr, p_isym, _line, regmask, regoffset, _opt, fregmask, fregoffset, frameoffset, framereg, pcreg,
             *_tail) = PDR.unpack_from(pdrs, number * PDR.size)
            if not 0 <= p_isym < len(symbols):
                raise Invalid('procedure symbol index is outside its file')
            symbol = symbols[p_isym]
            procedures.append({'name': _string(strings, symbol['iss'], 'procedure name'), 'address': p_adr, 'file': name,
                               'static': symbol['symbol_type'] == ST_STATIC_PROC, 'size': _size_of(symbols, p_isym),
                               'frame_bytes': frameoffset, 'saved_register_mask': regmask, 'register_offset': regoffset,
                               'float_register_mask': fregmask, 'float_register_offset': fregoffset,
                               'frame_register': framereg, 'return_register': pcreg})
    externals = []
    for at in range(header['iextMax']):
        (flags,) = struct.unpack_from('<I', exts, at * EXTR)
        iss, value, bits = SYMR.unpack_from(exts, at * EXTR + 4)
        externals.append({'name': _string(ext_ss, iss, 'external name'), 'value': value, 'symbol_type': bits & 0x3F,
                          'storage_class': (bits >> 6) & 0x1F, 'file_index': flags >> 16})
    counts = {'procedures': header['ipdMax'], 'files': header['ifdMax'], 'local_symbols': header['isymMax'],
              'externals': header['iextMax'], 'line_bytes': header['cbLine']}
    return {'header': counts, 'files': files, 'procedures': procedures, 'externals': externals}
