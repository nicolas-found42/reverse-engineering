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

from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, write_result
from ptg_profile import MAX_BYTES, HeaderRelationError, classify


def read_bounded(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise Invalid(f"{path.name}: {size} bytes exceeds the {MAX_BYTES} byte processing bound")
    return path.read_bytes()


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    expected = baseline.entries(".ptg;1")
    entries, failures, profiles, violations = [], [], collections.Counter(), 0
    for entry in expected:
        name = entry.path.lstrip("/")
        try:
            result = classify(entry.load())
        except HeaderRelationError as exc:
            violations += 1
            failures.append(f"{name}: {exc}")
            continue
        except Invalid as exc:
            failures.append(f"{name}: {exc}")
            continue
        profiles[result["profile"]] += 1
        entries.append({"path": name, **result})
    return {
        "provenance": baseline.provenance,
        "files": len(expected),
        "profiles": dict(sorted(profiles.items())),
        "header_relation_violations": violations,
        "file_results": entries,
        "claim_limits": "Structure only: no palette, tile-pointer or pixel-color decoding is claimed.",
        "failures": failures,
    }


def check_file(data: bytes) -> dict:
    result = classify(data)
    if result["profile"] == "single_unsupported":
        raise Incomplete(f"single-tile file is outside the supported profiles: {result['diagnostic']}", result)
    return result


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
        return check_file(read_bounded(args.inputs[0]))

    return write_result(args.output, "ptg:" + args.family, run, [] if args.family == "corpus" else args.inputs)


if __name__ == "__main__":
    raise SystemExit(main())
