"""Section chain of an FR2 `.PS2` model, translated from the executable's loader.

Verified on the unchanged PAL corpus only. The loader (`FUN_0011ed90`) parses the buffer as a chain:

1. name tree: word 0 is the byte offset of the next section, rounded up to 16 (`FUN_00123908`);
2. texture library (`FUN_0022ba30`): three palette-block counts A, B, C; a 12-byte table entry per block;
   the blocks themselves (A and C blocks of 0x400 bytes, B blocks of 0x40); a count N and one extra word;
   then N items, each a flags word, a length-prefixed name, a 0x40-byte descriptor (format byte at 0x34,
   mip-level count at 0x35, a 64-bit field at 0x38 whose bits 15-18 and 19-22 are log2 width and height),
   a 0x10-byte record per mip level, and finally the image planes, each 16-byte aligned;
3. the next section starts at the 16-byte-aligned end and opens with a record count (records of 0x34 bytes).

Level-zero decoding covers format 1 (32-bit linear) and formats 3/4 under the
bounded static upload contract in ps2_texture_indices. Descriptor bit8 selects
packed upload versus direct linear indices. Mips and later geometry remain
separate, and no original rendering or hardware execution is claimed.
"""

from __future__ import annotations

from functools import lru_cache
import struct

from evidence_common import Invalid, sha256
from format_contracts import model

FORMATS = {1, 2, 3, 4}
MAX_BLOCKS = 4096
MAX_ITEMS = 4096
MAX_NAME = 256
MAX_DIM = 2048
MAX_MIPS = 8
NEXT_RECORD = 0x34


class Unsupported(ValueError):
    """The item is valid but its pixels are outside the measured decoding profile."""


def align16(n: int) -> int:
    return (n + 15) & ~15


def level_bytes(fmt: int, w: int, h: int) -> int:
    return {1: w * h * 4, 2: w * h * 2, 3: w * h, 4: w * h // 2}[fmt]


# Static mip upload contract, traced from FUN_0022ba30/FUN_00222358/FUN_00222110
# (see notes/evidence/fr2-texture-upload-audit/mip-upload-static-audit/README.md).
# Format and descriptor bit8 select the transfer representation; each extra-level
# slot halves both transfer dimensions; QWC is (w*h*bpp)>>7. Pixel decoding of
# levels above zero is unresolved; only plane spans and byte counts are covered.
UPLOAD_SLOTS = 3
TRANSFER_BITS = {
    (1, False): 32,
    (3, False): 8,
    (3, True): 32,
    (4, False): 4,
    (4, True): 16,
}


def check_mip_count(mips: int) -> None:
    if mips > UPLOAD_SLOTS:
        raise Invalid(
            f"mip count {mips} exceeds the {UPLOAD_SLOTS} extra-level slots of the traced uploader"
        )


def check_level_plane(fmt: int, level: dict) -> None:
    expected = level_bytes(fmt, level["width"], level["height"])
    if level["size"] != expected:
        raise Invalid(
            f"level {level['level']} plane is {level['size']} bytes; "
            f"format {fmt} needs {expected} for {level['width']}x{level['height']}"
        )


def check_level_upload(
    fmt: int, packed: bool, level: dict, transfer_w: int, transfer_h: int
) -> int:
    """Predicted transfer bytes for one level; rejects mispredicted sizes."""
    try:
        bpp = TRANSFER_BITS[(fmt, packed)]
    except KeyError:
        raise Invalid(
            f"format {fmt} packed={packed} has no measured transfer route"
        ) from None
    predicted = (transfer_w * transfer_h * bpp) // 128 * 16
    if predicted != level["size"]:
        raise Invalid(
            f"level {level['level']} plane is {level['size']} bytes; "
            f"upload predicts {predicted} for {transfer_w}x{transfer_h} at {bpp} bpp"
        )
    return predicted


def mip_coverage(data: bytes) -> dict:
    """Per-level plane spans and upload byte counts for every texture in one model."""
    parsed = parse(data)
    levels, source, predicted, rejected = 0, 0, 0, []
    for item in parsed["textures"]["items"]:
        descriptor = data[item["descriptor_offset"] : item["descriptor_offset"] + 0x40]
        (field,) = struct.unpack_from("<Q", descriptor, 0x38)
        packed = bool(field & 256)
        transfer_w, transfer_h = 1 << ((field >> 23) & 15), 1 << ((field >> 27) & 15)
        try:
            check_mip_count(item["mips"])
        except Invalid as exc:
            rejected.append(f"texture {item['index']}: {exc}")
            continue
        for level in item["levels"]:
            try:
                check_level_plane(item["format"], level)
                predicted += check_level_upload(
                    item["format"],
                    packed,
                    level,
                    transfer_w >> level["level"],
                    transfer_h >> level["level"],
                )
                source += level["size"]
                levels += 1
            except Invalid as exc:
                rejected.append(
                    f"texture {item['index']} level {level['level']}: {exc}"
                )
    return {
        "levels": levels,
        "source_plane_bytes": source,
        "predicted_transfer_bytes": predicted,
        "rejected_levels": rejected,
    }


def check_palette_reference(item: dict, block_sizes: list[int]) -> dict:
    """Class, entry count and index bound for one indexed texture's palette reference."""
    index = item["palette_index"]
    if index >= len(block_sizes):
        raise Invalid(
            f"texture {item['index']}: palette index {index} outside the {len(block_sizes)}-entry table"
        )
    size = block_sizes[index]
    allowed = {3: (0x400,), 4: (0x40, 0x400)}.get(item["format"], ())
    if size not in allowed:
        raise Invalid(
            f"texture {item['index']}: format {item['format']} palette block is {size:#x} bytes; "
            f"measured sizes are {['%#x' % v for v in allowed]}"
        )
    entries = 256 if size == 0x400 else 16
    if item["format"] == 4:
        entries = 16
    return {"entries": entries, "max_index": entries - 1}


def palette_coverage(data: bytes) -> dict:
    """Palette block spans and per-texture index bounds for one model."""
    parsed = parse(data)
    tex = parsed["textures"]
    a, b, c = tex["palette_blocks"]
    sizes = [0x400] * a + [0x40] * b + [0x400] * c
    region_start, region_end = tex["palette_region"]
    offsets, references, rejected = [], [], []
    cursor = region_start
    for size in sizes:
        offsets.append(cursor)
        cursor += size
    for item in tex["items"]:
        if item["format"] == 1:
            continue
        try:
            bound = check_palette_reference(item, sizes)
        except Invalid as exc:
            rejected.append(str(exc))
            continue
        index = item["palette_index"]
        klass = "A" if index < a else ("B" if index < a + b else "C")
        references.append(
            {
                "name": item["name"],
                "index": item["index"],
                "class": klass,
                "entries": bound["entries"],
                "max_index": bound["max_index"],
                "span": [offsets[index], offsets[index] + sizes[index]],
                "span_within_region": region_start <= offsets[index]
                and offsets[index] + sizes[index] <= region_end,
            }
        )
    return {"blocks": sizes, "references": references, "rejected_references": rejected}


def parse(data: bytes) -> dict:
    tree = model(data)
    pool_end = tree["leading_count"]
    start = align16(pool_end)

    def need(pos: int, size: int, what: str) -> None:
        if pos < 0 or size < 0 or pos + size > len(data):
            raise Invalid(
                f"{what} at {pos:#x} (+{size}) exceeds the {len(data)}-byte file"
            )

    need(start, 12, "texture section header")
    a, b, c = struct.unpack_from("<3I", data, start)
    if max(a, b, c) > MAX_BLOCKS:
        raise Invalid(f"palette block counts {(a, b, c)} exceed the bound {MAX_BLOCKS}")
    total = a + b + c
    table = start + 12
    need(table, 12 * total, "palette block table")
    palettes = align16(table + 12 * total)
    block_size = [0x400] * a + [0x40] * b + [0x400] * c
    block_at = [palettes + sum(block_size[:i]) for i in range(total)]
    pos = palettes + sum(block_size)
    need(palettes, pos - palettes, "palette blocks")
    need(pos, 8, "texture count")
    count, extra = struct.unpack_from("<2I", data, pos)
    if count > MAX_ITEMS:
        raise Invalid(f"texture count {count} exceeds the bound {MAX_ITEMS}")
    pos += 8
    items = []
    for i in range(count):
        need(pos, 8, f"texture {i} header")
        flags, length = struct.unpack_from("<2I", data, pos)
        pos += 8
        if not 1 <= length <= MAX_NAME:
            raise Invalid(f"texture {i}: name length {length} outside 1..{MAX_NAME}")
        need(pos, length, f"texture {i} name")
        raw = data[pos : pos + length]
        name = raw.split(b"\0")[0]
        if raw[-1:] != b"\0" or not name or not all(32 <= ch < 127 for ch in name):
            raise Invalid(f"texture {i}: name is not a printable NUL-terminated string")
        pos += length
        if flags & 1:
            raise Invalid(
                f"texture {i}: items without image data are outside the measured profile"
            )
        pos = align16(pos)
        need(pos, 0x40, f"texture {i} descriptor")
        struct_at = pos
        palette_index = struct.unpack_from("<I", data, pos)[0]
        fmt, mips = data[pos + 0x34], data[pos + 0x35]
        (field,) = struct.unpack_from("<Q", data, pos + 0x38)
        width, height = 1 << ((field >> 15) & 0xF), 1 << ((field >> 19) & 0xF)
        if fmt not in FORMATS:
            raise Invalid(f"texture {i}: unknown format {fmt}")
        if mips > MAX_MIPS or width > MAX_DIM or height > MAX_DIM:
            raise Invalid(
                f"texture {i}: mips {mips} or size {width}x{height} outside the measured profile"
            )
        if mips >= min(width, height).bit_length():
            raise Invalid(
                f"texture {i}: {mips} mips exceed the {min(width, height).bit_length() - 1} halvings a {width}x{height} image supports"
            )
        if fmt in (3, 4) and palette_index >= total:
            raise Invalid(
                f"texture {i}: palette index {palette_index} outside the {total}-entry table"
            )
        pos += 0x40 + 0x10 * mips
        need(struct_at, pos - struct_at, f"texture {i} descriptor and mip records")
        items.append(
            {
                "index": i,
                "name": name.decode("ascii"),
                "flags": flags,
                "descriptor_offset": struct_at,
                "format": fmt,
                "mips": mips,
                "width": width,
                "height": height,
                "palette_index": palette_index,
                "palette_offset": block_at[palette_index]
                if palette_index < total
                else None,
                "palette_bytes": block_size[palette_index]
                if palette_index < total
                else None,
                "descriptor_field": f"{field:#018x}",
                "levels": [],
            }
        )
    for it in items:
        w, h = it["width"], it["height"]
        for level in range(it["mips"] + 1):
            pos = align16(pos)
            size = level_bytes(it["format"], w, h)
            need(pos, size, f"texture {it['index']} level {level} image data")
            it["levels"].append(
                {"level": level, "offset": pos, "size": size, "width": w, "height": h}
            )
            pos += size
            w, h = w >> 1, h >> 1
    end = align16(pos)
    need(end, 4, "record count of the next section")
    (records,) = struct.unpack_from("<I", data, end)
    if 4 + NEXT_RECORD * records > len(data) - end:
        raise Invalid(
            f"next section announces {records} records of {NEXT_RECORD} bytes, which do not fit after {end:#x}"
        )
    return {
        "tree": {"name_pool_end": pool_end, "next_section_offset": start},
        "textures": {
            "section_start": start,
            "palette_blocks": (a, b, c),
            "palette_table_sha256": sha256(data[table : table + 12 * total]),
            "palette_region": [palettes, palettes + sum(block_size)],
            "extra_word": extra,
            "image_count": count,
            "items": items,
            "section_end": end,
        },
        "next_section": {
            "offset": end,
            "record_count": records,
            "record_bytes": NEXT_RECORD,
        },
    }


@lru_cache(maxsize=64)
def _block_order8(w: int, h: int) -> tuple[int, ...]:
    """Source index in the GS 8-bit block layout for each pixel of a w x h image, row-major."""
    order = []
    for y in range(h):
        for x in range(w):
            block = (y & ~0xF) * w + (x & ~0xF) * 2
            swap = (((y + 2) >> 2) & 1) * 4
            row = (((y & ~3) >> 1) + (y & 1)) & 7
            column = row * w * 2 + ((x + swap) & 7) * 4
            order.append(block + column + ((y >> 1) & 1) + ((x >> 2) & 2))
    return tuple(order)


def unswizzle8(plane: bytes, w: int, h: int) -> bytes:
    if w < 16 or h < 16 or w % 16 or h % 16:
        raise Unsupported(f"8-bit block layout needs multiples of 16; got {w}x{h}")
    order = _block_order8(w, h)
    if len(plane) < w * h or max(order) >= len(plane):
        raise Unsupported("plane is shorter than the block layout requires")
    return bytes(map(plane.__getitem__, order))


def decode_rgba(data: bytes, item: dict) -> bytes:
    """Level-0 RGBA with the stored alpha (the game's palettes use 0..0x80 as opaque)."""
    level = item["levels"][0]
    plane = data[level["offset"] : level["offset"] + level["size"]]
    if item["format"] == 1:
        return plane
    if item["format"] in (3, 4):
        from ps2_texture_indices import decode_indices

        count = 256 if item["format"] == 3 else 16
        palette_size = count * 4
        allowed_sizes = (0x400,) if item["format"] == 3 else (0x40, 0x400)
        if item["palette_bytes"] not in allowed_sizes:
            raise Unsupported(
                f"format {item['format']} palette block is outside the measured profile"
            )
        pixels = decode_indices(data, item)
        palette_block = data[
            item["palette_offset"] : item["palette_offset"] + item["palette_bytes"]
        ]
        if len(palette_block) != item["palette_bytes"]:
            raise Invalid("palette bytes are outside the input")
        # The 16x16 PSMCT32 upload of a 256-color A/C block follows the
        # loader's bit3/4 permutation; CSM0/CSA0 then restores raw indices
        # 0..15 for PSMT4, as does the unpermuted 8x2 sixteen-color upload.
        palette = palette_block[:palette_size]
        entries = [palette[4 * i : 4 * i + 4] for i in range(count)]
        return b"".join(map(entries.__getitem__, pixels))
    raise Unsupported(f"format {item['format']} pixel layout is not decoded")
