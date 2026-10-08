"""Public contract checks for the strict behavioral oracle runner."""
import configparser
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from headless_oracle import (build_settings, make_sandbox_profile,
                             validate_observation, validate_probe_files,
                             verify_qt_inputs, validate_timeout, _kill_group)
from evidence_common import Invalid, identity


class HeadlessOracleProfile(unittest.TestCase):
    def test_timeout_is_bounded(self):
        validate_timeout(1)
        validate_timeout(60)
        for timeout in (0, 61, -1):
            with self.assertRaisesRegex(Invalid, "timeout must be within 1..60"):
                validate_timeout(timeout)

    def test_owned_process_group_is_terminated_and_verified(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                   start_new_session=True)
        result = _kill_group(process, grace=1)
        self.assertEqual(result["returncode"], -15)
        self.assertFalse(result["forced_kill"])
        self.assertFalse(result["process_group_remaining"])

    def test_cli_requires_independent_sources_and_environment_build_evidence(self):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("headless_oracle.py")),
                                 "--help"], capture_output=True, text=True, check=True)
        for flag in ("--probe-source", "--linker-script", "--probe-build-log",
                     "--desktop-observer-source", "--qt-source-archive",
                     "--qt-source-dir", "--qt-build-command", "--qt-preparation-record",
                     "--timeout", "--output"):
            self.assertIn(flag, result.stdout)

    def test_qt_source_and_environment_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_dir = root / "src"
            source_dir.mkdir()
            files = [root / "archive", root / "command", root / "preparation"]
            for path in files:
                path.write_bytes(path.name.encode())
            for name in ("main.cpp", "qoffscreencommon.cpp",
                         "qoffscreenintegration.cpp", "qoffscreenwindow.cpp"):
                (source_dir / name).write_bytes(name.encode())
            with patch("headless_oracle.QT_ARCHIVE_SHA256", identity(files[0])["sha256"]), \
                 patch("headless_oracle.QT_BUILD_COMMAND_SHA256", identity(files[1])["sha256"]), \
                 patch("headless_oracle.QT_PREPARATION_SHA256", identity(files[2])["sha256"]), \
                 patch("headless_oracle.QT_SOURCE_HASHES", {
                     name: identity(source_dir / name)["sha256"]
                     for name in ("main.cpp", "qoffscreencommon.cpp",
                                  "qoffscreenintegration.cpp", "qoffscreenwindow.cpp")
                 }):
                record = verify_qt_inputs(*files[:1], source_dir, *files[1:])
                self.assertEqual(set(record["qt_offscreen_sources"]),
                                 {"main.cpp", "qoffscreencommon.cpp",
                                  "qoffscreenintegration.cpp", "qoffscreenwindow.cpp"})
                (source_dir / "qoffscreenwindow.cpp").write_bytes(b"changed")
                with self.assertRaisesRegex(Invalid, "qoffscreenwindow.cpp"):
                    verify_qt_inputs(*files[:1], source_dir, *files[1:])

    def test_profile_forces_offscreen_null_outputs_and_isolated_preferences(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            bios = root / "bios.bin"
            bios.write_bytes(b"test firmware identity")
            settings = build_settings(home, bios, 28031)
            parsed = configparser.ConfigParser(interpolation=None)
            parsed.optionxform = str
            parsed.read(settings)
            self.assertEqual(parsed["UI"]["StartFullscreen"], "false")
            self.assertEqual(parsed["UI"]["SetupWizardIncomplete"], "false")
            self.assertEqual(parsed["Debugger/UserInterface"]["ShowOnStartup"], "false")
            self.assertEqual(parsed["Logging"]["EnableLogWindow"], "false")
            self.assertEqual(parsed["EmuCore/GS"]["Renderer"], "11")
            self.assertEqual(parsed["SPU2/Output"]["Backend"], "Null")
            self.assertEqual(parsed["EmuCore"]["EnablePINE"], "true")
            self.assertEqual(parsed["EmuCore"]["EnablePatches"], "false")
            self.assertEqual(parsed["EmuCore"]["EnableCheats"], "false")
            self.assertEqual(parsed["Folders"]["Bios"], str(bios.parent.resolve()))
            self.assertEqual(parsed["Filenames"]["BIOS"], bios.name)
            self.assertIn("Renderer = 11", settings.read_text())
            self.assertIn("PINESlot = 28031", settings.read_text())
            self.assertFalse((Path.home() / "Library/Application Support/PCSX2").resolve()
                             == settings.parent.resolve())

    def test_sandbox_denies_mach_lookup_ip_network_and_allows_only_pine_unix_socket(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = make_sandbox_profile(root, 28031)
            self.assertIn("(deny mach-lookup)", profile)
            self.assertIn("(deny network*)", profile)
            self.assertIn("(allow network-inbound (local unix-socket", profile)
            self.assertIn("(allow network-outbound (local unix-socket", profile)
            self.assertIn("pcsx2.sock.28031", profile)
            self.assertIn(f'(allow file-write* (subpath "{root.resolve()}")', profile)
            if sys.platform == "darwin":
                profile_path = root / "profile.sb"
                profile_path.write_text(profile)
                socket_path = root / "tmp" / "pcsx2.sock.28031"
                socket_path.parent.mkdir()
                server = root / "server.py"
                server.write_text(
                    "import socket\n"
                    f"s=socket.socket(socket.AF_UNIX); s.bind({str(socket_path)!r}); s.listen(1)\n"
                    "try:\n"
                    "  ip=socket.socket(); ip.bind(('127.0.0.1', 0)); print('ip-allowed')\n"
                    "except OSError:\n"
                    "  print('ip-denied')\n"
                    "c,_=s.accept(); c.recv(4); c.sendall(b'pong'); c.close(); s.close()\n"
                )
                process = subprocess.Popen(["/usr/bin/sandbox-exec", "-f", str(profile_path),
                                             sys.executable, str(server)],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    for _ in range(100):
                        if socket_path.exists():
                            break
                        if process.poll() is not None:
                            self.fail(process.stderr.read())
                        time.sleep(0.01)
                    client = socket.socket(socket.AF_UNIX)
                    client.connect(str(socket_path))
                    client.sendall(b"ping")
                    self.assertEqual(client.recv(4), b"pong")
                    client.close()
                    stdout, stderr = process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 0, stderr)
                    self.assertEqual(stdout.strip(), "ip-denied")
                finally:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=2)

    def test_changed_output_is_a_behavioral_failure_and_focus_variation_is_incomplete(self):
        expected = [0x46523250, 21, 0x10DF30BF, 1]
        good_desktop = {"frontmost_pids": [123, 123], "owned_window_counts": [0, 0]}
        self.assertEqual(validate_observation(expected, good_desktop)["status"], "pass")
        changed = [*expected]
        changed[2] ^= 1
        self.assertEqual(validate_observation(changed, good_desktop)["status"], "fail")
        focus_changed = {"frontmost_pids": [123, 456], "owned_window_counts": [0, 0]}
        self.assertEqual(validate_observation(expected, focus_changed)["status"], "incomplete")
        with_window = {"frontmost_pids": [123, 123], "owned_window_counts": [0, 1]}
        self.assertEqual(validate_observation(expected, with_window)["status"], "fail")

    def test_probe_source_or_elf_mutation_is_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            elf, source, linker = (root / name for name in ("probe.elf", "probe.c", "probe.ld"))
            elf.write_bytes(b"controlled elf")
            source.write_bytes(b"controlled source")
            linker.write_bytes(b"controlled linker")
            recipe = {key: identity(path) for key, path in
                      (("probe_elf", elf), ("probe_source", source), ("linker_script", linker))}
            result = validate_probe_files(elf, source, linker, recipe)
            self.assertEqual(result["probe_elf"]["sha256"], recipe["probe_elf"]["sha256"])
            source.write_bytes(b"mutated source")
            with self.assertRaisesRegex(Invalid, "probe_source differs"):
                validate_probe_files(elf, source, linker, recipe)


if __name__ == "__main__":
    unittest.main()
