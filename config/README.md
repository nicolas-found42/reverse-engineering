# Recorded decision tables

These tables are repository decisions, not inputs a gate caller can override.
`tools/recorded_decisions.py` reads their fixed paths and checks their SHA-256
pins, source/ADR/evidence bindings and candidate compiler flags. Changing a
recorded decision requires evidence, an ADR change where applicable, a deliberate
pin update, and new controls. There are no scope or denominator CLI switches.

- [sections.tsv](sections.tsv): metadata exclusion patterns and the default mixed scope.
- [units.tsv](units.tsv): the one bounded game-owned range and its source/decision/evidence identities.
- [flags.tsv](flags.tsv): exploratory candidate flags copied from the compiler probe recipe; they do not identify the original compiler.
- [not_functions.txt](not_functions.txt): no established exclusions yet; this file grants no matching credit.

The byte gate reads section and range decisions. Corpus accounting and completion
retain their independent identity and fresh-build checks. The flags table is a
checked index of the probe recipe, not a replacement compiler configuration.

Reproduce the consistency and negative controls with:

```sh
tools/check.sh test_recorded_decisions test_matching test_matching_ranges
python3 tools/repository_hygiene.py check
```
