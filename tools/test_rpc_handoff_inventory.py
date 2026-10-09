"""Public CLI priority controls; synthetic inputs contain no corpus bytes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


import struct
from elf_fixture import Spec, build_elf
from inventory_rpc_handoffs import derive_handoffs
from rpc_handoffs import (
    decode_bind_sites,
    decode_call_sites,
    decode_register_sites,
    join_handoffs,
)


def stream_candidate_images(transfer_bytes=0x800):
    """Synthetic complete static binding, without proprietary instruction bytes."""
    ee_words = (
        0x24041000,
        0x3C050001,
        0x34A52345,
        0x0C07B43C,
        0,
        0x24041000,
        0x24050000,
        0x24072000,
        0x24080000 | transfer_bytes,
        0x24093000,
        0x240A0800,
        0x0C07B4B0,
        0,
    )
    ee = build_elf(
        [Spec(".text", struct.pack("<13I", *ee_words), flags=6, address=0x1000)]
    )
    registration = struct.pack(
        "<7I", 0x3C050001, 0x34A52345, 0x3C060001, 0x24C6D410, 0x24072000, 0x0C00000C, 0
    )
    imports = struct.pack("<III8s", 0x41E00000, 0, 0x100, b"sifcmd\0\0")
    text = registration + imports + struct.pack("<4I", 0x03E00008, 0x24000001, 0, 0)
    strings = b"\0sceSifRegisterRpc\0ProcessEECommand\0"
    symbols = bytes(16) + struct.pack("<IIIBBH", 1, 48, 8, 0x12, 0, 1)
    symbols += struct.pack("<IIIBBH", 19, 0xD410, 4, 0x12, 0, 1)
    module = bytearray(
        build_elf(
            [
                Spec(".text", text, flags=6, address=0),
                Spec(
                    ".iopmod",
                    struct.pack("<IIIIIIH", 0, 0, 0, len(text), 0, 0, 0x100)
                    + b"stream\0",
                    kind=0x70000080,
                    flags=0,
                ),
                Spec(".symtab", symbols, kind=2, flags=0),
                Spec(".strtab", strings, kind=3, flags=0),
            ]
        )
    )
    struct.pack_into("<H", module, 16, 0xFF80)
    shoff = struct.unpack_from("<I", module, 32)[0]
    struct.pack_into("<I", module, shoff + 3 * 40 + 24, 4)
    return ee, bytes(module)


class RpcFrontierPriority(unittest.TestCase):
    def test_cli_missing_only_frontier_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("inventory_rpc_handoffs.py")),
                    str(root),
                    "--output",
                    str(root / "receipts"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_cli_available_malformed_rom_wins_over_missing_ee(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "IRX").mkdir()
            rom = root / "IRX/IOPRP255.IMG"
            rom.write_bytes(b"")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("inventory_rpc_handoffs.py")),
                    str(root),
                    "--output",
                    str(root / "receipts"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)["result"]).read_text())
            self.assertIn("ROMDIR prefix", report["diagnostics"][0])
            self.assertIn(str(rom), report["inputs"])

    def test_cli_missing_ee_and_rom_cannot_hide_changed_pinned_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "IRX").mkdir()
            module = root / "IRX/STREAM.IRX"
            module.write_bytes(b"changed pinned module")
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("inventory_rpc_handoffs.py")),
                    str(root),
                    "--output",
                    str(root / "receipts"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)["result"]).read_text())
            self.assertIn(
                "STREAM.IRX exact static identity mismatch", report["diagnostics"][0]
            )
            self.assertIn(str(module), report["inputs"])


class HandoffDecoding(unittest.TestCase):
    def test_stream_contract_requires_its_evidenced_transfer_sizes(self):
        ee, stream = stream_candidate_images()
        positive = derive_handoffs(ee, {"STREAM.IRX": stream})[0]
        self.assertEqual(positive["status"], "bound")
        self.assertIn("contract", positive)
        ee, stream = stream_candidate_images(transfer_bytes=0x400)
        changed = derive_handoffs(ee, {"STREAM.IRX": stream})[0]
        self.assertEqual(changed["status"], "unresolved")
        self.assertNotIn("contract", changed)
        self.assertEqual(changed["call_candidates"][0]["send"]["bytes"], 0x400)

    def test_other_module_registration_cannot_borrow_stream_handler_symbols(self):
        ee, other_module = stream_candidate_images()
        stream_symbols_only = other_module.replace(
            b"sceSifRegisterRpc", b"unrelated".ljust(17, b"\0")
        )
        row = derive_handoffs(
            ee, {"OTHER.IRX": other_module, "STREAM.IRX": stream_symbols_only}
        )[0]
        self.assertEqual(row["status"], "unresolved")
        self.assertEqual(row["module"], "OTHER.IRX")
        self.assertNotIn("contract", row)

    def test_inventory_bind_arguments_include_call_delay_slot(self):
        # a1 changes from service 1 to service 2 before the callee enters.
        text = struct.pack("<4I", 0x24041000, 0x24050001, 0x0C07B43C, 0x24050002)
        elf = build_elf([Spec(".text", text, flags=6, address=0x1000)])
        rows = derive_handoffs(elf, {})
        self.assertEqual(rows[0]["service_id"], 2)
        self.assertEqual(rows[0]["status"], "incomplete")

    def test_inventory_does_not_join_stale_arguments_after_unmodeled_writes(self):
        # XOR and LB write a1; a prior call may clobber it, and a branch may
        # skip argument setup. None of these paths establishes service 1.
        for intervening in (
            (0x00A52826,),
            (0x80A50000,),
            (0x0C000400, 0),
            (0x0C000400, 0x24050002),
            (0x10000002, 0),
            (0x10000002, 0, 0x24041000, 0x24050001),
            (0x00052000,),
            (0x00A52818,),
            (0x00A52819,),
        ):
            words = (0x24041000, 0x24050001, *intervening, 0x0C07B43C, 0)
            elf = build_elf(
                [
                    Spec(
                        ".text",
                        struct.pack(f"<{len(words)}I", *words),
                        flags=6,
                        address=0x1000,
                    )
                ]
            )
            with self.subTest(intervening=intervening):
                row = derive_handoffs(elf, {})[0]
                self.assertIsNone(row["service_id"])
                self.assertEqual(row["status"], "incomplete")

    def test_inventory_zero_register_cannot_be_rewritten(self):
        words = (0x24000001, 0x24041000, 0x00002821, 0x0C07B43C, 0)
        elf = build_elf(
            [Spec(".text", struct.pack("<5I", *words), flags=6, address=0x1000)]
        )
        row = derive_handoffs(elf, {})[0]
        self.assertEqual(row["service_id"], 0)

    def test_bind_candidates_require_aligned_jal_and_complete_delay_slot(self):
        words = (0x24041000, 0x24050001, 0x0C07B43C, 0)
        elf = build_elf(
            [Spec(".text", struct.pack("<4I", *words), flags=6, address=0x1000)]
        )
        for site in (0xFFC, 0x1001, 0x1004, 0x100C, 0x1010):
            with self.subTest(site=site):
                self.assertEqual(
                    decode_bind_sites(elf, site)[0]["status"], "unresolved"
                )
        truncated = build_elf(
            [Spec(".text", struct.pack("<3I", *words[:3]), flags=6, address=0x1000)]
        )
        self.assertEqual(derive_handoffs(truncated, {})[0]["status"], "incomplete")

    def test_bind_site_decodes_client_record_and_service_id(self):
        # lui s0,0x36; addiu a0,s0,-0x6d80; lui a1,0x1; ori a1,a1,0x2345; jal bind.
        text = struct.pack(
            "<7I",
            0x3C100036,
            0x26049280,
            0x3C050001,
            0x34A52345,
            0x0C000000,
            0x00000000,
            0x00000000,
        )
        elf = build_elf([Spec(".text", text, flags=6, address=0x138280)])
        sites = decode_bind_sites(elf, 0x138290)
        self.assertEqual(
            sites,
            [{"site": 0x138290, "client_record": 0x359280, "service_id": 0x12345}],
        )

    def test_call_site_decodes_command_buffers_and_callback(self):
        # addiu a0,s1,-28032; move a1,zero; move a2,s0; lui a3,0x23;
        # addiu a3,a3,25664; lui t1,0x36; addiu t1,t1,-31872;
        # lui t3,0x14; addiu t3,t3,-5432; addiu t0,zero,2048;
        # addiu t2,zero,2048; jal call.
        text = struct.pack(
            "<14I",
            0x3C110036,
            0x26249280,
            0x0000282D,
            0x0200302D,
            0x3C070023,
            0x24E76440,
            0x3C090036,
            0x25298380,
            0x3C0B0014,
            0x256BEAC8,
            0x24080800,
            0x240A0800,
            0x0C000000,
            0x00000000,
        )
        elf = build_elf([Spec(".text", text, flags=6, address=0x1397A8)])
        sites = decode_call_sites(elf, 0x1397D8)
        self.assertEqual(
            sites,
            [
                {
                    "site": 0x1397D8,
                    "client_record": 0x359280,
                    "command": 0,
                    "send": {"address": 0x236440, "bytes": 0x800},
                    "receive": {"address": 0x358380, "bytes": 0x800},
                    "callback": 0x13EAC8,
                }
            ],
        )

    def test_call_and_registration_arguments_include_delay_slot(self):
        call = build_elf(
            [
                Spec(
                    ".text",
                    struct.pack("<4I", 0x24041000, 0x24050001, 0x0C000000, 0x24050002),
                    flags=6,
                    address=0x1000,
                )
            ]
        )
        self.assertEqual(decode_call_sites(call, 0x1008)[0]["command"], 2)
        registration = build_elf(
            [
                Spec(
                    ".text",
                    struct.pack("<4I", 0x24050001, 0x24062000, 0x0C000000, 0x24063000),
                    flags=6,
                    address=0x1000,
                )
            ]
        )
        self.assertEqual(
            decode_register_sites(registration, 0x1008)[0]["handler"], 0x3000
        )

    def test_memory_loaded_command_stays_unresolved(self):
        # lw a1,4(a3) kills the constant; site must not invent a command.
        text = struct.pack("<4I", 0x3C040036, 0x8CE50004, 0x0C000000, 0x00000000)
        elf = build_elf([Spec(".text", text, flags=6, address=0x1000)])
        sites = decode_call_sites(elf, 0x1008)
        self.assertEqual(sites[0]["command"], None)
        self.assertEqual(sites[0]["status"], "unresolved")


class HandoffJoin(unittest.TestCase):
    def test_register_site_decodes_service_handler_and_queue(self):
        # lui a1,0x1; ori a1,a1,0x2345; lui a2,0x1; addiu a2,a2,0xd410;
        # lui a3,0x2; addiu a3,a3,0x32a0; jal register.
        text = struct.pack(
            "<8I",
            0x3C050001,
            0x34A52345,
            0x3C060001,
            0x24C6D410,
            0x3C070002,
            0x24E732A0,
            0x0C000000,
            0x00000000,
        )
        elf = build_elf([Spec(".text", text, flags=6, address=0xD4D8)])
        sites = decode_register_sites(elf, 0xD4F0)
        self.assertEqual(
            sites,
            [
                {
                    "site": 0xD4F0,
                    "service_id": 0x12345,
                    "handler": 0xD410,
                    "queue": 0x232A0,
                }
            ],
        )

    def test_memory_loaded_service_stays_unresolved(self):
        # lw a1,0(a3) kills the constant; site must not invent a service.
        text = struct.pack("<4I", 0x3C060001, 0x8CE50000, 0x0C000000, 0x00000000)
        elf = build_elf([Spec(".text", text, flags=6, address=0x1000)])
        sites = decode_register_sites(elf, 0x1008)
        self.assertEqual(sites[0]["service_id"], None)
        self.assertEqual(sites[0]["status"], "unresolved")

    def test_join_binds_matching_service_and_leaves_unbound_incomplete(self):
        binds = [
            {"site": 0x1000, "client_record": 0x359280, "service_id": 0x12345},
            {"site": 0x2000, "client_record": 0x359284, "service_id": 0x99999},
        ]
        calls = [
            {
                "site": 0x1010,
                "client_record": 0x359280,
                "command": 0,
                "send": {"address": 0x236440, "bytes": 0x800},
                "receive": {"address": 0x358380, "bytes": 0x800},
                "callback": 0x13EAC8,
            }
        ]
        registers = [
            {"site": 0x3000, "service_id": 0x12345, "handler": 0xD410, "queue": 0x232A0}
        ]
        rows = join_handoffs(binds, calls, registers)
        self.assertEqual(rows[0]["status"], "bound")
        self.assertEqual(rows[0]["call_sites"], [0x1010])
        self.assertEqual(rows[0]["commands"], [0])
        self.assertEqual(rows[1]["status"], "incomplete")

    def test_conflicting_registration_candidates_never_choose_a_handler_by_order(self):
        # AC15: a handler name alone cannot pass the contract check.
        binds = [{"site": 0x1000, "client_record": 0x359280, "service_id": 0x12345}]
        calls = [
            {
                "site": 0x1010,
                "client_record": 0x359280,
                "command": 0,
                "send": {"address": 0x236440, "bytes": 0x800},
                "receive": {"address": 0x358380, "bytes": 0x800},
            }
        ]
        registrations = [
            {"site": 0x3000, "service_id": 0x12345, "handler": 0xD410, "queue": 0x2000},
            {"site": 0x4000, "service_id": 0x12345, "handler": 0xABCD, "queue": 0x2000},
        ]
        first = join_handoffs(binds, calls, registrations)[0]
        reverse = join_handoffs(binds, calls, list(reversed(registrations)))[0]
        self.assertEqual(first["status"], "unresolved")
        self.assertEqual(first, reverse)
        self.assertEqual(len(first["registration_candidates"]), 2)
        self.assertNotIn("handler", first)

    def test_unbound_transfer_buffers_or_registration_queue_keep_handoff_incomplete(
        self,
    ):
        import copy

        # Spec AC15: "A handler name alone or an unbound shared buffer cannot
        # pass the contract check." Known handler/command cannot fill these gaps.
        binds = [{"site": 0x1000, "client_record": 0x359280, "service_id": 0x12345}]
        call = {
            "site": 0x1010,
            "client_record": 0x359280,
            "command": 0,
            "send": {"address": 0x236440, "bytes": 0x800},
            "receive": {"address": 0x358380, "bytes": 0x800},
        }
        registration = {
            "site": 0x3000,
            "service_id": 0x12345,
            "handler": 0xD410,
            "queue": 0x232A0,
        }
        for missing in (
            "send address",
            "send bytes",
            "receive address",
            "receive bytes",
            "queue",
        ):
            calls, registers = [copy.deepcopy(call)], [dict(registration)]
            if missing == "queue":
                registers[0]["queue"] = None
            else:
                direction, field = missing.split()
                calls[0][direction][field] = None
            with self.subTest(missing=missing):
                row = join_handoffs(binds, calls, registers)[0]
                self.assertEqual(row["status"], "incomplete")
                self.assertNotIn("contract", row)
                self.assertEqual(row["registration_candidates"], registers)

    def test_join_with_missing_handler_state_is_incomplete(self):
        binds = [
            {
                "site": 0x1000,
                "client_record": None,
                "service_id": None,
                "status": "unresolved",
            }
        ]
        rows = join_handoffs(
            binds,
            [],
            [
                {
                    "site": 0x3000,
                    "service_id": 0x12345,
                    "handler": 0xD410,
                    "queue": 0x232A0,
                }
            ],
        )
        self.assertEqual(rows[0]["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
