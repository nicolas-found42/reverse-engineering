import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from completion import reconstruction_status
from evidence_common import Invalid

TOOLS = Path(__file__).resolve().parent


class CompletionCli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_completion(self):
        output = self.root / 'reports'
        before = set(output.glob('*/result.json'))
        process = subprocess.run([sys.executable, str(TOOLS / 'completion.py'),
                                  str(self.root / 'game'), '--output', str(output)],
                                 capture_output=True, text=True, timeout=30)
        receipts = list(set(output.glob('*/result.json')) - before)
        self.assertEqual(len(receipts), 1, process.stderr)
        result = json.loads(receipts[0].read_text())
        self.assertTrue(receipts[0].with_name('report.md').is_file())
        return process.returncode, result

    def test_missing_corpus_retains_every_criterion_and_child_receipts_as_incomplete(self):
        code, result = self.run_completion()
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        details = result['details']
        self.assertEqual([c['id'] for c in details['criteria']],
                         [f'AC{n:02d}' for n in range(1, 33)])
        self.assertEqual(details['behavioral']['status'], 'incomplete')
        self.assertTrue(details['criteria'][4]['evidence'])
        self.assertEqual(details['criteria'][4]['status'], 'incomplete')
        self.assertEqual(details['ledger']['matched_bytes'], 0)
        self.assertFalse(details['real_corpus_completion'])
        self.assertTrue(details['children'])
        for child in details['children']:
            self.assertTrue(Path(child['receipt']).is_file())
            self.assertEqual(len(child['sha256']), 64)
        inputs = {Path(path) for path in result['inputs']}
        recipe = TOOLS / 'compiler_probe_recipe'
        self.assertTrue({TOOLS / 'compiler_probe.py', recipe / 'run.py', recipe / 'build.py',
                         TOOLS / 'matching_diff.py', TOOLS / 'matching_sections.py',
                         TOOLS / 'corpus_contract.py', TOOLS / 'ps2_executables.py',
                         TOOLS / 'evidence_common.py',
                         recipe / 'candidate.c', recipe / 'candidate.ld',
                         recipe / 'manifest.template.json', recipe / 'docker-linux-exec.sh',
                         recipe / 'docker-wine-exec.sh'} <= inputs)

    def test_changed_present_input_fails_even_when_other_required_inputs_are_missing(self):
        game = self.root / 'game'
        game.mkdir()
        (game / 'ford-racing-2.bin').write_bytes(b'changed disc input')
        code, result = self.run_completion()
        self.assertEqual((code, result['status']), (1, 'fail'))
        criterion = result['details']['criteria'][0]
        self.assertEqual(criterion['status'], 'fail')
        self.assertIn('changed corpus input', json.dumps(criterion['evidence']))

    def test_repeated_attempt_preserves_prior_receipts(self):
        self.run_completion()
        before = {path: path.read_bytes() for path in (self.root / 'reports').rglob('result.json')}
        self.run_completion()
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertEqual(len(list((self.root / 'reports').glob('*/result.json'))), 2)

    def test_skip_and_scope_flags_cannot_turn_absence_into_success(self):
        for flag in ('--skip', '--scope', '--denominator'):
            run = subprocess.run([sys.executable, str(TOOLS / 'completion.py'),
                                  str(self.root / 'game'), '--output', str(self.root / 'reports'),
                                  flag, '0'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('unrecognized arguments', run.stderr)


class ReconstructionReport(unittest.TestCase):
    def complete(self):
        criteria = [{'id': f'AC{n:02d}', 'status': 'pass', 'evidence': ['current receipt']}
                    for n in range(1, 33)]
        return criteria, {'game_owned_bytes': 4, 'matched_bytes': 4, 'unresolved_bytes': 0}

    def test_nonempty_complete_reconstruction_reports_pass_with_behavior_unverified(self):
        criteria, ledger = self.complete()
        for row in criteria[24:26]:
            row['status'] = 'incomplete'
        self.assertEqual(reconstruction_status(criteria, ledger, authority='real_corpus'), 'pass')

    def test_required_mismatch_takes_precedence_over_incomplete(self):
        criteria, ledger = self.complete()
        criteria[0]['status'], criteria[7]['status'] = 'incomplete', 'fail'
        self.assertEqual(reconstruction_status(criteria, ledger, authority='real_corpus'), 'fail')

    def test_synthetic_success_empty_scope_or_missing_criteria_cannot_pass(self):
        criteria, ledger = self.complete()
        self.assertEqual(reconstruction_status(criteria, ledger, authority='synthetic'), 'incomplete')
        ledger['game_owned_bytes'] = ledger['matched_bytes'] = 0
        self.assertEqual(reconstruction_status(criteria, ledger, authority='real_corpus'), 'incomplete')
        with self.assertRaises(Invalid):
            reconstruction_status(criteria[:-1], ledger, authority='real_corpus')

    def test_unmatched_unresolved_or_evidenceless_required_work_cannot_pass(self):
        for mutation in ('unmatched', 'unresolved', 'evidence'):
            criteria, ledger = self.complete()
            if mutation == 'unmatched':
                ledger['matched_bytes'] = 3
            elif mutation == 'unresolved':
                ledger['unresolved_bytes'] = 1
            else:
                criteria[0]['evidence'] = []
            self.assertEqual(reconstruction_status(criteria, ledger, authority='real_corpus'), 'incomplete')


if __name__ == '__main__':
    unittest.main()
