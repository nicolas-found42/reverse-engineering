#!/usr/bin/env python3
"""Inventory every PT_LOAD byte and apply the one identity-pinned ADR-0005 split.

Structural accounting alone earns no matching credit. Corpus mode records the
first measured source-unit range; completion.py separately validates its fresh
build receipt. The file command accepts synthetic ELF fixtures and cannot earn
corpus ownership or matching credit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from ps2_executables import parse_elf, parse_romdir
from ps2_vu import parse_overlays

ROOT = Path(__file__).resolve().parent.parent
IOP_RECEIPT = ROOT / ('notes/evidence/fr2-static-recovery/iop/results/'
                      '20261004T094558Z-d5361c498cad468ba50e450e88c7b88b/result.json')
EE_CORPUS_SHA256 = '216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95'
UNIT_START, UNIT_END = 0x001D1800, 0x001D183C
UNIT_SHA256 = '1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e'
UNIT_SOURCE_SHA256 = '44b17bacf38c4a9befdb77dca2b137ac1e0826cb595ad7dd87c4775dfa5375bc'
UNIT_SOURCE = ROOT / 'reconstruction/ee/app3d/misc3d_db_id.c'
ADR0005 = ROOT / 'docs/adr/0005-game-owned-sdk-boundary.md'
SOURCE_MAP = ROOT / 'notes/evidence/fr2-source-map/source-map-result.json'
BOUNDARY_METADATA = ROOT / 'notes/evidence/fr2-first-unit/adr0005-misc3d-boundary.json'
SAVED_FUNCTION_INVENTORY = ROOT / 'notes/evidence/fr2-first-unit/saved-function-inventory-digest.json'


def boundary_provenance() -> dict:
    """Verify the local metadata's source-map and saved-function evidence hashes."""
    evidence_paths = (BOUNDARY_METADATA, SOURCE_MAP, SAVED_FUNCTION_INVENTORY)
    for path in evidence_paths:
        if not path.is_file():
            raise Incomplete(f'first-unit boundary evidence missing: {path}')
    metadata = json.loads(BOUNDARY_METADATA.read_text())
    source_map = json.loads(SOURCE_MAP.read_text())
    if (source_map.get('status') != 'pass'
            or metadata.get('evidence_inputs', {}).get('source_map', {}).get('status') != 'pass'):
        raise Invalid('first-unit source-map evidence must report pass consistently with boundary metadata')
    inventory = json.loads(SAVED_FUNCTION_INVENTORY.read_text())
    functions = inventory.get('functions', [])
    if (inventory.get('executable_sha256') != EE_CORPUS_SHA256
            or len(functions) != 1 or functions[0].get('entry') != f'{UNIT_START:08x}'
            or functions[0].get('size') != UNIT_END - UNIT_START):
        raise Invalid('first-unit structural inventory digest contradicts the recorded corpus or range')
    source_map_id, inventory_id = identity(SOURCE_MAP), identity(SAVED_FUNCTION_INVENTORY)
    evidence = metadata.get('evidence_inputs', {})
    if (metadata.get('corpus', {}).get('sha256') != EE_CORPUS_SHA256
            or evidence.get('source_map', {}).get('sha256') != source_map_id['sha256']
            or evidence.get('saved_function_inventory', {}).get('sha256') != inventory_id['sha256']
            or metadata.get('range', {}).get('sha256') != UNIT_SHA256
            or metadata.get('range', {}).get('start') != f'{UNIT_START:08x}'
            or metadata.get('range', {}).get('end_exclusive') != f'{UNIT_END:08x}'):
        raise Invalid('first-unit ownership metadata does not match its source-map, inventory, or range')
    return {'metadata': identity(BOUNDARY_METADATA), 'source_map': source_map_id,
            'saved_function_inventory': inventory_id}


def attribute_first_source_unit(artifact: dict, executable: bytes) -> None:
    """Split one identity-pinned EE range; structural inventory still earns no match."""
    if sha256(executable) != EE_CORPUS_SHA256:
        return
    elf = parse_elf(executable)
    text_sections = [s for s in elf['sections'] if s.get('name') == '.text'
                     and s['address'] <= UNIT_START and s['address'] + s['size'] >= UNIT_END]
    if len(text_sections) != 1:
        raise Invalid('recorded first-unit span is not uniquely contained by EE .text')
    section = text_sections[0]
    offset = section['offset'] + UNIT_START - section['address']
    unit_bytes = executable[offset:offset + UNIT_END - UNIT_START]
    if len(unit_bytes) != UNIT_END - UNIT_START or sha256(unit_bytes) != UNIT_SHA256:
        raise Invalid('recorded first-unit bytes differ from ADR-0005 evidence')
    candidate_source_identity = sha256(UNIT_SOURCE.read_bytes())
    evidence_inputs = boundary_provenance()
    decision_identity = sha256(ADR0005.read_bytes())
    output = []
    for row in artifact['ranges']:
        start, end = row['address'], row['address'] + row['length']
        if row['section'] != '.text' or end <= UNIT_START or start >= UNIT_END:
            output.append(row)
            continue
        for lower, upper in ((start, min(end, UNIT_START)),
                             (max(start, UNIT_START), min(end, UNIT_END)),
                             (max(start, UNIT_END), end)):
            if lower >= upper:
                continue
            child = dict(row, address=lower, length=upper - lower)
            if row['storage'] == 'initialized':
                child['file_offset'] = row['file_offset'] + lower - start
                child['sha256'] = sha256(executable[child['file_offset']:
                                                    child['file_offset'] + upper - lower])
            if lower == UNIT_START and upper == UNIT_END:
                child.update(classification='game_owned', decision='ADR-0005',
                             unit='misc3d_db_id',
                             reconstruction_source_sha256=UNIT_SOURCE_SHA256,
                             candidate_source_sha256=candidate_source_identity,
                             build_unit='reconstruction/ee/app3d/misc3d_db_id.c',
                             decision_sha256=decision_identity,
                             evidence_inputs=evidence_inputs,
                             evidence='identity-pinned source-built unit range')
            output.append(child)
    artifact['ranges'] = output
    artifact['game_owned_bytes'] = sum(r['length'] for r in output
                                       if r['classification'] == 'game_owned')
    artifact['unresolved_bytes'] = sum(r['length'] for r in output
                                       if r['classification'] != 'game_owned')
    # Structural inventory records ownership only; byte-match credit belongs to
    # completion.py after it verifies a fresh source-build receipt.
    artifact['matched_bytes'] = 0


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
        'substitute_disposition': 'no ranges attributed as substitute',
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
    missing, additional = set(standalone) - discovered, discovered - set(standalone)
    if additional:
        raise Invalid(f'additional IOP modules: {sorted(additional)}')
    payloads = []
    for source, row in sorted(standalone.items()):
        if source in missing:
            continue
        payload = (extracted / source).read_bytes()
        if (len(payload), sha256(payload)) != (row['bytes'], row['sha256']):
            raise Invalid(f'changed IOP module: {source}')
        payloads.append((row['name'], payload))
    container = (extracted / 'IRX/IOPRP255.IMG').read_bytes()
    embedded = parse_romdir(container)['modules']
    expected_embedded = {row['name']: row for row in expected if row['offset'] != 0}
    if {row['name'] for row in embedded} != set(expected_embedded):
        raise Invalid('embedded IOP module inventory differs from the recorded corpus')
    for row in embedded:
        pinned = expected_embedded[row['name']]
        payload = container[row['offset']:row['offset'] + row['bytes']]
        if (row['offset'], row['bytes'], sha256(payload)) != (
                pinned['offset'], pinned['bytes'], pinned['sha256']):
            raise Invalid(f"changed embedded IOP module: {row['name']}")
        payloads.append((row['name'], payload))
    if missing:
        raise Incomplete(f'missing IOP modules: {sorted(missing)}')
    executable = (extracted / 'SLES_517.05').read_bytes()
    ee_artifact = {'artifact': 'EE', **load_image_partition(executable)}
    attribute_first_source_unit(ee_artifact, executable)
    artifacts = [ee_artifact]
    for name, payload in payloads:
        artifacts.append({'artifact': 'IOP:' + name, **load_image_partition(payload)})
    return {
        'provenance': provenance, 'module_inventory_sha256': sha256(IOP_RECEIPT.read_bytes()),
        'artifacts': artifacts, 'iop_modules': len(payloads),
        'vu_programs': parse_overlays(executable)['overlays'],
        'file_backed_bytes': sum(a['file_backed_bytes'] for a in artifacts),
        'zero_fill_bytes': sum(a['zero_fill_bytes'] for a in artifacts),
        'unresolved_bytes': sum(a['unresolved_bytes'] for a in artifacts),
        'game_owned_bytes': sum(a.get('game_owned_bytes', 0) for a in artifacts),
        'matched_bytes': 0, 'substitute_bytes': 0,
        'substitute_disposition': 'no ranges attributed as substitute',
        'evidence_authority': 'pinned_corpus_structural_inventory',
        'attribution_status': 'partial' if ee_artifact['game_owned_bytes'] else 'incomplete',
        'claim_limits': ['Only the exact identity-pinned EE source unit recorded in ADR-0005 is split.',
                         'Structural inventory records zero matched bytes; source-build evidence is separate.',
                         'All other initialized load bytes and zero-fill layout remain mixed/unresolved.',
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
                            lambda: corpus_load_images(args.input),
                            [IOP_RECEIPT, ADR0005, SOURCE_MAP, UNIT_SOURCE,
                             *(p for p in (BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY)
                               if p.is_file())])
    return write_result(args.output, 'matching-range-inventory:file',
                        lambda: load_image_partition(args.input.read_bytes()), [args.input])


if __name__ == '__main__':
    raise SystemExit(main())
