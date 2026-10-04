# Bounded static recovery checkpoint: batch `g1` (412 gap-fill functions)

One isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV5.java`, schema-2 config `config.json`) on a byte-identical copy of the 4,718-function project. It added **412** provisional functions (14,953 raw ELF-matched instruction words, 59,812 bytes), taking the function count to **5,130**.

These candidates do not come from the PS2Recomp function table. They are **gap-fill** seeds taken from executable bytes that no saved function owned:

1. `tools/verify_text_denominator.py` splits the 195,812 unlisted executable bytes into structural classes (zero fill 17,576; code-shaped 164,512; VU microcode 13,584; sparse 140).
2. `tools/verify_text_references.py` finds static references into the 503 code-shaped spans: 62 anchored, 8 reached only through anchored spans, 433 with no static reference.
3. `tools/gap_seeds.py` derives 1,186 deterministic seeds; the existing batch guard walk accepts 641 (101,132 bytes).
4. `tools/verify_gap_candidates.py` tiers them by independent evidence classes (stack-frame consistency, boundary layout, static reference). Tier A (two or more classes) has 433 candidates (74,800 bytes); B 173; C 35. Candidate frame results match the saved-function control (frame inconsistent 2 of 641 against 3 of 3,670). Jev chose tier A at 0.79 (confidence 0.74); the earlier decision over the raw sets had confidence 0.23 and is recorded as such in `jev-decisions.json`.
5. `iterate_batch.py` ran the batch guard three times, excluding 21 seeds, and created 412 functions on the fourth.

All 412 have **no known incoming direct caller**. Their evidence is a closed raw-word control-flow walk, frame consistency, layout (149 end at a saved entry, 113 at another candidate) and, for some, a static reference. No function identity, behavior, runtime reachability or original boundary is claimed.

## Result

| Measure | Before (4,718) | After (5,130) |
| --- | ---: | ---: |
| Function-owned executable bytes | 1,051,516 (84.3%) | 1,111,328 (89.1%) |
| Code-shaped unlisted bytes | 164,512 in 503 spans | 103,776 in 354 spans |
| Spans anchored / via anchored / unreferenced | 62 / 8 / 433 | 58 / 7 / 289 |
| Decompiler API failures | 0 | 0 |
| Warning comments | 620 | 685 |

## Verified

- Config re-derived independently from the ELF (`root-config-check.json`).
- Transaction `EE_BATCH_CANDIDATES_OK`; old function snapshot, initialized memory and defined data preserved.
- Read-only reopen and export: 5,130 generated, 0 failed; reusable verifier passed (`verifier-summary.json`).
- Reconciliation 16/16 (`reconciliation.json`); root rehash of 9,848 C artifacts passed; four prior C files changed, each only by seed label substitution, line re-wrap, retyping of undefined types, auto-variable prefix renames and pointer-label renames, and each mentions a seed (`reconciliation.json`).
- Jev verify: six claims verified, the overclaim "identified as the original game functions" contradicted at 0.99 (`jev-verify-result.json`).

## Not established

The guard escalations of earlier batches are unchanged. 21 seeds were rejected by the guard (PARAM references into a span interior, decoder delay-slot mismatches, one span arithmetic mismatch); see `failed-attempt-*`. Tiers B and C (208 candidates) are held. 289 code-shaped spans with no static reference remain. Generated C and Ghidra project copies stay in ignored scratch.
