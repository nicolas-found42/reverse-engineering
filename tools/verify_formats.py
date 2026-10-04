#!/usr/bin/env python3
"""Independent FR2 format check; exits 0=pass, 1=fail, 2=incomplete."""

import argparse
from pathlib import Path
from evidence_common import Incomplete, Invalid, write_result
from corpus_contract import coverage
from format_contracts import archive, bank, model, sprite


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "family", choices=["archive", "bank", "model", "sprite", "corpus"]
    )
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "notes/extracted-manifest.tsv",
    )
    parser.add_argument(
        "--output", type=Path, default=Path(".scratch/evidence/formats")
    )
    args = parser.parse_args()
    expected = 2 if args.family in {"archive", "bank"} else 1

    def run():
        if len(args.inputs) < expected:
            raise Incomplete(
                f"{args.family} needs {expected} inputs; supplied {len(args.inputs)}"
            )
        if len(args.inputs) > expected:
            raise Invalid(f"{args.family} needs exactly {expected} inputs")
        if args.family == "corpus":
            return coverage(args.inputs[0], args.manifest)
        return {"archive": archive, "bank": bank, "model": model, "sprite": sprite}[
            args.family
        ](*(p.read_bytes() for p in args.inputs))

    return write_result(
        args.output,
        "formats:" + args.family,
        run,
        [args.manifest] if args.family == "corpus" else args.inputs,
    )


if __name__ == "__main__":
    raise SystemExit(main())
