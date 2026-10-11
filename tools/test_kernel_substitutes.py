"""Exercise the public substitute command and its output-verification seam."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import struct

from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, Invalid

TOOLS = Path(__file__).resolve().parent


class SubstituteOutputTests(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        from evidence_common import sha256
        from ps2_executables import parse_elf
        _, linked = self.fixture()
        hashes = {s['name'][6:]: sha256(linked[s['offset']:s['offset'] + s['size']])
                  for s in parse_elf(linked)['sections'] if s['name'].startswith('.text.fr2_')}
        patcher = patch('kernel_substitutes.BUILT_CONSUMERS', hashes)
        patcher.start()
        self.addCleanup(patcher.stop)

    def fixture(self, *, changed=False, missing=False):
        names = [('SignalSema', 0x1eab80, 66), ('FlushCache', 0x1eade0, 100),
                 ('sceSifDmaStat', 0x1eaf00, 118), ('sceSifSetDma', 0x1eaf20, 119)]
        specs = [Spec('.text.' + name, struct.pack('<4I', 0x24030000 | number,
                      12, 0x03e00008, 0), flags=6, address=address)
                 for name, address, number in names]
        specs += [Spec('.text.fr2_dma_copy', bytes.fromhex('78ab070c00000000c8ab070c00000000c0ab070c00000000'),
                       flags=6, address=0x11b780),
                  Spec('.text.fr2_mfile_release', bytes.fromhex('e0aa070800000000'),
                       flags=6, address=0x20c940),
                  Spec('.data.fr2_mfile_sema', bytes(4), flags=3, address=0x24bad8),
                  Spec('.data.fr2_mfile_marker', b'\xff' * 4, flags=3, address=0x24f8e0),
                  Spec('.data.fr2_mfile_count', bytes(4), flags=3, address=0x24f8e4)]
        reference = build_elf(specs)
        if missing:
            specs = specs[1:]
        if changed:
            index = next(i for i, spec in enumerate(specs) if spec.name == '.text.FlushCache')
            specs[index] = Spec('.text.FlushCache', b'x' * 16, flags=6, address=0x1eade0)
        return reference, build_elf(specs)

    def test_identical_substitute_outputs_never_earn_matched_credit(self):
        from kernel_substitutes import verify_outputs
        result = verify_outputs(*self.fixture())
        self.assertEqual(result['matched_bytes'], 0)
        self.assertEqual(result['substitute_bytes'], 64)
        self.assertEqual(result['ac11_status'], 'incomplete')

    def test_changed_output_fails_even_when_another_output_is_missing(self):
        from kernel_substitutes import verify_outputs
        with self.assertRaises(Invalid):
            verify_outputs(*self.fixture(changed=True, missing=True))

    def test_missing_substitute_is_incomplete(self):
        from kernel_substitutes import verify_outputs
        with self.assertRaises(Incomplete):
            verify_outputs(*self.fixture(missing=True))

    def test_uncalled_sdk_objects_cannot_satisfy_a_consumer_interface(self):
        from kernel_substitutes import verify_outputs
        from ps2_executables import parse_elf
        retail, linked = self.fixture()
        section = next(s for s in parse_elf(linked)['sections']
                       if s['name'] == '.text.fr2_dma_copy')
        changed = bytearray(linked)
        changed[section['offset']:section['offset'] + section['size']] = bytes(section['size'])
        with self.assertRaisesRegex(Invalid, 'consumer transfer'):
            verify_outputs(retail, bytes(changed))

    def test_changed_consumer_preserving_all_call_targets_is_rejected(self):
        from kernel_substitutes import verify_outputs
        from ps2_executables import parse_elf
        retail, linked = self.fixture()
        section = next(s for s in parse_elf(linked)['sections']
                       if s['name'] == '.text.fr2_dma_copy')
        changed = bytearray(linked)
        # Change a delay instruction without changing any encoded call target.
        struct.pack_into('<I', changed, section['offset'] + 4, 0x24020001)
        with self.assertRaisesRegex(Invalid, 'consumer bytes'):
            verify_outputs(retail, bytes(changed))

    def test_unexpected_loadable_payload_is_rejected(self):
        from kernel_substitutes import verify_outputs
        from ps2_executables import parse_elf
        retail, linked = self.fixture()
        specs = [Spec(s['name'], linked[s['offset']:s['offset'] + s['size']],
                      flags=s['flags'], address=s['address'])
                 for s in parse_elf(linked)['sections'] if s['flags'] & 2]
        specs.append(Spec('.text.retail_injection', b'copied', flags=6, address=0x300000))
        with self.assertRaisesRegex(Invalid, 'unexpected allocated'):
            verify_outputs(retail, build_elf(specs))

    def test_consumers_preserve_boundary_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'controls'
            run = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                  '-fsanitize=undefined',
                                  str(TOOLS / 'kernel_substitute_recipe/host_controls.c'),
                                  str(TOOLS.parent / 'reconstruction/ee/system/sdk_consumers.c'),
                                  '-o', str(executable)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            run = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)


class SubstituteCommandTests(unittest.TestCase):
    def test_missing_inputs_are_incomplete_with_no_matched_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = subprocess.run([sys.executable, str(TOOLS / 'kernel_substitutes.py'),
                                  str(root / 'game'), str(root / 'sdk'),
                                  '--output', str(root / 'receipts')],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stderr)
            receipts = list((root / 'receipts').glob('*/result.json'))
            self.assertEqual(len(receipts), 1)
            result = json.loads(receipts[0].read_text())
            self.assertEqual(result['status'], 'incomplete')
            self.assertEqual(result['details']['matched_bytes'], 0)


if __name__ == '__main__':
    unittest.main()
