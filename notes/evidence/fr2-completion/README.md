# Reconstruction completion command

The [implementation summary](20261008-implementation-summary.json) is the current
bounded progress record for draft PR #36. Its clean real-corpus aggregate at
source revision `9c4f9fa` exits 2: AC01, AC07, AC16 and AC18 pass, with 60
attributed/matched bytes, 3,506,988 unresolved bytes and zero substitutes.
Its recorded whole-suite command ran 711 tests, OK, with no skips or dependency
exclusions. Fresh misc3d source/observation receipts, the refused oracle
preflight, exact reproduction commands and independent review dispositions
are linked there. The additional misc3d source outputs are candidates with
zero new ownership credit; full reconstruction and behavior remain incomplete.

The historical [continuation summary](20261008-continuation-summary.json) records a clean
real-corpus run at reviewed source revision `181c705`. It exits 2, incomplete:
AC01, AC07, AC16 and AC18 pass; all remaining criteria retain their required
work. The ledger records 60 game-owned/matched bytes, 3,506,988 unresolved
bytes and zero substitute bytes. This is one source-built unit, not whole-game
acceptance. The exact aggregate and validation commands, external receipt and
log identities, and claim limits are in the summary. Whole-suite validation
ran 633 tests, OK, with the pinned source checkout configured and no skips or
missing-dependency exclusions. CI remains a separate tooling check without
these private inputs.

Run from a clean checkout with the unchanged local PAL corpus:

```sh
python3 tools/completion.py games/ford-racing-2 \
  --assembler .scratch/mesh/codex-root/binutils-dvp-build/gas/as-new \
  --objdump .scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/completion
```

Native DVP tools may alternatively be on PATH; the explicit options select
executables, never scope or acceptance thresholds. They require independent
permitted-source provenance. Compiler tools default to the declared local
`.scratch/compiler-probe-tools` directory; `--compiler-tools` may name a different
installed tool directory. The fixed exploratory recipe still chooses its
recorded candidate set, source and reference range. The generic compiler probe
cannot assign ownership. The fixed source-unit child applies the independently
recorded ADR-0005 range decision and may supply local AC07 credit, while AC05
historical compiler identification remains incomplete. The command runs
independent load-image, archive, VU, asset-contract and exploratory compiler
checks in fresh child directories and retains their
receipt/report identities. It reports all AC01–AC32 criteria from issue #5.
Reconstruction and behavioral results have separate scopes. AC25/AC26 do not
contribute static matching evidence. Missing source builds, attribution,
toolchain pins, contracts, or acceptance receipts remain incomplete.

This implementation builds and compares the first hand-written EE source unit;
it does not build the complete EE/IOP reconstruction, orchestrate a qualified
oracle, implement all subsystem contracts, or prove the full specification.
The [source integration evidence](../fr2-source-integration/README.md) records
the bounded source-to-byte result, negative control, and conserved ledger.
The [strict oracle attempt](../fr2-headless-oracle/README.md) has separate
behavioral scope and remains incomplete. Unimplemented criteria cannot be satisfied by
importing hand-written receipts, shrinking a denominator or declaring a skip.
The child commands retain their independent claims: archive structural success
does not complete asset consumers, and VU encoding success does not complete
entry/state interfaces. Asset raw/zlib accounting is not a catalog of decoded
body variants. Structural inventory alone always records zero matched bytes;
aggregate credit requires fresh independent source, decision, build, and byte
bindings. Its matched fraction is explicitly a fraction of the attributed
game-owned scope. The unresolved load-image bytes remain visible and prevent
whole-corpus completion.

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

The [2026-10-08 progress summary](20261008-progress-summary.json) retains the
observed aggregate and child receipt hashes for source revision `d572366`.
The command above returned 2: AC01, AC16 and AC18 passed; every other criterion
remained incomplete. The exploratory compiler child executed its fixed seven
candidates without operational errors and selected `ee-gcc2.96`, while AC05
remained incomplete. The inventory recorded 3,507,048 unresolved load-image
bytes and zero attributed game-owned, substitute or matched bytes. This is a
summary of that attempt, not an input that can confer acceptance on another run.

`tools/check.sh` at that revision passed 585 tests with one unittest skip; the
optional `test_research_jev_battery` module was excluded for missing
`typesafe_sdk`. The [whole-suite log](20261008-whole-suite.log) includes expected
pass/fail/incomplete fixture receipts. `python3 tools/ip_rails.py --tree`
returned 0. These checks validate the partial tooling; source builds and the
remaining whole-corpus acceptance work are still incomplete.
