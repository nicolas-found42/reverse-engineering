# Synthetic EE integer-division validation

The four pinned PS2Recomp `DIV`, `DIVU`, `DIV1`, and `DIVU1` translation expressions pass 600,600 synthetic comparisons each under Clang UBSan. Each comparison checks quotient/remainder sign extension, the untouched HI/LO bank, and every original register. A separately compiled variant flips the low quotient bit after each actual emitted expression; all 600,600 comparisons fail for every operation, as required. No translator repair was justified by these results.

The verifier checks PS2Recomp commit `c5a9d02573410a2085a4b4b831b0b68ba3515440`, three source SHA-256 values, and the pinned SSE2NEON header before compiling. It extracts the actual four `fmt::format` templates, low-word register extractor, and signed/unsigned register-read macros. It refuses an existing output directory. It compiles only these public translator expressions against a synthetic context; it never executes original game code.

The independent reference arithmetic widens signed operands to 64 bits before division. This makes `INT32_MIN/-1` defined in the oracle while retaining the EE low-word result. Sign extension is expressed with unsigned bit masks. The matrix contains all 100 pairs of ten directed values plus 100,000 seeded random pairs, each in six source-register modes: ordinary, reversed, zero dividend, zero divisor, same source register, and both zero. Nonzero storage in register zero verifies that the production read macros select zero. Valid sign-extended source words are used; instruction timing and undefined non-word input behavior are outside the test.

Sony's [EE Core Instruction Set Manual](https://docs.alexrp.com/mips/ee_insns.pdf), printed pp. 67–68, 138, and 140, specifies the sign-extended quotient/remainder and the signed overflow result. It explicitly leaves a zero divisor's arithmetic result undefined. Zero-divisor checks therefore establish agreement with the pinned software policy only. [PCSX2's pinned interpreter](https://github.com/PCSX2/pcsx2/blob/81526d4dc7cc70e4ae75abb35a789417456c6d43/pcsx2/R5900OpcodeImpl.cpp) supplies an independent software comparison for signed/unsigned divide-by-zero results. Its nearby DIVU comments disagree with the signed cast in its implementation; the audit uses the expression, not the comment. Firecrawl fetched that exact source revision and Jev screened it with recommendation `pass`; receipt identities are in `source-provenance.json`.

The historical 3,446-function static inventory contains 47 `DIV`, 43 `DIVU`, and four `DIV1` instructions, with no `DIVU1`. These are unique-address counts for that saved inventory, not a complete executable inventory or execution-frequency measure. `historical-inventory-counts.json` pins its source hash. The newer decompiler inventory remains a separate artifact.

Eight focused tests cover extraction, source/commit/dependency drift, fresh-output preservation, and the native matrix with its corrupted-quotient control. Pyright reports zero errors and warnings. The initial two extraction errors are preserved: an internal `);` in a C string prematurely ended the first regex. The corrected adjacent-string grammar then passed six tests; two additional source-pin guards brought the focused suite to eight. This failure was in the new verifier, not the game or upstream translator.

Jev's root gate remains `escalate`, with composite 0.857 and safe-to-apply 0.50. It verified all four claims, but retained low confidence on source guards and the test-result claim and on several test-gap/blast-radius rubrics. The exact arguments and result are in `root-jev-gate.json`; direct evidence and limits are recorded in `root-disposition.json`. The judgment was not retried for approval. Independent read-only review found no actionable defect and independently passed the eight tests. Its Jev review also remains escalated (safe-to-apply 0.41); separate verification supported four bounded source/oracle/matrix claims. The adjacent independent receipts retain those results.

Reproduce with the pinned private checkout and dependency:

```sh
python3 tools/recomp/verify_integer_division.py \
  --upstream .scratch/mesh/codex-root/PS2Recomp \
  --fresh-output-dir .scratch/mesh/codex-root/integer-div-fresh-output \
  --sse2neon .scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src
PYTHONPATH=tools python3 -m unittest tools.test_recomp_integer_division -v
```

This evidence does not establish original function boundaries, decoder coverage, scheduling, instruction timing, runtime integration, hardware equivalence, or whole-game completeness. Full game pseudocode, payloads, and original executable bytes remain outside this bundle.
