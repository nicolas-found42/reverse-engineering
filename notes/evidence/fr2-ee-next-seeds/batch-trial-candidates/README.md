# Bounded static recovery checkpoint: batch `trial` (6 functions)

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV5.java`, schema-2 config `config.json`) on a fresh byte-identical copy of the 3863-function project. It added **6** provisional functions (124 raw ELF-matched instruction words; 101 were already decoded as unowned instructions and the rest newly decoded), taking the function count to **3869**.

Evidence per seed: 0 seeds have at least one direct JAL from decoded code (0 incoming call sites in total); 6 seeds have no direct call and are PS2Recomp function-table leads whose structure passed the same raw CFG validation. 2 non-call references into entries (for example PARAM address-taken references from saved functions) were recorded and verified unchanged. 0 call targets remain unresolved (uncreated), so the set is not call-closed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): every seed's span, edges, calls, zero words, coverage states and all incoming JAL sites.
- Transaction `EE_BATCH_CANDIDATES_OK`; in-guard checks: old instructions/data/memory/functions unchanged, listing delta equals exactly the newly decoded words, global reference additions equal exactly the raw CFG flow edges of newly decoded words, per-seed reference partition (entry calls / intra-span branches / non-call refs), full call-graph equality against the config prediction, unresolved callees uncreated, next-word states.
- Read-only reopen and export: 3869 generated, 0 failed, 607 warning comments; reusable verifier passed.
- Reconciliation `16/16` (`reconciliation.json`); root rehash of all C artifacts passed (`root-export-check.json`).
- The V5 guard review escalated (safe_to_apply 0.11); root's disposition is in `jev-review-v5-result.json`. Failed earlier V5 runs (rolled back, with the guard changes they caused) are in `failed-attempt-*`.

No function identity, behavior, runtime reachability or original boundary is claimed. Generated C and Ghidra project copies stay in ignored scratch.
