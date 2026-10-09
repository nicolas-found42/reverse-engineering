"""Public CLI priority controls; synthetic inputs contain no corpus bytes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


import struct
from elf_fixture import Spec, build_elf
from rpc_handoffs import (
    decode_bind_sites,
    decode_call_sites,
    decode_register_sites,
    join_handoffs,
)


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
        sites = decode_call_sites(elf, 0x1397DC)
        self.assertEqual(
            sites,
            [
                {
                    "site": 0x1397DC,
                    "client_record": 0x359280,
                    "command": 0,
                    "send": {"address": 0x236440, "bytes": 0x800},
                    "receive": {"address": 0x358380, "bytes": 0x800},
                    "callback": 0x13EAC8,
                }
            ],
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
