"""Measured structure of FR2 .ptg files beyond the single-sprite profile.

Verified for the unchanged PAL corpus only. Header words are
`[count, columns, rows, stride, cell, width, height, last]`. In all 548 files count == columns * rows,
stride == cell and columns/rows == ceil(width/cell) / ceil(height/cell). Files whose last word is
0xDDDDDDDD follow an exact layout; every other multi-tile file is checked at header level only.
Palette location, pointer meaning and the descriptor constants are not recovered.
"""

import struct

from evidence_common import Invalid, sha256
from format_contracts import sprite

DD = 0xDDDDDDDD
HEADER, PREFIX_END, RECORD, DESCRIPTOR, TILE_BYTES, TAIL_BYTES = 32, 80, 16, 64, 1024, 1040
BASE_SIZE, TILE_SIZE = 1120, 1104  # PREFIX_END + TAIL_BYTES, and RECORD + DESCRIPTOR + TILE_BYTES
MAX_BYTES = 128 * 1024 * 1024
DESCRIPTOR_PADDING_WORDS = (2, 3, 4, 5, 6, 7, 8, 9, 11, 15)
DESCRIPTOR_CONSTANT_WORDS = (0, 1, 12, 13, 14)


class HeaderRelationError(Invalid):
    """A universal header relation failed."""


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def header(data: bytes) -> dict:
    if len(data) < HEADER:
        raise HeaderRelationError(f"truncated header: {len(data)} bytes")
    count, columns, rows, stride, cell, width, height, last = struct.unpack("<8I", data[:HEADER])
    if cell == 0 or width == 0 or height == 0:
        raise HeaderRelationError("cell, width and height must be positive")
    if stride != cell:
        raise HeaderRelationError(f"stride {stride} differs from cell {cell}")
    if columns != -(-width // cell):
        raise HeaderRelationError(f"columns {columns} differ from ceil({width}/{cell})")
    if rows != -(-height // cell):
        raise HeaderRelationError(f"rows {rows} differ from ceil({height}/{cell})")
    if count != columns * rows:
        raise HeaderRelationError(f"count {count} differs from columns * rows = {columns * rows}")
    return {"count": count, "columns": columns, "rows": rows, "cell": cell, "width": width, "height": height, "last": last}


def tiled_dd(data: bytes, h: dict) -> dict:
    count, columns, cell = h["count"], h["columns"], h["cell"]
    if len(data) != BASE_SIZE + TILE_SIZE * count:
        raise Invalid(f"size {len(data)} differs from 1120 + 1104 * {count} = {BASE_SIZE + TILE_SIZE * count}")
    pointers = []
    for i in range(count):
        extent_u, extent_v, pointer, pad = struct.unpack_from("<4I", data, PREFIX_END + RECORD * i)
        want_u = min(cell, h["width"] - (i % columns) * cell) / cell
        want_v = min(cell, h["height"] - (i // columns) * cell) / cell
        if (extent_u, extent_v) != (f32_bits(want_u), f32_bits(want_v)) or pad != DD:
            raise Invalid(f"tile {i}: pointer-record extent differs from the row-major position extent ({want_u}, {want_v})")
        pointers.append(pointer)
    base = PREFIX_END + RECORD * count
    constants = None
    for i in range(count):
        words = struct.unpack_from("<16I", data, base + DESCRIPTOR * i)
        if any(words[j] != DD for j in DESCRIPTOR_PADDING_WORDS):
            raise Invalid(f"descriptor {i}: words that must be 0xDDDDDDDD differ")
        current = tuple(words[j] for j in DESCRIPTOR_CONSTANT_WORDS)
        if constants is None:
            constants = current
        elif current != constants:
            raise Invalid(f"descriptor words 0, 1 and 12-14 are not constant across tiles: tile {i} differs")
    pixels = base + DESCRIPTOR * count
    tail = data[pixels + TILE_BYTES * count :]
    return {
        "tiles": {"count": count, "columns": columns, "rows": h["rows"], "cell": cell, "order": "row-major"},
        "spans": {
            "prefix": [HEADER, PREFIX_END],
            "pointer_records": [PREFIX_END, base],
            "descriptors": [base, pixels],
            "pixels": [pixels, pixels + TILE_BYTES * count],
            "tail": [len(data) - len(tail), len(data)],
        },
        "pixel_sha256": sha256(data[pixels : pixels + TILE_BYTES * count]),
        "pointer_range": [min(pointers), max(pointers)],
        "pointer_values_within_file": all(p < len(data) for p in pointers),
        "descriptor_constants": [hex(v) for v in constants or ()],
        "tail_fill": hex(tail[0]) if tail and len(set(tail)) == 1 else "varied",
        "prefix_sha256": sha256(data[HEADER:PREFIX_END]),
    }


UNRESOLVED_DD = [
    "palette location and format: none located; the pixel region holds 8-bit indices",
    "tile pointer values: not file offsets as measured; meaning unknown",
    "descriptor words 0, 1 and 12-14: constant within a file; meaning unknown",
    "48-byte prefix and 1040-byte tail purpose",
]


def classify(data: bytes) -> dict:
    h = header(data)
    result = {"header": h, "bytes": len(data), "sha256": sha256(data)}
    if h["count"] == 1:
        try:
            parsed = sprite(data)
        except Invalid as exc:
            return result | {"profile": "single_unsupported", "diagnostic": f"outside the sprite contract: {exc}", "unresolved": ["pixel layout"]}
        return result | {"profile": "sprite", "pixel_sha256": parsed["pixel_sha256"], "unresolved": ["palette/table role"]}
    if h["last"] == DD and h["cell"] == 32:
        return result | {"profile": "tiled_dd", **tiled_dd(data, h), "unresolved": UNRESOLVED_DD}
    return result | {
        "profile": "tiled_header_only",
        "unresolved": ["body layout: only the universal header relations are verified"],
    }
