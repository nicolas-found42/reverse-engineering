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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        objcopy = Path(item["objcopy"][0]).resolve()
        row = {"id": name, "status": "incomplete", "compiler": str(compiler),
               "objcopy": str(objcopy), "compile_argv": item["compile"],
               "objcopy_argv": item["objcopy"], "flags": item.get("flags", [])}
        if not compiler.is_file() or not objcopy.is_file():
            row["reason"] = "candidate compiler or objcopy is unavailable"
            results.append(row)
            continue
        row["compiler_sha256"] = digest(compiler)
        row["objcopy_sha256"] = digest(objcopy)
        with tempfile.TemporaryDirectory(prefix="fr2-compiler-probe-") as temp:
            obj = Path(temp) / "candidate.o"
            extracted = Path(temp) / "function.bin"
            compile_argv = [str(compiler), *item["compile"][1:], *item.get("flags", []),
                            "-ffunction-sections", "-c", str(source), "-o", str(obj)]
            compiled = subprocess.run(compile_argv, capture_output=True, text=True)
            row["compile_returncode"] = compiled.returncode
            row["compile_stderr"] = compiled.stderr[-4000:]
            if compiled.returncode:
                row.update(status="fail", reason="candidate compilation failed")
                results.append(row)
                continue
            objcopy_argv = [str(objcopy), *item["objcopy"][1:], "--dump-section",
                            f".text.{symbol}={extracted}", str(obj)]
            copied = subprocess.run(objcopy_argv, capture_output=True, text=True)
            row["objcopy_returncode"] = copied.returncode
            row["objcopy_stderr"] = copied.stderr[-4000:]
            if copied.returncode or not extracted.is_file():
                row.update(status="incomplete", reason="function section could not be extracted")
                results.append(row)
                continue
            actual = extracted.read_bytes()
            row["actual_sha256"] = hashlib.sha256(actual).hexdigest()
            row["actual_bytes"] = len(actual)
            row["reference_sha256"] = hashlib.sha256(expected).hexdigest()
            row["reference_bytes"] = len(expected)
            target = Section(f".probe.{symbol}", 0, 0, len(expected), expected,
                             hashlib.sha256(expected).hexdigest())
            verdict = compare(target, actual)
            row.update(status=verdict.status, gate=verdict.as_dict())
            if verdict.status == "fail":
                row["reason"] = "function bytes differ"
            results.append(row)
    matches = [r["id"] for r in results if r["status"] == "pass"]
    failures = [r["id"] for r in results if r["status"] == "fail"]
    incomplete = [r["id"] for r in results if r["status"] == "incomplete"]
    status = "pass" if len(matches) == 1 and not incomplete else "fail" if failures else "incomplete"
    return {"status": status, "selected_id": matches[0] if status == "pass" else None,
            "matches": matches, "failures": failures, "incomplete": incomplete,
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
    result = run_probe(args.manifest, args.output)
    run = args.output / uuid.uuid4().hex
    run.mkdir(parents=True, exist_ok=False)
    receipt = run / "result.json"
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    result["receipt"] = str(receipt)
    print(json.dumps(result, indent=2))
    return {"pass": 0, "fail": 1, "incomplete": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
