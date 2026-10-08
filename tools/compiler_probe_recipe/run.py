#!/usr/bin/env python3
"""Run the exploratory compiler probe as a standard immutable evidence check."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from compiler_probe import run_probe  # noqa: E402
from evidence_common import Incomplete, write_result  # noqa: E402
from compiler_probe_recipe.build import prepare  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="corpus game directory")
    parser.add_argument("tool_root", type=Path, help="installed candidate tools and Docker wrappers")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-probe"))
    args = parser.parse_args()
    executable = args.game / "extracted/SLES_517.05"
    recipe = Path(__file__).parent

    def action() -> dict:
        # The Docker and Wine wrappers mount only TOOL_ROOT. Keep source,
        # reference, object, and linked files below that mount.
        with tempfile.TemporaryDirectory(prefix="compiler-probe-recipe-", dir=args.tool_root) as temp:
            staging = Path(temp)
            manifest, _ = prepare(args.game, args.tool_root, staging)
            result = run_probe(manifest, staging / "candidate-work")
        result["ac05_status"] = "incomplete"
        result["ac05_reason"] = (
            "The source, ABI, range ownership, linker substitutions, and profile are exploratory; "
            "a unique byte match does not identify the original compiler."
        )
        result["claim_limits"] = result.get("claim_limits", []) + [
            "This child check is diagnostic evidence only and cannot complete AC05."
        ]
        result["probe_status"] = result.pop("status")
        result["nonmatching_candidates"] = result.pop("failures", [])
        if result.get("errors") or result.get("incomplete"):
            raise Incomplete("compiler probe prerequisites or candidate executions are incomplete", result)
        return result

    return write_result(args.output, "compiler-probe-exploratory", action,
                        [executable, recipe / "candidate.c", recipe / "candidate.ld",
                         recipe / "manifest.template.json"])


if __name__ == "__main__":
    raise SystemExit(main())
