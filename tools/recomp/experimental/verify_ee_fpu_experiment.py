#!/usr/bin/env python3
"""Verify and compile the bounded experimental EE FPU emitter templates."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
HELPER = BASE / "ee_fpu_helpers.hpp"
PROBE = BASE / "probe.cpp"  # Included as the shared assertion body in generated actual-template harness.
PATCH = BASE / "ee-fpu-semantics.patch"
MANIFEST = BASE / "source-manifest.json"
EXPECTED_COMMIT = "c5a9d02573410a2085a4b4b831b0b68ba3515440"
EXPECTED_SOURCES = {
    "ps2xRecomp/src/lib/fpu_translator.cpp": "8675ddde6b708dd2d06a680f7d62b41c286776fee3340d530b56271fdc281726",
    "ps2xRuntime/include/ps2_runtime_macros.h": "c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e",
}
EXPECTED_CHANGED_PATHS = [
    "ps2xRuntime/include/ps2_runtime_macros.h",
    "ps2xRuntime/include/ee_fpu_experimental_helpers.h",
    "ps2xRecomp/src/lib/fpu_translator.cpp",
]
EXPECTED_BASELINE = {
    "macro_cvt": "#define FPU_CVT_W_S(a) ((int32_t)nearbyintf((float)(a)))",
    "macro_sqrt": "#define FPU_SQRT_S(a) sqrtf((float)(a))",
    "emit_cvt": 'return fmt::format("{{ int32_t tmp = FPU_CVT_W_S(ctx->f[{}]); std::memcpy(&ctx->f[{}], &tmp, sizeof(tmp)); }}", fs, fd);',
    "emit_sqrt": 'return fmt::format("ctx->f[{}] = FPU_SQRT_S(ctx->f[{}]);", fd, fs);',
    "emit_min": 'return fmt::format("ctx->f[{}] = std::min(ctx->f[{}], ctx->f[{}]);", fd, fs, ft);',
    "emit_max": 'return fmt::format("ctx->f[{}] = std::max(ctx->f[{}], ctx->f[{}]);", fd, fs, ft);',
}
EXPECTED_CANDIDATE = {
    "macro_cvt": "#define FPU_CVT_W_S(a) Ps2FpuCvtWS((float)(a))",
    "macro_sqrt": "#define FPU_SQRT_S(a) Ps2FpuSqrtS((float)(a), ctx->fcr31)",
    "emit_cvt": EXPECTED_BASELINE["emit_cvt"],
    "emit_sqrt": EXPECTED_BASELINE["emit_sqrt"],
    "emit_min": 'return fmt::format("{{ ctx->f[{}] = Ps2FpuMinS(ctx->f[{}], ctx->f[{}]); ctx->fcr31 &= ~0x0000c000u; }}", fd, fs, ft);',
    "emit_max": 'return fmt::format("{{ ctx->f[{}] = Ps2FpuMaxS(ctx->f[{}], ctx->f[{}]); ctx->fcr31 &= ~0x0000c000u; }}", fd, fs, ft);',
}

class VerificationError(Exception):
    def __init__(self, stage: str, message: str, command: list[str] | None = None):
        super().__init__(message)
        self.stage = stage
        self.command = command


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise VerificationError("read", f"cannot read {path}: {exc}") from exc


def run(command: list[str], *, stage: str, timeout: float, cwd: Path | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, input=input_text, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(stage, f"command timed out after {timeout:g}s", command) from exc
    except OSError as exc:
        raise VerificationError(stage, f"cannot run command: {exc}", command) from exc


def read_source_tree(source_tree: Path, timeout: float) -> tuple[dict[str, Any], str, str]:
    if not source_tree.is_dir() or not (source_tree / ".git").exists():
        raise VerificationError("source_guard", f"not a Git checkout: {source_tree}")
    proc = run(["git", "-C", str(source_tree), "rev-parse", "HEAD"], stage="source_guard", timeout=timeout)
    if proc.returncode:
        raise VerificationError("source_guard", f"git rev-parse failed: {proc.stderr.strip()}", ["git", "-C", str(source_tree), "rev-parse", "HEAD"])
    commit = proc.stdout.strip()
    if commit != EXPECTED_COMMIT:
        raise VerificationError("source_guard", f"source commit mismatch: expected {EXPECTED_COMMIT}, got {commit}")
    hashes = {}
    for rel, expected in EXPECTED_SOURCES.items():
        actual = sha256_file(source_tree / rel)
        if actual != expected:
            raise VerificationError("source_guard", f"source hash mismatch for {rel}: expected {expected}, got {actual}")
        hashes[rel] = actual
    try:
        translator = (source_tree / "ps2xRecomp/src/lib/fpu_translator.cpp").read_text()
        macros = (source_tree / "ps2xRuntime/include/ps2_runtime_macros.h").read_text()
    except OSError as exc:
        raise VerificationError("source_guard", f"cannot read pinned emitter source: {exc}") from exc
    return {"commit": commit, "source_sha256": hashes}, translator, macros


def extract_exact_line(source: str, expected: str, label: str, stage: str) -> str:
    lines = [line.strip() for line in source.splitlines() if line.strip() == expected]
    if len(lines) != 1:
        raise VerificationError(stage, f"expected exactly one {label} template, found {len(lines)}")
    return lines[0]


def extract_baseline(source_tree: Path, timeout: float) -> dict[str, Any]:
    source_meta, translator, macros = read_source_tree(source_tree, timeout)
    templates = {}
    for name in ("macro_cvt", "macro_sqrt"):
        templates[name] = extract_exact_line(macros, EXPECTED_BASELINE[name], name, "template_extract")
    for name in ("emit_cvt", "emit_sqrt", "emit_min", "emit_max"):
        templates[name] = extract_exact_line(translator, EXPECTED_BASELINE[name], name, "template_extract")
    source_meta["exact_baseline_templates"] = templates
    return source_meta


def load_manifest() -> dict[str, Any]:
    try:
        return json.loads(MANIFEST.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError("manifest", f"cannot read valid manifest {MANIFEST}: {exc}") from exc


def verify_package_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    changed_paths = manifest.get("patch", {}).get("changed_paths")
    if changed_paths != EXPECTED_CHANGED_PATHS:
        raise VerificationError(
            "manifest",
            f"patch changed paths differ from verifier allowlist: expected {EXPECTED_CHANGED_PATHS}, got {changed_paths}",
        )
    artifact_hashes = manifest.get("artifact_sha256")
    if not isinstance(artifact_hashes, dict):
        raise VerificationError("manifest", "source manifest has no artifact_sha256 mapping")
    checked = {}
    for rel, expected in artifact_hashes.items():
        path = ROOT / rel
        actual = sha256_file(path)
        if actual != expected:
            raise VerificationError("manifest", f"package hash mismatch for {rel}: expected {expected}, got {actual}")
        checked[rel] = actual
    patch_pin = manifest.get("patch", {}).get("sha256")
    if patch_pin != sha256_file(PATCH):
        raise VerificationError("manifest", "patch SHA-256 differs from checked manifest")
    if manifest.get("upstream", {}).get("commit") != EXPECTED_COMMIT:
        raise VerificationError("manifest", "manifest upstream commit differs from verifier pin")
    return checked


def decode_cpp_string(literal: str) -> str:
    try:
        return json.loads('"' + literal + '"')
    except json.JSONDecodeError as exc:
        raise VerificationError("template_extract", f"cannot decode C++ string literal: {literal}") from exc


def extract_format_string(line: str, label: str) -> str:
    match = re.search(r'return fmt::format\("((?:\\.|[^"\\])*)"\s*,', line)
    if not match:
        raise VerificationError("template_extract", f"no fmt::format string found in {label}")
    return decode_cpp_string(match.group(1))


def expand_fmt(template: str, values: list[str]) -> str:
    out=[]; i=0; index=0
    while i < len(template):
        if template.startswith("{{", i): out.append("{"); i += 2
        elif template.startswith("}}", i): out.append("}"); i += 2
        elif template.startswith("{}", i):
            if index >= len(values): raise VerificationError("template_expand", "not enough placeholder values")
            out.append(values[index]); index += 1; i += 2
        else: out.append(template[i]); i += 1
    if index != len(values): raise VerificationError("template_expand", "unused placeholder values")
    return "".join(out)


def apply_patch_in_temp(source_tree: Path, timeout: float, expected_manifest: dict[str, Any]) -> dict[str, Any]:
    patch_text = PATCH.read_text()
    expected_changed_paths = expected_manifest.get("patch", {}).get("changed_paths")
    changed_paths = re.findall(r"^\+\+\+ b/(.+)$", patch_text, flags=re.MULTILINE)
    if expected_changed_paths != EXPECTED_CHANGED_PATHS or changed_paths != EXPECTED_CHANGED_PATHS:
        raise VerificationError("patch_guard", f"patch changed paths differ from verifier allowlist: expected {EXPECTED_CHANGED_PATHS}, manifest has {expected_changed_paths}, patch has {changed_paths}")
    expected_patch_hash = expected_manifest.get("patch", {}).get("sha256")
    actual_patch_hash = sha256_file(PATCH)
    if actual_patch_hash != expected_patch_hash:
        raise VerificationError("patch_guard", f"patch hash mismatch: manifest has {expected_patch_hash}, current patch has {actual_patch_hash}")
    with tempfile.TemporaryDirectory(prefix="ee-fpu-patch-check-") as temp:
        root=Path(temp)
        changed = ["ps2xRuntime/include/ps2_runtime_macros.h", "ps2xRecomp/src/lib/fpu_translator.cpp"]
        for rel in changed:
            dst=root/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source_tree/rel,dst)
        proc=run(["patch","-p1","--batch"],stage="patch_apply",timeout=timeout,cwd=root,input_text=patch_text)
        if proc.returncode:
            raise VerificationError("patch_apply", f"patch application failed: {proc.stdout}{proc.stderr}", ["patch","-p1","--batch"])
        files={
            "ps2xRuntime/include/ee_fpu_experimental_helpers.h":(root/"ps2xRuntime/include/ee_fpu_experimental_helpers.h").read_text(),
            "ps2xRuntime/include/ps2_runtime_macros.h":(root/"ps2xRuntime/include/ps2_runtime_macros.h").read_text(),
            "ps2xRecomp/src/lib/fpu_translator.cpp":(root/"ps2xRecomp/src/lib/fpu_translator.cpp").read_text(),
        }
        expected_files=expected_manifest.get("patch",{}).get("applied_file_sha256",{})
        hashes={name:sha256_bytes(body.encode()) for name,body in files.items()}
        if hashes != expected_files:
            raise VerificationError("patch_guard", f"patched output hashes differ from manifest: expected {expected_files}, got {hashes}")
        if files["ps2xRuntime/include/ee_fpu_experimental_helpers.h"] != HELPER.read_text():
            raise VerificationError("patch_guard", "applied helper differs from tested reference helper")
        macros=files["ps2xRuntime/include/ps2_runtime_macros.h"]
        translator=files["ps2xRecomp/src/lib/fpu_translator.cpp"]
        candidate={}
        for name in ("macro_cvt","macro_sqrt"):
            candidate[name]=extract_exact_line(macros,EXPECTED_CANDIDATE[name],name,"candidate_template")
        for name in ("emit_cvt","emit_sqrt","emit_min","emit_max"):
            candidate[name]=extract_exact_line(translator,EXPECTED_CANDIDATE[name],name,"candidate_template")
        return {"patch_sha256":actual_patch_hash,"patch_apply_exit":proc.returncode,"patched_file_sha256":hashes,"exact_experimental_templates":candidate,"patch_stdout":proc.stdout,"patched_files":files}


def generated_harness(baseline: dict[str,str], candidate: dict[str,str]) -> str:
    bodies={}
    for family, templates in (("base",baseline),("cand",candidate)):
        bodies[family]={
            "cvt":expand_fmt(extract_format_string(templates["emit_cvt"],family+" CVT"),["1","0"]),
            "sqrt":expand_fmt(extract_format_string(templates["emit_sqrt"],family+" SQRT"),["0","1"]),
            "min":expand_fmt(extract_format_string(templates["emit_min"],family+" MIN"),["0","1","2"]),
            "max":expand_fmt(extract_format_string(templates["emit_max"],family+" MAX"),["0","1","2"]),
        }
    base=bodies["base"]; cand=bodies["cand"]
    code=['''#include <algorithm>\n#include <cfenv>\n#include <cmath>\n#include <cstdint>\n#include <cstdio>\n#include <cstdlib>\n#include <cstring>\n#include "ee_fpu_experimental_helpers.h"\nstruct Ctx { float f[32]{}; uint32_t fcr31=0; };\n''']
    code.extend(baseline[name]+"\n" for name in ("macro_cvt","macro_sqrt"))
    code.append('''static int32_t base_cvt(float x) { Ctx c; Ctx *ctx=&c; ctx->f[1]=x; '''+base["cvt"]+''' int32_t out; std::memcpy(&out,&ctx->f[0],4); return out; }\n''')
    code.append('''static float base_sqrt(float x, uint32_t &flags) { Ctx c; Ctx *ctx=&c; ctx->fcr31=flags; ctx->f[1]=x; '''+base["sqrt"]+''' flags=ctx->fcr31; return ctx->f[0]; }\n''')
    code.append('''static float base_min(float a,float b) { Ctx c; Ctx *ctx=&c; ctx->f[1]=a;ctx->f[2]=b; '''+base["min"]+''' return ctx->f[0]; }\n''')
    code.append('''static float base_max(float a,float b) { Ctx c; Ctx *ctx=&c; ctx->f[1]=a;ctx->f[2]=b; '''+base["max"]+''' return ctx->f[0]; }\n''')
    code.append("#undef FPU_CVT_W_S\n#undef FPU_SQRT_S\n")
    code.extend(candidate[name]+"\n" for name in ("macro_cvt","macro_sqrt"))
    code.append('''static int32_t cand_cvt(float x) { Ctx c; Ctx *ctx=&c; ctx->f[1]=x; '''+cand["cvt"]+''' int32_t out; std::memcpy(&out,&ctx->f[0],4); return out; }\n''')
    code.append('''static float cand_sqrt(float x, uint32_t &flags) { Ctx c; Ctx *ctx=&c; ctx->fcr31=flags; ctx->f[1]=x; '''+cand["sqrt"]+''' flags=ctx->fcr31; return ctx->f[0]; }\n''')
    code.append('''static float cand_min(float a,float b,uint32_t &flags) { Ctx c; Ctx *ctx=&c; ctx->fcr31=flags;ctx->f[1]=a;ctx->f[2]=b; '''+cand["min"]+''' flags=ctx->fcr31; return ctx->f[0]; }\n''')
    code.append('''static float cand_max(float a,float b,uint32_t &flags) { Ctx c; Ctx *ctx=&c; ctx->fcr31=flags;ctx->f[1]=a;ctx->f[2]=b; '''+cand["max"]+''' flags=ctx->fcr31; return ctx->f[0]; }\n''')
    code.append(PROBE.read_text())
    return "".join(code)


def compile_actual_template_probe(source_tree: Path, baseline_info: dict[str, Any], patch_info: dict[str, Any], compiler: str, timeout: float, manifest: dict[str, Any]) -> dict[str, Any]:
    # Reapply in a fresh temp tree so the helper compiled below is the actual patched file.
    with tempfile.TemporaryDirectory(prefix="ee-fpu-actual-template-") as td:
        root=Path(td)
        applied=apply_patch_in_temp(source_tree,timeout,manifest)
        header=applied["patched_files"]["ps2xRuntime/include/ee_fpu_experimental_helpers.h"]
        (root/"ee_fpu_experimental_helpers.h").write_text(header)
        source=generated_harness(baseline_info["exact_baseline_templates"],patch_info["exact_experimental_templates"])
        cpp=root/"actual_template_probe.cpp"; cpp.write_text(source)
        exe=root/"probe"
        command=[compiler,"-std=c++17","-O1","-g","-fsanitize=undefined,float-cast-overflow","-fno-sanitize-recover=all",str(cpp),"-o",str(exe)]
        build=run(command,stage="compile",timeout=timeout)
        if build.returncode:
            raise VerificationError("compile",f"actual-template probe compile failed: {build.stdout}{build.stderr}",command)
        execution=run([str(exe)],stage="probe_run",timeout=timeout)
        if execution.returncode:
            raise VerificationError("probe_run",f"actual-template probe failed: {execution.stdout}{execution.stderr}",[str(exe)])
        return {"compiler":compiler,"compile_command":command,"compile_exit":build.returncode,"run_exit":execution.returncode,"stdout":execution.stdout,"stderr":execution.stderr,"compiled_source_sha256":sha256_file(cpp),"compiled_candidate_helper_sha256":sha256_bytes(header.encode()),"baseline_templates_compiled":list(baseline_info["exact_baseline_templates"]),"candidate_templates_compiled":list(patch_info["exact_experimental_templates"])}


def atomic_write_fresh(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=path.parent,prefix=f".{path.name}.",delete=False) as out:
            temp_name=out.name
            out.write(content); out.flush(); os.fsync(out.fileno())
        try:
            os.link(temp_name,path)
        except FileExistsError as exc:
            raise VerificationError("output",f"refusing to overwrite existing output: {path}") from exc
        finally:
            os.unlink(temp_name)
    except VerificationError:
        raise
    except OSError as exc:
        if temp_name:
            try: os.unlink(temp_name)
            except OSError: pass
        raise VerificationError("output",f"cannot atomically create output {path}: {exc}") from exc


def validate_patch(source_tree: Path, timeout: float, manifest: dict[str, Any]) -> dict[str, Any]:
    # Public validation boundary: always prove the exact upstream revision and source bytes first.
    package_hashes = verify_package_manifest(manifest)
    source = extract_baseline(source_tree, timeout)
    applied = apply_patch_in_temp(source_tree, timeout, manifest)
    return {"source": source, "patch": applied, "verified_package_hashes": package_hashes}


def build_result(source_tree: Path, compiler: str, timeout: float) -> dict[str, Any]:
    manifest=load_manifest()
    checked=verify_package_manifest(manifest)
    validated=validate_patch(source_tree,timeout,manifest)
    baseline=validated["source"]
    patched=validated["patch"]
    compiler_path=shutil.which(compiler)
    if compiler_path is None:
        raise VerificationError("dependency_guard",f"compiler not found: {compiler}")
    dependency=manifest.get("dependencies",{})
    driver_hash=sha256_file(Path(compiler_path))
    if compiler=="clang++" and dependency.get("compiler_driver_sha256")!=driver_hash:
        raise VerificationError("dependency_guard",f"clang++ driver SHA mismatch: manifest has {dependency.get('compiler_driver_sha256')}, current is {driver_hash}")
    version=run([compiler,"--version"],stage="dependency_guard",timeout=timeout)
    if version.returncode or not version.stdout.splitlines():
        raise VerificationError("dependency_guard",f"compiler version check failed: {version.stderr.strip()}",[compiler,"--version"])
    version_line=version.stdout.splitlines()[0]
    if dependency.get("compiler_version") != version_line:
        raise VerificationError("dependency_guard",f"compiler version mismatch: manifest has {dependency.get('compiler_version')!r}, current is {version_line!r}")
    probe=compile_actual_template_probe(source_tree,baseline,patched,compiler,timeout,manifest)
    return {"status":"pass","scope":"actual pristine and patched synthetic emitter templates; no game routine, emulator, or hardware","source":baseline,"patch":{k:v for k,v in patched.items() if k!="patched_files"},"probe":probe,"dependencies":{"compiler_version":version_line,"compiler_path":compiler_path,"compiler_driver_sha256":driver_hash,"python":sys.version.split()[0],"verified_package_hashes":checked}}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-tree",type=Path,required=True,help="explicit checkout of the pinned PS2Recomp revision")
    parser.add_argument("--compiler",default="clang++")
    parser.add_argument("--timeout",type=float,default=30.0)
    parser.add_argument("--output",type=Path,help="create a fresh JSON result atomically; existing files are refused")
    args=parser.parse_args(argv)
    if args.timeout<=0:
        error=VerificationError("arguments","--timeout must be positive")
    else:
        try:
            result=build_result(args.source_tree,args.compiler,args.timeout)
            encoded=json.dumps(result,indent=2)+"\n"
            if args.output:
                atomic_write_fresh(args.output,encoded)
            else:
                print(encoded,end="")
            return 0
        except VerificationError as exc:
            error=exc
        except (OSError,ValueError,KeyError,TypeError) as exc:
            error=VerificationError("internal",str(exc))
    diagnostic={"status":"error","error":{"stage":error.stage,"type":type(error).__name__,"message":str(error),"command":error.command}}
    print(json.dumps(diagnostic,indent=2),file=sys.stderr)
    return 2

if __name__=="__main__":
    raise SystemExit(main())
