import hashlib
import unittest

from test_text_denominator import (
    ADDIU_SP,
    BASE,
    JR_RA,
    LW_RA,
    NOP,
    elf_with,
    elf_with_data,
)
from verify_text_references import find_span_references

CODE = [ADDIU_SP, LW_RA, JR_RA, NOP]


def jal(target):
    return (3 << 26) | ((target >> 2) & 0x3FFFFFF)


def beq_zero(pc, target):
    return (4 << 26) | (((target - (pc + 4)) >> 2) & 0xFFFF)


def lui(rt, hi):
    return (0x0F << 26) | (rt << 16) | hi


def addiu(rt, rs, imm):
    return (9 << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)


def addr(index):
    return BASE + 4 * index


def static_owning(data, owned):
    """Export whose single function owns exactly the word indices in owned."""
    rows = [{"address": f"{addr(i):08x}", "bytes": bytes(data[84 + 4 * i:88 + 4 * i]).hex()}
            for i in sorted(owned)]
    return {"schema_version": 1, "language": "r5900:LE:32:default",
            "executable_sha256": hashlib.sha256(data).hexdigest(),
            "inventory_count": 1, "functions": [{"entry": rows[0]["address"], "instructions": rows}]}


def scenario(words, owned, data_words=None):
    data = elf_with_data(words, data_words) if data_words else elf_with(words)
    return data, static_owning(data, owned)


def span_at(result, address):
    return next(s for s in result["spans"] if s["address"] == f"{address:08x}")


class TextReferencesTest(unittest.TestCase):
    def test_direct_call_from_owned_code_anchors_the_target_span(self):
        data, static = scenario([jal(addr(4)), NOP, JR_RA, NOP] + CODE, owned=range(4))
        span = span_at(find_span_references(data, static), addr(4))
        self.assertEqual(span["incoming"], {"owned_direct": 1})
        self.assertEqual(span["targets"], [f"{addr(4):08x}"])
        self.assertTrue(span["anchored"] and span["reached"])

    def test_branch_from_owned_code_into_a_span_is_an_owned_direct_reference(self):
        data, static = scenario([beq_zero(addr(0), addr(6)), NOP, JR_RA, NOP] + CODE, owned=range(4))
        span = span_at(find_span_references(data, static), addr(4))
        self.assertEqual(span["incoming"], {"owned_direct": 1})
        self.assertEqual(span["targets"], [f"{addr(6):08x}"])

    def test_aligned_data_pointer_anchors_and_misaligned_is_only_counted_as_control(self):
        data, static = scenario([JR_RA, NOP, NOP, NOP] + CODE, owned=range(1),
                                data_words=[addr(5), addr(5) + 1, addr(0), 7])
        result = find_span_references(data, static)
        span = span_at(result, addr(1))
        self.assertEqual(span["incoming"], {"data_pointer": 1})
        self.assertEqual(span["targets"], [f"{addr(5):08x}"])
        self.assertEqual(result["controls"]["data_words_in_executable_range"],
                         {"aligned": 2, "misaligned": 1})
        self.assertEqual(result["controls"]["data_words_at_function_entries"], 1)

    def test_lui_addiu_constant_in_owned_code_is_an_address_constant_reference(self):
        owned = [lui(8, 0), NOP, addiu(4, 8, addr(6)), JR_RA]
        data, static = scenario(owned + CODE, owned=range(4))
        span = span_at(find_span_references(data, static), addr(4))
        self.assertEqual(span["incoming"], {"owned_address_constant": 1})
        self.assertEqual(span["targets"], [f"{addr(6):08x}"])

    def test_span_is_reached_only_through_an_anchored_span_and_orphans_stay_unreached(self):
        words = ([jal(addr(4)), NOP, JR_RA, NOP]            # 0-3 owned, calls A
                 + [ADDIU_SP, jal(addr(9)), JR_RA, NOP]    # 4-7 span A, calls B
                 + [JR_RA]                                  # 8 owned
                 + CODE                                     # 9-12 span B
                 + [JR_RA]                                  # 13 owned
                 + CODE)                                    # 14-17 span C, no references
        data, static = scenario(words, owned=[0, 1, 2, 3, 8, 13])
        result = find_span_references(data, static)
        a, b, c = (span_at(result, addr(i)) for i in (4, 9, 14))
        self.assertEqual((a["anchored"], a["reached"]), (True, True))
        self.assertEqual(b["incoming"], {"span_direct": 1})
        self.assertEqual((b["anchored"], b["reached"]), (False, True))
        self.assertEqual((c["incoming"], c["anchored"], c["reached"]), ({}, False, False))
        self.assertEqual(result["summary"], {
            "anchored": {"spans": 1, "bytes": 16}, "reached_via_spans_only": {"spans": 1, "bytes": 16},
            "unreferenced": {"spans": 1, "bytes": 16}})

    def test_references_that_do_not_land_in_code_shaped_spans_are_ignored(self):
        data, static = scenario([jal(addr(0)), NOP, JR_RA, NOP] + CODE, owned=range(4))
        result = find_span_references(data, static)
        self.assertEqual(span_at(result, addr(4))["incoming"], {})
