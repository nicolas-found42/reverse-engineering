"""Compile and execute V5 guard controls against a locally installed Ghidra API.

Set GHIDRA_HEADLESS and JAVA_HOME to use another installation. The local ignored
Ghidra and Homebrew JDK are fallbacks; missing dependencies produce an explicit
skip. The Java fixture loads no game artifact or database.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class EeCandidateV5Test(unittest.TestCase):
    def test_real_address_sets_and_flow_types_enforce_the_guard(self):
        headless = os.environ.get('GHIDRA_HEADLESS')
        ghidra = (Path(headless).resolve().parent.parent if headless else
                  ROOT / '.scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC')
        java_home = Path(os.environ.get('JAVA_HOME', '/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home'))
        jars = sorted((ghidra / 'Ghidra').rglob('*.jar'))
        if not jars or not (java_home / 'bin/javac').is_file():
            self.skipTest('requires Ghidra jars and a JDK (GHIDRA_HEADLESS, JAVA_HOME)')
        classpath = os.pathsep.join(map(str, jars))
        source = ROOT / 'tools/ghidra/experimental'
        (ROOT / '.scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='v5-guard-', dir=ROOT / '.scratch') as folder:
            compile_result = subprocess.run([str(java_home / 'bin/javac'), '-cp', classpath, '-d', folder,
                str(source / 'CreateEeCandidateV5.java'), str(source / 'tests/CreateEeCandidateV5GuardTest.java')],
                capture_output=True, text=True, timeout=90)
            self.assertEqual(compile_result.returncode, 0, compile_result.stdout + compile_result.stderr)
            run = subprocess.run([str(java_home / 'bin/java'), '-cp', folder + os.pathsep + classpath,
                'CreateEeCandidateV5GuardTest'], capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn('V5_GUARD_CONTROLS_OK', run.stdout)
            print(run.stdout.strip())
