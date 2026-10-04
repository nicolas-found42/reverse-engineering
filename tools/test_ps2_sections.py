"""Public section-chain parser and verifier contracts from FUN_0011ed90."""
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

import ps2_sections
from evidence_common import Incomplete, Invalid
from test_ps2_textures import container

TOOLS = Path(__file__).resolve().parent
GAME = TOOLS.parent / "games/ford-racing-2"


def fixture(record=b"", allocations=None):
    """Literal worked example: no geometry headers; 17 globals; 5 trailing counts."""
    data = bytearray(container([], a=0, b=0, c=0, tail_count=0))
    data += bytes(-len(data) % 16)
    globals_ = [17, int(bool(record))] + [0] * 15
    for index, value in (allocations or {}).items():
        globals_[index] = value
    data += struct.pack("<17I", *globals_) + record + bytes(20)
    data += bytes(-len(data) % 16)
    return bytes(data)


def legacy_fixture(record_data=b"", raw_words=None):
    """Exploratory measured 60-byte profile: 15 raw global words, no 0x11 marker."""
    data = bytearray(container([], a=0, b=0, c=0, tail_count=0))
    data += bytes(-len(data) % 16)
    words = [0] * 15 if raw_words is None else list(raw_words)
    words[0] = int(bool(record_data)) if raw_words is None else words[0]
    data += struct.pack("<15I", *words) + record_data + bytes(20)
    data += bytes(-len(data) % 16)
    return bytes(data)


def record(nodes=b"", capacity=0, options=0, nodes80=b""):
    words = [0xFFFFFFFF] * 4 + [0, 0, 0, 0, 0, 0, options]
    data = struct.pack("<11I", *words)
    if options & 2:
        data += struct.pack("<2I", 0xFFFF, 1) + nodes80
    data += struct.pack("<9I", 0, capacity, 0, 0, 0, 0, 0, 0, int(bool(nodes)))
    return data + nodes


class Chain(unittest.TestCase):
    def test_zero_count_chain_ends_exactly_at_eof(self):
        data = fixture()
        result = ps2_sections.parse(data)
        self.assertTrue(result["exact_eof"])
        self.assertEqual(result["end"], len(data))
        self.assertEqual(result["later"]["global_words"], [17] + [0] * 16)
        self.assertEqual(result["tail"]["final_allocation_counts"], [0, 0, 0])

    def test_a_texture_only_prefix_is_not_a_complete_section_chain(self):
        with self.assertRaises(Invalid):
            ps2_sections.parse(container([], a=0, b=0, c=0, tail_count=0))

    def test_recursive_2c_nodes_use_40_serialized_bytes_and_44_memory_bytes(self):
        # Parent: eight fixed words, pair descriptor=0, child count=1; leaf ends at word 10.
        parent = bytes(36) + struct.pack("<I", 1)
        child = bytes(40)
        data = fixture(record(parent + child, capacity=2), {9: 2})
        result = ps2_sections.parse(data)
        nodes = result["later"]["records"][0]["nodes_2c"]
        self.assertEqual([(n["depth"], n["children"]) for n in nodes], [(0, 1), (1, 0)])
        self.assertEqual(nodes[1]["offset"] - nodes[0]["offset"], 40)
        self.assertEqual(result["later"]["node_counts"]["node_2c"], 2)

    def test_recursive_80_nodes_use_108_serialized_bytes(self):
        parent = bytearray(108)
        struct.pack_into("<I", parent, 12, 1)
        data = fixture(record(options=2, nodes80=bytes(parent) + bytes(108)), {14: 2})
        result = ps2_sections.parse(data)
        nodes = result["later"]["records"][0]["nodes_80"]
        self.assertEqual(nodes[1]["offset"] - nodes[0]["offset"], 108)
        self.assertEqual(result["later"]["node_counts"]["node_80"], 2)

    def test_expanded_memory_records_have_independently_counted_serialized_strides(self):
        source = bytearray(record())
        struct.pack_into("<I", source, 20, 1)
        source[24:24] = bytes(80)
        result = ps2_sections.parse(fixture(bytes(source), {4: 1}))
        self.assertEqual(result["later"]["records"][0]["expanded_70"]["size"], 80)
        source = bytearray(record())
        struct.pack_into("<I", source, 36, 1)
        source[40:40] = bytes(32)
        result = ps2_sections.parse(fixture(bytes(source), {3: 1}))
        self.assertEqual(result["later"]["records"][0]["expanded_24"]["size"], 32)

    def test_in_bounds_payload_with_wrong_allocation_count_fails(self):
        with self.assertRaisesRegex(Invalid, "allocation word 13"):
            ps2_sections.parse(fixture(allocations={13: 1}))

    def test_packed_group_ranges_must_fit_the_packed_entry_allocation(self):
        def grouped_tail(group_count, packed_count=1):
            data = bytearray(container([], a=0, b=0, c=0, tail_count=0))
            data += bytes(-len(data) % 16)
            globals_ = [17, 0] + [0] * 15
            globals_[15] = 1
            data += struct.pack("<17I", *globals_)
            data += struct.pack("<II", packed_count, 0)
            data += struct.pack("<I", group_count)
            data += bytes(packed_count * 4)
            data += bytes(20)  # zero rows and zero final records
            data += bytes(-len(data) % 16)
            return bytes(data)

        # A smaller group range is allowed: unused packed entries may be reserved.
        self.assertTrue(ps2_sections.parse(grouped_tail(0))[
            "exact_eof"])
        with self.assertRaisesRegex(Invalid, "group ranges exceed"):
            ps2_sections.parse(grouped_tail(2))

    def test_truncation_appended_bytes_and_corrupt_final_padding_fail(self):
        data = fixture()
        for blob in (data[:-1], data + bytes(16), data[:-1] + b"\x01"):
            with self.subTest(size=len(blob)), self.assertRaises(Invalid):
                ps2_sections.parse(blob)

    def test_recursive_counts_cannot_exceed_file_or_allocation(self):
        for blob in (fixture(record(bytes(36) + struct.pack("<I", 0xFF), capacity=1)),
                     fixture(record(bytes(40), capacity=0))):
            with self.assertRaises(Invalid):
                ps2_sections.parse(blob)

    def test_unsupported_header_returns_incomplete_with_geometry_evidence(self):
        data = bytearray(fixture())
        parsed = ps2_sections.parse(bytes(data))
        struct.pack_into("<I", data, parsed["later"]["section_start"], 18)
        with self.assertRaises(Incomplete) as caught:
            ps2_sections.parse(bytes(data))
        self.assertEqual(caught.exception.details["observed_first_word"], 18)

    def test_explicit_legacy_profile_maps_and_preserves_its_raw_header(self):
        data = legacy_fixture(record())
        with self.assertRaises(Incomplete):
            ps2_sections.parse(data)
        parsed = ps2_sections.parse(data, later_profile="measured_legacy60")
        later = parsed["later"]
        self.assertEqual(later["profile"], "measured_legacy60")
        self.assertEqual(later["global_header"]["size"], 60)
        self.assertEqual(len(later["global_header"]["raw_words"]), 15)
        self.assertEqual(later["global_words"], [17, 1] + [0] * 15)
        self.assertEqual(later["records"][0]["offset"], later["section_start"] + 60)
        self.assertTrue(parsed["exact_eof"])

    def test_legacy_profile_rejects_truncation_wrong_count_and_allocation_mapping(self):
        data = legacy_fixture(record())
        parsed = ps2_sections.parse(data, later_profile="measured_legacy60")
        header_at = parsed["later"]["section_start"]
        with self.assertRaisesRegex(Invalid, "legacy 15-word global header"):
            ps2_sections.parse(data[:header_at + 59], later_profile="measured_legacy60")
        wrong_count = bytearray(data)
        struct.pack_into("<I", wrong_count, header_at, 2)
        with self.assertRaisesRegex(Invalid, "record 1 sentinel"):
            ps2_sections.parse(bytes(wrong_count), later_profile="measured_legacy60")
        wrong_allocation = bytearray(data)
        struct.pack_into("<I", wrong_allocation, header_at + 4, 1)
        with self.assertRaisesRegex(Invalid, "global allocation word 2"):
            ps2_sections.parse(bytes(wrong_allocation), later_profile="measured_legacy60")

    def test_unknown_later_profile_is_rejected(self):
        with self.assertRaisesRegex(Invalid, "unsupported later-section profile"):
            ps2_sections.parse(fixture(), later_profile="guess")

    def test_seeded_mutations_never_escape_the_bounded_parser_errors(self):
        data = fixture(record(bytes(40), capacity=1), {9: 1})
        rng = random.Random(27)
        rejected = 0
        for i in range(300):
            blob = bytearray(data)
            if i % 2:
                del blob[rng.randrange(len(blob)):]
            else:
                blob[rng.randrange(len(blob))] = rng.randrange(256)
            try:
                ps2_sections.parse(bytes(blob))
            except (Invalid, Incomplete):
                rejected += 1
        self.assertGreater(rejected, 150)


class Cli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def command(self, family, path):
        output = self.root / "results"
        run = subprocess.run([sys.executable, str(TOOLS / "verify_sections.py"), family,
                              str(path), "--output", str(output)], capture_output=True, text=True)
        receipt = json.loads(run.stdout)
        result_path = Path(receipt["result"])
        self.assertTrue(result_path.with_name("report.md").exists())
        return run.returncode, json.loads(result_path.read_text())

    def test_complete_malformed_unsupported_and_missing_inputs_have_distinct_statuses(self):
        path = self.root / "model.ps2"
        path.write_bytes(fixture())
        code, result = self.command("file", path)
        self.assertEqual((code, result["status"], result["details"]["exact_eof"]), (0, "pass", True))
        path.write_bytes(fixture()[:-1])
        code, result = self.command("file", path)
        self.assertEqual((code, result["status"]), (1, "fail"))
        data = bytearray(fixture())
        offset = ps2_sections.parse(bytes(data))["later"]["section_start"]
        struct.pack_into("<I", data, offset, 18)
        path.write_bytes(data)
        code, result = self.command("file", path)
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_file_cli_requires_explicit_legacy_profile_selection(self):
        path = self.root / "legacy.ps2"
        path.write_bytes(legacy_fixture(record()))
        default_code, default = self.command("file", path)
        self.assertEqual((default_code, default["status"]), (2, "incomplete"))
        output = self.root / "legacy-profile-results"
        run = subprocess.run([sys.executable, str(TOOLS / "verify_sections.py"), "file", str(path),
                              "--later-profile", "measured_legacy60", "--output", str(output)],
                             capture_output=True, text=True)
        receipt = json.loads(run.stdout)
        result = json.loads(Path(receipt["result"]).read_text())
        self.assertEqual((run.returncode, result["status"]), (0, "pass"))
        self.assertEqual(result["details"]["later_profile"], "measured_legacy60")
        code, result = self.command("file", self.root / "missing.ps2")
        self.assertEqual((code, result["status"]), (2, "incomplete"))

    def test_real_corpus_uses_hash_bound_profiles_for_56_exact_eof_results(self):
        if not (GAME / "extracted" / "FILES.HDR").exists():
            self.skipTest("real corpus absent; CLI reports incomplete")
        code, result = self.command("corpus", GAME)
        self.assertEqual((code, result["status"]), (0, "pass"))
        details = result["details"]
        self.assertEqual((details["models"], details["exact_eof_models"]), (56, 56))
        self.assertEqual(details["profile_counts"], {"loader68": 54, "measured_legacy60": 2})
        self.assertEqual(details["unsupported"], [])
        self.assertFalse(details["failures"])
        self.assertTrue(all(x["exact_eof"] for x in details["file_results"]))
        self.assertIn("not evidence that the current executable loader supports/selects it", details["claim_limits"])
        profiles = {Path(x["path"]).name: x["later_profile"] for x in details["file_results"]}
        self.assertEqual(profiles["Brands.PS2;1"], "measured_legacy60")
        self.assertEqual(profiles["Canyon.PS2;1"], "measured_legacy60")
        self.assertEqual({Path(x["path"]).name for x in details["file_results"] if x["path"].lower().endswith('/debug.ps2;1') or x["path"].lower().endswith('/misc.ps2;1')}, {"debug.ps2;1", "misc.ps2;1"})


if __name__ == "__main__":
    unittest.main()
