# Link-only build preflight result

No runtime executable link was attempted. The local host has `clang++` and Apple Command Line Tools, but `cmake --version` failed with exit 127 (`zsh:1: command not found: cmake`), and `command -v pkg-config` returned no executable. The dependency cache `.scratch/mesh/codex-root/recomp-build/_deps` contains sse2neon, rabbitizer, fmt, toml11, libdwarf, and ELFIO sources/builds, but no `raylib-src`, `imgui-src`, or `rlimgui-src`; no raylib header/library was found under the searched local project and Homebrew directories. `brew list --versions cmake raylib` returned no installed package versions.

A read-only syntax check against the actual pinned runtime implementation failed immediately because the runtime includes `ps2_host_backend.h`, which requires raylib:

```text
clang++ -std=c++20 -DUSE_SSE2NEON -I .scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xRuntime/include -I .scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src -I .scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xIOP/include -I .scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xRuntime/src/lib/Kernel -fsyntax-only .scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xRuntime/src/lib/ps2_runtime.cpp
```

Compiler diagnostic:

```text
In file included from .scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xRuntime/src/lib/ps2_runtime.cpp:13:
.scratch/mesh/codex-root/PS2Recomp-fpu-01/ps2xRuntime/include/ps2_host_backend.h:3:10: fatal error: 'raylib.h' file not found
    3 | #include "raylib.h"
      |          ^~~~~~~~~~
1 error generated.
```

The generated input objects are Mach-O 64-bit arm64, as confirmed by `file` on `batch-00.o` and `recomp-registration-fpu-01.o`; the earlier archive evidence records successful object compilation and archive creation. These checks do not establish that the runtime source compiles or links. No CMake patch was applied because the required local configure tool and raylib dependency were not present, and this CMake project has no raylib-free runtime target.

Concrete next build plan: use an already-local CMake and raylib source tree; configure the pinned runtime with `PS2X_BUILD_RUNTIME=ON`, other app targets off, `PS2X_ENABLE_DEBUG_UI=OFF`, and `PS2X_ENABLE_FFMPEG=OFF`; keep FetchContent disconnected; add the 17 existing generated arm64 objects as external object sources to the runner link; build/link only and do not launch. Static objects are preferred for the test because runtime and generated archives reference each other through the table globals and `PS2Runtime` methods. A passing link would prove only ABI/link compatibility on the matched macOS arm64 configuration.
