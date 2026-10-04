"""Provisional pure integer model for the unowned 0x0022a180 leaf candidate.

This models the observed shifts and ORs only. It does not execute or emulate
the game routine, establish a caller contract, or prove that the candidate is
used as an ARGB1555 conversion by the renderer.
"""


def uint32_to_argb1555_candidate(value: int) -> int:
    """Pack little-endian RGBA bytes into the hypothesized A1R5G5B5-style bit layout.

    The machine-code hypothesis maps input byte 0 to output bits 10..14,
    byte 1 to bits 5..9, byte 2 to bits 0..4, and any nonzero byte 3 to bit 15.
    Each color byte is truncated by shifting right three bits.
    """
    if type(value) is not int:
        raise TypeError("value must be an int")
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("value must fit in uint32")

    byte0 = value & 0xFF
    byte1 = (value >> 8) & 0xFF
    byte2 = (value >> 16) & 0xFF
    byte3 = (value >> 24) & 0xFF

    return (
        ((byte2 >> 3) & 0x1F)
        | (((byte1 >> 3) & 0x1F) << 5)
        | (((byte0 >> 3) & 0x1F) << 10)
        | ((1 if byte3 != 0 else 0) << 15)
    )
