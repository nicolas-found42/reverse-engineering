#!/usr/bin/env python3
"""Check finite, ordered endpoint pairs in parser-derived 0x34 geometry rows.

FUN_0021b710 resolves this table; FUN_00122d90 constructs eight corners from
adjacent endpoint pairs at +4/+8, +12/+16 and +20/+24. No game code runs.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import struct

import ps2_sections
import verify_sections
from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result

STRIDE = 52
SOURCE_PAIRS = ((4, 8), (12, 16), (20, 24))
PREVIEW_LIMIT = 20


def inspect_table(data: bytes, table: dict) -> dict:
    """Inspect only a complete, bounded parser-shaped table of 52-byte rows."""
    try:
        offset, count, stride, size, end = (
            table[k] for k in ("offset", "count", "stride", "size", "end")
        )
    except (KeyError, TypeError) as exc:
        raise Invalid("geometry table lacks parser span fields") from exc
    if any(type(v) is not int for v in (offset, count, stride, size, end)):
        raise Invalid("geometry table span fields must be integers")
    if count < 0 or count > ps2_sections.MAX_RECORDS or stride != STRIDE or size != count * STRIDE:
        raise Invalid("geometry table differs from the bounded 52-byte row profile")
    if offset < 0 or offset > len(data) or end != offset + size or size > len(data) - offset:
        raise Invalid("geometry table exceeds input or has inconsistent bounds")
    nonfinite = inverted = zeros = 0
    anomalies = []
    minima: list[float | None] = [None] * 6
    maxima: list[float | None] = [None] * 6
    for index in range(count):
        row_at = offset + index * STRIDE
        values = struct.unpack_from("<6f", data, row_at + 4)
        for word, value in enumerate(values):
            if not math.isfinite(value):
                nonfinite += 1
                if len(anomalies) < PREVIEW_LIMIT:
                    bits = struct.unpack_from("<I", data, row_at + 4 + 4 * word)[0]
                    anomalies.append({"record": index, "source_offset": 4 + 4 * word,
                                      "kind": "nonfinite", "bits": f"0x{bits:08x}"})
            else:
                lo, hi = minima[word], maxima[word]
                minima[word] = value if lo is None else min(lo, value)
                maxima[word] = value if hi is None else max(hi, value)
        for pair in range(3):
            low, high = values[pair * 2:pair * 2 + 2]
            if math.isfinite(low) and math.isfinite(high) and low > high:
                inverted += 1
                if len(anomalies) < PREVIEW_LIMIT:
                    anomalies.append({"record": index, "pair": pair, "kind": "inverted",
                                      "low": low, "high": high})
        zeros += all(value == 0.0 for value in values)
    failures = []
    if nonfinite:
        failures.append(f"{nonfinite} nonfinite geometry endpoint words")
    if inverted:
        failures.append(f"{inverted} geometry endpoint pairs are reversed")
    return {
        "table": table, "source_pairs": [list(p) for p in SOURCE_PAIRS],
        "records_checked": count, "words_checked": count * 6,
        "nonfinite_words": nonfinite, "inverted_pairs": inverted,
        "all_zero_records": zeros, "finite_word_minima": minima, "finite_word_maxima": maxima,
        "anomaly_preview": anomalies, "anomaly_preview_truncated": nonfinite + inverted > len(anomalies),
        "failures": failures,
    }


def check_model(data: bytes, later_profile: str = "loader68") -> dict:
    parsed = ps2_sections.parse(data, later_profile=later_profile)
    return {"sha256": sha256(data), "bytes": len(data), "exact_eof": parsed["exact_eof"],
            "later_profile": parsed["later"]["profile"],
            **inspect_table(data, parsed["geometry"]["table"])}


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    entries = baseline.entries(".ps2;1")
    models, failures, unsupported = [], [], []
    for entry in entries:
        name = entry.path.lstrip("/")
        profile = "measured_legacy60" if (name, entry.sha256) in verify_sections.MEASURED_LEGACY60 else "loader68"
        try:
            result = check_model(entry.load(), profile)
        except Incomplete as exc:
            unsupported.append({"path": name, "reason": str(exc)})
            continue
        except Invalid as exc:
            failures.append({"path": name, "reason": str(exc)})
            continue
        models.append({"path": name, **result})
        failures.extend({"path": name, "reason": reason} for reason in result["failures"])
    if len(entries) != 56:
        unsupported.append({"reason": "archive model count differs from the measured 56-file profile",
                            "observed": len(entries)})
    result = {
        "provenance": baseline.provenance, "models_expected": len(entries),
        "models_checked": len(models), "models_exact_eof": sum(m["exact_eof"] for m in models),
        "profile_counts": {p: sum(m["later_profile"] == p for m in models)
                           for p in ps2_sections.LATER_PROFILES},
        **{k: sum(m[k] for m in models) for k in (
            "records_checked", "words_checked", "nonfinite_words", "inverted_pairs", "all_zero_records")},
        "file_results": models, "failures": failures, "unsupported": unsupported,
        "claim_limits": [
            "Checks three source endpoint pairs only. Coordinate axes, units, vertex containment, planes and renderer semantics remain unproved.",
            "ID zero is rejected by the observed record resolver, but every serialized row is measured, including the first row.",
            "Input finiteness and ordered pairs do not prove finite transformed corners or VU equivalence.",
            "Two SHA-bound legacy profiles are measured structural interpretations, not proven current-loader compatibility.",
        ],
    }
    if unsupported and not failures:
        raise Incomplete("geometry bounds profile prerequisites incomplete", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=("file", "corpus"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/geometry-bounds"))
    parser.add_argument("--later-profile", choices=ps2_sections.LATER_PROFILES, default="loader68")
    args = parser.parse_args()

    def run():
        if args.family == "corpus":
            return check_corpus(args.input)
        if args.input.stat().st_size > ps2_sections.MAX_BYTES:
            raise Invalid("model exceeds section parser processing bound")
        return check_model(args.input.read_bytes(), args.later_profile)

    return write_result(args.output, "geometry-bounds:" + args.family, run,
                        [] if args.family == "corpus" else [args.input])


if __name__ == "__main__":
    raise SystemExit(main())
