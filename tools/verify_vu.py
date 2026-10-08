#!/usr/bin/env python3
"""Offline DVP overlay recovery and mnemonic round-trip verification.

Private code/assembly artifacts are written only to a fresh work directory.
Success establishes byte-preserving assembly, not VU program meaning, scheduling,
VU0/VU1 ownership, geometry semantics, or whole-game behavioral equivalence.
"""
import argparse
import hashlib
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


def verify_instruction_anchors(source: dict, *, executable_sha256: str, read_address) -> None:
    """Require retained EE instruction bytes to match their pinned executable."""
    identity = source.get('executable')
    anchors = source.get('instruction_anchors')
    if not isinstance(identity, dict) or not isinstance(anchors, list) or not anchors:
        raise Invalid('instruction anchor evidence lacks executable identity or anchor rows')
    if identity.get('sha256') != executable_sha256:
        raise Invalid('instruction anchor executable SHA-256 differs from the verified corpus')
    for anchor in anchors:
        if not isinstance(anchor, dict):
            raise Invalid('instruction anchor row is malformed')
        try:
            address = int(anchor['address'], 16)
            expected = bytes.fromhex(anchor['bytes'])
        except (KeyError, TypeError, ValueError) as exc:
            raise Invalid('instruction anchor address or bytes are malformed') from exc
        if not expected or read_address(address, len(expected)) != expected:
            raise Invalid(f"instruction anchor bytes differ at {anchor.get('address', 'unknown')}")


def validate_entry_map(entry_map: dict, overlays: list[dict], evidence: dict[str, dict],
                       executable: bytes | None = None) -> dict:
    """Validate MSCAL callers and explicitly bounded interface evidence."""
    rows = entry_map.get('overlays')
    if not isinstance(rows, list) or len(rows) != 8 or [row.get('index') for row in rows] != list(range(8)):
        raise Invalid('entry map must describe all eight overlays in index order')
    by_index = {row['index']: row for row in overlays}
    incomplete = []
    documented = 0
    partial_interfaces = []
    complete_interfaces = []
    elf = None
    executable_hash = hashlib.sha256(executable).hexdigest() if executable is not None else None
    verified_ee_evidence = set()

    def verify_ee_evidence(source: dict) -> None:
        nonlocal elf
        if not source.get('instruction_anchors') or not isinstance(source.get('executable'), dict):
            raise Invalid('documented EE caller evidence requires executable identity and instruction anchors')
        if executable is None:
            raise Incomplete('verified executable is required to check EE instruction anchors')
        identity = source.get('executable')
        if not isinstance(identity, dict) or identity.get('sha256') != executable_hash:
            raise Invalid('instruction anchor executable SHA-256 differs from the verified corpus')
        if elf is None:
            elf = parse_elf(executable)

        def read_address(address: int, size: int) -> bytes | None:
            matches = [segment for segment in elf['programs']
                       if segment['type'] == 1 and segment['virtual_address'] <= address
                       and address + size <= segment['virtual_address'] + segment['file_size']]
            if len(matches) != 1:
                return None
            segment = matches[0]
            offset = segment['offset'] + address - segment['virtual_address']
            return executable[offset:offset + size]

        verify_instruction_anchors(source, executable_sha256=executable_hash,
                                   read_address=read_address)
        verified_ee_evidence.add(id(source))

    for row in rows:
        index = row['index']
        if index not in by_index:
            raise Invalid('entry map overlay identity is absent from the executable')
        overlay = by_index[index]
        interface = row.get('interface')
        if interface == 'unresolved':  # v1 compatibility for older map fixtures
            interface_status = 'unresolved'
        elif isinstance(interface, dict):
            required_fields = ('status', 'inputs', 'outputs', 'state', 'evidence', 'unknowns')
            if any(field not in interface for field in required_fields):
                raise Invalid('interface contract lacks required inputs, outputs, state, evidence, or unknowns')
            if interface.get('status') not in ('unresolved', 'partial', 'complete'):
                raise Invalid('interface contract status is invalid')
            if any(not isinstance(interface.get(field), list) for field in required_fields[1:]):
                raise Invalid('interface contract fields must be lists')
            for evidence_ref in interface['evidence']:
                if not isinstance(evidence_ref, dict) or not isinstance(evidence_ref.get('source'), str):
                    raise Invalid('VU interface evidence must name a source and its anchors')
                evidence_name = evidence_ref['source']
                if evidence_name not in evidence:
                    raise Incomplete(f'VU interface evidence is unavailable: {evidence_name}')
                source = evidence[evidence_name]
                if 'instruction_anchors' in source:
                    verify_ee_evidence(source)
                if source.get('overlay_index') not in (None, index):
                    raise Invalid('VU interface evidence names a different overlay')
                anchors = source.get('overlay_mapping', {}).get('anchors', [])
                requested_addresses = evidence_ref.get('anchor_addresses')
                if not isinstance(requested_addresses, list) or not requested_addresses:
                    raise Invalid('VU interface evidence must name instruction anchor addresses')
                mapping = source.get('overlay_mapping', {})
                if mapping.get('section_base') not in (hex(overlay['vu_byte_address']),
                                                       f"0x{overlay['vu_byte_address']:x}"):
                    raise Invalid(f"VU interface evidence overlay base contradicts executable inventory: "
                                  f"{mapping.get('section_base')} != {hex(overlay['vu_byte_address'])}")
                by_address = {anchor.get('address'): anchor for anchor in anchors if isinstance(anchor, dict)}
                for address_text in requested_addresses:
                    anchor = by_address.get(address_text)
                    if anchor is None:
                        raise Invalid('VU interface evidence refers to an absent instruction anchor')
                    try:
                        address = int(address_text, 16)
                        raw_anchor = bytes.fromhex(anchor['raw_bytes'])
                    except (KeyError, TypeError, ValueError) as exc:
                        raise Invalid('VU interface instruction anchor has malformed raw bytes') from exc
                    if executable is None:
                        raise Incomplete('verified executable is required to check VU interface anchors')
                    relative = address - overlay['vu_byte_address']
                    if relative < 0 or relative + len(raw_anchor) > overlay['bytes']:
                        raise Invalid('VU interface instruction anchor lies outside its overlay')
                    offset = overlay['source_offset'] + relative
                    if executable[offset:offset + len(raw_anchor)] != raw_anchor:
                        raise Invalid(f'VU interface instruction anchor bytes differ at {address_text}')
            if interface['status'] == 'complete':
                if (not interface['inputs'] or not interface['outputs'] or not interface['state'] or
                        not interface['evidence'] or interface['unknowns']):
                    raise Invalid('complete interface requires evidenced inputs, outputs, state, and no unknowns')
                complete_interfaces.append(index)
            elif interface['status'] == 'partial':
                if not interface['evidence'] or not interface['unknowns']:
                    raise Invalid('partial interface requires evidence and explicit unknowns')
                partial_interfaces.append(index)
            interface_status = interface['status']
        else:
            raise Invalid('interface contract must be unresolved or an evidenced mapping')
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
            if id(source) not in verified_ee_evidence:
                verify_ee_evidence(source)
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
            'partial_interface_overlay_indices': partial_interfaces,
            'complete_interface_overlay_indices': complete_interfaces,
            'interface_status': 'documented' if len(complete_interfaces) == 8 else 'incomplete',
            'interfaces': [{'overlay_index': row['index'],
                            'status': (row['interface'].get('status')
                                       if isinstance(row['interface'], dict) else row['interface'])}
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
            'encoding_status': 'pass',
            'work_directory': str(work), 'whole_game_decompiled': False,
            'claim_limits': inventory['claim_limits'] + [
                'Mnemonic source, signed branch displacement conversion, and nine-digit binary32 literals reproduce these chunks byte for byte.',
                'No raw-opcode fallback is used. This is reconstruction/encoding validation, not a behavioral or scheduling oracle.']}
    try:
        entry_map, evidence = load_entry_map(entry_map_path)
        entry_map_result = validate_entry_map(entry_map, inventory['overlays'], evidence, executable=data)
    except (Incomplete, Invalid, ValueError, KeyError, TypeError, OSError) as exc:
        status = 'incomplete' if isinstance(exc, (Incomplete, FileNotFoundError)) else 'fail'
        details.update(entry_map={'status': status, 'diagnostic': str(exc)},
                       entry_map_disposition=status, interface_status=status)
        error = Incomplete if status == 'incomplete' else Invalid
        raise error(f'VU byte reassembly passed; entry map {status}: {exc}', details) from exc
    details.update(entry_map=entry_map_result,
                   interface_status=entry_map_result['interface_status'],
                   entry_map_disposition='incomplete' if entry_map_result['incomplete_overlay_indices'] else 'documented')
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
