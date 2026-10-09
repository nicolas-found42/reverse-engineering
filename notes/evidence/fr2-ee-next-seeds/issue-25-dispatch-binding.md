# Issue #25 dispatch-domain evidence binding (AC10, AC30)

Parent: [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23)
(reconstruct all game-owned EE ranges with evidenced data and ABI contracts).
This ticket blocks #23; it claims no game-owned range and no compiler result
(non-goals: #23 ownership, #8 compiler, no game-owned claims from code-shape).

## Criterion 1 — inventory (code-shaped != game-owned)

- `tools/dispatch_inventory.py` joins `verify_text_denominator` classification,
  `verify_text_references` static references, and `jump_table` switch profiles
  into one corpus/revision-bound inventory. Every unlisted span row carries
  measured classification, incoming references, reason, and falsifier; every
  dispatch row pins site/table/count/targets with its domain
  (`owned`/`single_span`/`split`) and falsifier. Recognized switches whose
  table is outside any unique allocated data section are retained as
  `refused_dispatches` rows (site/table/count/reason/falsifier), never
  silently dropped.
- Unreferenced code-shaped spans stay `unresolved`; the tool's claim limits
  state that classification and references are structural and do not establish
  ownership, identity, or behavior.

## Criterion 2 — reconciliation (save/reopen, isolated copies)

- Guard `tools/ghidra/experimental/CreateEeCandidateV5.java` snapshots every
  saved function name/source/body, all instruction address/text/bytes, defined
  data, initialized memory, references, and call graphs before the transaction,
  and asserts them unchanged after (count grows by exactly the batch size;
  listing delta equals newly decoded words).
- `export_verify.sh` reopens the saved project read-only; `post_seed.py` /
  `post_batch.py` reconcile the new export against the pinned baseline
  (the retained receipts identify the checked candidates).
- Retained receipts: `fr2-ee-next-seeds/00200d10-reconciliation.json`,
  `batch-g3-candidates/reconciliation.json` + `root-export-check.json`,
  `fr2-ee-unresolved-audit/recovery/` (three-seed union), and the
  `fr2-dispatch-pair` containment receipts (compared entries, memory, data,
  and C-file changes).

## Criterion 3 — controls (relaxed guard cannot silently admit)

- Non-returning last switch case: the walker (`seedlib.py`), the batch config
  generator (`make_batch_config.py`), and the independent checker
  (`check_batch_config_root.py`, which re-derives without importing the walker)
  all reject a terminal transfer that is not the last return, a pinned tail
  jump, or a jump to a shared (reached JR RA) return. Positive control (jump to
  shared return walks) and negative control (self-loop rejects) each exist in
  `test_pipeline_walker.py` and `test_batch_switch_config.py`; the checker
  additionally rejects forged configs hiding a terminal loop.
- Noreturn-call / delay-slot: delay-slot words accept only linear flow
  (control/trap in a delay slot rejects; dual-context words reject). A terminal
  `JAL` requires the exact `CALL_TERMINATOR` shape with null fallthrough and a
  decoded callee body without terminal flows (`pinnedNoreturnCall`); the only
  body relaxation admits pinned post-delay NOP omissions at site+8
  (`bodyDeltaIsPinnedNoreturnNops`). All paths are exercised by the
  Ghidra-API guard test (`CreateEeCandidateV5GuardTest`, via
  `test_ee_candidate_v5.py`).

## Criterion 4 — bindings and retained unknowns

- Accepted discoveries: gap-fill batches `g1`/`g2`/`g3` (method + hold-out
  basis in each bundle README), the two bounded
  dispatch reconstructions at `001fbe48`/`001161a8` (`fr2-dispatch-pair`,
  Jev-verified containment), and the `00200d10` / three-seed union candidates
  (provisional, caller-evidenced).
- Ownership evidence: every candidate edge is recorded as provisional static
  structure; the overclaim "the saved functions are the original game functions"
  is explicitly unsupported/contradicted in the retained `jev-verify-note.json`.
  No recovered original identity is claimed anywhere.
- Retained unresolved/failed: unreferenced code-shaped spans after `g3`;
  anchored spans blocked by guard limits; residual computed-JR sites classified in
  `jump-table-pipeline-review/residual-recognizer-measurement.json`;
  `failed-attempt-*`, `failed-attempt-untagged-NOTE.txt`,
  `broad-disassembly-superseded.json`, `pair-only-superseded.json`, and the
  overwritten first CFG report (hash retained, provenance loss recorded).

No game code was executed. Generated C, full inventories, and Ghidra projects
remain in ignored local storage.

## Reproduction and historical scope

```sh
bash tools/check.sh test_dispatch_inventory test_pipeline_walker test_batch_switch_config test_ee_candidate_v5
```

The command checks the public inventory and synthetic guard controls. The
save/reopen and discovery receipts above record historical local observations;
this note does not certify their counts against the current corpus/revision.
Reproducing those observations requires the corresponding ignored Ghidra
projects and static exports, and the bundle commands named in their READMEs.
