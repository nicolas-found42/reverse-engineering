#!/usr/bin/env python3
"""Recheck isolated misc3d boundary reconciliation and retain only safe metadata."""
import argparse
import json
from pathlib import Path
import struct

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from matching_ranges import EE_CORPUS_SHA256
from misc3d_observation import observe
from misc3d_lifecycle import SPANS
from ps2_executables import parse_elf

TARGETS = (0x1d17a8, 0x1d17c8, 0x1d1800, 0x1d1840, 0x1d1844, 0x1d1880, 0x1d18c0)


def validate_boundary(boundary: dict) -> None:
    expected = {'status': 'pass', 'executable_sha256': EE_CORPUS_SHA256,
                'original_entry': '001d1844', 'original_bytes': 60,
                'raw_load_previously_owned': False, 'reconciled_entry': '001d1840',
                'reconciled_end_exclusive': '001d1880', 'reconciled_bytes': 64,
                'reconciled_instruction_count': 16}
    if any(boundary.get(key) != value for key, value in expected.items()):
        raise Invalid('isolated boundary receipt contradicts the recorded reconciliation')


def reconcile(data: bytes, before: dict, after: dict, boundary: dict) -> dict:
    if sha256(data) != EE_CORPUS_SHA256:
        raise Invalid('lifecycle observation requires the unchanged recorded executable')
    validate_boundary(boundary)
    old_observation, new_observation = observe(data, before), observe(data, after)
    originals = {f['entry']: f for f in before['functions']}
    corrected = {f['entry']: f for f in after['functions']}
    if '001d1844' not in originals or '001d1840' not in corrected:
        raise Incomplete('original or reconciled saved function boundary missing')
    if '001d1844' in corrected or any(i['address'] == '001d1840'
            for f in before['functions'] for i in f['instructions']):
        raise Invalid('original or reconciled ownership contradicts the raw-load boundary')
    for functions, entry, size in ((originals, 0x1d1844, 60), (corrected, 0x1d1840, 64)):
        addresses = [int(i['address'], 16) for i in functions[f'{entry:08x}']['instructions']]
        if addresses != list(range(entry, 0x1d1880, 4)) or functions[f'{entry:08x}']['size'] != size:
            raise Invalid('saved sibling span is disjoint, overlapping or incomplete')
    elf = parse_elf(data)
    file_sections = [s for s in elf['sections'] if s['type'] != 8 and s['flags'] & 2]

    def payload(start, size):
        found = [s for s in file_sections if s['address'] <= start
                 and start + size <= s['address'] + s['size']]
        if len(found) != 1:
            raise Invalid('lifecycle span lacks unique file storage')
        offset = found[0]['offset'] + start - found[0]['address']
        return data[offset:offset + size]

    owners = {int(i['address'], 16): f['entry'] for f in after['functions'] for i in f['instructions']}
    references, accesses = [], []
    for section in file_sections:
        for offset in range(0, section['size'] - 3, 4):
            site = section['address'] + offset
            word = struct.unpack_from('<I', data, section['offset'] + offset)[0]
            if word in TARGETS:
                references.append({'site': f'{site:08x}', 'to': f'{word:08x}',
                                   'kind': 'aligned_literal', 'saved_owner': owners.get(site)})
            if not section['flags'] & 4:
                continue
            opcode = word >> 26
            target = ((site + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
            if opcode in (2, 3) and target in TARGETS:
                references.append({'site': f'{site:08x}', 'to': f'{target:08x}',
                                   'kind': 'jal' if opcode == 3 else 'j', 'saved_owner': owners.get(site),
                                   'window_sha256': sha256(payload(site, 24))})
            if opcode in (0x23, 0x2b) and (word >> 21) & 31 == 28:
                displacement = word & 0xffff
                if displacement & 0x8000:
                    displacement -= 0x10000
                cell = 0x295d70 + displacement
                if cell in (0x290ac4, 0x290ac8, 0x290acc, 0x290ad0, 0x290ad4):
                    accesses.append({'site': f'{site:08x}', 'cell': f'{cell:08x}',
                                     'kind': 'load' if opcode == 0x23 else 'store', 'width': 4,
                                     'register': (word >> 16) & 31, 'saved_owner': owners.get(site),
                                     'word_sha256': sha256(payload(site, 4))})
    if any(r['to'] == '001d1844' for r in references + boundary.get('incoming_saved_references', [])):
        raise Invalid('incoming reference to interior saved entry contradicts the full source-unit boundary')
    spans = {name: {'address': f'{start:08x}', 'bytes': size,
                    'sha256': sha256(payload(start, size))} for name, start, size in SPANS}
    release = corrected.get('001d17c8')
    if release is None or release['callees'] != ['00120aa8']:
        raise Invalid('release dependency differs from the recorded callee')
    dependency = corrected.get('00120aa8')
    if dependency is None:
        raise Incomplete('release callee saved body is missing')
    dependency_record = {'entry': '00120aa8', 'saved_bytes': dependency['size'],
                         'entry_window_bytes': 64, 'entry_window_sha256': sha256(payload(0x120aa8, 64)),
                         'ordered_instruction_word_sha256': sha256(b''.join(bytes.fromhex(i['bytes'])
                                                    for i in dependency['instructions'])),
                         'normal_return_sites': [i['address'] for i in dependency['instructions']
                                                 if int.from_bytes(bytes.fromhex(i['bytes']), 'little') == 0x03e00008],
                         'input': 'A0 is shifted right20 then masked15, forming an index with stride276 into base00233070. Pointer stored in a shared GP cell before cleanup calls.',
                         'return': 'Normal return site exists; wrapper ignores its value. Original declaration unknown.',
                         'ownership': 'External dependency only; no attribution or implementation credit.'}
    return {'executable_sha256': EE_CORPUS_SHA256, 'boundary': boundary,
            'spans': spans, 'incoming_references': references, 'cell_accesses': accesses,
            'previous_accessor_observation': old_observation['spans']['accessor'],
            'reconciled_db_id_loads': new_observation['cell_accesses'],
            'release_callee': '00120aa8', 'release_dependency': dependency_record,
            'search_boundary': 'All aligned file-backed allocated words, direct J/JAL and literal pointers; all saved instruction bytes compared to ELF. No computed alias or unaligned-pointer analysis.',
            'limits': ['No direct or literal incoming references to release or siblings observed.',
                       'No sibling caller argument/return use or runtime reachability established.',
                       'Loader saved body is noncontiguous; its envelope receives no attribution.',
                       'New spans remain ownership candidates; original accessor retains its prior decision.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('original_inventory', type=Path)
    parser.add_argument('reconciled_inventory', type=Path)
    parser.add_argument('boundary', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def action():
        missing, observations, inventories = [], {}, {}
        try:
            corpus_identity(args.game)
        except Incomplete as exc:
            missing.append(str(exc))
        ee_path = args.game / 'extracted/SLES_517.05'
        data = None
        if ee_path.is_file():
            data = ee_path.read_bytes()
            if sha256(data) != EE_CORPUS_SHA256:
                raise Invalid('lifecycle observation requires the unchanged recorded executable')
        else:
            missing.append('required EE executable is absent: ' + str(ee_path))
        boundary = {}
        if args.boundary.is_file():
            boundary = json.loads(args.boundary.read_text())
            validate_boundary(boundary)
        else:
            missing.append('required isolated boundary receipt is absent: ' + str(args.boundary))
        for name, path in [('original_inventory', args.original_inventory),
                           ('reconciled_inventory', args.reconciled_inventory)]:
            if not path.is_file():
                missing.append('required ' + name + ' is absent: ' + str(path))
                continue
            inventories[name] = json.loads(path.read_text())
            if data is not None:
                try:
                    observations[name] = observe(data, inventories[name])
                except Incomplete as exc:
                    missing.append(name + ': ' + str(exc))
                    observations[name] = exc.details
        if data is None or missing:
            raise Incomplete('; '.join(missing), {'observations': observations, 'boundary': boundary})
        result = reconcile(data, inventories['original_inventory'],
                           inventories['reconciled_inventory'], boundary)
        result['private_inputs'] = {name: identity(path) for name, path in (
            ('original_inventory', args.original_inventory),
            ('reconciled_inventory', args.reconciled_inventory), ('boundary', args.boundary))}
        return result

    inputs = [Path(__file__), args.game / 'extracted/SLES_517.05', args.original_inventory, args.reconciled_inventory, args.boundary,
                         *(Path(__file__).resolve().parent / name for name in (
                             'corpus_contract.py', 'evidence_common.py', 'matching_ranges.py',
                             'misc3d_observation.py', 'misc3d_lifecycle.py', 'ps2_executables.py'))]
    return write_result(args.output, 'misc3d-lifecycle-observation', action,
                        [path for path in inputs if path.is_file()])


if __name__ == '__main__':
    raise SystemExit(main())
