# Bounded static recovery checkpoint: batch `all-1` (477 functions)

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV5.java`, schema-2 config `config.json`) on a fresh byte-identical copy of the 3869-function project. It added **477** provisional functions (4803 raw ELF-matched instruction words; 2708 were already decoded as unowned instructions and the rest newly decoded), taking the function count to **4346**.

Evidence per seed: 1 seeds have at least one direct JAL from decoded code (1 incoming call sites in total); 476 seeds have no direct call and are PS2Recomp function-table leads whose structure passed the same raw CFG validation. 808 non-call references into entries (for example PARAM address-taken references from saved functions) were recorded and verified unchanged. 8 call targets remain unresolved (uncreated), so the set is not call-closed.
Seeds: 477 of 936 PS2Recomp function-table entries that were neither saved functions nor inside one and lay in .text. 455 were not created: dropped offline by the generator (200 had a branch from outside the span into the span, 110 had unreachable gap words, 101 had no JR RA at span end minus eight, 34 had computed jumps, traps or flow into saved functions, 5 overlapped another seed, 3 had an odd next-word state, 1 self-call, 1 other) or excluded after guard rejections (0015e898, 001710d8, 00180990, 001ed230: Ghidra direct-jump classification differed from the raw word).


## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): every seed's span, edges, calls, zero words, coverage states and all incoming JAL sites.
- Transaction `EE_BATCH_CANDIDATES_OK`; in-guard checks: old instructions/data/memory/functions unchanged, listing delta equals exactly the newly decoded words, global reference additions equal exactly the raw CFG flow edges of newly decoded words, per-seed reference partition (entry calls / intra-span branches / non-call refs), full call-graph equality against the config prediction, unresolved callees uncreated, next-word states.
- Read-only reopen and export: 4346 generated, 0 failed, 609 warning comments; reusable verifier passed.
- Reconciliation `16/16` (`reconciliation.json`); root rehash of all C artifacts passed (`root-export-check.json`).
- The V5 guard review escalated (safe_to_apply 0.11); root's disposition is in `jev-review-v5-result.json`. Failed earlier V5 runs (rolled back, with the guard changes they caused) are in `failed-attempt-*`.

No function identity, behavior, runtime reachability or original boundary is claimed. Generated C and Ghidra project copies stay in ignored scratch.
