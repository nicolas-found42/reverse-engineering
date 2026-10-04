# Next EE function-seed crosswalk

The first section below records a **historical, read-only scan** of the reopened 3,841-function Ghidra export against the original ELF and pinned PS2Recomp function-source tree. The requested priority category—**nonzero, defined but unowned instruction entries with exact saved direct incoming calls**—had no matches in that snapshot. Across 32,788 unowned decoded instruction addresses and 13,839 saved unconditional-call references, there are zero call targets in the unowned-instruction set that also began a PS2Recomp generated interval. The 3,838-function baseline contributed zero direct saved calls to then-missing entry addresses.

Three weaker follow-up leads exist. All are in `.text`, have nonzero first words, and have exact saved direct callers from the newly added provisional functions at `001fbfb8` and `001fc118`. All three targets are **undefined in Ghidra**, rather than defined/unowned, and none has a baseline function caller. Their PS2Recomp interval comments are contiguous, start exactly at the call target, and every commented raw instruction word matches the original ELF:

| Target | Saved callers/sites | PS2Recomp interval | Words / bytes | First word |
|---|---|---|---:|---|
| `00200d10` | `001fbfb8:001fc018`; `001fc118:001fc18c`, `001fc1fc` | `[00200d10, 00200de0)` | 52 / 208 | `27bdffd0` |
| `00200de0` | `001fbfb8:001fc04c`; `001fc118:001fc210` | `[00200de0, 00200e70)` | 36 / 144 | `27bdffe0` |
| `00200e70` | `001fbfb8:001fc008`, `001fc02c`; `001fc118:001fc174`, `001fc1dc` | `[00200e70, 00201128)` | 174 / 696 | `0080382d` |

At the time of that scan these were evidence-backed leads, not recovered functions. Every listed callsite belonged to a provisional caller, so no target had an independently established incoming caller. Jev Find ranked `00200e70` first at `0.50` but gave only partial existence confidence `0.53`; Jev Rerank favored `00200d10` at `0.62`, then `00200e70` at `0.56` and `00200de0` at `0.41`. Those rankings were advisory.

The exact historical input and source pins, callsites, interval-file hashes, scan counts, and raw-word crosswalk checks are in [next-seeds.json](next-seeds.json). The source-only PS2Recomp search receipts remain in scratch: `jgrep-function-intervals.json` (hit `ps2xRecomp/src/lib/function_emitter.cpp:71–130`, SHA-256 `02317983878b82f066990b3b511e7012c3101be73e737276edc060a27b7f475f`) and `jgrep-function-entry-discovery.json` (hit `ps2xRecomp/src/lib/elf_parser.cpp:1612–1671`, SHA-256 `f530fb125e9e2bca6b81b80e79c6f42a2ba108405e1f35151c8bb5cc396c7d43`). The historical scan script and full output are in `.scratch/mesh/codex-audit/next-seeds-01/`; its first report had an integer/string address comparison bug, preserved as `scan-result-attempt01-bug-failed.json`, and was corrected before the durable 3841 result.

The generator source is PS2Recomp base revision `c5a9d02573410a2085a4b4b831b0b68ba3515440` with the recorded working-tree patch hash in the JSON. jgrep located its fallback entry scanner, which adds starts from direct JALs and other address heuristics, and its emitter's interval comment. Therefore the boundary listing is a second tool's static hypothesis, not fully independent evidence of function identity; the exact per-word ELF comparisons validate only that the emitted instruction comments correspond to the bytes. This does not prove PS2Recomp semantic equivalence, correct original function identities, runtime reachability, or whole-game completeness.

Jev Find and Rerank disagreed on the top historical fallback target. Jev Verify's broad batch had two contradicted claims and two review flags; those outcomes remain preserved. A focused follow-up verified all three core fallback facts with no review flags. The original broader batch and focused receipts are in [`jev/`](jev/). The first jgrep command failed to search files under a hidden `.scratch` path; that exact failed invocation and its observed output are preserved in scratch beside the successful source receipts.


## Follow-up: provisional `00200d10` closure

The candidate was subsequently added in one guarded transaction to a fresh copy of the 3841 project, producing a reopened 3842-function export. See [00200d10-preflight.md](00200d10-preflight.md) for the bounded CFG and transaction evidence. The final reconciliation has **17 checks**. The root's independent validation is `.scratch/mesh/codex-root/root-ee-3842-validation-01.json` (SHA-256 `fe8d595d173df212e30e79ce3cc655d3cee226a225d23cce0b70f70f2ffa4939`): it recomputed 7,683 C artifact hashes, confirmed the three expected caller-label substitutions, preserved prior function names/bodies/instruction text and bytes plus memory/string inventories, and matched all 51 new words to the ELF. These checks support only the documented static candidate; they do not establish identity or semantics.

The first read-only CFG report for `00200d10` had SHA-256 `773d149608167f900e8980002a3dbcd41fc7bfb6ab3487eb2d73946a5715a428`. The report was corrected after finding that the scratch traversal treated unconditional `beq $zero,$zero` at `00200d70` as having a fallthrough. The corrected report is the one cited in the preflight below; the first JSON was overwritten and could not be recovered from the workspace search. No Ghidra project data was changed during that CFG-only correction. The later guarded Ghidra candidate transaction is documented separately.


The refreshed 3842 crosswalk and current read-only follow-on proposals are in [next-seeds-3842.md](next-seeds-3842.md). They do not meet the original defined/unowned-target priority category and do not justify a new Ghidra mutation without a separate guard review.

Bounded results are now saved here: [reconciliation](00200d10-reconciliation.json), [root validation](root-3842-validation.json), [verifier summary](3842-verifier-summary.json), and [exact command record](00200d10-commands.md). The generated C, full instruction inventories, original ELF and Ghidra projects remain in ignored local storage. The root recovered both historical gate invocation/result pairs; the preflight explains the unresolved older source argument and the incorrect historical gate tests-count.

## Later guarded checkpoints (3,843 to 4,718 functions)

Each bundle records one isolated transaction on a byte-identical Ghidra project copy, the independent re-derivation of its config from the raw ELF, the read-only re-export, and a reconciliation against the pinned previous export. All are provisional static candidates; none claims original identity, behavior or runtime reachability. Single-seed bundles use guards V3/V4 (`tools/ghidra/experimental/CreateEeCandidateV3.java`, `...V4.java`); batch bundles use V5. Pipeline scripts are recorded under `tools/ghidra/experimental/pipeline/`.

| Function count after | Bundle | Functions added |
| ---: | --- | ---: |
| 3,844 | [`00200e70-candidate`](00200e70-candidate/README.md) | 1 |
| 3,845 | [`001ff038-candidate`](001ff038-candidate/README.md) | 1 |
| 3,846 | [`001feb80-candidate`](001feb80-candidate/README.md) | 1 |
| 3,847 | [`001ff270-candidate`](001ff270-candidate/README.md) | 1 |
| 3,848 | [`001ff140-candidate`](001ff140-candidate/README.md) | 1 |
| 3,849 | [`001ff460-candidate`](001ff460-candidate/README.md) | 1 |
| 3,850 | [`001ff520-candidate`](001ff520-candidate/README.md) | 1 |
| 3,851 | [`001ffbf0-candidate`](001ffbf0-candidate/README.md) | 1 |
| 3,852 | [`001fed80-candidate`](001fed80-candidate/README.md) | 1 |
| 3,853 | [`001ff9c8-candidate`](001ff9c8-candidate/README.md) | 1 |
| 3,854 | [`00200408-candidate`](00200408-candidate/README.md) | 1 |
| 3,855 | [`001fef28-candidate`](001fef28-candidate/README.md) | 1 |
| 3,856 | [`001ffec8-candidate`](001ffec8-candidate/README.md) | 1 |
| 3,857 | [`001fce10-candidate`](001fce10-candidate/README.md) | 1 |
| 3,858 | [`001ffa50-candidate`](001ffa50-candidate/README.md) | 1 |
| 3,859 | [`00201a48-candidate`](00201a48-candidate/README.md) | 1 |
| 3,860 | [`001fd060-candidate`](001fd060-candidate/README.md) | 1 |
| 3,861 | [`001fd768-candidate`](001fd768-candidate/README.md) | 1 |
| 3,862 | [`002018d8-candidate`](002018d8-candidate/README.md) | 1 |
| 3,863 | [`001feda0-candidate`](001feda0-candidate/README.md) | 1 |
| 3,869 | [`batch-trial-candidates`](batch-trial-candidates/README.md) | 6 |
| 4,346 | [`batch-all-1-candidates`](batch-all-1-candidates/README.md) | 477 |
| 4,542 | [`batch-r2-candidates`](batch-r2-candidates/README.md) | 196 |
| 4,718 | [`batch-r3-candidates`](batch-r3-candidates/README.md) | 176 |
| 5,130 | [`batch-g1-candidates`](batch-g1-candidates/README.md) | 412 |
| 5,243 | [`batch-g2-candidates`](batch-g2-candidates/README.md) | 113 |

The three large batches add PS2Recomp function-table entries that were not saved functions. Their evidence per seed is table membership plus raw-word CFG validation; where available, direct JAL callers and non-call (address-taken) references into the entry are recorded and verified unchanged. In 96 saved functions' decompiled output (64, 26 and 6 across the three batches) address-of-label stores and pointer labels are now printed with the new function symbols (many are table-initializer functions storing code addresses), which is consistent with these being address-taken code but does not identify them. The V5 guard reviews escalated; see each bundle's `jev-review-*` receipts and root dispositions.

Batch `g1` (2026-10-04) differs in kind: its 412 candidates are gap-fill seeds from executable bytes no saved function owned, not PS2Recomp table entries, and none has a known direct caller. Their evidence classes (closed control-flow walk, stack-frame consistency, boundary layout, static reference) and the Jev decisions behind the set are in the bundle README.
