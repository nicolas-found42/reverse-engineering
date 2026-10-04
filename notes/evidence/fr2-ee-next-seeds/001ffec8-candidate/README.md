# Bounded static recovery checkpoint: `001ffec8`

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV4.java` with the pinned config `config.json`) on a fresh byte-identical copy of the 3855-function project. It added one provisional function at `001ffec8` with 94 raw ELF-matched instruction words (376 bytes, `[001ffec8,00200040)`), taking the function count to **3856**. Incoming raw JAL: `001fed88` in `candidate_ee_001fed80`, `001fef70` in `candidate_ee_001fef28`, `001ff594` in `candidate_ee_001ff520`, `001ffc3c` in `candidate_ee_001ffbf0`, `001ffc94` in `candidate_ee_001ffbf0`. The next word `00200040` (`27bdffc0`) is the entry of a saved function, which is unchanged and outside the candidate. 2 zero words inside the span are reachable and stay in the body.

All direct JAL targets are saved function entries. No function identity, behavior, runtime reachability or original boundary is claimed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): span, edge counts, calls, zero words, incoming raw JALs.
- Transaction `EE_CLOSURE_CANDIDATE_OK`; internal guard checks cover old instructions/data/memory/functions, exact incoming calls, exact new flow references, reciprocal call-graph additions only, unresolved callees.
- Read-only reopen and export: 3856 generated, 0 failed, 606 warning comments; reusable verifier passed.
- Reconciliation `17/17`: all 3855 prior names/sizes/blocks/instruction address-text-bytes preserved; reference and call-graph deltas exactly as predicted; changed old C outputs 001fed80, 001fef28, 001ff520, 001ffbf0 differ only by label substitution; `.text` gains 94 instructions / 376 owned bytes. Root rehash of all C artifacts passed (`root-export-check.json`).
- Jev verify: see `jev-verify-result.json` (zero contradicted/unsupported; review flags and root dispositions recorded there). The V3 guard review (`jev-review-v3-*.json`, only present in the first bundle that used V3) escalated (safe_to_apply 0.13); root's disposition is recorded in its result file.

Generated C and the Ghidra project copies remain in ignored scratch.
