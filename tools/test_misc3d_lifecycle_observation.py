"""Public observation CLI priority controls; no retail payload is needed."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from elf_fixture import Spec, build_elf
from evidence_common import Incomplete, sha256
import misc3d_lifecycle_observation as observation


class LifecycleObservationPriority(unittest.TestCase):
    def test_wrong_boundary_wins_over_absent_ee_and_counterpart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            boundary = root / 'boundary.json'
            boundary.write_text('{"reconciled_bytes": 60}')
            result = subprocess.run([sys.executable,
                                     str(Path(__file__).with_name('misc3d_lifecycle_observation.py')),
                                     str(root), str(root / 'missing-before'), str(root / 'missing-after'),
                                     str(boundary), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('boundary receipt contradicts', result.stdout)

    def test_available_instruction_contradiction_wins_over_missing_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'extracted').mkdir()
            data = build_elf([Spec('.text', b'\0' * 4, flags=6, address=0x1000)])
            (root / 'extracted/SLES_517.05').write_bytes(data)
            inventory = root / 'before.json'
            inventory.write_text(json.dumps({'executable_sha256': sha256(data),
                'functions': [{'entry': '00001000', 'instructions': [
                    {'address': '00001000', 'bytes': '01000000'}]}]}))
            output = StringIO()
            argv = ['observation', str(root), str(inventory), str(root / 'missing-after'),
                    str(root / 'missing-boundary'), '--output', str(root / 'receipts')]
            with patch.object(sys, 'argv', argv), redirect_stdout(output), \
                 patch.object(observation, 'EE_CORPUS_SHA256', sha256(data)), \
                 patch.object(observation, 'corpus_identity', side_effect=Incomplete('absent disc')):
                result = observation.main()
            self.assertEqual(result, 1, output.getvalue())
            self.assertIn('saved instruction differs', output.getvalue())

    def test_missing_only_metadata_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run([sys.executable,
                                     str(Path(__file__).with_name('misc3d_lifecycle_observation.py')),
                                     str(root), str(root / 'missing-before'), str(root / 'missing-after'),
                                     str(root / 'missing-boundary'), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_changed_ee_wins_over_missing_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'extracted').mkdir()
            ee = root / 'extracted/SLES_517.05'
            ee.write_bytes(b'changed executable')
            result = subprocess.run([sys.executable,
                                     str(Path(__file__).with_name('misc3d_lifecycle_observation.py')),
                                     str(root), str(root / 'missing-before'), str(root / 'missing-after'),
                                     str(root / 'missing-boundary'), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)['result']).read_text())
            self.assertIn(str(ee), report['inputs'])


if __name__ == '__main__':
    unittest.main()
