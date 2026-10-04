import unittest

from small_data_plan import build_plan

GP = 0x295D70
SDATA = {"name": ".sdata", "start": "0028ec00", "end": "002905c6"}
SBSS = {"name": ".sbss", "start": "00290600", "end": "00290b23"}
LIT4 = {"name": ".lit4", "start": "0028dd80", "end": "0028ebc3"}
HASHES = "ab" * 32


def fn(entry, *texts):
    return {"entry": entry, "instructions": [{"address": f"{0x100000 + 4 * i:08x}", "text": t} for i, t in enumerate(texts)]}


def plan_for(*functions):
    result = build_plan({"memory": [SDATA, SBSS, LIT4], "functions": list(functions)}, GP, HASHES)
    return {e["address"]: e for e in result["entries"]}, result


class RulesTest(unittest.TestCase):
    def test_a_float_access_makes_a_word_global_float(self):
        entries, _ = plan_for(fn("00100000", "lwc1 f0,-0x6ee8(gp)", "swc1 f1,-0x6ee8(gp)"))
        self.assertEqual(entries["0028ee88"]["type"], "float")
        self.assertEqual(entries["0028ee88"]["evidence"], {"lwc1": 1, "swc1": 1})

    def test_float_wins_when_an_integer_copy_also_touches_the_word(self):
        entries, _ = plan_for(fn("00100000", "lwc1 f0,-0x6ee8(gp)", "lw v0,-0x6ee8(gp)"))
        self.assertEqual(entries["0028ee88"]["type"], "float")

    def test_integer_only_words_are_not_typed(self):
        entries, result = plan_for(fn("00100000", "lw v0,-0x6ee8(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["integer_or_pointer_word"], 1)

    def test_signed_and_unsigned_bytes_and_halves(self):
        entries, _ = plan_for(fn("00100000", "lb v0,-0x6ee8(gp)", "lbu v0,-0x6ee4(gp)", "lh v0,-0x6ee0(gp)", "lhu v0,-0x6ede(gp)"))
        self.assertEqual([entries[a]["type"] for a in ("0028ee88", "0028ee8c", "0028ee90", "0028ee92")],
                         ["char", "uchar", "short", "ushort"])

    def test_signed_load_beats_unsigned_load_at_one_address(self):
        entries, _ = plan_for(fn("00100000", "lbu v0,-0x6ee8(gp)", "lb v1,-0x6ee8(gp)"))
        self.assertEqual(entries["0028ee88"]["type"], "char")

    def test_store_only_bytes_have_no_sign_evidence(self):
        entries, result = plan_for(fn("00100000", "sb v0,-0x6ee8(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["no_sign_evidence"], 1)

    def test_mixed_widths_are_skipped(self):
        entries, result = plan_for(fn("00100000", "lw v0,-0x6ee8(gp)", "lbu v1,-0x6ee8(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["mixed_widths"], 1)


class ExclusionTest(unittest.TestCase):
    def test_address_taken_globals_are_skipped(self):
        entries, result = plan_for(fn("00100000", "addiu v0,gp,-0x6ee8", "lwc1 f0,-0x6ee8(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["address_taken"], 1)

    def test_indexed_array_bases_are_skipped(self):
        entries, result = plan_for(fn("00100000", "addu at,v0,gp", "lhu v1,-0x6ee8(at)", "lhu v1,-0x6ee8(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["address_taken"], 1)

    def test_delay_slot_prefix_is_read(self):
        entries, _ = plan_for(fn("00100000", "_lwc1 f0,-0x6ee8(gp)"))
        self.assertEqual(entries["0028ee88"]["type"], "float")

    def test_addresses_outside_small_data_blocks_are_skipped(self):
        entries, result = plan_for(fn("00100000", "lwc1 f0,0x7000(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["outside_small_data"], 1)

    def test_a_word_spanning_a_neighbour_is_skipped(self):
        entries, result = plan_for(fn("00100000", "lwc1 f0,-0x6ee8(gp)", "lbu v0,-0x6ee6(gp)"))
        self.assertEqual(entries, {})
        self.assertEqual(result["skipped"]["overlaps_neighbour"], 2)


class LiteralPoolTest(unittest.TestCase):
    # .lit4 holds 0x28dd80..0x28ebc3; gp 0x295d70 - 0x7f90 = 0x28dde0
    def test_float_loads_from_the_literal_pool_type_the_constant_and_mark_it_constant(self):
        entries, result = plan_for(fn("00100000", "lwc1 f0,-0x7f90(gp)", "lwc1 f1,-0x7f8c(gp)"))
        self.assertEqual({a: e["type"] for a, e in entries.items()}, {"0028dde0": "float", "0028dde4": "float"})
        self.assertEqual({e["mutability"] for e in entries.values()}, {"constant"})
        self.assertEqual(result["constant_pool"], {"name": ".lit4", "start": "0028dd80", "end": "0028ebc3",
                                                   "addresses": 2, "reads": 2, "writes": 0})

    def test_small_data_entries_outside_the_pool_have_no_mutability(self):
        entries, _ = plan_for(fn("00100000", "lwc1 f0,-0x6ee8(gp)"))
        self.assertNotIn("mutability", entries["0028ee88"])

    def test_one_store_into_the_pool_withdraws_the_constant_proposal(self):
        entries, result = plan_for(fn("00100000", "lwc1 f0,-0x7f90(gp)", "swc1 f1,-0x7f90(gp)", "lwc1 f1,-0x7f8c(gp)"))
        self.assertIsNone(result["constant_pool"])
        self.assertEqual(result["skipped"]["written_literal_pool"], 1)
        self.assertNotIn("mutability", entries["0028dde4"])

    def test_an_address_taken_pool_entry_withdraws_the_constant_proposal(self):
        entries, result = plan_for(fn("00100000", "addiu v0,gp,-0x7f90", "lwc1 f0,-0x7f8c(gp)"))
        self.assertIsNone(result["constant_pool"])

    def test_integer_loads_from_the_pool_are_not_typed_but_do_not_block_the_proposal(self):
        entries, result = plan_for(fn("00100000", "lw v0,-0x7f90(gp)", "lwc1 f0,-0x7f8c(gp)"))
        self.assertEqual(list(entries), ["0028dde4"])
        self.assertEqual(result["constant_pool"]["writes"], 0)


class MemoryMapTest(unittest.TestCase):
    def test_overlay_blocks_without_plain_hex_addresses_are_ignored(self):
        overlay = {"name": ".DVP.overlay", "start": ".DVP.overlay..0x0::00000000", "end": ".DVP.overlay..0x0::0000ffff"}
        result = build_plan({"memory": [overlay, SDATA], "functions": [fn("00100000", "lwc1 f0,-0x6ee8(gp)")]}, GP, HASHES)
        self.assertEqual(result["type_counts"], {"float": 1})


class ReportTest(unittest.TestCase):
    def test_entries_name_the_functions_that_touch_them_and_pin_the_export(self):
        entries, result = plan_for(fn("00100000", "lwc1 f0,-0x6ee8(gp)"), fn("00100100", "swc1 f0,-0x6ee8(gp)"))
        self.assertEqual(entries["0028ee88"]["functions"], ["00100000", "00100100"])
        self.assertEqual(result["inventory_sha256"], HASHES)
        self.assertEqual(result["gp_value"], "00295d70")


if __name__ == "__main__":
    unittest.main()
