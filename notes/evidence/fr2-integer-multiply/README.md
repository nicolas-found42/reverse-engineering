# EE integer multiply: bounded source audit

This bundle checks the pinned PS2Recomp emitters for `MULT`, `MULTU`, `MULT1`, and `MADD` against the operation definitions in Sony's EE Core Instruction Set Manual. It extracts the actual emitted C++ snippets and runtime register helpers from the pinned checkout, compiles those snippets into synthetic wrappers, and compares state changes with a separate widened/modulo arithmetic oracle.

The saved FR2 static export has 241 `MULT`, 5 `MULTU`, 24 `MULT1`, and 3 `MADD` instructions at unique addresses. These are inventory counts from a hash-pinned, 3446-function export; they do not mean every instruction site or caller was semantically validated.

The fresh run checked all eight emitted variants (destination register nonzero and zero for each operation) 201,440 times each. Every actual-template result matched the oracle. The negative control flips one bit of the selected LO or LO1 output and all 201,440 checks failed in each variant. The matrix uses twelve boundary values in all ordered pairs plus 20,000 deterministic random pairs; ten register modes cover distinct sources, source equality, `rd` aliasing either or both sources, zero source registers, zero destination, and the combined alias/zero case. It also checks that output writes preserve the non-output register state, the GPR upper half, register zero, and the other HI/LO bank.

Sony's printed manual pages are 142 (`MADD`), 154 (`MULT`), 155 (`MULT1`), and 156 (`MULTU`). The manual requires sign-extended 32-bit input words for defined results. The probe constructs such inputs while varying the low 32-bit words. `MULTU` multiplies the unsigned low words; the other three use signed low words. Each result word is sign-extended to 64 bits, and `MULT1` writes the secondary bank. `MADD` accumulates into the concatenation of the low 32 bits of HI and LO. The pinned PCSX2 source provides an independent software cross-check of those arithmetic/result-lane behaviors, not a hardware oracle.

Run the verifier from the repository root with explicit pinned inputs and a new output directory:

```sh
python3 -m tools.recomp.verify_integer_multiply \
  --upstream .scratch/mesh/codex-root/PS2Recomp \
  --static-export .scratch/evidence/static-export.json \
  --fresh-output-dir .scratch/mesh/codex-root/integer-multiply-audit-NN \
  --sse2neon .scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src
```

The verifier refuses an existing output path, checks the upstream commit and source hashes, the executable/export identity and instruction inventory, and the `sse2neon.h` hash before compiling. See `source-provenance.json` for source pins, `result.json` and `native-run-receipt.json` for the measured outcome and exact native arguments, and the `jev-*.json` receipts for screened manual text and claim verification.

This is a static-template experiment with synthetic register state. It does not test opcode decoding, original game routines, asynchronous completion/interlocks, timing, exceptions, silicon behavior, or the PS2 hardware. The randomized component is deterministic and sampled, not an exhaustive enumeration of all input pairs.

The initial `result.json`, `source-provenance.json`, 10-test validation, and agent Jev receipts predate root status enforcement. They are preserved as historical artifacts. [Root hardening](root-hardening/README.md) records the current code, fresh native run, 11 focused tests and 286-test full suite. Root corrected the mutant description: it corrupts the selected output bank, while the comparison independently verifies preservation of the other bank.
