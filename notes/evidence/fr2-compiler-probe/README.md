# FR2 compiler probe

`tools/compiler_probe.py` compiles one source file with each candidate in a JSON
manifest, extracts `.text.<symbol>` with each candidate's GNU `objcopy`, and
compares the function bytes through `matching_diff.compare`. It writes an
immutable JSON receipt under `.scratch/evidence/compiler-probe/` by default.
The receipt records source and reference identities, candidate executable
hashes, argv, return codes, function hashes, and per-candidate gate verdicts.

## Reproduce the exploratory seven-candidate run

This probe compiles the hand-written reconstruction unit
[`reconstruction/ee/app3d/misc3d_db_id.c`](../../../reconstruction/ee/app3d/misc3d_db_id.c)
and uses the linker script in [`tools/compiler_probe_recipe/`](../../../tools/compiler_probe_recipe/).
The unit uses inferred names and ABI, guided by saved instruction and string
evidence. It is not original source. Its local ownership decision now has
independent source-map, caller, and helper evidence recorded in ADR-0005 and
the [first-unit evidence](../fr2-first-unit/README.md). The fixed child recipe
can credit that source-built range under AC07; generic caller-supplied probe
manifests cannot assign ownership. The historical receipt below predates this
decision and remains an exploratory compiler result. No generated decompiler C,
pseudocode, assembly, payload, compiler archive, executable, or retail bytes are
committed.

The candidates are from the public
[`decompme/compilers` GNU EE package and the `compilers` release](https://github.com/decompme/compilers/releases/tag/compilers).
The checked-in manifest template pins the seven candidate IDs, tool paths,
flags, and file fingerprints in the generated receipt. On this machine, the
installed distributions are under `spec-5-tools/compilers/`. The committed
Linux and Wine wrappers execute immutable Docker image IDs. Before any
candidate runs, the verifier inspects each image by ID and requires the exact
recorded ID and `linux/amd64` platform; the observed identities are retained in
the result. Native compiler candidates use the Debian Bookworm image, the
official Windows 2.95 drivers use the Wine 8 image, and object preparation,
linking, and extraction use the Debian image. The images install
`libc6:i386`, `libgcc-s1:i386`, and GNU binutils. GNU binutils 2.40 performs
object preparation, linking, and extraction as an explicit open-tool
substitution; it is not the original proprietary linker. The recipe records
each release archive URL and SHA-256. The seven local release archives were
hash-checked. Package-specific source and redistribution terms remain unresolved;
the [package provenance disposition](package-provenance.md) separates the
compiler's evidenced GNU identity from the missing exact-package binding.
Absence of license files does not establish proprietary status. No compiler binaries are
included here.

From the repository root, run the immutable child verifier:

```sh
python3 tools/compiler_probe_recipe/run.py \
  games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers
```

The runner first applies the repository corpus identity gate, then reads the
60-byte range at virtual address `0x001d1800` from `.text`. It checks the range
SHA-256 (`1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e`)
before writing a temporary local reference file and expanding the checked-in
manifest template with the installed tool root. Source, linker script,
reference bytes, objects, and linked objects are temporary children of that
tool root so the Docker and Wine wrappers can see them through their `/tools`
mount; they are removed when the run finishes. Neither reference bytes nor
generated manifest are committed. The result uses `evidence_common.write_result`
and records a report hash in a new immutable run directory. Set `--output` to
choose a different receipt directory. A unique match remains marked
`ac05_status: incomplete` because the probe is exploratory. The tool root must
contain the installed candidates and binutils; temporary inputs and outputs
are mounted at `/tools` by the committed wrappers.

The recorded run is preserved in
[`receipts/seven-candidate-run-20261008T061143Z/result.json`](receipts/seven-candidate-run-20261008T061143Z/result.json)
with its report. The result JSON SHA-256 is
`fa7ea650cef3912987dc216aeb499ecb4bdfa817f7b65101de88b221068d6703`; its
`report.md` SHA-256 is
`b88c4c77a351e79e77ff1019a73ca077b873ce7c7894858181df6b29969863cc`. It
records the observed Linux image ID
`sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca`
and Wine image ID
`sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba`,
both verified as `linux/amd64` before invocation.

The latest recorded local run produced these results with `-G8 -O2`, adding
`-fno-optimize-sibling-calls` for 2.9, 2.96, and 3.2 candidates where supported.
The older 2.95 drivers reject that flag, so they were run with `-G8 -O2`.
Linking resolves relocations to the retail addresses represented in the
hand-written candidate. A unique match applies only to this source, flags,
reference range, linker, and runtime profile; it does not establish which
compiler produced the game.

| GNU candidate | Function bytes | Result |
| --- | ---: | --- |
| `ee-gcc2.9-991111-01` | 64 | nonmatch |
| `ee-gcc2.95.2-273a` | 68 | nonmatch |
| `ee-gcc2.95.3-114` | 68 | nonmatch |
| `ee-gcc2.95.3-136` | 68 | nonmatch |
| `ee-gcc2.96` | 60 | byte match |
| `ee-gcc3.2-030926` | 64 | nonmatch |
| `ee-gcc3.2-040921` | 64 | nonmatch |

The byte match is diagnostic only because the source/profile was explored while
interpreting the same retail range. The GNU `ld` 2.40 substitution is also a
material limit: relocation and layout choices can differ from the original
linker. A second independently evidenced function and independent game-owned
range attribution remain necessary before compiler identification. A run is
`pass` only when exactly one candidate matches and every candidate executes
without operational errors; zero matches is `fail`, while missing tools,
multiple matches, runtime ID changes, or operational errors are `incomplete`.

Synthetic controls run with:

```sh
tools/check.sh test_compiler_probe test_compiler_probe_recipe
```

## Fixed independent EE panel (#8)

Run the four-unit panel through the existing recipe CLI:

```sh
python3 tools/compiler_probe_recipe/run.py \
  games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --profile --output .scratch/evidence/compiler-profile
```

The panel adds the hand-written reset, entity-list setter, and parser lookup in
[`profile-units.json`](profile-units.json) to the existing accessor. The recorded
source-map and static-reference evidence predates the compiler trials. These
are independent retail units, with inferred source forms and names; they are
not independent original-source recoveries. The decision records source and
range hashes, addresses, contiguous extents, caller/boundary metadata, ABI/data
inferences, and what each unit can distinguish. Source forms were explored
against the references; that limits any historical-identity inference.

Every unit runs all seven candidates using the recorded per-candidate flags.
The additional `-v` flag retains the compiler driver's cc1/assembler commands.
Installed drivers, compiler passes, assemblers and specs must match members of
the SHA-256-pinned release archives. Runtime images are inspected by immutable
ID and platform. Receipts bind the effective compile, preparation, link and
extraction argv, source/reference identities, compiler object, prepared object,
linked object and extracted-function hashes, phase tools, and located failures.
Missing components or archive/source/runtime provenance produce incomplete.

The pre-link diagnostic reads ELF32/MIPS REL and RELA entries. It compares
instruction bits outside `R_MIPS_26`, `HI16`, `LO16` and `GPREL16` fields; the
[GNU MIPS relocation definitions](https://raw.githubusercontent.com/ps2dev/binutils-gdb/master/include/elf/mips.h)
identify those types. Explicit addends and symbol indexes remain in the receipt.
Unknown relocations remain incomplete. This diagnostic ignores relocated
fields and cannot prove symbol binding, addends or placement. It grants zero
matched-byte credit. The separate linked gate compares every byte, including
those fields, at the recorded addresses with the GNU ld 2.40 substitution.
The linker script uses [GNU ld input-section selection](https://sourceware.org/binutils/docs/ld/Input-Section-Basics.html)
to keep each emitted function section at its declared address.

Selection requires one candidate to pass both comparisons for **every** fixed
unit, with all candidates completing. Multiple surviving candidates or any
operational gap are incomplete; no common candidate is a failed panel
hypothesis. A candidate passing a subset is retained but never selected.
`ac05_status` remains incomplete: this panel is EE-only, source forms remain
inferred, and exact historical package/source identity is unresolved under #21.
It changes no ownership decisions or AC07 credit, and does not establish
package permission. The original accessor-only CLI remains available for AC07.

Synthetic positive, negative, contradictory, ambiguous, changed-identity and
missing-evidence controls run with:

```sh
tools/check.sh test_compiler_probe test_compiler_probe_recipe \
  test_compiler_output test_compiler_profile test_compiler_packages
```

`independent-panel/` retains safe trial metadata. Generated assembly, objects,
reference bytes and compiler/runtime payloads stay local under the tool root.

The final fixed-recipe run is retained in
[`independent-panel/20261008T152841Z-c4176aa1d76246979d6dcd4dba068fff/result.json`](independent-panel/20261008T152841Z-c4176aa1d76246979d6dcd4dba068fff/result.json).
Its SHA-256 is `296389363958c9b08af1584371e234694684ecbd3cfcc3a7b22c39164a0bc931`.
The command above reproduces this bounded observation (receipt paths/timestamps
and object debug-path hashes can differ across fresh runs): all 28 combinations
completed with no operational gaps, but no candidate passed the whole panel.

| Unit | Reference bytes | Candidates passing both comparisons |
| --- | ---: | --- |
| Existing accessor | 60 | `ee-gcc2.96` |
| Misc3d reset | 28 | 2.9, all three 2.95 packages, and 2.96 |
| Entity-list setter | 60 | `ee-gcc2.96` |
| Parser lookup | 80 | none |

The setter provides distinguishing evidence beyond the accessor. The reset
supports the small-data/store profile but does not distinguish the older
candidates. The parser contradicts a claim that this source/flag profile matches
all declared units: 2.96 emits 100 bytes, and the linked gate locates a difference
at `0x0018b84c` (function offset 12); the compiler diagnostic also records the
80-versus-100-byte extent mismatch. This is a source/profile hypothesis failure,
not evidence that a particular historical compiler is excluded for every
possible original source form or flag set. The panel exits 1, selects no
candidate, and leaves AC05 incomplete. Resolving the parser's source/loop and
flag alternatives is remaining #8 investigation; it must not be dropped to
manufacture a profile pin. Historical package/source binding remains #21.

The saved setter inventory reports a body sum of 56 bytes, while its blocks
span `0x0018bba8..0x0018bbe3`, including a four-byte alignment hole and the return
delay slot. The fixed contiguous comparison extent is consequently 60 bytes.
The earlier 56-byte trial is retained as a failed experiment; its apparent
four-byte output excess was a reference-boundary error. No owned-byte ledger
is expanded by correcting this diagnostic extent.

Validation for this implementation is retained in
[`independent-panel/focused-tests.log`](independent-panel/focused-tests.log) and
[`independent-panel/whole-suite.log`](independent-panel/whole-suite.log).
The focused command above passed 42 tests. `tools/check.sh` passed 662 tests,
with one unittest skip and the separate exclusion of `test_research_jev_battery`
because `typesafe_sdk` was unavailable. Python compilation checks and staged/
tracked-tree `tools/ip_rails.py` checks passed. These checks validate tooling;
they do not turn the failed real panel into a historical compiler pin.
