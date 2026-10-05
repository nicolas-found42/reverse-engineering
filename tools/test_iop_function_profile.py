import unittest

from iop_function_profile import build_profile

IMAGE = bytearray(0x200)
IMAGE[0x100:0x118] = b"ERROR: SOUND_StopDTS\n\x00\x00\x00\x00"
IMAGE[0x120:0x124] = b"ab\x00\x00"
INVENTORY = {"functions": [
    {"entry": "00000000", "name": "FUN_00000000", "instructions": [{"address": f"{a:08x}"} for a in range(0, 0x40, 4)]},
    {"entry": "00000040", "name": "makeThread", "instructions": [{"address": f"{a:08x}"} for a in range(0x40, 0x80, 4)]}]}
IMPORTS = [{"library": "thbase", "version": 258, "index": 4, "stub_text_offset": 0x1F0, "candidate_name": "CreateThread"},
           {"library": "usbd", "version": 257, "index": 5, "stub_text_offset": 0x1F8, "candidate_name": None}]
EXPORTS = [{"library": "lgdev", "version": 264, "links": [{"offset": 0x40}, {"offset": 0x999}]}]
REFS = [
    {"site": 0x08, "kind": "jump", "target": 0x1F0},
    {"site": 0x0C, "kind": "jump", "target": 0x1F0},
    {"site": 0x10, "kind": "jump", "target": 0x1F8},
    {"site": 0x44, "kind": "hi_lo", "lo_site": 0x48, "target": 0x100},
    {"site": 0x4C, "kind": "hi_lo", "lo_site": 0x50, "target": 0x120},
    {"site": 0x140, "kind": "word", "target": 0x40},
]


PROCEDURES = [{"name": "makeThread", "linked_address": 0x40, "file": "stream.c", "frame_bytes": 32, "size": 64,
               "saved_register_mask": 0x80000000}]


def profile(procedures=None):
    return {f["entry"]: f for f in build_profile(INVENTORY, REFS, IMPORTS, EXPORTS, bytes(IMAGE), procedures)["functions"]}


class ProfileTest(unittest.TestCase):
    def test_import_calls_are_listed_once_with_names_or_none(self):
        imports = profile()["00000000"]["imports"]
        self.assertEqual(imports, [{"library": "thbase", "index": 4, "name": "CreateThread"},
                                   {"library": "usbd", "index": 5, "name": None}])

    def test_long_printable_strings_are_attached_and_short_ones_are_not(self):
        self.assertEqual(profile()["00000040"]["strings"], ["ERROR: SOUND_StopDTS\n"])

    def test_exports_match_function_entries_by_offset(self):
        self.assertEqual(profile()["00000040"]["exported_as"], [{"library": "lgdev", "index": 0}])
        self.assertEqual(profile()["00000000"]["exported_as"], [])

    def test_data_pointers_to_a_function_entry_are_counted(self):
        self.assertEqual(profile()["00000040"]["data_pointer_references"], 1)
        self.assertEqual(profile()["00000000"]["data_pointer_references"], 0)

    def test_the_ghidra_name_is_carried_through(self):
        self.assertEqual(profile()["00000040"]["name"], "makeThread")

    def test_debug_procedures_attach_by_linked_address(self):
        p = profile(PROCEDURES)
        self.assertEqual(p["00000040"]["procedure"], {"file": "stream.c", "frame_bytes": 32, "size": 64})
        self.assertIsNone(p["00000000"]["procedure"])

    def test_name_sources_flow_through_to_imports(self):
        imports = [dict(IMPORTS[0], name_source="module symbol table"), IMPORTS[1]]
        result = build_profile(INVENTORY, REFS, imports, EXPORTS, bytes(IMAGE))
        first = result["functions"][0]["imports"]
        self.assertEqual(first[0]["name_source"], "module symbol table")
        self.assertNotIn("name_source", first[1])

    def test_summary_counts(self):
        summary = build_profile(INVENTORY, REFS, IMPORTS, EXPORTS, bytes(IMAGE))["summary"]
        self.assertEqual(summary, {"functions": 2, "calling_imports": 1, "calling_named_imports": 1, "with_strings": 1,
                                   "exported": 1, "with_debug_procedure": 0, "export_offsets_without_function": 1})


if __name__ == "__main__":
    unittest.main()
