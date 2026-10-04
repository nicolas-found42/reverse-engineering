"""Bounded ELF32/MIPS metadata and RESET-at-zero PS2 ROMDIR inspection.

ROMDIR layout basis: ps2homebrew/ps2img at
017018224a8a77a79bf57f387bbcea3f4505c8f0, common.h and ximg.c:165-172.
This reader describes file boundaries; it does not discover raw/packed code,
apply relocations, recover functions, or prove executable coverage.
"""
from __future__ import annotations

import hashlib
import re
import struct

from evidence_common import Incomplete, Invalid


def _span(data: bytes, offset: int, size: int, label: str) -> bytes:
    if offset < 0 or size < 0 or offset > len(data) or size > len(data) - offset:
        raise Invalid(f'{label} span {offset:#x}+{size:#x} exceeds {len(data)} bytes')
    return data[offset:offset + size]


def parse_elf(data: bytes) -> dict:
    if _span(data, 0, 16, 'ELF identity')[:4] != b'\x7fELF':
        raise Invalid('ELF magic is absent')
    if data[4:7] != b'\x01\x01\x01':
        raise Incomplete('only ELF32 little-endian version 1 is supported')
    _span(data, 0, 52, 'ELF header')
    values = struct.unpack_from('<HHIIIIIHHHHHH', data, 16)
    names = ('type', 'machine', 'version', 'entry', 'program_offset',
             'section_offset', 'flags', 'header_size', 'program_stride',
             'program_count', 'section_stride', 'section_count', 'strings_section')
    result: dict = dict(zip(names, values))
    if result['machine'] != 8 or result['version'] != 1 or result['header_size'] != 52:
        raise Invalid('ELF header is not the supported 52-byte MIPS version-1 header')
    if result['program_count'] == 0xFFFF or result['strings_section'] == 0xFFFF or (
        result['section_count'] == 0 and result['section_offset'] != 0
    ):
        raise Incomplete('ELF extended section/program numbering is unsupported')
    programs = []
    if result['program_count']:
        if result['program_stride'] != 32:
            raise Invalid('ELF32 program headers must have 32-byte stride')
        _span(data, result['program_offset'], result['program_count'] * 32, 'program table')
    for i in range(result['program_count']):
        row = dict(zip(('type', 'offset', 'virtual_address', 'physical_address',
                        'file_size', 'memory_size', 'flags', 'alignment'),
                       struct.unpack_from('<8I', data, result['program_offset'] + i * 32)))
        _span(data, row['offset'], row['file_size'], f'program {i} payload')
        if row['type'] == 1 and row['memory_size'] < row['file_size']:
            raise Invalid(f'LOAD program {i} file bytes exceed memory size')
        if row['virtual_address'] + row['memory_size'] > 0x1_0000_0000:
            raise Invalid(f'program {i} virtual extent exceeds 32-bit address space')
        programs.append(row)
    sections = []
    if result['section_count']:
        if result['section_stride'] != 40:
            raise Invalid('ELF32 section headers must have 40-byte stride')
        _span(data, result['section_offset'], result['section_count'] * 40, 'section table')
    for i in range(result['section_count']):
        row = dict(zip(('name_offset', 'type', 'flags', 'address', 'offset', 'size',
                        'link', 'info', 'alignment', 'entry_size'),
                       struct.unpack_from('<10I', data, result['section_offset'] + i * 40)))
        if row['type'] not in (0, 8) and row['size']:
            _span(data, row['offset'], row['size'], f'section {i} payload')
        if row['address'] + row['size'] > 0x1_0000_0000:
            raise Invalid(f'section {i} extent exceeds 32-bit address space')
        sections.append(row)
    if result['strings_section']:
        if result['strings_section'] >= len(sections):
            raise Invalid('section-name string table index is out of range')
        table = sections[result['strings_section']]
        if table['type'] != 3:
            raise Invalid('section-name table is not STRTAB')
        strings = _span(data, table['offset'], table['size'], 'section names')
        for row in sections:
            at = row['name_offset']
            end = strings.find(b'\0', at)
            if at >= len(strings) or end < 0:
                raise Invalid('section name exceeds string table')
            row['name'] = strings[at:end].decode('ascii', errors='backslashreplace')
    result.update(programs=programs, sections=sections,
                  bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return result


def parse_romdir(data: bytes) -> dict:
    """Inspect measured RESET-size-zero profile; do not guess generic BIOS starts."""
    _span(data, 0, 48, 'ROMDIR prefix')
    prefix = [struct.unpack_from('<10sHI', data, at) for at in (0, 16, 32)]
    if [row[0].split(b'\0', 1)[0] for row in prefix] != [b'RESET', b'ROMDIR', b'EXTINFO']:
        raise Incomplete('only RESET/ROMDIR/EXTINFO-at-zero profile is supported')
    if prefix[0][2] != 0:
        raise Incomplete('nonempty RESET bootstrap is outside the supported profile')
    directory_size = prefix[1][2]
    if directory_size < 64 or directory_size % 16:
        raise Invalid('ROMDIR size must include entries and a 16-byte terminator')
    directory = _span(data, 0, directory_size, 'ROMDIR table')
    entries = []
    for at in range(0, directory_size - 16, 16):
        raw_name, extended_size, size = struct.unpack_from('<10sHI', directory, at)
        if b'\0' not in raw_name:
            raise Invalid('ROMDIR name is not terminated within ten bytes')
        name = raw_name.split(b'\0', 1)[0]
        if not re.fullmatch(rb'[A-Z0-9_]{1,9}', name):
            raise Invalid('ROMDIR name is empty or outside the safe measured character set')
        if any(raw_name[len(name) + 1:]):
            raise Invalid('ROMDIR name has nonzero trailing bytes')
        entries.append({'name': name.decode('ascii'), 'extended_info_bytes': extended_size,
                        'bytes': size, 'directory_offset': at})
    if any(directory[-16:]):
        raise Invalid('ROMDIR terminator is not sixteen zero bytes')
    if len({row['name'] for row in entries}) != len(entries):
        raise Invalid('ROMDIR contains duplicate names')
    if sum(row['extended_info_bytes'] for row in entries) != prefix[2][2]:
        raise Invalid('ROMDIR extended-info lengths do not match EXTINFO size')
    _span(data, directory_size, prefix[2][2], 'EXTINFO payload')
    cursor = (directory_size + prefix[2][2] + 15) & ~15
    _span(data, directory_size + prefix[2][2], cursor - directory_size - prefix[2][2], 'EXTINFO padding')
    modules = []
    logical_end = cursor
    for row in entries[3:]:
        payload = _span(data, cursor, row['bytes'], row['name'] + ' module')
        modules.append({**row, 'offset': cursor, 'sha256': hashlib.sha256(payload).hexdigest(),
                        'elf': parse_elf(payload)})
        logical_end = cursor + row['bytes']
        cursor = (logical_end + 15) & ~15
    if len(data) < logical_end or len(data) > cursor:
        raise Invalid('ROMDIR payload end differs from file end or final alignment')
    return {'entries': entries, 'modules': modules, 'logical_end': logical_end,
            'padding_bytes': len(data) - logical_end,
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
