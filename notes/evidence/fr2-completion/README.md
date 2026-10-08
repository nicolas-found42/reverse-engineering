# Reconstruction completion command

Run from a clean checkout with the unchanged local PAL corpus:

```sh
python3 tools/completion.py games/ford-racing-2 \
  --assembler .scratch/mesh/codex-root/binutils-dvp-build/gas/as-new \
  --objdump .scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --output .scratch/evidence/completion
```

Native DVP tools may alternatively be on PATH; the explicit options select
executables, never scope or acceptance thresholds. They require independent
permitted-source provenance. Compiler tools default to the declared local
`.scratch/compiler-probe-tools` directory; `--compiler-tools` may name a different
installed tool directory. The fixed exploratory recipe still chooses its
recorded candidate set, source and reference range. No compiler probe supplies
ownership attribution or an exact original-compiler pin. The command runs
independent load-image, archive, VU, asset-contract and exploratory compiler
checks in fresh child directories and retains their
receipt/report identities. It reports all AC01–AC32 criteria from issue #5.
Reconstruction and behavioral results have separate scopes. AC25/AC26 do not
contribute static matching evidence. Missing source builds, attribution,
toolchain pins, contracts, or acceptance receipts remain incomplete.

This implementation is a progress verifier. It does not yet build EE/IOP
reconstruction source, launch an oracle, implement all subsystem contracts, or
prove the full specification. Unimplemented criteria cannot be satisfied by
importing hand-written receipts, shrinking a denominator or declaring a skip.
The child commands retain their independent claims: archive structural success
does not complete asset consumers, and VU encoding success does not complete
entry/state interfaces. Asset raw/zlib accounting is not a catalog of decoded
body variants. All source-built matched credit remains zero until evidenced
range attribution and builds exist.

Exit codes are 0 for a complete reconstruction, 1 for a known required mismatch,
and 2 for missing required work without a known mismatch. A known changed corpus
input takes precedence over other missing inputs. The report seam has a positive
synthetic control for a nonempty complete ledger, a negative mismatch control,
and incomplete/synthetic/empty-scope controls. These test reporting policy; they
cannot confer real-corpus acceptance. CLI controls exercise missing/changed
inputs, immutable repeat attempts, and rejection of scope/skip/denominator flags.

```sh
tools/check.sh test_completion test_matching_ranges test_matching test_corpus_binding
```

Every run retains its own result and Markdown report. Previous successful or
incomplete attempts are never overwritten. Child executable/manifest identities,
current source revision, and tool-script hashes are retained; the source dirty
flag distinguishes an uncommitted experiment from a clean checkout receipt.
