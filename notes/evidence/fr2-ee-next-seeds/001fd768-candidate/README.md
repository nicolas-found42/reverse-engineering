# Bounded static recovery checkpoint: `001fd768`

One root-authorized, isolated Ghidra transaction (guard `tools/ghidra/experimental/CreateEeCandidateV4.java` with the pinned config `config.json`) on a fresh byte-identical copy of the 3860-function project. It added one provisional function at `001fd768` with 263 raw ELF-matched instruction words (1052 bytes, `[001fd768,001fdb84)`), taking the function count to **3861**. Incoming raw JAL: `001fd174` in `candidate_ee_001fd060`, `001fd1b4` in `candidate_ee_001fd060`, `001fd220` in `candidate_ee_001fd060`, `001fd25c` in `candidate_ee_001fd060`, `001fd29c` in `candidate_ee_001fd060`, `001fd3e8` in `candidate_ee_001fd060`, `001fd4d0` in `candidate_ee_001fd060`, `001fd520` in `candidate_ee_001fd060`, `001fd5dc` in `candidate_ee_001fd060`, `001fd61c` in `candidate_ee_001fd060`, `001fd674` in `candidate_ee_001fd060`, `001fd6cc` in `candidate_ee_001fd060`, `001fd714` in `candidate_ee_001fd060`. The next word `001fdb84` (`00000000`) stays undefined and unowned. 0 zero words inside the span are reachable and stay in the body.

All direct JAL targets are saved function entries. No function identity, behavior, runtime reachability or original boundary is claimed.

## Verified

- Config re-derived independently from raw ELF PT_LOAD bytes (`root-config-check.json`): span, edge counts, calls, zero words, incoming raw JALs.
- Transaction `EE_CLOSURE_CANDIDATE_OK`; internal guard checks cover old instructions/data/memory/functions, exact incoming calls, exact new flow references, reciprocal call-graph additions only, unresolved callees.
- Read-only reopen and export: 3861 generated, 0 failed, 606 warning comments; reusable verifier passed.
- Reconciliation `17/17`: all 3860 prior names/sizes/blocks/instruction address-text-bytes preserved; reference and call-graph deltas exactly as predicted; changed old C outputs 001fd060 differ only by label substitution; `.text` gains 263 instructions / 1052 owned bytes. Root rehash of all C artifacts passed (`root-export-check.json`).
- Jev verify: see `jev-verify-result.json` (zero contradicted/unsupported; review flags and root dispositions recorded there). The V3 guard review (`jev-review-v3-*.json`, only present in the first bundle that used V3) escalated (safe_to_apply 0.13); root's disposition is recorded in its result file.

Generated C and the Ghidra project copies remain in ignored scratch.
