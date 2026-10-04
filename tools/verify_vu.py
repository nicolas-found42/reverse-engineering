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


def verify(executable: Path, objdump: Path | None, assembler: Path | None, work: Path) -> dict:
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
        rows.append(row)
        if recovered != code:
            raise Invalid('VU mnemonic round trip differs from executable code bytes', {'tools': tools, 'overlays': rows})
    return {**inventory, 'tools': tools, 'overlays': rows, 'exact_roundtrip_overlays': len(rows),
            'work_directory': str(work), 'whole_game_decompiled': False,
            'claim_limits': inventory['claim_limits'] + [
                'Mnemonic source, signed branch displacement conversion, and nine-digit binary32 literals reproduce these chunks byte for byte.',
                'No raw-opcode fallback is used. This is reconstruction/encoding validation, not a behavioral or scheduling oracle.']}


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
