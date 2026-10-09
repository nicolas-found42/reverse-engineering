#!/usr/bin/env python3
"""Independent FR2 model texture-library check; exits 0=pass, 1=fail, 2=incomplete.

Separate from the other checks. Parses the section chain of each `.PS2` model the way the executable's
loader does (name tree, texture library, start of the next section) and decodes level-0 pixels for
format 1 (32-bit linear) and indexed formats 3/4 under the bounded static model
upload contract. Descriptor bit8 selects packed versus direct source indices.
Every mip level carries measured plane spans and predicted upload sizes under the traced
uploader's byte-count contract; palette references carry class spans and index bounds.
Mip pixels above level 0, palette entry contents and later sections stay unresolved.
"""

import argparse
import collections
import struct
from pathlib import Path

import ps2_container
from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result

MAX_BYTES = 128 * 1024 * 1024
UNRESOLVED = [
    "format 2 (16-bit): handled by the parser's size rules but absent from the corpus",
    "indexed texture dimensions or transfer/buffer-width profiles outside the bounded measured level-zero contract",
    "mip pixels above level 0: plane spans and upload byte counts are covered, pixels are not decoded",
    "contents of palette blocks and the 12-byte palette table entries (only spans, bounds and hashes) and the extra word after the texture count",
    "every section after the texture library, including geometry and the 0x34-byte records",
]


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise Invalid(
            f"{path.name}: {size} bytes exceeds the {MAX_BYTES} byte processing bound"
        )
    return path.read_bytes()


def check_model(data: bytes) -> dict:
    parsed = ps2_container.parse(data)
    tex = parsed["textures"]
    textures, formats = [], collections.Counter()
    variants = []
    for item in tex["items"]:
        formats[str(item["format"])] += 1
        (field,) = struct.unpack_from("<Q", data, item["descriptor_offset"] + 0x38)
        entry = {
            "name": item["name"],
            "format": item["format"],
            "width": item["width"],
            "height": item["height"],
            "mips": item["mips"],
            "palette_index": item["palette_index"],
            "data_offset": item["levels"][0]["offset"],
        }
        try:
            entry["rgba_sha256"] = sha256(ps2_container.decode_rgba(data, item))
        except ps2_container.Unsupported as exc:
            entry["decode"] = f"not decoded: {exc}"
        textures.append(entry)
        variants.append(
            {
                "name": item["name"],
                "format": item["format"],
                "width": item["width"],
                "height": item["height"],
                "mips": item["mips"],
                "packed_upload": bool(field & 256),
                "small_image": min(item["width"], item["height"]) < 16,
                "levels": [
                    {
                        "level": lv["level"],
                        "width": lv["width"],
                        "height": lv["height"],
                        "offset": lv["offset"],
                        "size": lv["size"],
                    }
                    for lv in item["levels"]
                ],
                "level0_decoded": "rgba_sha256" in entry,
            }
        )
    mips = ps2_container.mip_coverage(data)
    palettes = ps2_container.palette_coverage(data)
    failures = [
        *mips["rejected_levels"],
        *[f"palette: {row}" for row in palettes["rejected_references"]],
    ]
    return {
        "texture_count": len(textures),
        "formats": dict(sorted(formats.items())),
        "palette_blocks": list(tex["palette_blocks"]),
        "section_start": tex["section_start"],
        "section_end": tex["section_end"],
        "next_section": parsed["next_section"],
        "textures": textures,
        "variant_coverage": {
            "variants": variants,
            "levels": mips["levels"],
            "source_plane_bytes": mips["source_plane_bytes"],
            "predicted_transfer_bytes": mips["predicted_transfer_bytes"],
            "rejected_levels": mips["rejected_levels"],
            "palette_references": palettes["references"],
            "palette_rejected_references": palettes["rejected_references"],
        },
        "unresolved": UNRESOLVED,
        "failures": failures,
    }


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    expected = baseline.entries(".ps2;1")
    models, failures, formats, textures = [], [], collections.Counter(), 0
    decoded = 0
    levels, source_bytes, transfer_bytes = 0, 0, 0
    variant_rows: dict[tuple, int] = collections.Counter()
    small_images = 0
    for entry in expected:
        name = entry.path.lstrip("/")
        try:
            result = check_model(entry.load())
        except Invalid as exc:
            failures.append(f"{name}: {exc}")
            continue
        formats.update(result["formats"])
        textures += result["texture_count"]
        decoded += sum("rgba_sha256" in t for t in result["textures"])
        coverage = result["variant_coverage"]
        levels += coverage["levels"]
        source_bytes += coverage["source_plane_bytes"]
        transfer_bytes += coverage["predicted_transfer_bytes"]
        failures.extend(f"{name}: {row}" for row in result["failures"])
        for row in coverage["variants"]:
            variant_rows[(row["format"], row["packed_upload"], row["mips"])] += 1
            small_images += row["small_image"]
        models.append(
            {
                "path": name,
                **{
                    k: v
                    for k, v in result.items()
                    if k
                    not in ("textures", "unresolved", "variant_coverage", "failures")
                },
                "textures": result["textures"],
                "variant_coverage": coverage,
            }
        )
    return {
        "provenance": baseline.provenance,
        "models": len(expected),
        "texture_count": textures,
        "formats": dict(sorted(formats.items())),
        "decoded_level0_images": decoded,
        "next_section_records_fit": len(models),
        "variant_coverage": {
            "levels": levels,
            "source_plane_bytes": source_bytes,
            "predicted_transfer_bytes": transfer_bytes,
            "small_images": small_images,
            "variants": [
                {
                    "format": fmt,
                    "packed_upload": packed,
                    "mips": mips,
                    "texture_count": count,
                }
                for (fmt, packed, mips), count in sorted(variant_rows.items())
            ],
        },
        "file_results": models,
        "unresolved": UNRESOLVED,
        "claim_limits": "Texture-library structure, per-level plane/upload coverage and bounded level-zero decoding for formats 1, 3, and 4 under the static model upload contract. No mip-pixel, geometry, renderer execution, or hardware equivalence claim.",
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["file", "corpus"])
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument(
        "--output", type=Path, default=Path(".scratch/evidence/textures")
    )
    args = parser.parse_args()

    def run():
        if len(args.inputs) != 1:
            raise Incomplete(
                f"{args.family} needs 1 input; supplied {len(args.inputs)}"
            )
        if args.family == "corpus":
            return check_corpus(args.inputs[0])
        return check_model(read_bounded(args.inputs[0]))

    return write_result(
        args.output,
        "textures:" + args.family,
        run,
        [] if args.family == "corpus" else args.inputs,
    )


if __name__ == "__main__":
    raise SystemExit(main())
