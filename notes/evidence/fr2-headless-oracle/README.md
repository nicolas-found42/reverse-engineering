# Strict headless behavioral oracle

`tools/headless_oracle.py` is a separate behavioral check for AC25. It launches
one hand-written controlled EE probe under the locally installed PCSX2 v2.6.3
build. It does not consume the reconstructed-code ledger, matching receipts, or
the corpus, and its result explicitly grants zero static byte credit.

The runner fixes `-nogui -nofullscreen -elf`, forces Qt's offscreen platform,
disables foreground transformation, uses null GS and SPU2 output, and writes a
fresh PCSX2 profile beneath the run directory. It denies all Mach service
lookups and IP networking. The only socket exception is the fixed local PINE
Unix socket. The runner reads the probe's four expected words through the
read-only PINE adapter, samples the frontmost process and PCSX2-owned window
count with the external desktop observer, then terminates and verifies cleanup
of its own process group. A changing foreground process is incomplete; any
PCSX2-owned window or output mismatch fails.

The isolated profile explicitly disables the debugger, log window, setup wizard,
fullscreen, OSD, cheats, and patches. The runner rejects a timeout outside its
bounded 1–60 second range before verifying inputs or starting a process.

The known probe is hand-written, not game-derived. Its source, linker script,
ELF digest, output address and expected words are pinned in
[`headless_oracle_recipe.json`](../../../tools/headless_oracle_recipe.json).
The local build log records the modern GNU toolchain/container used. The Qt
offscreen plugin was built from official Qt 6.10.1 source against the matching
installed Qt libraries; no Qt or PCSX2 binary is committed. The runtime recipe
is specific to this local macOS build and is not portable CI acceptance.

Invoke it with the explicit local artifacts:

```sh
python3 tools/headless_oracle.py \
  --emulator /Applications/PCSX2.app/Contents/MacOS/PCSX2 \
  --platform-plugin /path/to/qt-platform/plugins/platforms/libqoffscreen.dylib \
  --elf /path/to/controlled-probe.elf \
  --probe-source /path/to/controlled-probe.c \
  --linker-script /path/to/controlled-probe.ld \
  --probe-build-log /path/to/controlled-probe-build-02.log \
  --bios /path/to/ps2-bios.bin \
  --desktop-observer /path/to/observe-desktop \
  --desktop-observer-source /path/to/observe-desktop.m \
  --qt-source-archive /path/to/qtbase.7z \
  --qt-source-dir /path/to/qt-offscreen-src \
  --qt-build-command /path/to/plugin-build-command-03.json \
  --qt-preparation-record /path/to/offscreen-plugin-preparation.json \
  --output /path/to/fresh-evidence-directory
```

The runner pins all four Qt offscreen implementation source files, the original
Qt 6.10.1 source archive, the build command, the prepared-plugin record, and the
probe source/linker/build log. Altered inputs are rejected before PCSX2 launch.

The current strict runtime attempt is **incomplete**. PCSX2 loaded the isolated
configuration and probe, then exited with SIGSEGV in `GSDeviceMTL::Create`
before PINE returned probe memory. Its log reported no Metal devices, while
the sandbox recorded denied lookups for system policy, trust, analytics,
OpenDirectory, logging, and notification services. The strict profile was
retained; none of those denials is whitelisted. The external desktop observer
sampled 400 times with no PCSX2-owned windows and an unchanged foreground PID
during that attempt. That observation does not compensate for the missing
probe output, and no behavior pass is claimed. Per-run logs, configuration,
sandbox profile, process cleanup result, input hashes, and the incomplete
receipt remain in the local continuation evidence directory.

That retained attempt predates the runner's Qt source/build evidence arguments;
its original receipt pins the plugin binary and runtime inputs, but does not
retroactively bind the Qt source archive or build command. The committed runner
requires and records those provenance inputs for any subsequent execution.

The v2.6.3 source enum defines GS renderer `Null` as 11 (`Metal` is 17), and
the isolated, case-preserving profile contains `Renderer = 11`; audio is set to
`Backend = Null`. The crash therefore remains unexplained by the verified
renderer/audio keys. No service exception or renderer substitution is made.
An earlier unsandboxed `--help` attempt is retained as an excluded incident;
it is not part of the strict observation and supports no no-window or no-focus
claim. Its separate local incident record preserves the PID, command, timing,
termination, and verification details.

The focused tests exercise the runner's fixed profile, isolated/null settings,
known-output comparison, focus/window rejection, and rejection of a mutated
probe source before execution. They do not emulate PCSX2 or count as AC25 runtime
acceptance. The oracle remains separate from static completion; AC26's
original-versus-rebuilt observations are still unimplemented.
