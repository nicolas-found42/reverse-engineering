"""Abstract word labels for a narrow, pinned corner-packing instruction span.

This reads saved metadata and validates bytes against the ELF. It never runs
the game. Word labels are symbolic, and no VU arithmetic is evaluated.
"""
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from ps2_executables import parse_elf


def main():
    static_path = Path(".scratch/evidence/static-export.json")
    executable = Path("games/ford-racing-2/extracted/SLES_517.05")
    static = json.loads(static_path.read_text())
    raw = executable.read_bytes()
    digest = lambda data: hashlib.sha256(data).hexdigest()
    assert digest(raw) == static["executable_sha256"]
    elf = parse_elf(raw)
    functions = {f["entry"]: f for f in static["functions"]}
    verified = 0
    pins = []
    for entry in ("00122d90", "0021b710"):
        rows = functions[entry]["instructions"]
        for row in rows:
            address = int(row["address"], 16)
            matches = [p for p in elf["programs"] if p["type"] == 1 and
                       p["virtual_address"] <= address < p["virtual_address"] + p["file_size"]]
            assert len(matches) == 1
            segment = matches[0]
            offset = segment["offset"] + address - segment["virtual_address"]
            assert raw[offset:offset + 4] == bytes.fromhex(row["bytes"])
            verified += 1
        pins.append({"entry": entry, "instruction_words": len(rows),
                     "instruction_bytes_sha256": digest(b"".join(bytes.fromhex(r["bytes"]) for r in rows))})

    # Exact preceding loads: a2=record+4,t0=+8,f3=+12,f1=+16,
    # f0=+20,f2=+24. The branch-likely delay at 00122dac adds4.
    registers = {"zero": ["0"] * 4, "a2": ["4", "?", "?", "?"],
                 "t0": ["8", "?", "?", "?"]}
    scalar = {"f3": "12", "f1": "16", "f0": "20", "f2": "24"}
    instructions = {r["address"]: r["text"] for r in functions["00122d90"]["instructions"]}
    for address, text in {
        "00122da8": "bnel v0,zero,0x00122dd0",
        "00122dac": "_addiu v0,v0,0x4",
        "00122dd4": "lw a2,0x0(v0)",
        "00122de8": "lw t0,0x4(v0)",
        "00122dfc": "lwc1 f3,0x8(v0)",
        "00122e0c": "lwc1 f1,0xc(v0)",
        "00122e1c": "lwc1 f0,0x10(v0)",
        "00122de4": "_lwc1 f2,0x14(v0)",
    }.items():
        assert instructions[address] == text
    stores = {}
    for row in functions["00122d90"]["instructions"]:
        address = int(row["address"], 16)
        if not 0x122e7c <= address <= 0x122f0c:
            continue
        op, arguments = row["text"].split(" ", 1)
        args = arguments.split(",")
        if op == "mfc1":
            registers[args[0]] = [scalar[args[1]], "?", "?", "?"]
        elif op == "lui":
            if args == ["a0", "0x3f80"]:
                registers["a0"] = ["1.0", "0", "0", "0"]
            else:
                # After t3 has been packed, it becomes a VU matrix address.
                assert args == ["t3", "0x2d"]
        elif op == "pextlw":
            rs, rt = registers[args[1]], registers[args[2]]
            registers[args[0]] = [rt[0], rs[0], rt[1], rs[1]]
        elif op == "pcpyld":
            rs, rt = registers[args[1]], registers[args[2]]
            registers[args[0]] = rt[:2] + rs[:2]
        elif op == "por":
            assert args[1] == "zero"
            registers[args[0]] = registers[args[2]].copy()
        elif op == "sq":
            offset = int(args[1].split("(")[0], 16)
            assert args[1].endswith("(sp)")
            stores[offset] = registers[args[0]].copy()
        else:
            assert op in ("addiu", "move", "li")
    corners = [stores[i * 16] for i in range(8)]
    assert all(corner[3] == "1.0" for corner in corners)
    expected = set(itertools.product(("4", "8"), ("12", "16"), ("20", "24")))
    assert {tuple(corner[:3]) for corner in corners} == expected
    result = {"schema_version": 1, "executable_sha256": digest(raw),
              "static_export_sha256": digest(static_path.read_bytes()),
              "verified_instruction_words": verified, "function_instruction_pins": pins,
              "abstract_corners_source_offsets": corners, "all_eight_pair_combinations": True,
              "source_pairs": [[4, 8], [12, 16], [20, 24]],
              "claim_limits": "Symbolic packed-word construction only; no game or VU execution, no axis/unit assignment, no transformed-corner or vertex-containment proof."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
