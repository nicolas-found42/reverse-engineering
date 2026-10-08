#!/usr/bin/env python3
"""Compile one evidenced function with pinned GNU EE candidates and compare bytes.

The manifest supplies argv arrays, never shell snippets. Candidate tools and source
are hashed into the receipt. A unique passing candidate is a probe result, not
proof of a unique original compiler unless the probe is independently diagnostic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import uuid

from evidence_common import Incomplete, Invalid, identity
from matching_diff import compare
from matching_sections import Section

COMMAND_TIMEOUT_SECONDS = 120


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand_command(command: list[str], paths: dict[str, Path]) -> list[str]:
    return [arg.format(**{key: str(value) for key, value in paths.items()}) for arg in command]


def run_command(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True,
                          timeout=COMMAND_TIMEOUT_SECONDS)


def run_probe(manifest_path: Path, output: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    required = {"source", "symbol", "reference", "candidates"}
    if not required <= manifest.keys() or not manifest["candidates"]:
        raise Invalid("manifest requires source, symbol, reference, and nonempty candidates")
    source = Path(manifest["source"]).resolve()
    reference = Path(manifest["reference"]).resolve()
    if not source.is_file() or not reference.is_file():
        raise Incomplete("source or reference bytes are missing")
    expected = reference.read_bytes()
    symbol = manifest["symbol"]
    results = []
    output.mkdir(parents=True, exist_ok=True)
    for item in manifest["candidates"]:
        name = item.get("id")
        if not name or not item.get("compile") or not item.get("objcopy"):
            raise Invalid("each candidate needs id, compile argv, and objcopy argv")
        compiler = Path(item["compile"][0]).resolve()
        compiler_binary = Path(item.get("compiler_executable", item["compile"][0])).resolve()
        objcopy = Path(item["objcopy"][0]).resolve()
        objcopy_binary = Path(item.get("objcopy_executable", item["objcopy"][0])).resolve()
        row = {"id": name, "status": "incomplete", "compiler_launcher": str(compiler),
               "compiler": str(compiler_binary), "objcopy_launcher": str(objcopy),
               "objcopy": str(objcopy_binary), "runtime": item.get("runtime"),
               "compile_argv": item["compile"],
               "objcopy_argv": item["objcopy"], "flags": item.get("flags", [])}
        if compiler.is_file():
            row["compiler_launcher_sha256"] = digest(compiler)
        if objcopy.is_file():
            row["objcopy_launcher_sha256"] = digest(objcopy)
        tool_files = item.get("tool_files", {})
        row["tool_files"] = {}
        missing_tools = []
        for tool_name, tool_path in tool_files.items():
            path = Path(tool_path).resolve()
            if not path.is_file():
                missing_tools.append(tool_name)
            else:
                row["tool_files"][tool_name] = {"path": str(path), **identity(path)}
        if (missing_tools or not compiler.is_file() or not compiler_binary.is_file()
                or not objcopy.is_file() or not objcopy_binary.is_file()):
            if missing_tools:
                row["reason"] = "pinned candidate tool files are unavailable: " + ", ".join(missing_tools)
                results.append(row)
                continue
            row["reason"] = "candidate compiler or objcopy is unavailable"
            results.append(row)
            continue
        row["compiler_sha256"] = digest(compiler_binary)
        row["objcopy_sha256"] = digest(objcopy_binary)
        # Keep transient files under the mounted tool root: remote/container
        # candidate launchers cannot see a host-only /var/folders temp path.
        with tempfile.TemporaryDirectory(prefix="fr2-compiler-probe-", dir=output) as temp:
            obj = Path(temp) / "candidate.o"
            extracted = Path(temp) / "function.bin"
            compile_argv = [str(compiler), *item["compile"][1:], *item.get("flags", []),
                            "-ffunction-sections", "-c", str(source), "-o", str(obj)]
            try:
                compiled = subprocess.run(compile_argv, capture_output=True, text=True,
                                         timeout=COMMAND_TIMEOUT_SECONDS)
            except (OSError, subprocess.TimeoutExpired) as exc:
                row.update(status="error", reason=f"candidate compiler could not complete: {exc}")
                results.append(row)
                continue
            row["compile_returncode"] = compiled.returncode
            row["compile_stderr"] = compiled.stderr[-4000:]
            if compiled.returncode:
                row.update(status="error", reason="candidate compilation failed")
                results.append(row)
                continue
            paths = {"object": obj, "prepared_object": Path(temp) / "prepared.o",
                     "linked_object": Path(temp) / "linked.o"}
            object_to_extract = obj
            for phase in ("prepare_object", "link"):
                if phase not in item:
                    continue
                phase_argv = expand_command(item[phase], paths)
                row[f"{phase}_argv"] = phase_argv
                try:
                    phase_result = run_command(phase_argv)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    row.update(status="error", reason=f"{phase} could not complete: {exc}")
                    results.append(row)
                    break
                row[f"{phase}_returncode"] = phase_result.returncode
                row[f"{phase}_stderr"] = phase_result.stderr[-4000:]
                if phase_result.returncode:
                    row.update(status="error", reason=f"{phase} failed")
                    results.append(row)
                    break
                object_to_extract = paths["prepared_object"] if phase == "prepare_object" else paths["linked_object"]
            else:
                objcopy_argv = [str(objcopy), *item["objcopy"][1:], "--dump-section",
                                f".text.{symbol}={extracted}", str(object_to_extract)]
                try:
                    copied = run_command(objcopy_argv)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    row.update(status="error", reason=f"function extraction could not complete: {exc}")
                    results.append(row)
                    continue
                row["objcopy_returncode"] = copied.returncode
                row["objcopy_stderr"] = copied.stderr[-4000:]
                if copied.returncode or not extracted.is_file():
                    row.update(status="error", reason="function section could not be extracted")
                    results.append(row)
                    continue
                actual = extracted.read_bytes()
                row["actual_sha256"] = hashlib.sha256(actual).hexdigest()
                row["actual_bytes"] = len(actual)
                row["reference_sha256"] = hashlib.sha256(expected).hexdigest()
                row["reference_bytes"] = len(expected)
                reference_range = manifest.get("evidence", {}).get("reference_range", {})
                section_name = reference_range.get("section", f".probe.{symbol}")
                address = int(reference_range.get("vaddr", "0"), 16)
                file_offset = int(reference_range.get("file_offset", "0"), 16)
                target = Section(section_name, address, file_offset, len(expected), expected,
                                 hashlib.sha256(expected).hexdigest())
                verdict = compare(target, actual)
                row.update(status=verdict.status, gate=verdict.as_dict())
                if verdict.status == "fail":
                    row["reason"] = "function bytes differ"
                results.append(row)
    matches = [r["id"] for r in results if r["status"] == "pass"]
    failures = [r["id"] for r in results if r["status"] == "fail"]
    incomplete = [r["id"] for r in results if r["status"] == "incomplete"]
    errors = [r["id"] for r in results if r["status"] == "error"]
    if errors or incomplete or len(matches) > 1:
        status = "incomplete"
    elif len(matches) == 1:
        status = "pass"
    elif failures:
        status = "fail"
    else:
        status = "incomplete"
    return {"status": status, "selected_id": matches[0] if status == "pass" else None,
            "matches": matches, "failures": failures, "errors": errors,
            "incomplete": incomplete,
            "manifest": {"path": str(manifest_path.resolve()), **identity(manifest_path)},
            "evidence": manifest.get("evidence", {}),
            "source": {"path": str(source), **identity(source)},
            "reference": {"path": str(reference), **identity(reference)},
            "symbol": symbol, "candidates": results,
            "claim_limits": ["A unique match identifies this source/compiler/flags/reference probe only.",
                             "It does not establish the original compiler ID without an independently evidenced retail function/reference pair.",
                             "This runner executes compiler and objcopy argv from the local manifest."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-probe"))
    args = parser.parse_args()
    try:
        result = run_probe(args.manifest, args.output)
    except Incomplete as exc:
        result = {"status": "incomplete", "diagnostics": [str(exc)],
                  "manifest": str(args.manifest)}
    except FileNotFoundError as exc:
        result = {"status": "incomplete", "diagnostics": [str(exc)],
                  "manifest": str(args.manifest)}
    except (Invalid, ValueError, KeyError, IndexError, TypeError, OSError) as exc:
        result = {"status": "fail", "diagnostics": [f"{type(exc).__name__}: {exc}"],
                  "manifest": str(args.manifest)}
    run = args.output / uuid.uuid4().hex
    run.mkdir(parents=True, exist_ok=False)
    receipt = run / "result.json"
    result["receipt"] = str(receipt)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    report = f"# Compiler probe: {result['status']}\n\n"
    report += "\n".join(result.get("diagnostics", [])) + "\n\n```json\n"
    report += json.dumps(result, indent=2) + "\n```\n"
    (run / "report.md").write_text(report)
    print(json.dumps(result, indent=2))
    return {"pass": 0, "fail": 1, "incomplete": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
