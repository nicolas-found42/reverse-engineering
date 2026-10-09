#!/usr/bin/env python3
"""Run the tool tests with the paths they expect, so green means green.

    tools/check.sh                      # whole suite
    tools/check.sh test_matching        # narrow run: module names or dotted test ids

Puts `tools/` and the repository root on sys.path (tests import flat modules and `tools.*`).
Only recorded module/dependency pairs may be skipped during discovery. Named
modules are never skipped. CI excludes NEEDS_LOCAL_INPUTS by name; unexpected
imports, failures and errors remain red. Counts and skip reasons are JSON.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
MISSING = re.compile(r"ModuleNotFoundError: No module named '([\w.]+)'")


def leaves(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from leaves(item)
        else:
            yield item


# Tests that read gitignored local inputs (.scratch exports, the corpus). In CI they are skipped
# by name; locally they run. Move a module off this list once it builds its own fixtures.
NEEDS_LOCAL_INPUTS = frozenset({"test_batch_switch_config", "test_recomp_fpu_experimental"})
# Only these exact module/dependency pairs may disappear from a discovered suite.
OPTIONAL_DEPENDENCIES = {"test_research_jev_battery": frozenset({"typesafe_sdk"})}


def skip_local_inputs(suite: unittest.TestSuite) -> tuple[unittest.TestSuite, list[dict]]:
    kept, skipped = unittest.TestSuite(), []
    for test in leaves(suite):
        module = type(test).__module__
        if module in NEEDS_LOCAL_INPUTS:
            note = {'module': module, 'reason': 'local_inputs', 'inputs': ['.scratch', 'corpus']}
            if note not in skipped:
                skipped.append(note)
            continue
        kept.addTest(test)
    return kept, skipped


def local_module(name: str) -> bool:
    top = name.split(".")[0]
    return (TOOLS / f"{top}.py").exists() or (TOOLS / top).is_dir() or (ROOT / top).is_dir()


def skip_missing_dependencies(suite: unittest.TestSuite) -> tuple[unittest.TestSuite, list[dict]]:
    kept, skipped = unittest.TestSuite(), []
    for test in leaves(suite):
        if type(test).__name__ == "_FailedTest":
            found = MISSING.findall(str(test._exception))
            allowed = OPTIONAL_DEPENDENCIES.get(test._testMethodName, frozenset())
            missing = [name for name in found if name in allowed and not local_module(name)]
            if found and len(missing) == len(found):
                skipped.append({'module': test._testMethodName, 'reason': 'optional_dependency',
                                'dependencies': sorted(set(missing))})
                continue
        kept.addTest(test)
    return kept, skipped


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, help='Write counts and explicit skip reasons as JSON')
    parser.add_argument('modules', nargs='*')
    args = parser.parse_args(argv)
    for path in (str(ROOT), str(TOOLS)):
        if path not in sys.path:
            sys.path.insert(0, path)
    loader = unittest.TestLoader()
    skipped: list[dict] = []
    if args.modules:  # named tests must exist: no skipping
        suite = loader.loadTestsFromNames(args.modules)
    else:
        suite = loader.discover(str(TOOLS), pattern="test_*.py", top_level_dir=str(TOOLS))
        suite, skipped = skip_missing_dependencies(suite)
        if os.environ.get("CI"):
            suite, ci_skipped = skip_local_inputs(suite)
            skipped += ci_skipped
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    summary = {'schema': 'fr2-test-summary/v1', 'successful': result.wasSuccessful(),
               'tests_run': result.testsRun, 'failures': len(result.failures),
               'errors': len(result.errors),
               'skipped_tests': [{'test': test.id(), 'reason': reason} for test, reason in result.skipped],
               'excluded_modules': skipped}
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
