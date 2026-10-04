# Bounded static recovery checkpoint: `001fce10`

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV4.java` with the pinned config `config.json`) on a fresh byte-identical copy of the 3856-function project. It added one provisional function at `001fce10` with 148 raw ELF-matched instruction words (592 bytes, `[001fce10,001fd060)`), taking the function count to **3857**. Incoming raw JAL: `001ff3e8` in `candidate_ee_001ff270`. The next word `001fd060` (`27bdff10`) stays undefined and unowned. 5 zero words inside the span are reachable and stay in the body. Shapes pinned beyond the V3 guard: `BREAK` in a branch-likely delay slot at `001fce5c`.

The candidate is **not call-closed**: `001fd060`, `002018d8` remain uncreated and undefined. No function identity, behavior, runtime reachability or original boundary is claimed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): span, edge counts, calls, zero words, incoming raw JALs.
- Transaction `EE_CLOSURE_CANDIDATE_OK`; internal guard checks cover old instructions/data/memory/functions, exact incoming calls, exact new flow references, reciprocal call-graph additions only, unresolved callees.
- Read-only reopen and export: 3857 generated, 0 failed, 606 warning comments; reusable verifier passed.
- Reconciliation `19/19`: all 3856 prior names/sizes/blocks/instruction address-text-bytes preserved; reference and call-graph deltas exactly as predicted; changed old C outputs 001ff270 differ only by label substitution; `.text` gains 148 instructions / 592 owned bytes. Root rehash of all C artifacts passed (`root-export-check.json`).
- Jev verify: see `jev-verify-result.json` (zero contradicted/unsupported; review flags and root dispositions recorded there). The V3 guard review (`jev-review-v3-*.json`, only present in the first bundle that used V3) escalated (safe_to_apply 0.13); root's disposition is recorded in its result file.

Generated C and the Ghidra project copies remain in ignored scratch.
