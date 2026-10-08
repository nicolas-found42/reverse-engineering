# Strict headless behavioral oracle

`tools/headless_oracle.py` is a separate behavioral check for AC25. It launches
one hand-written controlled EE probe under the locally installed PCSX2 v2.6.3
build. It does not consume the reconstructed-code ledger, matching receipts, or
the corpus, and its result explicitly grants zero static byte credit.

The runner fixes `-nogui -nofullscreen -elf`, forces Qt's offscreen platform,
disables foreground transformation, requests null GS and SPU2 output, and writes a
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

The PINE reader waits for the probe's final sentinel before reading the complete
known output. Raw probe/window/focus observations are retained separately from
AC25 acceptance. Even a raw match remains **incomplete** for this installed
profile: the Null/muted settings are requests, not independent evidence of the
effective audio route, and the desktop observer takes 400 samples at a nominal
50 ms interval over 20 seconds. Events between samples, or outside the sampled
interval, can be missed. No caller flag or receipt claim can turn these
observations into an AC25 pass.

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
  --qt-sdk-archive /path/to/qtbase.7z \
  --qt-source-dir /path/to/qt-offscreen-src \
  --qt-build-command /path/to/plugin-build-command-03.json \
  --qt-preparation-record /path/to/offscreen-plugin-preparation.json \
  --output /path/to/fresh-evidence-directory
```

The runner pins all four Qt offscreen implementation source files, the local SDK
archive, the build command, the prepared-plugin record, and the probe
source/linker/build log. Altered inputs are rejected before PCSX2 launch. The
four local offscreen `.cpp` files were checked against the matching hashes from
the official [Qt 6.10.1 source tag](https://github.com/qt/qtbase/tree/v6.10.1/src/plugins/platforms/offscreen).
The official [Qt 6.10.1 source archive](https://download.qt.io/official_releases/qt/6.10/6.10.1/submodules/qtbase-everywhere-src-6.10.1.zip)
is a source reference; it is not the local `qtbase.7z` SDK archive.

Each of the four offscreen implementation files carries this header:

```text
// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
```

These are the source's declared license alternatives, not a determination of
which alternative governs every linked SDK component. The local `qtbase.7z`
archive is a prebuilt SDK package, not corresponding source. Its Qt-generated
SBOM points to qtbase commit `90b845d15ffb97693dba527385db83510ebd121a`; the
package-level SPDX fields are `NOASSERTION`, while individual Qt module entries
declare the alternatives above. This evidence does not bind the full source
corresponding to that SDK build, an applicable written offer, or all package
notices. Qt's official [licensing](https://doc.qt.io/qt-6/licensing.html) and
[LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)
describe source and redistribution routes; this repository neither includes
the SDK archive nor distributes the locally built plugin or Qt libraries.

The current strict runtime attempt is **incomplete**. PCSX2 loaded the isolated
configuration and probe, then exited with SIGSEGV in `GSDeviceMTL::Create`
before PINE returned probe memory. Its log reported no Metal devices, while
the sandbox recorded denied lookups for system policy, trust, analytics,
OpenDirectory, logging, and notification services. The strict profile was
retained; none of those denials is whitelisted. The external desktop observer
sampled 400 times with no PCSX2-owned windows and an unchanged foreground PID
across its nominal 20-second interval. PCSX2 exited about 3.0 seconds after
launch; observer samples had no timestamps, so exact overlap with the live
process cannot be established. This observation does not compensate for the missing
probe output, and no behavior pass is claimed. Per-run logs, configuration,
sandbox profile, process cleanup result, input hashes, and the incomplete
receipt remain in the local continuation evidence directory.

That retained attempt predates the runner's Qt source/build evidence arguments;
its original receipt pins the plugin binary and runtime inputs, but does not
retroactively bind the Qt SDK archive or build command. The committed runner
requires and records those provenance inputs for any subsequent execution.

The v2.6.3 source enum defines GS renderer `Null` as 11 (`Metal` is 17), and
the isolated, case-preserving profile contains `Renderer = 11`; audio is set to
`Backend = Null`. The crash therefore remains unexplained by the verified
renderer/audio keys. No service exception or renderer substitution is made.
An earlier unsandboxed `--help` attempt is retained as an excluded incident;
it is not part of the strict observation and supports no no-window or no-focus
claim. Its separate local incident record preserves the PID, command, timing,
termination, and verification details.

The focused tests cover the fixed profile, source/environment mutation,
sentinel/deadline behavior, process-group cleanup, raw positive and negative
observations, and the rule that raw positive observations remain AC25
incomplete. A public completion CLI test attempts `--behavioral-receipt` and
verifies refusal before output creation. These tests do not emulate PCSX2 or
count as AC25 runtime acceptance. The oracle remains separate from static
completion; AC26's original-versus-rebuilt observations are still unimplemented.
