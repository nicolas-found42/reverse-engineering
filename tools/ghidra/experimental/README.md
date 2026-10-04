# Guarded Ghidra duplicate target experiment

These files are an experimental supplement for the single PAL `FUN_0017f510` switch. They were tested with Ghidra 12.1.3 in a private copy. They are not a general fix for backward normalization and must not be applied to the installed baseline release as part of ordinary export.

`VerifiedJumpTableOverride.java` checks the exact game executable SHA-256, table bytes, computed branch, loop domain, and argument-setting opcodes before writing an override. It retains all seven table occurrences, including the shared destinations at indices 3 and 6. It then requires eight assertions about the generated C and writes a supplemental manifest in a fresh output directory. Run it only against a copied project. Headless `-readOnly` discards the in-memory project changes after export.

The script also requires the R5900 language, a dispatch instruction inside the retrieved function body, and the exact tested private native decompiler hash. Its manifest binds the native binary, Java script, native patch, executable, and generated C hashes. The baseline native tool was rejected by the guard and produced no C or manifest. The provenance-hardened positive run produced the same C hash as the earlier full export.

`ordered-jumptable-override.patch` changes the native decompiler to retain and check order only for override arrays that contain duplicate destinations. Unique-address arrays retain the previous unordered set algorithm. The list persists through clone, encode, and decode. The source baseline is the Ghidra 12.1.3 release's `Ghidra/Features/Decompiler/src/decompile/cpp`; hashes are `c8bf07367f23f827e0d290bb6bfb3c2ef9db67e2c9543931203b6b627892b7fe` for `jumptable.cc` and `3d26746eab3763dd76a15082105e928fca81abf06f828cee44a0b3da0e682ad6` for `jumptable.hh`.

Apply the patch in an isolated source copy and build `ghidra_opt` with `make -j8 ghidra_opt CXX=clang++ ARCH_TYPE= OSDIR=mac_arm_64`. Place the result in an isolated release copy's native decompiler location. The tested private binary hash is `cd6d7e92061f7e47c7eaa86f82cb7045b4c3e624d1764832283f00b8dca57acd`.

Duplicate, permuted unique, deliberately mismatched duplicate, and saved-project-reopen regressions passed. A read-only full export with the guarded override generated all 3,837 saved functions. There were still 608 warning comments. The Jev review escalated with `safe_to_apply=0.17`; that result is preserved and is not approval. The bounded result and independent review do not establish generic patch correctness, exact source recovery, or whole-program equivalence. See the repository's static-recovery evidence for manifests, hashes, historical failures, and remaining coverage gaps.

## Two additional dispatch experiments

`VerifiedDispatchPairOverride.java` is a separate bounded experiment for two computed dispatches. It requires the same PAL SHA-256, R5900 language, patched-native SHA-256, and ordered-patch SHA-256. A normalized self-hash pins the script source, and the script also pins the 3,837-entry baseline decompilation-manifest SHA-256. It checks that the existing function-entry set is unchanged before and after each run. It validates the selector bounds and every raw table target for `001fbe48` and `001161a8`; the latter additionally pins the 95-entry table byte hash and its two-target index mapping. The script checks for competing function ownership and overlapping instructions. It decodes with control-flow following and automatic code analysis disabled, restricts every decode to the exact target span `001fbef8..001fbf7f`, then compares the complete listing before and after: only 29 previously undefined instructions at `001fbf0c..001fbf7c` may be added. It also checks every initialized-block data code unit remains unchanged and enforces the full `.text` coverage totals before and after, alongside all 3,837 original function entries, unchanged initialized memory, and body growth of 232→368 bytes and 968→976 bytes. The first five instructions `001fbef8..001fbf08` were already decoded and unowned; the two table entries at `001fbf3c` and `001fbf60` point within the same allowed span. The script records all body and listing deltas and exports the two target C files plus a supplemental manifest. Follow it with `ExportEvidence.java` and `ExportCoverage.java` in the same read-only headless invocation to produce the post-experiment inventory and coverage summary.

Run `positive` and `permuted` modes in separate invocations against separate pristine copies of the 3,837-function project with `-noanalysis -readOnly`. For each mode, pass a new output directory, the pinned baseline manifest, and the patch file, then run both inventory and coverage exporters:

```sh
support/analyzeHeadless <copied-project> fr2 -process SLES_517.05 -noanalysis -readOnly \
  -scriptPath "<repo>/tools/ghidra/experimental;<repo>/tools/ghidra" \
  -postScript VerifiedDispatchPairOverride.java positive <fresh-positive-output> \
  <repo>/.scratch/mesh/codex-root/decompile-guarded-3837-01/manifest.json \
  <repo>/tools/ghidra/experimental/ordered-jumptable-override.patch \
  -postScript ExportEvidence.java <fresh-positive-output>/inventory.json \
  -postScript ExportCoverage.java <fresh-positive-output>/coverage.json
```

Repeat with `permuted` and a separate fresh output path. The positive mode supplies the raw five-target sequence for `001fbe48`, including the duplicate final target, and the exact 95 target words for `001161a8`. The permutation negative control swaps target indices 1 and 2 only for `001fbe48`; it must fall back to pointer-table switch pseudocode. The `001161a8` table remains exact in both runs. Its positive output removes the failed synthetic case label and retains the bounded indexed pointer-table switch with its two verified executable targets. The experiment does not claim runtime reachability, original source identity, or whole-program equivalence.

The earlier broad `disassemble(target)` prototype decoded 2,876 extra instructions in 22 unrelated intervals; that failed run is retained as a superseded scratch receipt. The current script rejects any listing delta beyond the 29 exact new instructions in the table-target span, checks their raw bytes and all pre-existing instruction bytes, and hashes initialized memory before and after. Five other body additions at `001fbef8..001fbf08` and two at `00116510..00116514` were already decoded but unowned. Thus, the two bodies gain 36 instructions total (144 bytes), while the global listing gains only 29 instructions (116 bytes). The C hashes differ under the deliberate permutation for `001fbe48`; the `001161a8` C hash remains stable because its table is unchanged. The 608 warning-comment count was reconciled against the recorded ordered comment pairs; an earlier ad hoc scan had missed one warning.

To export all 3,837 functions from the same isolated patched project, use a fresh project copy and fresh pair/full-C output directories. The command below applies the singleton seven-entry override first and the two dispatch-pair overrides next, then exports the complete generated-C inventory, saved-function inventory, and listing coverage in one read-only process:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk@27 \
  .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless \
  <fresh-copied-project> fr2 -process SLES_517.05 -noanalysis -readOnly \
  -scriptPath "$PWD/tools/ghidra/experimental;$PWD/tools/ghidra" \
  -postScript VerifiedJumpTableOverride.java <fresh-singleton-output> \
  -postScript VerifiedDispatchPairOverride.java positive <fresh-pair-output> \
  "$PWD/.scratch/mesh/codex-root/decompile-guarded-3837-01/manifest.json" \
  "$PWD/tools/ghidra/experimental/ordered-jumptable-override.patch" \
  -postScript ExportDecompilation.java <fresh-full-c-output> 30 \
  -postScript ExportEvidence.java <fresh-full-c-output>/inventory.json \
  -postScript ExportCoverage.java <fresh-full-c-output>/coverage.json
```

For the recorded independent runs, the complete listing delta was exactly 29 instructions (+116 bytes); function bodies gained 36 instructions (+144 bytes), because seven were already decoded and unowned. All 36 body additions matched the PAL ELF `.text` bytes, and the 3,837 saved entry set remained unchanged. The positive and permutation-negative receipts, output hashes, exact coverage deltas, failed containment attempts, and broad-disassembly superseded intervals are preserved in ignored local scratch at `.scratch/mesh/codex-helpers/dispatch-pair-reproducibility-20261004-05.json` and `.scratch/mesh/codex-helpers/dispatch-pair-broad-disassembly-superseded-20261004.json`.

## Provisional unowned leaf candidate

An additional 72-byte unowned span at the start of executable `.user_section_uncommon` (`0x0022a180..0x0022a1c7`, file offset `0x0012b180`) has a balanced 16-byte stack frame, a complete `jr ra` return, and a stack restore in its delay slot. Its shifts and ORs support the provisional interpretation “four-byte RGBA value to A1R5G5B5-style packed word.” The only Ghidra incoming reference is imported ELF section-header metadata; raw scans found no aligned file-backed pointer, direct JAL/JALX, or conditional branch target. The candidate's original function identity, direct reachability, caller contract, and renderer use remain unproved.

`argb1555_candidate.py` is a pure `uint32 -> uint16` reference for that arithmetic hypothesis. `test_argb1555_candidate.py` checks the input domain, each channel's location and truncation boundaries, every possible 8-bit channel/alpha value, and combined channel values. These are synthetic arithmetic tests; they do not execute the original game bytes or establish the format interpretation. The isolated Ghidra reconstruction used `SourceType.ANALYSIS`, the explicit name `candidate_leaf_0022a180`, and exactly the existing 18 instruction words. It changed one saved function entry/body in memory only; full function-body ranges for the original 3,837 functions, instruction listing, defined data, neighboring ownership, and initialized memory were checked unchanged. The project ran `-readOnly`; its candidate C and 3,838-entry inventory remain local scratch at `.scratch/mesh/codex-helpers/leaf-candidate-reconstruction-20261004/`.

`CreateProvisionalLeafCandidate.java` is the reusable guarded version of that experiment. It requires the pinned PAL SHA-256, R5900 little-endian language, exact ELF section mapping, exact 72-byte file and loaded-memory span hashes, exact 3,837-entry baseline manifest, and verifies that the pre-candidate Ghidra entry set equals the manifest's entry set. It also checks all 18 pre-existing instruction words and the single imported ELF section-header DATA reference. It creates only `candidate_leaf_0022a180` over `0022a180..0022a1c7`; it never disassembles or changes memory. Before writing the isolated C/inventory/manifest outputs, it verifies every prior function body, instruction byte, defined data unit, initialized memory byte, reference, and neighbor owner remains unchanged. Its manifest records the active Ghidra version and the resolved native decompiler path and SHA-256 used for C generation; those values are metadata, not hardcoded acceptance pins. Run it only with a fresh copied Ghidra project and `-noanalysis -readOnly`:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk@27 \
  .scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC/support/analyzeHeadless \
  <fresh-copied-project> fr2 -process SLES_517.05 -noanalysis -readOnly \
  -scriptPath "$PWD/tools/ghidra/experimental" \
  -postScript CreateProvisionalLeafCandidate.java <new-output-directory> \
  "$PWD/games/ford-racing-2/extracted/SLES_517.05" \
  "$PWD/.scratch/mesh/codex-root/decompile-guarded-3837-01/manifest.json"
```

The pinned manifest must hash to `39302b3579c4c88f688a962fc794a6f9c6d652730c4f09794e7a40b29001192e`; output paths must not already exist. The generated candidate is not added to the saved project or whole-game export. Run the synthetic packing tests from repository root with `python3 -m unittest discover -s tools -p 'test_argb1555_candidate.py' -v`. The top-level shim exposes the focused experimental tests to the normal `tools/` discovery command.

The durable provenance and raw-reference audit are in `notes/evidence/fr2-static-recovery/discovery/leaf-candidate-reconstruction.md`, with machine-readable receipts beside it. Those records state the open identity and reachability questions and retain the Jev semantic-label review disposition.
