# Fixed prerequisite precedence repair

Spec #5 AC02 requires: “A contradiction or mismatch takes precedence over
missing evidence.” The final review found that newly introduced prerequisite
checks sometimes returned incomplete before examining an available fixed input.
This repair scans available evidence for the known contradictions and defers
absence until those checks finish. Receipt input identities include available
files, even when a counterpart is missing.

The bounded controls cover Qt Core absent with changed Gui; lifecycle observation
or previous provenance absent with changed source; one source absent with changed
sibling source; observation metadata absent with changed EE, wrong boundary, or
a saved instruction differing from raw bytes; RPC EE absent with changed STREAM
or malformed packet; and frontier EE/ROM absent with changed pinned module or
malformed available ROM. Missing-only controls remain incomplete. The observation
boundary scalar validation has one fixed expected map shared by the CLI and
reconciliation function.

No guest execution, source ownership, protocol expansion or matching credit is
introduced. The Qt qualification, parent RPC handoff inventory and lifecycle
loader/alias/caller prerequisites retain their incomplete dispositions.

The final [Standards review](standards-review.md) and [Spec review](spec-review.md)
independently inspect merged source revision `9c4f9fa` and execute the combined
controls. Their recorded commands pass; the [independent real controls](independent-controls.json)
bind fresh RPC/frontier receipt identities to that revision. Both reviewers
explicitly disposition the four contradicted Jev claims for the tested cases.
The original gate, thresholds and probability distributions remain unchanged
and escalated; no automatic acceptance or full-parent completion is asserted.

## Reproduction

From the repository root, the focused check below ran 88 tests with three skips:

```sh
PYTHON=/Users/Nicolas/Documents/github/hermes/coder-prompt-evals/.venv/bin/python \
  tools/check.sh test_headless_oracle test_misc3d_lifecycle test_misc3d_contract \
  test_misc3d_lifecycle_observation test_compiler_probe_recipe test_matching_ranges \
  test_rpc_contracts test_rpc_handoff_inventory
python3 tools/ip_rails.py --tree
git diff --check
pyright tools/misc3d_lifecycle.py tools/test_misc3d_lifecycle.py \
  tools/misc3d_lifecycle_observation.py tools/test_misc3d_lifecycle_observation.py \
  tools/check_rpc_contracts.py tools/test_rpc_contracts.py \
  tools/inventory_rpc_handoffs.py tools/test_rpc_handoff_inventory.py
```

The latter type command reports zero errors. Headless typing retains 14 existing
diagnostics. `pyright tools/headless_oracle.py tools/test_headless_oracle.py
--outputjson` reproduces the current diagnostics; the same command against those
files and directly imported helpers from integration baseline
`fe44c0c0357fb988ee24b657dd0f473734bdf3b8` reproduces the same messages and rules.
The saved baseline/current JSON and comparison remain under
`/Users/Nicolas/Documents/github/hermes/fr2-implementation-context/precedence-evidence/`.

`checks.json` retains actual RED/GREEN and focused logs. The frontier RED control
initially used a lowercase spelling in its diagnostic assertion; the pinned
program name is `STREAM.IRX`, corrected before the final passing check.
`rpc-controls.json` records exact commands and exit codes for real static bindings
with locally generated packets. The fixed child positive/malformed/unsupported
controls remain 0/1/2; with missing EE they return 2/1/2. The full fixed 24-module
frontier returns 2. Receipt directories are preserved outside the worktree at
`/Users/Nicolas/Documents/github/hermes/fr2-implementation-context/precedence-controls/`.
Only identities and metadata are retained here; no executable or packet payload
is published.

## New judgment and independent disposition

`gate-input.json` contains the actual narrow raw code/test diff and evidence sent
once to Jev; `gate-result.json` is its complete unmodified result. The gate
escalated with safe-to-apply 0.15 and composite 0.561625. It marked lifecycle
provenance, observation, RPC combined controls and frontier claims contradicted
at confidence 0.51, 0.67, 0.49 and 0.73 respectively. Its correctness rubric
confidence was low across the changed files. The focused test count was verified
at confidence 0.91. These outcomes remain visible; no gate retry or replacement
was performed. Independent review of the final patch and combined controls is
required to disposition these judgments before publication. Earlier gates and
their dispositions remain unchanged in their original evidence directories.
