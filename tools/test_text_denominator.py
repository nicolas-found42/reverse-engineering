import hashlib
import struct
import unittest

from evidence_common import Incomplete, Invalid
from verify_text_denominator import classify_unlisted

BASE = 0x1000
NOP = 0x00000000
JR_RA = 0x03E00008
ADDIU_SP = 0x27BDFFE0
LW_RA = 0x8FBF0010


def elf_with(words):
    """ELF32 MIPS with one executable LOAD segment holding the given words at BASE."""
    payload = b"".join(struct.pack("<I", w) for w in words)
    data = bytearray(84 + len(payload))
    data[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    struct.pack_into("<HHIIIIIHHHHHH", data, 16, 0xFF80, 8, 1, BASE, 52, 0, 1, 52, 32, 1, 40, 0, 0)
    struct.pack_into("<8I", data, 52, 1, 84, BASE, BASE, len(payload), len(payload), 5, 4)
    data[84:] = payload
    return bytes(data)


def elf_with_data(words, data_words):
    """As elf_with, plus a non-executable allocated data section after the payload."""
    base = bytearray(elf_with(words))
    extra = b"".join(struct.pack("<I", w) for w in data_words)
    data_at = len(base)
    shoff = data_at + len(extra)
    base += extra + bytes(40) + struct.pack("<10I", 0, 1, 2, 0x2000, data_at, len(extra), 0, 0, 4, 0)
    struct.pack_into("<I", base, 32, shoff)
    struct.pack_into("<HHH", base, 46, 40, 2, 0)
    return bytes(base)


def static_for(data, owned_words):
    """Export that claims the first owned_words words as one function."""
    rows = [{"address": f"{BASE + 4 * i:08x}", "bytes": bytes(data[84 + 4 * i:88 + 4 * i]).hex()}
            for i in range(owned_words)]
    functions = [{"entry": f"{BASE:08x}", "instructions": rows}] if owned_words else []
    return {"schema_version": 1, "language": "r5900:LE:32:default",
            "executable_sha256": hashlib.sha256(data).hexdigest(),
            "inventory_count": len(functions), "functions": functions}


OWNED = [ADDIU_SP, LW_RA, JR_RA, NOP]


def build(tail, owned=OWNED):
    data = elf_with(list(owned) + list(tail))
    return data, static_for(data, len(owned))


class TextDenominatorTest(unittest.TestCase):
    def test_all_zero_unlisted_span_is_zero_fill_and_bytes_balance(self):
        data, static = build([NOP] * 5)
        result = classify_unlisted(data, static)
        self.assertEqual(result["mapped_executable_bytes"], 36)
        self.assertEqual(result["function_owned_bytes"], 16)
        self.assertEqual(result["classes"]["zero_fill"]["bytes"], 20)
        self.assertEqual(sum(c["bytes"] for c in result["classes"].values()), 20)
        self.assertFalse(result["whole_game_decompiled"])
        self.assertTrue(any("reachability" in limit for limit in result["claim_limits"]))

    def test_valid_shaped_unlisted_words_are_code_shaped(self):
        data, static = build([ADDIU_SP, LW_RA, JR_RA, NOP])
        result = classify_unlisted(data, static)
        self.assertEqual(result["classes"]["code_shaped"]["bytes"], 16)
        self.assertEqual(result["classes"]["code_shaped"]["zero_words"], 1)
        self.assertEqual(result["classes"]["code_shaped"]["with_return"], 1)
        self.assertNotIn("zero_fill", result["classes"])

    def test_words_pointing_into_executable_memory_are_a_pointer_table(self):
        data, static = build([BASE, BASE + 0x10, BASE + 0x08, BASE + 0x04])
        result = classify_unlisted(data, static)
        self.assertEqual(result["classes"]["code_pointer_table"]["bytes"], 16)
        self.assertNotIn("code_shaped", result["classes"])

    def test_invalid_shaped_words_are_other_nonzero(self):
        data, static = build([0x4C000001, 0x4C000002, JR_RA])
        result = classify_unlisted(data, static)
        self.assertEqual(result["classes"]["other_nonzero"]["bytes"], 12)

    def test_single_nonzero_word_is_sparse_not_code_shaped(self):
        data, static = build([NOP, JR_RA, NOP])
        result = classify_unlisted(data, static)
        self.assertEqual(result["classes"]["sparse_nonzero"]["bytes"], 12)
        self.assertNotIn("code_shaped", result["classes"])

    def test_spans_are_split_by_owned_bytes(self):
        data = elf_with([JR_RA, NOP, NOP, ADDIU_SP, LW_RA, JR_RA])
        static = static_for(data, 1)
        static["functions"][0]["instructions"].append(
            {"address": f"{BASE + 12:08x}", "bytes": bytes(data[84 + 12:88 + 12]).hex()})
        result = classify_unlisted(data, static)
        self.assertEqual(result["mapped_executable_bytes"], 24)
        self.assertEqual(result["function_owned_bytes"], 8)
        self.assertEqual(result["classes"]["zero_fill"], {"bytes": 8, "spans": 1, "zero_words": 2, "with_return": 0})
        self.assertEqual(result["classes"]["code_shaped"]["bytes"], 8)
        self.assertEqual(result["classes"]["code_shaped"]["spans"], 1)

    def test_dvp_overlay_source_bytes_are_vu_microcode_not_unknown_data(self):
        from test_ps2_vu import fixture as vu_fixture
        data, _, _ = vu_fixture()
        static = {"schema_version": 1, "language": "r5900:LE:32:default",
                  "executable_sha256": hashlib.sha256(data).hexdigest(),
                  "inventory_count": 0, "functions": []}
        result = classify_unlisted(data, static)
        self.assertEqual(result["classes"]["vu_microcode"]["bytes"], 8)
        self.assertNotIn("other_nonzero", result["classes"])

    def test_owned_words_that_fail_the_shape_filter_make_the_check_incomplete(self):
        data, static = build([JR_RA], owned=[0x4C000001, 0x4C000002, JR_RA])
        with self.assertRaisesRegex(Incomplete, "shape filter"):
            classify_unlisted(data, static)

    def test_owned_and_data_controls_are_reported(self):
        data = elf_with_data(OWNED + [JR_RA], [0x4C000000, 0x4C000001, ADDIU_SP, 0])
        result = classify_unlisted(data, static_for(data, 4))
        self.assertEqual(result["controls"]["owned"], {"nonzero_words": 3, "plausible": 3})
        self.assertEqual(result["controls"]["data"], {"nonzero_words": 3, "plausible": 1})

    def test_coverage_that_disagrees_on_unlisted_bytes_is_invalid(self):
        data, static = build([NOP] * 2)
        good = {"blocks": [{"name": "LOAD_0", "unowned_instruction_bytes": 0, "undefined_bytes": 8,
                            "defined_data_bytes": 0}]}
        self.assertEqual(classify_unlisted(data, static, good)["coverage_cross_check"], {"LOAD_0": 8})
        bad = {"blocks": [{"name": "LOAD_0", "unowned_instruction_bytes": 0, "undefined_bytes": 4,
                           "defined_data_bytes": 0}]}
        with self.assertRaisesRegex(Invalid, "coverage"):
            classify_unlisted(data, static, bad)

    def test_export_for_a_different_executable_is_invalid(self):
        data, static = build([NOP] * 2)
        static["executable_sha256"] = "0" * 64
        with self.assertRaises(Invalid):
            classify_unlisted(data, static)

    def test_export_instruction_bytes_that_differ_from_the_executable_are_invalid(self):
        data, static = build([NOP] * 2)
        static["functions"][0]["instructions"][0]["bytes"] = "01000000"
        with self.assertRaises(Invalid):
            classify_unlisted(data, static)
