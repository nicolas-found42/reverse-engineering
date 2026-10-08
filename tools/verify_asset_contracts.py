#!/usr/bin/env python3
"""Check archive-derived asset family/variant coverage and loader-bound contracts.

Exit status: 0 complete, 1 malformed/contradictory coverage, 2 honest but incomplete.
The checker inventories extensions and raw/zlib variants from FILES.HDR and FILES.DAT;
contract declarations cannot shrink that denominator.
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from evidence_common import Incomplete, Invalid, write_result
from format_contracts import archive

ROOT = Path(__file__).resolve().parent.parent
FUNCTION = re.compile(r"(?:FUN_)?[0-9a-fA-F]{8}\Z")


def extension(path: str) -> str:
    name = path.rsplit("/", 1)[-1].lower()
    if ";" in name:
        name = name.rsplit(";", 1)[0]
    dot = name.rfind(".")
    return name[dot:] if dot > 0 else "<none>"


def catalog(parsed: dict) -> dict:
    found = defaultdict(Counter)
    paths = defaultdict(list)
    for item in parsed["files"]:
        ext = extension(item["path"])
        found[ext][item["classification"]] += 1
        paths[ext].append(item["path"])
    return {
        ext: {"file_count": sum(counts.values()), "variants": dict(sorted(counts.items())),
              "examples": sorted(paths[ext])[:3]}
        for ext, counts in sorted(found.items())
    }


def check_contracts(parsed: dict, declarations: dict) -> dict:
    if declarations.get("schema_version") != 1 or not isinstance(declarations.get("contracts"), list):
        raise Invalid("contract manifest must have schema_version 1 and a contracts array")
    actual = catalog(parsed)
    by_extension, errors, unresolved, checked = {}, [], [], []
    for contract in declarations["contracts"]:
        if not isinstance(contract, dict):
            errors.append("each contract must be an object")
            continue
        ident, status, extensions = contract.get("id"), contract.get("status"), contract.get("extensions")
        if not isinstance(ident, str) or not ident:
            errors.append("contract is missing an id")
            continue
        if status not in {"complete", "partial", "unresolved"}:
            errors.append(f"{ident}: status must be complete, partial, or unresolved")
        terms = contract.get("consumer_contract")
        required_terms = ("consumer", "bounds", "field_effects", "transformations",
                          "allocation_lifetime", "handoffs", "unknowns")
        if not isinstance(terms, dict) or any(not terms.get(key) for key in required_terms):
            errors.append(f"{ident}: consumer_contract must document {', '.join(required_terms)}")
        if not isinstance(extensions, list) or not extensions:
            errors.append(f"{ident}: extensions must be a nonempty list")
            continue
        evidence = contract.get("loader_evidence", [])
        if not isinstance(evidence, list):
            errors.append(f"{ident}: loader_evidence must be a list")
            evidence = []
        bound = []
        for item in evidence:
            if not isinstance(item, dict):
                errors.append(f"{ident}: malformed loader evidence")
                continue
            function, source = item.get("function"), item.get("source")
            if not isinstance(function, str) or not FUNCTION.fullmatch(function):
                errors.append(f"{ident}: loader evidence needs a function identifier (FUN_XXXXXXXX)")
                continue
            if not isinstance(source, str):
                errors.append(f"{ident}: loader evidence for {function} needs a repository source path")
                continue
            path = (ROOT / source).resolve()
            if ROOT.resolve() not in path.parents or not path.is_file():
                errors.append(f"{ident}: loader evidence source does not exist inside the repository: {source}")
                continue
            if function.lower() not in path.read_text(errors="replace").lower():
                errors.append(f"{ident}: {function} is not named in loader evidence source {source}")
                continue
            bound.append({"function": function, "source": source})
        if status in {"complete", "partial"} and not bound:
            errors.append(f"{ident}: {status} contract claim has no bound loader evidence")
        if status in {"complete", "partial"} and isinstance(terms, dict):
            consumer = str(terms.get("consumer", "")).lower()
            for item in bound:
                if item["function"].lower() not in consumer:
                    errors.append(f"{ident}: consumer contract does not name cited loader {item['function']}")
        structures = contract.get("structure_evidence", [])
        if not isinstance(structures, list):
            errors.append(f"{ident}: structure_evidence must be a list")
            structures = []
        for source in structures:
            if not isinstance(source, str):
                errors.append(f"{ident}: malformed structure evidence path")
                continue
            path = (ROOT / source).resolve()
            if ROOT.resolve() not in path.parents or not path.is_file():
                errors.append(f"{ident}: structure evidence source does not exist inside the repository: {source}")
        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith("."):
                errors.append(f"{ident}: extension values must start with a dot")
                continue
            key = ext.lower()
            if key not in actual:
                errors.append(f"{ident}: declared extension {key} is absent from the archive")
            if key in by_extension:
                errors.append(f"extension {key} is assigned to more than one contract")
            else:
                by_extension[key] = contract
        checked.append({"id": ident, "status": status, "extensions": extensions,
                        "loader_evidence": bound, "variant_dispositions": contract.get("variant_dispositions", {}),
                        "structure_evidence": structures})
        if status != "complete":
            unresolved.append(ident)
    missing = sorted(set(actual) - set(by_extension))
    if missing:
        errors.append("archive extensions have no contract: " + ", ".join(missing))
    for ext, contract in by_extension.items():
        dispositions = contract.get("variant_dispositions", {})
        if not isinstance(dispositions, dict):
            errors.append(f"{ext}: variant_dispositions must be an object")
            continue
        required = set(actual.get(ext, {}).get("variants", {}))
        absent = sorted(required - set(dispositions))
        invented = sorted(set(dispositions) - required)
        if absent:
            errors.append(f"{ext}: archive variants lack a disposition: {', '.join(absent)}")
        if invented:
            errors.append(f"{ext}: dispositions name variants absent from the archive: {', '.join(invented)}")
        invalid = sorted(v for v in required if dispositions.get(v) not in {"covered", "unresolved"})
        if invalid:
            errors.append(f"{ext}: variant dispositions must be covered or unresolved: {', '.join(invalid)}")
        if contract.get("status") == "complete" and any(dispositions.get(v) != "covered" for v in required):
            errors.append(f"{ext}: complete contract has unresolved archive variants")
        if contract.get("status") == "partial" and not any(dispositions.get(v) == "covered" for v in required):
            errors.append(f"{ext}: partial contract covers none of the archive variants")
    if errors:
        raise Invalid("; ".join(errors), {"catalog": actual, "contracts": checked})
    return {"catalog": actual, "contracts": checked, "unresolved_contracts": unresolved,
            "complete": not unresolved,
            "claim_limits": "Archive-derived extension and raw/zlib inventory plus evidence-binding validation only. Complete status requires documented coverage of every observed storage variant. This checker does not validate asset semantics or prove loader behavior beyond its cited evidence."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["archive"])
    parser.add_argument("header", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("--contracts", type=Path, default=Path(__file__).resolve().parent.parent / "notes/asset-consumer-contracts.json")
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/asset-contracts"))
    args = parser.parse_args()

    def run():
        parsed = archive(args.header.read_bytes(), args.data.read_bytes())
        try:
            declarations = json.loads(args.contracts.read_text())
        except json.JSONDecodeError as exc:
            raise Invalid(f"invalid contract manifest JSON: {exc}") from exc
        details = check_contracts(parsed, declarations)
        if details["unresolved_contracts"]:
            raise Incomplete("required asset consumer contracts remain partial or unresolved", details)
        return details

    return write_result(args.output, "assets:consumer-contracts", run, [args.header, args.data, args.contracts])


if __name__ == "__main__":
    raise SystemExit(main())
