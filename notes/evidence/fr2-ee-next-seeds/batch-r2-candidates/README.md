# Bounded static recovery checkpoint: batch `r2` (196 functions)

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV5.java`, schema-2 config `config.json`) on a fresh byte-identical copy of the 4346-function project. It added **196** provisional functions (6543 raw ELF-matched instruction words; 5209 were already decoded as unowned instructions and the rest newly decoded), taking the function count to **4542**.

Evidence per seed: 4 seeds have at least one direct JAL from decoded code (4 incoming call sites in total); 192 seeds have no direct call and are PS2Recomp function-table leads whose structure passed the same raw CFG validation. 249 non-call references into entries (for example PARAM address-taken references from saved functions) were recorded and verified unchanged. 0 call targets remain unresolved (uncreated), so the set is not call-closed.
Round 2 over the 455 PS2Recomp function-table entries that remained uncreated after batch all-1 (after correcting a generator bug that scanned misaligned byte addresses and had wrongly dropped about 177 seeds in batch all-1). 203 were feasible; 7 were excluded after guard rejections (0015e898, 001710d8, 00180990, 001ed230: Ghidra direct-jump classification differs; 00170488, 00177790, 001802e8: calls to a non-returning function with null fall-through); 196 created. Guard changes made during this round: tail jumps accept Ghidra's CALL_TERMINATOR flow type (adds call-graph edges) as well as UNCONDITIONAL_JUMP. An earlier attempt of this round (177 functions, guard before those changes) is not part of this bundle; its project copy was kept in ignored scratch.


## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): every seed's span, edges, calls, zero words, coverage states and all incoming JAL sites.
- Transaction `EE_BATCH_CANDIDATES_OK`; in-guard checks: old instructions/data/memory/functions unchanged, listing delta equals exactly the newly decoded words, global reference additions equal exactly the raw CFG flow edges of newly decoded words, per-seed reference partition (entry calls / intra-span branches / non-call refs), full call-graph equality against the config prediction, unresolved callees uncreated, next-word states.
- Read-only reopen and export: 4542 generated, 0 failed, 613 warning comments; reusable verifier passed.
- Reconciliation `16/16` (`reconciliation.json`); root rehash of all C artifacts passed (`root-export-check.json`).
- The V5 guard review escalated (safe_to_apply 0.11); root's disposition is in `jev-review-v5-result.json`. Failed earlier V5 runs (rolled back, with the guard changes they caused) are in `failed-attempt-*`.

No function identity, behavior, runtime reachability or original boundary is claimed. Generated C and Ghidra project copies stay in ignored scratch.
