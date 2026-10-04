"""Parse the game's two bounded PS2 DMA/VIF upload chains.

This intentionally supports only one CNT tag, tag-transfer (TTE) words of an
exact NOP followed by an MPG command, NOP/MPG words in the CNT body, and one
zero-payload END tag. It does not model DMA scheduling,
interrupts, other tag kinds, other VIF commands, or VU execution semantics.
MPG NUM=0 means 256 instruction pairs; IMM is a VU instruction index, so the
reported byte address is IMM * 8. Encoding basis: the pinned ps2dev/binutils-gdb
tree at .scratch/mesh/codex-root/binutils-dvp, especially opcodes/dvp-opc.c
and gas/config/tc-dvp.c (vif_insn_len and MPG data-length handling).
Pinned revision: 3eb45ea37f0efd498d1de3cf9562de07197aefa8. Relevant definitions
are opcodes/dvp-opc.c:1454-1455, 1742-1773, and 2041-2070; the VIF opcode
classification includes include/opcode/dvp.h:284. MPG location is recorded in
dwords and converted to VU byte addresses by gas/config/tc-dvp.c:806-818.
"""
from __future__ import annotations

import hashlib
import struct

from evidence_common import Incomplete, Invalid


def parse_chain(packet: bytes, start_address: int, *, tte: bool = True) -> dict:
    """Parse exactly one CNT -> bounded NOP/MPG stream -> END transfer.

    `packet` begins at the CNT tag and ends immediately after its END tag.
    `start_address` is a label used in evidence; no pointer chasing is done.
    """
    if not tte:
        raise Incomplete('only the statically guarded tag-transfer-enabled profile is supported')
    if start_address < 0 or start_address % 16:
        raise Invalid('DMA chain start address must be nonnegative and qword aligned')
    if len(packet) < 32 or len(packet) % 16:
        raise Invalid('DMA packet must contain aligned CNT data and a complete END tag')

    tag_word, tag_addr, tag_vif0, tag_vif1 = struct.unpack_from('<4I', packet, 0)
    tag_id = (tag_word >> 28) & 7
    qwc = tag_word & 0xffff
    if tag_word & 0x8fff0000:
        raise Incomplete('CNT tag contains unsupported IRQ or reserved flag bits')
    if tag_id != 1:
        raise Incomplete('only a CNT DMA tag is supported at chain start')
    if tag_addr != 0:
        raise Incomplete('CNT tag address word must be zero in this profile')
    if qwc == 0:
        raise Invalid('CNT tag must transfer at least one qword')
    if tag_vif0 != 0:
        raise Incomplete('first TTE upper word must be the guarded NOP before the MPG header')
    if tag_vif1 & 0x80000000 or (tag_vif1 >> 24) != 0x4a:
        raise Incomplete('second TTE upper word must be an MPG header in this profile')

    body_start = 16
    body_end = body_start + qwc * 16
    end_tag_offset = body_end
    if end_tag_offset + 16 != len(packet):
        raise Invalid('CNT QWC does not place the END tag at the exact packet boundary')
    end_word, end_addr, end_vif0, end_vif1 = struct.unpack_from('<4I', packet, end_tag_offset)
    if end_word != 0x70000000 or end_addr != 0 or end_vif0 != 0 or end_vif1 != 0:
        raise Incomplete('only a zero-QWC, zero-address, zero-payload END tag is supported')

    body = packet[body_start:body_end]
    command_words = [(tag_vif0, 'tag-upper-0'), (tag_vif1, 'tag-upper-1')]
    command_index = 0
    body_cursor = 0
    chunks = []
    nops = []

    while True:
        command_offset = None
        if command_index < len(command_words):
            command, command_source = command_words[command_index]
            command_index += 1
        elif body_cursor < len(body):
            if len(body) - body_cursor < 4:
                raise Invalid('VIF body ends with a partial command word')
            command = struct.unpack_from('<I', body, body_cursor)[0]
            command_source = 'cnt-body'
            command_offset = body_cursor
            body_cursor += 4
        else:
            break

        if command == 0:
            nops.append({'source': command_source,
                         'body_offset': command_offset if command_source == 'cnt-body' else None})
            continue
        if command & 0x80000000:
            raise Incomplete('VIF interrupt flag is outside the supported profile')
        if (command >> 24) != 0x4a:
            raise Incomplete(f'unsupported VIF command word {command:#010x}; only NOP and MPG are supported')

        count_field = (command >> 16) & 0xff
        pair_count = count_field or 256
        instruction_index = command & 0xffff
        byte_address = instruction_index * 8
        byte_count = pair_count * 8
        if instruction_index >= 2048 or byte_address + byte_count > 16384:
            raise Invalid('MPG destination exceeds the bounded 16-KiB VU instruction memory profile')
        if body_cursor + byte_count > len(body):
            raise Invalid('MPG payload exceeds the CNT QWC body')
        payload_offset = body_start + body_cursor
        payload = body[body_cursor:body_cursor + byte_count]
        chunks.append({
            'index': len(chunks),
            'command_word': f'{command:08x}',
            'command_source': command_source,
            'command_body_offset': command_offset if command_source == 'cnt-body' else None,
            'instruction_index': instruction_index,
            'vu_byte_address': byte_address,
            'instruction_pairs': pair_count,
            'bytes': byte_count,
            'payload_packet_offset': payload_offset,
            'payload_chain_address': start_address + payload_offset,
            'payload_sha256': hashlib.sha256(payload).hexdigest(),
            'payload': payload,
        })
        body_cursor += byte_count

    if body_cursor != len(body):
        raise Invalid('VIF command stream did not consume the exact CNT QWC body')
    if not chunks:
        raise Incomplete('bounded DMA chain contains no supported MPG payload')

    # Keep the large private payloads available to the verifier, but make them
    # explicit so report serializers can omit bytes safely.
    return {
        'start_address': start_address,
        'qwc': qwc,
        'tag_transfer_enabled': True,
        'encoding_basis': {
            'repository': 'ps2dev/binutils-gdb',
            'revision': '3eb45ea37f0efd498d1de3cf9562de07197aefa8',
            'sources': ['opcodes/dvp-opc.c:1454-1455', 'opcodes/dvp-opc.c:1742-1773',
                        'opcodes/dvp-opc.c:2041-2070', 'include/opcode/dvp.h:284',
                        'gas/config/tc-dvp.c:806-818'],
        },
        'body_bytes': len(body),
        'end_tag_address': start_address + end_tag_offset,
        'chunks': chunks,
        'nop_count': len(nops),
        'nops': nops,
        'claim_limits': [
            'Static packet syntax and MPG byte spans only; runtime transfer is not observed.',
            'VU scheduling, execution, geometry meaning, and rendered output are not established.',
        ],
    }


def public_chain(parsed: dict) -> dict:
    """Return packet evidence without copying executable payload bytes."""
    result = {key: value for key, value in parsed.items() if key != 'chunks'}
    result['chunks'] = [{key: value for key, value in row.items() if key != 'payload'}
                        for row in parsed['chunks']]
    return result
