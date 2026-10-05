import unittest

from iop_annotation_plan import build_plan

SHA = "ab" * 32


def func(entry, imports=(), strings=(), exported=(), pointers=0, name=None, procedure=None):
    return {"entry": entry, "name": name or f"FUN_{entry}", "procedure": procedure, "imports": list(imports), "strings": list(strings),
            "exported_as": list(exported), "data_pointer_references": pointers}


def plan(*functions):
    result = build_plan({"functions": list(functions), "module": {"name": "m", "sha256": SHA}}, SHA)
    return {e["entry"]: e for e in result["entries"]}


class CommentTest(unittest.TestCase):
    def test_functions_without_any_fact_get_no_entry(self):
        self.assertEqual(plan(func("00000000")), {})

    def test_imports_are_listed_with_their_name_status(self):
        entry = plan(func("00000000", imports=[{"library": "thbase", "index": 4, "name": "CreateThread"},
                                                {"library": "libsd", "index": 7, "name": None}]))["00000000"]
        self.assertIn("CreateThread", entry["comment"])
        self.assertIn("libsd#7", entry["comment"])
        self.assertIn("candidate", entry["comment"])
        self.assertIn("unnamed", entry["comment"])

    def test_every_matching_tag_is_listed_without_forcing_one_role(self):
        comment = plan(func("00000000", imports=[{"library": "thbase", "index": 4, "name": "CreateThread"},
                                                  {"library": "thsemap", "index": 4, "name": "CreateSema"},
                                                  {"library": "libsd", "index": 26, "name": None}]))["00000000"]["comment"]
        for tag in ("thread_control", "semaphore", "sound_driver"):
            self.assertIn(tag, comment)

    def test_strings_exports_and_pointer_counts_are_shown(self):
        comment = plan(func("00000040", strings=["host0:"], exported=[{"library": "lgdev", "index": 3}], pointers=2))["00000040"]["comment"]
        self.assertIn("host0:", comment)
        self.assertIn("lgdev", comment)
        self.assertIn("2 data pointer", comment)

    def test_debug_procedure_facts_get_their_own_line_and_a_function_with_only_that_is_kept(self):
        comment = plan(func("00000040", procedure={"file": "stream.c", "frame_bytes": 32, "size": 64}))["00000040"]["comment"]
        self.assertIn("stream.c", comment)
        self.assertIn("frame 32 bytes", comment)

    def test_symbol_table_names_are_labelled_as_read_not_as_candidates(self):
        entry = plan(func("00000000", imports=[{"library": "libsd", "index": 4, "name": "sceSdInit", "name_source": "module symbol table"}]))["00000000"]
        self.assertIn("sceSdInit (read from the module symbol table)", entry["comment"])
        self.assertNotIn("candidate name", entry["comment"])

    def test_the_comment_says_no_identity_is_claimed(self):
        comment = plan(func("00000000", strings=["host0:"]))["00000000"]["comment"]
        self.assertIn("No identity claim", comment)


class RenameTest(unittest.TestCase):
    def test_a_single_self_naming_error_string_gives_a_rename(self):
        entry = plan(func("00006204", strings=["ERROR: SOUND_StopDTS\n", "DTS Not supported\n"]))["00006204"]
        self.assertEqual(entry["rename"], "SOUND_StopDTS")
        self.assertIn("self-naming", entry["comment"])

    def test_a_function_that_already_has_a_real_name_is_not_renamed(self):
        entry = plan(func("00006204", strings=["ERROR: SOUND_StopDTS\n"], name="SOUND_StopDTS"))["00006204"]
        self.assertNotIn("rename", entry)

    def test_two_different_self_naming_strings_give_no_rename(self):
        entry = plan(func("00006204", strings=["ERROR: Foo\n", "ERROR: Bar\n"]))["00006204"]
        self.assertNotIn("rename", entry)

    def test_a_name_claimed_by_two_functions_is_not_used(self):
        entries = plan(func("00000010", strings=["ERROR: Foo\n"]), func("00000020", strings=["ERROR: Foo\n"]))
        self.assertNotIn("rename", entries["00000010"])
        self.assertNotIn("rename", entries["00000020"])

    def test_text_after_error_that_is_not_one_identifier_is_not_a_name(self):
        entry = plan(func("00000010", strings=["ERROR: could not open file\n"]))["00000010"]
        self.assertNotIn("rename", entry)


class PinTest(unittest.TestCase):
    def test_the_plan_pins_the_module_hash(self):
        result = build_plan({"functions": [func("00000000", strings=["host0:"])], "module": {"name": "m", "sha256": SHA}}, SHA)
        self.assertEqual(result["executable_sha256"], SHA)
        self.assertEqual(result["schema_version"], 1)

    def test_a_different_pin_is_rejected(self):
        with self.assertRaises(ValueError):
            build_plan({"functions": [], "module": {"name": "m", "sha256": SHA}}, "cd" * 32)


if __name__ == "__main__":
    unittest.main()
