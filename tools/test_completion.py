import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import completion

from completion import aggregate_ledger, reconstruction_status
from evidence_common import Invalid

TOOLS = Path(__file__).resolve().parent


class CompletionCli(unittest.TestCase):
    def fixture_children(self, failures=()):
        """Exercise the aggregate report seam with bounded child verdicts."""
        def child(name, arguments, output):
            status = 'fail' if name in failures else 'incomplete'
            if name in ('misc3d_contract.py', 'misc3d_lifecycle.py') and name not in failures:
                status = 'pass'
            result = {'status': status, 'details': {},
                      'diagnostics': ['located child mismatch'] if status == 'fail' else []}
            return {'status': status, 'command': [name], 'diagnostics': result['diagnostics']}, result
        return child

    def test_bounded_child_pass_retains_evidence_without_completing_full_ee_or_rpc(self):
        with patch.object(completion, 'run_child', side_effect=self.fixture_children()), \
             patch.object(completion, 'source_unit_credit', return_value=0):
            with self.assertRaises(Incomplete) as caught:
                completion.check(Path('/fixture/game'), self.root, None, None, self.root)
        details = caught.exception.details
        self.assertEqual(details['reconstruction_status'], 'incomplete')
        for criterion in (6, 8, 9, 14, 15):
            row = details['criteria'][criterion - 1]
            self.assertEqual(row['status'], 'incomplete')
            self.assertTrue(row['evidence'], row['id'])
        self.assertEqual(details['ledger']['matched_bytes'], 0)

    def test_available_ee_and_rpc_child_mismatch_overrides_missing_full_build(self):
        for name, criterion in (('linker_layout.py', 6), ('misc3d_contract.py', 9),
                                ('misc3d_lifecycle.py', 8),
                                ('misc3d_loader_recipe/source_build.py', 8),
                                ('inventory_rpc_handoffs.py', 14),
                                ('check_rpc_contracts.py', 15)):
            with self.subTest(child=name):
                with patch.object(completion, 'run_child', side_effect=self.fixture_children((name,))), \
                     patch.object(completion, 'source_unit_credit', return_value=0):
                    with self.assertRaises(Invalid) as caught:
                        completion.check(Path('/fixture/game'), self.root, None, None, self.root)
                details = caught.exception.details
                self.assertEqual(details['reconstruction_status'], 'fail')
                self.assertEqual(details['criteria'][criterion - 1]['status'], 'fail')
                self.assertEqual(details['criteria'][11]['status'], 'incomplete')

    def test_malformed_child_receipt_is_retained_as_failure_instead_of_losing_criteria(self):
        script = self.root / 'bad_child.py'
        script.write_text('''import json, pathlib, sys
root = pathlib.Path(sys.argv[sys.argv.index('--output') + 1]) / 'original'
root.mkdir(parents=True)
(root / 'report.md').write_text('original child report')
(root / 'result.json').write_text(json.dumps({
    'status': 'pass', 'details': {}, 'artifacts': {'report.md': {'bytes': 0, 'sha256': '0' * 64}}
}))
''')
        with patch.object(completion, 'TOOLS', self.root):
            child, result = completion.run_child('bad_child.py', [], self.root / 'child')
        self.assertEqual((child['status'], result['status']), ('fail', 'fail'))
        self.assertTrue(child['validation_failure'])
        original = self.root / 'child/original/result.json'
        self.assertTrue(original.is_file())
        self.assertEqual(result['details']['rejected_receipts'][0]['sha256'],
                         completion.identity(original)['sha256'])
        children = self.fixture_children()
        def with_rejection(name, arguments, output):
            return (child, result) if name == 'misc3d_contract.py' else children(name, arguments, output)
        with patch.object(completion, 'run_child', side_effect=with_rejection), \
             patch.object(completion, 'source_unit_credit', return_value=0):
            with self.assertRaises(Invalid) as caught:
                completion.check(Path('/fixture/game'), self.root, None, None, self.root)
        criteria = caught.exception.details['criteria']
        self.assertEqual(len(criteria), 32)
        self.assertEqual(criteria[1]['status'], 'fail')

    def test_entry_evidence_failure_does_not_fail_exact_vu_encoding(self):
        results = [
            {'status': 'pass', 'details': {}},
            {'status': 'pass', 'details': {}},
            {'status': 'fail', 'details': {
                'exact_roundtrip_overlays': 8,
                'overlays': [{'index': i, 'byte_gate': {'status': 'pass'}} for i in range(8)],
                'entry_map': {'status': 'fail', 'diagnostic': 'changed evidence'}}},
            {'status': 'incomplete', 'details': {}},
            {'status': 'incomplete', 'details': {}},
            *[{'status': 'incomplete', 'details': {}} for _ in range(6)],
        ]
        children = [({'status': result['status']}, result) for result in results]
        with patch.object(completion, 'run_child', side_effect=children), \
             patch.object(completion, 'source_unit_credit', return_value=0):
            with self.assertRaises(Invalid) as caught:
                completion.check(Path('/fixture/game'), self.root, None, None, self.root)
        criteria = caught.exception.details['criteria']
        self.assertEqual(criteria[15]['status'], 'pass')
        self.assertEqual(criteria[16]['status'], 'fail')

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
        required_public_inputs = {
            TOOLS / 'compiler_probe.py', recipe / 'run.py', recipe / 'build.py',
            TOOLS / 'matching_diff.py', TOOLS / 'matching_sections.py',
            TOOLS / 'corpus_contract.py', TOOLS / 'ps2_executables.py',
            TOOLS / 'evidence_common.py',
            TOOLS.parent / 'reconstruction/ee/app3d/misc3d_db_id.c',
            TOOLS.parent / 'docs/adr/0005-game-owned-sdk-boundary.md',
            TOOLS.parent / 'notes/evidence/fr2-source-map/source-map-result.json',
            recipe / 'candidate.ld', recipe / 'manifest.template.json',
            recipe / 'docker-linux-exec.sh', recipe / 'docker-wine-exec.sh',
        }
        optional_private_inputs = {
            TOOLS.parent / 'notes/evidence/fr2-first-unit/adr0005-misc3d-boundary.json',
            TOOLS.parent / 'notes/evidence/fr2-first-unit/saved-function-inventory-digest.json',
        }
        self.assertTrue(required_public_inputs <= inputs)
        for path in optional_private_inputs:
            self.assertEqual(path in inputs, path.is_file(), str(path))

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
        for flag in ('--skip', '--scope', '--denominator', '--receipts'):
            run = subprocess.run([sys.executable, str(TOOLS / 'completion.py'),
                                  str(self.root / 'game'), '--output', str(self.root / 'reports'),
                                  flag, '0'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('unrecognized arguments', run.stderr)

    def test_real_corpus_cli_conserves_bytes_and_references_limited_ac30_evidence(self):
        game = TOOLS.parent / 'games/ford-racing-2'
        compiler_tools = Path.home() / 'Documents/github/hermes/spec-5-tools/compilers'
        if not (game / 'extracted/IRX/USBD.IRX').is_file() or not compiler_tools.is_dir():
            self.skipTest('real aggregate CLI control needs local corpus and compiler tools')
        output = self.root / 'real-aggregate'
        run = subprocess.run([sys.executable, str(TOOLS / 'completion.py'), str(game),
                              '--compiler-tools', str(compiler_tools), '--output', str(output)],
                             capture_output=True, text=True, timeout=300)
        receipt = next(output.glob('*/result.json'))
        result = json.loads(receipt.read_text())
        self.assertEqual((run.returncode, result['status']), (2, 'incomplete'), result['diagnostics'])
        details = result['details']
        ledger = details['ledger']
        total = ledger['file_backed_bytes'] + ledger['zero_fill_bytes']
        self.assertEqual(total, ledger['unresolved_bytes'] + ledger['game_owned_bytes']
                         + ledger['substitute_bytes'])
        self.assertEqual((ledger['game_owned_bytes'], ledger['matched_bytes'],
                          ledger['unresolved_bytes']), (60, 60, total - 60))
        self.assertEqual(ledger['matched_fraction_scope'], 'attributed_game_owned_bytes')
        self.assertEqual(details['criteria'][6]['status'], 'pass')
        self.assertEqual(details['criteria'][4]['status'], 'incomplete')
        for index in (26, 28, 29, 30, 31):
            self.assertEqual(details['criteria'][index]['status'], 'incomplete')
            self.assertTrue(details['criteria'][index]['evidence'])
        self.assertFalse(details['real_corpus_completion'])


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

    def test_source_unit_credit_conserves_partition_and_fraction_is_owned_scope_only(self):
        details = {'file_backed_bytes': 2171407, 'zero_fill_bytes': 1335641,
                   'game_owned_bytes': 60, 'substitute_bytes': 0,
                   'unresolved_bytes': 3506988}
        ledger = aggregate_ledger(details, 60)
        self.assertEqual(ledger['file_backed_bytes'] + ledger['zero_fill_bytes'],
                         ledger['unresolved_bytes'] + ledger['game_owned_bytes']
                         + ledger['substitute_bytes'])
        self.assertEqual((ledger['matched_bytes'], ledger['matched_fraction'],
                          ledger['matched_fraction_scope']),
                         (60, 1.0, 'attributed_game_owned_bytes'))

    def test_double_subtraction_and_ownership_overcredit_fail_conservation(self):
        details = {'file_backed_bytes': 2171407, 'zero_fill_bytes': 1335641,
                   'game_owned_bytes': 60, 'substitute_bytes': 0,
                   'unresolved_bytes': 3506928}
        with self.assertRaises(Invalid):
            aggregate_ledger({**details, 'unresolved_bytes': 3506928 - 60}, 60)
        with self.assertRaises(Invalid):
            aggregate_ledger(details, 61)


if __name__ == '__main__':
    unittest.main()
