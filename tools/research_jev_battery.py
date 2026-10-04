#!/usr/bin/env python3
"""Rerun a source-bound TypeSafe research battery (screen sources beforehand).

Run with typesafe-sdk==0.7.2 and OPENROUTER_API_KEY supplied by the environment.
The fixture contains expected outcomes for evaluation; they never enter model state.
"""
import argparse
import importlib.metadata
import json
import math
import os
import time
from pathlib import Path

from typesafe_sdk import Choice, Noul, TypeSafeClient


def run(fixture, output):
    cases = json.loads(fixture.read_text())
    results = []
    with TypeSafeClient(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api",
        timeout=60,
    ) as client:
        for case in cases:
            if case["intake"] not in {"pass", "review_inspected"}:
                raise ValueError(f"Source not cleared for {case['id']}")
            questions = {
                "relation": Choice(
                    instructions="How does `source` relate to `claim`? Judge ONLY supplied evidence, not outside knowledge. Missing details are silence, not contradiction.",
                    criteria={
                        "supports": "The source explicitly states or directly implies the claim.",
                        "contradicts": "The source explicitly states or directly implies the opposite for the same subject.",
                        "says_nothing": "The source does not establish the claim or its opposite.",
                    },
                ),
                "ps2_validation": Noul(
                    instructions="Does `source` explicitly report empirical validation of the discussed method on PlayStation 2 Emotion Engine R5900 game executables? Generic MIPS support or a debugger targeting R5900 is not an empirical evaluation.",
                ),
                "overreach": Noul(
                    instructions="Does `claim` add an architecture, performance, automation, or capability assertion that `source` does not support? Judge only supplied evidence.",
                ),
            }
            started = time.perf_counter()
            try:
                response = client.system_one(
                    state={"source": case["source"], "claim": case["claim"]},
                    questions=questions,
                    model="typesafe/jev-1.13",
                )
                answer = response.answers["relation"]
                probabilities = answer.probabilities
                assert set(probabilities) == {"supports", "contradicts", "says_nothing"}
                assert all(math.isfinite(v) and 0 <= v <= 1 for v in probabilities.values())
                assert abs(sum(probabilities.values()) - 1) <= 0.02
                assert answer.choice in probabilities
                assert math.isfinite(answer.confidence) and 0 <= answer.confidence <= 1
                for question in ["ps2_validation", "overreach"]:
                    value = response.answers[question].noul
                    assert math.isfinite(value) and 0 <= value <= 1
                result = {
                    "id": case["id"], "source_url": case["source_url"],
                    "claim": case["claim"], "expected": case["expected"],
                    "seconds": round(time.perf_counter() - started, 3),
                    "response": response.model_dump(mode="json"),
                    "matches_expected": answer.choice == case["expected"],
                    "action": "auto" if answer.confidence >= 0.8 else "review",
                }
            except Exception as exc:
                # Record the failure class, never credentials or request headers.
                result = {"id": case["id"], "error_type": type(exc).__name__, "matches_expected": False, "action": "invalid_response"}
            results.append(result)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps({"sdk_version": importlib.metadata.version("typesafe-sdk"), "results": results}, indent=2) + "\n")
            print(json.dumps({key: result[key] for key in ["id", "matches_expected", "action"]}), flush=True)
    summary = {
        "cases": len(results),
        "matches_expected": sum(r["matches_expected"] for r in results),
        "review": sum(r["action"] == "review" for r in results),
        "invalid": sum(r["action"] == "invalid_response" for r in results),
        "questions": 3 * len(results),
        "input_tokens": sum(r.get("response", {}).get("usage", {}).get("input_tokens", 0) or 0 for r in results),
        "output_tokens": sum(r.get("response", {}).get("usage", {}).get("output_tokens", 0) or 0 for r in results),
    }
    output.write_text(json.dumps({"sdk_version": importlib.metadata.version("typesafe-sdk"), "summary": summary, "results": results}, indent=2) + "\n")
    print(json.dumps(summary), flush=True)
    return 0 if summary["matches_expected"] == summary["cases"] and not summary["invalid"] and not summary["review"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.fixture, args.output))
