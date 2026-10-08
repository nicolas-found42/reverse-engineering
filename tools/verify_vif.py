#!/usr/bin/env python3
"""Verify two guarded static CNT/END VIF upload packets against ELF overlays.

Passing means exact packet bytes statically contain bounded MPG spans that map
one-to-one to all eight DVP overlay byte ranges. The two caller/helper paths
and DMA-channel pointer table are additionally guarded by exact executable
identity and raw instruction/table bytes. This does not demonstrate that either
routine ran, establish scheduling, interpret VU code, or prove geometry/output.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct

from evidence_common import Incomplete, Invalid, write_result
from ps2_executables import parse_elf
from ps2_vif import parse_chain, public_chain
from ps2_vu import parse_overlays


EXECUTABLE_SHA256 = '216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95'

# Whole function instruction bytes captured from the saved static instruction
# inventory. Exact executable identity is required as well; these local guards
# make the caller/argument/register evidence auditable without trusting prose.
STATIC_CODE = {
    0x0022fd48: bytes.fromhex('f0ffbd270000b0ff0800bfff4ed0070c010004242d8040002100023c0000038eff0f053ce07b4224ffffa5344000633424284500000003ae1ad1070c2d2000022d2000020800bfdf2d2800000000b0df2d300000c2d107081000bd27'),
    0x00114fe0: bytes.fromhex('0000023c0000033c600442240000632423104300f0ffbd27011042280000b0ff070040140800bfff2500043c2500063c90128424b812c6242216040c1c0005244ed0070c2d200000ff0f053c2d8040002200023c0000038ee0ac4224ffffa5342d20000240006334242845001ad1070c000003ae2d2000020800bfdf2d2800000000b0df2d300000c2d107081000bd27'),
    0x001f4138: bytes.fromhex('0a00822c060040102500023c80180400b8d04224211862000800e0030000628c0800e0032d100000'),
    0x001f4468: bytes.fromhex('d0ffbd270000b0ff2d8080001000b1ff2000bfff36d0070c2d20a0002d884000f8cf070c2d200002ffff023c3000038effff423401006254300011ae0000028ef3ff0324200000ae241043002000bfdf050142341000b1df000002ae0000b0df0800e0033000bd27'),
    0x001f40d8: bytes.fromhex('070003240217040005004314ff0f023c0080033cffff423424208200252083000800e0032d108000'),
}
CHANNEL_TABLE_ADDRESS = 0x0024d0b8
CHANNEL_TABLE_BYTES = bytes.fromhex('0080001000900010')

CHAIN_PROFILES = (
    {
        'name': 'vu1-static-upload', 'start': 0x00217be0, 'channel_index': 1,
        'channel': 'VIF1', 'qwc': 782, 'end': 0x0021acd0,
        'expected': [(0, 256, 2048), (256, 256, 2048), (512, 256, 2048),
                     (768, 256, 2048), (1024, 256, 2048), (1280, 256, 2048),
                     (1536, 22, 176)],
    },
    {
        'name': 'vu0-static-upload', 'start': 0x0021ace0, 'channel_index': 0,
        'channel': 'VIF0', 'qwc': 70, 'end': 0x0021b150,
        'expected': [(0, 140, 1120)],
    },
)


def virtual_slice(data: bytes, elf: dict, address: int, size: int, label: str) -> tuple[bytes, int]:
    if address < 0 or size <= 0 or address + size > 0x1_0000_0000:
        raise Invalid(f'{label} has an invalid 32-bit address span')
    matches = []
    for segment in elf['programs']:
        if (segment['type'] == 1 and segment['virtual_address'] <= address
                and address + size <= segment['virtual_address'] + segment['file_size']):
            offset = segment['offset'] + address - segment['virtual_address']
            if offset + size <= len(data):
                matches.append(offset)
    if len(matches) != 1:
        raise Incomplete(f'{label} does not map uniquely to file-backed PT_LOAD bytes')
    offset = matches[0]
    return data[offset:offset + size], offset


def check_static_guards(data: bytes, elf: dict) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXECUTABLE_SHA256:
        raise Incomplete('only the pinned SLES_517.05 executable identity is supported')
    guarded = {}
    for address, expected in STATIC_CODE.items():
        raw, offset = virtual_slice(data, elf, address, len(expected), f'static code at {address:08x}')
        if raw != expected:
            raise Invalid(f'raw instruction bytes differ from the guarded source at {address:08x}')
        guarded[f'{address:08x}'] = {'file_offset': offset, 'bytes': len(raw),
                                     'sha256': hashlib.sha256(raw).hexdigest()}
    table, table_offset = virtual_slice(data, elf, CHANNEL_TABLE_ADDRESS,
                                        len(CHANNEL_TABLE_BYTES), 'DMA channel pointer table')
    if table != CHANNEL_TABLE_BYTES:
        raise Invalid('DMA channel pointer table words differ from the guarded VIF0/VIF1 values')
    words = list(struct.unpack('<2I', table))
    return {
        'executable_sha256': digest,
        'guarded_functions': guarded,
        'channel_pointer_table': {
            'address': f'{CHANNEL_TABLE_ADDRESS:08x}', 'file_offset': table_offset,
            'words': [f'{word:08x}' for word in words],
            'index_0': {'register_address': f'{words[0]:08x}', 'label': 'VIF0'},
            'index_1': {'register_address': f'{words[1]:08x}', 'label': 'VIF1'},
        },
        'static_conditional_ownership': [
            {'caller': '0022fd48', 'channel_index': 1, 'packet_address': '00217be0',
             'when': 'if this caller executes and the guarded helper path is reached'},
            {'caller': '00114fe0', 'channel_index': 0, 'packet_address': '0021ace0',
             'when': 'if this caller executes and the guarded helper path is reached'},
        ],
        'limits': [
            'Raw code and pointer-table guards ground a static conditional ownership mapping; neither caller execution nor DMA completion was observed.',
            'CHCR tag-transfer enable and unchanged non-SPR pointer behavior are established only for the guarded helper instruction bytes.',
        ],
    }


def verify(data: bytes) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXECUTABLE_SHA256:
        raise Incomplete('only the pinned SLES_517.05 executable identity is supported')
    elf = parse_elf(data)
    guards = check_static_guards(data, elf)
    overlays = parse_overlays(data)
    if overlays['executable_sha256'] != guards['executable_sha256']:
        raise Invalid('overlay parser executable identity differs from the guarded executable')

    parsed_chains = []
    transfer_rows = []
    for profile in CHAIN_PROFILES:
        # The QWC itself is read only to size the bounded span; it is immediately
        # checked against the pinned profile before the full packet is parsed.
        prefix, _ = virtual_slice(data, elf, profile['start'], 16, profile['name'] + ' CNT tag')
        first_word = struct.unpack_from('<I', prefix)[0]
        qwc = first_word & 0xffff
        if qwc != profile['qwc']:
            raise Invalid(f"{profile['name']} QWC differs from guarded value {profile['qwc']}")
        packet_size = 16 + qwc * 16 + 16
        packet, packet_offset = virtual_slice(data, elf, profile['start'], packet_size, profile['name'])
        if profile['start'] + packet_size - 16 != profile['end']:
            raise Invalid(f"{profile['name']} END address does not match its guarded profile")
        parsed = parse_chain(packet, profile['start'], tte=True)
        if parsed['qwc'] != profile['qwc'] or parsed['end_tag_address'] != profile['end']:
            raise Invalid(f"{profile['name']} parsed chain bounds differ from the guarded profile")
        actual = [(row['instruction_index'], row['instruction_pairs'], row['bytes'])
                  for row in parsed['chunks']]
        if actual != profile['expected']:
            raise Invalid(f"{profile['name']} MPG destination/count sequence differs from the guarded profile")
        parsed['name'] = profile['name']
        parsed['packet_file_offset'] = packet_offset
        parsed['channel_index'] = profile['channel_index']
        parsed['channel'] = profile['channel']
        parsed_chains.append(parsed)
        for row in parsed['chunks']:
            transfer_rows.append({**row, 'chain': profile['name'],
                                  'channel_index': profile['channel_index'],
                                  'channel': profile['channel']})

    overlay_rows = overlays['overlays']
    if len(overlay_rows) != 8:
        raise Invalid(f'expected eight mapped DVP overlays; found {len(overlay_rows)}')
    unmatched = list(range(len(overlay_rows)))
    matches = []
    for chunk in transfer_rows:
        candidates = [index for index in unmatched
                      if overlay_rows[index]['vu_byte_address'] == chunk['vu_byte_address']
                      and overlay_rows[index]['bytes'] == chunk['bytes']]
        if len(candidates) != 1:
            raise Invalid('MPG payload does not identify exactly one remaining VU overlay by VMA/length')
        index = candidates[0]
        overlay = overlay_rows[index]
        mapped, _ = virtual_slice(data, elf, overlay['load_address'], overlay['bytes'], overlay['name'])
        # parse_overlays independently returns its exact source offset. Require
        # the transfer bytes to equal the bytes at that very file offset.
        source = data[overlay['source_offset']:overlay['source_offset'] + overlay['bytes']]
        packet_file_offset = chunk['payload_packet_offset'] + next(
            x['packet_file_offset'] for x in parsed_chains if x['name'] == chunk['chain'])
        if (mapped != source or source != chunk['payload']
                or packet_file_offset != overlay['source_offset']
                or chunk['payload_chain_address'] != overlay['load_address']):
            raise Invalid('MPG bytes differ from the exact parse_overlays source span')
        if hashlib.sha256(source).hexdigest() != overlay['sha256']:
            raise Invalid('overlay source bytes fail parse_overlays SHA-256')
        matches.append({
            'chain': chunk['chain'], 'channel': chunk['channel'],
            'channel_index': chunk['channel_index'],
            'mpg_instruction_index': chunk['instruction_index'],
            'vu_byte_address': chunk['vu_byte_address'],
            'instruction_pairs': chunk['instruction_pairs'], 'bytes': chunk['bytes'],
            'packet_chain_address': f"{chunk['payload_chain_address']:08x}",
            'packet_file_offset': packet_file_offset,
            'overlay_index': overlay['index'], 'overlay_name': overlay['name'],
            'overlay_load_address': f"{overlay['load_address']:08x}",
            'overlay_source_offset': overlay['source_offset'],
            'exact_bytes_match': True, 'exact_file_offset_match': True,
            'exact_load_address_match': True, 'sha256': overlay['sha256'],
        })
        unmatched.remove(index)
    if unmatched:
        raise Incomplete('one or more VU overlays have no matching MPG transfer',
                         {'unmatched_overlay_indices': unmatched})
    if len(matches) != 8 or len(transfer_rows) != 8:
        raise Invalid('transfer-to-overlay cardinality is not exactly eight')

    return {
        'status': 'verified_static_packet_mapping',
        'executable_sha256': guards['executable_sha256'],
        'static_guards': guards,
        'dma_chains': [public_chain(row) for row in parsed_chains],
        'overlay_count': len(overlay_rows), 'transfer_count': len(transfer_rows),
        'matched_count': len(matches), 'unmatched_overlay_count': len(unmatched),
        'matches': matches,
        'total_instruction_pairs': sum(row['instruction_pairs'] for row in matches),
        'total_transferred_bytes': sum(row['bytes'] for row in matches),
        'whole_game_execution_or_render_proven': False,
        'claim_limits': [
            'All eight static MPG payload byte spans match exactly one parse_overlays source span, with no unmatched overlays or extra transfers.',
            'The first seven chunks map conditionally to VIF1 over VU byte-address range [0,12464); the last maps conditionally to VIF0 over [0,1120).',
            'No runtime upload, VU scheduling, geometry semantics, or rendered output is established.',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path,
                        default=Path('games/ford-racing-2/extracted/SLES_517.05'))
    parser.add_argument('--output', type=Path, default=Path('.scratch/evidence/vif'))
    args = parser.parse_args()
    return write_result(args.output, 'vif-static-mapping',
                        lambda: verify(args.executable.read_bytes()), [args.executable])


if __name__ == '__main__':
    raise SystemExit(main())
