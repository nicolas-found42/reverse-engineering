#!/usr/bin/env python3
"""Retain the fixed PAL RPC candidate frontier; parent stays incomplete."""

import argparse
import json
import struct
from pathlib import Path
from check_rpc_contracts import EE_TARGETS, PARENT_GAPS, PROFILE, scan_calls
from evidence_common import Incomplete, Invalid, sha256, write_result
from iop_symbols import read_symbols
from ps2_executables import parse_romdir
from ps2_irx import parse_irx
from rpc_handoffs import (
    decode_bind_sites,
    decode_call_sites,
    decode_register_sites,
    jal_target,
    join_handoffs,
)

PINS_PATH = (
    Path(__file__).resolve().parents[1]
    / "notes/evidence/fr2-iop-export-recovery/index.json"
)

STREAM_CONTRACT = {
    "service_id": 0x12345,
    "module": "STREAM.IRX",
    "handler": "ProcessEECommand",
    "handler_address": 0xD410,
    "dispatch_command": 0,
    "consumer": "AdpcmSetParam",
    "consumer_address": 0x11D44,
    "record": {
        "transfer_bytes": 0x800,
        "version": 62,
        "layout": "version:u16, count:i16, records(command:u16, length:i16, args:length*u16)",
    },
    "shared_objects": {
        "rpc_arg": {"size": 0x800},
        "aret": {"size": 0x800},
        "StreamBuffer": {"size": 26304, "stride": 0x224, "slots": 48},
    },
    "ownership": "EE owns the addresses of its static staging/send/reply buffers in the static image; "
    "IOP symbol objects live in the separate IOP image; transfer is EE-to-IOP for the request "
    "and IOP-to-EE for the reply; actual ownership duration is unobserved",
    "synchronization": "EE checks the client status before reuse with caller-supplied mode; "
    "the IOP dispatcher can sleep when MS_IntrFlag is set and later signals gSem; "
    "the interrupt wakeup chain, callback extent and simultaneous callers are unresolved",
    "outputs": "command 0 routes to AdpcmSetParam and returns aret; full reply fields are not recovered; "
    "subcommand 2 passes three halfwords to SOUND_SetChannelVolume with a trailing zero; "
    "other subcommands stay incomplete",
    "runtime": {
        "registration": "unobserved",
        "load_base": None,
        "registration_order": "unobserved",
    },
}


def _jal_sites_to(data: bytes, targets: set) -> list[int]:
    """List .text addresses holding a JAL word to one of the target addresses."""
    from ps2_executables import parse_elf

    sites = []
    for section in parse_elf(data)["sections"]:
        if section["type"] != 1 or not section["flags"] & 4:
            continue
        for offset in range(0, section["size"], 4):
            at = section["address"] + offset
            word = struct.unpack_from("<I", data, section["offset"] + offset)[0]
            target = jal_target(at, word)
            if target is not None and target in targets:
                sites.append(at)
    return sites


def derive_handoffs(ee: bytes | None, payloads: dict) -> list[dict]:
    """Join decoded EE caller groups to IOP registrations by service id.

    A bound row additionally carries the evidenced STREAM record contract;
    a row whose handler address has no symbol binding, or a name-only or
    unbound shared buffer, stays incomplete or unresolved. Actual load
    bases and registration order stay unobserved.
    """
    binds, calls = [], []
    if ee is not None:
        for row in scan_calls(ee, EE_TARGETS)["direct_candidates"]:
            if row["domain"] == "bind-candidate":
                binds += decode_bind_sites(ee, row["site"])
            else:
                calls += decode_call_sites(ee, row["site"])
    registers = []
    stream_symbols: dict = {}
    for name, data in payloads.items():
        try:
            symbols = {s["name"]: s for s in read_symbols(data)}
        except Exception:
            continue
        stubs = {
            s["value"]: s["name"]
            for s in symbols.values()
            if s["name"].startswith("sceSif")
        }
        if name == "STREAM.IRX":
            stream_symbols = symbols
        register_stubs = set()
        for table in parse_irx(data)["imports"]:
            if table["library"] not in ("sifcmd", "sifman"):
                continue
            for link in table["links"]:
                if stubs.get(link["stub_text_offset"], "") == "sceSifRegisterRpc":
                    register_stubs.add(link["stub_text_offset"])
        if register_stubs:
            for site in _jal_sites_to(data, register_stubs):
                for row in decode_register_sites(data, site):
                    if "status" not in row:
                        registers.append({**row, "module": name})
    handoffs = join_handoffs(binds, calls, registers)
    for row in handoffs:
        if row.get("status") != "bound":
            continue
        if row.get("module") != "STREAM.IRX":
            row["status"] = "unresolved"
            row["reason"] = (
                "registration module is outside the evidenced STREAM dispatch domain"
            )
            continue
        handler_name = next(
            (
                n
                for n, s in stream_symbols.items()
                if s["value"] == row.get("handler") and s["type"] == 2
            ),
            None,
        )
        if handler_name is None:
            row["status"] = "unresolved"
            row["reason"] = "handler address carries no symbol binding"
            continue
        row["handler_name"] = handler_name
        if (
            row.get("service_id") == STREAM_CONTRACT["service_id"]
            and handler_name == STREAM_CONTRACT["handler"]
        ):
            if any(
                call[direction]["bytes"] != STREAM_CONTRACT["record"]["transfer_bytes"]
                for call in row["call_candidates"]
                for direction in ("send", "receive")
            ):
                row["status"] = "unresolved"
                row["reason"] = (
                    "decoded transfer size differs from the evidenced STREAM record contract"
                )
                continue
            row["contract"] = STREAM_CONTRACT
        else:
            row["status"] = "unresolved"
            row["reason"] = "dispatch domain beyond the evidenced STREAM child"
    return handoffs


def inventory_handoffs(extracted: Path) -> dict:
    missing, payloads = [], {}
    ee_path = extracted / "SLES_517.05"
    ee = None
    if ee_path.is_file():
        ee = ee_path.read_bytes()
        if sha256(ee) != PROFILE["ee_sha256"]:
            raise Invalid("EE profile identity mismatch")
    else:
        missing.append("required EE image is absent: " + str(ee_path))
    pins = {
        r["program"]: r["sha256"]
        for r in json.loads(PINS_PATH.read_text())["input_modules"]
    }
    rom_path = extracted / "IRX/IOPRP255.IMG"
    if rom_path.is_file():
        image = rom_path.read_bytes()
        try:
            payloads = {
                r["name"] + ".irx": image[r["offset"] : r["offset"] + r["bytes"]]
                for r in parse_romdir(image)["modules"]
            }
        except Incomplete as exc:
            missing.append(str(exc))
    else:
        missing.append("required ROM image is absent: " + str(rom_path))
    for name, digest in pins.items():
        path = extracted / "IRX" / name
        if path.is_file():
            data = path.read_bytes()
            if sha256(data) != digest:
                raise Invalid(name + " exact static identity mismatch")
            payloads.setdefault(name, data)
        if name not in payloads:
            missing.append("required pinned module is absent: " + name)
    rows = []
    for name, digest in sorted(pins.items()):
        if name not in payloads:
            continue
        data = payloads[name]
        if sha256(data) != digest:
            raise Invalid(name + " exact static identity mismatch")
        try:
            module = parse_irx(data)
        except Incomplete as exc:
            missing.append(name + ": " + str(exc))
            continue
        targets = {}
        tables = []
        for table in module["imports"]:
            if table["library"] in ("sifcmd", "sifman"):
                tables.append(
                    {
                        "library": table["library"],
                        "version": table["version"],
                        "ordinals": [
                            {"ordinal": link["index"], "stub": link["stub_text_offset"]}
                            for link in table["links"]
                        ],
                    }
                )
                targets.update(
                    {
                        link["stub_text_offset"]: table["library"]
                        + "/"
                        + str(link["index"])
                        for link in table["links"]
                    }
                )
        rows.append(
            {
                "module": name,
                "sha256": digest,
                "sif_tables": tables,
                "candidates": scan_calls(data, targets),
                "handler_status": "unresolved except committed STREAM volume child",
            }
        )
    ee_candidates = {}
    if ee is not None:
        try:
            ee_candidates = scan_calls(ee, EE_TARGETS)
        except Incomplete as exc:
            missing.append(str(exc))
    handoffs = derive_handoffs(ee, payloads)
    if missing:
        raise Incomplete(
            "; ".join(missing),
            {
                "ee": ee_candidates,
                "modules": rows,
                "handoffs": handoffs,
                "parent_status": "incomplete",
            },
        )
    return {
        "scope": "all fixed 24 modules and aligned EE executable words",
        "ee": ee_candidates,
        "modules": rows,
        "handoffs": handoffs,
        "parent_status": "incomplete",
        "gaps": PARENT_GAPS,
        "runtime_registration": "unobserved",
        "claim_limits": "Numeric exact-version imports and JAL/JALR-shaped words are candidates; neither handlers nor complete decoded control flow.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extracted", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    def action():
        result = inventory_handoffs(args.extracted)
        raise Incomplete(
            "required parent handoff inventory is not yet reconciled", result
        )

    pins = json.loads(PINS_PATH.read_text())["input_modules"]
    inputs = [
        args.extracted / "SLES_517.05",
        args.extracted / "IRX/IOPRP255.IMG",
        *[args.extracted / "IRX" / row["program"] for row in pins],
        PINS_PATH,
        *[
            Path(__file__).with_name(name)
            for name in (
                "inventory_rpc_handoffs.py",
                "check_rpc_contracts.py",
                "rpc_contracts.py",
                "rpc_handoffs.py",
                "rpc_profile.json",
                "iop_symbols.py",
                "ps2_executables.py",
                "ps2_irx.py",
                "evidence_common.py",
            )
        ],
    ]
    return write_result(
        args.output,
        "PAL RPC handoff frontier",
        action,
        [path for path in inputs if path.is_file()],
    )


if __name__ == "__main__":
    raise SystemExit(main())
