#!/usr/bin/env python3
"""Run the tool tests with the paths they expect, so green means green.

    tools/check.sh                      # whole suite
    tools/check.sh test_matching        # narrow run: module names or dotted test ids

Puts `tools/` and the repository root on sys.path (tests import flat modules and `tools.*`).
In a whole-suite run, a test module whose import fails because a third-party module is
missing is skipped and named in the summary; named modules are never skipped; with CI set, modules in NEEDS_LOCAL_INPUTS are skipped by name; any other import failure, failure or error stays red.
"""
from __future__ import annotations

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


def skip_local_inputs(suite: unittest.TestSuite) -> tuple[unittest.TestSuite, list[str]]:
    kept, skipped = unittest.TestSuite(), []
    for test in leaves(suite):
        module = type(test).__module__
        if module in NEEDS_LOCAL_INPUTS:
            note = f"{module} (needs local inputs: .scratch or the corpus)"
            if note not in skipped:
                skipped.append(note)
            continue
        kept.addTest(test)
    return kept, skipped


def local_module(name: str) -> bool:
    top = name.split(".")[0]
    return (TOOLS / f"{top}.py").exists() or (TOOLS / top).is_dir() or (ROOT / top).is_dir()


def skip_missing_dependencies(suite: unittest.TestSuite) -> tuple[unittest.TestSuite, list[str]]:
    kept, skipped = unittest.TestSuite(), []
    for test in leaves(suite):
        if type(test).__name__ == "_FailedTest":
            found = MISSING.findall(str(test._exception))
            missing = [name for name in found if not local_module(name)]
            if found and len(missing) == len(found):
                skipped.append(f"{test._testMethodName} (needs {', '.join(sorted(set(missing)))})")
                continue
        kept.addTest(test)
    return kept, skipped


def main(argv: list[str]) -> int:
    for path in (str(ROOT), str(TOOLS)):
        if path not in sys.path:
            sys.path.insert(0, path)
    loader = unittest.TestLoader()
    skipped: list[str] = []
    if argv:  # named tests must exist: no skipping
        suite = loader.loadTestsFromNames(argv)
    else:
        suite = loader.discover(str(TOOLS), pattern="test_*.py", top_level_dir=str(TOOLS))
        suite, skipped = skip_missing_dependencies(suite)
        if os.environ.get("CI"):
            suite, ci_skipped = skip_local_inputs(suite)
            skipped += ci_skipped
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    for line in skipped:
        print(f"SKIPPED (missing dependency): {line}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
