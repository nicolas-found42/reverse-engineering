#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check four source-pinned integer division emitters using synthetic registers."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
COMMIT = "c5a9d02573410a2085a4b4b831b0b68ba3515440"
HEADER = "ps2xRuntime/include/ps2_runtime_macros.h"
SPECIAL = "ps2xRecomp/src/lib/special_translator.cpp"
MMI = "ps2xRecomp/src/lib/mmi_translator.cpp"
SOURCE_HASHES = {
    HEADER: "c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e",
    SPECIAL: "98adc0305effdd57ca34ea029070f117379bd7e78c9f8944a8e9276c8c7bd3cd",
    MMI: "24deb4f0bc0004c42674e0340d80e50e6e676b326f11d6a2df3dd0b60319249f",
}
DEPENDENCY_HASH = "78632498a57bf7e080e84cb8d74c47ce93b204cece77eab79de2908eb8bc92ed"
OPERATIONS = ("DIV", "DIVU", "DIV1", "DIVU1")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pinned_sources(root: Path) -> dict[str, str]:
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("source checkout is unavailable") from exc
    if head != COMMIT:
        raise ValueError("source commit differs from pinned revision")
    sources = {}
    for name, expected in SOURCE_HASHES.items():
        raw = (root / name).read_bytes()
        if digest(raw) != expected:
            raise ValueError(f"source SHA-256 differs: {name}")
        sources[name] = raw.decode()
    return sources


def extract_case(source: str, marker: str, arguments: list[str]) -> str:
    start = source.find(f"case {marker}:")
    if start < 0:
        raise ValueError(f"division case absent: {marker}")
    end = source.find("case ", start + len(f"case {marker}:"))
    body = source[start:end if end >= 0 else len(source)]
    # All four pinned cases have exactly one literal fmt::format return.
    match = re.search(r'return fmt::format\(\s*((?:"(?:\\.|[^"\\])*"\s*)+),', body)
    if not match:
        raise ValueError(f"division format template absent: {marker}")
    literals = re.findall(r'"(?:\\.|[^"\\])*"', match[1])
    if not literals:
        raise ValueError(f"division literal template absent: {marker}")
    return "".join(ast.literal_eval(x) for x in literals).format(*arguments)


def extracted_header(sources: dict[str, str]) -> tuple[str, dict[str, str]]:
    header = sources[HEADER]
    start = header.find("static inline int32_t Ps2ExtractEpi32(")
    end = header.find("static inline int64_t Ps2ExtractEpi64(", start)
    if start < 0 or end < 0:
        raise ValueError("pinned low-word register extractor absent")
    macros = []
    for name in ("PS2_EXTRACT_EPI32_0", "GPR_U32", "GPR_S32"):
        line = next((s for s in header.splitlines()
                     if s.startswith(f"#define {name}(")), None)
        if line is None:
            raise ValueError(f"register macro absent: {name}")
        macros.append(line)
    templates = {
        "DIV": extract_case(sources[SPECIAL], "SPECIAL_DIV", ["rt", "rs"]),
        "DIVU": extract_case(sources[SPECIAL], "SPECIAL_DIVU", ["rt", "rs", "rs", "rs"]),
        "DIV1": extract_case(sources[MMI], "MMI_DIV1", ["rt", "rs"]),
        "DIVU1": extract_case(sources[MMI], "MMI_DIVU1", ["rt", "rs", "rs", "rs"]),
    }
    wrappers = [f"void generated_{name}(Context* ctx,int rs,int rt){{{body}}}"
                for name, body in templates.items()]
    result = ("// Source-pinned production expressions and register read macros.\n"
              '#include <cstdint>\n#include "sse2neon.h"\n'
              "struct Context { __m128i r[32]; uint64_t hi,lo,hi1,lo1; };\n"
              + header[start:end] + "\n".join(macros + wrappers) + "\n")
    return result, templates


def verify(root: Path, output: Path, dependency: Path, *, compiler: str = "clang++") -> dict:
    if output.exists():
        raise ValueError("output directory must be fresh")
    sources = pinned_sources(root)
    raw_dependency = (dependency / "sse2neon.h").read_bytes()
    if digest(raw_dependency) != DEPENDENCY_HASH:
        raise ValueError("sse2neon SHA-256 differs from pinned dependency")
    header, templates = extracted_header(sources)
    output.mkdir(parents=True)
    generated = output / "division_templates.h"
    generated.write_text(header)
    probe = HERE / "integer_division_probe.cpp"
    executable = output / "division-probe"
    argv = [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=undefined", "-fno-sanitize-recover=all",
            "-I", str(output.resolve()), "-isystem", str(dependency.resolve()),
            str(probe.resolve()), "-o", str(executable.resolve())]
    compiled = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    (output / "compile.json").write_text(json.dumps({"argv": argv,
        "returncode": compiled.returncode, "stdout": compiled.stdout,
        "stderr": compiled.stderr}, indent=2) + "\n")
    if compiled.returncode:
        raise ValueError("division probe compilation failed; inspect compile.json")
    run = subprocess.run([str(executable.resolve())], capture_output=True,
                         text=True, timeout=60)
    (output / "run.json").write_text(json.dumps({"returncode": run.returncode,
        "stdout": run.stdout, "stderr": run.stderr}, indent=2) + "\n")
    if run.returncode or run.stderr:
        raise ValueError("division probe failure or sanitizer diagnostic; inspect run.json")
    details = json.loads(run.stdout)
    if (details.get("names") != list(OPERATIONS)
            or details.get("checks") != [600600] * 4
            or details.get("mismatches") != [0] * 4):
        raise ValueError("division comparison matrix failed")
    # Compile an independently corrupted emitted quotient for each operation.
    # This proves the comparison reports mismatches instead of merely running.
    mutant = output / "mutant"
    mutant.mkdir()
    wrong_header = header
    for name, body in templates.items():
        bank = "lo" if name in ("DIV", "DIVU") else "lo1"
        original = f"void generated_{name}(Context* ctx,int rs,int rt){{{body}}}"
        wrong = f"void generated_{name}(Context* ctx,int rs,int rt){{{body}ctx->{bank} ^= 1ull;}}"
        if wrong_header.count(original) != 1:
            raise ValueError("negative-control wrapper is not unique")
        wrong_header = wrong_header.replace(original, wrong)
    (mutant / "division_templates.h").write_text(wrong_header)
    mutant_argv = list(argv)
    mutant_argv[mutant_argv.index("-I") + 1] = str(mutant.resolve())
    mutant_argv[-1] = str((mutant / "division-probe").resolve())
    mutant_compile = subprocess.run(mutant_argv, capture_output=True, text=True, timeout=60)
    if mutant_compile.returncode:
        raise ValueError("negative-control compilation failed")
    mutant_run = subprocess.run([mutant_argv[-1]], capture_output=True, text=True, timeout=60)
    mutant_details = json.loads(mutant_run.stdout)
    (mutant / "result.json").write_text(json.dumps({"compiler_argv": mutant_argv,
        "compile_stderr": mutant_compile.stderr, "returncode": mutant_run.returncode,
        "stderr": mutant_run.stderr, "details": mutant_details}, indent=2) + "\n")
    if (mutant_run.returncode != 1 or mutant_run.stderr
            or mutant_details.get("mismatches") != [600600] * 4):
        raise ValueError("corrupted-quotient negative control was not detected")
    result = {"schema_version": 1, "status": "pass", "source_commit": COMMIT,
        "source_hashes": SOURCE_HASHES, "dependency_sha256": DEPENDENCY_HASH,
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "probe_sha256": digest(probe.read_bytes()), "extracted_sha256": digest(generated.read_bytes()),
        "templates": templates, "details": details, "compiler_argv": argv,
        "negative_control": mutant_details,
        "claim_limit": "Synthetic arithmetic, sign extension, zero-register reads, source aliasing and untouched-bank/register checks only. Divide-by-zero follows the pinned software policy; Sony documents its arithmetic result as undefined. No timing, decoder, game execution or hardware equivalence is proved."}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--fresh-output-dir", type=Path, required=True)
    parser.add_argument("--sse2neon", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.upstream, args.fresh_output_dir, args.sse2neon)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
