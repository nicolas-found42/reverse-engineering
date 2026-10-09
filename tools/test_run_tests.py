import unittest
import tempfile
from pathlib import Path

import run_tests


class Sample(unittest.TestCase):
    def test_a(self):
        pass


class SkipLocalInputsTest(unittest.TestCase):
    def suite(self):
        suite = unittest.TestSuite()
        suite.addTest(Sample("test_a"))
        return suite

    def test_listed_modules_are_skipped_by_name_in_ci(self):
        original = run_tests.NEEDS_LOCAL_INPUTS
        run_tests.NEEDS_LOCAL_INPUTS = frozenset({Sample.__module__})
        try:
            kept, skipped = run_tests.skip_local_inputs(self.suite())
        finally:
            run_tests.NEEDS_LOCAL_INPUTS = original
        self.assertEqual(list(run_tests.leaves(kept)), [])
        self.assertEqual(skipped, [{'module': Sample.__module__, 'reason': 'local_inputs',
                                   'inputs': ['.scratch', 'corpus']}])

    def test_unlisted_modules_are_kept(self):
        kept, skipped = run_tests.skip_local_inputs(self.suite())
        self.assertEqual(len(list(run_tests.leaves(kept))), 1)
        self.assertEqual(skipped, [])

    def test_the_listed_modules_exist(self):
        for name in run_tests.NEEDS_LOCAL_INPUTS:
            self.assertTrue((run_tests.TOOLS / f"{name}.py").exists(), name)

    def discovery(self, name, dependency):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, name + '.py').write_text('import ' + dependency + '\n')
            return unittest.TestLoader().discover(directory, top_level_dir=directory)

    def test_unexpected_external_import_is_a_failure(self):
        suite = self.discovery('test_retro_unexpected', 'unrecognized_dependency_probe')
        kept, skipped = run_tests.skip_missing_dependencies(suite)
        self.assertEqual(kept.countTestCases(), 1)
        self.assertEqual(skipped, [])

    def test_optional_dependency_is_scoped_to_its_module(self):
        suite = self.discovery('test_retro_optional', 'unrecognized_dependency_probe')
        from unittest.mock import patch
        with patch.dict(run_tests.OPTIONAL_DEPENDENCIES,
                        {'test_retro_optional': frozenset({'unrecognized_dependency_probe'})}):
            kept, skipped = run_tests.skip_missing_dependencies(suite)
        self.assertEqual(kept.countTestCases(), 0)
        self.assertEqual(len(skipped), 1)

    def test_optional_dependency_typo_stays_red(self):
        suite = self.discovery('test_retro_typo', 'typesafe_sdk_typo')
        kept, skipped = run_tests.skip_missing_dependencies(suite)
        self.assertEqual(kept.countTestCases(), 1)
        self.assertEqual(skipped, [])


if __name__ == "__main__":
    unittest.main()
