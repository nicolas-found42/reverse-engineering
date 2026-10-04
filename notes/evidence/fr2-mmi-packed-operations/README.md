# Packed MMI operation-template audit

This package records a bounded static and synthetic audit of 13 packed-register operations used by the corpus. The verifier compiles templates extracted from pristine, hash-pinned PS2Recomp source. It never accepts game assembly/C as input and does not execute an original game routine or an emulator.

The exact rerun used:

```sh
python3 tools/recomp/verify_mmi_packed.py \
  --upstream .scratch/mesh/codex-root/PS2Recomp \
  --fresh-output-dir .scratch/mesh/codex-root/mmi-packed-promoted-fixed-01 \
  --sse2neon .scratch/mesh/codex-root/recomp-build/_deps/sse2neon-src
```

The run passed. It compiled with Clang C++20, `-Wall -Wextra -Werror`, UBSan, and pinned SSE2NEON. Each of the 13 operations received 80,096 independent byte/word-reference comparisons with zero mismatches and no sanitizer diagnostics. The matrix uses four basis inputs, eight boundary/pattern inputs, and 10,000 deterministic random pairs (seed 5900), crossed with eight register configurations: distinct sources/destination, `rd==rs`, `rd==rt`, `rd==0` with a sentinel, `rs==0`, `rt==0`, both sources zero, and all three registers aliased.

The extracted templates implement PCPYLD and PCPYUD half-vector copies, PCPYH halfword replication, PEXT lower/upper interleaves, 128-bit bitwise logic, and byte/word wrapping subtraction. The independent reference and pinned manual/PCSX2 operation definitions agree on these mappings. This establishes only behavior of the extracted expressions with the tested host vector implementation and modeled register-zero policy. It does not cover decoding, flags, pipeline/timing, broader runtime semantics, or game/emulator equivalence.

Pinned inputs:

- PS2Recomp commit: `c5a9d02573410a2085a4b4b831b0b68ba3515440`
- `ps2xRuntime/include/ps2_runtime_macros.h`: SHA-256 `c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e`
- `ps2xRecomp/src/lib/mmi_translation_helpers.cpp`: SHA-256 `1402bdb9f81923a8c91c7fa790399a2563ebc5f7cd0c899b7c29cb7c6bafc5ee`
- `sse2neon.h`: SHA-256 `78632498a57bf7e080e84cb8d74c47ce93b204cece77eab79de2908eb8bc92ed`
- verifier: see `source-hashes.json`

## Oracle development history

Earlier harness attempts remain preserved in private scratch and are superseded by audit 03 and the promoted verifier. The first failed compilation because a generated PCPYH wrapper left an unused parameter under `-Werror`. The second harness ran but produced mismatches because its expected-input setup selected the wrong source buffer for one register mode. The correction changed the synthetic oracle setup only; it did not alter upstream code. Exact scratch receipts are `.scratch/mesh/codex-root/mmi-packed-audit/compile.json` and `.scratch/mesh/codex-root/mmi-packed-audit-02/run.json`; the passing scratch receipt is `.scratch/mesh/codex-root/mmi-packed-audit-03/`.

## Jev dispositions

The earlier audit Jev receipt is preserved in `jev-initial.json`. Jev verified the PEXT lane order, logical operations, subtraction truncation, zero/alias coverage, and probe result. PCPYLD and PCPYH remained `review` at confidence 0.51 and 0.69, and the full-equivalence claim was unsupported. Those low-confidence outcomes were retained without retries. A final check over the promoted verifier artifacts is in `jev-final.json`: four claims were verified; the source identity claim still carries `review` at confidence 0.73. These judgment outcomes are advisory and do not replace the explicit-source manual/PCSX2 comparison.

The primary instruction reference is Sony's EE Core Instruction Set Manual v6.0, https://docs.alexrp.com/mips/ee_insns.pdf (printed pages: PAND 176; PCPYH 189, PCPYLD 190, PCPYUD 191; PEXTLB 203, PEXTLH 204, PEXTLW 205, PEXTUW 208; PNOR 252, POR 253, PSUBB 270, PSUBW 284, PXOR 285). The independent implementation comparison is pinned PCSX2 MMI.cpp commit `81526d4dc7cc70e4ae75abb35a789417456c6d43`, https://github.com/PCSX2/pcsx2/blob/81526d4dc7cc70e4ae75abb35a789417456c6d43/pcsx2/MMI.cpp. Fetch provenance from the earlier shuffle audit is retained at `notes/evidence/fr2-mmi-shuffles/source-provenance.json`.

Firecrawl and jgrep were used as discovery/navigation aids; their warnings and no-result searches are retained in the copied receipts. Exact source inspection and the instruction manual remain the basis for claims. No full game assembly, generated game C, or original payload is included here.

Root review found that directed samples 5 and 9 left one input vector uninitialized. UBSan does not detect uninitialized reads, so the original complete-sample result is superseded. The probe now clears both full vectors before each directed pattern. A fresh native run passed all 80,096 comparisons per operation with the corrected source; its compiler/run/result receipts and source hashes replace the current receipt while the prior versions are retained with a `superseded` filename. All 10,000 random pairs were already fully initialized. The earlier Jev receipts apply to their recorded older inputs and do not validate this correction.

The root gate over the corrected probe is preserved in `root-corrected-probe-jev-gate.json`. It escalated at composite 0.754 and safe-to-apply 0.46, with low test-gap confidence. It marked the corrected initialization/count claim verified at confidence 0.32 and the bounded-scope claim verified at 0.98. The low-confidence result is retained. Root independently checked that basis inputs clear both vectors, every directed-pattern branch begins with two full clears, and each random sample assigns every byte; the fresh native receipt and six focused source-guard tests passed. These are the concrete basis for the bounded result, without an automatic approval or full-equivalence claim.
