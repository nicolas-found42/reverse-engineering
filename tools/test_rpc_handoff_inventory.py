"""Public CLI priority controls; synthetic inputs contain no corpus bytes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class RpcFrontierPriority(unittest.TestCase):
    def test_cli_missing_only_frontier_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('inventory_rpc_handoffs.py')),
                                     str(root), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_cli_available_malformed_rom_wins_over_missing_ee(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'IRX').mkdir()
            rom = root / 'IRX/IOPRP255.IMG'
            rom.write_bytes(b'')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('inventory_rpc_handoffs.py')),
                                     str(root), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)['result']).read_text())
            self.assertIn('ROMDIR prefix', report['diagnostics'][0])
            self.assertIn(str(rom), report['inputs'])

    def test_cli_missing_ee_and_rom_cannot_hide_changed_pinned_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'IRX').mkdir()
            module = root / 'IRX/STREAM.IRX'
            module.write_bytes(b'changed pinned module')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('inventory_rpc_handoffs.py')),
                                     str(root), '--output', str(root / 'receipts')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(Path(json.loads(result.stdout)['result']).read_text())
            self.assertIn('STREAM.IRX exact static identity mismatch', report['diagnostics'][0])
            self.assertIn(str(module), report['inputs'])


if __name__ == '__main__':
    unittest.main()
