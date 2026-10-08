#!/usr/bin/env python3
"""Prove bounded GNU placement, relocation and zero-fill contracts without byte credit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import subprocess

from evidence_common import Incomplete, Invalid, identity, write_result
from misc3d_contract import check as build_misc3d, verify_cell_object
from linker_layout_recipe.packages import bind as bind_gnu_packages
from linker_layout_recipe.fixture import build as build_gnu_fixture
from ps2_executables import parse_elf

ROOT = Path(__file__).resolve().parent.parent
DECISION = ROOT / 'notes/evidence/fr2-linker-layout-continuation/decision.json'
TEXT = '.text.fr2_misc3d_get_database_id'
CELL = '.sbss.fr2_misc3d_db_id'
SECTION_CONTRACT = {
    TEXT: (0x1d1800, 60, 1, 6, 8),
    '.fr2_file': (0x2831a8, 29, 1, 2, 8),
    '.fr2_message': (0x283320, 55, 1, 2, 8),
    CELL: (0x290ac4, 4, 8, 3, 4),
}
SYMBOLS = {'misc3d_db_id': 0x290ac4, 'report_error': 0x105888}
GP = 0x295d70


def verify_outputs(data: bytes) -> dict:
    """Check the fixed accessor/data/cell layout and its actual loader mapping."""
    elf = parse_elf(data)
    if elf['type'] != 2 or elf['flags'] != 0x20924001:
        raise Invalid('linked ELF requires ET_EXEC, EM_MIPS and e_flags 0x20924001')
    if elf['entry'] != 0x1d1800:
        raise Invalid(f"entry {elf['entry']:#010x} differs from accessor entry 0x001d1800")
    loads = [p for p in elf['programs'] if p['type'] == 1]
    if not loads:
        raise Incomplete('linked output has no PT_LOAD coverage')
    for index, load in enumerate(loads):
        alignment = load['alignment']
        if (alignment < 4 or alignment & (alignment - 1)
                or load['virtual_address'] % alignment != load['offset'] % alignment
                or load['physical_address'] != load['virtual_address']):
            raise Invalid(f'PT_LOAD[{index}] alignment/address congruence differs')
    verified = []
    missing = []
    for name, (address, size, kind, flags, alignment) in SECTION_CONTRACT.items():
        rows = [s for s in elf['sections'] if s.get('name') == name]
        if len(rows) > 1:
            raise Invalid(f'required section duplicated: {name}')
        if not rows:
            missing.append(name)
            continue
        section = rows[0]
        if (section['address'], section['size'], section['type'], section['flags']) != (address, size, kind, flags):
            raise Invalid(f'{name}@{address:#010x} address/size/storage/flags differ')
        observed_alignment = section['alignment']
        if (observed_alignment < alignment or observed_alignment & (observed_alignment - 1)
                or address % observed_alignment):
            raise Invalid(f'{name}@{address:#010x} alignment differs')
        covering = [p for p in loads if p['virtual_address'] <= address
                    and address + size <= p['virtual_address'] + p['memory_size']]
        if len(covering) != 1:
            raise Invalid(f'{name}@{address:#010x} requires exactly one covering PT_LOAD')
        load = covering[0]
        relative = address - load['virtual_address']
        required_permissions = 4 | (2 if flags & 1 else 0) | (1 if flags & 4 else 0)
        if load['flags'] != required_permissions:
            raise Invalid(f'{name}@{address:#010x} PT_LOAD permissions differ')
        if kind == 8:
            if relative < load['file_size']:
                raise Invalid(f'{name}@{address:#010x} NOBITS overlaps PT_LOAD file bytes')
        elif (relative + size > load['file_size']
              or section['offset'] != load['offset'] + relative):
            raise Invalid(f'{name}@{address:#010x} section file position differs from PT_LOAD')
        verified.append({'section': name, 'address': f'{address:08x}', 'bytes': size,
                         'alignment': observed_alignment, 'storage': 'NOBITS' if kind == 8 else 'PROGBITS',
                         'file_bytes': 0 if kind == 8 else size})
    if missing:
        raise Incomplete('required section missing: ' + ', '.join(missing))
    return {'machine': elf['machine'], 'flags': f"{elf['flags']:08x}", 'entry': f"{elf['entry']:08x}",
            'sections': verified, 'loads': loads, 'matched_bytes': 0,
            'zero_fill': 'ELF PT_LOAD memory tail contract; execution was not observed'}


def _signed16(word: int) -> int:
    value = word & 0xffff
    return value - 0x10000 if value & 0x8000 else value


def verify_relocations(object_data: bytes, linked_data: bytes) -> dict:
    """Replay the fixed unit's MIPS REL records; never mask relocated fields."""
    obj, linked = parse_elf(object_data), parse_elf(linked_data)
    if obj['type'] != 1 or obj['flags'] != 0x20924001:
        raise Invalid('accessor object requires ET_REL and e_flags 0x20924001')
    rows = obj['sections']
    text_rows = [(i, s) for i, s in enumerate(rows) if s.get('name') == TEXT]
    linked_rows = [s for s in linked['sections'] if s.get('name') == TEXT]
    if len(text_rows) != 1 or len(linked_rows) != 1:
        raise Incomplete('relocation replay requires one accessor section in both artifacts')
    index, source = text_rows[0]
    target = linked_rows[0]
    if source['size'] != 60 or target['size'] != 60 or target['address'] != 0x1d1800:
        raise Invalid('relocation replay accessor range differs')
    tables = [s for s in rows if s['info'] == index and s['type'] in (4, 9)]
    if len(tables) != 1:
        raise Incomplete('accessor REL table missing or duplicated')
    rel = tables[0]
    if rel['type'] != 9:
        raise Incomplete('only MIPS REL relocation records are supported')
    if (rel['entry_size'] != 8 or rel['size'] % 8 or not 0 < rel['link'] < len(rows)):
        raise Invalid('accessor REL table stride/symbol link is malformed')
    symbols = rows[rel['link']]
    if (symbols['type'] != 2 or symbols['entry_size'] != 16 or symbols['size'] % 16
            or not 0 < symbols['link'] < len(rows) or rows[symbols['link']]['type'] != 3):
        raise Invalid('accessor relocation symbol table is malformed')
    strings = rows[symbols['link']]
    names = object_data[strings['offset']:strings['offset'] + strings['size']]
    expected = bytearray(object_data[source['offset']:source['offset'] + source['size']])
    records = []
    sites = set()
    pending: dict[int, list[tuple[int, int]]] = {}
    for offset, info in struct.iter_unpack('<II', object_data[rel['offset']:rel['offset'] + rel['size']]):
        kind, symbol_index = info & 255, info >> 8
        if kind not in (4, 5, 6, 7):
            raise Incomplete(f'unsupported relocation kind {kind} at {TEXT}+{offset:#x}')
        if offset % 4 or offset + 4 > source['size'] or offset in sites:
            raise Invalid(f'duplicate/unaligned/outside relocation at {TEXT}+{offset:#x}')
        sites.add(offset)
        if symbol_index >= symbols['size'] // 16:
            raise Invalid(f'relocation symbol index out of bounds at {TEXT}+{offset:#x}')
        name_at, value, _, _, _, section_index = struct.unpack_from('<IIIBBH', object_data,
            symbols['offset'] + symbol_index * 16)
        end = names.find(b'\0', name_at)
        if name_at >= len(names) or end < 0:
            raise Invalid('relocation symbol name exceeds string table')
        name = names[name_at:end].decode('ascii')
        if section_index == 0 and name in SYMBOLS:
            binding = SYMBOLS[name]
        elif 0 < section_index < len(rows):
            section_name = rows[section_index].get('name', '')
            if section_name not in SECTION_CONTRACT:
                raise Incomplete(f'unsupported relocation section symbol {section_name}')
            name = section_name
            binding = SECTION_CONTRACT[section_name][0] + value
        else:
            raise Incomplete(f'unrecorded relocation symbol {name}')
        word = struct.unpack_from('<I', expected, offset)[0]
        if kind == 5:
            pending.setdefault(symbol_index, []).append((offset, word))
            records.append({'offset': offset, 'kind': kind, 'symbol': name, 'binding': f'{binding:08x}'})
            continue
        if kind == 6:
            low = _signed16(word)
            for high_offset, high_word in pending.pop(symbol_index, []):
                full = binding + ((high_word & 0xffff) << 16) + low
                struct.pack_into('<I', expected, high_offset,
                                 (high_word & 0xffff0000) | (((full + 0x8000) >> 16) & 0xffff))
            relocated = (word & 0xffff0000) | ((binding + low) & 0xffff)
        elif kind == 7:
            displacement = binding + _signed16(word) - GP
            if not -0x8000 <= displacement <= 0x7fff:
                raise Invalid(f'GPREL16 displacement overflows at {TEXT}+{offset:#x}')
            relocated = (word & 0xffff0000) | (displacement & 0xffff)
        else:
            destination = binding + ((word & 0x3ffffff) << 2)
            if (not 0 <= destination <= 0xffffffff or destination & 3
                    or (destination ^ (target['address'] + offset + 4)) & 0xf0000000):
                raise Invalid(f'R_MIPS_26 destination not encodable at {TEXT}+{offset:#x}')
            relocated = (word & 0xfc000000) | ((destination >> 2) & 0x3ffffff)
        struct.pack_into('<I', expected, offset, relocated)
        records.append({'offset': offset, 'kind': kind, 'symbol': name, 'binding': f'{binding:08x}'})
    if pending:
        raise Invalid('unpaired R_MIPS_HI16 relocation remains')
    if len(records) != 6 or sorted(r['kind'] for r in records) != [4, 5, 5, 6, 6, 7]:
        raise Incomplete('fixed accessor relocation set differs from six required records')
    actual = linked_data[target['offset']:target['offset'] + target['size']]
    for at in range(0, 60, 4):
        if expected[at:at + 4] != actual[at:at + 4]:
            raise Invalid(f'linked relocation/instruction differs at {TEXT}+{at:#x} (vaddr {target["address"] + at:#010x})',
                          {'offset': at, 'expected_word': f'{struct.unpack_from("<I", expected, at)[0]:08x}',
                           'observed_word': f'{struct.unpack_from("<I", actual, at)[0]:08x}', 'matched_bytes': 0})
    return {'records': records, 'replayed_bytes': 60, 'matched_bytes': 0,
            'claim_limit': 'Fixed accessor REL bindings only; no full-image relocation coverage'}


def check(game: Path, tool_root: Path) -> dict:
    if not DECISION.is_file():
        raise Incomplete('recorded GNU linker decision is missing')
    decision = json.loads(DECISION.read_text())
    tool_root = tool_root.resolve(strict=True)
    missing, changed, observed = [], [], {}
    for name, expected in decision['tool_files'].items():
        path = tool_root / name
        if not path.is_file():
            missing.append(name)
            continue
        observed[name] = identity(path)
        if observed[name] != expected:
            changed.append(name)
    admission = {'tool_identities': observed, 'missing_tools': missing, 'changed_tools': changed}
    if changed:
        raise Invalid('GNU linker tool identity differs: ' + ', '.join(changed), admission)
    if missing:
        raise Incomplete('GNU linker tool missing: ' + ', '.join(missing), admission)
    packages = bind_gnu_packages(tool_root, decision)
    built = build_misc3d(game, tool_root)
    fixture = build_gnu_fixture(tool_root, decision)
    artifacts = built['artifacts']
    original = Path(artifacts['linked_output']['path'])
    linked = original.with_name('linker-entry.elf')
    argv = list(built['build']['candidates'][0]['link_argv'])
    argv[argv.index('-o') + 1] = str(linked)
    argv.extend(['-e', 'fr2_misc3d_get_database_id'])
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Incomplete(f'GNU linker invocation unavailable: {exc}') from exc
    if result.returncode:
        raise Invalid('GNU linker invocation failed', {'argv': argv, 'stderr': result.stderr[-2000:]})
    data = linked.read_bytes()
    output_contract = verify_outputs(data)
    accessor_object = Path(artifacts['accessor_prepared_object']['path']).read_bytes()
    relocations = verify_relocations(accessor_object, data)
    cell = verify_cell_object(Path(artifacts['cell_object']['path']).read_bytes())
    return {'scope': 'recorded misc3d accessor, diagnostic constants and four-byte cell',
            'decision': identity(DECISION), 'gnu_packages': packages,
            'gnu_machine_fixture': fixture,
            'output_contract': output_contract, 'relocations': relocations,
            'cell_object_contract': cell, 'original_entry': f"{parse_elf(original.read_bytes())['entry']:08x}",
            'command': argv, 'runtime_identity': built['runtime_identity'],
            'artifacts': {**artifacts, 'linked_with_entry': {'path': str(linked), **identity(linked)}},
            'build': built, 'matched_bytes': 0, 'ac06_status': 'incomplete', 'issue9_status': 'incomplete',
            'claim_limits': ['GNU binutils 2.40 Debian substitution; no Sony linker recovery.',
                             'Exact EE assembler source/permission remains compiler dependency #8/#21.',
                             'Fixed range contract only; full EE/all IOP placement and relocations are not reconstructed.',
                             'Zero-fill is the ELF load contract, not observed guest initialization.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('tool_root', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/linker-layout'))
    args = parser.parse_args()
    return write_result(args.output, 'gnu-linker-layout', lambda: check(args.game, args.tool_root),
                        [Path(__file__), DECISION, Path(__file__).with_name('misc3d_contract.py'),
                         Path(__file__).with_name('ps2_executables.py'),
                         *(ROOT/'tools/linker_layout_recipe'/name for name in
                           ('packages.py','fixture.py','fixture.s','fixture.ld'))])


if __name__ == '__main__':
    raise SystemExit(main())
