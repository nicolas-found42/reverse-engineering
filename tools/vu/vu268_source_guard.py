#!/usr/bin/env python3
"""Guard VU0 entry 0x268's source identity, pair span, and raw LOI payloads.

This verifies exact static source bytes only. It does not establish VU runtime
semantics, instruction scheduling, or hardware equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
for import_path in (REPO_ROOT, TOOLS_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))
from tools.ps2_vu import parse_overlays  # noqa: E402
from tools.vu.vu268_reference import LOI_BITS  # noqa: E402

DEFAULT_EXECUTABLE = REPO_ROOT / "games/ford-racing-2/extracted/SLES_517.05"


@dataclass(frozen=True)
class GuardContract:
    executable_sha256: str
    overlay_index: int
    overlay_name: str
    overlay_load_address: int
    overlay_vma: int
    overlay_source_section: str
    overlay_source_offset: int
    overlay_bytes: int
    overlay_pairs: int
    overlay_sha256: str
    span_start_pair: int
    span_end_pair_exclusive: int
    span_bytes: int
    span_sha256: str
    loi_words: tuple[tuple[int, str, int], ...]


PINNED_CONTRACT = GuardContract(
    executable_sha256="216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95",
    overlay_index=7,
    overlay_name=".DVP.overlay..0x0.495278677.35.0",
    overlay_load_address=2206960,
    overlay_vma=0,
    overlay_source_section=".vutext",
    overlay_source_offset=1162480,
    overlay_bytes=1120,
    overlay_pairs=140,
    overlay_sha256="2093b6946baea64312037ec6a6dce16a7451b7729f4cf7e88042ac90895422e1",
    span_start_pair=77,
    span_end_pair_exclusive=102,
    span_bytes=200,
    span_sha256="24fbedaf59f41ea50e1f3507e7ca7a2ad15642e22c7a05b3cd955576c4b83611",
    loi_words=(
        (78, "pi_over_2", 0x3FC90FDB),
        (80, "minus_inv_tau", 0xBE22F983),
        (82, "magic_12582912", 0x4B400000),
        (84, "minus_inv_tau_again", 0xBE22F983),
        (85, "half", 0x3F000000),
        (87, "quarter", 0x3E800000),
        (89, "coefficient_minus_76_5749588", 0xC2992661),
        (90, "coefficient_minus_41_3416748", 0xC2255DE0),
        (91, "coefficient_81_6022263", 0x42A33457),
        (95, "coefficient_39_710659", 0x421ED7B7),
        (99, "coefficient_6_28318501", 0x40C90FDA),
    ),
)


class SourceGuardError(ValueError):
    """Raised when the executable or guarded source span differs from contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceGuardError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expected_model_bits(contract: GuardContract) -> dict[str, int]:
    return {name: bits for _, name, bits in contract.loi_words if name != "minus_inv_tau_again"}


def verify_source_bytes(
    data: bytes,
    inventory: Mapping,
    *,
    model_bits: Mapping[str, int] = LOI_BITS,
    contract: GuardContract = PINNED_CONTRACT,
) -> dict:
    """Check parse_overlays output and exact source bytes against a pinned contract.

    This separate byte/inventory seam is testable with synthetic fixtures. The
    public `verify_executable` entrypoint always obtains inventory by calling
    parse_overlays on the selected executable bytes.
    """
    actual_exe_sha = _sha256(data)
    _require(actual_exe_sha == contract.executable_sha256, "executable SHA-256 differs from pinned identity")
    _require(inventory.get("executable_sha256") == actual_exe_sha,
             "parse_overlays executable identity differs from the input bytes")
    rows = [row for row in inventory.get("overlays", []) if row.get("index") == contract.overlay_index]
    _require(len(rows) == 1, "pinned overlay index is missing or ambiguous")
    overlay = rows[0]
    for field, expected in (
        ("name", contract.overlay_name), ("load_address", contract.overlay_load_address),
        ("vu_byte_address", contract.overlay_vma), ("source_section", contract.overlay_source_section),
        ("source_offset", contract.overlay_source_offset), ("bytes", contract.overlay_bytes),
        ("instruction_pairs", contract.overlay_pairs), ("sha256", contract.overlay_sha256),
    ):
        _require(overlay.get(field) == expected, f"overlay {field} differs from pinned mapping")
    source_start = overlay["source_offset"]
    source_end = source_start + overlay["bytes"]
    _require(0 <= source_start <= source_end <= len(data), "overlay source span is outside executable bytes")
    overlay_bytes = data[source_start:source_end]
    _require(_sha256(overlay_bytes) == contract.overlay_sha256,
             "overlay source bytes differ from pinned overlay digest")

    span_start = source_start + contract.span_start_pair * 8
    span_end = source_start + contract.span_end_pair_exclusive * 8
    _require(contract.span_end_pair_exclusive - contract.span_start_pair == 25,
             "pinned instruction span must contain 25 pairs")
    _require(span_end - span_start == contract.span_bytes, "pinned instruction span byte length mismatch")
    span = data[span_start:span_end]
    _require(len(span) == contract.span_bytes, "pinned instruction span is truncated")
    span_sha = _sha256(span)
    _require(span_sha == contract.span_sha256, "pair 77..101 source bytes differ from pinned digest")

    loads = []
    for pair, name, expected_bits in contract.loi_words:
        offset = source_start + pair * 8
        lower, upper = struct.unpack_from("<II", data, offset)
        _require(bool(upper & 0x80000000), f"pair {pair} is missing the LOI upper-word flag")
        _require(lower == expected_bits, f"pair {pair} LOI lower-word bits differ from pinned value")
        value = struct.unpack("<f", struct.pack("<I", lower))[0]
        loads.append({"pair": pair, "file_offset": offset, "name": name,
                      "lower_word_hex": f"{lower:08x}", "value_f32": value,
                      "upper_word_hex": f"{upper:08x}", "I_flag": True})

    _require(dict(model_bits) == _expected_model_bits(contract),
             "model LOI bit table differs from raw source pair words")
    return {
        "status": "pass",
        "model_LOI_table_matches_source_bits": True,
        "exe_sha256": actual_exe_sha,
        "overlay_index": contract.overlay_index,
        "overlay_name": overlay["name"],
        "overlay_vma": overlay["vu_byte_address"],
        "overlay_load_address": overlay["load_address"],
        "overlay_bytes": overlay["bytes"],
        "overlay_pairs": overlay["instruction_pairs"],
        "source_section": overlay["source_section"],
        "source_offset": source_start,
        "overlay_sha256": contract.overlay_sha256,
        "instruction_span_start_pair": contract.span_start_pair,
        "instruction_span_end_pair_exclusive": contract.span_end_pair_exclusive,
        "instruction_span_source_offset": span_start,
        "instruction_span_bytes": len(span),
        "instruction_span_sha256": span_sha,
        "loads": loads,
        "claim_limit": "Identity, overlay source mapping, span bytes and LOI payload bits only; instruction semantics are a separate interpretation.",
    }


def verify_executable(path: Path = DEFAULT_EXECUTABLE) -> dict:
    """Read an executable and check its overlay/source bytes; creates no files."""
    data = path.read_bytes()
    inventory = parse_overlays(data)
    return {"executable_path": str(path), **verify_source_bytes(data, inventory)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, default=DEFAULT_EXECUTABLE,
                        help="private game ELF to validate (defaults to the local extracted PAL executable)")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify_executable(args.executable), indent=2))
    except (OSError, SourceGuardError, ValueError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
