#!/usr/bin/env python3
"""Reconcile the pinned IOP source candidate with original GNU archives and patch.

This prepares a temporary local source tree only. It neither builds a compiler
nor certifies a historical package or game-owned IOP byte match.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from compiler_provenance import DECISION
from evidence_common import Incomplete, Invalid, identity, sha256, write_result


GNU_ARCHIVES = {
    "gcc-2.8.1": "https://ftp.gnu.org/gnu/gcc/gcc-2.8.1.tar.gz",
    "binutils-2.9.1": "https://ftp.gnu.org/gnu/binutils/binutils-2.9.1.tar.gz",
}

# Recorded source-tree reconciliation, fixed independently of caller inputs.
# Expected modern changes remain differences; extra or missing changes fail.
EXPECTED_COMPARISON = {
    "gcc-2.8.1": {"same_files": 1219, "changed": ["c-gperf.h", "config.in", "obstack.h"],
                  "missing": [], "additional": ["config.in~"]},
    "binutils-2.9.1": {"same_files": 2083, "changed": ["include/obstack.h"],
                       "missing": [], "additional": []},
}


def validate_comparison(results: dict) -> None:
    observed = {
        name: {**row, "changed": [item["path"] for item in row["changed"]]}
        for name, row in results["comparison"].items()
    }
    if observed != EXPECTED_COMPARISON:
        raise Invalid("IOP derived source tree differs from recorded reconciliation", results)


def reconcile(source_archive: Path, gnu_root: Path) -> dict:
    decision = json.loads(DECISION.read_text())
    if identity(source_archive) != decision["archive"]:
        raise Invalid("source candidate archive differs from its fixed pin",
                      {"source_archive": identity(source_archive), "expected": decision["archive"]})
    results = {"source_archive": identity(source_archive), "gnu_archives": {}, "comparison": {},
               "missing": [], "changed": [],
               "historical_binding_status": "incomplete", "matched_bytes": 0,
               "limitations": ["Source derivation only; no compiler was built and no game code was executed.",
                               "GCC 2.8.1 and its IOP retargeting patch do not bind the selected EE 2.96 package.",
                               "Changed modern source files are retained as differences, not assumed behavior-preserving."]}
    with zipfile.ZipFile(source_archive) as source, tempfile.TemporaryDirectory(prefix="fr2-iop-source-") as temporary:
        root = Path(temporary)
        prefix = decision["root"]
        originals = {}
        for name, url in GNU_ARCHIVES.items():
            member = f"iop/original/{name}.tar.gz"
            original = source.read(prefix + member)
            observed = {"bytes": len(original), "sha256": sha256(original)}
            downloaded = gnu_root / f"gnu-{name}.tar.gz"
            downloaded_identity = identity(downloaded) if downloaded.is_file() else None
            results["gnu_archives"][name] = {"url": url, **observed,
                                            "downloaded": downloaded_identity,
                                            "candidate_member_equal": downloaded_identity == observed}
            if downloaded_identity is None:
                results["missing"].append(name)
            if observed != decision["members"][member] or (downloaded_identity is not None and downloaded_identity != observed):
                results["changed"].append(name)
            originals[name] = original
        # Inspect both inputs first; an absent archive must not hide a later
        # changed one. No patch/extraction runs with unresolved identities.
        if results["changed"]:
            raise Invalid("GNU download or candidate original archive differs", results)
        if results["missing"]:
            raise Incomplete("GNU source archive download is missing", results)
        for name, original in originals.items():
            with tarfile.open(fileobj=io.BytesIO(original)) as package:
                for entry in package:
                    # Write regular source files ourselves. Do not restore archive
                    # links, ownership, modes or paths outside the temporary tree.
                    rel = PurePosixPath(entry.name)
                    if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != name:
                        raise Invalid("GNU source archive has an unsupported path", results)
                    target = root.joinpath(*rel.parts)
                    if entry.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    elif entry.isfile():
                        stream = package.extractfile(entry)
                        if stream is None:
                            raise Invalid("GNU source member is unreadable", results)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with stream:
                            target.write_bytes(stream.read())
                    else:
                        raise Invalid("GNU source archive has an unsupported link or member type", results)
        patch_member = "iop/original/iop-gcc.patch"
        patch_data = source.read(prefix + patch_member)
        if {"bytes": len(patch_data), "sha256": sha256(patch_data)} != decision["members"][patch_member]:
            raise Invalid("IOP retargeting patch differs from its fixed pin", results)
        patch_file = root / "iop-gcc.patch"
        patch_file.write_bytes(patch_data)
        argv = ["patch", "--batch", "-p0", "-i", str(patch_file)]
        patched = subprocess.run(argv, cwd=root, capture_output=True, timeout=30)
        results["patch"] = {"argv_template": ["patch", "--batch", "-p0", "-i", "<temporary>/iop-gcc.patch"],
                            "returncode": patched.returncode, "stdout_sha256": sha256(patched.stdout),
                            "stderr_sha256": sha256(patched.stderr), "patch_identity": identity(patch_file)}
        if patched.returncode != 0:
            raise Invalid("pinned IOP source patch did not apply cleanly", results)
        for name in GNU_ARCHIVES:
            directory = root / name
            archive_prefix = prefix + f"iop/{name}/"
            listed = [item for item in source.namelist() if item.startswith(archive_prefix) and not item.endswith("/")]
            original_files = {p.relative_to(directory).as_posix(): p for p in directory.rglob("*") if p.is_file()}
            current_files = {item[len(archive_prefix):]: item for item in listed}
            same, changed = 0, []
            for relative in sorted(original_files.keys() & current_files.keys()):
                derived = identity(original_files[relative])
                candidate_data = source.read(current_files[relative])
                current = {"bytes": len(candidate_data), "sha256": sha256(candidate_data)}
                if derived == current:
                    same += 1
                else:
                    changed.append({"path": relative, "derived": derived, "candidate": current})
            results["comparison"][name] = {
                "same_files": same, "changed": changed,
                "missing": sorted(original_files.keys() - current_files.keys()),
                "additional": sorted(current_files.keys() - original_files.keys()),
            }
    validate_comparison(results)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_archive", type=Path)
    parser.add_argument("gnu_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/compiler-iop-source"))
    args = parser.parse_args(argv)
    return write_result(args.output, "compiler-iop-source-reconciliation", lambda: reconcile(args.source_archive, args.gnu_root),
                        [DECISION, Path(__file__)])


if __name__ == "__main__":
    sys.exit(main())
