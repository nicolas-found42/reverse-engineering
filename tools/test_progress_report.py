"""Controls for zero-credit structural export, conservation and address semantics."""
import copy
import json
import unittest

from evidence_common import Invalid
from progress_report import ROOT, LEDGER_PATH, build_report


class ProgressReportTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / LEDGER_PATH).read_text())

    def test_positive_export_has_no_fresh_match_or_completion_credit(self):
        report = build_report(self.snapshot)
        self.assertEqual(report['version'], 2)
        for field in ('matched_code', 'matched_data', 'complete_code', 'complete_data'):
            self.assertEqual(report['measures'][field], '0')
        self.assertNotIn('matched_code_percent', report['measures'])
        self.assertEqual(int(report['measures']['total_code']) + int(report['measures']['total_data']), 3507048)
        owned = next(c for c in report['categories'] if c['id'] == 'game-owned')
        self.assertEqual(owned['measures']['total_code'], '60')
        unit = next(u for u in report['units'] if u['metadata']['progress_categories'] == ['game-owned'])
        item = unit['sections'][0]
        self.assertEqual(item['address'], str(0x1d1800 - 0x100000))
        self.assertEqual(item['metadata']['virtual_address'], str(0x1d1800))

    def test_imported_historical_credit_is_rejected(self):
        self.snapshot['details']['matched_bytes'] = 60
        with self.assertRaisesRegex(Invalid, 'cannot earn'):
            build_report(self.snapshot)

    def test_expanded_owned_range_is_rejected(self):
        row = next(x for x in self.snapshot['details']['artifacts'][0]['ranges']
                   if x['classification'] == 'game_owned')
        row['classification'] = 'mixed_unresolved'
        with self.assertRaisesRegex(Invalid, 'denominator'):
            build_report(self.snapshot)

    def test_overlapping_ranges_are_rejected(self):
        ranges = self.snapshot['details']['artifacts'][0]['ranges']
        ranges[1]['address'] = ranges[0]['address']
        with self.assertRaisesRegex(Invalid, 'overlapping'):
            build_report(self.snapshot)

    def test_nonconserving_total_is_rejected(self):
        self.snapshot['details']['zero_fill_bytes'] += 4
        with self.assertRaisesRegex(Invalid, 'conservation'):
            build_report(self.snapshot)

    def test_incomplete_inventory_is_not_a_passing_report(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['status'] = 'incomplete'
        with self.assertRaisesRegex(Invalid, 'did not pass'):
            build_report(snapshot)


if __name__ == '__main__':
    unittest.main()
