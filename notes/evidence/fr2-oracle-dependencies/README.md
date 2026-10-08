# Strict oracle dependency preflight (#22)

The installed strict profile remains incomplete. Its prebuilt Qt SDK archive,
four upstream offscreen implementation files and local build command do not
bind full corresponding source or an applicable source offer, complete package
notices, and exact installed-library build identities. No permitted-use or
redistribution conclusion follows from matching bytes. #22 remains open; #14's
window, display, audio and focus qualification remains a separate requirement.

REA static Mach-O inspection of the pinned PCSX2 executable returned
`ev_7af24916f45f85a3befc9bc987d3b1b64c4ffa9a51847698ab6fd7646c9511a5`.
It observes load commands for Qt Core, Gui and Widgets (version 6.10.1) and
the docking library (version 2.4.0). Inspection of the pinned offscreen plugin
returned `ev_a9253cb54fd9c8921205d5f914309b0beeeca754411b8efb265135407129e466`;
its load commands refer to the installed Qt Core and Gui libraries.
[Retained dependency metadata](static-dependencies.json) includes identities,
complete dependency lists for these two roots, tool provenance and limitations.
The native sessions were closed. No emulator or guest code was executed.

Reproduce those static observations through REA `open_binary` on
`/Applications/PCSX2.app`, then `inspect_macho({})`, then `close_binary({})`;
repeat with the plugin from the command below. Ordinary local inspection is:

```sh
otool -L /Applications/PCSX2.app/Contents/MacOS/PCSX2
otool -L /Applications/PCSX2.app/Contents/Frameworks/libQt6Core.6.dylib
otool -L /Applications/PCSX2.app/Contents/Frameworks/libQt6Gui.6.dylib
otool -L /Applications/PCSX2.app/Contents/Frameworks/libQt6Widgets.6.dylib
otool -L /Applications/PCSX2.app/Contents/Frameworks/libkddockwidgets-qt6.3.dylib
otool -L /Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/oracle/qt-platform/plugins/platforms/libqoffscreen.dylib
```

These are static dependency declarations, not observed dynamic loads. They
do not enumerate dynamically selected plugins, establish a complete dependency
license closure, or prove which SDK tools produced the installed libraries.
Other bundled libraries and operating-system dependencies remain visible in
the retained root lists. Unused SDK files receive no permission disposition.

The public oracle CLI now refuses this profile before creating runtime state
or launching a process. It checks the four installed Qt/docking library hashes
recorded in `tools/headless_oracle.py`, then returns an immutable incomplete
receipt naming the missing provenance. A modified installed library returns
fail with its name; a missing library returns incomplete. Caller input cannot
change the qualification decision. A later dependency solution needs a reviewed
source/package/build record and a new recorded profile decision.

The local preflight was reproduced on 2026-10-08 after compiling the current
observer source. The observer matched its existing recorded binary pin. The
first attempt used an older observer and stopped at that identity check; that
failed prerequisite attempt remains local. The subsequent all-input-bound run
returned exit 2 at the #22 qualification check, with `lifecycle.launched: false`
and zero static-byte credit. No `strict-runtime-*` directory was created.

The declared local input root below already exists on this machine. The
ignored `.scratch/issue-22/bios.bin` link refers to the owner's existing local
firmware; neither the firmware nor its contents are published. From the repo:

```sh
clang -fobjc-arc tools/observe-desktop.m -framework AppKit -framework CoreGraphics -o .scratch/issue-22/observe-desktop
oracle_root=/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/oracle
python3 tools/headless_oracle.py \
  --emulator /Applications/PCSX2.app/Contents/MacOS/PCSX2 \
  --platform-plugin "$oracle_root/qt-platform/plugins/platforms/libqoffscreen.dylib" \
  --elf "$oracle_root/controlled-probe.elf" \
  --probe-source "$oracle_root/controlled-probe.c" \
  --linker-script "$oracle_root/controlled-probe.ld" \
  --probe-build-log "$oracle_root/controlled-probe-build-02.log" \
  --bios .scratch/issue-22/bios.bin \
  --desktop-observer .scratch/issue-22/observe-desktop \
  --desktop-observer-source tools/observe-desktop.m \
  --qt-sdk-archive "$oracle_root/qtbase.7z" \
  --qt-source-dir "$oracle_root/qt-offscreen-src" \
  --qt-build-command "$oracle_root/plugin-build-command-03.json" \
  --qt-preparation-record "$oracle_root/offscreen-plugin-preparation.json" \
  --output .scratch/issue-22/preflight
tools/check.sh test_headless_oracle
```

The synthetic CLI controls preserve the same behavior without Qt, firmware or
PCSX2: matching fixture identities still refuse unresolved provenance, changed
library bytes fail, and missing library bytes are incomplete. Process creation
is guarded at the system boundary so even a red test cannot execute a guest.
The existing observation/cleanup tests still cover historical lifecycle behavior;
they confer no runtime qualification. Full #22 AC1–AC3 remain incomplete, while
this change establishes the bounded missing/changed dependency refusal in AC4.
