"""Failure-path checks for research acceptance; never make API requests."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import research_jev_battery as battery


class BatteryFailures(unittest.TestCase):
    def invoke(self, *, intake="pass", confidence=1.0, probabilities=None, error=None):
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "fixture.json"
            output = Path(temp) / "output.json"
            fixture.write_text(json.dumps([{
                "id": "control", "intake": intake,
                "source": "First-party source states the documented feature.",
                "source_url": "https://example.org/source", "claim": "The feature is documented.",
                "expected": "supports",
            }]))
            client = MagicMock()
            response = SimpleNamespace(
                answers={
                    "relation": SimpleNamespace(choice="supports", confidence=confidence, probabilities=probabilities or {"supports": 1.0, "contradicts": 0.0, "says_nothing": 0.0}),
                    "ps2_validation": SimpleNamespace(noul=0.0),
                    "overreach": SimpleNamespace(noul=0.0),
                },
                model_dump=lambda **kw: {"answers": {}, "usage": {"input_tokens": 1, "output_tokens": 1}},
            )
            client.system_one.side_effect = error
            client.system_one.return_value = response
            with patch.object(battery, "TypeSafeClient") as constructor, patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-placeholder"}), contextlib.redirect_stdout(io.StringIO()):
                constructor.return_value.__enter__.return_value = client
                if intake == "block":
                    with self.assertRaises(ValueError):
                        battery.run(fixture, output)
                    self.assertEqual(client.system_one.call_count, 0)
                    return None, None, client
                code = battery.run(fixture, output)
            return code, json.loads(output.read_text()), client

    def test_blocked_source_never_reaches_api(self):
        self.invoke(intake="block")

    def test_expected_label_does_not_enter_model_state(self):
        code, result, client = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(set(client.system_one.call_args.kwargs["state"]), {"source", "claim"})
        self.assertEqual(result["summary"]["matches_expected"], 1)

    def test_api_failure_is_not_success(self):
        code, result, _ = self.invoke(error=RuntimeError("deliberate test failure"))
        self.assertEqual(code, 1)
        self.assertEqual(result["summary"]["invalid"], 1)
        self.assertEqual(result["results"][0]["error_type"], "RuntimeError")

    def test_malformed_distribution_is_not_success(self):
        code, result, _ = self.invoke(probabilities={"supports": float("nan"), "contradicts": 0.0, "says_nothing": 0.0})
        self.assertEqual(code, 1)
        self.assertEqual(result["summary"]["invalid"], 1)

    def test_uncertain_result_requires_review(self):
        code, result, _ = self.invoke(confidence=0.5)
        self.assertEqual(code, 1)
        self.assertEqual(result["summary"]["review"], 1)


if __name__ == "__main__":
    unittest.main()
