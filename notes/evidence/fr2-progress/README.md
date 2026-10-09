# Structural progress snapshot

Established: [structural-ledger.json](structural-ledger.json) records a passing
load-image partition from the pinned corpus, including the one 60-byte owned
range. Its initialized and zero-fill byte totals are conserved. This run earns
zero matched bytes: no compiler or fresh build receipt was run for this snapshot.

Not established: original compiler/linker identity, complete game/SDK attribution,
whole-game reconstruction or behavioral equivalence. Archived compiler results
are linked separately in [progress provenance](../../../progress/provenance.json).

Reproduce the static inventory locally, using your own unchanged corpus:

```sh
python3 tools/matching_ranges.py corpus games/ford-racing-2 --output .scratch/progress-inventory
```

The snapshot records the command, corpus hashes, source hashes and base revision.
`source_working_tree_dirty: true` records that the new table-reading module and
corrected ADR link were present before this commit existed; exact source pins,
rather than that parent revision alone, bind this measurement. It contains only
structural measurements and identities, with no instruction bytes or generated C.

Reproduce the portable export and freshness checks:

```sh
python3 tools/repository_hygiene.py generate
python3 tools/repository_hygiene.py check
tools/check.sh test_progress_report test_repository_hygiene
```

A changed source, ownership decision, boundary record, or snapshot pin fails the
check. Re-measure and review a new snapshot when those inputs change; changing a
caller argument or importing an archived receipt cannot create match credit.
