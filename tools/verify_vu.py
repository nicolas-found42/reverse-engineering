#!/usr/bin/env python3
"""Offline DVP overlay recovery and mnemonic round-trip verification.

Private code/assembly artifacts are written only to a fresh work directory.
Success establishes byte-preserving assembly, not VU program meaning, scheduling,
VU0/VU1 ownership, geometry semantics, or whole-game behavioral equivalence.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import uuid

from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from ps2_executables import parse_elf
from ps2_vu import parse_overlays, canonical_source
from matching_diff import compare_unit

ENTRY_MAP = Path(__file__).resolve().parents[1] / 'notes/evidence/fr2-geometry-vu-entry-map.json'


def validate_entry_map(entry_map: dict, overlays: list[dict], evidence: dict[str, dict]) -> dict:
    """Validate documented MSCAL entries against overlay extents and evidence refs."""
    rows = entry_map.get('overlays')
    if not isinstance(rows, list) or len(rows) != 8 or [row.get('index') for row in rows] != list(range(8)):
        raise Invalid('entry map must describe all eight overlays in index order')
    by_index = {row['index']: row for row in overlays}
    incomplete = []
    documented = 0
    for row in rows:
        index = row['index']
        if row.get('interface') != 'unresolved':
            raise Invalid('interface claims require a separately evidence-backed contract')
        if index not in by_index:
            raise Invalid('entry map overlay identity is absent from the executable')
        overlay = by_index[index]
        status, entries = row.get('status'), row.get('entries')
        if status == 'incomplete':
            if not row.get('incomplete_reasons'):
                raise Invalid('incomplete overlay must state why its map remains incomplete')
            incomplete.append(index)
        elif status != 'documented':
            raise Invalid('overlay entry disposition is invalid')
        if not isinstance(entries, list):
            raise Invalid('overlay entries must be a list, including when no caller is known')
        for entry in entries:
            required = ('msc_address', 'vu_byte_address', 'caller', 'evidence')
            if any(key not in entry for key in required):
                raise Invalid('documented entry lacks caller or MSCAL evidence fields')
            source = evidence.get(entry['evidence'])
            if source is None:
                raise Incomplete('documented VU entry references unavailable evidence')
            recorded = source.get('entry_mapping', {})
            if not recorded:
                recorded = next((candidate for candidate in source.get('derivations', [])
                                 if candidate.get('vu_byte_address') == hex(entry['vu_byte_address']) and
                                 candidate.get('caller') == entry['caller']), {})
                recorded = {**recorded, 'overlay_index': recorded.get('overlay_index'),
                            'vu_byte_address': recorded.get('vu_byte_address'),
                            'global_value': recorded.get('msc_immediate'),
                            'ee_builder': recorded.get('caller'),
                            'channel': recorded.get('channel')}
            if (recorded.get('overlay_index') != index or
                    recorded.get('vu_byte_address') != hex(entry['vu_byte_address']) or
                    recorded.get('global_value') != hex(entry['msc_address']) or
                    recorded.get('ee_builder') != entry['caller'] or
                    (entry.get('channel') and recorded.get('channel') != entry['channel'])):
                raise Invalid('documented VU entry contradicts its pinned EE caller evidence')
            byte_address = entry['vu_byte_address']
            if (byte_address != entry['msc_address'] * 8 or
                    not overlay['vu_byte_address'] <= byte_address < overlay['vu_byte_address'] + overlay['bytes']):
                raise Invalid('MSCAL entry does not resolve within its named overlay')
            if not isinstance(entry['caller'], str) or not entry['caller'].startswith('FUN_'):
                raise Invalid('MSCAL entry has no EE caller reference')
        documented += len(entries)
    return {'documented_entry_count': documented, 'incomplete_overlay_indices': incomplete,
            'interfaces': [{'overlay_index': row['index'], 'status': row['interface']}
                           for row in rows]}


def load_entry_map(path: Path = ENTRY_MAP) -> tuple[dict, dict[str, dict]]:
    if not path.is_file():
        raise Incomplete(f'required VU entry map is missing: {path}')
    value = json.loads(path.read_text())
    evidence = {}
    root = Path(__file__).resolve().parents[1]
    for name, pin in value.get('evidence', {}).items():
        referenced = root / pin['path']
        if not referenced.is_file():
            raise Incomplete(f'entry map evidence is unavailable: {pin["path"]}')
        if identity(referenced)['sha256'] != pin.get('sha256'):
            raise Invalid(f'entry map evidence identity changed: {pin["path"]}')
        evidence[name] = json.loads(referenced.read_text())
    return value, evidence


def _tool(explicit: Path | None, default: str) -> Path:
    path = explicit or (Path(found) if (found := shutil.which(default)) else None)
    if path is None or not path.is_file():
        raise Incomplete(f'required native tool is missing: {default}')
    return path.resolve()


def _run(command: list[str], stem: Path) -> dict:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Incomplete(f'native tool did not finish: {type(exc).__name__}') from exc
    stdout, stderr = stem.with_suffix('.stdout'), stem.with_suffix('.stderr')
    stdout.write_text(result.stdout); stderr.write_text(result.stderr)
    return {'command': command, 'exit_code': result.returncode,
            'stdout': {'path': str(stdout), **identity(stdout)},
            'stderr': {'path': str(stderr), **identity(stderr)}}


def verify(executable: Path, objdump: Path | None, assembler: Path | None, work: Path,
           entry_map_path: Path = ENTRY_MAP) -> dict:
    dump, assemble = _tool(objdump, 'dvp-objdump'), _tool(assembler, 'dvp-as')
    data = executable.read_bytes()
    inventory = parse_overlays(data)
    entry_map, evidence = load_entry_map(entry_map_path)
    entry_map_result = validate_entry_map(entry_map, inventory['overlays'], evidence)
    work.mkdir(parents=True, exist_ok=False)
    tools = {'objdump': {'path': str(dump), **identity(dump)},
             'assembler': {'path': str(assemble), **identity(assemble)}}
    rows = []
    for overlay in inventory['overlays']:
        index = overlay['index']
        code = data[overlay['source_offset']:overlay['source_offset'] + overlay['bytes']]
        raw, source, obj = [work / f'overlay-{index}.{suffix}' for suffix in ('bin', 's', 'o')]
        raw.write_bytes(code)
        command = [str(dump), '-D', '-z', '-b', 'binary', '-m', 'dvp:vu',
                   '--adjust-vma=' + str(overlay['vu_byte_address']), str(raw)]
        disassembly = _run(command, work / f'overlay-{index}-disassemble')
        if disassembly['exit_code']:
            raise Invalid('native VU disassembly failed', {'tools': tools, 'completed': rows, 'failed_command': disassembly})
        text = Path(disassembly['stdout']['path']).read_text()
        canonical, transforms = canonical_source(text, code, overlay['vu_byte_address'])
        source.write_text(canonical)
        assembly = _run([str(assemble), '-o', str(obj), str(source)], work / f'overlay-{index}-assemble')
        if assembly['exit_code']:
            raise Invalid('native VU assembly failed', {'tools': tools, 'completed': rows, 'failed_command': assembly})
        if not obj.is_file():
            raise Invalid('assembler reported success without writing its object', {'tools': tools, 'completed': rows, 'failed_command': assembly})
        object_data = obj.read_bytes()
        object_elf = parse_elf(object_data)
        relocations = [section for section in object_elf['sections'] if section['type'] in (4, 9) and section['size']]
        if relocations:
            raise Incomplete('assembled VU object contains unresolved relocations', {'completed': rows})
        sections = [section for section in object_elf['sections'] if section.get('name') == '.vutext']
        if len(sections) != 1 or sections[0]['type'] != 1:
            raise Invalid('assembler object has no unique file-backed .vutext')
        section = sections[0]
        recovered = object_data[section['offset']:section['offset'] + section['size']]
        row = {**overlay, 'exact_match': recovered == code,
               'assembled_bytes': len(recovered), 'assembled_sha256': sha256(recovered),
               'transformations': transforms, 'disassembly': disassembly, 'assembly': assembly,
               'artifacts': {str(path): identity(path) for path in (raw, source, obj)}}
        row['byte_gate'] = compare_unit(overlay['name'], overlay['vu_byte_address'],
                                        overlay['source_offset'], code, recovered).as_dict()
        rows.append(row)
        if recovered != code:
            raise Invalid('VU mnemonic round trip differs from executable code bytes', {'tools': tools, 'overlays': rows})
    details = {**inventory, 'tools': tools, 'overlays': rows, 'exact_roundtrip_overlays': len(rows),
            'entry_map': entry_map_result,
            'interface_status': 'incomplete' if any(item['interface'] != 'documented'
                                                      for item in entry_map['overlays']) else 'documented',
            'entry_map_disposition': 'incomplete' if entry_map_result['incomplete_overlay_indices'] else 'documented',
            'work_directory': str(work), 'whole_game_decompiled': False,
            'claim_limits': inventory['claim_limits'] + [
                'Mnemonic source, signed branch displacement conversion, and nine-digit binary32 literals reproduce these chunks byte for byte.',
                'No raw-opcode fallback is used. This is reconstruction/encoding validation, not a behavioral or scheduling oracle.']}
    if entry_map_result['incomplete_overlay_indices'] or details['interface_status'] == 'incomplete':
        raise Incomplete('VU byte reassembly passed; required entry or interface maps remain incomplete', details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    parser.add_argument('--objdump', type=Path)
    parser.add_argument('--assembler', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/vu'))
    args = parser.parse_args()
    work = args.output / ('private-work-' + uuid.uuid4().hex)
    return write_result(args.output, 'vu-roundtrip',
                        lambda: verify(args.executable, args.objdump, args.assembler, work),
                        [args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
