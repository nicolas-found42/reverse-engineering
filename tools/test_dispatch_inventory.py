import hashlib
import unittest

from test_text_denominator import ADDIU_SP, BASE, JR_RA, LW_RA, NOP, elf_with


def static_owning(data, owned):
    rows = [
        {
            "address": f"{BASE + 4 * i:08x}",
            "bytes": bytes(data[84 + 4 * i : 88 + 4 * i]).hex(),
        }
        for i in sorted(owned)
    ]
    return {
        "schema_version": 1,
        "language": "r5900:LE:32:default",
        "executable_sha256": hashlib.sha256(data).hexdigest(),
        "inventory_count": 1,
        "functions": [{"entry": rows[0]["address"], "instructions": rows}],
    }


class DispatchInventoryTest(unittest.TestCase):
    def test_every_unlisted_span_carries_classification_references_reason_and_falsifier(
        self,
    ):
        from dispatch_inventory import inventory

        owned = [ADDIU_SP, LW_RA, JR_RA, NOP]
        data = elf_with(owned + [ADDIU_SP, LW_RA, JR_RA, NOP])
        result = inventory(data, static_owning(data, range(4)))
        self.assertEqual(result["executable_sha256"], hashlib.sha256(data).hexdigest())

        self.assertEqual(len(result["spans"]), 1)
        span = result["spans"][0]
        self.assertEqual(span["address"], f"{BASE + 16:08x}")
        self.assertEqual(span["bytes"], 16)
        self.assertEqual(span["classification"], "code_shaped")
        self.assertEqual(span["incoming"], {})
        self.assertTrue(span["reason"])
        self.assertTrue(span["falsifier"])
        self.assertFalse(result["whole_game_decompiled"])


def switch_words(table_hi=0, table_lo=0x2000, count=2, branch_skip=9):
    from test_jump_table import AT, V0, V1, beq, jr, lw, sltiu, sll, addu, lui, NOP

    return [
        sltiu(V1, V0, count),
        beq(V1, 0, branch_skip),
        sll(V1, V0, 2),
        lui(AT, table_hi),
        addu(AT, AT, V1),
        lw(V0, table_lo, AT),
        NOP,
        jr(V0),
        NOP,
    ]


class DispatchDomainTest(unittest.TestCase):
    def test_recognized_switch_in_owned_code_pins_its_table_and_targets(self):
        from dispatch_inventory import inventory
        from test_text_denominator import elf_with_data

        words = switch_words() + [JR_RA, NOP]
        data = elf_with_data(words, [BASE + 36, BASE + 40])
        result = inventory(data, static_owning(data, range(len(words))))
        self.assertEqual(len(result["dispatches"]), 1)
        dispatch = result["dispatches"][0]
        self.assertEqual(dispatch["site"], f"{BASE + 28:08x}")
        self.assertEqual(dispatch["table"], "00002000")
        self.assertEqual(dispatch["count"], 2)
        self.assertEqual(dispatch["targets"], [f"{BASE + 36:08x}", f"{BASE + 40:08x}"])
        self.assertTrue(dispatch["falsifier"])

    def test_switch_inside_an_unlisted_span_is_inventoried_without_an_owner(self):
        from dispatch_inventory import inventory
        from test_text_denominator import elf_with_data

        owned = [ADDIU_SP, LW_RA, JR_RA, NOP]
        words = owned + switch_words() + [JR_RA, NOP]
        data = elf_with_data(words, [BASE + 52, BASE + 56])
        result = inventory(data, static_owning(data, range(4)))
        self.assertEqual(len(result["dispatches"]), 1)
        dispatch = result["dispatches"][0]
        self.assertEqual(dispatch["site"], f"{BASE + 44:08x}")
        self.assertIsNone(dispatch["owner_entry"])
        self.assertEqual(dispatch["span"], f"{BASE + 16:08x}")
        self.assertEqual(dispatch["domain"], "single_span")
        self.assertTrue(dispatch["falsifier"])


if __name__ == "__main__":
    unittest.main()
