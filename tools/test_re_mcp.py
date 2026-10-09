"""Controls for private token handling and enforced backend environment defaults."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import re_mcp


class ReMcpTests(unittest.TestCase):
    def test_token_permissions_and_missing_inputs(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_mcp, 'LOCAL', Path(directory)):
            path = Path(directory) / 'ghidra-token'
            with self.assertRaises(FileNotFoundError):
                re_mcp.token()
            path.write_text('synthetic-test-token-' + 'x' * 32)
            path.chmod(0o644)
            with self.assertRaisesRegex(RuntimeError, 'private'):
                re_mcp.token()
            path.chmod(0o600)
            self.assertEqual(re_mcp.token(), 'synthetic-test-token-' + 'x' * 32)

    def test_ambient_script_enable_cannot_override_launcher(self):
        settings = {'java_home': '/jdk', 'ghidra': '/ghidra', 'file_root': '/inputs',
                    'url': 'http://127.0.0.1:8090'}
        with patch.object(re_mcp, 'token', return_value='synthetic'), patch.dict('os.environ', {'GHIDRA_MCP_ALLOW_SCRIPTS': '1'}):
            env = re_mcp.backend_env(settings)
            self.assertEqual(env['GHIDRA_MCP_ALLOW_SCRIPTS'], '0')
            self.assertEqual(env['GHIDRA_MCP_REQUIRE_PROGRAM_SELECTORS'], '1')
            self.assertEqual(env['GHIDRA_MCP_AUTH_TOKEN'], 'synthetic')
            self.assertEqual(env['GHIDRA_MCP_FILE_ROOT'], '/inputs')

    def test_isolated_settings_override_ambient_user_extensions(self):
        settings = {'java_home': '/jdk', 'ghidra': '/ghidra', 'file_root': '/inputs',
                    'url': 'http://127.0.0.1:8090', 'settings_dir': '/candidate settings'}
        with patch.object(re_mcp, 'token', return_value='synthetic'):
            self.assertEqual(re_mcp.backend_env(settings)['XDG_CONFIG_HOME'], '/candidate settings')

    def test_scoped_runtime_identity(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            jar = Path(directory) / 'runtime.jar'
            jar.write_bytes(b'synthetic reviewed extension')
            settings = {'extension_jar': str(jar), 'extension_sha256': hashlib.sha256(jar.read_bytes()).hexdigest()}
            re_mcp.validate_runtime(settings)
            jar.write_bytes(b'unreviewed replacement')
            with self.assertRaisesRegex(RuntimeError, 'identity changed'):
                re_mcp.validate_runtime(settings)
            jar.unlink()
            with self.assertRaisesRegex(RuntimeError, 'identity changed'):
                re_mcp.validate_runtime(settings)
        with self.assertRaisesRegex(RuntimeError, 'identity is missing'):
            re_mcp.validate_runtime({})

    def test_existing_unauthenticated_backend_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_mcp, 'LOCAL', Path(directory)):
            (Path(directory) / 'config.json').write_text(json.dumps({}))
            with patch.object(re_mcp, 'validate_runtime'), patch.object(re_mcp, 'health', return_value=True), patch.object(re_mcp, 'request', return_value=b'{}'):
                with self.assertRaisesRegex(RuntimeError, 'does not enforce'):
                    re_mcp.start()

    def test_dead_owned_pid_is_cleaned_without_signalling(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_mcp, 'LOCAL', Path(directory)):
            pid = Path(directory) / 'backend.pid'
            pid.write_text('12345')
            gone = subprocess.CompletedProcess([], 1, stdout='', stderr='')
            with patch('re_mcp.subprocess.run', return_value=gone), patch('re_mcp.os.killpg') as signal:
                re_mcp.stop()
            self.assertFalse(pid.exists())
            signal.assert_not_called()

    def test_unrelated_pid_is_not_signalled(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_mcp, 'LOCAL', Path(directory)):
            (Path(directory) / 'backend.pid').write_text('12345')
            unrelated = subprocess.CompletedProcess([], 0, stdout='unrelated user service', stderr='')
            with patch('re_mcp.subprocess.run', return_value=unrelated), patch('re_mcp.os.killpg') as signal:
                with self.assertRaisesRegex(RuntimeError, 'does not identify'):
                    re_mcp.stop()
            signal.assert_not_called()


if __name__ == '__main__':
    unittest.main()
