import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from compiler_probe_recipe.packages import bind_packages
from evidence_common import Incomplete


class PackageBindingTests(unittest.TestCase):
    def test_installed_components_are_bound_to_archive_members(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            driver = root / 'candidates/fixture/bin/ee-gcc'
            driver.parent.mkdir(parents=True)
            driver.write_bytes(b'public synthetic driver')
            archive = root / 'fixture.tar.gz'
            with tarfile.open(archive, 'w:gz') as package:
                info = tarfile.TarInfo('bin/ee-gcc')
                info.size = driver.stat().st_size
                package.addfile(info, io.BytesIO(driver.read_bytes()))
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            manifest = {'candidates': [{'id': 'fixture', 'compiler_executable': str(driver)}]}
            with patch('compiler_probe_recipe.packages.DISTRIBUTIONS', {'fixture': (archive.name, digest)}):
                rows = bind_packages(manifest, root)
                self.assertEqual(rows[0]['members']['driver']['member'], 'bin/ee-gcc')
                self.assertEqual(rows[0]['members']['driver']['sha256'],
                                 hashlib.sha256(b'public synthetic driver').hexdigest())
                driver.write_bytes(b'replacement')
                with self.assertRaisesRegex(Incomplete, 'installed candidate differs'):
                    bind_packages(manifest, root)
                archive.unlink()
                with self.assertRaisesRegex(Incomplete, 'archive is missing or changed'):
                    bind_packages(manifest, root)
