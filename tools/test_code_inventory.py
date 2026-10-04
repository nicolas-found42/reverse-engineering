import hashlib
import unittest

from evidence_common import Incomplete, Invalid
from verify_code_inventory import inspect
from test_ps2_executables import elf


def fixture():
    import struct
    data = bytearray(elf())
    # A loaded executable span containing three four-byte instructions.
    struct.pack_into('<I', data, 52 + 8, 0x1000)
    source = {'schema_version': 1, 'language': 'r5900:LE:32:default',
              'executable_sha256': hashlib.sha256(data).hexdigest(),
              'inventory_count': 1, 'functions': [{'entry': '00001000', 'instructions': [
                  {'address': f'{0x1000+i:08x}', 'bytes': bytes(data[84+i:88+i]).hex()}
                  for i in (0, 4, 8)]}]}
    return bytes(data), source


class CodeInventoryTest(unittest.TestCase):
    def test_bytes_match_and_exact_narrow_coverage(self):
        data, source = fixture()
        result = inspect(data, source)
        self.assertEqual(result['mapped_executable_bytes'], 12)
        self.assertEqual(result['listed_instruction_bytes'], 12)
        self.assertFalse(result['whole_game_decompiled'])

    def test_missing_instruction_coverage_is_incomplete(self):
        data, source = fixture(); source['functions'][0]['instructions'].pop()
        with self.assertRaises(Incomplete) as caught:
            inspect(data, source)
        self.assertEqual(caught.exception.details['unlisted_executable_bytes'], 4)

    def test_mismatch_instructions_are_invalid(self):
        data, source = fixture(); source['functions'][0]['instructions'][0]['bytes'] = '01000000'
        with self.assertRaises(Invalid):
            inspect(data, source)

    def test_wrong_identity_or_count_invalid(self):
        for field, value in (('executable_sha256', 'wrong'), ('inventory_count', 2)):
            data, source = fixture(); source[field] = value
            with self.assertRaises(Invalid):
                inspect(data, source)

    def test_outside_address_or_straddling_instruction_invalid(self):
        for address in ('00000ffc', '0000100a'):
            data, source = fixture(); source['functions'][0]['instructions'][0]['address'] = address
            with self.assertRaises(Invalid):
                inspect(data, source)

    def test_duplicate_owner_same_bytes_is_reported(self):
        data, source = fixture(); source['functions'].append({'entry': '00001004', 'instructions': [source['functions'][0]['instructions'][1]]}); source['inventory_count'] = 2
        result = inspect(data, source)
        self.assertEqual(result['shared_instruction_count'], 1)

    def test_vu_placeholder_is_excluded_but_actual_code_remains(self):
        from test_ps2_vu import fixture as vu_fixture
        data, offsets, _ = vu_fixture()
        source = {'schema_version': 1, 'language': 'r5900:LE:32:default',
                  'executable_sha256': hashlib.sha256(data).hexdigest(),
                  'inventory_count': 0, 'functions': []}
        with self.assertRaises(Incomplete) as caught:
            inspect(data, source)
        result = caught.exception.details
        self.assertEqual(result['mapped_executable_bytes'], 8)
        self.assertEqual(result['unlisted_executable_bytes'], 8)
        self.assertEqual(result['excluded_synthetic_bytes'], 8)
        self.assertEqual(result['regions'][0]['offset'], offsets[1])
        self.assertEqual(result['synthetic_regions'][0]['source_offset'], offsets[1])

    def test_nonzero_placeholder_is_not_silently_excluded(self):
        from test_ps2_vu import fixture as vu_fixture
        data, offsets, _ = vu_fixture()
        changed = bytearray(data); changed[offsets[4]] = 1
        source = {'schema_version': 1, 'language': 'r5900:LE:32:default',
                  'executable_sha256': hashlib.sha256(changed).hexdigest(),
                  'inventory_count': 0, 'functions': []}
        with self.assertRaisesRegex(Incomplete, 'nonzero placeholder'):
            inspect(bytes(changed), source)

    def test_empty_or_unlisted_entry_cannot_count_as_a_function(self):
        for entry, rows in (('00001000', []), ('00001004', [0])):
            data, source = fixture()
            source['functions'][0]['entry'] = entry
            source['functions'][0]['instructions'] = [source['functions'][0]['instructions'][i] for i in rows]
            with self.assertRaisesRegex(Invalid, 'entry is absent'):
                inspect(data, source)

    def test_section_mapping_must_match_load_mapping(self):
        from test_ps2_vu import fixture as vu_fixture
        import struct
        data, offsets, shoff = vu_fixture(); changed = bytearray(data)
        struct.pack_into('<I', changed, 52 + 8, 0x2000)
        struct.pack_into('<I', changed, shoff + 4*40 + 4, 1)
        struct.pack_into('<I', changed, shoff + 4*40 + 8, 0)
        source = {'schema_version': 1, 'language': 'r5900:LE:32:default',
                  'executable_sha256': hashlib.sha256(changed).hexdigest(),
                  'inventory_count': 1, 'functions': [{'entry': '00001000', 'instructions': [
                      {'address': '00001000', 'bytes': data[offsets[1]:offsets[1]+4].hex()}]}]}
        with self.assertRaisesRegex(Invalid, 'section mapping disagrees'):
            inspect(bytes(changed), source)


if __name__ == '__main__':
    unittest.main()
