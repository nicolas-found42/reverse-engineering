"""Public source-record controls; inventories cannot qualify guest execution."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import tarfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from evidence_common import Incomplete, Invalid
from oracle_dependency_sources import check, verify_source_records


class OracleSourceRecords(unittest.TestCase):
    # SHA1 of the literal b'abc', independently known from the SHA1 test vector.
    RECORD = b"FileName: ./source.c\nFileChecksum: SHA1: a9993e364706816aba3e25717850c26c9cd0d89d\n"

    def test_positive_record_comparison_has_zero_byte_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.c").write_bytes(b"abc")
            result = verify_source_records(self.RECORD, root)
        self.assertEqual(result["checked_files"], 1)
        self.assertEqual(result["matched_bytes"], 0)

    def test_changed_source_fails_even_with_another_file_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.c").write_bytes(b"changed")
            records = self.RECORD + self.RECORD.replace(b"source.c", b"missing.c")
            with self.assertRaises(Invalid) as caught:
                verify_source_records(records, root)
        self.assertEqual(caught.exception.details["missing"], ["missing.c"])
        self.assertEqual(caught.exception.details["changed"][0]["path"], "source.c")

    def test_missing_source_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Incomplete):
                verify_source_records(self.RECORD, Path(directory))

    def test_empty_duplicate_malformed_and_escaping_records_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            for records in (
                b"",
                self.RECORD * 2,
                self.RECORD.replace(
                    b"a9993e364706816aba3e25717850c26c9cd0d89d", b"wrong"
                ),
                self.RECORD.replace(b"./source.c", b"../source.c"),
            ):
                with self.subTest(records=records), self.assertRaises(Invalid):
                    verify_source_records(records, Path(directory))

    def test_available_changed_installed_executable_outranks_missing_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "app/Contents/MacOS/PCSX2"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"changed PCSX2")
            with self.assertRaises(Invalid) as caught:
                check(root / "evidence", root / "sdk", root / "sdk.7z", root / "app")
        self.assertIn(str(executable), caught.exception.details["changed"])

    def test_admitted_source_contradiction_outranks_other_missing_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = root / "sdk/sbom/qtbase-6.10.1.source.spdx"
            record.parent.mkdir(parents=True)
            record.write_bytes(self.RECORD)
            source = root / "evidence/qtbase-git/source.c"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"changed")
            with patch(
                "oracle_dependency_sources.SOURCE_RECORD_SHA256",
                hashlib.sha256(self.RECORD).hexdigest(),
            ):
                with self.assertRaises(Invalid) as caught:
                    check(
                        root / "evidence", root / "sdk", root / "sdk.7z", root / "app"
                    )
        self.assertEqual(
            caught.exception.details["sdk_source_inventory"]["changed"][0]["path"],
            "source.c",
        )
        self.assertTrue(caught.exception.details["missing"])

    def test_closure_source_gap_is_incomplete_and_changed_source_fails(self):
        import oracle_dependency_sources as sources

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_dir = root / "archives"
            archive_dir.mkdir()
            manifest = {
                "components": {
                    "qtbase": {
                        "archive": "qtbase.tar.xz",
                        "version": "6.10.1",
                        "provides": ["libQt6Core.6.dylib"],
                        "licenses": [{"path": "LICENSES/LGPL-3.0-only.txt"}],
                    },
                    "missing": {
                        "archive": "absent.tar.xz",
                        "version": "0",
                        "provides": ["libAbsent.1.dylib"],
                        "licenses": [{"path": "LICENSE"}],
                    },
                }
            }
            (archive_dir / "qtbase.tar.xz").write_bytes(b"qtbase source bytes")
            with patch.object(
                sources,
                "DEPENDENCY_PINS",
                {
                    "shasums": {
                        "qtbase.tar.xz": hashlib.sha256(
                            b"qtbase source bytes"
                        ).hexdigest(),
                        "absent.tar.xz": "0" * 64,
                    }
                },
            ):
                with self.assertRaises(Incomplete) as caught:
                    sources.verify_closure_sources(manifest, archive_dir)
            self.assertIn("absent.tar.xz", str(caught.exception))
            (archive_dir / "absent.tar.xz").write_bytes(b"wrong bytes")
            with patch.object(
                sources,
                "DEPENDENCY_PINS",
                {
                    "shasums": {
                        "qtbase.tar.xz": hashlib.sha256(
                            b"qtbase source bytes"
                        ).hexdigest(),
                        "absent.tar.xz": "0" * 64,
                    }
                },
            ):
                with self.assertRaises(Invalid):
                    sources.verify_closure_sources(manifest, archive_dir)

    def test_closure_license_gap_is_incomplete_and_changed_notice_fails(self):
        import oracle_dependency_sources as sources

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "components": {
                    "qtbase": {
                        "archive": "qtbase.tar.xz",
                        "provides": ["libQt6Core.6.dylib"],
                        "licenses": [
                            {
                                "path": "LICENSES/LGPL-3.0-only.txt",
                                "sha256": hashlib.sha256(b"lgpl text").hexdigest(),
                            }
                        ],
                    },
                    "gap": {
                        "archive": "gap.tar.xz",
                        "provides": ["libGap.1.dylib"],
                        "licenses": [{"path": "LICENSE"}],
                    },
                }
            }
            source_root = root / "sources"
            (source_root / "qtbase.tar.xz" / "qtbase-6.10.1" / "LICENSES").mkdir(
                parents=True
            )
            (
                source_root
                / "qtbase.tar.xz"
                / "qtbase-6.10.1"
                / "LICENSES"
                / "LGPL-3.0-only.txt"
            ).write_bytes(b"lgpl text")
            with self.assertRaises(Incomplete) as caught:
                sources.verify_closure_licenses(manifest, source_root)
            self.assertIn("gap", str(caught.exception))
            (source_root / "gap.tar.xz" / "gap-0").mkdir(parents=True)
            (source_root / "gap.tar.xz" / "gap-0" / "LICENSE").write_bytes(
                b"changed notice"
            )
            with patch.object(sources, "DEPENDENCY_PINS", {"shasums": {}}):
                with self.assertRaises(Invalid):
                    sources.verify_closure_licenses(
                        {
                            "components": {
                                "gap": {
                                    "archive": "gap.tar.xz",
                                    "provides": ["libGap.1.dylib"],
                                    "licenses": [
                                        {"path": "LICENSE", "sha256": "0" * 64}
                                    ],
                                }
                            }
                        },
                        source_root,
                    )

    def test_missing_closure_branch_keeps_check_incomplete(self):
        import oracle_dependency_sources as sources

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archives = root / "archives"
            archives.mkdir()
            present = "KDDockWidgets-2.4.0.tar.gz"
            (archives / present).write_bytes(b"admitted")
            pins = {
                "shasums": {
                    **sources.DEPENDENCY_PINS["shasums"],
                    present: hashlib.sha256(b"admitted").hexdigest(),
                }
            }
            with patch.object(sources, "DEPENDENCY_PINS", pins):
                with self.assertRaises(Incomplete) as caught:
                    check(
                        root / "evidence",
                        root / "sdk",
                        root / "sdk.7z",
                        root / "app",
                        archives=archives,
                        sources=root / "sources",
                    )
            self.assertIn("closure_source_inventory", caught.exception.details)

    def test_extracted_notice_directory_still_runs_notice_inventory(self):
        import oracle_dependency_sources as sources

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archives = root / "archives"
            archives.mkdir()
            present = "KDDockWidgets-2.4.0.tar.gz"
            (archives / present).write_bytes(b"admitted")
            pins = {
                "shasums": {
                    **sources.DEPENDENCY_PINS["shasums"],
                    present: hashlib.sha256(b"admitted").hexdigest(),
                }
            }
            source_root = root / "sources"
            (
                source_root / "qtbase-everywhere-src-6.10.1.tar.xz" / "qtbase-6.10.1"
            ).mkdir(parents=True)
            with patch.object(sources, "DEPENDENCY_PINS", pins):
                with self.assertRaises(Incomplete) as caught:
                    check(
                        root / "evidence",
                        root / "sdk",
                        root / "sdk.7z",
                        root / "app",
                        archives=archives,
                        sources=source_root,
                    )
            self.assertIn("closure_notice_inventory", caught.exception.details)

    def test_changed_non_qt_notice_outranks_absent_qt_source_directory(self):
        import oracle_dependency_sources as sources

        manifest = json.loads(sources.DEPENDENCY_MANIFEST.read_text())
        component = manifest["components"]["ffmpeg"]
        notice = component["licenses"][0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "sources"
            changed = (
                source_root / component["archive"] / "ffmpeg-version" / notice["path"]
            )
            changed.parent.mkdir(parents=True)
            changed.write_bytes(b"changed known notice")
            with self.assertRaises(Invalid) as caught:
                check(
                    root / "evidence",
                    root / "sdk",
                    root / "sdk.7z",
                    root / "app",
                    sources=source_root,
                )
            self.assertIn("closure_notice_inventory", caught.exception.details)
            self.assertTrue(caught.exception.details["missing"])
            self.assertTrue(
                caught.exception.details["closure_notice_inventory"]["changed"]
            )

    def test_absent_notice_root_is_incomplete_with_other_inputs_valid(self):
        import oracle_dependency_sources as sources

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence, sdk = root / "evidence", root / "sdk"
            evidence.mkdir()
            (sdk / "sbom").mkdir(parents=True)
            release = evidence / "pcsx2-v2.6.3-macos-Qt.tar.xz"
            with tarfile.open(release, "w:xz"):
                pass
            (sdk / sources.SOURCE_RECORD).write_bytes(self.RECORD)
            (evidence / "qtbase-git").mkdir()
            (evidence / "qtbase-git/source.c").write_bytes(b"abc")
            sdk_archive = root / "sdk.7z"
            sdk_archive.write_bytes(b"abc")
            (evidence / "component.tar.xz").write_bytes(b"abc")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "components": {
                            "component": {
                                "archive": "component.tar.xz",
                                "licenses": [
                                    {
                                        "path": "LICENSE",
                                        "sha256": hashlib.sha256(b"notice").hexdigest(),
                                    }
                                ],
                            }
                        }
                    }
                )
            )
            replacements = {
                "DEPENDENCY_MANIFEST": manifest,
                "ARCHIVES": {
                    release.name: hashlib.sha256(release.read_bytes()).hexdigest()
                },
                "RELEASE_MEMBERS": {},
                "SOURCE_RECORD_SHA256": hashlib.sha256(self.RECORD).hexdigest(),
                "QT_SDK_ARCHIVE_SHA256": hashlib.sha256(b"abc").hexdigest(),
                "DEPENDENCY_PINS": {
                    "shasums": {
                        "component.tar.xz": hashlib.sha256(b"abc").hexdigest()
                    }
                },
            }
            notice_root = root / "sources"
            with ExitStack() as stack:
                for name, value in replacements.items():
                    stack.enter_context(patch.object(sources, name, value))
                with self.assertRaises(Incomplete) as caught:
                    check(evidence, sdk, sdk_archive, root / "app", sources=notice_root)
                self.assertEqual(caught.exception.details["changed"], [])
                self.assertIn("closure_notice_inventory", caught.exception.details)
                self.assertEqual(
                    caught.exception.details["closure_notice_inventory"]["missing"],
                    ["component: extracted source is absent"],
                )
                # Supplying exactly the missing notice completes the bounded
                # inventory, while issue #22 itself remains incomplete.
                notice = notice_root / "component.tar.xz/component/LICENSE"
                notice.parent.mkdir(parents=True)
                notice.write_bytes(b"notice")
                result = check(
                    evidence, sdk, sdk_archive, root / "app", sources=notice_root
                )
                self.assertEqual(result["missing"], [])
                self.assertEqual(result["issue22_status"], "incomplete")
                self.assertIn("closure_notice_inventory", result)

    def test_public_cli_negative_and_incomplete_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "app"
            command = [
                sys.executable,
                str(Path(__file__).with_name("oracle_dependency_sources.py")),
                str(root / "evidence"),
                str(root / "sdk"),
                str(root / "sdk.7z"),
                "--app",
                str(app),
                "--output",
                str(root / "receipts"),
            ]
            run = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            missing_receipt = Path(json.loads(run.stdout)["result"])
            retained = missing_receipt.read_bytes()
            executable = app / "Contents/MacOS/PCSX2"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"changed PCSX2")
            run = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
            result = json.loads(Path(json.loads(run.stdout)["result"]).read_text())
            self.assertIn(str(executable), result["details"]["changed"])
            self.assertTrue(result["details"]["missing"])
            self.assertEqual(missing_receipt.read_bytes(), retained)


if __name__ == "__main__":
    unittest.main()
