# Source-unit aggregate credit

The matching-range inventory now splits one range for the identity-pinned PAL
EE executable: `.text[0x001d1800, 0x001d183c)`, 60 bytes, SHA-256
`1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e`. The
split carries the pinned handwritten source identity and current ADR-0005
identity. Synthetic ELF and modified reconstruction source retain no owned
range. Structural inventory still reports `matched_bytes: 0`.

`tools/completion.py` runs the range and compiler children itself in fresh,
unique output directories. It binds each immutable child receipt to the
receipt file, command, corpus executable, reconstruction source, candidate
output and byte hash, and ADR-0005 decision. It credits 60 bytes only when that
fresh source-built exact comparison passes. The compiler child keeps AC05
`incomplete`; the aggregate reports AC07 pass while the full reconstruction
remains incomplete. There is no CLI path for importing a caller receipt.

The aggregate receipt at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration/20261008T075849Z-31227a6d24864e1f8575e59cb5321e6e/result.json`
is superseded: the inventory had already removed the owned 60 bytes from
unresolved accounting, and that aggregate removed them a second time. The
fixed ledger now asserts conservation directly; its next fresh positive receipt
must show `file_backed_bytes + zero_fill_bytes = unresolved_bytes +
game_owned_bytes + substitute_bytes`.

The source mutation control changes the sentinel branch and reruns the real
aggregate. Its latest receipt is
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-mutation/20261008T075955Z-e0eaa11bc4ea4f3e956785151a72b5aa/result.json`.
The altered source loses its fixed source identity; the compiler probe also
finds no matching candidate. AC05 and AC07 fail, while both owned and matched
bytes stay zero. A separate changed diagnostic-string control retained zero
ownership and zero matching credit at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-negative/20261008T074913Z-816a67bdd4394f28be0f0aa34f7ee230/result.json`.

Focused verification:

```sh
tools/check.sh test_matching_ranges test_completion test_compiler_probe_recipe test_compiler_probe test_matching
```

This local range decision and child build establish one matching unit only.
`matched_fraction` is the fraction of the attributed game-owned scope only; it
is not a whole-corpus completion fraction. These local results do not resolve
whole-image ownership, complete compiler/linker identity, the rest of the
source build, or the other issue #5 criteria.
