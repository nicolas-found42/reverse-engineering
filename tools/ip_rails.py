#!/usr/bin/env python3
"""Refuse to commit a PS2 boot executable or any Sony-derived artifact (ADR-0004).

Reads the staged blobs, not the working tree, so `git commit -a` and partial staging cannot
slip a corpus file through. Intended as the body of `tools/hooks/pre-commit`; `--tree` scans every tracked file (CI).
"""
from __future__ import annotations

import fnmatch
import re
import struct
import subprocess
import sys
from pathlib import Path

EE_MACHINE = 8
EE_MACH_BITS = 0x00920000  # EF_MIPS_MACH for the R5900, ICO and the retail e_flags
BOOT_NAME = re.compile(r"(?i)(?:^|/)(?:SLES|SLUS|SCES|SCUS|SLPM|SLPS)_\d{3}\.?\d{2}$")
FORBIDDEN_PATTERNS = ("*.irx", "*.IRX", "*.a", "*.o", "*.iso", "*.img", "*.elf", "*.sav", "*.mcd",
                      "*/extracted/*", "extracted/*", "*FILES.DAT", "*FILES.HDR", "games/*/*.bin")
STAMP = re.compile(rb"PsII[a-z0-9 ]{8}[0-9]{4}")


def violations(path: str, data: bytes) -> list[str]:
    found = []
    if BOOT_NAME.search(path):
        found.append("PS2 boot executable name")
    for pattern in FORBIDDEN_PATTERNS:
        if fnmatch.fnmatchcase(path.lower(), pattern.lower()):
            found.append(f"path matches the never-commit pattern {pattern}")
            break
    if data[:4] == b"\x7fELF" and len(data) >= 52:
        machine, = struct.unpack_from("<H", data, 18)
        flags, = struct.unpack_from("<I", data, 36)
        if machine == EE_MACHINE:
            note = " with EE mach bits" if (flags & 0x00FF0000) == EE_MACH_BITS else ""
            found.append(f"MIPS ELF (PS2 Emotion Engine or IOP artifact, e_machine 8){note}")
    if STAMP.search(data) and not _is_text(data):
        found.append("Sony SDK library stamp inside a binary blob")
    return found


def _is_text(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return b"\0" not in data


def staged() -> list[tuple[str, bytes]]:
    names = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
                           capture_output=True, check=True).stdout.split(b"\0")
    blobs = []
    for raw in filter(None, names):
        path = raw.decode()
        blobs.append((path, subprocess.run(["git", "show", ":" + path], capture_output=True,
                                           check=True).stdout))
    return blobs


def tracked_violations(root: Path) -> dict[str, list[str]]:
    """Every tracked file that breaks a rule: the CI check, independent of any local hook."""
    names = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True,
                           check=True).stdout.split(b"\0")
    found = {}
    for raw in filter(None, names):
        path = root / raw.decode()
        if path.is_file() and (why := violations(raw.decode(), path.read_bytes())):
            found[raw.decode()] = why
    return found


def main() -> int:
    if "--tree" in sys.argv[1:]:
        refused = tracked_violations(Path.cwd())
    else:
        refused = {path: why for path, data in staged() if (why := violations(path, data))}
    for path, reasons in refused.items():
        print(f"refused {path}: " + "; ".join(reasons), file=sys.stderr)
    if refused:
        print("docs/LEGAL.md lists what may never be committed.", file=sys.stderr)
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
