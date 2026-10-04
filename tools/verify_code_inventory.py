#!/usr/bin/env python3
"""Check saved R5900 instruction bytes and expose executable inventory gaps.

This checks the inventory against the ELF, independently of decompiler success.
An exact byte match does not establish correct instruction semantics or recovered
source. Verified zero-filled synthetic DVP overlays are reported separately from
physical executable code, whose bytes are stored at the overlay table's LMAs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from evidence_common import Incomplete, Invalid, write_result
from ps2_executables import parse_elf
from ps2_vu import parse_overlays


def _address(value, label: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{8}', value):
        raise Invalid(f'{label} must be an eight-digit default-space address')
    return int(value, 16)


def inspect(data: bytes, static: dict) -> dict:
    elf = parse_elf(data)
    if static.get('schema_version') != 1 or static.get('language') != 'r5900:LE:32:default':
        raise Incomplete('only the current R5900 static-export schema/profile is supported')
    if static.get('executable_sha256') != hashlib.sha256(data).hexdigest():
        raise Invalid('static export and executable SHA-256 differ')
    functions = static.get('functions')
    if not isinstance(functions, list) or type(static.get('inventory_count')) is not int or static['inventory_count'] != len(functions):
        raise Invalid('static function count does not match rows')
    synthetic = []
    if any(section['type'] == 0x7FFFF421 for section in elf['sections']):
        overlay_inventory = parse_overlays(data)
        for overlay in overlay_inventory['overlays']:
            if overlay['placeholder_nonzero_bytes']:
                raise Incomplete('DVP overlay metadata contains nonzero placeholder bytes; physical-code classification is unresolved')
            synthetic.append({'name': overlay['name'], 'offset': overlay['placeholder_offset'],
                              'bytes': overlay['bytes'], 'sha256': overlay['placeholder_sha256'],
                              'source_offset': overlay['source_offset'], 'source_sha256': overlay['sha256'],
                              'classification': 'verified_zero_filled_DVP_placeholder'})
    synthetic_offsets = {row['offset'] for row in synthetic}
    if any(section['type'] == 0x7FFFF421 and section['offset'] not in synthetic_offsets
           for section in elf['sections']):
        raise Incomplete('DVP overlay section is absent from the bounded load-address mapping')
    regions = []
    for index, section in enumerate(elf['sections']):
        if section['flags'] & 4 and section['type'] not in (0, 8) and section['size']:
            if section['type'] == 0x7FFFF421 and section['offset'] in synthetic_offsets:
                continue
            name = section.get('name', f'section_{index}')
            regions.append({'name': name, 'address': section['address'], 'offset': section['offset'],
                            'bytes': section['size'], 'separate_overlay': name.startswith('.DVP.overlay.')})
    if not regions:
        for index, program in enumerate(elf['programs']):
            if program['type'] == 1 and program['flags'] & 1 and program['file_size']:
                regions.append({'name': f'LOAD_{index}', 'address': program['virtual_address'],
                                'offset': program['offset'], 'bytes': program['file_size'], 'separate_overlay': False})
    if not regions:
        raise Incomplete('no file-backed executable region exists in ELF metadata')
    coverage = [bytearray(region['bytes']) for region in regions]
    entries, instructions, owners = set(), {}, {}
    for function in functions:
        if not isinstance(function, dict):
            raise Invalid('static function row must be an object')
        entry = _address(function.get('entry'), 'function entry')
        if entry in entries:
            raise Invalid('duplicate static function entry')
        entries.add(entry)
        rows = function.get('instructions')
        if not isinstance(rows, list):
            raise Invalid('static function instructions must be an array')
        entry_found = False
        for row in rows:
            if not isinstance(row, dict):
                raise Invalid('static instruction row must be an object')
            address = _address(row.get('address'), 'instruction address')
            entry_found |= address == entry
            raw = row.get('bytes')
            if not isinstance(raw, str) or not re.fullmatch(r'[0-9a-fA-F]{8}', raw) or address % 4:
                raise Invalid('R5900 instruction must be aligned and contain four bytes')
            payload = bytes.fromhex(raw)
            if address in instructions and instructions[address] != payload:
                raise Invalid('instruction bytes disagree between function rows')
            instructions[address] = payload
            owners.setdefault(address, set()).add(entry)
            matches = [(index, region) for index, region in enumerate(regions)
                       if not region['separate_overlay'] and region['address'] <= address
                       and address + 4 <= region['address'] + region['bytes']]
            if len(matches) != 1:
                raise Invalid(f'instruction {address:#x} is outside or ambiguously inside file-backed executable regions')
            index, region = matches[0]
            at = region['offset'] + address - region['address']
            loads = [program for program in elf['programs'] if program['type'] == 1
                     and program['virtual_address'] <= address
                     and address + 4 <= program['virtual_address'] + program['file_size']
                     and at == program['offset'] + address - program['virtual_address']]
            if len(loads) != 1:
                raise Invalid('instruction section mapping disagrees with ELF LOAD file mapping')
            if data[at:at + 4] != payload:
                raise Invalid(f'instruction {address:#x} bytes differ from executable')
            delta = address - region['address']
            coverage[index][delta:delta + 4] = b'\1' * 4
        if not entry_found:
            raise Invalid('function entry is absent from its instruction rows')
    sections = []
    for region, covered in zip(regions, coverage):
        missing = []
        start = None
        for index, flag in enumerate(covered):
            if not flag and start is None:
                start = index
            if flag and start is not None:
                missing.append({'offset': start, 'bytes': index - start})
                start = None
        if start is not None:
            missing.append({'offset': start, 'bytes': len(covered) - start})
        count = sum(covered)
        sections.append({**region, 'listed_instruction_bytes': count,
                         'unlisted_bytes': region['bytes'] - count, 'unlisted_spans': missing})
    total = sum(region['bytes'] for region in regions)
    listed = sum(sum(row) for row in coverage)
    details = {'executable_sha256': elf['sha256'], 'inventory_count': len(functions),
               'unique_instruction_count': len(instructions),
               'shared_instruction_count': sum(len(value) > 1 for value in owners.values()),
               'mapped_executable_bytes': total, 'listed_instruction_bytes': listed,
               'unlisted_executable_bytes': total - listed, 'regions': sections,
               'excluded_synthetic_bytes': sum(row['bytes'] for row in synthetic),
               'synthetic_regions': synthetic,
               'whole_game_decompiled': False,
               'claim_limits': ['Listed instruction bytes match the executable; semantics are unverified.',
                                'Unlisted bytes may be code, tables, padding, or VU programs; classification remains open.',
                                'Verified zero-filled DVP overlay placeholders are excluded; actual code at the LMAs remains counted.',
                                'Function discovery, original source, types, rebuilds, and behavior remain unproven.']}
    if total != listed:
        raise Incomplete('executable file regions contain bytes outside the saved function instruction inventory', details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-export', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/code-inventory'))
    args = parser.parse_args()
    return write_result(args.output, 'code-inventory',
                        lambda: inspect(args.executable.read_bytes(), json.loads(args.static_export.read_text())),
                        [args.static_export, args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
