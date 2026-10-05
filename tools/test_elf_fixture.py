import struct
import unittest

from elf_fixture import Spec, build_elf
from ps2_executables import parse_elf

EE_FLAGS = 0x20924001


class BuildElfTest(unittest.TestCase):
    def test_the_repo_parser_reads_back_every_section_name_type_address_and_bytes(self):
        data = build_elf([Spec(".text", b"\x01\x02\x03\x04", flags=6, address=0x100100),
                          Spec(".sbss", b"", kind=8, flags=3, address=0x290000, size=0x20),
                          Spec(".reginfo", b"\0" * 24, kind=0x70000006)])
        elf = parse_elf(data)
        self.assertEqual((elf["machine"], elf["flags"], elf["type"]), (8, EE_FLAGS, 2))
        rows = {row["name"]: row for row in elf["sections"] if row.get("name")}
        self.assertEqual(sorted(rows), [".reginfo", ".sbss", ".shstrtab", ".text"])
        text = rows[".text"]
        self.assertEqual((text["address"], text["size"], text["flags"]), (0x100100, 4, 6))
        self.assertEqual(data[text["offset"]:text["offset"] + 4], b"\x01\x02\x03\x04")
        self.assertEqual((rows[".sbss"]["type"], rows[".sbss"]["size"]), (8, 0x20))
        self.assertEqual(rows[".reginfo"]["type"], 0x70000006)

    def test_payloads_are_sixteen_byte_aligned_and_do_not_overlap(self):
        data = build_elf([Spec(".a", b"x" * 5), Spec(".b", b"y" * 7)])
        rows = {row["name"]: row for row in parse_elf(data)["sections"] if row.get("name")}
        self.assertEqual(rows[".a"]["offset"] % 16, 0)
        self.assertEqual(rows[".b"]["offset"] % 16, 0)
        self.assertGreaterEqual(rows[".b"]["offset"], rows[".a"]["offset"] + 5)

    def test_machine_and_flags_can_describe_a_non_ee_elf(self):
        data = build_elf([Spec(".t", b"\0\0\0\0")], machine=62, flags=0)
        self.assertEqual(struct.unpack_from("<H", data, 18)[0], 62)
        self.assertEqual(parse_elf(build_elf([Spec(".t", b"\0" * 4)], flags=0))["flags"], 0)


if __name__ == "__main__":
    unittest.main()
