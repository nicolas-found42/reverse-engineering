"""Pytest collection hooks mirroring tools/run_tests.py's optional-dependency skip.

tools/run_tests.py skips a test module whose import fails because a third-party
module is missing (unittest does this naturally at load time; pytest raises a
collection error instead). Mirror that behavior for the one optional import:
"""
from importlib.util import find_spec
from pathlib import Path

if find_spec("typesafe_sdk") is None:
    collect_ignore = [str(Path(__file__).parent / "test_research_jev_battery.py")]
