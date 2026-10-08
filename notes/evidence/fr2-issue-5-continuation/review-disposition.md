# Landing review disposition: staged continuation diff

Branch `codex/feature/issue-5-integration` at `98dc02b` (post-merge of PR #36).
The staged diff adds the misc3d loader/terminal, GNU linker layout, compiler
provenance and oracle dependency source frontiers, extends the aggregate
checker with six child checks and malformed-receipt retention, and excludes
the three preexisting experimental WIP files (`tools/ghidra/experimental`
modification and its two untracked companions stay uncommitted).

## Executed verification (this session, fresh)

```sh
PYTHON=/Users/Nicolas/Documents/github/hermes/coder-prompt-evals/.venv/bin/python \
PS2RECOMP_SOURCE_ROOT=$PWD/.scratch/mesh/codex-root/PS2Recomp \
  tools/check.sh test_compiler_provenance test_linker_layout \
  test_misc3d_loader test_oracle_dependency_sources test_completion
# -> Ran 67 tests in 65.194s, OK

PYTHON=... tools/check.sh            # full suite
# -> Ran 749 tests in 165.788s, OK, exit=0
#    (2 CI-mode skips of NEEDS_LOCAL_INPUTS modules because CI=true in this
#    shell; the historical local run had 711 tests, 0 skips)

pyright <16 staged/changed Python files>   # -> 0 errors, 0 warnings, 0 informations
python3 tools/ip_rails.py --tree           # -> exit=0

python3 tools/completion.py games/ford-racing-2 \
  --assembler .scratch/mesh/codex-root/binutils-dvp-build/gas/as-new \
  --objdump .scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/aggregate-fresh-20261008
# -> exit=2, status incomplete; AC01/AC07/AC16/AC18 pass, 28 incomplete,
#    no child failure; ledger 60 attributed/matched game-owned bytes,
#    3,506,988 unresolved bytes, 0 substitutes
#    receipt 20261008T221416Z-96198163dd4a400fad0a6fd6a400e64d
```

## Jev landing review

Per-file `jev_review` over the staged code diff (payloads regenerable from
`git diff --cached` at this commit; full distributions retained in
[jev-review-landing-result.json](jev-review-landing-result.json)):

| Group | Files | Action | Composite | safe_to_apply | Limiting rubrics |
| --- | ---: | --- | ---: | ---: | --- |
| A (completion, compiler provenance, oracle sources) | 7 | escalate | 0.795 | 0.49 | test_gap; blast_radius (test_completion, oracle pair) |
| B (linker layout, misc3d loader, reconstruction source) | 12 | escalate | 0.748 | 0.46 | test_gap; spec_match (fixture, packages, test_misc3d_loader, headers) |

Correctness scores were 1.45-1.84 and spec_match 1.40-1.83 (of 2); the
escalation is driven by low-confidence `test_gap` (confidence 0.00-0.46) and
middling `blast_radius`, not by a contradicted correctness claim.

## Independent disposition of the escalation

The `test_gap` concern was investigated rather than retried unchanged:

1. `jev_verify` of "test_completion.py exercises the new child wiring,
   mismatch precedence and malformed-receipt retention, and VU entry failure
   stays separate from AC16": **verified**, supports 0.98 / contradicts 0.02,
   confidence 0.97.
2. `jev_verify` of "each new tool module ships positive/negative/incomplete
   tests (11+18+16+7 methods) and the staged evidence retains executed
   control receipts": **verified**, supports 0.98 / contradicts 0.01,
   confidence 0.97.
3. `jev_verify` of the checks-green claim: first attempt **unsupported**
   (0.41 supports) because the evidence lacked the process exit code; a
   second attempt with imprecise "implied" wording split 0.45/0.55; the
   final attempt with the shell-observed `exit=2`, the receipt status, and
   the code-grounded `write_result` mapping `{'pass': 0, 'fail': 1,
   'incomplete': 2}` ([evidence_common.py](../../../tools/evidence_common.py))
   returned **verified**, supports 0.78 / contradicts 0.21, confidence 0.67
   (action review, below auto-accept; distribution retained).

Executed evidence contradicts the `test_gap` reading: 67 focused tests and
the 749-test full suite pass on the staged tree, and each new CLI ships
executed positive/negative/incomplete control receipts. The escalation is
dispositioned as a diff-only-context confidence artifact. No gate is weakened
and no matching credit is added by this diff; AC01/AC07/AC16/AC18 remain the
only passing criteria and the parent stays incomplete.

Fetched-content screening: the live issue #5 body screened `pass`
(injection 0.17, substance 0.99, relevance 0.98). The handoff document
screened `review` (injection 0.68, below the 0.75 block threshold);
agent-side inspection found no credential requests, tool redirection or
operating-rule overrides, so its separable task data was retained.

This review supports landing the staged continuation. It does not support
closing #5, #8, #9, #21, #22, #35 or #37.
