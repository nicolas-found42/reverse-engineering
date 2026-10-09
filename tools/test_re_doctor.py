"""Controls for synthetic doctor failures, RPC framing and truthful status observations."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error

import re_doctor
import re_mcp
from re_rpc import Rpc


class DoctorTests(unittest.TestCase):
    def test_success_response_with_error_body_is_rejected(self):
        class Session:
            def tool(self, *args):
                return {'isError': False}, '{"error":"missing program"}'
        with self.assertRaisesRegex(RuntimeError, 'rejected'):
            re_doctor.call(Session(), 'load_program', {})

    def test_disabled_script_control_cannot_pass_on_a_compile_error(self):
        class Session:
            def tool(self, *args):
                return {'isError': True}, 'Java compile failed'
        with self.assertRaisesRegex(RuntimeError, 'did not reject'):
            re_doctor.rejected(Session(), 'run_script_inline', {}, 'script execution disabled')

    def test_healthy_status_does_not_invent_verified_script_policy(self):
        settings = {'url': 'http://127.0.0.1:8090', 'ghidra': '/ghidra', 'file_root': '/inputs'}
        def request(path, *, authenticated=True):
            if not authenticated:
                raise urllib.error.HTTPError(settings['url'], 401, '', {}, None)
            return b'{}'
        with patch.object(re_mcp, 'config', return_value=settings), patch.object(re_mcp, 'health', return_value=True), \
                patch.object(re_mcp, 'validate_runtime'), patch.object(re_mcp, 'request', side_effect=request):
            report = re_mcp.status()
        self.assertTrue(all(report['observed'].values()))
        self.assertNotIn('scripts_allowed', report['observed'])
        self.assertIn('not probed', report['behavioral_controls'])

    def test_unavailable_backend_has_failed_observations(self):
        settings = {'url': 'http://127.0.0.1:8090', 'ghidra': '/ghidra', 'file_root': '/inputs'}
        with patch.object(re_mcp, 'config', return_value=settings), patch.object(re_mcp, 'health', return_value=False), \
                patch.object(re_mcp, 'validate_runtime'), patch.object(re_mcp, 'request', side_effect=OSError):
            self.assertFalse(all(re_mcp.status()['observed'].values()))

    def test_rpc_reads_real_newline_frames(self):
        script = "import sys,json\nfor line in sys.stdin:\n m=json.loads(line)\n if 'id' in m: print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':{'ok':True}}),flush=True)\n"
        with tempfile.TemporaryDirectory() as directory:
            with Rpc([sys.executable, '-u', '-c', script], Path(directory) / 'stderr.log', timeout=3) as rpc:
                self.assertEqual(rpc.call('probe', {}), {'ok': True})

    def test_malformed_rpc_stream_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with Rpc([sys.executable, '-u', '-c', "print('invalid JSON',flush=True); input()"],
                     Path(directory) / 'stderr.log', timeout=3) as rpc:
                with self.assertRaisesRegex(RuntimeError, 'Invalid RPC'):
                    rpc.call('probe', {})


if __name__ == '__main__':
    unittest.main()
