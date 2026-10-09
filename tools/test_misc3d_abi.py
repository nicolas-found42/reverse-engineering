"""Synthetic child-seam controls for the bounded misc3d raw ABI check."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid, sha256
import misc3d_abi as abi


def fixture(omit=(), changes=None):
    # Hand-authored synthetic instruction sites, not a corpus/export fixture.
    words = {}

    def immediate(site, op, base, target, value):
        words[site] = op << 26 | base << 21 | target << 16 | value & 0xffff

    def registers(site, left, right, target, operation, shift=0):
        words[site] = left << 21 | right << 16 | target << 11 | shift << 6 | operation

    for site, target in ((0x1d1448, 0x11ed90), (0x1d145c, 0x124f58), (0x125080, 0x21b6e0)):
        words[site] = 3 << 26 | target >> 2
    for site, op, base, target, value in (
        (0x1d1440, 15, 0, 4, 0x28), (0x1d144c, 9, 4, 4, 0x3208),
        (0x1d1460, 43, 28, 2, -0x52ac), (0x120588, 35, 28, 2, -0x6c4c),
        (0x12058c, 15, 0, 3, 0xfff0), (0x120590, 13, 3, 3, 0xffff),
        (0x120594, 15, 0, 5, 1), (0x12059c, 15, 0, 4, 0xffff),
        (0x1205d0, 43, 28, 2, -0x6c4c), (0x1205d8, 9, 29, 29, 0x290),
        (0x12506c, 9, 0, 2, -1), (0x125078, 4, 16, 2, 9),
        (0x12507c, 63, 29, 31, 8), (0x125088, 12, 16, 3, 0xffff),
        (0x12508c, 35, 2, 4, 236), (0x125098, 4, 0, 0, 2),
        (0x12509c, 35, 3, 2, 0), (0x1250a4, 55, 29, 16, 0),
        (0x1250a8, 55, 29, 31, 8), (0x1250b0, 9, 29, 29, 16)):
        immediate(site, op, base, target, value)
    for site, left, right, target, operation in (
        (0x11ed98, 4, 0, 16, 45), (0x1d1454, 2, 0, 4, 45),
        (0x120598, 2, 3, 2, 36), (0x1205a0, 2, 5, 2, 37),
        (0x1205ac, 2, 4, 2, 36), (0x1205d4, 31, 0, 0, 8),
        (0x125074, 4, 0, 16, 45), (0x125094, 3, 4, 3, 33),
        (0x1250a0, 0, 0, 2, 45), (0x1250ac, 31, 0, 0, 8)):
        registers(site, left, right, target, operation)
    registers(0x125090, 0, 3, 3, 0, shift=2)
    words[0x125084] = 0
    for index, register in enumerate((16, 17, 18, 19, 20, 21, 22, 23, 30, 31)):
        site = 0x1205a4 + index * 4 + (4 if index >= 2 else 0)
        immediate(site, 55, 29, register, 0x240 + index * 8)
    words.update(changes or {})
    return build_elf([Spec('.site'+str(site), struct.pack('<I', word), flags=6, address=site)
                      for site, word in sorted(words.items()) if site not in omit])


class AbiControls(unittest.TestCase):
    def check(self, data):
        with patch.object(abi, 'EE_CORPUS_SHA256', sha256(data)):
            return abi.check(data)

    def test_positive_retains_pointer_and_lifetime_limit(self):
        result = self.check(fixture())
        self.assertEqual(result['database_return_low_word'], '(old_id & 0xfff00000) | 0x00010000')
        self.assertEqual(result['resource_object']['pointer_stride'], 4)
        self.assertEqual(result['resource_object']['sentinel_result'], 'null')
        self.assertIn('pointer-lifetime', result['required_unknown'])
        self.assertEqual(result['new_attributed_match_bytes'], 0)

    def test_wrong_database_tag_fails(self):
        data = fixture(changes={0x120594: 15 << 26 | 5 << 16 | 2})
        with self.assertRaisesRegex(Invalid, 'database tag'):
            self.check(data)

    def test_changed_pointer_stride_fails(self):
        data = fixture(changes={0x125090: 3 << 16 | 3 << 11 | 3 << 6})
        with self.assertRaisesRegex(Invalid, 'scale resource index'):
            self.check(data)

    def test_return_register_clobber_in_frame_restore_fails(self):
        data = fixture(changes={0x1205cc: 55 << 26 | 29 << 21 | 2 << 16 | 0x288})
        with self.assertRaisesRegex(Invalid, 'frame restore'):
            self.check(data)

    def test_wrong_delay_slot_argument_fails(self):
        with self.assertRaisesRegex(Invalid, 'database name argument'):
            self.check(fixture(changes={0x1d144c: 0}))

    def test_missing_site_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'required ABI instruction absent'):
            self.check(fixture(omit=(0x1d1448,)))

    def test_contradiction_outranks_missing_site(self):
        with self.assertRaisesRegex(Invalid, 'database tag'):
            self.check(fixture(omit=(0x1d1448,), changes={0x120594: 0}))

    def test_unpinned_executable_fails(self):
        with self.assertRaisesRegex(Invalid, 'unchanged recorded executable'):
            abi.check(fixture())

    def test_public_child_cli_missing_corpus_writes_incomplete_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = subprocess.run([sys.executable, abi.__file__, str(root/'absent'),
                                     '--output', str(root/'result')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            receipt = json.loads(next((root/'result').glob('*/result.json')).read_text())
            self.assertEqual(receipt['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
