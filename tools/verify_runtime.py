#!/usr/bin/env python3
"""Replay recorded EE captures against independent archive output; never a live capture."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import struct

from corpus_contract import corpus_identity
from evidence_common import Incomplete, Invalid, identity, sha256, write_result
from format_contracts import archive, require
from pcsx2_pine import read_state


def elf_bytes(executable: bytes, address: int, size: int) -> bytes:
    require(
        executable[:7] == b"\x7fELF\x01\x01\x01",
        "expected little-endian ELF32 executable",
    )
    require(len(executable) >= 52, "truncated ELF header")
    offset = struct.unpack_from("<I", executable, 28)[0]
    stride, count = struct.unpack_from("<HH", executable, 42)
    require(
        stride >= 32 and offset + stride * count <= len(executable),
        "truncated ELF program headers",
    )
    for index in range(count):
        kind, start, guest, _, file_size = struct.unpack_from(
            "<5I", executable, offset + index * stride
        )
        if kind == 1 and guest <= address and address + size <= guest + file_size:
            begin = start + address - guest
            require(begin + size <= len(executable), "truncated ELF load segment")
            return executable[begin : begin + size]
    raise Invalid(f"guest code {address:#x} is not backed by executable bytes")


def verify(
    captures_path: Path,
    header: Path,
    data: Path,
    executable: Path,
    game: Path,
    synthetic: bool,
    pcsx2: Path | None,
    firmware: Path | None,
):
    manifest = json.loads(captures_path.read_text())
    require(manifest["schema_version"] == 1, "unknown runtime schema version")
    require(
        manifest["executable_identity"] == identity(executable),
        "stale executable identity",
    )
    require(
        manifest["archive_identity"]
        == {"header": identity(header), "data": identity(data)},
        "stale archive identity",
    )
    if manifest.get("origin") != ("synthetic" if synthetic else "pcsx2-live"):
        raise Incomplete(
            "capture origin does not match requested verification environment"
        )
    provenance = {} if synthetic else corpus_identity(game)
    if not synthetic:
        require(manifest["provenance"] == provenance, "stale capture corpus identity")
        if pcsx2 is None or firmware is None:
            raise Incomplete(
                "real replay requires local PCSX2 executable and firmware identities"
            )
        require(
            manifest["tools"]["pcsx2_executable"] == identity(pcsx2),
            "changed PCSX2 executable",
        )
        require(
            manifest["firmware_identity"] == identity(firmware),
            "changed firmware identity",
        )
    require(bool(manifest["tools"]["pcsx2"]), "missing emulator version")
    parsed = archive(header.read_bytes(), data.read_bytes())
    records = {record["idx"]: record for record in parsed["files"]}
    captures = manifest.get("captures", [])
    seen = set()
    comparisons = []
    branches: dict[str, list] = {"raw": [], "zlib": []}
    try:
        for capture in captures:
            event = capture["event_id"]
            require(
                event not in seen and isinstance(event, str) and bool(event),
                "duplicate/invalid capture event identity",
            )
            seen.add(event)
            branch = capture["branch"]
            require(branch in branches, "unknown observed branch")
            record = records.get(capture["record_id"])
            require(record is not None, "capture names a non-file archive record")
            if record is None:
                raise Invalid("missing archive record")
            require(
                record["path"] == capture["path"]
                and record["classification"] == branch,
                "wrong record/path/branch identity",
            )
            if not capture.get("procedure") or not capture.get("before_consumption"):
                raise Incomplete(
                    f"{event}: missing procedure or before-consumption observation"
                )
            datetime.fromisoformat(capture["captured_at"].replace("Z", "+00:00"))
            if capture.get("mutations"):
                raise Incomplete(
                    f"{event}: acceptance captures must follow a clean restart after mutations"
                )
            memory_path = captures_path.parent / capture["memory"]
            require(
                identity(memory_path) == capture["memory_identity"],
                f"{event}: changed/incomplete memory capture",
            )
            memory = memory_path.read_bytes()
            observations = {}
            if not synthetic:
                require(
                    len(memory) == 32 * 1024 * 1024,
                    "real EE capture must contain all 32 MiB",
                )
                state = captures_path.parent / capture["savestate"]
                require(
                    identity(state) == capture["savestate_identity"],
                    "changed savestate artifact",
                )
                saved_memory, saved_exit = read_state(state)
                require(
                    saved_memory == memory, "memory is not the saved EE memory artifact"
                )
                require(
                    saved_exit["pc"] == capture["exit"]["pc"]
                    and saved_exit["registers"] == capture["exit"]["registers"],
                    "exit registers differ from savestate",
                )
                if not capture.get("entry_savestate") or not capture.get(
                    "branch_savestate"
                ):
                    raise Incomplete("missing entry/branch observation artifacts")
                observations = {}
                for name in ["entry", "branch"]:
                    artifact = capture[name + "_savestate"]
                    path = captures_path.parent / artifact["path"]
                    require(
                        identity(path) == artifact["identity"],
                        "changed register observation",
                    )
                    observed_memory, registers = read_state(path)
                    require(
                        registers["pc"]
                        == capture[
                            "entry" if name == "entry" else "branch_observation"
                        ]["pc"]
                        and registers["registers"]
                        == capture[
                            "entry" if name == "entry" else "branch_observation"
                        ]["registers"],
                        f"{name} registers differ from savestate",
                    )
                    observations[name] = observed_memory
                require(
                    capture["entry"]["pc"] == 0x107CE0,
                    "wrong guest loader dispatch location",
                )
                require(
                    capture["branch_observation"]["pc"]
                    in (
                        {0x1067F8, 0x1069F0}
                        if branch == "raw"
                        else {0x106C48, 0x106EF8}
                    ),
                    "missing or wrong observed loader branch",
                )
                require(
                    capture["exit"]["pc"] == capture["entry"]["registers"]["ra"],
                    "capture is not at the actual caller return address",
                )
                require(
                    capture["exit"]["pc"]
                    in {0x101420, 0x11EE08, 0x22AC68, 0x22E014, 0x22E060},
                    "unverified before-consumption guest return",
                )
                filename_address = capture["entry"]["registers"]["a0"]
                require(
                    0 <= filename_address <= len(memory) - 256,
                    "invalid guest filename pointer",
                )
                filename = (
                    observations["entry"][filename_address : filename_address + 256]
                    .split(b"\0")[0]
                    .decode("ascii")
                )
                expected_name = (
                    record["path"].removesuffix(";1").replace("/", "\\").lstrip("\\")
                )
                require(
                    filename.casefold() == expected_name.casefold(),
                    "observed guest filename differs from selected archive record",
                )
            require(
                capture["entry"]["registers"]["a2"] == int(branch == "zlib"),
                "observed flag does not select recorded branch",
            )
            output = capture["output"]
            address, length = output["guest_address"], output["bytes"]
            require(
                type(address) is int
                and type(length) is int
                and 0 <= address <= len(memory)
                and 0 <= length <= len(memory) - address,
                "output guest span out of range; host pointers are not guest addresses",
            )
            require(
                capture["exit"]["registers"]["v0"] == address,
                "returned guest pointer differs from output span",
            )
            observed = memory[address : address + length]
            require(
                length == record["output_bytes"], "omitted bytes/output length mismatch"
            )
            digest = sha256(observed)
            require(
                digest == output["sha256"] == record["output_sha256"],
                "changed output or independent extraction mismatch",
            )
            if not capture.get("code"):
                raise Incomplete("missing guest code/overlay observation")
            for code in capture["code"]:
                offset = code["guest_address"]
                expected = bytes.fromhex(code["bytes_hex"])
                require(
                    bool(expected) and 0 <= offset <= len(memory) - len(expected),
                    "invalid guest code span",
                )
                require(
                    memory[offset : offset + len(expected)] == expected,
                    "guest code bytes changed/overlay mismatch",
                )
                if not synthetic:
                    require(
                        elf_bytes(executable.read_bytes(), offset, len(expected))
                        == expected,
                        "observed guest code differs from source executable",
                    )
                    require(
                        all(
                            observed[offset : offset + len(expected)] == expected
                            for observed in observations.values()
                        ),
                        "code/overlay differs between event observations",
                    )
            if not synthetic:
                required_code = {
                    capture["entry"]["pc"],
                    capture["branch_observation"]["pc"],
                    capture["exit"]["pc"],
                }
                require(
                    required_code
                    <= {code["guest_address"] for code in capture["code"]},
                    "omitted observed instruction code bytes",
                )
            comparisons.append(
                {
                    "event_id": event,
                    "branch": branch,
                    "record_id": record["idx"],
                    "path": record["path"],
                    "guest_address": address,
                    "host_address": "not used: savestate eeMemory.bin indexes are guest offsets",
                    "bytes": length,
                    "sha256": digest,
                    "memory_identity": capture["memory_identity"],
                    "capture_procedure": capture["procedure"],
                    "captured_at": capture["captured_at"],
                }
            )
            branches[branch].append(
                (record["idx"], digest, capture["memory_identity"]["sha256"])
            )
        for branch, events in branches.items():
            if len(events) < 2:
                raise Incomplete(f"missing {branch} branch or repeat capture")
            require(
                len({(record, digest) for record, digest, _ in events}) == 1,
                f"{branch}: repeat must select the same record and logical output",
            )
            require(
                len({memory for _, _, memory in events}) >= 2,
                f"{branch}: repeated artifact is not an independent event",
            )
    except (Incomplete, Invalid) as exc:
        exc.details = {
            "comparisons": comparisons,
            "provenance": provenance,
            "verification_mode": "offline_replay",
            "fresh_capture": False,
            "milestone_eligible": False,
            **exc.details,
        }
        raise
    except FileNotFoundError as exc:
        raise Incomplete(
            str(exc), {"comparisons": comparisons, "provenance": provenance}
        ) from exc
    except (ValueError, KeyError, IndexError, TypeError, OSError) as exc:
        raise Invalid(
            f"{type(exc).__name__}: {exc}",
            {"comparisons": comparisons, "provenance": provenance},
        ) from exc
    return {
        "comparisons": comparisons,
        "provenance": provenance,
        "synthetic": synthetic,
        "verification_mode": "offline_replay",
        "fresh_capture": False,
        "milestone_eligible": False,
        "evidence_eligible": not synthetic,
        "limitations": "Validates recorded evidence. Does not launch or freshly observe the game.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path)
    parser.add_argument("--game", type=Path, default=Path("games/ford-racing-2"))
    parser.add_argument("--header", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--pcsx2-executable", type=Path)
    parser.add_argument("--firmware", type=Path)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path(".scratch/evidence/runtime")
    )
    args = parser.parse_args()
    header = args.header or args.game / "extracted/FILES.HDR"
    data = args.data or args.game / "extracted/FILES.DAT"
    executable = args.executable or args.game / "extracted/SLES_517.05"

    def run():
        if args.captures is None:
            raise Incomplete(
                "missing --captures: real raw/zlib events and repeats have not been supplied"
            )
        return verify(
            args.captures,
            header,
            data,
            executable,
            args.game,
            args.synthetic,
            args.pcsx2_executable,
            args.firmware,
        )

    return write_result(
        args.output,
        "runtime",
        run,
        [p for p in [args.captures, header, data, executable] if p is not None],
    )


if __name__ == "__main__":
    raise SystemExit(main())
