import unittest

from compiler_probe_recipe.profile import summarize, CANDIDATE_IDS, UNIT_IDS


class CompilerProfileTests(unittest.TestCase):
    def panel(self):
        return [{'unit': name, 'candidates': [
            {'id': candidate, 'status': 'pass' if candidate == 'ee-gcc2.96' else 'fail',
             'compiler_output': {'status': 'pass' if candidate == 'ee-gcc2.96' else 'fail'}}
            for candidate in CANDIDATE_IDS]} for name in UNIT_IDS]

    def test_known_matching_panel_selects_declared_profile(self):
        result = summarize(self.panel())
        self.assertEqual((result['profile_status'], result['selected_id']), ('pass', 'ee-gcc2.96'))
        self.assertEqual(result['ac05_status'], 'incomplete')
        self.assertEqual(result['matched_bytes'], 0)

    def test_nonmatching_candidates_are_retained_for_every_unit(self):
        panel = self.panel()
        result = summarize(panel)
        self.assertEqual(len(result['unit_outcomes']), 4)
        self.assertTrue(all(row['matches'] == ['ee-gcc2.96'] for row in result['unit_outcomes']))

    def test_one_contradictory_independent_unit_prevents_selection(self):
        panel = self.panel()
        for row in panel[-1]['candidates']:
            row['status'] = 'pass' if row['id'] == 'ee-gcc2.9-991111-01' else 'fail'
            row['compiler_output']['status'] = row['status']
        result = summarize(panel)
        self.assertEqual((result['profile_status'], result['selected_id']), ('fail', None))
        self.assertEqual(result['unit_outcomes'][-1]['matches'], ['ee-gcc2.9-991111-01'])

    def test_missing_tool_or_diagnostic_is_incomplete_even_with_a_match(self):
        for status in ('incomplete', 'error'):
            panel = self.panel()
            panel[-1]['candidates'][0]['status'] = status
            result = summarize(panel)
            self.assertEqual((result['profile_status'], result['selected_id']), ('incomplete', None))
        panel = self.panel()
        del panel[-1]['candidates'][0]['compiler_output']
        self.assertEqual(summarize(panel)['profile_status'], 'incomplete')

    def test_ambiguity_is_preserved(self):
        panel = self.panel()
        for probe in panel:
            probe['candidates'][0].update(status='pass', compiler_output={'status': 'pass'})
        result = summarize(panel)
        self.assertEqual(result['profile_status'], 'incomplete')
        self.assertEqual(len(result['surviving_candidates']), 2)

    def test_missing_unit_duplicate_unit_or_replaced_candidate_is_incomplete(self):
        from evidence_common import Incomplete
        panel = self.panel()
        for probes in (panel[:-1], [panel[0], *panel[:-1]]):
            with self.assertRaisesRegex(Incomplete, 'required unit'):
                summarize(probes)
        panel[-1]['candidates'][0]['id'] = 'replacement'
        with self.assertRaisesRegex(Incomplete, 'candidate identities'):
            summarize(panel)

    def test_cli_missing_corpus_writes_incomplete_receipt(self):
        import json
        from pathlib import Path
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run([sys.executable,
                str(Path(__file__).with_name('compiler_probe_recipe') / 'run.py'),
                str(root / 'missing-game'), str(root / 'missing-tools'), '--profile',
                '--output', str(root / 'receipts')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            saved = json.loads(next((root / 'receipts').glob('*/result.json')).read_text())
            self.assertEqual(saved['status'], 'incomplete')
            self.assertTrue(saved['diagnostics'])
