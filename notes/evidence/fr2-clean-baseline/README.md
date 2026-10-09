# Ford Racing 2 PAL — clean static baseline

Canonical specification: [issue #5](https://github.com/nicolas-found42/reverse-engineering/issues/5).

**Current accepted source: `d14fe24278ad66a479ccd4d70ede7150a5521fef`** (squash merge of PR #42). The
documented aggregate ran on a clean detached checkout of that revision using the existing local
corpus, DVP assembler/objdump and compiler-tools inputs, and exited **2/incomplete**. This is a
recorded baseline, not game completion.

- AC01, AC07, AC16 and AC18 pass; the other 28 criteria remain incomplete.
- 2,171,407 initialized + 1,335,641 zero-fill = 3,507,048 total load-image bytes.
- **60** attributed game-owned bytes are freshly source-built and matched; **3,506,988** remain
  unresolved; **0** substitute bytes are attributed. The attributed-only fraction is not
  reconstruction progress.
- Eight VU encodings compare exactly. Entry/state maps remain incomplete.
- Eleven independent fresh child receipts were created at each revision. No guest/emulator
  execution was performed at either revision.
- `python3 tools/validate.py --revision d14fe24278ad66a479ccd4d70ede7150a5521fef` passes IP,
  hygiene, Ruff and the portable suite (785 tests, 33 skips, three excluded modules) against tree
  `6fe93267b01ca701ceecf66030503bb072c47add`.

The identical statuses and ledger were measured twice: first pre-merge at
`717f78df689be4e16ddc891b2def18cbda3ce79d` (`tools/check.sh` 756 tests, OK, 33 skips, three excluded
modules; tracked-tree IP check exit 0), then again after the merge. The pre-merge `.md` snapshot and
its commands are retained here as a dated record; the current rows are in the current matrix.

## Files and authority

[acceptance-matrix.md](acceptance-matrix.md) lists every canonical criterion with observed status,
exact command/receipt references, missing prerequisites, falsifiers and tickets;
[acceptance-matrix.json](acceptance-matrix.json) adds the full canonical requirement text and exact
commands plus receipt SHA-256 per row. [commands.md](commands.md) spells out every command and full
receipt hash. [verification.json](verification.json) records observed checks, the application
judgment-policy smoke and protected WIP identities.
[merged-revision-verification.json](merged-revision-verification.json) is the post-merge run.
[input-identities.json](input-identities.json) records the discovered local inputs; no binaries are
included. [semantic-experiments.json](semantic-experiments.json) retains full Jev distributions,
question/evidence hashes, labeled outcomes, thresholds, latency and token usage.
[baseline-claims-verification.json](baseline-claims-verification.json) preserves the final factual
judgment, including two escalations; independent dispositions are recorded separately rather than
retried for approval. [pr42-disposition.json](pr42-disposition.json),
[review-smoke.json](review-smoke.json) and [original-diff-bindings.json](original-diff-bindings.json)
record the PR #42 review, its independent reproduction and its exact-revision validation.
[tracker-publication.json](tracker-publication.json) and
[tracker-merge-verification.json](tracker-merge-verification.json) record the tracker updates and
their readback. [final-baseline-report.json](final-baseline-report.json) is the delivered summary.
[application-policy-smoke.json](application-policy-smoke.json) exercises the repository's own
fail-closed judgment policy. [live-judgment-experiments.json](live-judgment-experiments.json) and
[spec-review-raw.json](spec-review-raw.json) retain the standalone reviewer records. The pre-merge
dated snapshot is [acceptance-matrix-717f78d.md](acceptance-matrix-717f78d.md) with
[commands-717f78d.md](commands-717f78d.md).

Original historical/structural receipts remain in the repository. They were not imported to
manufacture a current acceptance result. Fresh child passes remain narrower than their incomplete
parents. In particular the documented aggregate does not supply `--packet`, so its STREAM framing
child is incomplete at both revisions; prior standalone packet receipts keep their historical
authority.

## Execution frontier

Native dependency edges and assignees are retained in [acceptance-matrix.json](acceptance-matrix.json).
Unassigned agent leaves: #12, #22, #25, #26, #27, #28, #29, #31 and #37. #8 and #13 have no open
blockers but are assigned; #21 is a human package/source provenance frontier. #35 is blocked by #37;
#24 by #35; final #5 by #34. No ticket was closed or reassigned from this baseline.

The next unassigned task in canonical map order is **#12**: bind an evidenced required SDK substitute
range and its actual reconstructed-game consumer interface, then build/link the pinned ps2sdk
replacement with retained source/dependency/output identities and mutation/missing-output controls.
Reuse the existing bootstrap; an upstream sample cannot finish this ticket.

## PR #42

Exact tested head `a8c8798807af81927cfab975530ac2445eec6f27`, base
`717f78df689be4e16ddc891b2def18cbda3ce79d`, squash-merged at
`d14fe24278ad66a479ccd4d70ede7150a5521fef` on owner decision after exact-head checks passed and
independent review surfaced consequential findings. Original seven patch escalations, the scoped gate
and the low-confidence factual verification are preserved unchanged in
`../fr2-setup-reliability/review-001.json` through `review-007.json` and
`../fr2-setup-reliability/review.json`, and all 24 original reviewed raw file diffs match the actual
PR diff hashes. The consequential findings are tracked as issue **#43**; that bug is open and its
acceptance criteria are unmet. This directory records them rather than retracting any original
judgment.

## Reproduce

Run from the repository root at the recorded revision with the unchanged local PAL corpus and the
declared local tool inputs recorded in [RE-SETUP](../../../docs/RE-SETUP.md). Select a fresh output
directory; previous receipts are never overwritten.

```sh
python3 tools/completion.py games/ford-racing-2 \
  --assembler <local dvp as-new> \
  --objdump <local dvp objdump> \
  --compiler-tools <local compiler-tools directory> \
  --output <fresh directory>
python3 tools/validate.py --revision d14fe24278ad66a479ccd4d70ede7150a5521fef
```

Current aggregate receipt SHA-256 `ebb63100132f995d4fa34c53fb08780a6a868f07c3159c679f1c2b9224b2cda7`;
pre-merge aggregate receipt SHA-256
`2aab9ae17f36311f6a91543b53efb673aa52955ddcc23e5385dbe6d26db5fdfb`. Receipt command lines inside the
JSON records carry this machine's declared input paths; they contain no corpus bytes, credentials, or
tokens. Exact local paths for the DVP tools and compiler bundle are the machine-specific inputs that
`docs/RE-SETUP.md` describes as a local recipe.

No source-code reconstruction change, new inference dependency, game-completion claim, guest launch,
or activation is part of this baseline. The primary WIP and the untracked ecosystem survey are
retained.
