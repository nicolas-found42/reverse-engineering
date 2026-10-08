import json
from pathlib import Path
import tempfile
import unittest

from compiler_probe import run_probe


class CompilerProbeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "probe.c"
        self.source.write_text("int probe(void) { return 7; }\n")
        self.reference = self.root / "retail-function.bin"
        self.reference.write_bytes(bytes.fromhex("01020304"))
        self.compiler = self.root / "fake-cc"
        self.compiler.write_text("#!/bin/bash\ncp \"$FAKE_OBJECT\" \"${@: -1}\"\n")
        self.compiler.chmod(0o755)
        self.objcopy = self.root / "fake-objcopy"
        self.objcopy.write_text("""#!/usr/bin/env python3
import os, pathlib, sys
target = sys.argv[sys.argv.index('--dump-section') + 1].split('=', 1)[1]
pathlib.Path(target).write_bytes(pathlib.Path(os.environ['FAKE_OBJECT']).read_bytes())
""")
        self.objcopy.chmod(0o755)
        self.object = self.root / "object.bin"
        self.object.write_bytes(bytes.fromhex("01020304"))
        import os
        self.old_env = os.environ.get("FAKE_OBJECT")
        os.environ["FAKE_OBJECT"] = str(self.object)

    def tearDown(self):
        import os
        if self.old_env is None:
            os.environ.pop("FAKE_OBJECT", None)
        else:
            os.environ["FAKE_OBJECT"] = self.old_env
        self.temp.cleanup()

    def manifest(self, candidate="gcc-test"):
        path = self.root / "manifest.json"
        path.write_text(json.dumps({
            "source": str(self.source), "symbol": "probe",
            "reference": str(self.reference),
            "candidates": [{"id": candidate, "compile": [str(self.compiler)],
                            "objcopy": [str(self.objcopy)]}]}))
        return path

    def test_a_candidate_whose_compiled_function_matches_is_selected(self):
        result = run_probe(self.manifest(), self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("pass", "gcc-test"))
        self.assertEqual(result["candidates"][0]["actual_sha256"], result["reference"]["sha256"])

    def test_a_nonmatching_candidate_is_a_failure_not_silently_skipped(self):
        self.object.write_bytes(bytes.fromhex("01020305"))
        result = run_probe(self.manifest(), self.root / "out")
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["failures"], ["gcc-test"])
        self.assertEqual(result["candidates"][0]["gate"]["first_difference"]["offset"], 0)

    def test_unavailable_candidate_is_incomplete_and_cannot_be_selected(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"][0]["compile"] = [str(self.root / "missing-ee-gcc")]
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["incomplete"], ["gcc-test"])

    def test_multiple_matching_candidates_remain_ambiguous(self):
        manifest = self.manifest()
        body = json.loads(manifest.read_text())
        body["candidates"].append({"id": "other-gcc", "compile": [str(self.compiler)],
                                    "objcopy": [str(self.objcopy)]})
        manifest.write_text(json.dumps(body))
        result = run_probe(manifest, self.root / "out")
        self.assertEqual((result["status"], result["selected_id"]), ("incomplete", None))
        self.assertEqual(result["matches"], ["gcc-test", "other-gcc"])


if __name__ == "__main__":
    unittest.main()
