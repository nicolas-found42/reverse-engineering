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
        self.assertEqual(d['unresolved_bytes'], 32)
        self.assertEqual([(r['address'], r['length'], r['section']) for r in d['ranges']],
                         [(0x100000, 8, '.text'), (0x100008, 8, None),
                          (0x100010, 16, '.bss')])
        self.assertEqual(d['evidence_authority'], 'structural_file_inventory')

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


if __name__ == '__main__':
    unittest.main()
