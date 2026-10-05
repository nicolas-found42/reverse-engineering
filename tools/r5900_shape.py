"""Structural plausibility of a 32-bit word as an R5900 instruction.

This is a field-level filter, not a disassembler: it rejects encodings that do
not exist on the R5900 (no COP3, no LL/SC, no double-precision FPU transfers,
reserved SPECIAL functions and REGIMM selectors). Data words often pass it, so
a pass only means the word is not impossible as code; the check is meaningful
only against measured controls, never on its own.
"""

_PRIMARY = (frozenset(range(0x13)) | frozenset(range(0x14, 0x1D)) | {0x1E, 0x1F}
            | frozenset(range(0x20, 0x30)) | {0x31, 0x33, 0x36, 0x37, 0x39, 0x3E, 0x3F})
_SPECIAL = frozenset({0x00, 0x01, 0x02, 0x03, 0x04, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D,
                      0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B}
                     | set(range(0x20, 0x30)) | {0x30, 0x31, 0x32, 0x33, 0x34, 0x36,
                                                 0x38, 0x3A, 0x3B, 0x3C, 0x3E, 0x3F})
_REGIMM = frozenset({0, 1, 2, 3, 8, 9, 10, 11, 12, 14, 16, 17, 18, 19, 24, 25})


def is_plausible(word: int) -> bool:
    opcode = word >> 26
    if opcode == 0x00:
        return (word & 0x3F) in _SPECIAL
    if opcode == 0x01:
        return (word >> 16) & 0x1F in _REGIMM
    return opcode in _PRIMARY
