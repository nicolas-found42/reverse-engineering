# Current clean PAL SLES-517.05 baseline — 2026-10-09

Canonical completion specification: [issue #5](https://github.com/nicolas-found42/reverse-engineering/issues/5).

The documented aggregate ran freshly from clean current main source
`05a685a35ae429aaddacce1a7faceb6b6438ab44`, tree
`df462a8e58bf43d1ee9d0a32f16ebfc7ae77421d`, using the unchanged local corpus and
existing DVP assembler, objdump and compiler inputs. It exited **2/incomplete**.
This is a recorded baseline, not completion of the game.

AC01, AC07, AC16 and AC18 pass. The other 28 criteria remain incomplete. The
ledger accounts for 2,171,407 initialized and 1,335,641 zero-fill bytes: **60**
freshly source-built attributed game-owned bytes match, **3,506,988** bytes
remain unresolved, and **zero** substitute bytes are attributed. Eight VU
encodings compare exactly; entry/state interfaces remain incomplete. Eleven
fresh independent children ran, with no failed child. Behavior remains
unverified; no guest or emulator was launched.

Exact-revision validation passed IP, hygiene, Ruff and the portable suite:
**792 tests run, zero failures/errors, 33 skipped tests and three excluded
modules**. The exclusions and reasons are preserved in
[test-summary.json](test-summary.json). These checks do not establish full
reconstruction acceptance.

## Acceptance matrix and receipts

[acceptance-matrix.md](acceptance-matrix.md) contains all 32 criteria, observed
statuses, exact commands, receipt identities, missing prerequisites, falsifiers
and linked tickets. [acceptance-matrix.json](acceptance-matrix.json) also retains
the unchanged canonical requirement text and native dependency/assignment
readback. [receipts.json](receipts.json) binds the fresh aggregate and every
child to its command, run ID and SHA-256. Raw corpus-bearing receipts remain
local; the public records contain identities and bounded conclusions.

Aggregate receipt: `20261009T152126Z-718499d4bc88455280610996082435eb`, SHA-256
`45d1186f03ca0fd3dbda4baa3f2ead84fe5ed12d06d2a065eabefe4da8ea2e5d`.

Historical receipts in `../fr2-clean-baseline` and
`../fr2-issue-5-continuation` remain unchanged. The current results happen to
agree with their bounded ledger; none was imported as fresh proof. Structural
reports confer no matching credit. The aggregate supplies no STREAM `--packet`,
so historical standalone packet framing cannot complete its current child.
Unmerged integration and review worktrees are outside this measured main.

## PR #42 review decision

PR #42 already squash-merged at
`d14fe24278ad66a479ccd4d70ede7150a5521fef`. Its head was
`a8c8798807af81927cfab975530ac2445eec6f27`, with base
`717f78df689be4e16ddc891b2def18cbda3ce79d`. No readiness or merge operation was
needed in this session. Its old local/remote branch was already absent.

Two independent reviews examined the actual diff, changed tests and synthetic
failure reproductions. All 24 original reviewed raw-file hashes match the
actual PR diff. The original seven Jev patch escalations and scoped gate are
preserved, with their full distributions and separate per-packet dispositions
in [standards-review.json](standards-review.json) and
[spec-review.json](spec-review.json). Both exact-head targeted replays passed
42 tests; those tests do not refute the reproduced defects.

**Consequential decision: candidate discovery isolation remains unresolved.**
Candidate discovery can accept the existing same-token backend and does not
prove the candidate instance answered. Failed-bootstrap cleanup and partial
client registration rollback also need repair; the independent doctor review
found an early failure before its cleanup guard. These are carried in
[issue #43](https://github.com/nicolas-found42/reverse-engineering/issues/43).
Continue the static completion work, while deferring candidate bootstrap and
activation until the isolation and cleanup controls are repaired. This review
does not retract the prior merge or claim the setup defects are fixed.

## Semantic policy and frontier

New baseline and frontier verification calls are bounded to the recorded
provider capacity. Full distributions, payload/evidence identities and usage
are retained in [baseline-claims-verification.json](baseline-claims-verification.json)
and [frontier-verification.json](frontier-verification.json). Low-confidence
results received independent dispositions in
[baseline-claim-dispositions.json](baseline-claim-dispositions.json) and
[frontier-claim-dispositions.json](frontier-claim-dispositions.json), without
retrying them for approval. Numerical authority remains deterministic.

The live TypeSafe confidence and citation-check documentation informed the
bounded claim/evidence separation. Choice confidence is distribution
concentration, not proof; exact identities, arithmetic, process exits and
dependency readiness stay in code. The documentation was fetched live with
HTTP because the browser reader could not open its Markdown endpoints.

Native dependency-ready, unassigned reconstruction leaves are **#12, #22,
#25, #26, #27, #28, #29, #31 and #37**. #8 and #13 are ready but assigned.
#21 is the unassigned human provenance frontier. #43 is a separate unassigned
setup defect, currently awaiting triage. #35 is blocked by #37; #24 by #35;
#23 by #8/#9/#24/#25; #5 by #34. No dependency, assignment, criterion definition
or reconstruction ticket closure changed.

The next executable unassigned reconstruction task in map order is **#12**:
build/link one evidenced required ps2sdk substitute range through its actual
reconstructed-game consumer, binding source/dependency/output identities and
changed/missing-output controls. Reuse the pinned existing installation; an
upstream sample alone does not finish #12. #43 is the next setup repair before
any candidate build or activation.

## Reproduce

Run from a clean checkout of the measured revision using the discovered inputs
in [input-identities.json](input-identities.json). Select a fresh output path.
The exact executed absolute argv and child commands are in the matrix.

```sh
python3 tools/completion.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 \
  --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new \
  --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate
python3 tools/validate.py --revision 05a685a35ae429aaddacce1a7faceb6b6438ab44 \
  --output .scratch/baseline-20261009/validation
```

Original judgments and the original ecosystem survey are hashed in
[preserved-identities.json](preserved-identities.json). The primary checkout and
unrelated WIP were preserved. This publication adds evidence, not reconstruction
source or matching credit. Screenshots are inapplicable to this static result.
