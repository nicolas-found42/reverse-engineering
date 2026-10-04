"""Candidate API names require exact table versions and unambiguous ordinals."""
import unittest

from evidence_common import Incomplete, Invalid
import ps2_irx_catalog as catalog


class ExportCatalogTest(unittest.TestCase):
    def test_comments_cannot_insert_or_shift_ordinals(self):
        tables = catalog.parse_tables('''
/* DECLARE_EXPORT_TABLE(fake, 1, 1)
DECLARE_EXPORT(wrong)
END_EXPORT_TABLE */
DECLARE_EXPORT_TABLE(thbase, 1, 2)
DECLARE_EXPORT(_start)
// DECLARE_EXPORT(wrong)
DECLARE_EXPORT(CreateThread) /* ignored */
END_EXPORT_TABLE
''', source="fixture.tab")
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["functions"], ["_start", "CreateThread"])
        self.assertEqual(tables[0]["version"], 0x0102)

    def test_conditional_table_is_incomplete_instead_of_guessing_build(self):
        with self.assertRaises(Incomplete):
            catalog.parse_tables('''#ifdef VARIANT
DECLARE_EXPORT_TABLE(demo, 1, 1)
DECLARE_EXPORT(one)
#else
DECLARE_EXPORT(two)
#endif
END_EXPORT_TABLE''', source="conditional.tab")

    def test_nested_unterminated_and_non_declaration_rows_are_rejected(self):
        start = "DECLARE_EXPORT_TABLE(demo, 1, 1)\n"
        for text in (start + start, start + "DECLARE_EXPORT(a)",
                     start + "DECLARE_EXPORT(f())\nEND_EXPORT_TABLE",
                     start + "UNKNOWN_EXPORT(a)\nEND_EXPORT_TABLE",
                     "END_EXPORT_TABLE", start + "END_EXPORT_TABLE"):
            with self.subTest(text=text), self.assertRaises(Invalid):
                catalog.parse_tables(text, source="bad.tab")

    def test_minor_mismatch_and_missing_index_stay_unresolved(self):
        table = {"library": "demo", "version": 0x0101,
                 "functions": ["entry", "service"], "source": "one.tab"}
        for version, index in ((0x0102, 1), (0x0101, 2)):
            result = catalog.candidate_name("demo", version, index, [table])
            self.assertIsNone(result["candidate_name"])
            self.assertEqual(result["status"], "unresolved")

    def test_disagreeing_exact_catalogs_do_not_choose_a_name(self):
        rows = [{"library": "demo", "version": 0x0101, "functions": [name],
                 "source": name + ".tab"} for name in ("alpha", "beta")]
        result = catalog.candidate_name("demo", 0x0101, 0, rows)
        self.assertIsNone(result["candidate_name"])
        self.assertEqual(result["status"], "ambiguous")

    def test_agreeing_catalogs_preserve_all_provenance_and_input(self):
        rows = [{"library": "demo", "version": 0x0101, "functions": ["service"],
                 "source": name} for name in ("first.tab", "second.tab")]
        result = catalog.candidate_name("demo", 0x0101, 0, rows)
        self.assertEqual(result["candidate_name"], "service")
        self.assertEqual(result["status"], "candidate-api-name")
        self.assertEqual(result["catalog_sources"], ["first.tab", "second.tab"])
        self.assertEqual(rows[0]["functions"], ["service"])
        self.assertFalse(result["original_identity_verified"])

    def test_versions_and_indices_have_bounded_integer_domains(self):
        for version, index in ((True, 0), (-1, 0), (0x10000, 0),
                               (0x0101, True), (0x0101, -1)):
            with self.subTest(version=version, index=index), self.assertRaises(Invalid):
                catalog.candidate_name("demo", version, index, [])

    def test_hex_octal_and_oversized_c_literals_are_not_guessed(self):
        for literal in ("0x01", "010", "00", "256"):
            text = (f"DECLARE_EXPORT_TABLE(demo, 1, {literal})\n"
                    "DECLARE_EXPORT(service)\nEND_EXPORT_TABLE")
            with self.subTest(literal=literal), self.assertRaises(Invalid):
                catalog.parse_tables(text, source="unsupported-literal.tab")


if __name__ == "__main__":
    unittest.main()
