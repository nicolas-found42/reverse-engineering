# Ford Racing 2 evidence pipeline — issue #2

This evidence is for the unchanged PAL SLES-517.05 corpus identified in `index.json`. Static, runtime, and format verification are separate commands. Each creates a new immutable UTC/UUID directory with `result.json` and `report.md`: `pass` exits 0, `fail` exits 1, and missing prerequisites or unresolved required observations produce `incomplete` and exit 2. Prior runs are retained. Run from the repository root with Python 3.14; no third-party Python dependency is needed for these checks.

## Three verification commands

```sh
python3 tools/verify_static.py \
  --export .scratch/evidence/static-export.json \
  --loader-map notes/evidence/fr2/loader-map.json

python3 tools/verify_runtime.py \
  --captures .scratch/evidence/captures/capture-070130502b3f4c228bfdca3e2bbca221/captures.json \
  --pcsx2-executable "$PCSX2_EXECUTABLE" --firmware "$LOCAL_FIRMWARE"

python3 tools/verify_formats.py corpus games/ford-racing-2
```

`PCSX2_EXECUTABLE` and `LOCAL_FIRMWARE` denote the local files whose lengths/hashes are in `runtime-result.json`, not credentials or downloadable inputs. Runtime verification is offline replay: it checks recorded memory, entry/branch/exit states, code bytes against ELF load segments, full output, and source/tool/firmware provenance. It neither starts PCSX2 nor counts as a fresh capture. Public runtime metadata cannot substitute for the local binary artifacts; absence yields `incomplete`. Static needs the complete local export; `functions.tsv` is the full public inventory and `loader-instructions.json` is a bounded selection of full loader/consumer bodies, not a substitute for that complete export.

For individual synthetic or researcher-supplied inputs, use `verify_formats.py archive HDR DAT`, `bank MSH MSB`, `model PS2`, or `sprite PTG`. All commands accept `--output`. Static/runtime `--synthetic` is explicitly ineligible for real milestone acceptance.

## Static export and interpretation

The successful exporter reads the existing saved program without analysis, saving, Python/PyGhidra, or native decompilation:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk \
  .scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC/support/analyzeHeadless \
  "$PWD/ghidra-project" fr2 -process SLES_517.05 -noanalysis -readOnly \
  -scriptPath "$PWD/tools/ghidra" \
  -postScript ExportEvidence.java "$PWD/.scratch/evidence/static-export.json"
```

Measured environment: Ghidra 12.1.3, Homebrew OpenJDK 27, Emotion Engine extension 2.1.37, language `r5900:LE:32:default`, macOS 26.4.1 arm64. The log reported `EVIDENCE_EXPORT_OK functions=3446 inventory=3446`. All entries are exported, including callers, callees, basic-block ranges, instruction bytes/references, memory blocks, and defined strings with xrefs. The original native decompiler is unavailable; no recovered C or complete source types are claimed.

`loader-map.json` identifies initialization, lookup, chunk read, raw transfer, decompression, and consumption. It binds the full export/executable, cited instruction bytes, both full Jev audits, independent reasoner review, and clean archive-table correlation by SHA-256. The runtime dispatch at `00107ce0` selected async raw `001069f0` and async compressed `00106ef8`; synchronous alternatives `001067f8`/`00106c48` remain separate entries. Actual caller returns `0022e014` and `0022ac68` are captured before those next instructions execute. Full bodies and references show subsequent consumer use. All 48 runtime segment pairs and 1,037 runtime records were independently compared with HDR fields: runtime segment stride 20, record stride 28, and archive chunks plus FILES.DAT base LBA 125000. Bytes after the first name NUL are uninitialized on disk and differ in RAM.

Jev is advisory. `loaderJudgment.json` retains original inputs and complete results; four stages received auto actions and initialization/lookup needed review. `tableJudgment.json` retains the second audit with new full context and exploratory table evidence; its two review actions remain visible. `reasoner-review.json` resolves the required claims against complete instruction bodies and clean runtime observations without relabeling Jev's outputs as automatic approval. A contradicted required verdict always stops verification. Thresholds remain at 0.8; this is a bounded case study, not empirical calibration of the judgment model. The screen audits record inspected issue/vendor sources. [judgment-dispositions.json](judgment-dispositions.json) records their dispositions and explicitly corrects the inaccurate headless premise in the original register-screen input while preserving that audit unchanged. The early mutated exploratory capture was excluded; no acceptance capture contains that mutation.

## Fresh capture procedure and its window behavior

The recorded runs were **unattended debugger captures, not headless**. PCSX2's `-nogui` hides its main window; opening the debugger to install saved breakpoints still creates windows and can take focus. Null rendering does not prevent that. The remaining verification commands run without windows. Do not run capture while someone needs an undisturbed desktop.

```sh
python3 tools/capture_runtime.py --allow-debugger-windows --firmware "$LOCAL_FIRMWARE"
```

The capture command is bounded to the measured macOS PCSX2 v2.6.3 build and savestate layout. It uses the existing PCSX2 profile, checks that no PCSX2 session is active, takes an exclusive preference lock, temporarily enables PINE slot 28031, disables patches/cheats, selects the null renderer, and installs saved conditional breakpoints. It restores the exact original preferences, breakpoint file, and save-slot contents after each owned process has exited, including ordinary failure paths. A forced process kill can prevent cleanup; the lock then marks unfinished ownership. The command requires `--allow-debugger-windows` so its UI behavior is explicit. Other operating systems/builds and a completely windowless capture mode are unverified.

Each repeat starts from a separate cold boot, with no controller actions. Stop at dispatch `00107ce0` with `a2 == 0` and a filename pointer in guest RAM. Save entry; restart from it to raw branch; save branch; restart to the actual entry `ra`; save exit. Then continue from that raw exit to the first compressed dispatch (`a2 == 1`), and repeat branch/return capture. Repeat the entire boot sequence once more. Entry filename bytes choose the exact archive record. PINE status must remain paused, guest ELF code must be present, and independent PINE memory reads must match saved EE bytes. Opcode 9 only acknowledges scheduling a save; the script waits for a newer complete ZIP before using it. Twelve complete snapshots bind entry, branch, and exit for four events; four full 32 MiB exit memories and full logical outputs remain local.

| Path / record | Branch PC | Return PC | Guest output | Logical length |
| --- | --- | --- | --- | --- |
| `/FONTS/fontbase.dat;1` / 311 | `001069f0` | `0022e014` | `00397e80` | 1,032 |
| `/GRAPHICS/LOADING/LOGO_EMP.ptg;1` / 830 | `00106ef8` | `0022ac68` | `00748e80` | 332,320 |

Both repeats match the complete independent DAT extraction length and SHA-256. No pre-comparison transformation is applied. Savestate `eeMemory.bin` indexes are guest addresses; host virtual addresses are never used. Full memory and state hashes differ between repeat events while output hashes match. `runtime-captures.json` publishes metadata, register values, code snippets, and hashes only. Media, firmware, payloads, complete memory and private emulator settings are excluded from version control.

The PINE and register-layout adapter derives from the official [PINE.cpp](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2/PINE.cpp), [SaveState.cpp](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2/SaveState.cpp), [R5900.h](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2/R5900.h), and [QtHost.cpp](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2-qt/QtHost.cpp). Saved breakpoint serialization follows [DebuggerSettingsManager.cpp](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2-qt/Debugger/DebuggerSettingsManager.cpp) and [BreakpointModel.cpp](https://github.com/PCSX2/pcsx2/blob/v2.6.3/pcsx2-qt/Debugger/Models/BreakpointModel.cpp). PINE commands used are reads/status/identity and save; no memory writes, patches, stubs, or load commands are sent through PINE.

## Supported format contracts

All integer words are little-endian u32; all reported spans are half-open byte ranges. The source hashes select one profile; changed media/ELF/HDR/DAT fail corpus verification. All 990 extracted files are compared by full SHA-256 with an independent archive read and by record/path/length/classification with the historical manifest.

* Archive: segment count, `(count, first)` pairs, **separate record count**, and 28-byte records. Segment partitions must be exact; directory cycles, repeated/unreachable segments, unsafe/duplicate paths, invalid sentinel/index values, short/overlapping DAT spans, and invalid names fail. Names terminate within 16 bytes; the remaining bytes are retained as unknown data. `u1` is a 2,048-byte chunk index and `u2` a stored byte length. The measured compressed marker is a u32 logical length followed by a recognized zlib header. Decompression requires exact bounded length, EOF, and only zero trailing padding; a corrupt/truncated recognized wrapper fails. Output is bounded to 128 MiB. Unrecognized markers are raw under this profile, not a universal codec detector. DAT gap spans/digests remain visible.
* Bank pair: MSH header is self-size, unknown word, nonempty descriptor count; descriptors are 16 bytes `(length, unknown, start, rate)`. Descriptor tails are at most 64 zero bytes. Sample spans form an exact consecutive chain covering MSB; all rates, including 16000/20000/22050, remain data. No payload codec or playback claim.
* Model: leading count stays unresolved; nonempty root name-offset array and group arrays must end exactly at the minimum referenced string offset. Every referenced name has an in-range printable NUL-terminated span of 1–60 characters. Remaining geometry is retained by range/hash, not decoded.
* Gear sprite: eight-word header with count 1, cell 32, final word 1, positive dimensions within stride; a complete 1,024-byte E3/E3/E3/index table with bits 3 and 4 exchanged; exact row bounds and DD row/allocation padding. Unknown header/prefix values are retained; the table's role stays unknown. Pixel hashes use the unscaled decoded width×height buffer. Gear0 is uppercase R and gear1 uppercase N; other meanings remain unassigned.

The final coverage report accounts for 48 segments, 1,037 records, 990 files (604 zlib / 386 raw), 27 bank pairs, 56 model trees, all eight gears and all 548 PTG files. The bounded sprite profile supports 16 PTG files; 532 are individually listed as unsupported with diagnostics. This does not imply general PTG, audio, or geometry decoding.

## Tests, review, and evidence index

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
pyright tools/evidence_common.py tools/format_contracts.py tools/corpus_contract.py \
  tools/judgment_contract.py tools/pcsx2_pine.py tools/capture_runtime.py \
  tools/verify_static.py tools/verify_runtime.py tools/verify_formats.py \
  tools/test_evidence_pipeline.py tools/extract_tree.py tools/msh_verify.py \
  tools/ps2_pairs2.py tools/ptg_render.py
```

Synthetic CLI tests check reports, status and exit codes, beyond-200 inventory coverage, omissions, malformed formats, complete outputs/repeats, stale source/capture identities, semantic uncertainty/contradictions/API errors, reasoner resolution and changed export bindings. The full local discovery run used the existing `.scratch/modern-re-research/sdk-venv/bin/python` (Python 3.12.14), because five pre-existing, untracked research tests require `typesafe_sdk`; it passed all 15 tests. The committed evidence suite has 10 tests and also passed on Python 3.14.7. Pyright checked all changed Python files with zero errors. The optional legacy PNG renderer still needs Pillow; the evidence checks do not. Synthetic successes are explicitly ineligible for milestone acceptance. Real integration results are separate `*-result.json` files. The public index links their exact original result/report hashes and safe textual copies; `.scratch/evidence/index.json` additionally locates the original local artifacts. Reviews and final Jev completion judgment are retained with dispositions; an AI gate does not execute tests. The valid final Jev gate returned `escalate`, with six verified claims, no contradictions, and low confidence in three claims and patch test/blast-radius scores. This is not automatic approval. The initial larger request returned an API400 error; that operational result is retained separately. The independent [completion reasoner review](completion-reasoner-review.json) accepted all six claims and six core file reviews within stated limits and found no supported correctness defect. It is recorded separately from Jev's unchanged action. The snapshot files retain the exact index/disposition bytes inspected before this final disposition was added. [restoration-check.json](restoration-check.json) records the final read-only emulator cleanup check.
