"""Public source-record controls; inventories cannot qualify guest execution."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from evidence_common import Incomplete, Invalid
from oracle_dependency_sources import check, verify_source_records


class OracleSourceRecords(unittest.TestCase):
    # SHA1 of the literal b'abc', independently known from the SHA1 test vector.
    RECORD = b'FileName: ./source.c\nFileChecksum: SHA1: a9993e364706816aba3e25717850c26c9cd0d89d\n'

    def test_positive_record_comparison_has_zero_byte_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.c').write_bytes(b'abc')
            result = verify_source_records(self.RECORD, root)
        self.assertEqual(result['checked_files'], 1)
        self.assertEqual(result['matched_bytes'], 0)

    def test_changed_source_fails_even_with_another_file_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.c').write_bytes(b'changed')
            records = self.RECORD + self.RECORD.replace(b'source.c', b'missing.c')
            with self.assertRaises(Invalid) as caught:
                verify_source_records(records, root)
        self.assertEqual(caught.exception.details['missing'], ['missing.c'])
        self.assertEqual(caught.exception.details['changed'][0]['path'], 'source.c')

    def test_missing_source_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Incomplete):
                verify_source_records(self.RECORD, Path(directory))

    def test_empty_duplicate_malformed_and_escaping_records_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            for records in (b'', self.RECORD * 2,
                            self.RECORD.replace(b'a9993e364706816aba3e25717850c26c9cd0d89d', b'wrong'),
                            self.RECORD.replace(b'./source.c', b'../source.c')):
                with self.subTest(records=records), self.assertRaises(Invalid):
                    verify_source_records(records, Path(directory))

    def test_available_changed_installed_executable_outranks_missing_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / 'app/Contents/MacOS/PCSX2'
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'changed PCSX2')
            with self.assertRaises(Invalid) as caught:
                check(root / 'evidence', root / 'sdk', root / 'sdk.7z', root / 'app')
        self.assertIn(str(executable), caught.exception.details['changed'])

    def test_admitted_source_contradiction_outranks_other_missing_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = root / 'sdk/sbom/qtbase-6.10.1.source.spdx'
            record.parent.mkdir(parents=True)
            record.write_bytes(self.RECORD)
            source = root / 'evidence/qtbase-git/source.c'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'changed')
            with patch('oracle_dependency_sources.SOURCE_RECORD_SHA256',
                       hashlib.sha256(self.RECORD).hexdigest()):
                with self.assertRaises(Invalid) as caught:
                    check(root / 'evidence', root / 'sdk', root / 'sdk.7z', root / 'app')
        self.assertEqual(caught.exception.details['sdk_source_inventory']['changed'][0]['path'], 'source.c')
        self.assertTrue(caught.exception.details['missing'])

    def test_public_cli_negative_and_incomplete_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / 'app'
            command = [sys.executable, str(Path(__file__).with_name('oracle_dependency_sources.py')),
                       str(root / 'evidence'), str(root / 'sdk'), str(root / 'sdk.7z'),
                       '--app', str(app), '--output', str(root / 'receipts')]
            run = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            missing_receipt = Path(json.loads(run.stdout)['result'])
            retained = missing_receipt.read_bytes()
            executable = app / 'Contents/MacOS/PCSX2'
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'changed PCSX2')
            run = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
            result = json.loads(Path(json.loads(run.stdout)['result']).read_text())
            self.assertIn(str(executable), result['details']['changed'])
            self.assertTrue(result['details']['missing'])
            self.assertEqual(missing_receipt.read_bytes(), retained)


if __name__ == '__main__':
    unittest.main()
