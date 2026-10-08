#!/usr/bin/env python3
"""Run the exploratory compiler probe as a standard immutable evidence check."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile

TOOLS = Path(__file__).resolve().parents[1]
ADR0005 = TOOLS.parent / "docs/adr/0005-game-owned-sdk-boundary.md"
sys.path.insert(0, str(TOOLS))
from compiler_probe import run_probe  # noqa: E402
from evidence_common import Incomplete, Invalid, write_result  # noqa: E402
from matching_diff import scope_of_range  # noqa: E402
from matching_ranges import (BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY, SOURCE_MAP,
                             boundary_provenance)  # noqa: E402
from compiler_probe_recipe import build  # noqa: E402
from compiler_probe_recipe.build import prepare  # noqa: E402

LINUX_IMAGE_ID = "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca"
WINE_IMAGE_ID = "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba"


def apply_recorded_range(result: dict, reference_range: dict) -> None:
    """Apply repository-owned attribution to the pinned recipe's byte verdicts."""
    section = reference_range["section"]
    address = int(reference_range["vaddr"], 16)
    file_offset = int(reference_range["file_offset"], 16)
    size = int(reference_range["bytes"])
    scope = scope_of_range(section, address, size)
    provenance = boundary_provenance()
    if reference_range.get("scope") != scope.value:
        raise Incomplete("compiler recipe scope differs from the recorded range map", {
            "declared_scope": reference_range.get("scope"), "recorded_scope": scope.value})
    for candidate in result.get("candidates", []):
        gate = candidate.get("gate")
        if gate is None:
            continue
        gate.update(section=section, scope=scope.value, section_bytes=size)
        difference = gate.get("first_difference")
        if difference is not None:
            difference["address"] = f"{address + difference['offset']:08x}"
            difference["file_offset"] = f"{file_offset + difference['offset']:08x}"
    passed = (result.get("status") == "pass" and scope.value == "game_owned"
              and provenance is not None
              and len(result.get("matches", [])) == 1
              and any(candidate.get("status") == "pass"
                      and candidate.get("gate", {}).get("scope") == "game_owned"
                      for candidate in result.get("candidates", [])))
    result["ac07_status"] = "pass" if passed else (
        "fail" if result.get("status") == "fail" and scope.value == "game_owned" else "incomplete")
    result["ac07_evidence"] = {
        "range": {"section": section, "vaddr": f"{address:08x}",
                  "file_offset": f"{file_offset:08x}", "bytes": size,
                  "sha256": reference_range["sha256"], "scope": scope.value},
        "byte_match": "pass" if passed else result.get("status", "incomplete"),
        "source_built": True,
        "source_sha256": hashlib.sha256(build.RECONSTRUCTION_SOURCE.read_bytes()).hexdigest(),
        "decision_sha256": hashlib.sha256(ADR0005.read_bytes()).hexdigest(),
        "evidence_inputs": provenance,
        "compiler_identification": "separate; see ac05_status",
    }


def validate_runtime_images() -> dict[str, dict[str, str]]:
    """Require the declared immutable image IDs and record Docker's observed identity."""
    observed = {}
    for profile, expected_id in (("linux-tools", LINUX_IMAGE_ID), ("wine-compiler", WINE_IMAGE_ID)):
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", expected_id, "--format", "{{.Id}}|{{.Os}}/{{.Architecture}}"],
                capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Incomplete(f"cannot inspect pinned {profile} image: {type(exc).__name__}") from exc
        if result.returncode:
            raise Incomplete(f"pinned {profile} image is unavailable", {
                "expected_image_id": expected_id, "stderr": result.stderr[-1000:]})
        actual_id, separator, platform = result.stdout.strip().partition("|")
        if not separator or actual_id != expected_id or platform != "linux/amd64":
            raise Incomplete(f"pinned {profile} image identity or platform differs", {
                "expected_image_id": expected_id, "observed": result.stdout.strip(),
                "required_platform": "linux/amd64"})
        observed[profile] = {"image_id": actual_id, "platform": platform}
    return observed


def validate_manifest_runtimes(manifest_path: Path, tool_root: Path) -> None:
    """Bind every compiler and binutils phase to this recipe's pinned wrappers."""
    manifest = json.loads(manifest_path.read_text())
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 7:
        raise Incomplete("compiler recipe candidate set differs from the pinned seven-candidate profile")
    for candidate in candidates:
        candidate_id = candidate.get("id", "")
        is_wine = candidate_id.startswith("ee-gcc2.95")
        expected_image = WINE_IMAGE_ID if is_wine else LINUX_IMAGE_ID
        if candidate.get("runtime", {}).get("image_id") != expected_image:
            raise Incomplete(f"candidate {candidate_id} declares a different runtime image", {
                "expected_image_id": expected_image,
                "declared_image_id": candidate.get("runtime", {}).get("image_id")})
        for phase in ("compile", "objcopy", "prepare_object", "link"):
            command = candidate.get(phase, [])
            wine_phase = is_wine and phase == "compile"
            wrapper = "docker-wine-exec.sh" if wine_phase else "docker-linux-exec.sh"
            expected_prefix = ["/bin/bash", str((manifest_path.parent / wrapper).resolve()),
                               str(tool_root.resolve())]
            if command[:3] != expected_prefix:
                raise Incomplete(f"candidate {candidate_id} {phase} is not bound to its pinned wrapper", {
                    "expected_prefix": expected_prefix, "declared_prefix": command[:3]})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="corpus game directory")
    parser.add_argument("tool_root", type=Path, help="installed candidate tools and Docker wrappers")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-probe"))
    args = parser.parse_args(argv)
    executable = args.game / "extracted/SLES_517.05"
    recipe = Path(__file__).parent

    def action() -> dict:
        # The Docker and Wine wrappers mount only TOOL_ROOT. Keep source,
        # reference, object, and linked files below that mount. Resolve aliases
        # before creating any paths so Docker receives the host-visible mount
        # path rather than a lexical symlink path.
        tool_root = args.tool_root.resolve(strict=True)
        with tempfile.TemporaryDirectory(prefix="compiler-probe-recipe-", dir=tool_root) as temp:
            staging = Path(temp).resolve()
            manifest, _ = prepare(args.game, tool_root, staging)
            validate_manifest_runtimes(manifest, tool_root)
            reference_range = json.loads(manifest.read_text())["evidence"]["reference_range"]
            runtime_identity = validate_runtime_images()
            result = run_probe(manifest, (staging / "candidate-work").resolve())
        apply_recorded_range(result, reference_range)
        result["runtime_identity"] = runtime_identity
        result["runtime_phases"] = {
            "native_compiler_candidates": "linux-tools",
            "windows_compiler_candidates": "wine-compiler",
            "prepare_object_link_objcopy": "linux-tools",
        }
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
        if result["probe_status"] == "incomplete" or result.get("errors") or result.get("incomplete"):
            raise Incomplete("compiler probe prerequisites or candidate executions are incomplete", result)
        if result["probe_status"] == "fail":
            raise Invalid("no compiler candidate matched the exploratory reference range", result)
        if result["probe_status"] != "pass":
            raise Invalid(f"compiler probe returned an unknown status: {result['probe_status']}", result)
        return result

    return write_result(args.output, "compiler-probe-exploratory", action,
                        [executable, Path(__file__), recipe / "build.py",
                         TOOLS / "compiler_probe.py", TOOLS / "matching_diff.py",
                         TOOLS / "matching_sections.py", TOOLS / "corpus_contract.py",
                         TOOLS / "ps2_executables.py", TOOLS / "evidence_common.py", ADR0005,
                         SOURCE_MAP, *(p for p in (BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY)
                                       if p.is_file()),
                         build.RECONSTRUCTION_SOURCE,
                         recipe / "candidate.ld", recipe / "manifest.template.json",
                         recipe / "docker-linux-exec.sh", recipe / "docker-wine-exec.sh"])


if __name__ == "__main__":
    raise SystemExit(main())
