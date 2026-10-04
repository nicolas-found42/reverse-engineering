"""Fail-closed policy for retained semantic decisions, separate from deterministic facts."""

import math

from evidence_common import Incomplete, Invalid
from format_contracts import require


def accepted(judgment: dict, claim: str, resolution: dict | None = None):
    require(judgment.get("claim") == claim, "judgment does not bind the required claim")
    probabilities = judgment.get("probabilities", {})
    require(
        set(probabilities) == {"supports", "contradicts", "says_nothing"},
        "malformed judgment distribution",
    )
    require(
        all(
            type(p) in {int, float} and math.isfinite(p) and 0 <= p <= 1
            for p in probabilities.values()
        ),
        "malformed judgment probabilities",
    )
    require(
        abs(sum(probabilities.values()) - 1) <= 0.02,
        "judgment probabilities do not sum to one",
    )
    require(
        judgment.get("verdict") in {"verified", "unsupported", "contradicted"},
        "malformed judgment verdict",
    )
    require(judgment.get("action") in {"auto", "review"}, "malformed judgment action")
    confidence = judgment.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise Invalid("malformed judgment confidence")
    require(
        math.isfinite(confidence) and 0 <= confidence <= 1,
        "malformed judgment confidence",
    )
    if judgment["verdict"] == "contradicted":
        require(False, "required claim contradicted by judgment")
    if (
        judgment["verdict"] != "verified"
        or judgment["action"] != "auto"
        or confidence < 0.8
        or probabilities["supports"] < 0.8
    ):
        if resolution is None:
            raise Incomplete(
                "required semantic judgment needs review; it is not automatic approval"
            )
        require(resolution.get("claim") == claim, "reasoner review does not bind claim")
        if resolution.get("verdict") != "accepted" or not resolution.get("rationale"):
            raise Incomplete("required semantic reasoner review is unresolved")
    return True
