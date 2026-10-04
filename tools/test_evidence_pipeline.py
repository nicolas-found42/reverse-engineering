"""Tests at the issue's public CLI boundaries; no game media required."""

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

TOOLS = Path(__file__).resolve().parent


class EvidenceCommands(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def command(self, script, *args):
        out = self.root / "results"
        p = subprocess.run(
            [
                sys.executable,
                str(TOOLS / script),
                *map(str, args),
                "--output",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        reports = sorted(out.glob("*/result.json"), key=lambda p: p.stat().st_mtime_ns)
        self.assertTrue(reports, p.stderr)
        result = json.loads(reports[-1].read_text())
        self.assertTrue(reports[-1].with_name("report.md").exists())
        return p.returncode, result

    def archive(self, blob=b"abc", stored=None):
        record = b"asset;1\0".ljust(16, b"\0") + struct.pack(
            "<III", 0xFFFFFFFF, 0, len(blob) if stored is None else stored
        )
        hdr = struct.pack("<IIII", 1, 1, 0, 1) + record
        return self.write("hdr", hdr), self.write("dat", blob)

    def test_archive_checks_output_and_short_reads(self):
        hdr, dat = self.archive()
        code, result = self.command("verify_formats.py", "archive", hdr, dat)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(
            result["details"]["files"][0]["output_sha256"],
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        hdr, dat = self.archive(stored=4)
        code, result = self.command("verify_formats.py", "archive", hdr, dat)
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertIn("span", " ".join(result["diagnostics"]))

    def test_archive_rejects_cycles_truncation_and_corrupt_zlib(self):
        hdr, dat = self.archive(struct.pack("<I", 3) + zlib.compress(b"abc"))
        code, result = self.command("verify_formats.py", "archive", hdr, dat)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(result["details"]["counts"]["zlib"], 1)
        original = hdr.read_bytes()
        cases = [
            original[:3],
            original[:-1],
            original[:12] + struct.pack("<I", 2) + original[16:],
        ]
        for bad in cases:
            hdr.write_bytes(bad)
            code, result = self.command("verify_formats.py", "archive", hdr, dat)
            self.assertEqual((code, result["status"]), (1, "fail"))
            self.assertTrue(result["diagnostics"])
        hdr.write_bytes(original[:32] + struct.pack("<I", 0) + original[36:])
        code, result = self.command("verify_formats.py", "archive", hdr, dat)
        self.assertEqual(code, 1)
        self.assertIn("cycle", " ".join(result["diagnostics"]))
        hdr.write_bytes(original)
        for blob in [
            struct.pack("<I", 4) + zlib.compress(b"abc"),
            struct.pack("<I", 3) + zlib.compress(b"abc")[:-1],
            struct.pack("<I", 3) + b"\x78\xdaINVALID",
        ]:
            hdr, dat = self.archive(blob)
            code, result = self.command("verify_formats.py", "archive", hdr, dat)
            self.assertEqual((code, result["status"]), (1, "fail"))

    def test_bank_preserves_unusual_rates_and_rejects_broken_chains(self):
        bank = self.write("bank", b"abc")
        desc = self.write("desc", struct.pack("<7I", 28, 36, 1, 3, 99, 0, 2))
        code, result = self.command("verify_formats.py", "bank", desc, bank)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(result["details"]["descriptors"][0]["rate"], 2)
        for raw in [
            b"",
            struct.pack("<3I", 12, 36, 0),
            struct.pack("<7I", 28, 36, 1, 3, 99, 1, 22050),
            desc.read_bytes()[:-1],
        ]:
            desc.write_bytes(raw)
            code, result = self.command("verify_formats.py", "bank", desc, bank)
            self.assertEqual((code, result["status"]), (1, "fail"))

    def test_model_exact_pool_boundary_and_terminated_names(self):
        model = self.write(
            "model", struct.pack("<5I", 77, 1, 20, 1, 22) + b"A\0B\0GEOMETRY"
        )
        code, result = self.command("verify_formats.py", "model", model)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(result["details"]["string_pool_start"], 20)
        self.assertEqual(result["details"]["leading_count"], 77)
        original = model.read_bytes()
        for raw in [
            b"",
            original[:8],
            original[:8] + struct.pack("<I", 400) + original[12:],
            original[:20] + b"NO TERMINATOR",
            original[:16] + struct.pack("<I", 16) + original[20:],
        ]:
            model.write_bytes(raw)
            code, result = self.command("verify_formats.py", "model", model)
            self.assertEqual((code, result["status"]), (1, "fail"))

    def test_sprite_pixel_digest_and_bounds(self):
        header = struct.pack("<8I", 1, 0, 0, 4, 32, 2, 2, 1)
        # Literal first block from measured ordering; four 64-entry blocks.
        order = (
            list(range(8))
            + list(range(16, 24))
            + list(range(8, 16))
            + list(range(24, 32))
        )
        table = b"".join(
            bytes([227, 227, 227, i + base])
            for base in range(0, 256, 32)
            for i in order
        )
        raw = header + table + bytes([1, 2, 221, 221, 3, 4, 221, 221])
        sprite = self.write("sprite", raw)
        code, result = self.command("verify_formats.py", "sprite", sprite)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(
            result["details"]["pixel_sha256"],
            "9f64a747e1b97f131fabb6b447296c9b6f0201e79fb3c5356e6c77e89b6a806a",
        )
        for bad in [
            b"",
            raw[:35],
            raw[:-1],
            raw[:20] + struct.pack("<I", 5) + raw[24:],
            raw[:-1] + b"X",
            raw[:36] + b"XXXX" + raw[40:],
        ]:
            sprite.write_bytes(bad)
            code, result = self.command("verify_formats.py", "sprite", sprite)
            self.assertEqual((code, result["status"]), (1, "fail"))

    def test_missing_corpus_is_incomplete_and_preserves_previous_runs(self):
        code, result = self.command("verify_formats.py", "corpus", self.root / "absent")
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        self.assertTrue(result["diagnostics"])
        hdr, dat = self.archive()
        self.command("verify_formats.py", "archive", hdr, dat)
        self.command("verify_formats.py", "archive", hdr, self.root / "missing")
        self.assertEqual(len(list((self.root / "results").glob("*/result.json"))), 3)

    def test_static_inventory_beyond_200_and_missing_evidence(self):
        executable = self.write("executable", b"ELF fixture")
        functions = [
            {
                "entry": f"{0x100000 + i * 4:08x}",
                "name": f"f{i}",
                "size": 4,
                "instructions": [
                    {
                        "address": f"{0x100000 + i * 4:08x}",
                        "bytes": "00000000",
                        "text": "nop",
                        "references": [],
                    }
                ],
                "callers": [],
                "callees": [],
                "blocks": [],
            }
            for i in range(201)
        ]
        export = {
            "schema_version": 1,
            "program": "SLES_517.05",
            "language": "r5900:LE:32:default",
            "ghidra_version": "fixture",
            "executable_sha256": hashlib.sha256(b"ELF fixture").hexdigest(),
            "inventory_count": 201,
            "functions": functions,
            "memory": [{"start": "00100000", "end": "00200000"}],
            "strings": [],
        }
        exported = self.write("export.json", json.dumps(export).encode())
        loader = {
            "schema_version": 1,
            "executable_sha256": export["executable_sha256"],
            "stages": [
                {
                    "stage": stage,
                    "disposition": "accepted",
                    "evidence": [
                        {
                            "function": functions[-1]["entry"],
                            "address": functions[-1]["entry"],
                            "bytes": "00000000",
                        }
                    ],
                }
                for stage in [
                    "initialization",
                    "lookup",
                    "chunk_read",
                    "raw_transfer",
                    "decompression",
                    "consumption",
                ]
            ],
        }
        mapping = self.write("map.json", json.dumps(loader).encode())
        code, result = self.command(
            "verify_static.py",
            "--export",
            exported,
            "--loader-map",
            mapping,
            "--executable",
            executable,
            "--synthetic",
        )
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertEqual(result["details"]["function_count"], 201)
        export["functions"] = functions[:200]
        exported.write_text(json.dumps(export))
        code, result = self.command(
            "verify_static.py",
            "--export",
            exported,
            "--loader-map",
            mapping,
            "--executable",
            executable,
            "--synthetic",
        )
        self.assertEqual((code, result["status"]), (1, "fail"))
        export["functions"] = functions
        exported.write_text(json.dumps(export))
        loader["stages"][0]["disposition"] = "unresolved"
        mapping.write_text(json.dumps(loader))
        code, result = self.command(
            "verify_static.py",
            "--export",
            exported,
            "--loader-map",
            mapping,
            "--executable",
            executable,
            "--synthetic",
        )
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        loader["stages"][0].update(
            disposition="accepted", claim="fixture claim", correlation={"record": 0}
        )
        valid = {
            "claim": "fixture claim",
            "verdict": "verified",
            "action": "auto",
            "confidence": 0.9,
            "probabilities": {
                "supports": 0.95,
                "contradicts": 0.02,
                "says_nothing": 0.03,
            },
        }
        for kind, expected in [
            ("positive", "pass"),
            ("contradicted", "fail"),
            ("unsupported", "incomplete"),
            ("low_confidence", "incomplete"),
            ("malformed", "fail"),
            ("api_error", "fail"),
            ("blocked_intake", "incomplete"),
        ]:
            judgment = json.loads(json.dumps(valid))
            if kind == "contradicted":
                judgment["verdict"] = "contradicted"
            elif kind == "unsupported":
                judgment["verdict"] = "unsupported"
            elif kind == "low_confidence":
                judgment.update(action="review", confidence=0.7)
            elif kind == "malformed":
                judgment["probabilities"]["supports"] = 4
            elif kind == "api_error":
                judgment = {"error": "invalid_response"}
            elif kind == "blocked_intake":
                loader["stages"][0]["disposition"] = "intake_blocked"
            loader["stages"][0]["judgment"] = judgment
            mapping.write_text(json.dumps(loader))
            code, result = self.command(
                "verify_static.py",
                "--export",
                exported,
                "--loader-map",
                mapping,
                "--executable",
                executable,
                "--synthetic",
            )
            self.assertEqual(result["status"], expected, kind)
            loader["stages"][0]["disposition"] = "accepted"

        loader["stages"][0]["judgment"] = dict(valid, action="review", confidence=0.7)
        loader["export_sha256"] = hashlib.sha256(exported.read_bytes()).hexdigest()
        resolution = {
            "reviewer": "synthetic independent reviewer",
            "inputs": {
                "export_sha256": loader["export_sha256"],
                "executable_sha256": export["executable_sha256"],
            },
            "stages": [
                {
                    "claim": "fixture claim",
                    "verdict": "accepted",
                    "rationale": "Fixture reasoner review only; not a game observation.",
                }
            ],
        }
        review = self.write("review.json", json.dumps(resolution).encode())
        loader["reasoner_review"] = {
            "path": review.name,
            "identity": {
                "bytes": review.stat().st_size,
                "sha256": hashlib.sha256(review.read_bytes()).hexdigest(),
            },
        }
        mapping.write_text(json.dumps(loader))
        code, result = self.command(
            "verify_static.py",
            "--export",
            exported,
            "--loader-map",
            mapping,
            "--executable",
            executable,
            "--synthetic",
        )
        self.assertEqual((code, result["status"]), (0, "pass"))
        export["ghidra_version"] = "changed-export"
        exported.write_text(json.dumps(export))
        code, result = self.command(
            "verify_static.py",
            "--export",
            exported,
            "--loader-map",
            mapping,
            "--executable",
            executable,
            "--synthetic",
        )
        self.assertEqual((code, result["status"]), (1, "fail"))
        self.assertIn("stale loader map/export", " ".join(result["diagnostics"]))

    def test_capture_declares_window_requirement_without_launching(self):
        emulator = self.write("emulator", b"not executable")
        config = self.write("settings", b"original settings")
        firmware = self.write("firmware", b"fixture firmware")
        code, result = self.command(
            "capture_runtime.py",
            "--emulator",
            emulator,
            "--config",
            config,
            "--firmware",
            firmware,
        )
        self.assertEqual((code, result["status"]), (2, "incomplete"))
        self.assertIn("debugger windows", " ".join(result["diagnostics"]))
        self.assertEqual(config.read_bytes(), b"original settings")

    def runtime_fixture(self):
        raw, compressed = b"abc", struct.pack("<I", 3) + zlib.compress(b"xyz")
        hdr = struct.pack("<IIII", 1, 2, 0, 2)
        for name, chunk, payload in [("raw", 0, raw), ("zip", 1, compressed)]:
            hdr += name.encode().ljust(16, b"\0") + struct.pack(
                "<III", 0xFFFFFFFF, chunk, len(payload)
            )
        header = self.write("runtime.hdr", hdr)
        data = self.write("runtime.dat", raw.ljust(2048, b"\0") + compressed)
        executable = self.write("runtime.elf", b"ELF fixture")
        captures = []
        for branch, record, payload in [("raw", 0, raw), ("zlib", 1, b"xyz")]:
            for repeat in range(2):
                memory = bytearray(4096)
                memory[0] = repeat
                memory[128:131] = payload
                path = self.write(f"{branch}-{repeat}.ee.bin", memory)
                captures.append(
                    {
                        "event_id": f"{branch}-{repeat}",
                        "branch": branch,
                        "record_id": record,
                        "path": "/" + ("raw" if record == 0 else "zip"),
                        "memory": path.name,
                        "memory_identity": {
                            "bytes": len(memory),
                            "sha256": hashlib.sha256(memory).hexdigest(),
                        },
                        "output": {
                            "guest_address": 128,
                            "bytes": 3,
                            "sha256": hashlib.sha256(payload).hexdigest(),
                        },
                        "entry": {"pc": 64, "registers": {"a2": int(branch == "zlib")}},
                        "exit": {"pc": 68, "registers": {"v0": 128}},
                        "code": [{"guest_address": 64, "bytes_hex": "00000000"}],
                        "procedure": "Synthetic fixture execution; no emulator observation",
                        "mutations": [],
                        "captured_at": "2026-10-04T04:00:00Z",
                        "before_consumption": True,
                    }
                )
        manifest = {
            "schema_version": 1,
            "origin": "synthetic",
            "executable_identity": {
                "bytes": len(b"ELF fixture"),
                "sha256": hashlib.sha256(b"ELF fixture").hexdigest(),
            },
            "archive_identity": {
                "header": {
                    "bytes": len(hdr),
                    "sha256": hashlib.sha256(hdr).hexdigest(),
                },
                "data": {
                    "bytes": data.stat().st_size,
                    "sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                },
            },
            "tools": {"pcsx2": "fixture"},
            "captures": captures,
        }
        evidence = self.write("captures.json", json.dumps(manifest).encode())
        return header, data, executable, evidence, manifest

    def test_runtime_full_buffers_branches_repeats_and_stale_evidence(self):
        hdr, dat, elf, evidence, original = self.runtime_fixture()
        args = [
            "--captures",
            evidence,
            "--header",
            hdr,
            "--data",
            dat,
            "--executable",
            elf,
            "--synthetic",
        ]
        code, result = self.command("verify_runtime.py", *args)
        self.assertEqual((code, result["status"]), (0, "pass"))
        self.assertFalse(result["details"]["fresh_capture"])
        self.assertFalse(result["details"]["milestone_eligible"])
        self.assertFalse(result["details"]["evidence_eligible"])
        for change, status in [
            ("missing_repeat", "incomplete"),
            ("missing_branch", "incomplete"),
            ("stale_executable", "fail"),
            ("wrong_record", "fail"),
            ("short_output", "fail"),
            ("changed_output", "fail"),
            ("host_address", "fail"),
            ("mutation", "incomplete"),
        ]:
            fixture = json.loads(json.dumps(original))
            if change == "missing_repeat":
                fixture["captures"].pop()
            elif change == "missing_branch":
                fixture["captures"] = fixture["captures"][:2]
            elif change == "stale_executable":
                fixture["executable_identity"]["sha256"] = "0" * 64
            elif change == "wrong_record":
                fixture["captures"][0]["record_id"] = 1
            elif change == "short_output":
                fixture["captures"][0]["output"]["bytes"] = 2
            elif change == "changed_output":
                fixture["captures"][0]["output"]["sha256"] = "0" * 64
            elif change == "host_address":
                fixture["captures"][0]["output"]["guest_address"] = 0x7FFF00000000
            elif change == "mutation":
                fixture["captures"][0]["mutations"] = [
                    {"restored": False, "reason": "test"}
                ]
            evidence.write_text(json.dumps(fixture))
            code, result = self.command("verify_runtime.py", *args)
            self.assertEqual(result["status"], status, change)
            if change in {"missing_repeat", "missing_branch"}:
                self.assertEqual(
                    len(result["details"]["comparisons"]), len(fixture["captures"])
                )
            self.assertNotEqual(code, 0, change)
            self.assertTrue(result["diagnostics"])
        evidence.write_text(json.dumps(original))
        memory = self.root / original["captures"][0]["memory"]
        memory.write_bytes(memory.read_bytes()[:-1])
        code, result = self.command("verify_runtime.py", *args)
        self.assertEqual((code, result["status"]), (1, "fail"))

    def test_omitted_required_evidence_is_reported_as_incomplete(self):
        for script, args in [
            ("verify_static.py", []),
            ("verify_runtime.py", []),
            ("verify_formats.py", ["archive"]),
        ]:
            code, result = self.command(script, *args)
            self.assertEqual((code, result["status"]), (2, "incomplete"))
            self.assertTrue(result["diagnostics"])


if __name__ == "__main__":
    unittest.main()
