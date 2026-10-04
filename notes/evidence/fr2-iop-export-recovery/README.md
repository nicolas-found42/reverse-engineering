# Relocation-backed IOP export entries

The literal export-table reader treats the first zero word as a terminator. In the pinned 24-module IRX corpus, 13 such words are also exact `.rel.text` relocation sites with `r_info == 0x2`: `R_MIPS_32`, symbol index zero, and raw addend zero. The loader's relocation arithmetic adds the selected image base to that word, so a raw zero at one of these sites is a pointer addend in the modeled image rather than an unrelocated terminator. The site audit continues only across those exact type-2/symbol-zero words and stops on a zero without a relocation.

That deterministic scan finds 746 export pointer entries in 28 tables, versus 296 entries exposed by the literal scan. It recovers 450 entries hidden behind the 13 relocation-backed zeros. All 746 slots have the expected `.rel.text` `R_MIPS_32` symbol-zero record. At every table's stopping zero, no relocation is present. The 13 zero-pointer positions independently match the parent's relocation-aware crosswalk by SHA-256 for all 24 modules and exact `.text` offsets.

| Module | Library/version | Table offset | Zero-pointer ordinal | `.text` relocation site |
| --- | --- | ---: | ---: | ---: |
| CDVDMAN.irx | cdvdman / 257 | `0x9b80` | 0 | `0x9b94` |
| EESYNC.irx | eesync / 257 | `0x190` | 0 | `0x1a4` |
| IOMAN.irx | ioman / 260 | `0x1ca0` | 0 | `0x1cb4` |
| LOADCORE.irx | loadcore / 259 | `0x1cb0` | 0 | `0x1cc4` |
| MODLOAD.irx | modload / 262 | `0x2db0` | 0 | `0x2dc4` |
| SIFMAN.irx | sifman / 257 | `0xf20` | 0 | `0xf34` |
| STDIO.irx | stdio / 259 | `0x50` | 0 | `0x64` |
| SYSCLIB.irx | sysclib / 259 | `0x80` | 0 | `0x94` |
| THREADMAN.irx | thbase / 258 | `0x67b0` | 3 | `0x67d0` |
| TIMEMANI.irx | timrman / 259 | `0xda0` | 0 | `0xdb4` |
| SDRDRV.IRX | sdrdrv / 257 | `0xea0` | 0 | `0xeb4` |
| SIO2MAN.IRX | sio2man / 515 | `0xc30` | 4 and 27 | `0xc54` and `0xcb0` |

The table and ordinal locations are relative to each module's base-zero `.text`; they are not runtime addresses. `R_MIPS_32` symbol-zero arithmetic is modeled at an explicit synthetic base only. This establishes pointer-slot structure for the measured file profile; it does not resolve export names, prove module registration or load order, establish actual IOP addresses, or prove runtime import binding.

The metadata-only per-site receipt is [zero-export-site-audit.json](zero-export-site-audit.json); its independent Jev result is [jev-zero-export-verify.json](jev-zero-export-verify.json). The reproducible scanner and source/executable hashes are recorded by [index.json](index.json). The full crosswalk result remains in ignored scratch at [the pinned parent result](../../../.scratch/mesh/codex-root/iop-crosswalk-relocated-corpus-01/20261004T131815Z-9f7349ab06714a37b86fbca21b751331/result.json); this note does not duplicate its import-candidate graph.


## Export targets against the saved Ghidra listing

A second bounded analysis joins all 746 relocation-aware export pointers to the strict, same-raw-SHA Ghidra listing inventories. It uses an explicit synthetic base of `0x1000` only to exercise the static relocation model, then subtracts that base to compare section-relative targets. The result classifies 427 export entries at saved function entries, 162 at unowned decoded instructions, and 157 in undefined `.text` bytes. Among the 450 formerly hidden entries, the split is 246, 114, and 90 respectively. These are entry counts; duplicate module/target pointers mean there are 555 unique module-target pairs.

The target-by-target receipt and Jev verification are [relocated-export-listing-correlation.json](relocated-export-listing-correlation.json) and [jev-relocated-export-listing-verify.json](jev-relocated-export-listing-verify.json). The reproduction script and its hash are in [index.json](index.json). Jev verified the three count claims and rejected the runtime/callability overclaim. This is a coverage join, not a claim that every export is a function or that a Ghidra code unit is decoded correctly.

## Provisional recovery of export targets

Using the relocation-aware 746-entry export view, an isolated copy of the analyzed 24-module Ghidra project was extended with provisional candidates. The run preserved all 2,241 preexisting function entry/name/body rows and initialized memory, then added 13 metadata-entry candidates, 40 candidates at already decoded unowned instructions, and 94 bounded candidates from previously undefined export targets. Of 95 unique undefined target seeds, one was rejected: SYSCLIB offset `0x1004` flowed into a defined-data collision at `0x1080`. The 94 accepted bounded candidates added 1,180 instruction starts (4,720 bytes). All 24 final listing inventories had non-overlapping function body ranges.

The final scratch export produced 2,388/2,388 C files with zero failures. Nine preexisting C artifact hashes changed (2,232 remained identical). Four changes are the previously documented base-zero entry-label versus null-pointer presentation changes; five additional changes affect GP presentation in THREADMAN/MODLOAD and decompiler expression/types in LIBSD. These changes are recorded without claiming semantic equivalence. Warning comments changed from 91 to 106; this is an output diagnostic count, not a completeness score.

The durable bounded result and exact Jev receipt are [target-recovery-union.json](target-recovery-union.json) and [jev-target-recovery-verify.json](jev-target-recovery-verify.json). The full function C files and Ghidra project remain in ignored scratch; the static union receipt, per-module inventories, candidate receipts, and C hash audit are referenced by path and SHA-256 in the durable result. Jev verified the count and disposition claims and contradicted the claim that static export provenance proves runtime invocation or original symbol identity.

This run is limited to static export-slot provenance, bounded Ghidra listing edits, and decompiler output. Candidate names and extents are provisional CFG results. It does not establish exact original function boundaries, correct decoding, symbol names, module registration, runtime reachability, behavior, or source semantics. The earlier multi-seed transaction run is preserved as superseded: a rejected seed in one process rolled back preceding accepted edits, which is why the final union uses a separate saved-program open per undefined seed.


### Per-seed invocation guard

The undefined-target script now requires an explicit target offset whenever the module has more than one unique undefined target, before the candidate loop or any transaction. Its class comment now says to use a copied writable project with `-noanalysis`; accepted candidates are persisted, so `-readOnly` is incorrect for that script. A fresh SYSCLIB negative invocation omitted the target and hit the exact guard error. The read-only coverage JSON before and after was byte-identical (23 functions and identical function/block rows), and no candidate receipt was written. Ghidra headless returned status 0 even though it logged the script exception; the negative test checks the exact exception text plus unchanged coverage. See [negative-multiseed-guard.json](negative-multiseed-guard.json). The prior 2,388-function union and its original run manifest were preserved; its per-seed runner already supplied one selected target for every undefined-seed invocation. The one-shot Jev gate is [jev-single-seed-guard-gate.json](jev-single-seed-guard-gate.json); it escalated because its claim list included the false statement that the union had been regenerated. No retry was made.

Root validation recomputed all 2,388 generated C file hashes against their manifests, reconciled the 24 raw input hashes and reopened coverage entry sets, checked preservation of prior entry/name/body rows and initialized memory, and independently checked all body intervals for overlaps. The nine old C hash changes remain explicit. The negative-test excerpt omits the logger’s `HeadlessAnalyzer` prefix; the full log hash and exact exception payload match. The one-shot guard gate’s false regeneration claim remains rejected. See [root-union-validation.json](root-union-validation.json).
