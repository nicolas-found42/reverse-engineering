# Bounded static recovery checkpoint: `001fd060`

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV4.java` with the pinned config `config.json`) on a fresh byte-identical copy of the 3859-function project. It added one provisional function at `001fd060` with 449 raw ELF-matched instruction words (1796 bytes, `[001fd060,001fd764)`), taking the function count to **3860**. Incoming raw JAL: `001fcef4` in `candidate_ee_001fce10`. The next word `001fd764` (`00000000`) stays undefined and unowned. 1 zero words inside the span are reachable and stay in the body.

The candidate is **not call-closed**: `001fd768`, `001feda0` remain uncreated and undefined. No function identity, behavior, runtime reachability or original boundary is claimed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): span, edge counts, calls, zero words, incoming raw JALs.
- Transaction `EE_CLOSURE_CANDIDATE_OK`; internal guard checks cover old instructions/data/memory/functions, exact incoming calls, exact new flow references, reciprocal call-graph additions only, unresolved callees.
- Read-only reopen and export: 3860 generated, 0 failed, 606 warning comments; reusable verifier passed.
- Reconciliation `19/19`: all 3859 prior names/sizes/blocks/instruction address-text-bytes preserved; reference and call-graph deltas exactly as predicted; changed old C outputs 001fce10 differ only by label substitution; `.text` gains 449 instructions / 1796 owned bytes. Root rehash of all C artifacts passed (`root-export-check.json`).
- Jev verify: see `jev-verify-result.json` (zero contradicted/unsupported; review flags and root dispositions recorded there). The V3 guard review (`jev-review-v3-*.json`, only present in the first bundle that used V3) escalated (safe_to_apply 0.13); root's disposition is recorded in its result file.

Generated C and the Ghidra project copies remain in ignored scratch.
