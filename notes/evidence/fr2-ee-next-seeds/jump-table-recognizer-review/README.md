# Option B first-slice review checkpoint, 2026-10-04

Status: **review escalated; implementation incomplete and uncommitted**. This checkpoint covers only `tools/jump_table.py` and its tests. The walker, schema-2 generator, independent checker, Java guard, switch hold-out measurement, and batch g4 have not been changed or run. No saved functions or references were added; the gp-g2 baseline remains 5,454 saved functions.

The draft recognizer was tightened to reject reversed bounds branches, an index overwritten after its bound, control transfers within the pattern, bounds tested after an in-place scaling shift, and unmodelled register writes. A table reader maps the entire bounded table through one allocated, non-executable, file-backed PROGBITS ELF section. Seventeen focused tests pass. The fixed-source full suite ran **475 tests, OK with one skipped** (`full-tests-slice1.log`). Test success does not establish that the recognizer is safe.

The raw-byte scan over the existing 408 gap seeds found 29 distinct computed-JR sites; the tightened profile recognized **24**, and every recognized table had aligned targets within `.text` (`recognizer-measurement.json`). Five recognized tables contain targets already owned by saved functions. The conservative first integration policy is to reject such candidates, including saved entry targets; pinned switch tail transfers need separate evidence. Jev selected that policy with probability 0.62, confidence 0.55, and no contradicted requirement (`jev-targets-decision.json`).

The five unrecognized sites are `0011830c` (unmodelled COP1 instruction), `0011bae0` and `00123cb4` (branch-likely bounds forms), `00175cbc` (no local SLTIU bound in the window), and `0020ae54` (multiple branches and unresolved bound path). The last two require further static investigation; no semantics claim follows from the classification. The handoff's earlier permissive recognizer matched 26; accepting fewer sites here is a narrower supported profile, not new saved-function coverage.

## Concrete defect found after the passing tests

The independent specification review found that register zero is treated as writable when searching for the table-address definition. A synthetic `LUI $zero` followed by `ADDU base,$zero,scaled_index` incorrectly reports a table high half. `gpr0-negative-control.json` reproduces the false accept and records `failed_negative_control`. This is an implementation defect, not model uncertainty. Before committing, model GPR0 as immutable and add a regression test. The ELF reader also needs negative coverage for invalid mappings and extents before it can support guarded recovery.

The standards review found no documented-standard breaches and two minor possible smells: the callback/address-bound contract lacks a function docstring, and the result uses a plain dictionary. The specification review found one correctness defect and no additional first-slice scope creep. Neither review establishes readiness for pipeline integration.

## Jev receipts and disposition

All twelve capabilities were used for actual work; receipts are included:

- `screen`: official live TypeSafe documentation index passed (injection probability 0.02).
- `find`: located the independent schema-2 root checker; `exists_verdict=answered`, probability 0.96.
- `decide`: conservative saved-target policy described above.
- `noul`: nonlocal-bound and branch-likely hypotheses remained uncertain (0.51 and 0.73).
- `classify`: five unrecognized sites assigned to COP1, branch-likely, and unresolved-bound categories; labels guide inspection only.
- `rerank`: ordered further shape investigations. Its ranking placed the unresolved split-guard case first; this is advisory and no extension was made on that basis.
- `extract` and `audit`: suite count 475 and skipped count 1 extracted; audit passed, maximum reported wrong probability 0.08.
- `compare`: prose and measured scan summary agreed; all aspects returned `same_fact`.
- `verify`: suite and recognizer counts verified; planted original-function and universal-switch claims were unsupported. The planted claims are not conclusions.
- `review`: **escalate**, composite 0.845875, limiting `safe_to_apply=0.55`; recognizer blast-radius confidence 0.14 and test-gap concern. This review preceded the GPR0 finding.
- `gate`: **escalate**, `safe_to_apply=0.05`; all three bounded checkpoint claims returned verified, with incomplete-integration claim flagged review at confidence 0.79. The gate did not override the prior escalation.

Per the supplied handoff, escalation stops commit and integration. No push, PR, merge, original game code execution, emulator, or debugger was performed. Source files remain staged; this evidence directory is untracked. Next work, after the escalation is resolved: fix and test the GPR0 defect, extend table-reader negative coverage, review the changed evidence, then commit the first slice and continue the pre-agreed walker/config/checker/guard seams.
