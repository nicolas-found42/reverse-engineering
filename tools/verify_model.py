#!/usr/bin/env python3
"""Independent FR2 model-boundary check; exits 0=pass, 1=fail, 2=incomplete.

Separate from verify_formats.py. On top of the milestone name-tree contract it verifies that the
leading u32 equals the end offset of the name pool, that the bytes up to the next 16-byte boundary
are zero, and that the size is a multiple of 16. Geometry and the later header remain unresolved.
"""

import argparse
import collections
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, sha256, write_result
from format_contracts import model

MAX_BYTES = 128 * 1024 * 1024
UNRESOLVED = [
    "geometry: not decoded; the region after the pad holds data this check only hashes",
    "later header: the words at the aligned geometry start are not a stable structure across files",
]


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise Invalid(f"{path.name}: {size} bytes exceeds the {MAX_BYTES} byte processing bound")
    return path.read_bytes()


def check_model(data: bytes) -> dict:
    tree = model(data)
    pool_end = max(name["end"] for name in tree["names"])
    leading = tree["leading_count"]
    if leading != pool_end:
        raise Invalid(f"leading u32 {leading} differs from name pool end {pool_end}")
    if len(data) % 16:
        raise Invalid(f"size {len(data)} is not a multiple of 16")
    start = -(-pool_end // 16) * 16
    if any(data[pool_end:start]):
        raise Invalid(f"padding between the name pool end {pool_end} and {start} is not zero")
    return {
        "name_pool_end": pool_end,
        "geometry_region_start": start,
        "pad_length": start - pool_end,
        "geometry_bytes": len(data) - start,
        "geometry_sha256": sha256(data[start:]),
        "names": len(tree["names"]),
        "groups": len(tree["groups"]),
        "unresolved": UNRESOLVED,
    }


def check_corpus(game: Path) -> dict:
    files = game / "extracted" / "files"
    if not files.is_dir():
        raise Incomplete(f"corpus files directory missing: {files}")
    provenance = corpus_identity(game)
    paths = [p for p in sorted(files.rglob("*")) if p.is_file() and p.name.lower().endswith(".ps2;1")]
    if not paths:
        raise Incomplete("no .ps2 models found in the corpus")
    entries, failures, pads = [], [], collections.Counter()
    for path in paths:
        name = path.relative_to(files).as_posix()
        try:
            result = check_model(read_bounded(path))
        except Invalid as exc:
            failures.append(f"{name}: {exc}")
            continue
        pads[result["pad_length"]] += 1
        entries.append({"path": name, **result})
    return {
        "provenance": provenance,
        "models": len(paths),
        "leading_equals_pool_end": len(entries),
        "zero_padding": len(entries),
        "pad_lengths": dict(sorted(pads.items())),
        "file_results": entries,
        "claim_limits": "Name-pool boundary only: no geometry or mesh decoding is claimed.",
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["file", "corpus"])
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/model"))
    args = parser.parse_args()

    def run():
        if len(args.inputs) != 1:
            raise Incomplete(f"{args.family} needs 1 input; supplied {len(args.inputs)}")
        if args.family == "corpus":
            return check_corpus(args.inputs[0])
        return check_model(read_bounded(args.inputs[0]))

    return write_result(args.output, "model:" + args.family, run, [] if args.family == "corpus" else args.inputs)


if __name__ == "__main__":
    raise SystemExit(main())
