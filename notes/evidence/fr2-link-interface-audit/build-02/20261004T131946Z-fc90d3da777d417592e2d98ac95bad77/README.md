# Build 02: runtime and generated objects link successfully

The isolated `ps2EntryRunner` target configured and built with the bundled CMake 3.31.6 and Unix Makefiles. It compiled the pinned PS2Recomp runtime/IOP sources and raylib 5.5, then linked 16 generated function batches plus the generated registration object. The output is an arm64 Mach-O executable. **It was not executed**; this is compile/link evidence only.

The first link attempt exposed the real registration integration issue: the runtime's default `register_functions.cpp` defines a zero-initialized 4M-slot table, while the supplied generated registration object defines the same table and three metadata globals. The second isolated wrapper removes that placeholder source and supplies the generated registration object. The corrected link succeeds.

Raylib's CMake pin is tag `5.5` at commit `c1ab645ca298a2801097931d1079b10ff7eb9df8`; the shallow checkout is clean. Its `LICENSE` SHA-256 is recorded in `result.json`. Existing generator dependency source directories were provided as local FetchContent overrides; recompilation itself was disabled for this runtime-link check. FFmpeg and debug UI were disabled. Raylib was still built and linked as required by the desktop host backend.

CMake initially could not locate Ninja; `/usr/bin/make` was available, so the build used Unix Makefiles. The first Make-based link failed on the four duplicate table symbols described above. The final build completed with no unresolved-symbol errors. Build warnings are counted and retained in the JSON evidence.

This says nothing about executing the runner, game boot, gameplay, GUI behavior, media decoding, or semantic correctness of the 4,746 generated functions. Existing runtime fallbacks remain in scope as limitations. See `result.json` for exact commands, source/input/output hashes, build options, and retained compiler-warning text.
