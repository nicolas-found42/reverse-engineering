import struct
import unittest

from evidence_common import Incomplete, Invalid
from ps2_vu import parse_overlays, canonical_source


def fixture():
    names = ['', '.vutext', '.DVP.ovlytab', '.DVP.ovlystrtab', '.DVP.overlay.test', '.shstrtab']
    pool = b'\0'; name_offsets = [0]
    for name in names[1:]:
        name_offsets.append(len(pool)); pool += name.encode() + b'\0'
    code = struct.pack('<2I', 0x10010014, 0x2FF)
    values = [(0, 0, b''), (1, 6, code),
              (0x7FFFF420, 0, struct.pack('<3I', 1, 0x1000, 0)),
              (3, 0, b'\0.DVP.overlay.test\0'), (0x7FFFF421, 5, bytes(8)), (3, 0, pool)]
    data = bytearray(84); offsets = []
    for _, _, payload in values:
        offsets.append(len(data)); data += payload
    while len(data) % 4: data.append(0)
    shoff = len(data)
    for i, (kind, flags, payload) in enumerate(values):
        data += struct.pack('<10I', name_offsets[i], kind, flags, 0x1000 if i == 1 else 0,
                            offsets[i], len(payload), 0, 0, 1, 0)
    data[:16] = b'\x7fELF\x01\x01\x01' + bytes(9)
    struct.pack_into('<HHIIIIIHHHHHH', data, 16, 2, 8, 1, 0x1000, 52, shoff, 1, 52, 32, 1, 40, len(values), 5)
    struct.pack_into('<8I', data, 52, 1, offsets[1], 0x1000, 0x1000, 8, 8, 5, 4)
    return bytes(data), offsets, shoff


class VuTest(unittest.TestCase):
    def test_load_address_recovers_code_not_placeholder(self):
        data, offsets, _ = fixture(); result = parse_overlays(data)
        row = result['overlays'][0]
        self.assertEqual(row['source_offset'], offsets[1])
        self.assertEqual(row['placeholder_offset'], offsets[4])
        self.assertNotEqual(row['sha256'], row['placeholder_sha256'])
        self.assertEqual(row['instruction_pairs'], 1)

    def test_invalid_table_extent_name_and_lma(self):
        data, offsets, shoff = fixture()
        for location, value in ((shoff + 2*40 + 20, 11), (offsets[2], 9999), (offsets[2]+4, 0x2000)):
            changed = bytearray(data); struct.pack_into('<I', changed, location, value)
            with self.assertRaises(Invalid): parse_overlays(bytes(changed))

    def test_missing_required_table_is_incomplete(self):
        data, _, shoff = fixture(); changed = bytearray(data)
        struct.pack_into('<I', changed, shoff + 2*40, 0)
        with self.assertRaises(Incomplete): parse_overlays(bytes(changed))

    def test_canonical_branch_and_full_float_precision(self):
        data = struct.pack('<2I', 0x40000003, 0x2FF)
        text = ' 0:\t03 00 00 40 \tnop \tb 0x20\n 4:\tff 02 00 00\n'
        source, detail = canonical_source(text, data, 0)
        self.assertRegex(source, r'nop\s+b 3')
        self.assertEqual(detail['branches'][0]['target'], 32)
        data = struct.pack('<2I', 0x3FC90FDB, 0x800002FF)
        source, _ = canonical_source('0:\tdb 0f c9 3f \tnop[i]\tloi 1.5708\n', data, 0)
        self.assertIn('1.57079637', source)

    def test_missing_pairs_and_nonfinite_literal_are_incomplete(self):
        with self.assertRaises(Invalid): canonical_source('', bytes(8), 0)
        data = struct.pack('<2I', 0x7FC00001, 0x800002FF)
        with self.assertRaises(Incomplete):
            canonical_source('0:\t01 00 c0 7f \tnop[i]\tloi nan\n', data, 0)


if __name__ == '__main__': unittest.main()
