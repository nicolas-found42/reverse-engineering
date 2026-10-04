#!/usr/bin/env python3
"""Verify complete Ghidra inventory and instruction-backed loader evidence."""

import argparse
import json
from pathlib import Path
from corpus_contract import corpus_identity
from evidence_common import Invalid, Incomplete, identity, write_result
from format_contracts import require
from judgment_contract import accepted

STAGES = {
    "initialization",
    "lookup",
    "chunk_read",
    "raw_transfer",
    "decompression",
    "consumption",
}


def verify(
    export_path: Path, map_path: Path, executable: Path, game: Path, synthetic=False
):
    export = json.loads(export_path.read_text())
    mapping = json.loads(map_path.read_text())
    digest = identity(executable)["sha256"]
    if not synthetic or "export_sha256" in mapping:
        require(
            mapping["export_sha256"] == identity(export_path)["sha256"],
            "stale loader map/export pairing",
        )
    require(
        export["schema_version"] == mapping["schema_version"] == 1,
        "unknown static schema version",
    )
    require(
        export["executable_sha256"] == mapping["executable_sha256"] == digest,
        "stale executable identity",
    )
    require(
        export["program"] == "SLES_517.05"
        and export["language"] == "r5900:LE:32:default",
        "unexpected program/language",
    )
    functions = {f["entry"]: f for f in export["functions"]}
    require(
        len(functions) == len(export["functions"]) == export["inventory_count"] > 0,
        "omitted or duplicate function inventory",
    )
    require(
        bool(export["memory"])
        and "strings" in export
        and bool(export["ghidra_version"]),
        "missing memory/string/tool inventory",
    )
    stages = {s["stage"]: s for s in mapping["stages"]}
    if set(stages) != STAGES or len(stages) != len(mapping["stages"]):
        raise Incomplete("missing required loader stages")
    provenance = {} if synthetic else corpus_identity(game)
    if not synthetic:
        require(mapping["provenance"] == provenance, "stale loader-map corpus identity")
    details = {
        "function_count": len(functions),
        "inventory_sha256": identity(export_path)["sha256"],
        "loader_map_sha256": identity(map_path)["sha256"],
        "stages": list(stages.values()),
        "provenance": provenance,
        "synthetic": synthetic,
        "milestone_eligible": not synthetic,
        "tools": {"ghidra": export["ghidra_version"]},
        "decompiler": export.get("decompiler", "not used"),
    }
    resolutions = {}
    review = {}
    if mapping.get("reasoner_review"):
        artifact = mapping["reasoner_review"]
        path = map_path.parent / artifact["path"]
        require(
            identity(path) == artifact["identity"], "changed reasoner review artifact"
        )
        review = json.loads(path.read_text())
        require(
            review["inputs"]["export_sha256"] == identity(export_path)["sha256"]
            and review["inputs"]["executable_sha256"] == digest,
            "stale reasoner review evidence",
        )
        require(bool(review["reviewer"]), "missing reasoner identity")
        resolutions = {item["claim"]: item for item in review["stages"]}
    audits = []
    for artifact in mapping.get("judgment_audits", []):
        path = map_path.parent / artifact["path"]
        require(
            identity(path) == artifact["identity"], "changed judgment audit artifact"
        )
        audit = json.loads(path.read_text())
        result = json.loads(audit["result"]["content"][0]["text"])
        require(result["tool"] == "jev_verify", "wrong judgment audit tool")
        audits.append(result)
    if not synthetic:
        require(bool(audits), "missing full Jev inputs/results")
        if resolutions:
            require(
                {a["identity"]["sha256"] for a in mapping["judgment_audits"]}
                == {a["sha256"] for a in review["inputs"]["jeV_audits"]},
                "reasoner review binds different Jev audits",
            )
        correlation = mapping["runtime_correlation"]
        correlation_path = map_path.parent / correlation["path"]
        require(
            identity(correlation_path) == correlation["identity"],
            "changed archive/runtime correlation",
        )
    unresolved = []
    for stage in stages.values():
        if stage["disposition"] != "accepted" or not stage["evidence"]:
            unresolved.append(stage["stage"])
        for item in stage["evidence"]:
            function = functions.get(item["function"])
            if function is None:
                raise Invalid("loader function missing from inventory")
            matches = [
                i
                for i in function["instructions"]
                if i["address"] == item["address"] and i["bytes"] == item["bytes"]
            ]
            require(
                len(matches) == 1,
                f"instruction evidence absent/changed: {item['address']}",
            )
        if not synthetic or "judgment" in stage:
            judgment = stage.get("judgment")
            if judgment is None:
                unresolved.append(stage["stage"])
                continue
            if not synthetic:
                require(
                    any(judgment in audit["results"] for audit in audits),
                    "judgment does not match retained Jev output",
                )
            require(
                bool(stage["claim"]) and bool(stage["correlation"]),
                "missing claim/archive correlation",
            )
            try:
                accepted(judgment, stage["claim"], resolutions.get(stage["claim"]))
            except Incomplete:
                unresolved.append(stage["stage"])
    if not synthetic:
        for audit in audits:
            for judgment in audit["results"]:
                if judgment["claim"] in {s["claim"] for s in stages.values()}:
                    try:
                        accepted(
                            judgment,
                            judgment["claim"],
                            resolutions.get(judgment["claim"]),
                        )
                    except Incomplete:
                        unresolved.extend(
                            s["stage"]
                            for s in stages.values()
                            if s["claim"] == judgment["claim"]
                        )
    if unresolved:
        details["unresolved_stages"] = sorted(set(unresolved))
        raise Incomplete(
            "unresolved loader stages: " + ", ".join(details["unresolved_stages"]),
            details,
        )
    return details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--loader-map", type=Path)
    parser.add_argument("--game", type=Path, default=Path("games/ford-racing-2"))
    parser.add_argument("--executable", type=Path)
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="contract fixtures only; never eligible for milestone acceptance",
    )
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/static"))
    args = parser.parse_args()
    executable = args.executable or args.game / "extracted/SLES_517.05"

    def run():
        if args.export is None or args.loader_map is None:
            raise Incomplete("missing --export or --loader-map")
        return verify(
            args.export, args.loader_map, executable, args.game, args.synthetic
        )

    return write_result(
        args.output,
        "static",
        run,
        [p for p in [args.export, args.loader_map, executable] if p is not None],
    )


if __name__ == "__main__":
    raise SystemExit(main())
