# Bounded static recovery checkpoint: batch `g2` (113 functions, including the kernel syscall stubs)

One isolated Ghidra transaction (guard `CreateEeCandidateV5.java`, now allowing `syscall` as a non-terminating instruction; see commit `0a97358`) on a byte-identical copy of the 5,130-function project. It added **113** provisional functions (836 raw ELF-matched instruction words) and took the count to **5,243**.

Seeds were the 134 tier A candidates of the gap-fill pipeline (`tools/gap_seeds.py`, `tools/verify_gap_candidates.py`); the batch guard excluded 21 over three rejected iterations (`failed-attempt-*`, `iterate.log`). The guard change matters because the EE kernel library's syscall stubs (`addiu v1,zero,N; syscall; jr ra; nop`) were rejected as traps before: all **162** stubs the scanner finds are now saved functions (61 before this batch). `tools/verify_syscall_stubs.py` reads the pinned PS2SDK `syscallnr.h` (commit `ac92a9f657d2…`, header sha256 `573f0c32…`): 154 of 162 stub numbers have a candidate name, 15 stubs have more than one SDK name, and 8 numbers are absent from the table. Names are candidates only: the game's kernel library carries the stamp `PsIIlibkernl2550` (SDK 2.5.5 family) and commercial SDK syscall numbering is reported to differ from the open SDK in places. None is applied to Ghidra here.

| Measure | Before (5,130) | After (5,243) |
| --- | ---: | ---: |
| Function-owned executable bytes | 1,111,328 (89.1%) | 1,114,672 (89.4%) |
| Code-shaped unlisted bytes | 103,776 | 100,344 |
| Spans anchored / via anchored / unreferenced | 58 / 7 / 289 | 54 / 7 / 259 |
| Decompiler API failures | 0 | 0 |
| Warning comments | 685 | 720 |

## Verified

Config re-derived independently (`root-config-check.json`); transaction passed; export 5,243 generated, 0 failed (`verifier-summary.json`); reconciliation 16/16 and a rehash of the C artifacts (`reconciliation.json`, `root-export-check.json`). Jev: four claims verified, the overclaim "stub names are verified original symbols" contradicted at 1.00 (`jev-verify-result.json`). The guard change was reviewed by `jev_review`, which escalated (safe_to_apply 0.25, test gap); the walker decode now has a test that fails without the change (`tools/test_pipeline_walker.py`), and this batch is the run that exercised it.

## Not established

No function identity, behavior or runtime reachability. The 21 rejected seeds and tiers B and C were held for batch g3. Generated C and project copies stay in ignored scratch.
