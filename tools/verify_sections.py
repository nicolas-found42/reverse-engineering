#!/usr/bin/env python3
"""Offline FR2 model section-chain verifier: 0=pass, 1=fail, 2=incomplete.

Corpus completeness is bound to the independent archive manifest. A file outside
the measured later-header profile keeps the full corpus result incomplete.
"""
import argparse
from pathlib import Path

import ps2_sections
from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result

UNRESOLVED = [
    "Brands and Canyon match a measured 60-byte legacy header profile by pinned SHA-256 and exact EOF; the current FUN_0011ed90 disassembly does not show the loader selecting that profile, so executable compatibility remains unverified",
    "semantic names, index/vertex/texture relationships, finite geometry floats, bounding boxes and VU consumers",
    "pixel decoding limits from the separate texture verifier still apply",
    "source reconstruction, recompilation, runtime equivalence and owner render observations",
]

MEASURED_LEGACY60 = {
    ("3DDATA/TRACKS/Brands.PS2;1", "0b6235f545e870c7237a256952f4ab1ee261528ab466b2d403e9fb393b31fbb8"),
    ("3DDATA/TRACKS/Canyon.PS2;1", "bf689b86a426489f84e24a250a5fb26ea1655bcaba907f17769ba4d601ed5f48"),
}


def check_model(data: bytes, later_profile: str = "loader68") -> dict:
    parsed = ps2_sections.parse(data, later_profile=later_profile)
    geo, later, tail = parsed["geometry"], parsed["later"], parsed["tail"]
    return {
        "bytes": len(data), "sha256": sha256(data), "exact_eof": parsed["exact_eof"],
        "later_profile": later["profile"], "later_header": later["global_header"],
        "geometry_records": geo["table"]["count"], "geometry_headers": geo["header_count"],
        "section_offsets": {"textures": parsed["textures"]["section_start"],
                            "geometry": geo["section_start"], "geometry_payload": geo["payload_start"],
                            "later": later["section_start"], "tail": tail["section_start"],
                            "logical_end": tail["logical_end"], "end": parsed["end"]},
        "later_records": len(later["records"]), "node_counts": later["node_counts"],
        "tail_rows": len(tail["rows"]), "tail_records": len(tail["records"]),
        "final_padding": tail["padding"], "unresolved": UNRESOLVED,
    }


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    expected = baseline.entries(".ps2;1")
    models, failures, unsupported = [], [], []
    for entry in expected:
        name = entry.path.lstrip("/")
        profile = "measured_legacy60" if (name, entry.sha256) in MEASURED_LEGACY60 else "loader68"
        try:
            data = entry.load()
            result = check_model(data, later_profile=profile)
        except Incomplete as exc:
            unsupported.append({"path": name, "reason": str(exc), "details": exc.details})
            continue
        except Invalid as exc:
            failures.append(f"{name}: {exc}")
            continue
        models.append({"path": name, **result})
    profiles = {name: sum(model["later_profile"] == name for model in models)
                for name in ps2_sections.LATER_PROFILES}
    details = {"provenance": baseline.provenance, "models": len(expected),
               "exact_eof_models": len(models), "file_results": models,
               "profile_counts": profiles,
               "unsupported": unsupported, "failures": failures, "unresolved": UNRESOLVED,
               "claim_limits": "Exact byte consumption for listed models under explicit loader68 or SHA-256-bound measured_legacy60 structural profiles, including checked final zero alignment. The measured_legacy60 profile is not evidence that the current executable loader supports/selects it. No geometry interpretation or full-game decompilation claim."}
    if unsupported and not failures:
        raise Incomplete(f"{len(unsupported)} of {len(expected)} models lack a supported later-header profile", details)
    return details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=["file", "corpus"])
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/sections"))
    parser.add_argument("--later-profile", choices=ps2_sections.LATER_PROFILES, default="loader68",
                        help="file mode only; corpus mode selects the two measured legacy files by SHA-256")
    args = parser.parse_args()

    def run():
        if args.family == "corpus":
            return check_corpus(args.input)
        if args.input.stat().st_size > ps2_sections.MAX_BYTES:
            raise Invalid("model exceeds section parser processing bound")
        return check_model(args.input.read_bytes(), later_profile=args.later_profile)

    return write_result(args.output, "sections:" + args.family, run,
                        [] if args.family == "corpus" else [args.input])


if __name__ == "__main__":
    raise SystemExit(main())
