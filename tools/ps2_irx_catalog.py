"""Annotate IRX imports with provisional names from exact-version SDK tables.

The source is a pinned public PS2SDK checkout. This reads macro declarations,
never preprocesses or executes SDK code, and never identifies original symbols.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from evidence_common import Incomplete, Invalid
from ps2_irx import parse_irx

SDK_COMMIT = "ac92a9f657d2e531dd8f060250b07f2a5ac6dea5"
DECIMAL = r"(?:0|[1-9][0-9]{0,2})"
BEGIN = re.compile(r"DECLARE_EXPORT_TABLE\(([A-Za-z0-9_]{1,8}),\s*(" + DECIMAL
                   + r"),\s*(" + DECIMAL + r")\)")
EXPORT = re.compile(r"DECLARE_EXPORT\(([A-Za-z_][A-Za-z0-9_]*)\)")


def parse_tables(text: str, *, source: str) -> list[dict]:
    """Read only literal declarations; any preprocessor directive excludes a file."""
    if len(text.encode()) > 2_000_000:
        raise Invalid("export source exceeds bounded input size")
    # Declaration files contain no string operands in the supported grammar.
    # Anchored whole-line matches prevent strings outside a table becoming rows.
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)
    if "/*" in text or "*/" in text:
        raise Invalid("unterminated or unmatched block comment")
    lines = [line.split("//", 1)[0].strip() for line in text.splitlines()]
    if any(line.startswith("#") for line in lines):
        raise Incomplete("preprocessor-dependent export declarations are excluded")
    tables: list[dict] = []
    current: dict | None = None
    for line in lines:
        if not line:
            continue
        begin = BEGIN.fullmatch(line)
        if begin:
            if current is not None:
                raise Invalid("nested export table")
            major, minor = int(begin[2]), int(begin[3])
            if major > 255 or minor > 255:
                raise Invalid("export version exceeds byte fields")
            current = {"library": begin[1], "version": major << 8 | minor,
                       "functions": [], "source": source}
        elif line == "END_EXPORT_TABLE":
            if current is None or not current["functions"]:
                raise Invalid("unmatched or empty export table")
            tables.append(current)
            current = None
        elif current is not None:
            entry = EXPORT.fullmatch(line)
            if not entry or len(current["functions"]) >= 65536:
                raise Invalid("unsupported export row or excessive ordinal count")
            current["functions"].append(entry[1])
        elif "DECLARE_EXPORT_TABLE" in line or "DECLARE_EXPORT(" in line:
            raise Invalid("unsupported declaration outside export table")
        # Plain helper C after the table is irrelevant and never evaluated.
    if current is not None:
        raise Invalid("unterminated export table")
    if not tables:
        raise Invalid("no literal export table found")
    return tables


def candidate_name(library: str, version: int, index: int, tables: list[dict]) -> dict:
    if (type(version) is not int or not 0 <= version <= 65535
            or type(index) is not int or not 0 <= index <= 65535):
        raise Invalid("version and ordinal require bounded unsigned 16-bit integers")
    if not re.fullmatch(r"[A-Za-z0-9_]{1,8}", library):
        raise Invalid("library name is outside the measured identifier grammar")
    matching = [t for t in tables if t["library"] == library and t["version"] == version
                and index < len(t["functions"])]
    names = sorted({t["functions"][index] for t in matching})
    return {"candidate_name": names[0] if len(names) == 1 else None,
            "status": "candidate-api-name" if len(names) == 1 else
                      "ambiguous" if names else "unresolved",
            "catalog_sources": sorted({t["source"] for t in matching}),
            "original_identity_verified": False,
            "match_policy": "exact library/version/ordinal only"}


def catalog_from_sdk(root: Path) -> dict:
    def git(*args: str) -> bytes:
        try:
            return subprocess.run(["git", "-C", str(root), *args], check=True,
                                  capture_output=True, timeout=30).stdout
        except subprocess.CalledProcessError as exc:
            raise Invalid("pinned SDK Git source is unavailable") from exc
    if git("rev-parse", "HEAD").decode().strip() != SDK_COMMIT:
        raise Invalid("SDK revision differs from the pinned catalog source")
    names = git("ls-tree", "-r", "--name-only", SDK_COMMIT, "iop").decode().splitlines()
    names = [name for name in names if name.endswith("/exports.tab")]
    if not names or len(names) > 4096:
        raise Invalid("SDK export declaration file count is unsupported")
    tables: list[dict] = []
    sources, excluded = [], []
    for name in names:
        if not name.startswith("iop/") or ".." in Path(name).parts:
            raise Invalid("SDK source path escapes the bounded catalog")
        raw = (root / name).read_bytes()
        if raw != git("show", f"{SDK_COMMIT}:{name}"):
            raise Invalid(f"SDK source differs from the pinned Git object: {name}")
        sources.append({"path": name, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
        try:
            tables.extend(parse_tables(raw.decode(), source=name))
        except (Incomplete, Invalid) as exc:
            excluded.append({"path": name, "reason": str(exc)})
    return {"sdk_commit": SDK_COMMIT, "sources": sources,
            "excluded_sources": excluded, "tables": tables}


def annotate_irx(data: bytes, catalog: dict, *, source: str | None = None) -> dict:
    module = parse_irx(data, source=source)
    links = []
    counts: dict[str, int] = {}
    for table in module["imports"]:
        for link in table["links"]:
            candidate = candidate_name(table["library"], table["version"],
                                       link["index"], catalog["tables"])
            counts[candidate["status"]] = counts.get(candidate["status"], 0) + 1
            links.append({"library": table["library"], "version": table["version"],
                          "index": link["index"], "stub_text_offset": link["stub_text_offset"],
                          **candidate})
    return {"schema_version": 1, "source": source, "sha256": module["sha256"],
            "module_name": module["module"]["name"], "sdk_commit": catalog["sdk_commit"],
            "import_annotations": links, "counts": counts,
            "claim_limits": ["Names are candidates from public SDK tables, not recovered original symbols.",
                             "Exact versions are required; no minor-version or build-variant guess is made.",
                             "No module linking, relocation, machine-code execution or API semantics is proved."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path, required=True)
    parser.add_argument("--irx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise Invalid("output must be fresh")
        catalog = catalog_from_sdk(args.sdk_root)
        result = annotate_irx(args.irx.read_bytes(), catalog, source=str(args.irx))
        result["catalog_provenance"] = {k: v for k, v in catalog.items() if k != "tables"}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": "candidate-annotations", "counts": result["counts"],
                          "output": str(args.output)}))
        return 0
    except (Invalid, Incomplete, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
