"""Controls for pinned distributions, unsafe archives and activation rollback."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile
import subprocess

import re_bootstrap


class BootstrapTests(unittest.TestCase):
    def test_make_install_cannot_fall_back_to_a_system_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            build = re_bootstrap.Build(Path(directory), Path('/jdk'))
            with self.assertRaisesRegex(ValueError, 'candidate prefix'):
                build.run(['make', 'install'])
            with self.assertRaisesRegex(ValueError, 'candidate prefix'):
                build.run(['make', 'PREFIX=/usr/local', 'install'])

    def test_cache_hash_is_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / 'cache'
            cache.mkdir()
            (cache / 'asset').write_bytes(b'fixture')
            destination = root / 'install'
            destination.mkdir()
            asset = {'file': 'asset', 'url': 'https://invalid.example',
                     'sha256': hashlib.sha256(b'fixture').hexdigest()}
            re_bootstrap.fetch(asset, destination, cache)
            (destination / 'asset').write_bytes(b'replaced')
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                re_bootstrap.fetch(asset, destination, cache)

    def test_archive_traversal_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'fixture.zip'
            with zipfile.ZipFile(archive, 'w') as stream:
                stream.writestr('../escape', 'fixture')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                re_bootstrap.unpack(archive, root / 'install')
            self.assertFalse((root / 'escape').exists())

    def test_activation_failure_restores_private_config(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_bootstrap, 'ROOT', Path(directory)):
            config = Path(directory) / '.scratch/re-setup/config.json'
            re_bootstrap.private_json(config, {'original': True})
            with patch('re_bootstrap.wrappers', return_value={}), patch('re_bootstrap.re_mcp.validate_runtime'), \
                    patch('re_bootstrap.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'fixture')):
                with self.assertRaises(subprocess.CalledProcessError):
                    re_bootstrap.activate({'candidate': True})
            self.assertEqual(json.loads(config.read_text()), {'original': True})
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_wrapper_ownership_is_checked_before_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'r2').write_text('unrelated user command')
            with self.assertRaisesRegex(ValueError, 'unrelated'):
                re_bootstrap.wrappers(root)
            self.assertEqual((root / 'r2').read_text(), 'unrelated user command')

    def test_activation_keeps_running_analysis_untouched(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(re_bootstrap, 'ROOT', Path(directory)):
            config = Path(directory) / '.scratch/re-setup/config.json'
            re_bootstrap.private_json(config, {'original': True})
            config.with_name('backend.pid').write_text('fixture')
            with self.assertRaisesRegex(ValueError, 'interrupt'):
                re_bootstrap.activate({'candidate': True})
            self.assertEqual(json.loads(config.read_text()), {'original': True})

    def test_manifest_preserves_recorded_source_pins(self):
        manifest = json.loads(re_bootstrap.MANIFEST.read_text())
        receipt = json.loads((re_bootstrap.ROOT / manifest['provenance']).read_text())
        for name, key in [('ghidra-mcp', 'ghidra_mcp'), ('ccc', 'ccc'), ('radare2', 'radare2'), ('radare2-mcp', 'r2mcp')]:
            self.assertEqual(manifest['sources'][name]['commit'], receipt['source_commits'][key])


if __name__ == '__main__':
    unittest.main()
