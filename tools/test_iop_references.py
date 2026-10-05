import struct
import unittest

from evidence_common import Invalid
from iop_references import reference_sites
from test_ps2_irx_relocations import build_irx


class ReferenceSiteTest(unittest.TestCase):
    def sites(self, **kwargs):
        return {s["site"]: s for s in reference_sites(build_irx(**kwargs))}

    def test_default_module_gives_a_word_a_jump_and_a_hi_lo_pair(self):
        sites = self.sites()
        self.assertEqual(sites[0]["kind"], "word")
        self.assertEqual(sites[0]["target"], 0x100)
        self.assertEqual(sites[4]["kind"], "jump")
        self.assertEqual(sites[4]["target"], 0x100)
        self.assertEqual(sites[8]["kind"], "hi_lo")
        self.assertEqual(sites[8]["lo_site"], 12)
        self.assertEqual(sites[8]["target"], 0x12347800)
        self.assertNotIn(12, sites)

    def test_a_negative_low_half_borrows_from_the_high_half(self):
        sites = self.sites(words=(0, 0, 0x3C080001, 0x2484FFF0))
        self.assertEqual(sites[8]["target"], 0x0000FFF0)

    def test_sites_are_sorted_and_stable(self):
        result = reference_sites(build_irx())
        self.assertEqual([s["site"] for s in result], sorted(s["site"] for s in result))

    def test_a_malformed_module_is_rejected(self):
        with self.assertRaises(Invalid):
            reference_sites(build_irx(elf_type=2))


if __name__ == "__main__":
    unittest.main()
