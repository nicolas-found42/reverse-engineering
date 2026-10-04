# Bounded static recovery checkpoint: `001feda0`

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV4.java` with the pinned config `config.json`) on a fresh byte-identical copy of the 3862-function project. It added one provisional function at `001feda0` with 97 raw ELF-matched instruction words (388 bytes, `[001feda0,001fef24)`), taking the function count to **3863**. Incoming raw JAL: `001fd1e0` in `candidate_ee_001fd060`, `001fd488` in `candidate_ee_001fd060`. The next word `001fef24` (`00000000`) stays undefined and unowned. 1 zero words inside the span are reachable and stay in the body.

All direct JAL targets are saved function entries. No function identity, behavior, runtime reachability or original boundary is claimed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): span, edge counts, calls, zero words, incoming raw JALs.
- Transaction `EE_CLOSURE_CANDIDATE_OK`; internal guard checks cover old instructions/data/memory/functions, exact incoming calls, exact new flow references, reciprocal call-graph additions only, unresolved callees.
- Read-only reopen and export: 3863 generated, 0 failed, 606 warning comments; reusable verifier passed.
- Reconciliation `17/17`: all 3862 prior names/sizes/blocks/instruction address-text-bytes preserved; reference and call-graph deltas exactly as predicted; changed old C outputs 001fd060 differ only by label substitution; `.text` gains 97 instructions / 388 owned bytes. Root rehash of all C artifacts passed (`root-export-check.json`).
- Jev verify: see `jev-verify-result.json` (zero contradicted/unsupported; review flags and root dispositions recorded there). The V3 guard review (`jev-review-v3-*.json`, only present in the first bundle that used V3) escalated (safe_to_apply 0.13); root's disposition is recorded in its result file.

Generated C and the Ghidra project copies remain in ignored scratch.
