"""Build a minimal little-endian MIPS ELF32 from named sections, for tests.

    data = build_elf([Spec(".text", words, flags=6, address=0x100100),
                      Spec(".sbss", b"", kind=8, address=0x290000, size=0x20)])

Section payloads sit after the ELF header at 16-byte alignment; the section table and the
`.shstrtab` follow. There are no program headers. Defaults describe the retail EE executable
(machine 8, `e_flags` 0x20924001). The result parses with `ps2_executables.parse_elf`.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

PROGBITS = 1
STRTAB = 3
NOBITS = 8
EE_FLAGS = 0x20924001


@dataclass(frozen=True)
class Spec:
    name: str
    data: bytes = b""
    kind: int = PROGBITS
    flags: int = 2  # SHF_ALLOC
    address: int | None = None  # defaults to 0x100000 + 0x100 per section
    size: int | None = None  # NOBITS size; defaults to len(data)
    alignment: int = 16  # section-header alignment; payload placement stays 16-byte aligned


def _align(value: int, to: int = 16) -> int:
    return (value + to - 1) & ~(to - 1)


def build_elf(specs: list[Spec], *, machine: int = 8, flags: int = EE_FLAGS,
              entry: int = 0x100008) -> bytes:
    names = b"\0"
    name_at = {}
    for spec in [*specs, Spec(".shstrtab", kind=STRTAB, flags=0)]:
        name_at[spec.name] = len(names)
        names += spec.name.encode() + b"\0"
    body = bytearray(52)
    placed = []
    for spec in specs:
        offset = _align(len(body))
        body.extend(bytes(offset - len(body)))
        if spec.kind != NOBITS:
            body.extend(spec.data)
        placed.append((spec, offset if spec.kind != NOBITS else _align(len(body))))
    names_at = _align(len(body))
    body.extend(bytes(names_at - len(body)))
    body.extend(names)
    table = _align(len(body), 4)
    body.extend(bytes(table - len(body)))
    rows = [bytes(40)]
    for index, (spec, offset) in enumerate(placed):
        size = (spec.size if spec.size is not None else len(spec.data))
        address = spec.address if spec.address is not None else 0x100000 + 0x100 * (index + 1)
        rows.append(struct.pack("<10I", name_at[spec.name], spec.kind, spec.flags, address,
                                offset, size, 0, 0, spec.alignment, 0))
    rows.append(struct.pack("<10I", name_at[".shstrtab"], STRTAB, 0, 0, names_at, len(names),
                            0, 0, 1, 0))
    body.extend(b"".join(rows))
    struct.pack_into("<16sHHIIIIIHHHHHH", body, 0, b"\x7fELF\x01\x01\x01" + bytes(9), 2, machine,
                     1, entry, 0, table, flags, 52, 32, 0, 40, len(rows), len(rows) - 1)
    return bytes(body)
