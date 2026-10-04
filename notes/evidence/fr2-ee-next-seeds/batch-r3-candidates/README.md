# Bounded static recovery checkpoint: batch `r3` (176 functions)

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV5.java`, schema-2 config `config.json`) on a fresh byte-identical copy of the 4542-function project. It added **176** provisional functions (13382 raw ELF-matched instruction words; 11144 were already decoded as unowned instructions and the rest newly decoded), taking the function count to **4718**.

Evidence per seed: 6 seeds have at least one direct JAL from decoded code (60 incoming call sites in total); 170 seeds have no direct call and are PS2Recomp function-table leads whose structure passed the same raw CFG validation. 208 non-call references into entries (for example PARAM address-taken references from saved functions) were recorded and verified unchanged. 0 call targets remain unresolved (uncreated), so the set is not call-closed.
Round 3 over the 259 remaining PS2Recomp function-table entries after batch r2: 200 were feasible under the extended guard (terminal tail J, pinned zero padding words), 18 were excluded after guard rejections (six with a non-call reference from outside the span into the span interior; twelve calling a non-returning function with null fall-through), 176 created. 59 entries were not attempted because the generator found computed jumps, traps, unreachable non-zero words, or flow into saved functions. Padding words: 117 unreachable zero words inside the spans are pinned, checked zero in the ELF, excluded from the function bodies and left in their baseline state.


## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): every seed's span, edges, calls, zero words, coverage states and all incoming JAL sites.
- Transaction `EE_BATCH_CANDIDATES_OK`; in-guard checks: old instructions/data/memory/functions unchanged, listing delta equals exactly the newly decoded words, global reference additions equal exactly the raw CFG flow edges of newly decoded words, per-seed reference partition (entry calls / intra-span branches / non-call refs), full call-graph equality against the config prediction, unresolved callees uncreated, next-word states.
- Read-only reopen and export: 4718 generated, 0 failed, 620 warning comments; reusable verifier passed.
- Reconciliation `16/16` (`reconciliation.json`); root rehash of all C artifacts passed (`root-export-check.json`).
- The V5 guard review escalated (safe_to_apply 0.11); root's disposition is in `jev-review-v5-result.json` (present where this bundle was the first to use that guard version; later guard changes are in `jev-review-v5b-*.json`). Failed earlier V5 runs (rolled back, with the guard changes they caused) are in `failed-attempt-*`.

No function identity, behavior, runtime reachability or original boundary is claimed. Generated C and Ghidra project copies stay in ignored scratch.
