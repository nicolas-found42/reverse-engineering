# Static generated-archive/runtime interface audit

This read-only audit checks the native FPU-patched generated archive against its pinned PS2Recomp runtime source and CMake integration. It performs symbol-table and source inspection only. No game code, emulator, GUI, runtime, or executable was launched, and no link was attempted.

The archive `.scratch/mesh/codex-root/libfr2_recompiled-fpu-01.a` (83,527,016 bytes; SHA-256 `26592f274eeb1961d4f61f7d8f5d5d4707a7a67becaf32ebe292e1efe99f0ed8`) has 4,746 distinct generated `sub_...` definitions and includes its registration object. `nm -u` lists 4,767 distinct undefined names across archive members. Comparing those names with archive-wide global definitions resolves all 4,746 generated-function references. The 21 names that remain are 18 `PS2Runtime` methods and three Darwin stack-check ABI symbols (`___chkstk_darwin`, `___stack_chk_fail`, and `___stack_chk_guard`). The 18 runtime methods have declarations in `ps2xRuntime/include/ps2_runtime.h` and definitions in `ps2xRuntime/src/lib/ps2_runtime.cpp` in clone HEAD `c5a9d02573410a2085a4b4b831b0b68ba3515440`. The generated registration object defines the four `g_ps2RecompiledFunctionTable*` globals referenced by the runtime. Repeated helper definitions in object members are marked weak by `nm -m`, not strong duplicate definitions.

The compile/archive evidence stops before linking. The existing `recomp-fpu-build-01/CMakeCache.txt` sets `PS2X_BUILD_RUNTIME=OFF` and `PS2X_BUILD_RECOMP=ON`; the saved compiler report says it compiled translation units only, and the archive report says it inventoried symbols only. More directly, the inspected runtime CMake file does not include or link the measured generated archive/registration object: `ps2EntryRunner` links only `ps2_runtime`, and the runtime library target does not list the generated output. As the runtime source references the generated table globals, a full runner build must wire the generated archive/registration object into its link. This is an integration blocker in the inspected CMake state; no link failure was experimentally induced.

The current desktop CMake path is not a standalone headless target. On non-Vita builds, the host backend links raylib. FFmpeg defaults on for non-Android builds and requires pkg-config modules for libavcodec, libavformat, libavutil, libswresample, and libswscale; it can be disabled, in which case CMake describes the MPEG decode behavior as stub frames. Turning off the debug UI removes its optional rlImGui/imgui link from the runner, but does not remove raylib from the host backend. The current cache disabled the runtime altogether, so those runtime target dependencies have not been built in the inspected build.

Runtime source presence should not be read as complete game behavior. For example, an unhandled numeric syscall routes to a TODO fallback (whose generic unknown-syscall behavior logs and returns zero); the generic unimplemented imported PS2 stub throws `std::runtime_error`; and VU0 execution uses an idle-success fallback if code/data are absent or the start range is invalid. These are runtime policies/fallbacks, not unresolved link symbols, and their behavior is not validated here. The archive also has Darwin stack-check dependencies and should be rebuilt with the intended host toolchain for another OS.

## Evidence and commands

The following read-only checks were run:

- `shasum -a 256 .scratch/mesh/codex-root/libfr2_recompiled-fpu-01.a`
- `nm -u .scratch/mesh/codex-root/libfr2_recompiled-fpu-01.a`
- `nm -g .scratch/mesh/codex-root/libfr2_recompiled-fpu-01.a`
- `nm -m .scratch/mesh/codex-root/libfr2_recompiled-fpu-01.a` (checked repeated helper symbol binding)
- `nm -g .scratch/mesh/codex-root/recomp-registration-fpu-01.o` (checked generated table globals)
- `git -C .scratch/mesh/codex-root/PS2Recomp-fpu-01 rev-parse HEAD`
- `rg -n` for runtime method declarations/definitions, CMake source/target composition, and fallback paths
- `jgrep --json "defines the runtime context and helper functions called by generated recompiled function units" ps2xRuntime ps2xRecomp/src` from the pinned clone. It returned runtime-stub and syscall implementation candidates; exact declarations and definitions were then confirmed by direct source inspection.
- `jgrep --json "routes guest system calls that are not recognized by the runtime through a fallback handler that may be incomplete" ps2xRuntime/src/lib ps2xRuntime/src/lib/Kernel` from the pinned clone. It returned the syscall TODO and generic unimplemented-stub fallback candidates; behavior claims were checked in the source.

Source clone commit, input/archive hashes, unresolved API names, build toggles, source locations, and Jev outcomes are recorded in `metadata.json` and `jev-receipt.json`. The evidence contains no generated game function body or source payload.

## Later static link result

The [build-03 package](build-03/20261004T132336Z-15e0e2ec81eb4d19bcf27760c39e30c9/README.md) supersedes the initial prerequisite-only outcome. The runtime, IOP and pinned raylib library compiled, and all 17 generated objects linked after the runner placeholder registration source was excluded. Root independently checked the 81,438,416-byte arm64 Mach-O binary hash, all object hashes, all 4,746 distinct guest addresses, and exactly one definition per registration global. The runner has not been executed; successful static linkage does not prove headless execution or game equivalence. The exact failed attempts and Jev escalations remain preserved.
