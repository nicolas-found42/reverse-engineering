"""Controls for fixed-path decision tables and evidence/source binding failures."""
import shutil
import tempfile
import unittest
from pathlib import Path

from evidence_common import Invalid
from recorded_decisions import GAME_OWNED_RANGES, ROOT, TABLE_PINS, read_decisions


class RecordedDecisionTests(unittest.TestCase):
    def fixture(self, root):
        shutil.copytree(ROOT / 'config', root / 'config')
        for row in read_decisions()['units']:
            for field in ('source', 'decision', 'evidence'):
                target = root / row[field]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row[field], target)
        for row in read_decisions()['flags']:
            target = root / row['probe']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['probe'], target)

    def test_positive_bounded_decision(self):
        self.assertEqual(GAME_OWNED_RANGES, (('.text', 0x1d1800, 0x1d183c),))
        self.assertEqual(read_decisions()['flags'][0]['status'], 'exploratory')

    def test_mutated_table_cannot_expand_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / 'config/units.tsv'
            path.write_text(path.read_text().replace('001d183c', '001d2000'))
            with self.assertRaisesRegex(Invalid, 'pin changed'):
                read_decisions(root)

    def test_changed_source_revokes_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / read_decisions()['units'][0]['source']).write_text('int changed;\n')
            with self.assertRaisesRegex(Invalid, 'provenance changed'):
                read_decisions(root)

    def test_missing_table_is_incomplete_input_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'config' / next(iter(TABLE_PINS))).unlink()
            with self.assertRaisesRegex(Invalid, 'missing'):
                read_decisions(root)


if __name__ == '__main__':
    unittest.main()
