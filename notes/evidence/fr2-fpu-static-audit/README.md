# Static EE FPU translator audit

This package records source-backed discrepancies in pinned PS2Recomp COP1 output and a small game-independent synthetic probe. It does not run game code, an emulator, or hardware.

## Corpus usage

The pinned combined Ghidra inventory contains 3,837 saved function records for executable SHA-256 216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95. It records 487 CVT.W.S, 264 MIN.S, 105 MAX.S, and 14 SQRT.S instructions, alongside 1,235 ADD.S, 1,160 SUB.S, 2,258 MUL.S, and 391 DIV.S. Full normalized counts are in metadata.json.

## Concrete discrepancies

Pinned PS2Recomp commit c5a9d02573410a2085a4b4b831b0b68ba3515440 emits CVT.W.S through nearbyintf and a cast, SQRT.S through sqrtf, and MIN.S/MAX.S through std::min/std::max. Sony's manuals specify toward-zero conversion with saturation above biased exponent 0x9d, signed-zero min/max results, and negative SQRT.S as SQRT(ABS(x)) with I/SI set and D cause cleared. See exact manuals, page references, pinned source hashes, and scope in metadata.json. The conversion-overflow flag semantics remain unresolved because Sony’s manuals conflict: Table 8-4 says no cause flag, the instruction page does not list flag writes, but Table 8-6 says I/SI. The experiment leaves CVT.W.S FCR31 behavior unchanged.

The DIV.S template also diverges from the documented signed finite maximum and flags for division by zero. The pinned PCSX2 FPU implementation offers a separate software comparator with input normalization, overflow/underflow, divide-by-zero, signed-zero min/max, conversion, and square-root paths. It is not a silicon oracle. General arithmetic and DIV.S need a dedicated EE arithmetic model before any correction is proposed. Host float operators alone do not implement the documented overflow, underflow, flag, and custom-rounding rules.

## Synthetic check

Run python3 tools/recomp/experimental/verify_ee_fpu_experiment.py --source-tree .scratch/mesh/codex-root/PS2Recomp --output .scratch/mesh/codex-fpu-audit-01/actual-template-result.json. The verifier rejects mismatched source/patch/package hashes, applies the diff only in a temporary copy, expands exact pristine and candidate emitter strings, and compiles both generated synthetic paths with UBSan and float-cast-overflow. It refuses an existing output path and writes successful output atomically. A narrow, isolated experimental patch package is at tools/recomp/experimental; the pinned checkout remains unchanged. Its candidate helper is the exact helper file extracted from the temporary patch application, and the manifest pins all changed output hashes.

Full Jev arguments and results are preserved in jev-receipt.json and jev-patch-receipt.json. They support the cited text and bounded helper claims; neither establishes execution fidelity. The earlier DIV/SQRT review dispositions remain unresolved. Root’s independent Sony-manual check retained human review on the compound SQRT behavior claim (confidence 0.63); its exact call and result are preserved in r067-fpu-manual-verification.json. It also confirmed conflicting Sony descriptions for CVT.W.S overflow flags; the patch leaves those flags unchanged. Sony notes hardware truncation can differ from IEEE round-toward-zero in the least significant bit, so arbitrary host sqrtf results remain unverified.


The proposed source diff, test policy, and limits are documented in [tools/recomp/experimental/README.md](../../../tools/recomp/experimental/README.md). The earlier actual-template run is preserved as `actual-template-validation-superseded-02.json`; the refreshed hardening run is `actual-template-validation-02.json`. Source, patch, helper, test, and compiler-driver hashes are in tools/recomp/experimental/source-manifest.json.

Root subsequently integrated all four bounded patches in a separate fresh clone, regenerated and compiled 4,746 function units plus registration, and validated a private archive. [The root integration bundle](root-integration/README.md) records that later work, its 252-test suite, unchanged historical receipts, and the FPU patch gate that remains escalated at safe-to-apply 0.13. That integration proves compileability under the tested toolchain; it does not establish broad floating-point semantics or hardware fidelity.
