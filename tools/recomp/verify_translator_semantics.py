#!/usr/bin/env python3
"""Validate the pinned PS2Recomp scalar arithmetic translator experiment.

This tool stages only two pinned translator sources in a temporary directory,
applies the local patch there, extracts actual emitted C++ templates, and runs
synthetic arithmetic/control-flow checks. It never edits the supplied checkout.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PINNED_COMMIT = "c5a9d02573410a2085a4b4b831b0b68ba3515440"
SOURCE_HASHES = {
    "ps2xRecomp/src/lib/instruction_translator.cpp": "b24105265f6d6f14c48bb72e5066877e0b3e1ffe439ddd0331e0d297004bd226",
    "ps2xRecomp/src/lib/special_translator.cpp": "98adc0305effdd57ca34ea029070f117379bd7e78c9f8944a8e9276c8c7bd3cd",
}
AUXILIARY_HASHES = {
    "ps2xRecomp/src/lib/function_emitter.cpp": "a0dc4503e18abd010fa008f2e5b03b16ed9d05434435ff49725a72c11102ba84",
    "ps2xRecomp/src/lib/control_flow_emitter.cpp": "44c0204441106b033a6897bfd52e6e6ce551a6d64a12a7004518a76d657eea07",
    "ps2xRuntime/src/lib/ps2_runtime.cpp": "77cd184f2e70eacfd5ea584ec95829553e3deeead0a19c04e4b0970dd7c6c9ee",
}
CANDIDATE_HASHES = {
    "ps2xRecomp/src/lib/instruction_translator.cpp": "d4e99dca9b814c307f933085dde05d138a191a39e6c52fcf37767453a1f22eb7",
    "ps2xRecomp/src/lib/special_translator.cpp": "86a554b9172db6857b64a3ed05599d0b245bab4819dacfce082cd3eec87d753c",
}
BASELINE_FORMAT_ARGS = {"daddiu": [2, 1, 1]}
SPECS = [
    ("addi", "ps2xRecomp/src/lib/instruction_translator.cpp", "OPCODE_ADDI", "OPCODE_ADDIU", [1, 1, 0]),
    ("daddi", "ps2xRecomp/src/lib/instruction_translator.cpp", "OPCODE_DADDI", "OPCODE_DADDIU", [1, 1, 2]),
    ("daddiu", "ps2xRecomp/src/lib/instruction_translator.cpp", "OPCODE_DADDIU", "OPCODE_J", [1, 1, 2]),
    ("add", "ps2xRecomp/src/lib/special_translator.cpp", "SPECIAL_ADD", "SPECIAL_ADDU", [1, 2, 3]),
    ("sub", "ps2xRecomp/src/lib/special_translator.cpp", "SPECIAL_SUB", "SPECIAL_SUBU", [1, 2, 3]),
    ("dadd", "ps2xRecomp/src/lib/special_translator.cpp", "SPECIAL_DADD", "SPECIAL_DADDU", [1, 2, 3]),
    ("dsub", "ps2xRecomp/src/lib/special_translator.cpp", "SPECIAL_DSUB", "SPECIAL_DSUBU", [1, 2, 3]),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def verify_source_file_hashes(root: Path) -> None:
    """Reject missing or modified input files before staging or patching."""
    for rel, expected in SOURCE_HASHES.items():
        path = root / rel
        if not path.is_file():
            raise ValueError(f"missing pinned translator source: {rel}")
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"wrong input SHA-256 for {rel}: expected {expected}, got {actual}")


def verify_exception_propagation_sources(root: Path) -> None:
    """Pin and assert the caller/runtime checks downstream of this patch."""
    for rel, expected in AUXILIARY_HASHES.items():
        path = root / rel
        if not path.is_file():
            raise ValueError(f"missing pinned exception-flow source: {rel}")
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"wrong input SHA-256 for {rel}: expected {expected}, got {actual}")
    runtime = (root / "ps2xRuntime/src/lib/ps2_runtime.cpp").read_text()
    control = (root / "ps2xRecomp/src/lib/control_flow_emitter.cpp").read_text()
    function = (root / "ps2xRecomp/src/lib/function_emitter.cpp").read_text()
    required_runtime = (
        "targetFn(rdram, ctx, this);",
        "if (ctx->pc == entryPc)",
        "ctx->pc = fallthroughPc;",
        "return ctx->pc == fallthroughPc;",
        "ctx->pc = selectExceptionVector(ctx, tlbRefill);",
        "ctx->in_delay_slot = false;",
    )
    dispatch_start = control.index("void ControlFlowEmitter::emitRuntimeBranchDispatch")
    dispatch_end = control.index("bool ControlFlowEmitter::emitDirectFunctionJumpIfAvailable", dispatch_start)
    dispatch_body = control[dispatch_start:dispatch_end]
    direct_start = control.index("void ControlFlowEmitter::emitExternalJumpDispatch")
    indirect_start = control.index("void ControlFlowEmitter::emitExternalRegisterCallDispatch", direct_start)
    indirect_end = control.index("void ControlFlowEmitter::emitExternalRegisterJumpDispatch", indirect_start)
    direct_call_body = control[direct_start:indirect_start]
    indirect_call_body = control[indirect_start:indirect_end]
    if not all(token in runtime for token in required_runtime):
        raise ValueError("pinned runtime call/exception propagation source no longer matches reviewed flow")
    if ("if (!runtime->dispatchGuestBranch(rdram, ctx," not in dispatch_body
            or "if (returnOnTransfer)" not in dispatch_body
            or r'fmt::format("{}    return;\n", indent)' not in dispatch_body):
        raise ValueError("pinned generated runtime-dispatch wrapper does not return when transfer fails")
    if ('isCall ? "DirectCall" : "DirectJump"' not in direct_call_body
            or "indent,\n                                  true);" not in direct_call_body):
        raise ValueError("pinned direct call emission does not request caller return on failed transfer")
    if ('"IndirectCall"' not in indirect_call_body
            or "indent,\n                                  true);" not in indirect_call_body):
        raise ValueError("pinned indirect call emission does not request caller return on failed transfer")
    if "ctx->pc = 0x" not in function or "function.end" not in function:
        raise ValueError("pinned FunctionEmitter fallthrough-PC path was not found")


def verify_commit(root: Path) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        raise ValueError(f"source root is not a readable Git checkout: {result.stderr.strip()}")
    actual = result.stdout.strip()
    if actual != PINNED_COMMIT:
        raise ValueError(f"wrong PS2Recomp commit: expected {PINNED_COMMIT}, got {actual}")


def extract_case_template(source: str, case: str, next_case: str) -> str:
    start = source.find(f"case {case}:")
    if start < 0:
        raise ValueError(f"cannot find translator case {case}")
    end = source.find(f"case {next_case}:", start + len(case))
    if end < 0:
        raise ValueError(f"cannot find following case {next_case} after {case}")
    block = source[start:end]
    fmt_start = block.find("fmt::format(")
    if fmt_start < 0:
        raise ValueError(f"case {case} does not contain the expected fmt::format template")
    # One C++ string literal per concatenated template fragment; restrict to
    # the format call and reject empty or unexpected fields below.
    literals = re.findall(r'"(?:\\.|[^"\\])*"', block[fmt_start:])
    if not literals:
        raise ValueError(f"no format string literals found for {case}")
    template = "".join(ast.literal_eval(value) for value in literals)
    return template


def format_template(template: str, values: list[int]) -> str:
    out: list[str] = []
    i = 0
    value_index = 0
    while i < len(template):
        if template.startswith("{{", i):
            out.append("{"); i += 2
        elif template.startswith("}}", i):
            out.append("}"); i += 2
        elif template.startswith("{}", i):
            if value_index >= len(values):
                raise ValueError("not enough values for format fields")
            out.append(str(values[value_index])); value_index += 1; i += 2
        elif template[i] in "{}":
            raise ValueError(f"unexpected fmt field in bounded template: {template[i:i+12]!r}")
        else:
            out.append(template[i]); i += 1
    if value_index != len(values):
        raise ValueError(f"used {value_index} fields but got {len(values)} format values")
    return "".join(out)


def actual_template_source(root: Path, name: str, rel: str, case: str, next_case: str, args: list[int]) -> str:
    template = extract_case_template((root / rel).read_text(), case, next_case)
    return format_template(template, args)


def stage_and_patch(source_root: Path, temp_root: Path) -> Path:
    stage = temp_root / "stage"
    for rel in SOURCE_HASHES:
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / rel, target)
    file_set = {str(p.relative_to(stage)) for p in stage.rglob("*") if p.is_file()}
    if file_set != set(SOURCE_HASHES):
        raise ValueError(f"staging was not isolated to pinned translator files: {sorted(file_set)}")
    patch_file = Path(__file__).resolve().with_name("translator-semantics.patch")
    apply = subprocess.run(
        ["patch", "-p1", "--batch", "--forward", "-i", str(patch_file)],
        cwd=stage, capture_output=True, text=True, timeout=15,
    )
    if apply.returncode != 0:
        raise ValueError(f"cannot apply translator patch to pinned inputs: {apply.stdout}{apply.stderr}")
    for rel, expected in CANDIDATE_HASHES.items():
        actual = sha256(stage / rel)
        if actual != expected:
            raise ValueError(f"patched candidate SHA mismatch for {rel}: expected {expected}, got {actual}")
    file_set_after = {str(p.relative_to(stage)) for p in stage.rglob("*") if p.is_file()}
    if file_set_after != set(SOURCE_HASHES):
        raise ValueError(f"patch escaped isolated translator files: {sorted(file_set_after)}")
    return stage


HARNESS_PREAMBLE = r'''#include <cstdint>
#include <cstdio>
#include <stdexcept>
struct Context { uint64_t r[32]{}; uint32_t pc=0, epc=0, branch_pc=0; bool in_delay_slot=false, exl=false, later=false; };
struct Runtime { void SignalException(Context* c, int) { c->epc=c->in_delay_slot?c->branch_pc:c->pc; c->pc=0x80000180; c->in_delay_slot=false; c->exl=true; } };
enum { EXCEPTION_INTEGER_OVERFLOW=12 };
static uint32_t GPR_U32(Context* c,unsigned i){return i?uint32_t(c->r[i]):0;}
static int32_t GPR_S32(Context* c,unsigned i){return int32_t(GPR_U32(c,i));}
static uint64_t GPR_U64(Context* c,unsigned i){return i?c->r[i]:0;}
static int64_t GPR_S64(Context* c,unsigned i){return int64_t(GPR_U64(c,i));}
static void SET_GPR_S32(Context*c,unsigned i,int32_t x){if(i)c->r[i]=uint64_t(int64_t(x));}
static void SET_GPR_U64(Context*c,unsigned i,uint64_t x){if(i)c->r[i]=x;}
static void SET_GPR_S64(Context*c,unsigned i,int64_t x){if(i)c->r[i]=uint64_t(x);}
static void ADD32_OV(uint32_t a,int32_t b,uint32_t& r,bool& ov){int64_t w=int64_t(int32_t(a))+b;ov=w>INT32_MAX||w<INT32_MIN;r=uint32_t(w);}
static void SUB32_OV(uint32_t a,uint32_t b,uint32_t& r,bool& ov){int64_t w=int64_t(int32_t(a))-int64_t(int32_t(b));ov=w>INT32_MAX||w<INT32_MIN;r=uint32_t(w);}
'''


def generated_harness(candidate_root: Path) -> str:
    funcs = []
    for name, rel, case, next_case, values in SPECS:
        body = actual_template_source(candidate_root, name, rel, case, next_case, values)
        funcs.append(f"void generated_{name}(Context*ctx,Runtime*runtime){{ctx->pc=0x1000; {body} ctx->pc=0x1008; ctx->later=true;}}")
    entry = r'''static void req(bool x,const char*m){if(!x)throw std::runtime_error(m);}
int main(){Runtime rt;
 {Context c{};c.r[1]=0x7fffffffffffffffULL;c.r[2]=1;c.r[3]=0x12345678;generated_dadd(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180&&c.epc==0x1000&&c.r[3]==0x12345678,"DADD exception");}
 {Context c{};c.r[1]=0x8000000000000000ULL;c.r[2]=1;c.r[3]=0x12345678;generated_dsub(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180&&c.r[3]==0x12345678,"DSUB exception");}
 {Context c{};c.r[1]=0x7fffffffffffffffULL;c.r[3]=0x12345678;generated_daddi(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180&&c.r[3]==0x12345678,"DADDI exception");}
 {Context c{};c.r[1]=0xffffffffffffffffULL;generated_daddiu(&c,&rt);req(!c.exl&&c.r[2]==0&&c.later&&c.pc==0x1008,"DADDIU modulo");}
 {Context c{};c.r[1]=0x7fffffffULL;generated_addi(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180&&c.epc==0x1000&&c.r[0]==0,"ADDI rt0 overflow");}
 {Context c{};c.r[1]=0x7fffffffULL;c.r[2]=1;generated_add(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180,"ADD exception return");}
 {Context c{};c.r[1]=0x80000000ULL;c.r[2]=1;generated_sub(&c,&rt);req(c.exl&&!c.later&&c.pc==0x80000180,"SUB exception return");}
 {Context c{};c.r[1]=0x7fffffffULL;c.in_delay_slot=true;c.branch_pc=0x2000;generated_addi(&c,&rt);req(c.epc==0x2000&&c.exl&&!c.in_delay_slot&&!c.later&&c.pc==0x80000180,"delay slot ADDI exception");}
 {Context c{};c.r[1]=4;generated_addi(&c,&rt);req(!c.exl&&!c.r[0]&&c.later&&c.pc==0x1008,"ADDI rt0 no overflow");}
 {Context c{};c.r[1]=0x7fffffffffffffffULL;c.r[2]=1;c.pc=0x5000;const uint32_t entryPc=c.pc;generated_dadd(&c,&rt);if(c.pc==entryPc)c.pc=0x6000;bool returnedToFallthrough=(c.pc==0x6000);if(returnedToFallthrough){c.pc=0x7000;c.later=true;}req(!returnedToFallthrough&&!c.later&&c.pc==0x80000180,"callee exception propagation through caller");}
 std::puts("PASS extracted candidate translator templates: 10 normal/overflow/delay-slot/caller controls");}
'''
    return HARNESS_PREAMBLE + "\n".join(funcs) + "\n" + entry


def compile_run(cpp: Path, binary: Path, clang: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    subprocess.run(
        [clang, "-std=c++20", "-O1", "-Wall", "-Wextra", "-Wno-unused-parameter", "-fsanitize=undefined,signed-integer-overflow", "-fno-sanitize-recover=all", str(cpp), "-o", str(binary)],
        check=True, capture_output=True, text=True, timeout=timeout,
    )
    return subprocess.run([str(binary)], check=False, capture_output=True, text=True, timeout=timeout)


def run_verification(source_root: Path) -> dict[str, object]:
    source_root = source_root.resolve()
    verify_commit(source_root)
    verify_source_file_hashes(source_root)
    verify_exception_propagation_sources(source_root)
    patch_tool = shutil.which("patch")
    clang = shutil.which("clang++")
    if not patch_tool:
        raise RuntimeError("patch utility is required")
    if not clang:
        raise RuntimeError("clang++ is required for UBSan validation")
    with tempfile.TemporaryDirectory(prefix="translator-semantics-") as temp_name:
        temp = Path(temp_name)
        stage = stage_and_patch(source_root, temp)
        candidate_cpp = temp / "candidate_templates.cpp"
        candidate_cpp.write_text(generated_harness(stage))
        candidate_result = compile_run(candidate_cpp, temp / "candidate_templates", clang)
        if candidate_result.returncode != 0:
            raise RuntimeError(f"candidate emitted templates failed: {candidate_result.stdout}{candidate_result.stderr}")
        baseline_cpp = temp / "upstream_templates.cpp"
        baseline_cpp.write_text(HARNESS_PREAMBLE.replace("#include <cstdio>", "#include <cstdio>\n#include <string_view>") + "\n".join(
            f"void generated_{name}(Context*ctx,Runtime*runtime){{ctx->pc=0x1000; {actual_template_source(source_root, name, rel, case, next_case, BASELINE_FORMAT_ARGS.get(name, values))} ctx->pc=0x1008; ctx->later=true;}}"
            for name,rel,case,next_case,values in SPECS if name in {"dadd","dsub","daddi","daddiu"}
        ) + r'''int main(int argc,char**argv){ if(argc!=2)return 3; Runtime rt; Context c{}; const char*op=argv[1];
 if(std::string_view(op)=="dadd"){c.r[1]=0x7fffffffffffffffULL;c.r[2]=1;generated_dadd(&c,&rt);}
 else if(std::string_view(op)=="dsub"){c.r[1]=0x8000000000000000ULL;c.r[2]=1;generated_dsub(&c,&rt);}
 else if(std::string_view(op)=="daddi"){c.r[1]=0x7fffffffffffffffULL;generated_daddi(&c,&rt);}
 else if(std::string_view(op)=="daddiu"){c.r[1]=0x7fffffffffffffffULL;generated_daddiu(&c,&rt);}
 else if(std::string_view(op)=="safe"){c.r[1]=1;c.r[2]=2;generated_dadd(&c,&rt);generated_dsub(&c,&rt);generated_daddi(&c,&rt);generated_daddiu(&c,&rt);}
 else return 4; std::puts("baseline completed");}
''')
        subprocess.run(
            [clang, "-std=c++20", "-O1", "-Wall", "-Wextra", "-Wno-unused-parameter", "-fsanitize=undefined,signed-integer-overflow", "-fno-sanitize-recover=all", str(baseline_cpp), "-o", str(temp / "upstream_templates")],
            check=True, capture_output=True, text=True, timeout=30,
        )
        baseline = {}
        baseline_bin = temp / "upstream_templates"
        safe = subprocess.run([str(baseline_bin), "safe"], check=False, capture_output=True, text=True, timeout=30)
        if safe.returncode != 0:
            raise RuntimeError(f"upstream baseline safe control failed: {safe.stdout}{safe.stderr}")
        for op in ("dadd", "dsub", "daddi", "daddiu"):
            run = subprocess.run([str(baseline_bin), op], check=False, capture_output=True, text=True, timeout=30)
            diagnostic = run.stdout + run.stderr
            if run.returncode == 0 or "signed integer overflow" not in diagnostic:
                raise RuntimeError(f"upstream {op} negative control did not reproduce UBSan: {diagnostic}")
            baseline[op] = {"returncode": run.returncode, "ubsan_detected": True, "diagnostic": diagnostic.replace(str(temp), "<temporary-build-dir>").strip()[-500:]}
        arithmetic_cpp = Path(__file__).resolve().with_name("translator_semantics_arithmetic.cpp")
        arithmetic_run = compile_run(arithmetic_cpp, temp / "arithmetic_reference", clang)
        if arithmetic_run.returncode != 0:
            raise RuntimeError(f"independent arithmetic reference test failed: {arithmetic_run.stdout}{arithmetic_run.stderr}")
        return {
            "status": "pass",
            "upstream_commit": PINNED_COMMIT,
            "input_sha256": SOURCE_HASHES,
            "exception_flow_source_sha256": AUXILIARY_HASHES,
            "candidate_sha256": CANDIDATE_HASHES,
            "candidate_template_tests": candidate_result.stdout.strip(),
            "caller_exception_propagation": "PASS: pinned callee dispatch returns false when exception vector differs from call fallthrough; emitted caller returns on false",
            "baseline_ubsan_negative_controls": baseline,
            "baseline_safe_control": safe.stdout.strip(),
            "independent_reference": arithmetic_run.stdout.strip(),
            "isolated_files": sorted(SOURCE_HASHES),
            "patch_sha256": sha256(Path(__file__).resolve().with_name("translator-semantics.patch")),
            "limitations": [
                "Only two translator files are staged and patched; no full project or game source is generated.",
                "Synthetic register/runtime support is used. ADD32_OV and SUB32_OV are defined in the harness for the scalar ADDI/SUB checks; full runtime composition requires the separate defined-overflow patch.",
                "No original game routine or emulator is executed.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path, help="path to the pinned PS2Recomp checkout at the recorded commit")
    args = parser.parse_args()
    try:
        result = run_verification(args.source_root)
    except subprocess.CalledProcessError as exc:
        print(json.dumps({
            "status": "fail",
            "error": "validation subprocess failed",
            "returncode": exc.returncode,
            "stdout": (exc.stdout or "")[-4000:],
            "stderr": (exc.stderr or "")[-4000:],
        }, indent=2), file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
