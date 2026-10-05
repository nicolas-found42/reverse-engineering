# Bounded static recovery checkpoint: batch `g3` (211 functions)

One isolated Ghidra transaction (guard `CreateEeCandidateV5.java` as of commit `0a97358`) on a byte-identical copy of the 5,243-function project. It added **211** provisional functions (6,338 raw ELF-matched instruction words) and took the count to **5,454**.

Seeds were the 215 candidates of tiers A, B and C from the gap-fill pool after batch g2, minus the two `frame_inconsistent` candidates and the 21 seeds the g2 guard had rejected. Tiers B and C were included because the hold-out measurement (`tools/holdout_gap_method.py`, `holdout-seed*-g2-export.json`) found the batch guard walk itself carries the precision: over three seeds, 2,202 saved functions with no listed caller were held out, 85.4% came back with the exact start and end, and 99.7% of candidates inside the removed bodies were exact (frame-only 93 of 94, layout-only 7 of 7). The ground truth is saved functions, themselves provisional. The Jev decision (`jev-decisions.json`) had confidence 0.63.

The guard rejected three iterations (seeds `00123cc0`, `001796b0` and `001802e8` with seed-tagged failures; then an untagged failure, `unresolved outgoing callee was created/claimed at 0020fa68`, after which root excluded the only seed calling it, `0020ca60`) and the next run created 211 of 215 seeds (`failed-attempt-*`, `iterate.log`, `iterate2.log`).

| Measure | Before (5,243) | After (5,454) |
| --- | ---: | ---: |
| Function-owned executable bytes | 1,114,672 (89.4%) | 1,140,024 (91.4%) |
| Code-shaped unlisted bytes | 100,344 | 73,756 |
| Spans anchored / via anchored / unreferenced | 54 / 7 / 259 | 56 / 7 / 155 |
| Decompiler API failures | 0 | 0 |
| Warning comments | 720 | 757 |

## Verified

Config re-derived independently (`root-config-check.json`); transaction passed; export 5,454 generated, 0 failed (`verifier-summary.json`); reconciliation 16/16 (`reconciliation.json`, `root-export-check.json`). Jev verify: four claims verified (one flagged `review` at 0.72 for awkward wording, clarified above), the overclaim "the 211 functions are the original game functions" unsupported with relation contradicted at 0.93 (`jev-verify-note.json`).

## Not established

No function identity, behavior or runtime reachability. The 56 anchored spans (52,524 bytes) that remain are blocked by guard limits (computed jumps, gaps with code, flow into saved functions) rather than by missing evidence. Generated C and project copies stay in ignored scratch.
