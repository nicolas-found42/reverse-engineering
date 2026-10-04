# Bounded static recovery checkpoint: `001ff038`

One root-authorized, isolated Ghidra transaction on a fresh byte-identical copy of the 3,844-function project (the `00200e70` checkpoint). It added one provisional function at `001ff038` with 66 raw ELF-matched instruction words (264 bytes, `[001ff038,001ff140)`), taking the function count to **3,845**. The sole incoming raw JAL is `00200dac` in `candidate_ee_00200d10`. The next word `001ff140` (`27bdff90`) stays undefined and unowned. All five zero words inside the span are reachable and stay in the body; two are branch delay slots.

The candidate is **not call-closed**. It has five direct JALs: `001ffd70` and `001fc4e0` are saved entries; `001ff270`, `001feb80` and `001fdb88` remain uncreated and undefined. No function identity, behavior, runtime reachability or original boundary is claimed.

## What was verified

- Guard `tools/ghidra/experimental/CreateEeCandidate001ff038V2.java` (SHA-256 `85cb6d95...`) ran once, committed, and printed `EE_CLOSURE_CANDIDATE_OK`. Inside the transaction it checked old instructions/data/memory/functions, exact sole incoming call, exact ten new flow references, reciprocal call-graph additions only, and the unresolved callees.
- Read-only reopen and export: 3,845 generated, 0 failed, 606 warning comments (unchanged count); reusable verifier passed.
- Reconciliation against the pinned 3,844 export: 20/20 checks. All 3,844 prior names, sizes, blocks and instruction address/text/bytes preserved. Exactly one reference annotation changed (`00200dac` now resolves to the new function). Call-graph changes are exactly the owner gaining a callee and `001ffd70`/`001fc4e0` gaining a caller. `.text` gained 66 instructions / 264 owned bytes.
- Exactly one old C output changed (`00200d10`, one `func_0x001ff038` → `candidate_ee_001ff038` substitution). Root independently rehashed 7,689 C files and rechecked all 66 words through unique ELF PT_LOAD mappings.
- Jev verify: 7 claims verified, 0 contradicted/unsupported. One compound claim (raw-word match plus next-word exclusion) was flagged `review` at confidence 0.67; both halves are deterministic and covered by the two checkers above. Not retried.

## Review history kept

- The draft guard V1 (`guard-draft-V1.java`, SHA `cd664ee0...`) was never run. A read-only Ghidra inspection of a disposable baseline copy (`InspectRefs.java`, `inspect-readonly.log`) showed disassembler flow references carry source `DEFAULT`, not `ANALYSIS`, so V1's provenance checks would have failed. V2 changes only those two literals (`guard-V2-vs-e70.diff` is V2 against the e70 guard).
- Jev review of V2: `escalate` (safe_to_apply 0.20, composite 0.71, blast radius limiting). The diff argument was a prose summary, not the literal diff, so treat it as low-information. Root read the full guard and ran an independent port of its classifier/constants (`check_ee_f038_guard_port_root_03_v2.py`); the V1-draft port result is retained. Execution was confined to a fresh copy with rollback by default.
- The earlier source-only Jev decision was weak (0.53 vs 0.45, confidence 0.41); its invalid first attempt is kept.

## Pins

Baseline export: manifest `1e3f425e...`, inventory `b2369...`, coverage `2ff0ed89...`. New export hashes are in `export-pins.json`; the full export and generated C stay in ignored scratch. Source project DB `db.24.gbf` and post-transaction `db.25.gbf` hashes are in the `*.sha256` files. The Ghidra project copies are ignored scratch.
