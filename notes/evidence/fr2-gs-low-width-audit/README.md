# Low GS buffer-width software audit

The actual pinned CPU upload backend matches its width-clamped table model in all eight synthetic transfers. The unmodified raw-width reference differs for zero-width CT32 and CT16 transfers; indexed widths zero and one retain a zero page-row stride in this backend. These are observed public-software differences. They do not establish which out-of-range widths physical PS2 hardware accepts or how the game renders them.

The probe uploads authored pixel labels at DBP33 into zeroed 4 MiB memory, covering two vertical pages in CT32, CT16, T8 and T4 at DBW0 and DBW1. It compares every output byte, including untouched memory: eight cases and 33,554,432 compared bytes. Every process returned zero with empty stderr. Each matching expected buffer also has a one-byte mutation detected by the comparison.

| Bits per pixel | Serialized DBW | Transfer dimensions | Bytes different from raw-width reference | Bytes different from clamped model |
|---:|---:|---:|---:|---:|
| 32 | 0 | 64×64 | 16,352 | 0 |
| 32 | 1 | 64×64 | 0 | 0 |
| 16 | 0 | 64×128 | 16,351 | 0 |
| 16 | 1 | 64×128 | 0 | 0 |
| 8 | 0 | 128×128 | 0 | 0 |
| 8 | 1 | 128×128 | 0 | 0 |
| 4 | 0 | 128×256 | 0 | 0 |
| 4 | 1 | 128×256 | 0 | 0 |

The software route matters. `GSCpuBackend::UploadImage` applies `max(DBW,1)` before its GSMem write handlers. GSMem computes page-row stride as `floor(effective_width×64/page_width)`. That gives one page for CT32/CT16 at width zero after clamping, and zero pages for T8/T4 at widths zero/one. The separate standalone address headers clamp indexed effective page widths to one, so their indexed results cannot be substituted for the actual CPU-upload results.

The standalone helper experiment checked 1,474,560 addresses across widths zero/one, six synthetic base blocks and two pages on both axes. It retained 663,552 disagreements with the raw-width table reference. A one-bit output mutant differed in every comparison; the helper probe ran under UndefinedBehaviorSanitizer with zero exits and empty stderr. The CPU-backend probe uses the saved public runtime libraries and makes no sanitizer claim. Its tested source files match the pristine pinned revision even though the library was built from the separate four-EE-patch experiment tree.

All 56 archive model entries were independently loaded through the SHA-bound baseline. Their 2,571 extra-mip records include 224 serialized DBW0 values: 30 CT32, 182 T8 and 12 T4. Nine records cross a vertical page boundary: four CT32 and five T8. One additional CT32 record crosses only horizontally and is unrelated to page-row stride. Applying the tested formulas to these records conditionally identifies the four CT32 vertical cases; it does not demonstrate actual uploads or texture corruption. See [the exact corpus metadata](corpus-zero-width-crossings.json).

The native probe links no generated guest objects or registration table. Its symbol preflight excludes all 4,746 saved guest entry names and display/audio initialization entry symbols. Source review covers the constructor, reset/initialization and direction-zero transfer path; the authored program performs memory uploads only. No original game routine, asset payload, generated runner, emulator, drawing call or hardware was executed.

Public references are PS2Recomp revision `c5a9d02573410a2085a4b4b831b0b68ba3515440` ([backend source](https://github.com/ran-j/PS2Recomp/blob/c5a9d02573410a2085a4b4b831b0b68ba3515440/ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp), [GSMem source](https://github.com/ran-j/PS2Recomp/blob/c5a9d02573410a2085a4b4b831b0b68ba3515440/ps2xRuntime/include/runtime/gs/ps2_gs_memory.h)) and PCSX2 revision `81526d4dc7cc70e4ae75abb35a789417456c6d43` ([GS tables](https://github.com/PCSX2/pcsx2/blob/81526d4dc7cc70e4ae75abb35a789417456c6d43/pcsx2/GS/GSTables.cpp)). Both are public GPL sources; no upstream source body is copied here. The probes are authored experiment harnesses that include/link those sources locally. Source pins, compiler arguments, library hashes and process records are in [backend-result.json](backend-result.json) and [standalone-helper-result.json](standalone-helper-result.json).

Jev screened the bounded public source excerpt and verified the three reported software/corpus claims. Two claims were automatic; the combined corpus/formula claim was flagged for review with confidence0.40. The root directly checked the backend source route, all eight full-memory comparisons and the SHA-bound record counts and retains the conclusion as conditional static analysis. No threshold was changed and no unchanged judgment was retried. The exact argument/result envelope is [jev-verify.json](jev-verify.json).

Two checker mistakes are preserved in scratch/history metadata: the first standalone probe declared a four-element width array with only two initializers, repeating width-zero cases and failing cardinality; the root’s first corpus tally counted both axes, exposing a tenth horizontal-only record before the corrected vertical-only tally. Neither erroneous result was promoted as passing evidence. Native binaries and large synthetic output buffers remain ignored.
