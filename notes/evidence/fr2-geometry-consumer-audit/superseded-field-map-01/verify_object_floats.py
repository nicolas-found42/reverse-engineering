#!/usr/bin/env python3
"""Measure finite binary32 fields in parser-derived serialized 0x20-byte rows.

The four offsets are tied to the FUN_0011ed90 writer/consumer trace. This tool
does not assign a geometry meaning to the rows or execute game code.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import struct

import ps2_sections
import verify_sections
from corpus_binding import Baseline
from evidence_common import Incomplete, Invalid, sha256, write_result

ROW_STRIDE = 0x20
MAX_ROWS = 1_000_000
FIELDS = (
    {"source_offset": 0x04, "runtime_offset": 0x0C},
    {"source_offset": 0x08, "runtime_offset": 0x10},
    {"source_offset": 0x0C, "runtime_offset": 0x14},
    {"source_offset": 0x10, "runtime_offset": 0x18},
)
ANOMALY_PREVIEW = 20
MEASURED_MODEL_COUNT = 56


def _validate_span(data: bytes, span: dict) -> tuple[int, int, int]:
    """Reject spans not exactly shaped/bounded as parser-produced 32-byte rows."""
    try:
        offset, count, stride, size, end = (
            span["offset"], span["count"], span["stride"], span["size"], span["end"]
        )
    except (KeyError, TypeError) as exc:
        raise Invalid("expanded_24 row span is missing parser fields") from exc
    values = (offset, count, stride, size, end)
    if any(type(value) is not int for value in values):
        raise Invalid("expanded_24 row span fields must be integers")
    if count < 0 or count > MAX_ROWS:
        raise Invalid(f"expanded_24 row count {count} exceeds the bounded profile")
    if stride != ROW_STRIDE or size != count * ROW_STRIDE:
        raise Invalid("expanded_24 span does not have the parser's 32-byte row shape")
    if offset < 0 or end != offset + size or offset > len(data) or size > len(data) - offset:
        raise Invalid("expanded_24 row span exceeds the input or has inconsistent bounds")
    return offset, count, stride


def inspect_span(data: bytes, span: dict) -> dict:
    """Measure the four mapped fields in one parser-derived serialized row span."""
    offset, count, _ = _validate_span(data, span)
    fields = []
    for spec in FIELDS:
        source_offset = spec["source_offset"]
        finite_count = nan_count = posinf_count = neginf_count = 0
        minimum = maximum = None
        anomalies = []
        for row_index in range(count):
            at = offset + row_index * ROW_STRIDE + source_offset
            bits = struct.unpack_from("<I", data, at)[0]
            exponent, fraction = (bits >> 23) & 0xFF, bits & 0x7FFFFF
            if exponent == 0xFF:
                kind = "nan" if fraction else ("-inf" if bits >> 31 else "+inf")
                if kind == "nan":
                    nan_count += 1
                elif kind == "+inf":
                    posinf_count += 1
                else:
                    neginf_count += 1
                if len(anomalies) < ANOMALY_PREVIEW:
                    anomalies.append({"row": row_index, "file_offset": at,
                                      "bits": f"0x{bits:08x}", "kind": kind})
                continue
            value = struct.unpack_from("<f", data, at)[0]
            finite_count += 1
            minimum = value if minimum is None else min(minimum, value)
            maximum = value if maximum is None else max(maximum, value)
        fields.append({
            **spec,
            "values_checked": count,
            "finite": finite_count,
            "nan": nan_count,
            "positive_infinity": posinf_count,
            "negative_infinity": neginf_count,
            "nonfinite": nan_count + posinf_count + neginf_count,
            "finite_min": minimum,
            "finite_max": maximum,
            "anomaly_preview": anomalies,
            "anomaly_preview_truncated": nan_count + posinf_count + neginf_count > len(anomalies),
        })
    return {
        "span": {"offset": offset, "exclusive_end": offset + count * ROW_STRIDE,
                 "count": count, "stride": ROW_STRIDE, "size": count * ROW_STRIDE},
        "rows": count,
        "fields_checked": count * len(FIELDS),
        "finite": sum(f["finite"] for f in fields),
        "nan": sum(f["nan"] for f in fields),
        "positive_infinity": sum(f["positive_infinity"] for f in fields),
        "negative_infinity": sum(f["negative_infinity"] for f in fields),
        "nonfinite": sum(f["nonfinite"] for f in fields),
        "fields": fields,
    }


def check_model(data: bytes, later_profile: str = "loader68") -> dict:
    """Parse one complete model, then inspect only its four mapped row fields."""
    parsed = ps2_sections.parse(data, later_profile=later_profile)
    spans = [record["expanded_24"] for record in parsed["later"]["records"]]
    results = [inspect_span(data, span) for span in spans]
    fields = []
    for index, spec in enumerate(FIELDS):
        parts = [result["fields"][index] for result in results]
        finite_min = [part["finite_min"] for part in parts if part["finite_min"] is not None]
        finite_max = [part["finite_max"] for part in parts if part["finite_max"] is not None]
        fields.append({
            **spec,
            "values_checked": sum(p["values_checked"] for p in parts),
            "finite": sum(p["finite"] for p in parts),
            "nan": sum(p["nan"] for p in parts),
            "positive_infinity": sum(p["positive_infinity"] for p in parts),
            "negative_infinity": sum(p["negative_infinity"] for p in parts),
            "nonfinite": sum(p["nonfinite"] for p in parts),
            "finite_min": min(finite_min) if finite_min else None,
            "finite_max": max(finite_max) if finite_max else None,
        })
    result = {
        "bytes": len(data),
        "sha256": sha256(data),
        "later_profile": parsed["later"]["profile"],
        "exact_eof": parsed["exact_eof"],
        "serialized_row_span_count": len(spans),
        "rows": sum(item["rows"] for item in results),
        "fields_checked": sum(item["fields_checked"] for item in results),
        "finite": sum(item["finite"] for item in results),
        "nan": sum(item["nan"] for item in results),
        "positive_infinity": sum(item["positive_infinity"] for item in results),
        "negative_infinity": sum(item["negative_infinity"] for item in results),
        "nonfinite": sum(item["nonfinite"] for item in results),
        "fields": fields,
        "nonfinite_spans": [
            {"span": item["span"], "fields": [field for field in item["fields"] if field["nonfinite"]]}
            for item in results if item["nonfinite"]
        ],
    }
    result["failures"] = [
        f"{item['nonfinite']} non-finite mapped float fields in serialized row span at {item['span']['offset']:#x}"
        for item in results if item["nonfinite"]
    ]
    return result


def check_corpus(game: Path) -> dict:
    baseline = Baseline(game)
    expected = baseline.entries(".ps2;1")
    models, failures, unsupported = [], [], []
    for entry in expected:
        name = entry.path.lstrip("/")
        profile = "measured_legacy60" if (name, entry.sha256) in verify_sections.MEASURED_LEGACY60 else "loader68"
        try:
            data = entry.load()
            result = check_model(data, later_profile=profile)
        except Incomplete as exc:
            unsupported.append({"path": name, "reason": str(exc), "details": exc.details})
            continue
        except Invalid as exc:
            failures.append({"path": name, "reason": str(exc), "details": exc.details})
            continue
        models.append({"path": name, **result})
        failures.extend({"path": name, "reason": reason} for reason in result["failures"])
    if len(expected) != MEASURED_MODEL_COUNT:
        unsupported.append({"reason": "archive-pinned model count differs from the measured 56-file set",
                            "expected": MEASURED_MODEL_COUNT, "observed": len(expected)})
    fields = []
    for index, spec in enumerate(FIELDS):
        parts = [model["fields"][index] for model in models]
        minima = [p["finite_min"] for p in parts if p["finite_min"] is not None]
        maxima = [p["finite_max"] for p in parts if p["finite_max"] is not None]
        fields.append({
            **spec,
            "values_checked": sum(p["values_checked"] for p in parts),
            "finite": sum(p["finite"] for p in parts),
            "nan": sum(p["nan"] for p in parts),
            "positive_infinity": sum(p["positive_infinity"] for p in parts),
            "negative_infinity": sum(p["negative_infinity"] for p in parts),
            "nonfinite": sum(p["nonfinite"] for p in parts),
            "finite_min": min(minima) if minima else None,
            "finite_max": max(maxima) if maxima else None,
        })
    totals = {key: sum(model[key] for model in models)
              for key in ("rows", "fields_checked", "finite", "nan", "positive_infinity",
                          "negative_infinity", "nonfinite")}
    details = {
        "provenance": baseline.provenance,
        "models_expected": len(expected),
        "models_checked": len(models),
        "models_exact_eof": sum(model["exact_eof"] for model in models),
        "profile_counts": {profile: sum(m["later_profile"] == profile for m in models)
                           for profile in ps2_sections.LATER_PROFILES},
        **totals,
        "fields": fields,
        "file_results": models,
        "failures": failures,
        "unsupported": unsupported,
        "claim_limits": [
            "Fields are checked only in parser-derived expanded_24 spans with serialized stride 32; no row or plane semantics are inferred.",
            "Finite binary32 inputs do not prove finite VU0 outputs, runtime behavior, or renderer submission.",
            "Corpus membership and bytes are bound to the independent archive baseline; 60-byte legacy profile files remain structural measurements, not proven current-loader compatibility.",
        ],
    }
    if unsupported and not failures:
        raise Incomplete(f"{len(unsupported)} model/profile prerequisites are unsupported", details)
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=("file", "corpus"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".scratch/evidence/object-floats"))
    parser.add_argument("--later-profile", choices=ps2_sections.LATER_PROFILES, default="loader68",
                        help="file mode only; corpus mode selects SHA-256-bound measured legacy profiles")
    args = parser.parse_args()

    def run():
        if args.family == "corpus":
            return check_corpus(args.input)
        if args.input.stat().st_size > ps2_sections.MAX_BYTES:
            raise Invalid("model exceeds section parser processing bound")
        return check_model(args.input.read_bytes(), args.later_profile)

    inputs = [] if args.family == "corpus" else [args.input]
    return write_result(args.output, "object-float:" + args.family, run, inputs)


if __name__ == "__main__":
    raise SystemExit(main())
