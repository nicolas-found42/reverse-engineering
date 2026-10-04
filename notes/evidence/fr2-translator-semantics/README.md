# Scalar translator experiment

This directory preserves an experimental, source-pinned scalar arithmetic translator patch and bounded synthetic checks. It is not a verified decompilation or a claim that PS2Recomp output is equivalent to the game.

The patch is `tools/recomp/translator-semantics.patch`, SHA-256 `339f19be5a65ed63a11ab21f44bc548bb66210b45c2fe2648f629b2240d6d006`. It applies to upstream [`ran-j/PS2Recomp`](https://github.com/ran-j/PS2Recomp) commit `c5a9d02573410a2085a4b4b831b0b68ba3515440`. The patch modifies only `instruction_translator.cpp` and `special_translator.cpp`; it does not modify the upstream checkout in place.

The harness is `tools/recomp/verify_translator_semantics.py`. It requires an explicit `--source-root`, checks exact source and commit hashes before patching, stages only those two patch targets under a temporary directory, applies the local diff there, verifies candidate hashes, extracts and compiles the actual emitted C++ templates, and runs UBSan checks. Read-only pin assertions cover the call/exception path in FunctionEmitter, ControlFlowEmitter, and PS2Runtime; those sources are hash-checked separately and are not copied into the patch stage. The ordinary test-discovery module is `tools/test_translator_semantics.py`.

The latest immutable run result is [`translator-validation.json`](results/translator-validation.json). The focused test log is [`focused-tests.log`](results/focused-tests.log). The harness rejects any changed translator input SHA; the unit test deliberately changes one source and confirms rejection. It also rejects wrong repository revision, verifies patch application changes only two staged files, and checks the pinned downstream exception propagation text.

Validation results:

- The actual patched templates compile and pass ten synthetic controls covering DADD, DSUB, DADDI, DADDIU, ADDI to `$zero`, ADD/SUB overflow exits, a delay-slot EPC, and a callee exception observed by its caller.
- A separate C++ reference test checks 289 directed operand pairs, selected signed immediate values, and 100,000 deterministic random cases under UBSan.
- The original pinned DADD, DSUB, DADDI, and DADDIU templates each produce an UBSan signed-overflow diagnostic on directed boundary input; the safe original control passes. The initial pre-fix exception-vector overwrite repro is retained as a separate log.
- The focused Python module passes 7 tests, including compiler-failure diagnostics and the generated control count. The full ordinary `tools` discovery suite is run after all promoted changes are stable.

The exception propagation inspection follows a callee exception through the pinned dispatcher: `dispatchGuestBranch` calls the translated callee, only substitutes the call fallthrough when `ctx->pc` remains at the entry PC, and returns whether the PC equals call fallthrough. Generated DirectCall and IndirectCall sites return from the caller on a false result. The synthetic callee/caller control validates this branch behavior. This does not prove exception delivery end-to-end through every runtime loop or exception handler.

Architectural basis is Sony Computer Entertainment Inc., *EE Core Instruction Set Manual* v6.0 (2002), viewed at <https://docs.alexrp.com/mips/ee_insns.pdf>: ADDI PDF p.25; DADD p.47; DADDI p.48; DADDIU p.49; DSUB p.63. The relevant operations specify unchanged destination and Integer Overflow on signed overflow, while DADDIU does not trap. The Jev screen receipt is in [`sony-manual-screen.json`](jev/sony-manual-screen.json).

Jev review history is intentionally retained, including escalations. The first scratch gate had review composite 0.67675 and three unsupported completion claims; see [`initial-gate-disposition.json`](jev/initial-gate-disposition.json). The next gate, after emitted-template tests, remained escalated at composite 0.74475 / safe-to-apply 0.22; see [`prior-scratch-gate.json`](jev/prior-scratch-gate.json). A final gate for the promoted files is recorded separately. These scores are advisory and did not replace source inspection or the concrete test results.

The scratch and promoted experiment use test-only definitions of ADD32_OV and SUB32_OV with widened arithmetic. The repository’s separate `tools/recomp/defined-overflow.patch` must be included for a combined runtime build. This scalar patch does not cover packed/shuffle behavior; the root agent owns those changes separately. No full generated game code is produced or run, and no original routine or emulator is executed.

The promoted-files Jev gate is [`promotion-final-gate.json`](jev/promotion-final-gate.json). It remains escalated: composite `0.790125`, safe-to-apply `0.11`; it verified five claims, left one arithmetic claim unsupported, and flagged two claims for review. The call-dispatch propagation, source pinning, test execution, and scope limits were verified. This escalation is retained rather than softened or rerun; the patch is left for parent review.
