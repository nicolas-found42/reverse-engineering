# First source-built EE unit: `misc3d_db_id`

The first locally attributed code span is `.text` at `0x001d1800`, length 60
bytes, ending at `0x001d183c`. Its SHA-256 is
`1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e`. The
corpus executable is pinned at SHA-256
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`.

The measured ownership decision is recorded in [ADR-0005](../../../docs/adr/0005-game-owned-sdk-boundary.md).
The committed metadata record is
[`adr0005-misc3d-boundary.json`](adr0005-misc3d-boundary.json).
Its inventory pin refers to the committed
[`saved-function-inventory-digest.json`](saved-function-inventory-digest.json),
which retains only structural function identities, sizes, caller/callee addresses,
and the original local inventory digest. No instruction bytes, disassembly, or
retail strings are included. A clean checkout can validate these inputs; a missing
prerequisite produces an incomplete receipt naming the path.

Validate the retained metadata and range gate with:

```sh
tools/check.sh test_matching_ranges test_matching
```
It records the source-map and saved-function inventory identities, five static
callers and their call sites, the `../fr2/source/app3d/misc3d.c:188` source
reference, and the separately mapped `../modules4/system/ps2/asyncf.c` error
helper. The direct game caller is in `obstacle.c`. The referenced `.sbss`
address `0x00290ac4` remains unresolved and outside this code-range decision.
These are static observations; no runtime reachability is claimed.

The hand-written source is
[`reconstruction/ee/app3d/misc3d_db_id.c`](../../../reconstruction/ee/app3d/misc3d_db_id.c).
The child runner stages that source, builds it with each declared EE compiler
candidate, links the function and diagnostic data to their measured addresses,
and compares the function bytes against the pinned executable range. It does
not use generated decompiler C or assembly.

The real source-tree build and local AC07 child receipt were run with:

```sh
python3 tools/compiler_probe_recipe/run.py \
  games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output /Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/first-unit/final-credited
```

The immutable result is retained outside the repository at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/first-unit/final-credited/20261008T073940Z-a412a02285c54ec19618759bcfe6ac45/result.json`.
Exactly one of seven compiler candidates matched: `ee-gcc2.96`, using the
recorded flags and GNU binutils 2.40 linker substitution. The status is
exploratory. It narrows this source/profile probe only; AC05 remains incomplete.
The result does not establish the compiler or linker used for the complete
retail build. The child receipt reports `ac07_status: pass` for the source-built
60-byte match and fixed repository-owned range attribution, separately reports
`ac05_status: incomplete`, and does not alter the complete-image partition.

Two real-corpus negative controls were run from the same reconstruction source
and seven-candidate recipe. Inverting the loaded/unloaded sentinel branch
failed every candidate. Moving the diagnostic string by four bytes while
keeping the function at `0x001d1800` also failed every candidate. Their immutable
receipts are retained outside the repository:

- `.../first-unit/source-tree-branch-negative-control.json`
- `.../first-unit/source-tree-placement-negative-control.json`

The repository checks for the child CLI, matching gate, source staging, and
negative/incomplete behavior are:

```sh
tools/check.sh test_compiler_probe_recipe test_compiler_probe test_matching
```

A byte match is reported for this owned range only. This local result does not
complete whole-image attribution, the full reconstruction, substitute linking,
asset contracts, VU interfaces, or the remaining acceptance criteria.

Compiler recipe staging and candidate work directories are retained below the
local tool root. Receipt paths remain inspectable after the child returns. These
private directories include extracted reference and candidate bytes and must stay
outside version control. The receipt records their hashes and extraction range.
