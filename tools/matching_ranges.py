#!/usr/bin/env python3
"""Inventory every PT_LOAD byte, including section gaps and zero-fill layout.

This is structural accounting, not game/SDK attribution. ADR-0005 leaves the
entire load image unresolved until measured range decisions are committed.
The file command accepts synthetic ELF fixtures; it cannot earn corpus credit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, sha256, write_result
from ps2_executables import parse_elf, parse_romdir
from ps2_vu import parse_overlays

ROOT = Path(__file__).resolve().parent.parent
IOP_RECEIPT = ROOT / ('notes/evidence/fr2-static-recovery/iop/results/'
                      '20261004T094558Z-d5361c498cad468ba50e450e88c7b88b/result.json')


def load_image_partition(data: bytes) -> dict:
    """Return section-mapped ranges covering the declared load images."""
    elf = parse_elf(data)
    ranges = []
    images = sorted((p['virtual_address'], p['virtual_address'] + p['memory_size'])
                    for p in elf['programs'] if p['type'] == 1 and p['memory_size'])
    for previous, current in zip(images, images[1:]):
        if current[0] < previous[1]:
            raise Invalid(f'PT_LOAD images overlap at {current[0]:#x}')
    for index, program in enumerate(elf['programs']):
        if program['type'] != 1 or not program['memory_size']:
            continue
        start = program['virtual_address']
        end = start + program['memory_size']
        file_end = start + program['file_size']
        mapped = [s for s in elf['sections'] if s['flags'] & 2 and s['size']
                  and s['address'] < end and s['address'] + s['size'] > start]
        ordered = sorted(mapped, key=lambda s: s['address'])
        for left, right in zip(ordered, ordered[1:]):
            if right['address'] < left['address'] + left['size']:
                raise Invalid(f"allocated sections overlap at {right['address']:#x}: "
                              f"{left.get('name')} and {right.get('name')}")
        for section in mapped:
            address = section['address']
            if address < start or address + section['size'] > end:
                raise Invalid(f"section {section.get('name')} extends outside its PT_LOAD image")
            if section['type'] == 8:
                if address < file_end:
                    raise Invalid(f"NOBITS section {section.get('name')} overlaps initialized bytes")
            elif address + section['size'] > file_end or (
                    section['offset'] != program['offset'] + address - start):
                raise Invalid(f"section {section.get('name')} file mapping differs from PT_LOAD")
        boundaries = {start, end, file_end}
        for section in mapped:
            boundaries.update((max(start, section['address']),
                               min(end, section['address'] + section['size'])))
        points = sorted(boundaries)
        for lower, upper in zip(points, points[1:]):
            owners = [s for s in mapped if s['address'] <= lower
                      and s['address'] + s['size'] >= upper]
            backed = lower < file_end
            offset = program['offset'] + lower - start if backed else None
            ranges.append({
                'program': index, 'address': lower, 'length': upper - lower,
                'section': owners[0].get('name') if len(owners) == 1 else None,
                'file_offset': offset, 'storage': 'initialized' if backed else 'zero_fill',
                'classification': 'mixed_unresolved', 'decision': 'ADR-0005',
                'evidence': 'ELF PT_LOAD and SHF_ALLOC boundaries',
                'sha256': sha256(data[offset:offset + upper - lower]) if backed else None,
            })
    if not ranges:
        raise Incomplete('no nonempty PT_LOAD image; section-only inputs do not establish load layout')
    outside = [
        {'section': s.get('name'), 'address': s['address'], 'length': s['size'],
         'storage': 'zero_fill' if s['type'] == 8 else 'initialized',
         'classification': 'mixed_unresolved'}
        for s in elf['sections'] if s['flags'] & 2 and s['size']
        and not any(start <= s['address'] and s['address'] + s['size'] <= end
                    for start, end in images)
    ]
    return {
        'artifact_sha256': sha256(data), 'ranges': ranges,
        'allocated_sections_outside_load_images': outside,
        'file_backed_bytes': sum(r['length'] for r in ranges if r['storage'] == 'initialized'),
        'zero_fill_bytes': sum(r['length'] for r in ranges if r['storage'] == 'zero_fill'),
        'unresolved_bytes': sum(r['length'] for r in ranges),
        'game_owned_bytes': 0, 'matched_bytes': 0, 'substitute_bytes': 0,
        'evidence_authority': 'structural_file_inventory',
        'claim_limits': ['Complete declared load-image accounting only; no attribution or rebuild.',
                         'Zero-fill layout has no retail file bytes to compare.',
                         'All ranges remain unresolved; this inventory cannot pass reconstruction.'],
    }


def corpus_load_images(game: Path) -> dict:
    """Pin every module against the retained inventory, then account its image."""
    provenance = corpus_identity(game)
    extracted = game / 'extracted'
    expected = json.loads(IOP_RECEIPT.read_text())['details']['modules']
    standalone = {row['source']: row for row in expected if row['offset'] == 0}
    discovered = {p.relative_to(extracted).as_posix() for p in (extracted / 'IRX').iterdir()
                  if p.is_file() and p.suffix.upper() == '.IRX'}
    if discovered != set(standalone):
        missing, additional = set(standalone) - discovered, discovered - set(standalone)
        if additional:
            raise Invalid(f'additional IOP modules: {sorted(additional)}')
        raise Incomplete(f'missing IOP modules: {sorted(missing)}')
    container = (extracted / 'IRX/IOPRP255.IMG').read_bytes()
    embedded = parse_romdir(container)['modules']
    expected_embedded = {row['name']: row for row in expected if row['offset'] != 0}
    if {row['name'] for row in embedded} != set(expected_embedded):
        raise Invalid('embedded IOP module inventory differs from the recorded corpus')
    payloads = []
    for row in embedded:
        pinned = expected_embedded[row['name']]
        payload = container[row['offset']:row['offset'] + row['bytes']]
        if (row['offset'], row['bytes'], sha256(payload)) != (
                pinned['offset'], pinned['bytes'], pinned['sha256']):
            raise Invalid(f"changed embedded IOP module: {row['name']}")
        payloads.append((row['name'], payload))
    for source, row in sorted(standalone.items()):
        payload = (extracted / source).read_bytes()
        if (len(payload), sha256(payload)) != (row['bytes'], row['sha256']):
            raise Invalid(f'changed IOP module: {source}')
        payloads.append((row['name'], payload))
    executable = (extracted / 'SLES_517.05').read_bytes()
    artifacts = [{'artifact': 'EE', **load_image_partition(executable)}]
    for name, payload in payloads:
        artifacts.append({'artifact': 'IOP:' + name, **load_image_partition(payload)})
    return {
        'provenance': provenance, 'module_inventory_sha256': sha256(IOP_RECEIPT.read_bytes()),
        'artifacts': artifacts, 'iop_modules': len(payloads),
        'vu_programs': parse_overlays(executable)['overlays'],
        'file_backed_bytes': sum(a['file_backed_bytes'] for a in artifacts),
        'zero_fill_bytes': sum(a['zero_fill_bytes'] for a in artifacts),
        'unresolved_bytes': sum(a['unresolved_bytes'] for a in artifacts),
        'game_owned_bytes': 0, 'matched_bytes': 0, 'substitute_bytes': 0,
        'evidence_authority': 'pinned_corpus_structural_inventory',
        'attribution_status': 'incomplete',
        'claim_limits': ['All initialized load bytes and zero-fill layout remain mixed/unresolved.',
                         'This is not source reconstruction, ownership attribution or byte matching.',
                         'IOP addresses are link-relative; runtime load bases remain unobserved.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['file', 'corpus'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'corpus':
        return write_result(args.output, 'matching-range-inventory:corpus',
                            lambda: corpus_load_images(args.input), [IOP_RECEIPT])
    return write_result(args.output, 'matching-range-inventory:file',
                        lambda: load_image_partition(args.input.read_bytes()), [args.input])


if __name__ == '__main__':
    raise SystemExit(main())
