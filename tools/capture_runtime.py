#!/usr/bin/env python3
"""Capture FR2 boot events unattended with the PCSX2 v2.6.3 debugger and PINE.

macOS profile only. Debugger windows open; this command is not headless. Temporarily changes existing preferences and saved breakpoints;
restores their exact bytes after all owned emulator processes exit. Binary artifacts
are private local evidence. No guest writes or patches are issued.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import configparser
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time
import uuid
from typing import Any

from pcsx2_pine import Pine, read_state
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from corpus_contract import corpus_identity
from format_contracts import archive, require

PROCEDURE = (
    "Separate cold boot for each repeat. PCSX2 -nogui, null renderer, "
    "patches and cheats disabled, automatic saved conditional dispatch breakpoint. "
    "PINE paused status and ELF code present before savestate. Restart from entry "
    "snapshot to selected branch breakpoint, then from branch snapshot to caller ra. "
    "Save complete EE states with PINE opcode 9; confirm independent PINE memory "
    "reads against saved bytes. No memory writes or output transformations."
)


class CaseSensitiveConfig(configparser.ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


@contextmanager
def preferences(config: Path, firmware: Path, states: Path):
    if subprocess.run(["pgrep", "-x", "PCSX2"], capture_output=True).returncode == 0:
        raise Incomplete(
            "close the existing PCSX2 session before capturing shared preferences"
        )
    lock = config.parent / ".fr2-evidence-capture.lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise Incomplete("another capture owns the preference lock") from exc
    bpfile = config.parent / "debuggersettings/SLES-51705_37F695CD.json"
    slot = states / "SLES-51705 (37F695CD).181.p2s"
    paths = [config, bpfile, slot, Path(str(slot) + ".backup")]
    originals = {}
    try:
        originals = {
            path: path.read_bytes() if path.exists() else None for path in paths
        }
        settings = CaseSensitiveConfig(interpolation=None)
        settings.read(config)
        for section, values in {
            "Folders": {"Bios": str(firmware.parent), "Savestates": str(states)},
            "Filenames": {"BIOS": firmware.name},
            "EmuCore": {
                "EnablePINE": "true",
                "PINESlot": "28031",
                "EnablePatches": "false",
                "EnableCheats": "false",
                "EnableWideScreenPatches": "false",
                "EnableNoInterlacingPatches": "false",
            },
            "EmuCore/GS": {"Renderer": "11"},
            "Debugger/UserInterface": {"ShowOnStartup": "true"},
            "UI": {"StartPaused": "false", "PauseOnFocusLoss": "false"},
        }.items():
            if not settings.has_section(section):
                settings.add_section(section)
            for key, value in values.items():
                settings.set(section, key, value)
        bpfile.parent.mkdir(parents=True, exist_ok=True)
        states.mkdir(parents=True, exist_ok=True)
        with config.open("w") as stream:
            settings.write(stream)
        yield bpfile
    finally:
        for path, data in originals.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
        lock.rmdir()


def execute(args, out: Path):
    if not args.allow_debugger_windows:
        raise Incomplete(
            "capture opens debugger windows; supply --allow-debugger-windows to run it"
        )
    provenance = corpus_identity(args.game)
    game, exe, states = (
        args.game.resolve(),
        args.emulator.resolve(),
        args.states.resolve(),
    )
    config = args.config.resolve()
    identity(exe)
    identity(args.firmware)
    if not config.is_file():
        raise Incomplete("missing existing PCSX2 configuration")
    socket = Path(os.environ.get("TMPDIR", "/tmp")) / "pcsx2.sock.28031"
    records = archive(
        (game / "extracted/FILES.HDR").read_bytes(),
        (game / "extracted/FILES.DAT").read_bytes(),
    )["files"]
    byname = {
        r["path"].removesuffix(";1").replace("/", "\\").lstrip("\\").casefold(): r
        for r in records
    }
    out.mkdir(parents=True)
    with preferences(config, args.firmware.resolve(), states) as bpfile:

        def capture(tag, breakpoints, state=None):
            bpfile.write_text(
                json.dumps(
                    {
                        "Version": "0.01",
                        "SavedAddresses": [],
                        "Breakpoints": [
                            {
                                "TYPE": "8",
                                "OFFSET": f"{address:08x}",
                                "DESCRIPTION": tag,
                                "SIZE / LABEL": "",
                                "INSTRUCTION": "",
                                "CONDITION": condition,
                                "HITS": "0",
                                "X": "1",
                            }
                            for address, condition in breakpoints
                        ],
                    }
                )
            )
            command = [
                str(exe),
                "-nogui",
                "-nofullscreen",
                "-logfile",
                str(out / f"{tag}.log"),
            ]
            if state:
                command += ["-statefile", str(state)]
            command += ["--", str(game / "ford-racing-2.bin")]
            with (out / f"{tag}.launch.log").open("wb") as log:
                process = subprocess.Popen(
                    command, stdout=log, stderr=subprocess.STDOUT
                )
                pine = None
                try:
                    deadline = time.monotonic() + 60
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            raise Invalid(
                                f"{tag}: emulator exited {process.returncode}"
                            )
                        try:
                            pine = Pine(socket)
                            if (
                                pine.status() == 1
                                and pine.text(12) == "SLES-51705"
                                and pine.read(0x107CE0, 4) == bytes.fromhex("b0ffbd27")
                            ):
                                time.sleep(0.5)
                                if pine.status() == 1:
                                    break
                            pine.close()
                            pine = None
                        except OSError:
                            pass
                        time.sleep(0.2)
                    if pine is None:
                        raise Invalid(f"{tag}: no paused game event within 60 seconds")
                    version = pine.text(8)
                    require(
                        version == "PCSX2 v2.6.3",
                        "unsupported emulator protocol/layout",
                    )
                    slot = 181
                    source = states / f"SLES-51705 (37F695CD).{slot:02d}.p2s"
                    prior = source.stat().st_mtime_ns if source.exists() else 0
                    pine.save(slot)
                    destination = out / f"{tag}.p2s"
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        if source.exists() and source.stat().st_mtime_ns > prior:
                            try:
                                memory, observed = read_state(source)
                                shutil.copy2(source, destination)
                                break
                            except Exception:
                                pass
                        time.sleep(0.1)
                    else:
                        raise Invalid(f"{tag}: save-state completion timed out")
                    if pine.status() != 1:
                        raise Invalid("guest resumed during capture")
                    # Independent protocol memory reads confirm the paused savestate mapping.
                    for address, size in [
                        (0x107CE0, 16),
                        (0x283588, 64),
                        (observed["pc"], 16),
                    ]:
                        if pine.read(address, size) != memory[address : address + size]:
                            raise Invalid("PINE/savestate memory disagreement")
                    observed.update(
                        command=command,
                        process_id=process.pid,
                        captured_at=datetime.now(timezone.utc).isoformat(),
                        breakpoints=[
                            {"guest_address": a, "condition": c} for a, c in breakpoints
                        ],
                        pine_version=version,
                        memory_identity={
                            "bytes": len(memory),
                            "sha256": sha256(memory),
                        },
                        savestate=destination.name,
                    )
                    (out / f"{tag}.json").write_text(json.dumps(observed, indent=2))
                    print(
                        tag,
                        hex(observed["pc"]),
                        "v0",
                        hex(observed["registers"]["v0"]),
                        "a0",
                        hex(observed["registers"]["a0"]),
                        flush=True,
                    )
                    return destination, memory, observed
                finally:
                    if pine:
                        pine.close()
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()

        events: list[dict[str, Any]] = []
        for repeat in range(2):
            raw_exit = None
            for branch, flag in [("raw", 0), ("zlib", 1)]:
                event = f"{branch}-{repeat + 1}"
                entry, memory, observed = capture(
                    event + "-entry",
                    [
                        (
                            0x107CE0,
                            f"a2 == {flag} && a0 >= 0x00200000 && a0 < 0x02000000",
                        )
                    ],
                    raw_exit,
                )
                filename_pointer = observed["registers"]["a0"]
                name = (
                    memory[filename_pointer : filename_pointer + 256]
                    .split(b"\0")[0]
                    .decode("ascii")
                )
                record = byname[name.casefold()]
                require(
                    record["classification"] == branch,
                    "selected event has wrong archive branch",
                )
                pc = observed["pc"]
                instruction = struct.unpack_from("<I", memory, pc)[0]
                if pc == 0x107CE0:
                    return_target = observed["registers"]["ra"]
                else:
                    require(
                        instruction >> 26 == 3
                        and ((instruction & 0x3FFFFFF) << 2) == 0x107CE0,
                        "paused outside loader call",
                    )
                    return_target = pc + 8
                starts = (
                    [0x1067F8, 0x1069F0] if branch == "raw" else [0x106C48, 0x106EF8]
                )
                branched, _, branch_observation = capture(
                    event + "-branch",
                    [(a, "a0 >= 0x00200000 && a0 < 0x02000000") for a in starts],
                    entry,
                )
                exited, output_memory, exit_observation = capture(
                    event + "-exit",
                    [(return_target, "v0 >= 0x00200000 && v0 < 0x02000000")],
                    branched,
                )
                pointer = exit_observation["registers"]["v0"]
                payload = output_memory[pointer : pointer + record["output_bytes"]]
                require(
                    sha256(payload) == record["output_sha256"],
                    "captured output differs from independent archive read",
                )
                (out / f"{event}.output.bin").write_bytes(payload)
                (out / f"{event}.ee.bin").write_bytes(output_memory)
                events.append(
                    {
                        "event_id": event,
                        "branch": branch,
                        "record": record,
                        "filename": name,
                        "entry_state": entry.name,
                        "branch_state": branched.name,
                        "exit_state": exited.name,
                        "entry": observed,
                        "branch_observation": branch_observation,
                        "exit": exit_observation,
                        "return_target": return_target,
                        "output": {
                            "guest_address": pointer,
                            "bytes": len(payload),
                            "sha256": sha256(payload),
                        },
                    }
                )
                (out / "events.json").write_text(json.dumps(events, indent=2))
                print(
                    "MATCH",
                    event,
                    record["idx"],
                    name,
                    len(payload),
                    sha256(payload),
                    flush=True,
                )
                if branch == "raw":
                    raw_exit = exited

    manifest = {
        "schema_version": 1,
        "origin": "pcsx2-live",
        "provenance": provenance,
        "executable_identity": identity(game / "extracted/SLES_517.05"),
        "archive_identity": {
            "header": identity(game / "extracted/FILES.HDR"),
            "data": identity(game / "extracted/FILES.DAT"),
        },
        "tools": {"pcsx2": "v2.6.3", "pcsx2_executable": identity(exe)},
        "firmware_identity": identity(args.firmware),
        "captures": [],
    }
    for event in events:

        def observation(value: dict[str, Any]):
            return {key: value[key] for key in ["pc", "registers"]}

        memory_path = out / (event["event_id"] + ".ee.bin")
        memory = memory_path.read_bytes()
        manifest["captures"].append(
            {
                "event_id": event["event_id"],
                "branch": event["branch"],
                "record_id": event["record"]["idx"],
                "path": event["record"]["path"],
                "memory": memory_path.name,
                "memory_identity": identity(memory_path),
                "savestate": event["exit_state"],
                "savestate_identity": identity(out / event["exit_state"]),
                "entry_savestate": {
                    "path": event["entry_state"],
                    "identity": identity(out / event["entry_state"]),
                },
                "branch_savestate": {
                    "path": event["branch_state"],
                    "identity": identity(out / event["branch_state"]),
                },
                "entry": observation(event["entry"]),
                "branch_observation": observation(event["branch_observation"]),
                "exit": observation(event["exit"]),
                "output": event["output"],
                "code": [
                    {
                        "guest_address": event[name]["pc"],
                        "bytes_hex": memory[
                            event[name]["pc"] : event[name]["pc"] + 16
                        ].hex(),
                    }
                    for name in ["entry", "branch_observation", "exit"]
                ],
                "captured_at": event["exit"]["captured_at"],
                "procedure": PROCEDURE,
                "before_consumption": True,
                "mutations": [],
            }
        )
    path = out / "captures.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "manifest": str(path),
        "manifest_identity": identity(path),
        "events": len(events),
        "fresh_capture": True,
        "provenance": provenance,
        "next_check": "verify_runtime.py --captures <manifest> --pcsx2-executable <emulator> --firmware <firmware>",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    home = Path.home() / "Library/Application Support/PCSX2"
    parser.add_argument(
        "--allow-debugger-windows",
        action="store_true",
        help="required: capture opens the PCSX2 debugger",
    )
    parser.add_argument("--game", type=Path, default=Path("games/ford-racing-2"))
    parser.add_argument(
        "--emulator",
        type=Path,
        default=Path("/Applications/PCSX2.app/Contents/MacOS/PCSX2"),
    )
    parser.add_argument("--config", type=Path, default=home / "inis/PCSX2.ini")
    parser.add_argument("--states", type=Path, default=home / "sstates")
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path(".scratch/evidence/captures")
    )
    args = parser.parse_args()
    artifacts = args.output.resolve() / ("capture-" + uuid.uuid4().hex)
    return write_result(
        args.output,
        "capture",
        lambda: execute(args, artifacts),
        [args.emulator, args.config, args.firmware],
    )


if __name__ == "__main__":
    raise SystemExit(main())
