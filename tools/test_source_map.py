import unittest

from verify_source_map import build_source_map


def ins(address, text):
    return {"address": f"{address:08x}", "text": text, "bytes": "00000000"}


def function(entry, texts):
    return {"entry": f"{entry:08x}", "name": f"FUN_{entry:08x}",
            "instructions": [ins(entry + 4 * i, t) for i, t in enumerate(texts)]}


def string(address, value, *sites):
    return {"address": f"{address:08x}", "value": value,
            "references": [{"from": f"{a:08x}", "type": "PARAM"} for a in sites]}


def assert_site(entry, line):
    """lui/addiu loading a0 then a call whose delay slot sets a1 to the line."""
    return function(entry, ["lui a0,0x25", "addiu a0,a0,-0x620", "jal 0x00105888", f"_li a1,{line:#x}", "jr ra", "_nop"])


def export(functions, strings):
    return {"functions": functions, "strings": strings}


class SourceMapTest(unittest.TestCase):
    def test_reference_followed_by_a_call_records_file_function_and_line(self):
        static = export([assert_site(0x1000, 628)], [string(0x2000, "../modules4/system/memalloc.c", 0x1004)])
        result = build_source_map(static)
        self.assertEqual(result["files"][0]["path"], "../modules4/system/memalloc.c")
        self.assertEqual(result["files"][0]["functions"], [{"entry": "00001000", "lines": [628]}])
        self.assertEqual(result["summary"]["call_sites_with_line"], 1)

    def test_line_loaded_shortly_before_the_reference_is_found(self):
        early = function(0x1000, ["li a1,0x10", "lui a0,0x25", "addiu a0,a0,-0x620", "jal 0x00105888", "_nop", "jr ra", "_nop"])
        static = export([early], [string(0x2000, "a/b.c", 0x1008)])
        self.assertEqual(build_source_map(static)["files"][0]["functions"][0]["lines"], [16])

    def test_reference_without_a_nearby_call_is_counted_not_guessed(self):
        lone = function(0x1000, ["lui a0,0x25", "addiu a0,a0,-0x620", "nop", "nop", "nop", "nop", "nop", "nop", "nop", "nop", "nop", "nop", "nop", "jal 0x1", "_li a1,0x5", "jr ra"])
        static = export([lone], [string(0x2000, "a/b.c", 0x1004)])
        result = build_source_map(static)
        self.assertEqual(result["summary"]["references_without_line"], 1)
        self.assertEqual(result["files"][0]["functions"], [{"entry": "00001000", "lines": []}])

    def test_only_source_file_strings_with_code_references_are_files(self):
        static = export([assert_site(0x1000, 5)], [string(0x2000, "hello world", 0x1004),
                                                   string(0x2100, "x/y.h", 0x1004), string(0x2200, "z.cpp")])
        self.assertEqual([f["path"] for f in build_source_map(static)["files"]], ["x/y.h"])

    def test_functions_of_one_file_report_their_address_range_and_density(self):
        fns = [assert_site(0x1000, 10), function(0x1100, ["jr ra", "_nop"]), assert_site(0x1200, 30)]
        static = export(fns, [string(0x2000, "a/b.c", 0x1004, 0x1204)])
        file = build_source_map(static)["files"][0]
        self.assertEqual(file["ranges"], [{"block": "all", "first": "00001000", "last": "00001200",
                                           "referencing_functions": 2, "functions_in_range": 3}])

    def test_line_order_against_address_order_is_compared_with_a_shuffled_control(self):
        fns = [assert_site(0x1000 + 0x100 * i, 10 * (i + 1)) for i in range(6)]
        static = export(fns, [string(0x2000, "a/b.c", *[0x1004 + 0x100 * i for i in range(6)])])
        order = build_source_map(static, control_trials=50, seed=3)["line_order"]
        self.assertEqual(order["pairs"], 5)
        self.assertEqual(order["inversions"], 0)
        self.assertGreater(order["shuffled_inversion_rate"], 0.2)

    def test_files_whose_address_ranges_overlap_are_counted(self):
        fns = [assert_site(0x1000, 1), assert_site(0x1100, 2), assert_site(0x1200, 3), assert_site(0x1300, 4)]
        static = export(fns, [string(0x2000, "a.c", 0x1004, 0x1204), string(0x2100, "b.c", 0x1104, 0x1304)])
        self.assertEqual(build_source_map(static)["summary"]["overlapping_file_pairs"], 1)

    def test_ranges_are_kept_per_memory_block_so_split_files_do_not_overlap_everything(self):
        fns = [assert_site(0x1000, 1), assert_site(0x1100, 2), assert_site(0x9000, 3), assert_site(0x1200, 4)]
        static = export(fns, [string(0x2000, "a.c", 0x1004, 0x9004), string(0x2100, "b.c", 0x1104, 0x1204)])
        static["memory"] = [{"name": ".text", "start": "00001000", "end": "00001fff"},
                            {"name": ".user_section1", "start": "00009000", "end": "00009fff"}]
        result = build_source_map(static)
        a = next(f for f in result["files"] if f["path"] == "a.c")
        self.assertEqual([(r["block"], r["first"]) for r in a["ranges"]],
                         [(".text", "00001000"), (".user_section1", "00009000")])
        self.assertEqual(result["summary"]["overlapping_file_pairs"], 0)

    def test_headers_are_listed_but_excluded_from_unit_layout_tests(self):
        fns = [assert_site(0x1000, 1), assert_site(0x1100, 2), assert_site(0x1200, 3), assert_site(0x1300, 4)]
        static = export(fns, [string(0x2000, "a.c", 0x1004, 0x1204), string(0x2100, "inline.h", 0x1104, 0x1304)])
        result = build_source_map(static)
        self.assertEqual({f["path"]: f["kind"] for f in result["files"]}, {"a.c": "unit", "inline.h": "header"})
        self.assertEqual(result["summary"]["overlapping_file_pairs"], 0)
        self.assertEqual(result["line_order"]["pairs"], 1)

    def test_overlay_address_space_blocks_do_not_break_block_lookup(self):
        static = export([assert_site(0x1000, 1)], [string(0x2000, "a.c", 0x1004)])
        static["memory"] = [{"name": ".DVP.overlay..x", "start": ".DVP.overlay..x::00000000", "end": ".DVP.overlay..x::000007ff"},
                            {"name": ".text", "start": "00001000", "end": "00001fff"}]
        self.assertEqual(build_source_map(static)["files"][0]["ranges"][0]["block"], ".text")

    def test_result_states_what_a_reference_does_not_prove(self):
        static = export([assert_site(0x1000, 1)], [string(0x2000, "a/b.c", 0x1004)])
        self.assertTrue(any("not" in limit for limit in build_source_map(static)["claim_limits"]))


def message(address, text, *functions_sites):
    return {"address": f"{address:08x}", "value": text,
            "references": [{"from": f"{a:08x}", "function": f"{e:08x}", "type": "PARAM"} for e, a in functions_sites]}


def plain(entry, texts=("lui a0,0x25", "addiu a0,a0,-0x620", "jr ra", "_nop")):
    return function(entry, list(texts))


class StringAttributionTest(unittest.TestCase):
    def layout(self, extra_strings, extra_functions):
        functions = [assert_site(0x1000, 10), assert_site(0x1100, 20), *extra_functions]
        strings = [string(0x2000, "a.c", 0x1004), string(0x2100, "b.c", 0x1104), *extra_strings]
        return export(functions, strings)

    def test_function_using_only_other_strings_is_attributed_to_the_unit_whose_string_block_holds_them(self):
        static = self.layout([message(0x2010, "msg A", (0x1300, 0x1304)), message(0x2110, "msg B", (0x1400, 0x1404))],
                             [plain(0x1300), plain(0x1400)])
        attribution = build_source_map(static)["string_attribution"]
        self.assertEqual({row["entry"]: row["unit"] for row in attribution["functions"]},
                         {"00001300": "a.c", "00001400": "b.c"})

    def test_known_functions_are_checked_against_their_own_string_block_without_using_the_path_string(self):
        static = self.layout([message(0x2010, "msg A", (0x1000, 0x1008)),      # a.c function, a.c string: agrees
                              message(0x2110, "msg B", (0x1000, 0x1010)),      # same function, outvoted below
                              message(0x2120, "more B", (0x1100, 0x1018))],    # b.c function, b.c string: agrees
                             [])
        check = build_source_map(static)["string_attribution"]
        self.assertEqual((check["agree"], check["disagree"], check["ties"]), (1, 0, 1))
        self.assertEqual(check["functions"], [])

    def test_disagreement_between_a_path_reference_and_the_string_block_is_counted(self):
        static = self.layout([message(0x2110, "msg B", (0x1000, 0x1008))], [])
        check = build_source_map(static)["string_attribution"]
        self.assertEqual((check["agree"], check["disagree"]), (0, 1))

    def test_strings_before_the_first_unit_string_are_not_attributed(self):
        static = self.layout([message(0x1F00, "early", (0x1300, 0x1304))], [plain(0x1300)])
        self.assertEqual(build_source_map(static)["string_attribution"]["functions"], [])
