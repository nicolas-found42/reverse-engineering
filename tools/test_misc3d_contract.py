"""Public output-check seam: layout and byte comparison, with synthetic ELF controls."""
import unittest

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid
from misc3d_contract import verify_outputs


class Misc3dContractTests(unittest.TestCase):
    def retail(self):
        return build_elf([
            Spec('.text', b'r' * 60, flags=6, address=0x1d1800),
            Spec('.sbss', kind=8, flags=3, address=0x290600, size=1316),
        ])

    def linked(self, *, address=0x290ac4, size=4, kind=8, text=b'r' * 60):
        return build_elf([
            Spec('.text.fr2_misc3d_get_database_id', text, flags=6, address=0x1d1800),
            Spec('.sbss.fr2_misc3d_db_id', b'\0' * size if kind != 8 else b'',
                 kind=kind, flags=3, address=address, size=size, alignment=4),
        ])

    def test_preserves_accessor_and_checks_nobits_without_counting_file_bytes(self):
        result = verify_outputs(self.retail(), self.linked())
        self.assertEqual(result['accessor']['status'], 'pass')
        self.assertEqual(result['cell'], {
            'section': '.sbss.fr2_misc3d_db_id', 'address': '00290ac4',
            'bytes': 4, 'alignment': 4, 'type': 'NOBITS',
            'has_file_bytes': False, 'matched_file_bytes': 0,
        })

    def test_changed_accessor_fails(self):
        with self.assertRaisesRegex(Invalid, 'accessor bytes differ'):
            verify_outputs(self.retail(), self.linked(text=b'x' + b'r' * 59))

    def test_changed_cell_layout_fails(self):
        for address, size, kind in ((0x290ac8, 4, 8), (0x290ac4, 8, 8), (0x290ac4, 4, 1)):
            with self.subTest(address=address, size=size, kind=kind), self.assertRaisesRegex(Invalid, 'cell layout'):
                verify_outputs(self.retail(), self.linked(address=address, size=size, kind=kind))

    def test_missing_cell_is_incomplete(self):
        linked = build_elf([Spec('.text.fr2_misc3d_get_database_id', b'r' * 60,
                                 flags=6, address=0x1d1800)])
        with self.assertRaisesRegex(Incomplete, 'cell section'):
            verify_outputs(self.retail(), linked)

    def test_duplicate_cell_sections_fail_as_ambiguous_layout(self):
        linked = build_elf([
            Spec('.text.fr2_misc3d_get_database_id', b'r' * 60, flags=6, address=0x1d1800),
            Spec('.sbss.fr2_misc3d_db_id', kind=8, flags=3, address=0x290ac4, size=4, alignment=4),
            Spec('.sbss.fr2_misc3d_db_id', kind=8, flags=3, address=0x290ac8, size=4, alignment=4),
        ])
        with self.assertRaisesRegex(Invalid, 'duplicate section name'):
            verify_outputs(self.retail(), linked)


class Misc3dProvenanceTests(unittest.TestCase):
    def test_recorded_provenance_is_bound_and_missing_observation_is_incomplete(self):
        from pathlib import Path
        from unittest.mock import patch
        import misc3d_contract as contract
        self.assertIn('observation', contract.provenance())
        with patch.object(contract, 'OBSERVATION', Path('/missing/misc3d-observation.json')):
            with self.assertRaisesRegex(Incomplete, 'provenance missing'):
                contract.provenance()

    def test_changed_cell_source_fails_before_build(self):
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        import misc3d_contract as contract
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'cell.c'
            changed.write_text('int misc3d_db_id = -1;\n')
            with patch.object(contract, 'CELL_SOURCE', changed):
                with self.assertRaisesRegex(Invalid, 'cell_source identity differs'):
                    contract.provenance()


class Misc3dObservationTests(unittest.TestCase):
    def fixture(self):
        from evidence_common import sha256
        # Synthetic encoding of LW V1,-0x52ac(GP), not copied retail payload.
        text = bytearray(0xd1900)
        text[0xd1800:0xd1804] = bytes.fromhex('54ad838f')
        data = build_elf([Spec('.text', bytes(text), flags=6, address=0x100000)])
        inventory = {'executable_sha256': sha256(data), 'functions': [{
            'entry': '001d1800', 'instructions': [{
                'address': '001d1800', 'bytes': '54ad838f', 'references': []}]}]}
        return data, inventory

    def test_observation_retains_direct_access_metadata_without_instruction_dump(self):
        from misc3d_observation import observe
        data, inventory = self.fixture()
        result = observe(data, inventory)
        self.assertEqual(len(result['cell_accesses']), 1)
        row = result['cell_accesses'][0]
        self.assertEqual((row['site'], row['kind'], row['width'], row['saved_owners']),
                         ('001d1800', 'load', 4, ['001d1800']))
        self.assertNotIn('bytes', row)
        self.assertNotIn('text', row)

    def test_changed_saved_instruction_fails_observation(self):
        from misc3d_observation import observe
        data, inventory = self.fixture()
        inventory['functions'][0]['instructions'][0]['bytes'] = '00000000'
        with self.assertRaisesRegex(Invalid, 'saved instruction differs'):
            observe(data, inventory)

    def test_missing_saved_functions_is_incomplete(self):
        from misc3d_observation import observe
        data, inventory = self.fixture()
        inventory['functions'] = []
        with self.assertRaisesRegex(Incomplete, 'function inventory is missing'):
            observe(data, inventory)


class Misc3dCellObjectTests(unittest.TestCase):
    def fixture(self, *, size=4, storage=0xff03):
        import struct
        from ps2_executables import parse_elf
        symbols = bytes(16) + struct.pack('<IIIBBH', 1, 4, size, 17, 0, storage)
        data = bytearray(build_elf([
            Spec('.strtab', b'\0misc3d_db_id\0', kind=3, flags=0),
            Spec('.symtab', symbols, kind=2, flags=0),
        ]))
        elf = parse_elf(bytes(data))
        struct.pack_into('<I', data, elf['section_offset'] + 2 * 40 + 24, 1)
        struct.pack_into('<I', data, elf['section_offset'] + 2 * 40 + 36, 16)
        return bytes(data)

    def test_uninitialized_common_definition_has_no_file_bytes(self):
        from misc3d_contract import verify_cell_object
        result = verify_cell_object(self.fixture())
        self.assertEqual((result['bytes'], result['alignment'], result['has_file_bytes']), (4, 4, False))

    def test_wrong_sized_or_initialized_definition_fails(self):
        from misc3d_contract import verify_cell_object
        for size, storage in ((8, 0xff03), (4, 3)):
            with self.subTest(size=size, storage=storage), self.assertRaisesRegex(Invalid, 'common object'):
                verify_cell_object(self.fixture(size=size, storage=storage))

    def test_missing_definition_cannot_pass(self):
        from misc3d_contract import verify_cell_object
        with self.assertRaisesRegex(Invalid, 'common object'):
            verify_cell_object(build_elf([Spec('.text', b'', flags=6)]))


if __name__ == '__main__':
    unittest.main()
