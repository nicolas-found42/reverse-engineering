#!/usr/bin/env python3
"""Check archive-derived asset families against the fixed PAL consumer registry.

The archive determines file and storage-encoding counts. A pinned repository registry
determines the PAL corpus identity, evidence bindings, and required logical profiles.
Caller declarations may document registry entries but cannot create evidence or scope.

Exit status: 0 complete, 1 contradictory or stale evidence, 2 incomplete evidence.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, write_result
from format_contracts import archive

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "notes/asset-loader-registry.json"
REGISTRY_SHA256 = "c6cdf32442ce95c83aca74910edf952219c42a16367e94a8e455610c8fc5bcad"
MANIFEST_PATH = ROOT / "notes/asset-consumer-contracts.json"


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
        ext: {"file_count": sum(counts.values()), "storage_encodings": dict(sorted(counts.items())),
              "examples": sorted(paths[ext])[:3]}
        for ext, counts in sorted(found.items())
    }


def load_registry() -> dict:
    raw = REGISTRY_PATH.read_bytes()
    observed = hashlib.sha256(raw).hexdigest()
    if observed != REGISTRY_SHA256:
        raise Invalid("fixed asset loader registry digest differs from the reviewed pin")
    try:
        registry = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Invalid(f"invalid fixed registry JSON: {exc}") from exc
    if registry.get("schema_version") != 1:
        raise Invalid("unsupported fixed registry schema")
    sources = registry["corpus_profile"].get("evidence_sources", [])
    for item in [*sources, *registry.get("loader_bindings", [])]:
        source, expected = item.get("path", item.get("source")), item.get("sha256", item.get("source_sha256"))
        if not isinstance(source, str) or not isinstance(expected, str):
            raise Invalid("fixed registry has malformed source pin")
        path = (ROOT / source).resolve()
        if ROOT.resolve() not in path.parents or not path.is_file():
            raise Invalid(f"pinned evidence source is missing from the repository: {source}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise Invalid(f"pinned evidence source SHA-256 mismatch: {source}")
        anchor = item.get("anchor")
        if anchor and anchor not in path.read_text(errors="replace"):
            raise Invalid(f"pinned evidence anchor is absent from source: {source}")
    return registry


def identify_profile(header: Path, data: Path, registry: dict) -> dict | None:
    if header.parent.name != "extracted" or data.parent != header.parent:
        return None
    game = header.parent.parent
    try:
        observed = corpus_identity(game)
    except FileNotFoundError:
        return None
    expected = registry["corpus_profile"]
    if observed.get("profile") != expected.get("id"):
        raise Invalid("corpus profile differs from the fixed asset registry")
    if observed.get("corpus_id") != expected.get("corpus_id") or observed.get("sources") != expected.get("inputs"):
        raise Invalid("corpus identity differs from the fixed asset registry")
    return observed


def validate_declarations(actual: dict, declarations: dict, registry: dict, active_profile: dict | None) -> dict:
    if declarations.get("schema_version") != 1 or declarations.get("registry") != "notes/asset-loader-registry.json":
        raise Invalid("caller manifest must point to the fixed registry")
    declared = declarations.get("contracts")
    required = registry.get("contracts")
    if not isinstance(declared, list) or not isinstance(required, list):
        raise Invalid("manifest and registry contracts must be arrays")
    by_id = {item.get("id"): item for item in declared if isinstance(item, dict)}
    registry_by_id = {item.get("id"): item for item in required}
    errors = []
    if len(by_id) != len(declared) or set(by_id) != set(registry_by_id):
        errors.append("caller manifest must declare every registry contract exactly once")

    bindings_by_contract = defaultdict(list)
    for binding in registry.get("loader_bindings", []):
        bindings_by_contract[binding["contract_id"]].append(binding)
    resolved_contracts, unresolved_contracts, all_bindings = [], [], []
    pinned_sources = {item.get("path", item.get("source")) for item in registry["corpus_profile"].get("evidence_sources", [])}
    pinned_sources.update(item.get("path", item.get("source")) for item in registry.get("loader_bindings", []))
    active_id = active_profile.get("profile") if active_profile else None
    for ident, authority in registry_by_id.items():
        supplied = by_id.get(ident)
        if supplied is None:
            continue
        allowed = {"id", "asset_types", "extensions", "status", "binding_ids", "consumer_contract", "structure_evidence", "limits"}
        unexpected = set(supplied) - allowed
        if unexpected:
            errors.append(f"{ident}: caller manifest contains non-authoritative fields: {', '.join(sorted(unexpected))}")
        for field in ("asset_types", "extensions"):
            if supplied.get(field) != authority.get(field):
                errors.append(f"{ident}: {field} differs from the fixed registry")
        expected_bindings = sorted(item["id"] for item in bindings_by_contract[ident])
        given_bindings = supplied.get("binding_ids")
        if not isinstance(given_bindings, list) or sorted(given_bindings) != expected_bindings:
            errors.append(f"{ident}: binding_ids differ from the fixed registry")
        if supplied.get("status") != authority.get("status"):
            errors.append(f"{ident}: status differs from the fixed registry")
        if supplied.get("status") == "complete" and authority.get("status") != "complete":
            errors.append(f"{ident}: caller cannot promote a candidate or unresolved registry contract")
        logical_profiles = authority.get("profiles", [])
        for profile in logical_profiles:
            if not isinstance(profile.get("evidence_sources"), list) or any(source not in pinned_sources for source in profile["evidence_sources"]):
                errors.append(f"{ident}: logical profile {profile.get('id')} cites evidence outside the fixed profile pins")
        unresolved = [p for p in logical_profiles if p.get("disposition") != "accepted"]
        bindings = []
        for item in bindings_by_contract[ident]:
            bound = dict(item)
            bound["active_corpus_profile"] = item.get("profile_id") == active_id
            bound["evidence_disposition"] = item.get("disposition")
            bindings.append(bound)
            all_bindings.append(bound)
        complete = (supplied.get("status") == "complete" and not unresolved and active_id is not None
                    and all(item["active_corpus_profile"] and item["evidence_disposition"] == "accepted" for item in bindings))
        if not complete:
            unresolved_contracts.append(ident)
        resolved_contracts.append({
            "id": ident,
            "asset_types": authority["asset_types"],
            "extensions": authority["extensions"],
            "status": authority["status"],
            "loader_bindings": bindings,
            "required_logical_profiles": logical_profiles,
            "unresolved_profiles": unresolved,
        })

    expected_extensions = {ext for item in required for ext in item["extensions"]}
    missing_extensions = sorted(set(actual) - expected_extensions)
    if missing_extensions:
        errors.append("archive extensions are absent from the fixed registry: " + ", ".join(missing_extensions))
    active_profile_match = active_id == registry["corpus_profile"]["id"]
    if active_profile is not None and not active_profile_match:
        errors.append("active corpus profile is not the registry profile")
    if errors:
        raise Invalid("; ".join(errors), {"catalog": actual, "contracts": resolved_contracts})
    return {
        "registry_sha256": REGISTRY_SHA256,
        "corpus_profile": active_id,
        "corpus_profile_matches_registry": active_profile_match,
        "catalog": actual,
        "contracts": resolved_contracts,
        "candidate_loader_bindings": [item for item in all_bindings if item["evidence_disposition"] != "accepted"],
        "unresolved_contracts": unresolved_contracts,
        "unresolved_logical_profiles": [
            {"contract_id": item["id"], "asset_type": profile["asset_type"], "profile_id": profile["id"],
             "disposition": profile["disposition"]}
            for item in resolved_contracts for profile in item["unresolved_profiles"]
        ],
        "complete": not unresolved_contracts and active_profile_match,
        "claim_limits": registry["claim_limits"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["archive"])
    parser.add_argument("header", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("--contracts", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/asset-contracts"))
    args = parser.parse_args()

    def run():
        registry = load_registry()
        parsed = archive(args.header.read_bytes(), args.data.read_bytes())
        try:
            declarations = json.loads(args.contracts.read_text())
        except json.JSONDecodeError as exc:
            raise Invalid(f"invalid caller manifest JSON: {exc}") from exc
        profile = identify_profile(args.header.resolve(), args.data.resolve(), registry)
        details = validate_declarations(catalog(parsed), declarations, registry, profile)
        if not details["complete"]:
            raise Incomplete("fixed registry contains candidate or unresolved consumer profiles", details)
        return details

    return write_result(args.output, "assets:consumer-contracts", run, [args.header, args.data, args.contracts, REGISTRY_PATH])


if __name__ == "__main__":
    raise SystemExit(main())
