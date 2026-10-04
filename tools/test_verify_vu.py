"""Negative oracle checks for native-output validation, independent of GAS internals."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from evidence_common import Incomplete, Invalid
from test_ps2_vu import fixture
import verify_vu as subject


class NativeVuValidationTest(unittest.TestCase):
    def _run_fixture(self, mode):
        data, offsets, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable, tool = root / 'game.elf', root / 'native-tool'
            executable.write_bytes(data); tool.write_bytes(b'fixture tool identity')

            def native(command, stem):
                stdout = stem.with_suffix('.stdout')
                if '-D' in command:
                    stdout.write_text('0:\t14 00 01 10 \tnop\tnop\n')
                elif mode != 'missing':
                    output = bytearray(data)
                    if mode == 'mismatch': output[offsets[1]] ^= 1
                    if mode == 'relocation':
                        # Use the existing nonempty overlay-table payload as a relocation section.
                        shoff = struct.unpack_from('<I', output, 32)[0]
                        struct.pack_into('<I', output, shoff + 2*40 + 4, 9)
                    Path(command[2]).write_bytes(output)
                return {'command': command, 'exit_code': 0,
                        'stdout': {'path': str(stdout)}}

            with patch.object(subject, '_run', side_effect=native):
                return subject.verify(executable, tool, tool, root / 'work')

    def test_corrupted_native_object_cannot_pass(self):
        with self.assertRaisesRegex(Invalid, 'round trip differs') as caught:
            self._run_fixture('mismatch')
        self.assertFalse(caught.exception.details['overlays'][0]['exact_match'])

    def test_success_without_native_output_is_invalid(self):
        with self.assertRaisesRegex(Invalid, 'without writing'):
            self._run_fixture('missing')

    def test_unresolved_native_relocation_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'unresolved relocations'):
            self._run_fixture('relocation')

    def test_missing_native_tool_is_incomplete(self):
        with self.assertRaisesRegex(Incomplete, 'native tool is missing'):
            subject._tool(Path('/nonexistent/fr2-verifier-native-tool'), 'dvp-as')


if __name__ == '__main__': unittest.main()
