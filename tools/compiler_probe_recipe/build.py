#!/usr/bin/env python3
"""Prepare a compiler-probe manifest from the pinned corpus and installed tools.

The retail comparison bytes are extracted at runtime and never stored in this
repository. Candidate C is a hand-written exploratory reconstruction, not
source exported from a decompiler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

TOOLS = Path(__file__).resolve().parents[1]
RECONSTRUCTION_SOURCE = TOOLS.parent / "reconstruction/ee/app3d/misc3d_db_id.c"
sys.path.insert(0, str(TOOLS))
from corpus_contract import corpus_identity  # noqa: E402
from matching_sections import sections  # noqa: E402

FUNCTION_VADDR = 0x001D1800
FUNCTION_SIZE = 60
FUNCTION_SHA256 = "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e"
RELEASE_URL = "https://github.com/decompme/compilers/releases/download/compilers/"
DISTRIBUTIONS = {
    "ee-gcc2.9-991111-01": ("ee-gcc2.9-991111-01.tar.xz", "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8"),
    "ee-gcc2.95.2-273a": ("ee-gcc2.95.2-273a.tar.gz", "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e"),
    "ee-gcc2.95.3-114": ("ee-gcc2.95.3-114.tar.gz", "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb"),
    "ee-gcc2.95.3-136": ("ee-gcc2.95.3-136.tar.gz", "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f"),
    "ee-gcc2.96": ("ee-gcc2.96.tar.xz", "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a"),
    "ee-gcc3.2-030926": ("ee-gcc3.2-030926.tar.gz", "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9"),
    "ee-gcc3.2-040921": ("ee-gcc3.2-040921.tar.xz", "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f"),
}


def prepare(game: Path, tool_root: Path, output: Path) -> tuple[Path, Path]:
    identity = corpus_identity(game)
    executable = game / "extracted/SLES_517.05"
    text = sections(executable.read_bytes())[".text"]
    offset = FUNCTION_VADDR - text.address
    if offset < 0 or offset + FUNCTION_SIZE > len(text.data):
        raise ValueError("probe function range is outside the pinned .text section")
    reference = text.data[offset:offset + FUNCTION_SIZE]
    if hashlib.sha256(reference).hexdigest() != FUNCTION_SHA256:
        raise ValueError("probe function bytes do not match the pinned range identity")

    output.mkdir(parents=True, exist_ok=True)
    reference_path = output / "reference.bin"
    reference_path.write_bytes(reference)
    recipe_root = Path(__file__).parent.resolve()
    shutil.copyfile(RECONSTRUCTION_SOURCE, output / "candidate.c")
    for name in ("candidate.ld", "docker-linux-exec.sh", "docker-wine-exec.sh"):
        shutil.copyfile(recipe_root / name, output / name)
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
    distributions = []
    for candidate_id, (archive_name, expected_sha256) in DISTRIBUTIONS.items():
        archive_path = tool_root / archive_name
        actual_sha256 = hashlib.sha256(archive_path.read_bytes()).hexdigest() if archive_path.is_file() else None
        if actual_sha256 is not None and actual_sha256 != expected_sha256:
            raise ValueError(f"candidate distribution archive hash differs: {archive_name}")
        distributions.append({"candidate": candidate_id, "archive": archive_name,
                              "source": RELEASE_URL + archive_name,
                              "expected_sha256": expected_sha256,
                              "available_locally": actual_sha256 is not None,
                              "observed_sha256": actual_sha256})
    manifest["evidence"] = {
        "corpus": identity,
        "reference_range": {"section": ".text", "vaddr": f"{FUNCTION_VADDR:08x}",
                            "file_offset": f"{text.offset + offset:08x}",
                            "bytes": FUNCTION_SIZE, "sha256": FUNCTION_SHA256,
                            "scope": "game_owned",
                            "decision": "ADR-0005 local split, cross-checked against source map, callers, and helper provenance"},
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers release tag compilers; per-candidate archive URLs and SHA-256 values follow.",
        "tool_distributions": distributions,
        "license_status": "The release archives inspected do not include COPYING or LICENSE entries. Per-package redistribution terms are unresolved; no compiler binaries are redistributed here.",
        "runtime_profile": "Immutable image IDs are verified before invocation: Debian Bookworm linux/amd64 with Wine 8 for Windows compiler drivers, and GNU binutils 2.40 in the Debian image for object preparation, linking, and objcopy.",
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
