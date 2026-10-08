# Independent integration review

Baseline: `98dc02b`, after PR #36 merged. The scoped working diff includes new
source/audit tools and excludes the three preexisting experimental WIP files.
The restored `codex/feature/issue-5-integration` branch continues that baseline.

## Standards

No remaining hard violations in final reviewed code. One hard finding was
fixed: changed pinned GNU IOP source inputs now fail before unrelated missing
inputs. Independent CLI replay preserves both missing GCC and changed binutils
and exits 1. Positive reconciliation passes, missing-only exits 2, unexpected
derived-tree changes fail. Linker and oracle admission repairs preserve the
same policy. Independent scoped validation passed 35 tests.

Possible Duplicated Code smell: the positive compiler inventory test repeats
ZIP/decision construction supplied by its fixture helper. This is a minor
maintenance judgment, not an acceptance defect; it is retained without changing
the reviewed implementation solely for cosmetic consolidation.

Original low-confidence Jev concerns remain in their owning evidence
directories. Independent loader observation against actual pinned corpus and
isolated inventory confirms six disjoint ranges totaling
8+52+316+52+20+88 = 536 bytes, 29 cell accesses including 11 stores, and zero new
credit. Source-audit blast radius reads pinned inputs and writes unique receipts.

## Spec

Two P2 defects were repaired and independently replayed. Missing ld/as no longer
hides changed objcopy; the checker records all tool identities first. Missing
oracle prerequisites no longer hide installed or independently admitted source
contradictions; each available pinned branch is checked before disposition.
Independent linker/oracle validation passed 25 tests. Both original
reproductions now raise `Invalid`. Subsequent independent Jev verification of
the repaired failure semantics was auto, supports .98, contradicts .02,
confidence .97 (openrouter/typesafe/jev-1.13-20260917, threshold .8).

No remaining bounded-scope defect or scope creep found. The parent specification
still requires exact compiler provenance, complete ownership/reconstruction,
EE/IOP layouts and substitutes, VU/asset/interface contracts, two clean builds,
strict runtime qualification, and final acceptance. Reviews support integrating
this scoped change and do not support closing #5.

Findings: Standards 0 remaining hard violations, 1 minor smell; Spec 0 remaining
bounded defects, 2 repaired P2 defects. Parent acceptance remains incomplete.
