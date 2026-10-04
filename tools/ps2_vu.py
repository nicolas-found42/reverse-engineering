"""Recover DVP load-address mappings and assemble-able VU instruction text.

Layout basis: ps2dev/binutils-gdb 3eb45ea37f0efd498d1de3cf9562de07197aefa8,
gas/config/tc-dvp.c:2570-2630 and include/elf/mips.h:513-520.
The synthetic overlay section describes a size/address; code lives at its LMA.
"""
import hashlib
import math
import re
import struct

from evidence_common import Incomplete, Invalid
from ps2_executables import parse_elf


def parse_overlays(data: bytes) -> dict:
    elf = parse_elf(data)
    if elf['type'] != 2:
        raise Incomplete('DVP LMA inspection requires a linked executable, not an unrelocated object')
    named = {}
    for section in elf['sections']:
        name = section.get('name', '')
        if not name:
            continue
        if name in named:
            raise Invalid('duplicate ELF section name makes DVP mapping ambiguous')
        named[name] = section
    required = ('.DVP.ovlytab', '.DVP.ovlystrtab')
    if any(name not in named for name in required):
        raise Incomplete('DVP overlay table or string table is absent')
    table, strings = [named[name] for name in required]
    if table['type'] != 0x7FFFF420 or strings['type'] != 3:
        raise Invalid('DVP overlay metadata has unexpected section types')
    if table['size'] % 12 or not 0 < table['size'] // 12 <= 4096:
        raise Invalid('DVP overlay table must contain bounded 12-byte records')
    pool = data[strings['offset']:strings['offset'] + strings['size']]
    rows = []
    seen = set()
    for index in range(table['size'] // 12):
        name_offset, lma, vma = struct.unpack_from('<3I', data, table['offset'] + index * 12)
        end = pool.find(b'\0', name_offset)
        if name_offset >= len(pool) or end < 0:
            raise Invalid('DVP overlay name is outside its string table')
        try:
            name = pool[name_offset:end].decode('ascii')
        except UnicodeDecodeError as exc:
            raise Invalid('DVP overlay name is not ASCII') from exc
        if name not in named or not name.startswith('.DVP.overlay.') or name in seen:
            raise Invalid('DVP overlay name is missing, repeated, or outside its namespace')
        seen.add(name)
        overlay = named[name]
        size = overlay['size']
        if overlay['type'] != 0x7FFFF421 or not size or size % 8 or vma % 8 or vma + size > 16384:
            raise Invalid('DVP overlay extent is outside the eight-byte VU/16-KiB profile')
        sources = [section for section in elf['sections']
                   if section['type'] == 1 and section['flags'] & 2
                   and section['address'] <= lma and lma + size <= section['address'] + section['size']]
        if len(sources) != 1:
            raise Invalid('DVP LMA does not map uniquely into file-backed allocated PROGBITS')
        source = sources[0]
        offset = source['offset'] + lma - source['address']
        loads = [program for program in elf['programs']
                 if program['type'] == 1 and program['virtual_address'] <= lma
                 and lma + size <= program['virtual_address'] + program['file_size']
                 and offset == program['offset'] + lma - program['virtual_address']]
        if len(loads) != 1:
            raise Invalid('DVP LMA and section mapping disagree with ELF LOAD file mapping')
        code = data[offset:offset + size]
        placeholder = data[overlay['offset']:overlay['offset'] + size]
        rows.append({'index': index, 'name': name, 'load_address': lma, 'vu_byte_address': vma,
                     'bytes': size, 'instruction_pairs': size // 8,
                     'source_section': source.get('name'), 'source_offset': offset,
                     'sha256': hashlib.sha256(code).hexdigest(),
                     'placeholder_offset': overlay['offset'],
                     'placeholder_nonzero_bytes': sum(bool(value) for value in placeholder),
                     'placeholder_sha256': hashlib.sha256(placeholder).hexdigest()})
    return {'executable_sha256': elf['sha256'], 'overlay_count': len(rows),
            'code_bytes': sum(row['bytes'] for row in rows),
            'instruction_pairs': sum(row['instruction_pairs'] for row in rows),
            'overlays': rows,
            'claim_limits': ['LMA/code bounds and bytes only; VU0/VU1 ownership and semantic meaning remain unverified.',
                             'Overlays may share VU addresses; metadata identities remain separate.']}


def canonical_source(disassembly: str, data: bytes, vma: int) -> tuple[str, dict]:
    """Convert native objdump text to GAS operands without raw-opcode fallbacks.

Objdump prints byte-address branch targets, whereas GAS numeric branch operands
are signed instruction displacements. Its six-digit float output also loses
binary32 precision; literals use nine significant digits from the lower word.
"""
    if len(data) % 8:
        raise Invalid('VU code is not a whole number of instruction pairs')
    instructions = []
    branches, floats = [], []
    pattern = re.compile(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+){4})\s*(\S.*)$')
    for line in disassembly.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        index = len(instructions)
        if index >= len(data) // 8 or int(match.group(1), 16) != vma + index * 8:
            raise Invalid('objdump pair address/count differs from the input span')
        lower_text = bytes.fromhex(match.group(2))
        if lower_text != data[index * 8:index * 8 + 4]:
            raise Invalid('objdump displayed bytes differ from input lower word')
        text = match.group(3)
        if '*unknown*' in text:
            raise Incomplete('DVP disassembler returned an unknown instruction')
        if not re.match(r'^[a-z]', text):
            raise Invalid('objdump instruction is outside the expected mnemonic syntax')
        branch = re.search(r'\b(b|bal|ibeq|ibne|ibgtz|ibltz|iblez|ibgez)\s+.*?(0x[0-9a-f]+)\s*$', text)
        if branch:
            target = int(branch.group(2), 16)
            delta = target - (vma + index * 8 + 8)
            if delta % 8 or not -1024 <= delta // 8 <= 1023:
                raise Invalid('VU branch target is outside signed 11-bit displacement range')
            displacement = delta // 8
            text = text[:branch.start(2)] + str(displacement)
            branches.append({'pair': index, 'target': target, 'signed_displacement': displacement})
        if re.search(r'\bloi\s', text):
            lower, upper = struct.unpack_from('<2I', data, index * 8)
            if not upper & 0x80000000:
                raise Invalid('LOI text has no upper-word immediate flag')
            value = struct.unpack('<f', struct.pack('<I', lower))[0]
            if not math.isfinite(value):
                raise Incomplete('nonfinite LOI requires a separately supported exact representation')
            literal = format(value, '.9g')
            text = re.sub(r'\bloi\s+.*$', 'loi ' + literal, text)
            floats.append({'pair': index, 'literal': literal, 'bits': f'{lower:08x}'})
        instructions.append(text)
    if len(instructions) != len(data) // 8:
        raise Invalid('objdump did not emit exactly one mnemonic pair per eight input bytes')
    return '.vu\n' + '\n'.join(instructions) + '\n', {
        'instruction_pairs': len(instructions), 'branches': branches, 'float_literals': floats,
        'raw_opcode_fallbacks': 0,
    }
