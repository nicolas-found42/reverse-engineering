# PS2Recomp arithmetic experiment

The upstream PS2Recomp source is distributed under GNU GPL version 3. The patch and synthetic helper files in this directory use that license; the upstream license text is retained in `LICENSE`. Experiments keep modified upstream source copies in private scratch. The bounded changes cover the two overflow helpers, scalar arithmetic/exception templates, and three packed-register shuffle mappings.

`defined-overflow.patch` changes two runtime helpers in PS2Recomp commit `c5a9d02573410a2085a4b4b831b0b68ba3515440`. It evaluates signed 32-bit add/subtract in an `int64_t` intermediate, checks the result against `int32_t` bounds, and converts to `uint32_t` for a defined modulo-2³² result. Each operand is evaluated once. This removes the reproduced signed C++ overflow in the helpers; it does not validate a complete PS2 runtime or game.

The pristine header SHA-256 is `c0dfe8104803a380ff4f38a3ba3d5ed1979c68ad7234d83230863f079f354c4e`; the corrected header SHA-256 is `4b88ff8ea6966dd97aa17cb0e06c0c8ad98923b84af32b335e6e8972a0537973`. The patch SHA-256 is `3b14131ae25ff79ec204e4bc0b0de383b19d43d7cd71bb1407802a6b793ca31e`. Apply only to that pinned source. The verifier rejects a different header before compiling any extracted definitions.

`verify_overflow.py` extracts only the two macro definitions and compiles `overflow_probe.cpp` with Clang UBSan. It checks both operations across 297 input pairs, including a grid of signed boundaries and directed overflow cases. Run it against the corrected header for the positive result, or use `--expect-ubsan` against the pristine header for the signed-overflow negative control. Both compiler and probe subprocesses have 30-second bounds. No original game function or emulator is executed.

The source experiment, failed intermediate patch, exact hashes, model receipts, positive/negative results, and native integration compilation are retained in `notes/evidence/fr2-independent-recovery`. An initial sign-of-wide-result overflow predicate failed on `INT32_MIN + INT32_MIN`; that failure remains recorded. Final Jev arithmetic/scope claims were verified, while its patch review remained escalated on integration confidence. Root review and the subsequent full generated-function compilation provide independent bounded evidence; they do not change that model outcome.

## Experimental scalar translator patch

`translator-semantics.patch` is an experimental patch for PS2Recomp commit `c5a9d02573410a2085a4b4b831b0b68ba3515440`. It changes only `ps2xRecomp/src/lib/instruction_translator.cpp` and `ps2xRecomp/src/lib/special_translator.cpp`: DADD, DADDI, DSUB, and DADDIU use defined unsigned 64-bit intermediate arithmetic; the trapping forms retain signed-overflow detection; ADDI-to-`$zero` still reaches the overflow check; and arithmetic exception arms return immediately after signaling. ADD/SUB also return immediately so later generated statements cannot overwrite the exception vector.

Run the isolated verifier with an explicit path to the pinned PS2Recomp checkout:

```sh
python3 tools/recomp/verify_translator_semantics.py --source-root /path/to/PS2Recomp
```

The verifier rejects a different Git commit or any mismatch in the two source SHA-256 values. It checks SHA-256 pins for the unchanged FunctionEmitter, ControlFlowEmitter, and runtime exception/call-dispatch sources, stages only the two modified translator files in a temporary directory, applies the patch there, and checks the candidate file hashes. It extracts the actual `fmt::format` templates from the patched source, expands the reviewed instruction operands, then compiles and runs those generated snippets under Clang UBSan. It also compiles a separate synthetic edge-grid/reference check and confirms that the original four 64-bit templates still trigger UBSan while safe controls pass.

Focused tests are discoverable from the usual `tools` test directory. Set `PS2RECOMP_SOURCE_ROOT` explicitly; there is no repository- or scratch-specific default:

```sh
PS2RECOMP_SOURCE_ROOT=/path/to/PS2Recomp python3 -m unittest tools.test_translator_semantics -v
python3 -m unittest discover -s tools -p 'test_*.py'
```

The checked controls cover 289 directed operand pairs, five signed immediates, 100,000 deterministic randomized cases, ADDI-to-zero overflow and non-overflow, exception returns in a delay slot, and a bounded caller/callee propagation path. The call-flow audit confirms that `dispatchGuestBranch` preserves a callee's exception vector (it only substitutes call fallthrough if PC remains at entry) and that generated DirectCall/IndirectCall callers return when dispatch reports a non-fallthrough transfer.

This patch and verifier do not modify the supplied PS2Recomp checkout, emit game code, run original routines, or use an emulator. Synthetic register/runtime support validates the extracted arithmetic templates; it is not a full runtime build. ADD32_OV and SUB32_OV are modeled with defined widened arithmetic in this harness, so full runtime integration must also use `defined-overflow.patch`. No whole-translator or whole-game equivalence claim is made. The patch review’s Jev escalation remains preserved in `notes/evidence/fr2-translator-semantics/jev/` for parent review.
## Packed-register shuffle experiment

`shuffle-lanes.patch` corrects PEXEW, PEXCW and PROT3W word mappings in the pinned upstream revision. The low-to-high source-word orders are `[2,1,0,3]`, `[0,2,1,3]`, and `[1,2,0,3]`, respectively, following Sony's explicit Operation definitions and the pinned PCSX2 interpreter. The patch changes two runtime macros and two emitted templates; it preserves word 3.

Run the pinned-source verifier against an isolated pristine upstream checkout with a fresh output directory:

```sh
python3 tools/recomp/verify_shuffles.py --upstream /path/to/PS2Recomp \
  --output /path/to/fresh-shuffle-evidence --sse2neon /path/to/sse2neon
```

On an x86 host, omit `--sse2neon` to use its native SSE2 intrinsics. On the current ARM host, the verified run used the pinned bundled SSE2NEON dependency from the native generator build. The verifier preserves commands, compiler/probe logs, extracted templates, and result hashes. It rejects modified input sources or patches before compiling. Four lane basis vectors and 10,000 seeded random vectors cover distinct/in-place registers, reads from register zero, and suppressed writes to register zero. Each operation performs 40,016 comparisons. Baseline mismatches are mandatory negative controls; the candidate must have zero mismatches and no sanitizer diagnostics.

This is a synthetic translator check. It executes no game routine and proves neither full translator behavior nor game equivalence. Evidence, primary references, review dispositions, and static site counts are in `notes/evidence/fr2-mmi-shuffles/`. The patch and harness use GPL-3.0-only; see `LICENSE`.

## Remaining packed-register operations

`verify_mmi_packed.py` pins pristine PS2Recomp commit `c5a9d02573410a2085a4b4b831b0b68ba3515440`, checks the runtime header and translator-helper hashes, and extracts 13 packed-register templates. It also pins the `sse2neon.h` dependency hash because the verifier is currently run on Apple Silicon. The output directory must be new; the verifier writes extracted templates, exact compiler argv, logs, and result metadata there.

```sh
python3 tools/recomp/verify_mmi_packed.py \
  --upstream /path/to/PS2Recomp \
  --fresh-output-dir /path/to/new-packed-mmi-results \
  --sse2neon /path/to/sse2neon-include-directory
```

The synthetic probe covers PCPYLD, PCPYUD, PCPYH, PEXTLW, PEXTUW, PEXTLH, PEXTLB, PAND, POR, PNOR, PXOR, PSUBB and PSUBW. It checks source/destination alias modes and zero-register reads/writes against an independent byte/word reference across basis, boundary/pattern and seeded random inputs. This validates only the extracted host-vector expressions and tested register model; it says nothing about instruction decoding, flags, timing, full emulator behavior or game equivalence. The focused source guard and private-checkout probe tests are discoverable with `python3 -m unittest tools.test_recomp_mmi_packed -v`. Evidence, source hashes, superseded harness results and Jev dispositions are in `notes/evidence/fr2-mmi-packed-operations/`.
