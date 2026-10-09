import hashlib
import struct
import unittest

from elf_fixture import Spec, build_elf
from ps2_executables import parse_elf
from test_text_denominator import ADDIU_SP, JR_RA, LW_RA, NOP

BASE = 0x1000
TABLE_ADDRESS = 0x2000


def _image(text_words, table_words=()):
    """Executable carrying text_words at BASE plus an optional table at TABLE_ADDRESS.

    Sections come from tools/elf_fixture.py; the PT_LOAD program headers are
    patched in afterwards because the inventory check requires section-to-LOAD
    agreement (tools/test_linker_layout.py pattern).
    """
    specs = [
        Spec(
            ".text",
            struct.pack(f"<{len(text_words)}I", *text_words),
            flags=6,
            address=BASE,
        )
    ]
    if table_words:
        specs.append(
            Spec(
                ".data",
                struct.pack(f"<{len(table_words)}I", *table_words),
                flags=2,
                address=TABLE_ADDRESS,
            )
        )
    data = bytearray(build_elf(specs))
    sections = [
        section
        for section in parse_elf(bytes(data))["sections"]
        if section.get("name") in (".text", ".data")
    ]
    programs_at = len(data)
    for section in sections:
        permissions = (
            4 | (2 if section["flags"] & 1 else 0) | (1 if section["flags"] & 4 else 0)
        )
        data.extend(
            struct.pack(
                "<8I",
                1,
                section["offset"],
                section["address"],
                section["address"],
                section["size"],
                section["size"],
                permissions,
                16,
            )
        )
    struct.pack_into("<I", data, 28, programs_at)
    struct.pack_into("<H", data, 44, len(sections))
    return bytes(data)


def build(text_words, owned, table_words=()):
    data = _image(text_words, table_words)
    rows = [
        {
            "address": f"{BASE + 4 * i:08x}",
            "bytes": struct.pack("<I", text_words[i]).hex(),
        }
        for i in sorted(owned)
    ]
    return data, {
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
        data, static = build(owned + [ADDIU_SP, LW_RA, JR_RA, NOP], range(4))
        result = inventory(data, static)
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

        words = switch_words() + [JR_RA, NOP]
        data, static = build(words, range(len(words)), [BASE + 36, BASE + 40])
        result = inventory(data, static)
        self.assertEqual(len(result["dispatches"]), 1)
        dispatch = result["dispatches"][0]
        self.assertEqual(dispatch["site"], f"{BASE + 28:08x}")
        self.assertEqual(dispatch["table"], "00002000")
        self.assertEqual(dispatch["count"], 2)
        self.assertEqual(dispatch["targets"], [f"{BASE + 36:08x}", f"{BASE + 40:08x}"])
        self.assertTrue(dispatch["falsifier"])

    def test_switch_inside_an_unlisted_span_is_inventoried_without_an_owner(self):
        from dispatch_inventory import inventory

        owned = [ADDIU_SP, LW_RA, JR_RA, NOP]
        words = owned + switch_words() + [JR_RA, NOP]
        data, static = build(words, range(4), [BASE + 52, BASE + 56])
        result = inventory(data, static)
        self.assertEqual(len(result["dispatches"]), 1)
        dispatch = result["dispatches"][0]
        self.assertEqual(dispatch["site"], f"{BASE + 44:08x}")
        self.assertIsNone(dispatch["owner_entry"])
        self.assertEqual(dispatch["span"], f"{BASE + 16:08x}")
        self.assertEqual(dispatch["domain"], "single_span")
        self.assertTrue(dispatch["falsifier"])
        self.assertEqual(result["refused_dispatches"], [])
        self.assertEqual(result["summary"]["refused_dispatches"], 0)

    def test_recognized_switch_with_unreadable_table_is_refused_not_silent(self):
        from dispatch_inventory import inventory

        words = switch_words(table_hi=0x10, table_lo=0) + [JR_RA, NOP]
        data, static = build(words, range(len(words)), [BASE + 36, BASE + 40])
        result = inventory(data, static)
        self.assertEqual(result["dispatches"], [])
        self.assertEqual(len(result["refused_dispatches"]), 1)
        refused = result["refused_dispatches"][0]
        self.assertEqual(refused["site"], f"{BASE + 28:08x}")
        self.assertEqual(refused["table"], "00100000")
        self.assertEqual(refused["count"], 2)
        self.assertTrue(refused["reason"])
        self.assertTrue(refused["falsifier"])
        self.assertEqual(result["summary"]["refused_dispatches"], 1)


if __name__ == "__main__":
    unittest.main()
