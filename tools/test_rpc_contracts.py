"""Public STREAM record check controls; fixtures contain no corpus bytes."""

import struct
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
import check_rpc_contracts as checker
from elf_fixture import Spec, build_elf
from check_rpc_contracts import scan_calls, check_static_binding

from evidence_common import Incomplete, Invalid
from rpc_contracts import decode_volume_batch


def packet(*words):
    return struct.pack("<" + "H" * len(words), *words).ljust(2048, b"\xa5")


class StreamVolumeContracts(unittest.TestCase):
    def test_cli_checks_packet_framing_while_static_image_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream, raw_packet = root / "stream.irx", root / "packet.bin"
            stream.write_bytes(b"synthetic pinned stream")
            # Fixed-profile identity seam only; never invoke static binding with absent EE.
            from evidence_common import sha256

            for data, expected in [
                (b"", 1),
                (packet(62, 1, 2, 3, 0, 1, 2), 2),
                (packet(62, 1, 9, 0), 2),
            ]:
                raw_packet.write_bytes(data)
                argv = [
                    "check_rpc_contracts.py",
                    "--ee",
                    str(root / "missing"),
                    "--stream",
                    str(stream),
                    "--packet",
                    str(raw_packet),
                    "--output",
                    str(root / "receipts"),
                ]
                output = StringIO()
                with (
                    patch.object(sys, "argv", argv),
                    patch.dict(
                        checker.PROFILE, {"stream_sha256": sha256(stream.read_bytes())}
                    ),
                    redirect_stdout(output),
                    patch.object(
                        checker,
                        "check_static_binding",
                        side_effect=AssertionError("missing EE"),
                    ),
                ):
                    result = checker.main()
                self.assertEqual(result, expected, output.getvalue())
                report = json.loads(
                    Path(json.loads(output.getvalue())["result"]).read_text()
                )
                self.assertIn(str(raw_packet), report["inputs"])
                self.assertIn("packet", report["details"])

    def test_cli_missing_ee_cannot_hide_changed_stream_or_packet_identity(self):
        script = Path(__file__).with_name("check_rpc_contracts.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream, raw_packet = root / "stream.irx", root / "packet.bin"
            stream.write_bytes(b"wrong STREAM profile")
            raw_packet.write_bytes(b"")
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--ee",
                    str(root / "missing"),
                    "--stream",
                    str(stream),
                    "--packet",
                    str(raw_packet),
                    "--output",
                    str(root / "receipts"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)["result"]).read_text())
            self.assertIn(
                "stream static profile identity mismatch", report["diagnostics"][0]
            )
            self.assertIn(str(stream), report["inputs"])
            self.assertEqual(
                report["inputs"][str(raw_packet)]["sha256"],
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )

    def test_two_channel_volume_records_decode_and_tail_remains_opaque(self):
        result = decode_volume_batch(
            packet(62, 2, 2, 3, 0, 120, 240, 2, 3, 47, 600, 700)
        )
        self.assertEqual(
            result["records"],
            [
                {"channel": 0, "left": 120, "right": 240},
                {"channel": 47, "left": 600, "right": 700},
            ],
        )
        self.assertEqual(result["used_bytes"], 24)

    def test_invalid_length_arity_version_and_channel_fail(self):
        for data in (
            b"",
            packet(61, 1, 2, 3, 0, 1, 2),
            packet(62, 1, 2, 2, 0, 1),
            packet(62, 1, 2, 3, 48, 1, 2),
            packet(62, 1, 2, 65535),
        ):
            with self.subTest(data=data[:16]), self.assertRaises(Invalid):
                decode_volume_batch(data)

    def test_missing_required_subcommand_contract_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, "unresolved"):
            decode_volume_batch(packet(62, 1, 9, 2, 65535, 0))

    def test_known_malformed_record_wins_over_an_earlier_unknown_record(self):
        with self.assertRaises(Invalid):
            decode_volume_batch(packet(62, 2, 9, 0, 2, 4, 0, 1, 2, 3))

    def test_record_count_cannot_read_past_transfer(self):
        with self.assertRaises(Invalid):
            decode_volume_batch(packet(62, 512))

    def test_empty_batch_is_incomplete_for_the_volume_child(self):
        with self.assertRaisesRegex(Incomplete, "no channel-volume"):
            decode_volume_batch(packet(62, 0))

    def test_static_inventory_lists_direct_and_indirect_candidates(self):
        # MIPS jal 0x2000 followed by jalr t9; fixture assembled independently.
        elf = build_elf(
            [
                Spec(
                    ".text",
                    struct.pack("<II", 0x0C000800, 0x0320F809),
                    flags=6,
                    address=0x1000,
                )
            ]
        )
        result = scan_calls(elf, {0x2000: "fixture-rpc"})
        self.assertEqual(
            result["direct_candidates"],
            [{"site": 0x1000, "target": 0x2000, "domain": "fixture-rpc"}],
        )
        self.assertEqual(result["indirect_instruction_candidates"], [0x1004])

    def test_wrong_or_missing_caller_handler_image_never_uses_prior_evidence(self):
        fixture = build_elf([Spec(".text", b"\0" * 8, flags=6)])
        with self.assertRaisesRegex(Invalid, "identity mismatch"):
            check_static_binding(fixture, fixture)

    def test_cli_reports_missing_profile_as_incomplete_and_changed_profile_as_fail(
        self,
    ):
        script = Path(__file__).with_name("check_rpc_contracts.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ee = root / "ee.elf"
            ee.write_bytes(build_elf([Spec(".text", b"\0" * 8, flags=6)]))
            base = [
                sys.executable,
                str(script),
                "--stream",
                str(root / "missing.irx"),
                "--output",
                str(root / "receipts"),
            ]
            for path, expected in [(root / "missing.elf", 2), (ee, 1)]:
                result = subprocess.run(
                    [*base, "--ee", str(path)], capture_output=True, text=True
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                report = json.loads(
                    Path(json.loads(result.stdout)["result"]).read_text()
                )
                self.assertEqual(
                    report["status"], {1: "fail", 2: "incomplete"}[expected]
                )

    def test_invalid_packet_retains_exact_input_identity(self):
        with self.assertRaises(Invalid) as caught:
            decode_volume_batch(b"")
        self.assertEqual(
            caught.exception.details["input_sha256"],
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )


class StreamHandoffControls(unittest.TestCase):
    def _images(self):
        # EE: bind site (service 0x12345) at 0x1008, call site (command 0) at 0x1024.
        ee_text = struct.pack(
            "<14I",
            0x3C100036,
            0x26049280,
            0x3C050001,
            0x34A52345,
            0x0C000000,
            0x00000000,
            0x3C040036,
            0x24849280,
            0x34050000,
            0x3C070023,
            0x24E76440,
            0x0C000000,
            0x00000000,
            0x00000000,
        )
        # STREAM: register site (service 0x12345, handler 0xD410) at 0xD4F0.
        iop_text = struct.pack(
            "<8I",
            0x3C050001,
            0x34A52345,
            0x3C060000,
            0x24C6D410,
            0x3C070002,
            0x24E732A0,
            0x0C000000,
            0x00000000,
        )
        return ee_text, iop_text

    def test_name_only_handler_without_registration_stays_incomplete(self):
        from inventory_rpc_handoffs import join_handoffs

        binds = [{"site": 0x1000, "client_record": 0x359280, "service_id": 0x12345}]
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
        rows = join_handoffs(binds, calls, [])
        self.assertEqual(rows[0]["status"], "incomplete")

    def test_unbound_shared_buffer_without_caller_group_stays_incomplete(self):
        from inventory_rpc_handoffs import join_handoffs

        binds = [{"site": 0x2000, "client_record": 0x359284, "service_id": 0x99999}]
        registers = [
            {"site": 0x3000, "service_id": 0x12345, "handler": 0xD410, "queue": 0x232A0}
        ]
        rows = join_handoffs(binds, [], registers)
        self.assertEqual(rows[0]["status"], "incomplete")

    def test_register_decoder_flows_through_public_child_seam(self):
        from rpc_handoffs import decode_register_sites

        _, iop_text = self._images()
        stream = build_elf([Spec(".text", iop_text, flags=6, address=0xD4D8)])
        sites = decode_register_sites(stream, 0xD4F0)
        self.assertEqual(sites[0]["service_id"], 0x12345)


if __name__ == "__main__":
    unittest.main()
