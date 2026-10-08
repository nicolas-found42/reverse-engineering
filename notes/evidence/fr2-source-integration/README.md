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

The real aggregate positive control is retained at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration/20261008T075316Z-2263caa825d645eb8460b9bf4590b0b6/result.json`.
It reports AC07 pass, AC05 incomplete, `game_owned_bytes: 60`,
`matched_bytes: 60`, and `unresolved_bytes: 3506928`.

The source mutation control changes the sentinel branch and reruns the real
aggregate. Its receipt is
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-mutation/20261008T075411Z-a2860563b7d245ed9f503b5ce68f5c70/result.json`.
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
They do not resolve whole-image ownership, complete compiler/linker identity,
the rest of the source build, or the other issue #5 criteria.
