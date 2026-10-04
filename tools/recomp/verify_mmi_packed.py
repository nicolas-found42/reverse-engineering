#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check 13 pinned PS2Recomp packed-register templates on synthetic vectors.

This compiles only extracted translation expressions with the pinned runtime
macros. It does not execute game code or emulate instruction timing.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
HEADER_PATH = "ps2xRuntime/include/ps2_runtime_macros.h"
MMI_PATH = "ps2xRecomp/src/lib/mmi_translation_helpers.cpp"
SOURCE_COMMIT = "c5a9d02573410a2085a4b4b831b0b68ba3515440"
SOURCE_HASHES = {
    HEADER_PATH: "c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e",
    MMI_PATH: "1402bdb9f81923a8c91c7fa790399a2563ebc5f7cd0c899b7c29cb7c6bafc5ee",
}
SSE2NEON_HASH = "78632498a57bf7e080e84cb8d74c47ce93b204cece77eab79de2908eb8bc92ed"
OPERATIONS = ("PCPYLD", "PCPYUD", "PCPYH", "PEXTLW", "PEXTUW", "PEXTLH",
              "PEXTLB", "PAND", "POR", "PNOR", "PXOR", "PSUBB", "PSUBW")
MACRO_NAMES = ("PS2_PEXTLW", "PS2_PEXTUW", "PS2_PEXTLH", "PS2_PEXTLB",
               "PS2_PSUBB", "PS2_PSUBW", "PS2_PAND", "PS2_POR", "PS2_PNOR",
               "PS2_PXOR", "PS2_PCPYLD")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_sources(upstream: Path) -> dict[str, str]:
    try:
        actual_commit = subprocess.run(["git", "-C", str(upstream), "rev-parse", "HEAD"],
                                       check=True, capture_output=True, text=True).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("upstream is not a readable Git checkout") from exc
    if actual_commit != SOURCE_COMMIT:
        raise ValueError(f"pinned upstream commit mismatch: {actual_commit}")
    sources = {}
    for name, expected in SOURCE_HASHES.items():
        raw = (upstream / name).read_bytes()
        if digest(raw) != expected:
            raise ValueError(f"pinned source SHA-256 mismatch: {name}")
        sources[name] = raw.decode("utf-8")
    return sources


def _method_template(source: str, name: str, arguments: list[str]) -> str:
    marker = f"std::string CodeGenerator::translate{name}(const Instruction &inst)"
    start = source.find(marker)
    if start < 0:
        raise ValueError(f"production translation method is absent: {name}")
    end = source.find("\n    std::string CodeGenerator::", start + len(marker))
    body = source[start:end if end >= 0 else len(source)]
    ret = body.find("return fmt::format(")
    literals = re.findall(r'"(?:\\.|[^"\\])*"', body[ret:]) if ret >= 0 else []
    if not literals:
        raise ValueError(f"production translation template is absent: {name}")
    return "".join(ast.literal_eval(item) for item in literals).format(*arguments)


def _case_template(source: str, group: str, name: str) -> str:
    pattern = rf'case {group}_{name}:\s*return fmt::format\(\s*("(?:\\.|[^"\\])*")'
    match = re.search(pattern, source)
    if not match:
        raise ValueError(f"production dispatcher template is absent: {name}")
    return ast.literal_eval(match.group(1)).format("rd", "rs", "rt")


def extracted_header(sources: dict[str, str]) -> tuple[str, dict[str, str]]:
    header, mmi = sources[HEADER_PATH], sources[MMI_PATH]
    templates = {
        "PCPYLD": _method_template(mmi, "PCPYLD", ["rd", "rs", "rt"]),
        "PCPYUD": _method_template(mmi, "PCPYUD", ["rd", "rs", "rt"]),
        "PCPYH": _method_template(mmi, "PCPYH", ["rt", "rd"]),
    }
    for name, group in (("PEXTLW", "MMI0"), ("PEXTUW", "MMI1"),
                        ("PEXTLH", "MMI0"), ("PEXTLB", "MMI0"),
                        ("PAND", "MMI2"), ("POR", "MMI3"), ("PNOR", "MMI3"),
                        ("PXOR", "MMI2"), ("PSUBB", "MMI0"), ("PSUBW", "MMI0")):
        templates[name] = _case_template(mmi, group, name)
    macros = []
    for macro in MACRO_NAMES:
        line = next((line for line in header.splitlines() if line.startswith(f"#define {macro}(")), None)
        if line is None:
            raise ValueError(f"production runtime macro is absent: {macro}")
        macros.append(line)
    get_line = next((line for line in header.splitlines() if line.startswith("#define GPR_VEC(")), None)
    if get_line is None:
        raise ValueError("production GPR_VEC macro is absent")
    setter_start = header.find("#define SET_GPR_VEC(")
    setter_end = header.find("while (0)", setter_start)
    if setter_start < 0 or setter_end < 0:
        raise ValueError("production SET_GPR_VEC macro is absent")
    setter = header[setter_start:setter_end + len("while (0)")]
    wrappers = [f"void generated_{name}(Context* ctx,int rd,int rs,int rt){{(void)rs;{templates[name]}}}"
                for name in OPERATIONS]
    result = ("// Extracted from SHA-pinned PS2Recomp source.\n"
              "#include <cstdint>\n#include \"sse2neon.h\"\n"
              "struct Context { __m128i r[32]; };\n" + "\n".join(macros + [get_line, setter])
              + "\n" + "\n".join(wrappers) + "\n")
    return result, templates


def verify(upstream: Path, output: Path, sse2neon: Path, *, compiler: str = "clang++") -> dict:
    sources = pinned_sources(upstream)
    extracted, templates = extracted_header(sources)
    if output.exists():
        raise ValueError("fresh output directory already exists")
    dependency = sse2neon / "sse2neon.h"
    if not dependency.is_file() or digest(dependency.read_bytes()) != SSE2NEON_HASH:
        raise ValueError("pinned sse2neon dependency SHA-256 mismatch")
    output.mkdir(parents=True)
    (output / "probe_translations.h").write_text(extracted)
    probe = HERE / "mmi_packed_probe.cpp"
    executable = output / "mmi-packed-probe"
    command = [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined",
               "-I", str(output.resolve()), "-isystem", str(sse2neon.resolve()),
               str(probe.resolve()), "-o", str(executable.resolve())]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (output / "compile.json").write_text(json.dumps({"argv": command, "returncode": compiled.returncode,
        "stdout": compiled.stdout, "stderr": compiled.stderr}, indent=2) + "\n")
    if compiled.returncode:
        raise ValueError(f"probe compilation failed; inspect {output / 'compile.json'}")
    run = subprocess.run([str(executable.resolve())], capture_output=True, text=True, timeout=60)
    (output / "run.json").write_text(json.dumps({"argv": [str(executable.resolve())],
        "returncode": run.returncode, "stdout": run.stdout, "stderr": run.stderr}, indent=2) + "\n")
    details = json.loads(run.stdout)
    expected_checks = 10012 * 8
    if details.get("names") != list(OPERATIONS) or details.get("checks") != [expected_checks] * len(OPERATIONS):
        raise ValueError("probe did not complete the expected operation/sample matrix")
    if run.returncode or details.get("mismatches") != [0] * len(OPERATIONS) or run.stderr:
        raise ValueError("synthetic probe mismatch or sanitizer diagnostic")
    receipt = {
        "schema_version": 1, "status": "pass", "source_commit": SOURCE_COMMIT,
        "upstream": str(upstream.resolve()), "source_sha256": SOURCE_HASHES,
        "dependency": str(dependency.resolve()), "dependency_sha256": SSE2NEON_HASH,
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "probe_sha256": digest(probe.read_bytes()),
        "extracted_sha256": digest((output / "probe_translations.h").read_bytes()),
        "templates": templates, "operations": list(OPERATIONS),
        "checks_per_operation": expected_checks, "mismatches": details["mismatches"],
        "compiler_argv": command,
        "claim_limit": "Synthetic packed-vector mappings, source/destination aliasing, and zero-register macro behavior only; no game routine, instruction decoder, timing, flags, or whole-program equivalence is tested.",
    }
    (output / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="read-only pinned PS2Recomp checkout")
    parser.add_argument("--fresh-output-dir", type=Path, required=True, help="must not already exist")
    parser.add_argument("--sse2neon", type=Path, required=True, help="directory containing pinned sse2neon.h")
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    try:
        result = verify(args.upstream, args.fresh_output_dir, args.sse2neon, compiler=args.compiler)
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
