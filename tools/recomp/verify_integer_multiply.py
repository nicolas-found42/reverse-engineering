#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Probe four pinned EE multiply templates against an independent modulo oracle."""
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
STATIC_EXPORT_HASH = "554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383"
EXECUTABLE_HASH = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95"
MANUAL_PDF_HASH = "104205afc6f5a5071168d8bf693a6c8b4db9a02e1aa66eb51a828e8951f5c069"
INVENTORY_COUNTS = {"MULT": 241, "MULTU": 5, "MULT1": 24, "MADD": 3}
OPERATION_NAMES = ("MULT_RD", "MULT_R0", "MULTU_RD", "MULTU_R0",
                   "MULT1_RD", "MULT1_R0", "MADD_RD", "MADD_R0")
MACROS = ("PS2_EXTRACT_EPI32_0", "GPR_U32", "GPR_S32", "SET_GPR_S32")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pinned_sources(root: Path) -> dict[str, str]:
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True, timeout=30).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("source checkout is unavailable") from exc
    if head != COMMIT:
        raise ValueError("source commit differs from pinned revision")
    sources: dict[str, str] = {}
    for name, expected in SOURCE_HASHES.items():
        raw = (root / name).read_bytes()
        if digest(raw) != expected:
            raise ValueError(f"source SHA-256 differs: {name}")
        sources[name] = raw.decode("utf-8")
    return sources


def pinned_inventory(path: Path) -> tuple[dict, dict[str, list[str]]]:
    raw = path.read_bytes()
    if digest(raw) != STATIC_EXPORT_HASH:
        raise ValueError("static export SHA-256 differs from the pinned historical inventory")
    data = json.loads(raw)
    if (data.get("executable_sha256") != EXECUTABLE_HASH
            or data.get("language") != "r5900:LE:32:default"
            or len(data.get("functions", [])) != 3446):
        raise ValueError("static export identity/profile differs from the measured inventory")
    found: dict[str, list[str]] = {name: [] for name in INVENTORY_COUNTS}
    for function in data["functions"]:
        for instruction in function.get("instructions", []):
            text = instruction.get("text", "").strip().split()
            if text and text[0].upper() in found:
                found[text[0].upper()].append(instruction["address"])
    for name, expected in INVENTORY_COUNTS.items():
        addresses = found[name]
        if len(addresses) != expected or len(set(addresses)) != expected:
            raise ValueError(f"historical {name} inventory count/address set differs")
    return data, found


def inventory_summary(addresses: dict[str, list[str]]) -> dict[str, dict[str, str | int]]:
    """Keep the report compact while pinning each ordered address inventory."""
    return {
        name: {
            "count": len(values),
            "ordered_addresses_sha256": digest("\n".join(values).encode("ascii")),
        }
        for name, values in addresses.items()
    }


def extract_returns(source: str, marker: str, arguments: list[str]) -> list[str]:
    case_marker = f"case {marker}:"
    start = source.find(case_marker)
    if start < 0:
        raise ValueError(f"multiply translator case absent: {marker}")
    end = source.find("case ", start + len(case_marker))
    body = source[start:end if end >= 0 else len(source)]
    if "if (inst.rd != 0)" not in body and "if (rd != 0)" not in body:
        raise ValueError(f"destination-zero branch guard absent: {marker}")
    pattern = r'return fmt::format\(\s*((?:"(?:\\.|[^"\\])*"\s*)+),'
    templates = []
    for match in re.finditer(pattern, body):
        literals = re.findall(r'"(?:\\.|[^"\\])*"', match.group(1))
        templates.append("".join(ast.literal_eval(literal) for literal in literals).format(*arguments))
    if len(templates) != 2:
        raise ValueError(f"expected rd and zero-rd templates for {marker}; found {len(templates)}")
    return templates


def _inline(header: str, start_marker: str, end_marker: str, label: str) -> str:
    start = header.find(start_marker)
    end = header.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise ValueError(f"pinned {label} helper block absent")
    return header[start:end]


def _macro(header: str, name: str) -> str:
    start = header.find(f"#define {name}(")
    if start < 0:
        raise ValueError(f"pinned register macro absent: {name}")
    end = header.find("while (0)", start)
    if end < 0:
        newline = header.find("\n", start)
        return header[start:newline]
    return header[start:end + len("while (0)")]


def _single_line_macro(header: str, name: str) -> str:
    line = next((line for line in header.splitlines() if line.startswith(f"#define {name}(") ), None)
    if line is None:
        raise ValueError(f"pinned register macro absent: {name}")
    return line


def extracted_header(sources: dict[str, str]) -> tuple[str, dict[str, str], dict[str, str]]:
    header = sources[HEADER]
    special, mmi = sources[SPECIAL], sources[MMI]
    template_lists = {
        "MULT": extract_returns(special, "SPECIAL_MULT", ["rs", "rt", "rd"]),
        "MULTU": extract_returns(special, "SPECIAL_MULTU", ["rs", "rt", "rd"]),
        "MULT1": extract_returns(mmi, "MMI_MULT1", ["rs", "rt", "rd"]),
        "MADD": extract_returns(mmi, "MMI_MADD", ["rs", "rt", "rd"]),
    }
    templates = {"MULT_RD": template_lists["MULT"][0], "MULT_R0": template_lists["MULT"][1],
                 "MULTU_RD": template_lists["MULTU"][0], "MULTU_R0": template_lists["MULTU"][1],
                 "MULT1_RD": template_lists["MULT1"][0], "MULT1_R0": template_lists["MULT1"][1],
                 "MADD_RD": template_lists["MADD"][0], "MADD_R0": template_lists["MADD"][1]}
    extract32 = _inline(header, "static inline int32_t Ps2ExtractEpi32(",
                        "static inline int64_t Ps2ExtractEpi64(", "32-bit register extractor")
    hilo_helpers = _inline(header, "static inline uint64_t Ps2HiLoToU64(",
                           "// PLZCW:", "HI/LO word helpers")
    set_low = _inline(header, "static inline void Ps2SetGprLow64(",
                      "#define SET_GPR_U32(", "low-word register writer")
    helper = (extract32 + hilo_helpers + "using R5900Context = Context;\n" + set_low)
    macros = [_single_line_macro(header, name) for name in MACROS[:3]] + [_macro(header, "SET_GPR_S32")]
    wrappers: dict[str, str] = {}
    for name in OPERATION_NAMES:
        wrappers[name] = f"void generated_{name}(Context* ctx,int rd,int rs,int rt){{(void)rd;{templates[name]}}}"
    output = ("// Extracted production multiply emitters and register helpers from the pinned revision.\n"
              "#include <cstdint>\n#include <climits>\n#include \"sse2neon.h\"\n"
              "struct Context { __m128i r[32]; uint64_t hi,lo,hi1,lo1; };\n"
              + helper + "\n" + "\n".join(macros) + "\n" + "\n".join(wrappers.values()) + "\n")
    return output, templates, wrappers


def _run_probe(argv: list[str], output_file: Path, timeout: int = 120,
               *, expected_returncode: int = 0) -> dict:
    run = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    output_file.write_text(json.dumps({"argv": argv, "returncode": run.returncode,
                                      "stdout": run.stdout, "stderr": run.stderr}, indent=2) + "\n")
    if run.returncode != expected_returncode:
        raise ValueError(f"native probe exit status {run.returncode} differs from {expected_returncode}; inspect {output_file}")
    if run.stderr:
        raise ValueError(f"native probe emitted stderr; inspect {output_file}")
    try:
        return json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"native probe did not emit JSON; inspect {output_file}") from exc


def verify(upstream: Path, inventory: Path, output: Path, dependency: Path,
           *, compiler: str = "clang++") -> dict:
    if output.exists():
        raise ValueError("output directory must be fresh")
    sources = pinned_sources(upstream)
    inventory_data, inventory_addresses = pinned_inventory(inventory)
    raw_dependency = (dependency / "sse2neon.h").read_bytes()
    if digest(raw_dependency) != DEPENDENCY_HASH:
        raise ValueError("sse2neon SHA-256 differs from pinned dependency")
    header, templates, wrappers = extracted_header(sources)
    output.mkdir(parents=True)
    generated = output / "multiply_templates.h"
    generated.write_text(header)
    probe = HERE / "integer_multiply_probe.cpp"
    executable = output / "multiply-probe"
    command = [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined",
               "-fno-sanitize-recover=all", "-I", str(output.resolve()), "-isystem",
               str(dependency.resolve()), str(probe.resolve()), "-o", str(executable.resolve())]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (output / "compile.json").write_text(json.dumps({"argv": command, "returncode": compiled.returncode,
        "stdout": compiled.stdout, "stderr": compiled.stderr}, indent=2) + "\n")
    if compiled.returncode:
        raise ValueError("multiply probe compilation failed; inspect compile.json")
    expected_checks = (12 * 12 + 20000) * 10
    details = _run_probe([str(executable.resolve())], output / "run.json")
    if (details.get("names") != list(OPERATION_NAMES)
            or details.get("checks") != [expected_checks] * len(OPERATION_NAMES)
            or details.get("mismatches") != [0] * len(OPERATION_NAMES)):
        raise ValueError("multiply comparison matrix failed")

    mutant = output / "mutant"
    mutant.mkdir()
    mutant_header = header
    for name, wrapper in wrappers.items():
        bank = "lo1" if name.startswith("MULT1") else "lo"
        corrupted = wrapper[:-1] + f" ctx->{bank} ^= 1ull;}}"
        if mutant_header.count(wrapper) != 1:
            raise ValueError("negative-control wrapper is not unique")
        mutant_header = mutant_header.replace(wrapper, corrupted)
    (mutant / "multiply_templates.h").write_text(mutant_header)
    mutant_executable = mutant / "multiply-probe"
    mutant_command = command.copy()
    mutant_command[mutant_command.index("-I") + 1] = str(mutant.resolve())
    mutant_command[-1] = str(mutant_executable.resolve())
    mutant_compile = subprocess.run(mutant_command, capture_output=True, text=True, timeout=60)
    (mutant / "compile.json").write_text(json.dumps({"argv": mutant_command,
        "returncode": mutant_compile.returncode, "stdout": mutant_compile.stdout,
        "stderr": mutant_compile.stderr}, indent=2) + "\n")
    if mutant_compile.returncode:
        raise ValueError("multiply negative-control compilation failed")
    mutant_result = _run_probe([str(mutant_executable.resolve())], mutant / "run.json",
                               expected_returncode=1)
    if (mutant_result.get("names") != list(OPERATION_NAMES)
            or mutant_result.get("checks") != [expected_checks] * len(OPERATION_NAMES)
            or mutant_result.get("mismatches") != [expected_checks] * len(OPERATION_NAMES)):
        raise ValueError("corrupted multiply templates were not detected for every sample")

    result = {
        "schema_version": 1, "status": "pass", "source_commit": COMMIT,
        "source_hashes": SOURCE_HASHES, "dependency_sha256": DEPENDENCY_HASH,
        "static_export": {"sha256": STATIC_EXPORT_HASH, "executable_sha256": EXECUTABLE_HASH,
                           "function_count": len(inventory_data["functions"]),
                           "instruction_inventory": inventory_summary(inventory_addresses),
                           "counts": INVENTORY_COUNTS},
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "probe_sha256": digest(probe.read_bytes()), "extracted_sha256": digest(generated.read_bytes()),
        "templates": templates, "details": details, "checks_per_emitted_branch": expected_checks,
        "compiler_argv": command, "mutant": mutant_result,
        "manual": {"url": "https://docs.alexrp.com/mips/ee_insns.pdf",
                   "printed_pages": {"MADD": 142, "MULT": 154, "MULT1": 155, "MULTU": 156},
                   "pdf_sha256": MANUAL_PDF_HASH},
        "claim_limit": "Synthetic source-pinned expression checks for valid sign-extended 32-bit operands, low-64 HI/LO state, both register banks, rd=0, source aliases and register preservation. This does not test decoder behavior, asynchronous timing/interlocks, flags, execution of game code, or silicon equivalence.",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--static-export", type=Path, required=True)
    parser.add_argument("--fresh-output-dir", type=Path, required=True)
    parser.add_argument("--sse2neon", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    try:
        result = verify(args.upstream, args.static_export, args.fresh_output_dir,
                        args.sse2neon, compiler=args.compiler)
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
