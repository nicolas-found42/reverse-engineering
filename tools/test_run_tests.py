import unittest

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
        self.assertEqual(skipped, [f"{Sample.__module__} (needs local inputs: .scratch or the corpus)"])

    def test_unlisted_modules_are_kept(self):
        kept, skipped = run_tests.skip_local_inputs(self.suite())
        self.assertEqual(len(list(run_tests.leaves(kept))), 1)
        self.assertEqual(skipped, [])

    def test_the_listed_modules_exist(self):
        for name in run_tests.NEEDS_LOCAL_INPUTS:
            self.assertTrue((run_tests.TOOLS / f"{name}.py").exists(), name)


if __name__ == "__main__":
    unittest.main()
