import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from elf_fixture import Spec, build_elf

TOOLS = Path(__file__).resolve().parent


def image():
    data = bytearray(build_elf([
        Spec('.text', b'abcdefgh', flags=6, address=0x100000),
        Spec('.bss', kind=8, address=0x100010, size=16),
    ]))
    # Fixture: 8 initialized bytes, 8 unnamed zero-fill bytes, 16 BSS bytes.
    at = len(data)
    data.extend(struct.pack('<8I', 1, 64, 0x100000, 0x100000, 8, 32, 7, 16))
    struct.pack_into('<I', data, 28, at)
    struct.pack_into('<H', data, 44, 1)
    return bytes(data)


class BoundaryEvidenceTest(unittest.TestCase):
    def test_failed_source_map_with_a_matching_metadata_hash_cannot_earn_provenance(self):
        from unittest.mock import patch
        import matching_ranges
        from evidence_common import Invalid, identity
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            metadata = json.loads(matching_ranges.BOUNDARY_METADATA.read_text())
            source_map, boundary = root / 'source-map.json', root / 'boundary.json'
            for status in ('fail', 'incomplete', None):
                with self.subTest(status=status):
                    source_map.write_text(json.dumps({'status': status}))
                    metadata['evidence_inputs']['source_map']['sha256'] = identity(source_map)['sha256']
                    boundary.write_text(json.dumps(metadata))
                    with patch.object(matching_ranges, 'SOURCE_MAP', source_map), \
                         patch.object(matching_ranges, 'BOUNDARY_METADATA', boundary):
                        with self.assertRaisesRegex(Invalid, 'must report pass'):
                            matching_ranges.boundary_provenance()

    def test_boundary_evidence_is_reproducible_from_repository_files(self):
        from matching_ranges import boundary_provenance, ROOT, BOUNDARY_METADATA, SAVED_FUNCTION_INVENTORY
        self.assertTrue(BOUNDARY_METADATA.is_relative_to(ROOT / 'notes'))
        self.assertTrue(SAVED_FUNCTION_INVENTORY.is_relative_to(ROOT / 'notes'))
        self.assertEqual(set(boundary_provenance()), {'metadata', 'source_map', 'saved_function_inventory'})

    def test_missing_boundary_evidence_names_the_prerequisite(self):
        from unittest.mock import patch
        import matching_ranges
        from evidence_common import Incomplete
        with patch.object(matching_ranges, 'BOUNDARY_METADATA', Path('/missing/boundary.json')):
            with self.assertRaisesRegex(Incomplete, '/missing/boundary.json'):
                matching_ranges.boundary_provenance()


class RangeCli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def command(self, payload):
        source = self.root / 'fixture.bin'
        if payload is not None:
            source.write_bytes(payload)
        output = self.root / 'results'
        run = subprocess.run([sys.executable, str(TOOLS / 'matching_ranges.py'),
                              'file', str(source), '--output', str(output)],
                             capture_output=True, text=True)
        paths = list(output.glob('*/result.json'))
        self.assertEqual(len(paths), 1, run.stderr)
        result = json.loads(paths[0].read_text())
        self.assertTrue(paths[0].with_name('report.md').is_file())
        return run.returncode, result

    def test_partition_accounts_initialized_and_zero_fill_bytes_without_matching_credit(self):
        code, result = self.command(image())
        self.assertEqual((code, result['status']), (0, 'pass'), result['diagnostics'])
        d = result['details']
        self.assertEqual(d['file_backed_bytes'], 8)
        self.assertEqual(d['zero_fill_bytes'], 24)
        self.assertEqual(d['matched_bytes'], 0)
        self.assertEqual(d['substitute_bytes'], 0)
        self.assertEqual(d['substitute_disposition'], 'no ranges attributed as substitute')
        self.assertEqual(d['unresolved_bytes'], 32)
        self.assertEqual([(r['address'], r['length'], r['section']) for r in d['ranges']],
                         [(0x100000, 8, '.text'), (0x100008, 8, None),
                          (0x100010, 16, '.bss')])
        self.assertEqual(d['evidence_authority'], 'structural_file_inventory')

    def test_real_corpus_splits_only_the_identity_pinned_source_unit_and_keeps_match_zero(self):
        game = TOOLS.parent / 'games/ford-racing-2'
        if not (game / 'extracted/IRX/USBD.IRX').is_file():
            self.skipTest('real corpus range split requires the local pinned corpus')
        output = self.root / 'real-ranges'
        run = subprocess.run([sys.executable, str(TOOLS / 'matching_ranges.py'),
                              'corpus', str(game), '--output', str(output)],
                             capture_output=True, text=True)
        receipt = next(output.glob('*/result.json'))
        result = json.loads(receipt.read_text())
        self.assertEqual((run.returncode, result['status']), (0, 'pass'), result['diagnostics'])
        details = result['details']
        ee = next(item for item in details['artifacts'] if item['artifact'] == 'EE')
        owned = [row for row in ee['ranges'] if row['classification'] == 'game_owned']
        self.assertEqual([(row['address'], row['length'], row['section'], row['unit'])
                          for row in owned], [(0x1D1800, 60, '.text', 'misc3d_db_id')])
        self.assertEqual((ee['matched_bytes'], details['matched_bytes']), (0, 0))
        self.assertEqual((details['game_owned_bytes'], details['unresolved_bytes']),
                         (60, details['file_backed_bytes'] + details['zero_fill_bytes'] - 60))

    def test_real_corpus_ownership_is_stable_when_candidate_source_changes(self):
        game = TOOLS.parent / 'games/ford-racing-2'
        if not (game / 'extracted/IRX/USBD.IRX').is_file():
            self.skipTest('real corpus source mutation requires the local pinned corpus')
        from matching_ranges import UNIT_SOURCE
        original = UNIT_SOURCE.read_bytes()
        mutation = original.replace(b'value != -1', b'value == -1')
        self.assertNotEqual(original, mutation)
        output = self.root / 'mutated-source-ranges'
        UNIT_SOURCE.write_bytes(mutation)
        try:
            run = subprocess.run([sys.executable, str(TOOLS / 'matching_ranges.py'),
                                  'corpus', str(game), '--output', str(output)],
                                 capture_output=True, text=True)
        finally:
            UNIT_SOURCE.write_bytes(original)
        result = json.loads(next(output.glob('*/result.json')).read_text())
        self.assertEqual((run.returncode, result['status']), (0, 'pass'), result['diagnostics'])
        details = result['details']
        self.assertEqual((details['game_owned_bytes'], details['matched_bytes'],
                          details['unresolved_bytes']), (60, 0, 3506988))
        self.assertEqual(details['file_backed_bytes'] + details['zero_fill_bytes'],
                         details['unresolved_bytes'] + details['game_owned_bytes']
                         + details['substitute_bytes'])
        ee = next(item for item in details['artifacts'] if item['artifact'] == 'EE')
        row = next(row for row in ee['ranges'] if row.get('unit') == 'misc3d_db_id')
        self.assertNotEqual(row['candidate_source_sha256'], row['reconstruction_source_sha256'])

    def test_overlapping_load_images_fail_instead_of_double_counting(self):
        data = bytearray(image())
        data.extend(data[-32:])
        struct.pack_into('<H', data, 44, 2)
        code, result = self.command(bytes(data))
        self.assertEqual((code, result['status']), (1, 'fail'))
        self.assertIn('overlap', ' '.join(result['diagnostics']))

    def test_absent_image_is_incomplete_and_section_only_file_cannot_prove_load_layout(self):
        code, result = self.command(None)
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        # Separate output so both immutable attempts remain inspectable.
        self.root = self.root / 'second'
        self.root.mkdir()
        code, result = self.command(build_elf([Spec('.text', b'abcdefgh')]))
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        self.assertIn('PT_LOAD', ' '.join(result['diagnostics']))

    def test_section_payload_mapping_drift_fails_with_section_named(self):
        data = bytearray(image())
        table, = struct.unpack_from('<I', data, 32)
        struct.pack_into('<I', data, table + 40 + 16, 80)
        code, result = self.command(bytes(data))
        self.assertEqual((code, result['status']), (1, 'fail'))
        self.assertIn('.text', ' '.join(result['diagnostics']))

    def test_overlapping_allocated_sections_fail_with_located_diagnostic(self):
        data = bytearray(image())
        table, = struct.unpack_from('<I', data, 32)
        struct.pack_into('<I', data, table + 80 + 12, 0x100004)
        code, result = self.command(bytes(data))
        self.assertEqual((code, result['status']), (1, 'fail'))
        self.assertIn('sections overlap', ' '.join(result['diagnostics']))

    def test_allocated_sections_outside_load_images_remain_visible(self):
        data = bytearray(image())
        table, = struct.unpack_from('<I', data, 32)
        struct.pack_into('<I', data, table + 80 + 12, 0x200000)
        code, result = self.command(bytes(data))
        self.assertEqual((code, result['status']), (0, 'pass'))
        outside = result['details']['allocated_sections_outside_load_images']
        self.assertEqual([(s['section'], s['address'], s['length']) for s in outside],
                         [('.bss', 0x200000, 16)])

    def test_changed_module_fails_even_with_a_different_module_missing(self):
        game = TOOLS.parent / 'games/ford-racing-2'
        if not (game / 'extracted/IRX/USBD.IRX').is_file():
            self.skipTest('real pinned module mutation requires local corpus')
        mirror = self.root / 'game'
        mirror.mkdir()
        for name in ('ford-racing-2.bin', 'ford-racing-2.cue'):
            (mirror / name).symlink_to(game / name)
        ex = mirror / 'extracted'
        ex.mkdir()
        for name in ('SLES_517.05', 'FILES.HDR', 'FILES.DAT'):
            (ex / name).symlink_to(game / 'extracted' / name)
        modules = ex / 'IRX'
        modules.mkdir()
        for source in (game / 'extracted/IRX').iterdir():
            if source.name in ('PADMAN.IRX', '.DS_Store'):
                continue
            if source.name == 'USBD.IRX':
                (modules / source.name).write_bytes(source.read_bytes() + b'changed')
            else:
                (modules / source.name).symlink_to(source)
        output = self.root / 'results'
        run = subprocess.run([sys.executable, str(TOOLS / 'matching_ranges.py'),
                              'corpus', str(mirror), '--output', str(output)],
                             capture_output=True, text=True)
        result = json.loads(next(output.glob('*/result.json')).read_text())
        self.assertEqual((run.returncode, result['status']), (1, 'fail'))
        self.assertIn('USBD.IRX', ' '.join(result['diagnostics']))


if __name__ == '__main__':
    unittest.main()
