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
The unit uses inferred names, ABI, and ownership, guided by saved instruction
and string evidence. It is not original source. The source-map line alone does
not prove that the range is game-owned; the probe remains exploratory until an
independent ADR-0005 ownership decision is recorded. No generated decompiler C,
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
hash-checked; inspection found no `COPYING` or `LICENSE` entries in them, so
per-package redistribution terms remain unresolved. No compiler binaries are
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
