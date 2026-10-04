#!/usr/bin/env python3
"""Symbol evidence from an IOP IRX that was not stripped.

The ELF `.symtab` names functions, data and import stubs. The ECOFF `.mdebug` section lists the same procedures with
object-relative addresses, so each object file's procedures differ from their linked addresses by one constant. This
module reads the symbol table, pairs procedures with function symbols by name, requires one constant offset per file,
and names import stubs from symbols at the stub addresses. Disagreements are reported or rejected; nothing is guessed.
No module code is run.
"""
import struct

from evidence_common import Invalid
import ps2_executables

SYMBOL = struct.Struct('<IIIBBH')
STT_OBJECT, STT_FUNC, STT_SECTION, STT_FILE = 1, 2, 3, 4


def _section(elf: dict, name: str) -> dict:
    found = [s for s in elf['sections'] if s.get('name') == name]
    if not found:
        raise Invalid(f'module has no {name} section')
    return found[0]


def read_symbols(data: bytes) -> list[dict]:
    elf = ps2_executables.parse_elf(data)
    table = _section(elf, '.symtab')
    strings = elf['sections'][table['link']]
    if table['offset'] + table['size'] > len(data) or strings['offset'] + strings['size'] > len(data):
        raise Invalid('symbol table lies outside the file')
    symbols = []
    for at in range(1, table['size'] // SYMBOL.size):
        name, value, size, info, _other, _section_index = SYMBOL.unpack_from(data, table['offset'] + at * SYMBOL.size)
        if name >= strings['size']:
            raise Invalid('symbol name offset is outside the string table')
        raw = data[strings['offset'] + name:strings['offset'] + strings['size']]
        symbols.append({'name': raw.split(b'\0', 1)[0].decode('latin-1'), 'value': value, 'size': size,
                        'type': info & 15, 'bind': info >> 4})
    return symbols


def link_procedures(procedures: list[dict], symbols: list[dict]) -> dict:
    functions = {s['name']: s for s in symbols if s['type'] == STT_FUNC}
    offsets: dict[str, int] = {}
    linked, disagreements = [], []
    for procedure in procedures:
        symbol = functions.get(procedure['name'])
        if symbol is None:
            raise Invalid(f"procedure {procedure['name']} has no function symbol")
        delta = symbol['value'] - procedure['address']
        if offsets.setdefault(procedure['file'], delta) != delta:
            raise Invalid(f"procedures of {procedure['file']} do not share one address offset")
        if procedure['size'] is not None and procedure['size'] != symbol['size']:
            disagreements.append(procedure['name'])
        linked.append({**procedure, 'linked_address': symbol['value']})
    return {'procedures': linked, 'file_offsets': offsets, 'size_disagreements': disagreements}


def stub_names(stub_offsets: list[int], symbols: list[dict]) -> dict[int, str]:
    wanted = set(stub_offsets)
    names: dict[int, str] = {}
    for symbol in symbols:
        if symbol['type'] in (STT_OBJECT, STT_FUNC) and symbol['value'] in wanted and symbol['value'] not in names:
            names[symbol['value']] = symbol['name']
    return names


PROLOGUE_WORDS = 6
ADDIU_SP_SP = 0x27BD0000


def frame_agreement(procedures: list[dict], text: bytes) -> dict:
    """Compare each procedure's debug frame size with the `addiu sp,sp,-N` found in its first instructions."""
    agree, disagreements, none, outside = 0, [], 0, 0
    for procedure in procedures:
        start = procedure['linked_address']
        if start % 4 or start + 4 > len(text):
            outside += 1
            continue
        adjust = None
        for at in range(start, min(start + 4 * PROLOGUE_WORDS, len(text) - 3), 4):
            word = struct.unpack_from('<I', text, at)[0]
            if word & 0xFFFF0000 == ADDIU_SP_SP and word & 0x8000:
                adjust = 0x10000 - (word & 0xFFFF)
                break
        if adjust is None:
            none += 1
        elif adjust == procedure['frame_bytes']:
            agree += 1
        else:
            disagreements.append({'name': procedure['name'], 'prologue': adjust, 'debug': procedure['frame_bytes']})
    return {'agree': agree, 'disagree': len(disagreements), 'no_adjustment': none, 'outside_text': outside,
            'disagreements': disagreements}
