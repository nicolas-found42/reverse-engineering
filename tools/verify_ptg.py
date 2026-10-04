#!/usr/bin/env python3
"""Independent FR2 PTG structure check; exits 0=pass, 1=fail, 2=incomplete.

Separate from verify_formats.py. Verifies the universal header relations on every .ptg file and the
exact layout of the 0xDDDDDDDD-trailer profile; other multi-tile files are header-level only.
Palette, pointer and descriptor semantics are reported as unresolved, and no full-decoding claim
is made.
"""

import argparse
import collections
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, write_result
from ptg_profile import MAX_BYTES, HeaderRelationError, classify


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise Invalid(f"{path.name}: {size} bytes exceeds the {MAX_BYTES} byte processing bound")
    return path.read_bytes()


def check_corpus(game: Path) -> dict:
    files = game / "extracted" / "files"
    if not files.is_dir():
        raise Incomplete(f"corpus files directory missing: {files}")
    provenance = corpus_identity(game)
    entries, failures, profiles, violations = [], [], collections.Counter(), 0
    for path in sorted(files.rglob("*.ptg;1")):
        name = path.relative_to(files).as_posix()
        try:
            result = classify(read_bounded(path))
        except HeaderRelationError as exc:
            violations += 1
            failures.append(f"{name}: {exc}")
            continue
        except Invalid as exc:
            failures.append(f"{name}: {exc}")
            continue
        profiles[result["profile"]] += 1
        entries.append({"path": name, **result})
    if not entries and not failures:
        raise Incomplete("no .ptg files found in the corpus")
    return {
        "provenance": provenance,
        "files": len(entries) + len(failures),
        "profiles": dict(sorted(profiles.items())),
        "header_relation_violations": violations,
        "file_results": entries,
        "claim_limits": "Structure only: no palette, tile-pointer or pixel-color decoding is claimed.",
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["file", "corpus"])
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/ptg"))
    args = parser.parse_args()

    def run():
        if len(args.inputs) != 1:
            raise Incomplete(f"{args.family} needs 1 input; supplied {len(args.inputs)}")
        if args.family == "corpus":
            return check_corpus(args.inputs[0])
        return classify(read_bounded(args.inputs[0]))

    return write_result(args.output, "ptg:" + args.family, run, [] if args.family == "corpus" else args.inputs)


if __name__ == "__main__":
    raise SystemExit(main())
