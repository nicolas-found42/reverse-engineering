"""Guard and nibble-order tests for the static model upload interpretation."""
import copy
import struct
import unittest

import ps2_container
from evidence_common import Invalid
from test_ps2_textures import container, item
from ps2_texture_indices import decode_indices


def fixture(fmt=4, width=32, height=16, packed=True):
    data = bytearray(container([item('INDEXED', fmt, width, height, palette=2)]))
    texture = ps2_container.parse(bytes(data))['textures']['items'][0]
    at = texture['descriptor_offset']
    field = int(texture['descriptor_field'], 16)
    uw, uh = (width // 2, height // 2) if packed else (width, height)
    field |= (int(packed) << 8) | ((uw.bit_length() - 1) << 23) | ((uh.bit_length() - 1) << 27)
    struct.pack_into('<Q', data, at + 0x38, field)
    tbw, dbw = max(2, width // 64), max(1, uw // 64) if packed else max(2, width // 64)
    struct.pack_into('<I', data, at + 0x30, (tbw << 16) | (dbw << 22))
    texture = ps2_container.parse(bytes(data))['textures']['items'][0]
    return bytes(data), texture


class IndexDecoding(unittest.TestCase):
    def test_linear_four_bit_uses_low_then_high_nibbles(self):
        data, texture = fixture(width=8, height=8, packed=False)
        plane = texture['levels'][0]
        values = data[plane['offset']:plane['offset'] + plane['size']]
        expected = bytes(n for b in values for n in (b & 15, b >> 4))
        self.assertEqual(decode_indices(data, texture), expected)

    def test_packed_four_bit_known_first_row_cells(self):
        data, texture = fixture()
        at = texture['levels'][0]['offset']
        pixels = decode_indices(data, texture)
        # GS table coordinates: x=0,1,2,3 select input nibble 0,4,8,12.
        self.assertEqual(pixels[:4], bytes(data[at + n] & 15 for n in (0, 2, 4, 6)))
        self.assertEqual(len(pixels), 512)

    def test_linear_eight_bit_includes_small_images(self):
        data, texture = fixture(fmt=3, width=8, height=8, packed=False)
        plane = texture['levels'][0]
        self.assertEqual(decode_indices(data, texture), data[plane['offset']:plane['offset'] + plane['size']])

    def test_packed_eight_bit_matches_measured_existing_formula(self):
        data, texture = fixture(fmt=3)
        plane = texture['levels'][0]
        self.assertEqual(decode_indices(data, texture), ps2_container.unswizzle8(data[plane['offset']:plane['offset'] + plane['size']], 32, 16))

    def test_inconsistent_transfer_dimensions_are_rejected(self):
        data, texture = fixture()
        changed = bytearray(data)
        field = int(texture['descriptor_field'], 16) & ~(15 << 23)
        struct.pack_into('<Q', changed, texture['descriptor_offset'] + 0x38, field)
        parsed = ps2_container.parse(bytes(changed))['textures']['items'][0]
        with self.assertRaisesRegex(Invalid, 'transfer dimensions'):
            decode_indices(bytes(changed), parsed)

    def test_invalid_buffer_width_cannot_read_unwritten_memory(self):
        data, texture = fixture(width=256, height=256)
        changed = bytearray(data)
        struct.pack_into('<I', changed, texture['descriptor_offset'] + 0x30, 4 << 16)
        with self.assertRaisesRegex(Invalid, 'buffer width'):
            decode_indices(bytes(changed), texture)

    def test_truncated_plane_and_descriptor_are_rejected(self):
        data, texture = fixture()
        for end in (texture['descriptor_offset'] + 63, texture['levels'][0]['offset'] + 255):
            with self.assertRaises(Invalid):
                decode_indices(data[:end], texture)

    def test_item_dimensions_must_match_the_descriptor(self):
        data, texture = fixture()
        bad = copy.deepcopy(texture)
        bad['width'] = 16
        with self.assertRaisesRegex(Invalid, 'descriptor'):
            decode_indices(data, bad)


if __name__ == '__main__':
    unittest.main()
