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
from types import SimpleNamespace
from unittest.mock import MagicMock
import headless_oracle as oracle
from unittest.mock import patch

from headless_oracle import (build_settings, make_sandbox_profile,
                             validate_observation, validate_probe_files,
                             verify_qt_inputs, validate_timeout, _kill_group,
                             read_probe_output, wait_for_probe_output,
                             cleanup_failure, ac25_acceptance)
from evidence_common import Incomplete, Invalid, identity


class HeadlessOracleProfile(unittest.TestCase):
    def test_post_shutdown_or_untimed_desktop_samples_cannot_pass(self):
        desktop = {"sample_count": 400, "frontmost_pids": [123] * 400,
                   "owned_window_counts": [0] * 400,
                   "timestamps_ns": [1_000_000_000 + i * 50_000_000 for i in range(400)],
                   "emulator_started_ns": 1_000_000_000, "emulator_stopped_ns": 2_000_000_000}
        self.assertEqual(validate_observation(oracle.EXPECTED_WORDS, desktop)["status"], "incomplete")
        desktop.pop("timestamps_ns")
        self.assertEqual(validate_observation(oracle.EXPECTED_WORDS, desktop)["status"], "incomplete")

    def test_cleanup_failure_after_observation_produces_a_failed_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {name: root / name for name in (
                "emulator", "platform_plugin", "elf", "probe_source", "linker_script",
                "probe_build_log", "bios", "desktop_observer", "desktop_observer_source",
                "qt_sdk_archive", "qt_source_dir", "qt_build_command", "qt_preparation_record")}
            args = SimpleNamespace(**paths, timeout=1, sandbox_exec=Path("/usr/bin/sandbox-exec"))
            process = MagicMock(pid=123, returncode=None)
            process.poll.return_value = None
            observed = {"words": oracle.EXPECTED_WORDS}
            with patch.object(oracle.sys, "platform", "darwin"), \
                 patch.object(oracle, "verify_inputs", return_value={}), \
                 patch.object(oracle.subprocess, "Popen", return_value=process), \
                 patch.object(oracle, "_kill_group", return_value={"process_group_remaining": True}), \
                 patch.object(oracle, "Pine") as pine, \
                 patch.object(oracle, "wait_for_probe_output", return_value=observed), \
                 patch.object(oracle.Path, "exists", return_value=True):
                result = oracle.execute(args, root)
            self.assertEqual(result["status"], "fail")
            self.assertIn("owned process group survived cleanup", result["failures"])
            self.assertEqual(result["pine"], observed)

    def test_pine_reads_are_bounded_by_remaining_deadline(self):
        class FakeSocket:
            def __init__(self):
                self.timeouts = []

            def settimeout(self, timeout):
                self.timeouts.append(timeout)

        class FakePine:
            def __init__(self):
                self.socket = FakeSocket()
                self.reads = []

            def status(self):
                return 1

            def read(self, address, length):
                self.reads.append((address, length))
                return (0x46523250 if len(self.reads) == 1 else 21 if len(self.reads) == 2
                        else 0x10DF30BF if len(self.reads) == 3 else 1).to_bytes(4, "little")

        pine = FakePine()
        result = read_probe_output(pine, time.monotonic() + 2)
        self.assertEqual(result["words"], [0x46523250, 21, 0x10DF30BF, 1])
        self.assertEqual(len(pine.socket.timeouts), 5)
        with self.assertRaisesRegex(TimeoutError, "deadline expired"):
            read_probe_output(pine, time.monotonic() - 1)

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

    def test_cleanup_signals_descendants_after_the_group_leader_exits(self):
        child_code = (
            "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
            "print('ready',flush=True); time.sleep(30)"
        )
        parent_code = (
            "import subprocess,sys,time; "
            f"p=subprocess.Popen([sys.executable,'-c',{child_code!r}],stdout=subprocess.PIPE,text=True); "
            "p.stdout.readline(); print(p.pid,flush=True); time.sleep(30)"
        )
        process = subprocess.Popen([sys.executable, "-c", parent_code],
                                   stdout=subprocess.PIPE, text=True,
                                   start_new_session=True)
        child_pid = int(process.stdout.readline())
        result = _kill_group(process, grace=0.2)
        process.stdout.close()
        self.assertEqual(result["returncode"], -15)
        self.assertTrue(result["forced_kill"])
        self.assertFalse(result["process_group_remaining"])
        absent = False
        for _ in range(20):
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                absent = True
                break
            time.sleep(0.05)
        self.assertTrue(absent, "SIGKILLed descendant should be reaped")

    def test_surviving_group_is_a_failure_even_without_probe_output(self):
        self.assertEqual(cleanup_failure({"process_group_remaining": True}),
                         "owned process group survived cleanup")
        self.assertIsNone(cleanup_failure({"process_group_remaining": False}))
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                   start_new_session=True)
        with patch("headless_oracle._group_exists", return_value=True):
            lifecycle = _kill_group(process, grace=0.01)
        self.assertTrue(lifecycle["process_group_remaining"])
        self.assertEqual(cleanup_failure(lifecycle), "owned process group survived cleanup")

    def test_pine_output_waits_for_completion_sentinel(self):
        class FakeSocket:
            def settimeout(self, timeout):
                self.timeout = timeout

        class FakePine:
            def __init__(self):
                self.socket = FakeSocket()
                self.reads = 0

            def read(self, address, length):
                self.reads += 1
                if address == 0x00180000 + 12:
                    return (0 if self.reads == 1 else 1).to_bytes(4, "little")
                return {0x00180000: 0x46523250, 0x00180004: 21,
                        0x00180008: 0x10DF30BF, 0x0018000C: 1}[address].to_bytes(4, "little")

            def status(self):
                return 1

        class LiveProcess:
            def poll(self):
                return None

        pine = FakePine()
        result = wait_for_probe_output(pine, LiveProcess(), time.monotonic() + 1)
        self.assertEqual(result["words"], [0x46523250, 21, 0x10DF30BF, 1])
        self.assertGreaterEqual(pine.reads, 6)

    def test_dead_process_before_sentinel_retains_incomplete_observation(self):
        class FakePine:
            pass

        class DeadProcess:
            def poll(self):
                return -11

            @property
            def returncode(self):
                return -11

        with self.assertRaisesRegex(Incomplete, "completion sentinel"):
            wait_for_probe_output(FakePine(), DeadProcess(), time.monotonic() + 1)

    def test_cli_requires_independent_sources_and_environment_build_evidence(self):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("headless_oracle.py")),
                                 "--help"], capture_output=True, text=True, check=True)
        for flag in ("--probe-source", "--linker-script", "--probe-build-log",
                     "--desktop-observer-source", "--qt-sdk-archive",
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
            with patch("headless_oracle.QT_SDK_ARCHIVE_SHA256", identity(files[0])["sha256"]), \
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
        good_desktop = {"sample_count": 400, "frontmost_pids": [123] * 400,
                        "owned_window_counts": [0] * 400,
                        "timestamps_ns": [1_000_000_000 + i * 50_000_000 for i in range(400)],
                        "emulator_started_ns": 1_000_000_000, "emulator_stopped_ns": 21_000_000_000}
        raw = validate_observation(expected, good_desktop)
        self.assertEqual(raw["status"], "pass")
        acceptance = ac25_acceptance(raw)
        self.assertEqual(acceptance["status"], "incomplete")
        self.assertIn("Effective audio output", acceptance["blockers"][0])
        self.assertIn("50 ms", acceptance["blockers"][1])
        with self.assertRaises(TypeError):
            ac25_acceptance(raw, True)
        changed = [*expected]
        changed[2] ^= 1
        mismatch = validate_observation(changed, good_desktop)
        self.assertEqual(mismatch["status"], "fail")
        self.assertEqual(ac25_acceptance(mismatch)["status"], "fail")
        focus_changed = {"sample_count": 400, "frontmost_pids": [123, 456] + [456] * 398,
                         "owned_window_counts": [0] * 400,
                        "timestamps_ns": [1_000_000_000 + i * 50_000_000 for i in range(400)],
                        "emulator_started_ns": 1_000_000_000, "emulator_stopped_ns": 21_000_000_000}
        raw_focus = validate_observation(expected, focus_changed)
        self.assertEqual(raw_focus["status"], "incomplete")
        self.assertEqual(ac25_acceptance(raw_focus)["status"], "incomplete")
        with_window = {"sample_count": 400, "frontmost_pids": [123] * 400,
                       "owned_window_counts": [0] * 399 + [1],
                       "timestamps_ns": good_desktop["timestamps_ns"],
                       "emulator_started_ns": 1_000_000_000, "emulator_stopped_ns": 21_000_000_000}
        self.assertEqual(validate_observation(expected, with_window)["status"], "fail")

    def test_short_desktop_sample_is_incomplete_not_a_positive_observation(self):
        raw = validate_observation([0x46523250, 21, 0x10DF30BF, 1], {
            "sample_count": 20, "frontmost_pids": [123] * 20,
            "owned_window_counts": [0] * 20})
        self.assertEqual(raw["status"], "incomplete")
        self.assertEqual(ac25_acceptance(raw)["status"], "incomplete")

    def test_static_completion_rejects_behavior_receipt_import_before_running(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = root / "behavior.json"
            receipt.write_text('{"status":"pass","authority":"executed_behavioral_observation"}')
            output = root / "out"
            process = subprocess.run([
                sys.executable, str(Path(__file__).with_name("completion.py")),
                "not-a-real-corpus", "--output", str(output),
                "--behavioral-receipt", str(receipt)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertIn("unrecognized arguments: --behavioral-receipt", process.stderr)
            self.assertFalse(output.exists())

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
