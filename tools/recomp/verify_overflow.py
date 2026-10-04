#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import argparse
import hashlib
import subprocess
import sys
import tempfile

NAMES = ("ADD32_OV", "SUB32_OV")

def extract(text: str) -> str:
    lines = text.splitlines()
    output = ["#include <cstdint>", "#include <limits>"]
    for name in NAMES:
        start = next((i for i, line in enumerate(lines) if line.startswith(f"#define {name}(")), None)
        if start is None:
            raise ValueError(f"missing {name} macro")
        at = start
        while True:
            line = lines[at]
            output.append(line)
            if not line.rstrip().endswith("\\"):
                break
            at += 1
            if at >= len(lines):
                raise ValueError(f"unterminated {name} macro")
    return "\n".join(output) + "\n"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("header", type=Path)
    parser.add_argument("--expect-ubsan", action="store_true")
    args = parser.parse_args()
    expected = "c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e" if args.expect_ubsan else "4b88ff8ea6966dd97aa17cb0e06c0c8ad98923b84af32b335e6e8972a0537973"
    if hashlib.sha256(args.header.read_bytes()).hexdigest() != expected:
        sys.stderr.write("header SHA-256 differs from the pinned experiment profile\n")
        return 2
    work = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="recomp-overflow-") as temporary:
        temp = Path(temporary)
        (temp / "overflow_macros_only.h").write_text(extract(args.header.read_text()))
        binary = temp / "probe"
        compile_result = subprocess.run([
            "clang++", "-std=c++20", "-fsanitize=undefined,signed-integer-overflow",
            "-fno-sanitize-recover=all", "-Wall", "-Wextra", "-Werror",
            f"-I{temp}", str(work / "overflow_probe.cpp"), "-o", str(binary)
        ], text=True, capture_output=True, timeout=30)
        if compile_result.returncode:
            sys.stderr.write(compile_result.stdout + compile_result.stderr)
            return compile_result.returncode
        run = subprocess.run([str(binary)], text=True, capture_output=True, timeout=30)
        output = run.stdout + run.stderr
        if args.expect_ubsan:
            if run.returncode == 0 or "runtime error: signed integer overflow" not in output:
                sys.stderr.write("expected UBSan signed-overflow failure, got:\n" + output)
                return 1
            print("baseline reproduced UBSan signed-overflow failure")
            return 0
        if run.returncode:
            sys.stderr.write(output)
            return run.returncode
        print(output, end="")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
