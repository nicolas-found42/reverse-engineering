#!/usr/bin/env python3
"""Execute one pinned controlled probe in a strict, isolated PCSX2 profile.

This receipt is behavioral evidence only. It is not accepted by any byte or
reconstruction ledger. The runner fixes the emulator command/profile and only
accepts the hand-written probe compiled by the pinned local recipe.
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

from evidence_common import Incomplete, Invalid, identity, write_result
from pcsx2_pine import Pine

TOOLS = Path(__file__).resolve().parent
RECIPE = TOOLS / "headless_oracle_recipe.json"
PCSX2_SHA256 = "1972341a1bf079e3b5180eeba9c2c233574a9fe38cadd4e5e85ea179e334f13d"
OFFSCREEN_SHA256 = "ac97d9562bc77cce9a627e1ac474bd2d16c68af2f674fe65e3bece1cd0210679"
DESKTOP_OBSERVER_SHA256 = "a004275cc9da81e5492ed8eb90f63155177331991ec1bf816ebbf24c7479e16f"
DESKTOP_OBSERVER_SOURCE_SHA256 = "3f9f48ffa18d337db924e1b48c4b8980abedb5af8887d81d097e6ecee99d3926"
QT_SDK_ARCHIVE_SHA256 = "e469b996bd4dd6409aeab1a2034eb73267d5c8de84aa6224bf7c9520cdcbd309"
QT_BUILD_COMMAND_SHA256 = "e5786e5d4738715fd64ac6f35325b82ab67ba3be8139233d72f29dedaffe6ab5"
QT_PREPARATION_SHA256 = "068164de1068b1ebbb566224cd5ccb2b0bcebab6764afadcc5e365acf267dca1"
QT_SOURCE_HASHES = {
    "main.cpp": "94a0d2e4e5b2f74fe9508fba3e090d7735a7af955470a43d589a634fc981d03e",
    "qoffscreencommon.cpp": "81c8f3fad4e5db98d36fd463833f8b2350f651db546d7f513d970b03f50ab3ea",
    "qoffscreenintegration.cpp": "d0f5189839790e6c3535836765d831b7193a14d5e5f75f82187b3cb4986a7506",
    "qoffscreenwindow.cpp": "70cc98cee42d9a7779542e1e2a66e01d78214aa588ce984993186a6e62544558",
}
# Static LC_LOAD_DYLIB dependencies of the pinned PCSX2 executable and plugin.
# These pins bind installed bytes, not licenses or the effective runtime route.
QT_RUNTIME_LIBRARIES = {
    "libQt6Core.6.dylib": "5147afdc2cf2bd0189e3907ea49076b2ef5cad1eee355b19d7cccf8a53bf5afe",
    "libQt6Gui.6.dylib": "5e05e76aacb6dbc64330b44ceefcaa5c55c72de43293415d85e988ab19aa9f04",
    "libQt6Widgets.6.dylib": "1c393b9eaf659247739c862338e1a68f31dcbbedce975c444220876c8331681d",
    "libkddockwidgets-qt6.3.dylib": "60f5e6882d2a8207c8b4604a2c8324dad84c7d48584633f92daf396d8132fe06",
}
QT_DEPENDENCY_BLOCKERS = (
    "The prebuilt Qt SDK's full corresponding source or applicable source offer is not bound to the pinned package.",
    "The installed Qt libraries and docking library lack exact package/source/build and complete notice bindings.",
)
EXPECTED_WORDS = [0x46523250, 21, 0x10DF30BF, 1]
MAX_TIMEOUT_SECONDS = 60
DESKTOP_SAMPLE_INTERVAL_MS = 50
DESKTOP_SAMPLE_COUNT = 400
AC25_QUALIFICATION_BLOCKERS = (
    "Effective audio output has not been independently qualified; Null/mute settings are configuration requests only.",
    "Window and focus monitoring samples every 50 ms for 20 seconds and cannot rule out transient events between samples or outside that interval.",
)


def _sbpl(path: Path) -> str:
    value = str(path.resolve())
    if any(char in value for char in ('"', "\\", "\n", "\r")):
        raise Invalid("sandbox paths may not contain quotes, escapes, or newlines")
    return f'"{value}"'


def build_settings(home: Path, bios: Path, pine_slot: int) -> Path:
    """Write the complete small profile needed by this probe in a fresh HOME."""
    if not 28000 <= pine_slot <= 28999:
        raise Invalid("PINE slot must be in the fixed local test range 28000..28999")
    app_data = home / "Library" / "Application Support" / "PCSX2"
    inis = app_data / "inis"
    for folder in (inis, app_data / "logs", app_data / "sstates", app_data / "snaps",
                   app_data / "memcards", app_data / "cache", app_data / "cheats",
                   app_data / "patches", app_data / "resources", app_data / "textures",
                   app_data / "inputprofiles", app_data / "videos"):
        folder.mkdir(parents=True, exist_ok=True)
    settings = configparser.ConfigParser(interpolation=None)
    # PCSX2's INI option names are case-sensitive; preserve C++ setting keys.
    settings.optionxform = str
    settings["UI"] = {
        "SettingsVersion": "1", "StartPaused": "false", "PauseOnFocusLoss": "false",
        "StartFullscreen": "false", "RenderToSeparateWindow": "false",
        "HideMainWindowWhenRunning": "true", "SetupWizardIncomplete": "false",
    }
    settings["Folders"] = {
        "Bios": str(bios.parent.resolve()), "Logs": str(app_data / "logs"),
        "Savestates": str(app_data / "sstates"), "Snapshots": str(app_data / "snaps"),
        "MemoryCards": str(app_data / "memcards"), "Cache": str(app_data / "cache"),
        "Cheats": str(app_data / "cheats"), "Patches": str(app_data / "patches"),
        "UserResources": str(app_data / "resources"), "Textures": str(app_data / "textures"),
        "InputProfiles": str(app_data / "inputprofiles"), "Videos": str(app_data / "videos"),
    }
    settings["Filenames"] = {"BIOS": bios.name}
    settings["EmuCore"] = {
        "EnablePINE": "true", "PINESlot": str(pine_slot), "EnablePatches": "false",
        "EnableCheats": "false", "EnableWideScreenPatches": "false",
        "EnableNoInterlacingPatches": "false", "EnableDiscordPresence": "false",
        "HostFs": "false", "EnableGameFixes": "false",
    }
    settings["EmuCore/GS"] = {
        "Renderer": "11", "OsdShowSpeed": "false", "OsdShowFPS": "false",
        "OsdShowVPS": "false", "OsdShowCPU": "false", "OsdShowGPU": "false",
        "OsdShowResolution": "false", "OsdShowGSStats": "false", "OsdShowIndicators": "false",
        "OsdShowSettings": "false", "OsdShowVideoCapture": "false",
        "OsdShowInputRec": "false", "OsdShowVersion": "false",
    }
    settings["SPU2/Output"] = {"Backend": "Null", "OutputMuted": "true"}
    settings["Debugger/UserInterface"] = {"ShowOnStartup": "false"}
    settings["Logging"] = {"EnableLogWindow": "false"}
    settings["Achievements"] = {"Enabled": "false", "Enable": "false"}
    path = inis / "PCSX2.ini"
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        settings.write(stream)
    return path


def make_sandbox_profile(root: Path, pine_slot: int) -> str:
    """Deny service lookup and IP sockets; allow only the run tree and PINE UDS."""
    socket_path = root / "tmp" / f"pcsx2.sock.{pine_slot}"
    return "\n".join((
        "(version 1)",
        "(deny default)",
        "(allow process-exec)",
        "(allow process-fork)",
        "(allow process-info* (target self))",
        "(allow signal (target self))",
        "(allow sysctl-read)",
        "(allow file-read*)",
        f"(allow file-write* (subpath {_sbpl(root)}))",
        "(deny mach-lookup)",
        "(deny network*)",
        f"(allow network-inbound (local unix-socket (path {_sbpl(socket_path)})))",
        f"(allow network-outbound (local unix-socket (path {_sbpl(socket_path)})))",
        "",
    ))


def validate_observation(words: list[int], desktop: dict) -> dict:
    if words != EXPECTED_WORDS:
        return {"status": "fail", "reason": "controlled probe memory differs from the known output",
                "expected_words": EXPECTED_WORDS, "observed_words": words}
    timestamps = desktop.get("timestamps_ns", [])
    started, stopped = desktop.get("emulator_started_ns"), desktop.get("emulator_stopped_ns")
    frontmost = desktop.get("frontmost_pids", [])
    windows = desktop.get("owned_window_counts", [])
    if (not frontmost or len(frontmost) != len(windows)
            or len(frontmost) != desktop.get("sample_count")
            or len(frontmost) != DESKTOP_SAMPLE_COUNT):
        return {"status": "incomplete", "reason": "desktop observation was unavailable or malformed"}
    if (len(timestamps) != len(frontmost) or not isinstance(started, int)
            or not isinstance(stopped, int) or started >= stopped
            or any(not isinstance(at, int) or not started <= at <= stopped for at in timestamps)
            or any(right <= left for left, right in zip(timestamps, timestamps[1:]))):
        return {"status": "incomplete", "reason": "desktop samples do not cover the live emulator interval"}
    if any(count != 0 for count in windows):
        return {"status": "fail", "reason": "PCSX2 owned a native window during the run",
                "frontmost_pids": frontmost, "owned_window_counts": windows}
    if len(set(frontmost)) != 1:
        return {"status": "incomplete", "reason": "frontmost application changed during observation",
                "frontmost_pids": frontmost, "owned_window_counts": windows}
    return {"status": "pass", "reason": "known probe output observed with no PCSX2 window and stable foreground",
            "frontmost_pids": frontmost, "owned_window_counts": windows,
            "expected_words": EXPECTED_WORDS, "observed_words": words}


def ac25_acceptance(observation: dict) -> dict:
    """Fail closed: sampled observations cannot qualify this runtime profile."""
    if observation.get("status") == "fail":
        return {"status": "fail", "reason": observation.get("reason", "behavioral observation failed"),
                "blockers": list(AC25_QUALIFICATION_BLOCKERS)}
    return {"status": "incomplete",
            "reason": "Raw observations do not qualify AC25 for this installed runtime profile.",
            "blockers": list(AC25_QUALIFICATION_BLOCKERS)}


def validate_probe_files(elf: Path, source: Path, linker_script: Path, recipe: dict) -> dict:
    actual = {"probe_elf": identity(elf), "probe_source": identity(source),
              "linker_script": identity(linker_script)}
    for name, value in actual.items():
        if value["sha256"] != recipe[name]["sha256"]:
            raise Invalid(f"{name} differs from the pinned controlled-probe recipe")
    return actual


def verify_qt_inputs(sdk_archive: Path, source_dir: Path, build_command: Path,
                     preparation: Path) -> dict:
    actual = {
        "qt_sdk_archive": identity(sdk_archive),
        "qt_build_command": identity(build_command),
        "qt_preparation_record": identity(preparation),
        "qt_offscreen_sources": {name: identity(source_dir / name)
                                  for name in QT_SOURCE_HASHES},
    }
    expected_artifacts = {
        "qt_sdk_archive": QT_SDK_ARCHIVE_SHA256,
        "qt_build_command": QT_BUILD_COMMAND_SHA256,
        "qt_preparation_record": QT_PREPARATION_SHA256,
    }
    for name, expected in expected_artifacts.items():
        if actual[name]["sha256"] != expected:
            raise Invalid(f"{name} differs from the pinned Qt 6.10.1 SDK/build evidence")
    for name, expected in QT_SOURCE_HASHES.items():
        if actual["qt_offscreen_sources"][name]["sha256"] != expected:
            raise Invalid(f"Qt offscreen source differs from the pinned source: {name}")
    return actual


def verify_inputs(emulator: Path, plugin: Path, elf: Path, source: Path,
                  linker_script: Path, probe_build_log: Path, bios: Path,
                  observer: Path, observer_source: Path, qt_archive: Path,
                  qt_source_dir: Path, qt_build_command: Path,
                  qt_preparation: Path) -> dict:
    libraries, missing_libraries = {}, []
    for name, expected in QT_RUNTIME_LIBRARIES.items():
        path = emulator.parent.parent / "Frameworks" / name
        if not path.is_file():
            missing_libraries.append(f"required Qt runtime dependency is missing: {name}")
            continue
        libraries[name] = identity(path)
        if libraries[name]["sha256"] != expected:
            raise Invalid(f"Qt runtime dependency differs from the pinned installed profile: {name}")
    recipe = json.loads(RECIPE.read_text())
    for path in (emulator, plugin, elf, source, linker_script, probe_build_log,
                 bios, observer, observer_source, qt_archive, qt_build_command,
                 qt_preparation, *(qt_source_dir / name for name in QT_SOURCE_HASHES)):
        if not path.is_file():
            raise Incomplete(f"required local oracle input is missing: {path}")
    actual = {"pcsx2": identity(emulator), "offscreen_plugin": identity(plugin),
              **validate_probe_files(elf, source, linker_script, recipe),
              "probe_build_log": identity(probe_build_log),
              "firmware": identity(bios),
              "desktop_observer": identity(observer),
              "desktop_observer_source": identity(observer_source),
              **verify_qt_inputs(qt_archive, qt_source_dir,
                                 qt_build_command, qt_preparation)}
    if actual["pcsx2"]["sha256"] != PCSX2_SHA256:
        raise Incomplete("installed PCSX2 differs from the qualified v2.6.3 executable")
    if actual["offscreen_plugin"]["sha256"] != OFFSCREEN_SHA256:
        raise Incomplete("offscreen platform plugin differs from the qualified local build")
    if actual["desktop_observer"]["sha256"] != DESKTOP_OBSERVER_SHA256:
        raise Incomplete("desktop observer executable differs from the qualified local build")
    if actual["desktop_observer_source"]["sha256"] != DESKTOP_OBSERVER_SOURCE_SHA256:
        raise Invalid("desktop observer source differs from the qualified source")
    if actual["probe_build_log"]["sha256"] != recipe["builder"]["build_log_sha256"]:
        raise Invalid("probe builder log differs from the pinned build provenance")
    if missing_libraries:
        raise Incomplete("; ".join(missing_libraries))
    actual["qt_runtime_libraries"] = libraries
    # Byte identity is necessary but cannot supply the missing #22 disposition.
    # This is a recorded profile decision, never a caller-supplied unlock flag.
    raise Incomplete("Qt dependency qualification lacks corresponding source and package notice bindings (#22).", {
        "authority": "static_dependency_preflight", "criterion": "AC25",
        "inputs": {"identities": actual, "recipe": recipe},
        "dependency_qualification": {"status": "incomplete", "issue": 22,
                                     "blockers": list(QT_DEPENDENCY_BLOCKERS)},
        "lifecycle": {"launched": False},
        "separation": {"evidence_kind": "dependency_provenance", "static_byte_credit": 0,
                       "accepted_as_reconstruction_or_matching_evidence": False},
    })


def _kill_group(process: subprocess.Popen, grace: float = 2.0) -> dict:
    # The leader may have exited while a child remains in the owned session.
    # Signal and verify the process group regardless of the leader's state.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        code = process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        code = None
    group_deadline = time.monotonic() + grace
    while _group_exists(process.pid) and time.monotonic() < group_deadline:
        time.sleep(0.05)
    forced_kill = _group_exists(process.pid)
    if forced_kill:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        kill_deadline = time.monotonic() + grace
        while _group_exists(process.pid) and time.monotonic() < kill_deadline:
            time.sleep(0.05)
    if process.poll() is None:
        try:
            code = process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            code = process.poll()
    remaining = _group_exists(process.pid)
    return {"returncode": process.returncode if process.returncode is not None else code,
            "forced_kill": forced_kill, "process_group_remaining": remaining}


def _group_exists(group_id: int) -> bool:
    try:
        os.killpg(group_id, 0)
        return True
    except ProcessLookupError:
        return False


def cleanup_failure(lifecycle: dict) -> str | None:
    return "owned process group survived cleanup" if lifecycle.get("process_group_remaining") else None


def validate_timeout(timeout: int) -> None:
    if timeout <= 0 or timeout > MAX_TIMEOUT_SECONDS:
        raise Invalid(f"timeout must be within 1..{MAX_TIMEOUT_SECONDS} seconds")


def read_probe_output(pine: Pine, deadline: float) -> dict:
    """Read status and known words without allowing a stalled PINE reply to hang."""
    def bounded(call):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("strict oracle observation deadline expired")
        pine.socket.settimeout(remaining)
        return call()

    status = bounded(pine.status)
    words = [int.from_bytes(bounded(
        lambda index=index: pine.read(0x00180000 + index * 4, 4)), "little")
        for index in range(4)]
    return {"pine_status": status, "output_address": "0x00180000", "words": words}


def wait_for_probe_output(pine: Pine, process: subprocess.Popen,
                          deadline: float) -> dict:
    """Wait for the source-pinned final word before reading the complete output."""
    sentinel_address = 0x00180000 + 3 * 4
    while True:
        if process.poll() is not None:
            raise Incomplete(f"PCSX2 exited before the probe completion sentinel (exit {process.returncode})")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Incomplete("probe completion sentinel was not observed before the deadline")
        pine.socket.settimeout(remaining)
        sentinel = int.from_bytes(pine.read(sentinel_address, 4), "little")
        if sentinel == 1:
            observed = read_probe_output(pine, deadline)
            if process.poll() is not None:
                raise Incomplete(
                    f"PCSX2 exited during the probe observation (exit {process.returncode})"
                )
            return observed
        time.sleep(min(0.1, max(0, deadline - time.monotonic())))


def execute(args, output: Path) -> dict:
    if sys.platform != "darwin":
        raise Incomplete("strict PCSX2 oracle is currently qualified only on macOS")
    validate_timeout(args.timeout)
    (emulator, plugin, elf, source, linker, build_log, bios, observer,
     observer_source, qt_archive, qt_source_dir, qt_build_command,
     qt_preparation) = (Path(p).resolve() for p in (
         args.emulator, args.platform_plugin, args.elf, args.probe_source,
         args.linker_script, args.probe_build_log, args.bios,
         args.desktop_observer, args.desktop_observer_source,
         args.qt_sdk_archive, args.qt_source_dir, args.qt_build_command,
         args.qt_preparation_record))
    input_record = verify_inputs(emulator, plugin, elf, source, linker, build_log,
                                 bios, observer, observer_source, qt_archive,
                                 qt_source_dir, qt_build_command, qt_preparation)
    pine_slot = 28031
    run_root = output / ("strict-runtime-" + uuid.uuid4().hex)
    home = run_root / "home"
    tmp = run_root / "tmp"
    tmp.mkdir(parents=True, exist_ok=False)
    profile_path = run_root / "strict.sandbox"
    profile_path.write_text(make_sandbox_profile(run_root, pine_slot), encoding="utf-8")
    config_path = build_settings(home, bios, pine_slot)
    live_settings = Path.home() / "Library" / "Application Support" / "PCSX2"
    if config_path == live_settings / "inis" / "PCSX2.ini" or live_settings in config_path.parents:
        raise Invalid("isolated settings resolve into the user's existing PCSX2 profile")
    if args.sandbox_exec.resolve() != Path("/usr/bin/sandbox-exec"):
        raise Invalid("sandbox executable must be /usr/bin/sandbox-exec")
    socket_path = tmp / f"pcsx2.sock.{pine_slot}"
    log_path = run_root / "pcsx2.log"
    command = [str(args.sandbox_exec.resolve()), "-f", str(profile_path), str(emulator),
               "-nogui", "-nofullscreen", "-elf", str(elf), "-logfile", str(log_path)]
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(home), "TMPDIR": str(tmp),
        "QT_QPA_PLATFORM": "offscreen", "QT_QPA_PLATFORM_PLUGIN_PATH": str(plugin.parent),
        "QT_MAC_DISABLE_FOREGROUND_APPLICATION_TRANSFORM": "1", "QT_QPA_OFFSCREEN_NO_GLX": "1",
        "LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8",
    }
    (run_root / "command.json").write_text(json.dumps({"argv": command, "environment": env}, indent=2) + "\n")
    desktop_path = run_root / "desktop-observer.txt"
    stdout_path, stderr_path = run_root / "stdout.txt", run_root / "stderr.txt"
    process = None
    pine = None
    observer_process = None
    observed = None
    lifecycle = {}
    failure_reason = None
    emulator_started_ns = emulator_stopped_ns = None
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                       env=env, start_new_session=True, close_fds=True)
            emulator_started_ns = time.monotonic_ns()
            with desktop_path.open("wb") as desktop_stream:
                observer_process = subprocess.Popen([str(observer), str(process.pid)],
                                                    stdout=desktop_stream,
                                                    stderr=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    failure_reason = f"PCSX2 exited before the probe observation (exit {process.returncode})"
                    break
                if socket_path.exists():
                    try:
                        pine = Pine(socket_path)
                        break
                    except OSError:
                        pine = None
                time.sleep(0.1)
            if pine is None and failure_reason is None:
                failure_reason = "PCSX2 did not expose the expected bounded PINE Unix socket"
            if pine is not None:
                try:
                    observed = wait_for_probe_output(pine, process, deadline)
                except (Incomplete, OSError, Invalid) as error:
                    failure_reason = f"PINE observation failed before the deadline: {error}"
    finally:
        if pine is not None:
            pine.close()
        if process is not None:
            emulator_stopped_ns = time.monotonic_ns()
            lifecycle = _kill_group(process)
            lifecycle.update(started_ns=emulator_started_ns, stopped_ns=emulator_stopped_ns)
        if observer_process is not None:
            try:
                observer_process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                observer_process.terminate()
                try:
                    observer_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    observer_process.kill()
                    observer_process.wait(timeout=2)
        if desktop_path.exists():
            samples = []
            for line in desktop_path.read_text(errors="replace").splitlines():
                fields = line.split()
                if len(fields) == 4 and all(field.isdecimal() for field in fields):
                    samples.append([int(fields[0]), int(fields[2]), int(fields[3])])
            desktop = {"sample_count": len(samples),
                       "timestamps_ns": [item[0] for item in samples],
                       "frontmost_pids": [item[1] for item in samples],
                       "owned_window_counts": [item[2] for item in samples]}
        else:
            desktop = {"sample_count": 0, "frontmost_pids": [], "owned_window_counts": []}
    desktop.update(emulator_started_ns=emulator_started_ns, emulator_stopped_ns=emulator_stopped_ns)
    runtime_artifacts = {}
    for name, path in (("sandbox_profile", profile_path), ("settings", config_path),
                       ("stdout", stdout_path), ("stderr", stderr_path),
                       ("emulator_log", log_path), ("desktop_samples", desktop_path),
                       ("command", run_root / "command.json")):
        if path.is_file():
            runtime_artifacts[name] = {"path": str(path), **identity(path)}
    if observed is None:
        detail = {"authority": "incomplete_executed_runtime_attempt", "criterion": "AC25",
                  "acceptance": {"status": "incomplete",
                                 "blockers": list(AC25_QUALIFICATION_BLOCKERS)},
                  "observation_sampling": {"interval_ms": DESKTOP_SAMPLE_INTERVAL_MS,
                                           "sample_count_target": DESKTOP_SAMPLE_COUNT,
                                           "duration_ms": DESKTOP_SAMPLE_INTERVAL_MS * DESKTOP_SAMPLE_COUNT},
                  "inputs": input_record, "command": command, "environment": env,
                  "lifecycle": lifecycle, "desktop": desktop, "runtime_artifacts": runtime_artifacts,
                  "separation": {"evidence_kind": "behavioral", "static_byte_credit": 0,
                                 "accepted_as_reconstruction_or_matching_evidence": False},
                  "profile_limits": ["No mach-lookup or IP networking was permitted.",
                                     "Only the exact local PINE AF_UNIX socket was allowed."],
                  "reason": failure_reason or "strict oracle did not capture controlled probe output"}
        cleanup_error = cleanup_failure(lifecycle)
        if cleanup_error:
            detail["failures"] = [cleanup_error, detail["reason"]]
            return detail
        raise Incomplete(detail["reason"], detail)
    desktop_result = validate_observation(observed["words"], desktop)
    acceptance = ac25_acceptance(desktop_result)
    details = {
        "status": acceptance["status"], "authority": "executed_behavioral_observation",
        "acceptance": acceptance,
        "criterion": "AC25", "scope": "one hand-written controlled EE probe under PCSX2 v2.6.3",
        "inputs": input_record, "command": command, "environment": env,
        "settings_path": str(config_path), "settings_sha256": identity(config_path)["sha256"],
        "sandbox_profile": str(profile_path), "sandbox_profile_sha256": identity(profile_path)["sha256"],
        "pine": observed, "desktop": desktop, "observation": desktop_result,
        "observation_sampling": {"interval_ms": DESKTOP_SAMPLE_INTERVAL_MS,
                                 "sample_count_target": DESKTOP_SAMPLE_COUNT,
                                 "duration_ms": DESKTOP_SAMPLE_INTERVAL_MS * DESKTOP_SAMPLE_COUNT},
        "runtime_artifacts": runtime_artifacts,
        "lifecycle": lifecycle,
        "separation": {"evidence_kind": "behavioral", "static_byte_credit": 0,
                       "accepted_as_reconstruction_or_matching_evidence": False},
        "limitations": ["The probe is hand-written and synthetic; it is not reconstructed game code.",
                        "This does not establish original/rebuilt game equivalence or whole-game behavior.",
                        "Frontmost changes during the observation make the result incomplete."]}
    failures = []
    cleanup_error = cleanup_failure(lifecycle)
    if cleanup_error:
        failures.append(cleanup_error)
    if desktop_result["status"] == "fail":
        failures.append(desktop_result["reason"])
    if failures:
        details["status"] = "fail"
        details["failures"] = failures
        return details
    details["status"] = "incomplete"
    raise Incomplete(acceptance["reason"], details)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emulator", type=Path, required=True)
    parser.add_argument("--platform-plugin", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--probe-source", type=Path, required=True)
    parser.add_argument("--linker-script", type=Path, required=True)
    parser.add_argument("--probe-build-log", type=Path, required=True)
    parser.add_argument("--bios", type=Path, required=True)
    parser.add_argument("--desktop-observer", type=Path, required=True)
    parser.add_argument("--desktop-observer-source", type=Path, required=True)
    parser.add_argument("--qt-sdk-archive", type=Path, required=True)
    parser.add_argument("--qt-source-dir", type=Path, required=True)
    parser.add_argument("--qt-build-command", type=Path, required=True)
    parser.add_argument("--qt-preparation-record", type=Path, required=True)
    parser.add_argument("--sandbox-exec", type=Path, default=Path("/usr/bin/sandbox-exec"))
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate_timeout(args.timeout)
    except Invalid as error:
        parser.error(str(error))
    inputs = [Path(__file__), RECIPE, Path(args.emulator), Path(args.platform_plugin),
              Path(args.elf), Path(args.probe_source), Path(args.linker_script),
              Path(args.probe_build_log), Path(args.bios), Path(args.desktop_observer),
              Path(args.desktop_observer_source), Path(args.qt_sdk_archive),
              Path(args.qt_build_command), Path(args.qt_preparation_record),
              *(Path(args.qt_source_dir) / name for name in QT_SOURCE_HASHES),
              *(Path(args.emulator).parent.parent / "Frameworks" / name
                for name in QT_RUNTIME_LIBRARIES),
              TOOLS / "pcsx2_pine.py",
              TOOLS / "evidence_common.py"]
    return write_result(args.output, "fr2-headless-behavioral-oracle",
                        lambda: execute(args, args.output),
                        # Record available hashes; fixed preflight diagnoses absence
                        # after checking the available Qt libraries for contradictions.
                        [path for path in inputs if path.is_file()])


if __name__ == "__main__":
    raise SystemExit(main())
