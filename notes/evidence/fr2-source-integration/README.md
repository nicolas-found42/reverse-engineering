# Source-unit aggregate credit

The matching-range inventory now splits one range for the identity-pinned PAL
EE executable: `.text[0x001d1800, 0x001d183c)`, 60 bytes, SHA-256
`1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e`. The
split is based on corpus bytes plus ADR-0005, source-map, and saved-function
evidence identities. Synthetic ELF never inherits ownership. Changing the
candidate source leaves the retail range game-owned and changes its candidate
source binding; structural inventory still reports `matched_bytes: 0`.

`tools/completion.py` runs the range and compiler children itself in fresh,
unique output directories. It binds each immutable child receipt to the
receipt file, command, corpus executable, reconstruction source, candidate
output and byte hash, and ADR-0005 decision. It credits 60 bytes only when that
fresh source-built exact comparison passes. The compiler child keeps AC05
`incomplete`; the aggregate reports AC07 pass while the full reconstruction
remains incomplete. There is no CLI path for importing a caller receipt.

Reproduce the real aggregate from a clean checkout with the pinned local corpus
and compiler installations:

```sh
python3 tools/completion.py games/ford-racing-2 \
  --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output /Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration
```

The aggregate receipt at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration/20261008T075849Z-31227a6d24864e1f8575e59cb5321e6e/result.json`
is superseded because it subtracted the owned 60 bytes from unresolved
accounting twice. The clean receipt at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration/20261008T080215Z-c5c6714b15e74f18a7f184123a94debe/result.json`
corrected the total but is also superseded because ownership depended on the
candidate source hash. The source-accounting phase's fresh clean positive
receipt is
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration/20261008T081411Z-3ba61545b5a149e1b689964364468e11/result.json`.
It records AC07 pass, AC05 incomplete, 60 owned and matched bytes, 3,506,988
unresolved bytes, AC27/29/30/31/32 incomplete with current child-receipt
references, and a clean working tree at source revision `d03d5ad`.

The final reviewed code has a fresh aggregate at source revision
`181c705731b715725af48679e09728bd6e605898`, retained at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/post-ci-fix-aggregate/20261008T084909Z-1bd147b0a1644c43936c26e300481ebb/result.json`.
The [continuation summary](../fr2-completion/20261008-continuation-summary.json)
pins this current receipt and child hashes, the exact command, the conserved
ledger, and separate behavioral and dependency limits. It exits 2, incomplete.

The source mutation control changes the sentinel branch and reruns the real
aggregate. This earlier receipt is superseded because the range inventory had
coupled ownership to the candidate source hash:
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-mutation/20261008T075955Z-e0eaa11bc4ea4f3e956785151a72b5aa/result.json`.
The current changed-source receipt is
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-mutation/20261008T081222Z-79e32bee9eb044d5bea4ec0f310fe550/result.json`.
It records the intentionally changed working tree at source revision
`734b7ae2148ba7be424b1d5c02bd11e07df377d7`. The altered source fails its fixed
source binding; the compiler probe also finds no matching candidate. AC05 and
AC07 fail; the owned range remains 60, matched bytes remain zero, and unresolved
bytes remain 3,506,988. Reproduce it in a separate disposable checkout with the
same declared corpus/tools by changing `if (value != -1)` to
`if (value == -1)` in the reconstruction unit, then running the aggregate
command above into a fresh output directory. The unchanged-corpus ownership
control is also executable through
`tools/check.sh test_matching_ranges.RangeCli.test_real_corpus_ownership_is_stable_when_candidate_source_changes`.

A separate earlier diagnostic-string control retained zero ownership and zero
matching credit at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/source-integration-negative/20261008T074913Z-816a67bdd4394f28be0f0aa34f7ee230/result.json`.
Its source-coupled ownership accounting is superseded and must not be used as
the current range-attribution result.

Focused verification:

```sh
tools/check.sh test_matching_ranges test_completion test_compiler_probe_recipe test_compiler_probe test_matching
```

These focused modules pass 60 tests, including real-corpus aggregate and
source-mutation range command controls.

This local range decision and child build establish one matching unit only.
`matched_fraction` is the fraction of the attributed game-owned scope only; it
is not a whole-corpus completion fraction. These local results do not resolve
whole-image ownership, complete compiler/linker identity, the rest of the
source build, or the other issue #5 criteria.
