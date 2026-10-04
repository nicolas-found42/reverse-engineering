#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check pinned PS2Recomp shuffle templates using synthetic register vectors.

No game payload or generated game routine is executed. Input source hashes are
checked before any extracted template is compiled. A fresh output directory
retains probe sources, compiler commands, logs, and result hashes.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

DIRECTORY = Path(__file__).resolve().parent
HEADER_PATH = "ps2xRuntime/include/ps2_runtime_macros.h"
MMI_PATH = "ps2xRecomp/src/lib/mmi_translation_helpers.cpp"
SOURCE_COMMIT = "c5a9d02573410a2085a4b4b831b0b68ba3515440"
INPUT_HASHES = {
    HEADER_PATH: "c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e",
    MMI_PATH: "1402bdb9f81923a8c91c7fa790399a2563ebc5f7cd0c899b7c29cb7c6bafc5ee",
}
CANDIDATE_HASHES = {
    HEADER_PATH: "7371e263413510abba35291b9842609d33bfb8860ec9810edafe8a6379078530",
    MMI_PATH: "e0b82fa9b78f526ca3ec96ad430816b5d9c6e60ce47f16127eed6d212a8ba080",
}
PATCH_SHA256 = "86837455a5a1ca60a12c3064966397c9d1b1d16514e939d1e5267da79e10cf31"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_sources(upstream: Path) -> dict[str, str]:
    sources = {}
    for name, expected in INPUT_HASHES.items():
        raw = (upstream / name).read_bytes()
        if digest(raw) != expected:
            raise ValueError(f"pinned source SHA-256 mismatch: {name}")
        sources[name] = raw.decode("utf-8")
    if digest((DIRECTORY / "shuffle-lanes.patch").read_bytes()) != PATCH_SHA256:
        raise ValueError("shuffle patch SHA-256 mismatch")
    return sources


def corrected_sources(sources: dict[str, str]) -> dict[str, str]:
    replacements = {
        HEADER_PATH: [
            ("#define PS2_PEXEW(rs) _mm_shuffle_epi32(rs, _MM_SHUFFLE(2, 3, 0, 1))",
             "#define PS2_PEXEW(rs) _mm_shuffle_epi32(rs, _MM_SHUFFLE(3, 0, 1, 2))"),
            ("#define PS2_PROT3W(rs) _mm_shuffle_epi32(rs, _MM_SHUFFLE(0, 3, 2, 1))",
             "#define PS2_PROT3W(rs) _mm_shuffle_epi32(rs, _MM_SHUFFLE(3, 0, 2, 1))"),
        ],
        MMI_PATH: [
            ("// Rotates words left by 3: [d,c,b,a] -> [a,d,c,b]",
             "// Rotate the low three words; preserve word 3."),
            ("_MM_SHUFFLE(0,3,2,1)", "_MM_SHUFFLE(3,0,2,1)"),
            ("// Parallel Exchange Center Word (Swaps words 0<>2, 1<>3)",
             "// Exchange words 1 and 2; preserve words 0 and 3."),
            ("_MM_SHUFFLE(1,0,3,2)", "_MM_SHUFFLE(3,1,2,0)"),
        ],
    }
    candidate = dict(sources)
    for name, edits in replacements.items():
        text = candidate[name]
        for before, after in edits:
            if text.count(before) != 1:
                raise ValueError(f"shuffle replacement must match once: {name}")
            text = text.replace(before, after)
        if digest(text.encode()) != CANDIDATE_HASHES[name]:
            raise ValueError(f"candidate source SHA-256 mismatch: {name}")
        candidate[name] = text
    return candidate


def extracted_header(sources: dict[str, str]) -> str:
    header, mmi = sources[HEADER_PATH], sources[MMI_PATH]
    macros = "\n".join(line for line in header.splitlines() if line.startswith(
        ("#define PS2_PEXEW(", "#define PS2_PROT3W(", "#define GPR_VEC(")))
    setter = re.search(r"#define SET_GPR_VEC\([^\n]+\n(?:[^\n]+\\\n)*[^\n]+while \(0\)", header)
    if not setter:
        raise ValueError("production vector setter is absent")
    wrappers = []
    for name in ("PEXEW", "PEXCW", "PROT3W"):
        expression = re.search(
            r"std::string CodeGenerator::translate" + name
            + r'\(.*?return fmt::format\(("(?:[^"\\]|\\.)*"),\s*inst.rd, inst.rt\);',
            mmi, re.S)
        if not expression:
            raise ValueError(f"production translation template is absent: {name}")
        operation = ast.literal_eval(expression[1]).format("rd", "rt")
        wrappers.append(f"void generated_{name}(Context* ctx,int rd,int rt){{{operation}}}")
    wrappers.append("void generated_PROT3W_macro(Context* ctx,int rd,int rt){ "
                    "SET_GPR_VEC(ctx,rd,PS2_PROT3W(GPR_VEC(ctx,rt))); }")
    return ("// Extracted from hash-pinned PS2Recomp source; GPL-3.0-only.\n"
            "#if defined(USE_SSE2NEON)\n#include <sse2neon.h>\n"
            "#else\n#include <emmintrin.h>\n#endif\n"
            "struct Context { __m128i r[32]; };\n" + macros + "\n"
            + setter[0] + "\n" + "\n".join(wrappers) + "\n")


def verify(upstream: Path, output: Path, *, compiler: str = "clang++",
           sse2neon: Path | None = None) -> dict:
    # Verify all source before creating output or compiling extracted code.
    original = pinned_sources(upstream)
    candidate = corrected_sources(original)
    if output.exists():
        raise ValueError("output directory must be fresh")
    output.mkdir(parents=True)
    probe = DIRECTORY / "shuffle_probe.cpp"
    results = []
    for mode, sources in (("baseline", original), ("candidate", candidate)):
        folder = output / mode
        folder.mkdir()
        (folder / "probe_translations.h").write_text(extracted_header(sources))
        executable = folder / "probe"
        command = [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror",
                   "-fsanitize=undefined", "-I", str(folder.resolve())]
        if sse2neon is not None:
            command += ["-DUSE_SSE2NEON", "-isystem", str(sse2neon.resolve())]
        command += [str(probe), "-o", str(executable.resolve())]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=30)
        (folder / "compile.log").write_text(compiled.stdout + compiled.stderr)
        if compiled.returncode:
            raise ValueError(f"{mode} compiler failed; see {folder / 'compile.log'}")
        run = subprocess.run([str(executable.resolve())], capture_output=True, text=True, timeout=30)
        (folder / "run.log").write_text(run.stdout + run.stderr)
        details = json.loads(run.stdout)
        if details.get("checks") != [40016] * 4:
            raise ValueError(f"{mode} probe did not complete all checks")
        failures = details.get("mismatches")
        if mode == "baseline":
            if run.returncode != 1 or not isinstance(failures, list) or len(failures) != 4 or not all(failures):
                raise ValueError("original source did not reproduce each shuffle mismatch")
        elif run.returncode != 0 or failures != [0] * 4 or run.stderr:
            raise ValueError("candidate shuffle probe failed or emitted sanitizer diagnostics")
        results.append({"mode": mode, "command": command, "returncode": run.returncode,
                        "details": details, "extracted_source_sha256": digest((folder / 'probe_translations.h').read_bytes()),
                        "run_log_sha256": digest((folder / 'run.log').read_bytes())})
    receipt = {
        "schema_version": 1, "status": "pass", "source_commit": SOURCE_COMMIT,
        "input_sha256": INPUT_HASHES, "candidate_sha256": CANDIDATE_HASHES,
        "patch_sha256": PATCH_SHA256, "probe_sha256": digest(probe.read_bytes()),
        "sse2neon_header_sha256": (digest((sse2neon / 'sse2neon.h').read_bytes()) if sse2neon else None),
        "operations": ["PEXEW", "PEXCW", "PROT3W template", "PROT3W macro"],
        "results": results,
        "claim_limit": "Synthetic lane mappings, aliasing, and zero-register semantics only. No game routine executes; complete translator and game equivalence remain unproved.",
    }
    (output / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--sse2neon", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.upstream, args.output, compiler=args.compiler, sse2neon=args.sse2neon)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
