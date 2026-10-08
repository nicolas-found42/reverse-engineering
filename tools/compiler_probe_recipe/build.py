#!/usr/bin/env python3
"""Prepare a compiler-probe manifest from the pinned corpus and installed tools.

The retail comparison bytes are extracted at runtime and never stored in this
repository. Candidate C is a hand-written exploratory reconstruction, not
source exported from a decompiler.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from corpus_contract import corpus_identity  # noqa: E402
from matching_sections import sections  # noqa: E402

FUNCTION_VADDR = 0x001D1800
FUNCTION_SIZE = 60
FUNCTION_SHA256 = "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e"


def prepare(game: Path, tool_root: Path, output: Path) -> tuple[Path, Path]:
    identity = corpus_identity(game)
    executable = game / "extracted/SLES_517.05"
    text = sections(executable.read_bytes())[".text"]
    offset = FUNCTION_VADDR - text.address
    if offset < 0 or offset + FUNCTION_SIZE > len(text.data):
        raise ValueError("probe function range is outside the pinned .text section")
    reference = text.data[offset:offset + FUNCTION_SIZE]
    import hashlib
    if hashlib.sha256(reference).hexdigest() != FUNCTION_SHA256:
        raise ValueError("probe function bytes do not match the pinned range identity")

    output.mkdir(parents=True, exist_ok=True)
    reference_path = output / "reference.bin"
    reference_path.write_bytes(reference)
    recipe_root = Path(__file__).parent.resolve()
    shutil.copyfile(recipe_root / "candidate.c", output / "candidate.c")
    shutil.copyfile(recipe_root / "candidate.ld", output / "candidate.ld")
    template_path = Path(__file__).with_name("manifest.template.json")
    manifest = json.loads(template_path.read_text())
    values = {"{tool_root}": str(tool_root.resolve()),
              "{recipe_root}": str(output.resolve()),
              "{reference_path}": str(reference_path.resolve())}

    def replace(value):
        if isinstance(value, str):
            for marker, replacement in values.items():
                value = value.replace(marker, replacement)
            return value
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        return value

    manifest = replace(manifest)
    # The template's source path and linker script are kept in this repository.
    manifest["evidence"] = {
        "corpus": identity,
        "reference_range": {"section": ".text", "vaddr": f"{FUNCTION_VADDR:08x}",
                            "bytes": FUNCTION_SIZE, "sha256": FUNCTION_SHA256,
                            "interpretation": "source-map attribution only; not proof of authorship or ownership"},
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers public GNU EE platform package and official release assets; see recipe README.",
        "runtime_profile": "Debian Bookworm linux/amd64 with Wine 8 for Windows drivers and GNU binutils 2.40.",
        "linker_profile": "GNU binutils 2.40 substitution; not the original proprietary linker.",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest_path, reference_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="corpus game directory containing extracted/SLES_517.05")
    parser.add_argument("tool_root", type=Path, help="installed compiler candidates and Docker wrappers")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-probe-recipe"))
    args = parser.parse_args()
    manifest, _ = prepare(args.game, args.tool_root, args.output)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
