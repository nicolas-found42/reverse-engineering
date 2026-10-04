# Experimental EE FPU semantics patch

This package contains a proposed, source-pinned patch for three manual-specified COP1 cases. It is isolated from the pinned PS2Recomp checkout. Applying the patch to an actual generator or accepting its results is a separate review decision.

Root later tested the patch with the three prior bounded corrections in a separate fresh clone. [The integration evidence](../../../notes/evidence/fr2-fpu-static-audit/root-integration/README.md) records regenerated output, complete object/archive compilation, and the still-escalated patch review. The pristine checkout remains unchanged and this patch remains experimental.

The patch targets PS2Recomp commit `c5a9d02573410a2085a4b4b831b0b68ba3515440` and the exact `fpu_translator.cpp` and `ps2_runtime_macros.h` hashes recorded in `source-manifest.json`. `verify_ee_fpu_experiment.py` extracts the exact baseline emitter templates, rejects a different source revision or changed source bytes, applies the patch in a temporary copy, then builds and runs only `probe.cpp` with UBSan and float-cast-overflow sanitizers.

The proposed changes are:

- `CVT.W.S` truncates in-range values toward zero and saturates when the biased exponent exceeds `0x9d`. The bit-level range check runs before a C++ float-to-integer cast, so that cast receives only values strictly within signed 32-bit range. The patch does not write FCR31 for conversion. Sony’s manuals conflict on conversion-overflow flags: Table 8-4 says none, the instruction page lists no flag writes, while Table 8-6 says I/SI. Conversion flag behavior remains unresolved.
- `MIN.S` and `MAX.S` select signed zero according to Sony's zero table. For other finite values, selection follows the instruction's `<=` or `>=` definition. The emitter clears only the documented O/U cause bits and preserves sticky, condition, and control bits.
- `SQRT.S` preserves signed zeros, maps negative normal finite input through `sqrtf(abs(x))`, sets I and sticky I for that case, and clears only I/D cause bits. It preserves all other FCR31 bits. NaN, infinity, and denormal inputs take the original `sqrtf` host path because this package does not model those unsupported cases.

The probe tests exact roots (including `sqrt(-4)` and `sqrt(4)`), all four signed-zero operand combinations for MIN.S and MAX.S, positive and negative fractional conversion, the exponent boundary, positive and negative saturation, selected FCR31 cause/sticky preservation, and baseline negative controls. The verifier pins the compiler driver/version before compilation, calls the package-manifest check at the public patch-validation boundary, and constrains the patch to a verifier-owned three-path allowlist. It uses the system C++ library for square-root calculation. It does not prove EE-specific square-root rounding for arbitrary values. Sony notes that its hardware chopping can differ from IEEE round-toward-zero in the least significant bit, so host `sqrtf` results beyond the exact tested roots are not certified. The package also does not model full arithmetic, DIV.S, denormal behavior, NaN/infinity behavior, exception delivery, or all FCR31 rules. The independent manual review retained a Jev human-review disposition for the compound SQRT claim (confidence 0.63); see `notes/evidence/fr2-fpu-static-audit/r067-fpu-manual-verification.json`. No original game function, emulator, or console was run.

Run from the repository root:

```sh
python3 tools/recomp/experimental/verify_ee_fpu_experiment.py \
  --source-tree .scratch/mesh/codex-root/PS2Recomp \
  --output .scratch/mesh/codex-fpu-audit-01/promoted-result.json
python3 -m unittest tools.test_recomp_fpu_experimental -v
```

The first command writes fresh output and fails closed on a source mismatch. A passing patch dry-run and synthetic probe do not certify the whole recompiler.
