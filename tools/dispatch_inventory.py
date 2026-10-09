#!/usr/bin/env python3
"""Join every unlisted executable span and computed-dispatch domain into one bound inventory.

Span classification comes from `verify_text_denominator`, static references from
`verify_text_references`, and switch profiles from `jump_table`. Each span row carries its
measured classification, incoming references, the reason for its disposition, and the
falsifier that would overturn it. Each dispatch row pins a recognized switch (site, table,
count, targets) and whether its whole domain sits inside one span. Code-shaped structure is
not ownership: unreferenced code-shaped spans stay unresolved, never game-owned. No game
code is run.
"""

import argparse
import json
from pathlib import Path

from evidence_common import Invalid, write_result
from jump_table import read_table, recognize
from ps2_executables import parse_elf
from verify_text_denominator import WORD, _unlisted, segments
from verify_text_references import find_span_references


def _executable_words(data: bytes):
    regions = [
        s for s in parse_elf(data)["sections"] if s["type"] == 1 and s["flags"] & 4
    ]
    if not regions:
        for program in parse_elf(data)["programs"]:
            if program["type"] == 1 and program["flags"] & 1 and program["file_size"]:
                regions.append(
                    {
                        "address": program["virtual_address"],
                        "offset": program["offset"],
                        "size": program["file_size"],
                    }
                )

    def get(pc: int) -> int:
        matches = [
            s
            for s in regions
            if s["address"] <= pc and pc + WORD <= s["address"] + s["size"]
        ]
        if len(matches) != 1:
            raise Invalid("dispatch instruction has no unique executable section")
        section = matches[0]
        at = section["offset"] + pc - section["address"]
        return int.from_bytes(data[at : at + WORD], "little")

    return get


def _dispatch_rows(data: bytes, static: dict) -> list[dict]:
    get = _executable_words(data)
    pieces = segments(data, _unlisted(data, static))
    owned = {
        int(row["address"], 16)
        for function in static["functions"]
        for row in function["instructions"]
    }
    rows = []

    def scan(pc: int, floor: int, owner: str | None, span: dict | None) -> None:
        word = get(pc)
        if word >> 26 != 0 or word & 63 != 8 or word == 0x03E00008:
            return
        pin = recognize(get, pc, floor)
        if pin is None:
            return
        try:
            targets = read_table(data, pin["table"], pin["count"])
        except (Invalid, ValueError):
            return
        if span is None:
            domain = "owned" if all(t in owned for t in targets) else "split"
        else:
            lo, hi = span["address"], span["address"] + span["bytes"]
            domain = "single_span" if all(lo <= t < hi for t in targets) else "split"
        rows.append(
            {
                "site": f"{pin['site']:08x}",
                "table": f"{pin['table']:08x}",
                "count": pin["count"],
                "targets": [f"{t:08x}" for t in targets],
                "owner_entry": owner,
                "span": f"{span['address']:08x}" if span else None,
                "domain": domain,
                "guard_site": f"{pin['guard_site']:08x}",
                "falsifier": "a case index that escapes the bound or a table word outside the pinned section",
            }
        )

    for function in static["functions"]:
        floor = int(function["entry"], 16)
        for row in function["instructions"]:
            scan(int(row["address"], 16), floor, function["entry"], None)
    for piece in pieces:
        if piece["kind"] != "code_shaped":
            continue
        for index in range(len(piece["words"])):
            scan(piece["address"] + index * WORD, piece["address"], None, piece)
    return rows


def _span_rows(data: bytes, static: dict) -> list[dict]:
    refs = {row["address"]: row for row in find_span_references(data, static)["spans"]}
    rows = []
    for piece in segments(data, _unlisted(data, static)):
        row = {
            "address": f"{piece['address']:08x}",
            "bytes": piece["bytes"],
            "region": piece["region"],
            "classification": piece["kind"],
        }
        incoming = refs.get(row["address"], {}).get("incoming", {})
        row["incoming"] = incoming
        if piece["kind"] == "code_shaped" and incoming:
            row["disposition"] = "referenced_code_shaped"
            row["reason"] = f"static references {sorted(incoming)} reach this span"
            row["falsifier"] = (
                "a reference re-targeted outside the span or a word re-decoded as data"
            )
        elif piece["kind"] == "code_shaped":
            row["disposition"] = "unresolved"
            row["reason"] = (
                "code-shaped words with no static reference; reachability unknown"
            )
            row["falsifier"] = (
                "a static reference, a recognized dispatch target, or a data-word proof"
            )
        else:
            row["disposition"] = "structural_only"
            row["reason"] = f"classified {piece['kind']} by byte structure alone"
            row["falsifier"] = f"a word re-decoded outside the {piece['kind']} profile"
        rows.append(row)
    return rows


def inventory(data: bytes, static: dict) -> dict:
    details = _unlisted(data, static)
    spans = _span_rows(data, static)
    return {
        "executable_sha256": details["executable_sha256"],
        "inventory_count": details["inventory_count"],
        "spans": spans,
        "dispatches": _dispatch_rows(data, static),
        "summary": {
            "spans": len(spans),
            "unresolved_bytes": sum(
                s["bytes"] for s in spans if s["disposition"] == "unresolved"
            ),
        },
        "whole_game_decompiled": False,
        "claim_limits": [
            "classification and references are structural; ownership, identity and behavior are not established.",
            "code_shaped does not imply game-owned; unreferenced spans stay unresolved.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-export", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path(".scratch/evidence/dispatch-inventory")
    )
    args = parser.parse_args()
    return write_result(
        args.output,
        "dispatch-inventory",
        lambda: inventory(
            args.executable.read_bytes(), json.loads(args.static_export.read_text())
        ),
        [args.static_export, args.executable],
    )


if __name__ == "__main__":
    raise SystemExit(main())
