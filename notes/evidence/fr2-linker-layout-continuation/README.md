# GNU linker placement, relocation and loader contracts (#9 / AC06)

The bounded GNU child now passes for the previously attributed misc3d accessor,
its diagnostic constants and four-byte cell. AC06 and issue #9 remain incomplete:
this does not reconstruct full EE/all-IOP layout, identify the historical Sony
linker/assembler, or execute a clean build of the GNU tool source. The compiler
provenance dependency remains #8/#21. This experiment adds zero matching-byte
credit; the accessor's existing ADR-0005 credit remains separate.

The original misc3d recipe verified section placement and NOBITS storage, but
accepted a GNU default entry at `001d183c`, immediately past the accessor. It did
not check the loader's PT_LOAD mapping or independently replay relocation
bindings. `tools/linker_layout.py` now relinks the unchanged source-built objects
with explicit accessor entry `001d1800`, checks the actual load segments, and
replays all six MIPS REL records without masking any relocated instruction bit.
The original/prepared objects, original output, relinked output, source, script
and comparison identities remain in [the source receipt](real-source-build.json).
Relinking preserves the existing exact accessor byte comparison; it grants no
ownership to diagnostic constants or neighboring sections.

The new fixed contract checks ET_EXEC/EM_MIPS/e_flags `20924001`, the accessor's
address/size/alignment, both diagnostic constant sections, and cell address/size,
writable NOBITS storage and minimum alignment. It verifies unique PT_LOAD
coverage, file/address congruence, permissions and section-to-segment file
positions. The NOBITS cell must sit beyond the segment's file payload; the
compiled cell is also checked for uninitialized common storage. This is the ELF
zero-fill contract. Guest initialization and runtime behavior were not observed.
A present contradiction wins over a different missing required section.

GNU binutils 2.40 is an explicit substitution for the original 2.10 proposal.
Its native R5900 support removes any need to rewrite ELF flags. The independently
authored public assembly fixture includes R5900 `paddw`, creates a correctly tagged
object using `-EL -march=r5900 -mabi=eabi -no-pad-sections`, and links a loadable
output. Its HI16/LO16 pair targets `00108004`, exercising signed-low carry; its
separate four-byte NOBITS allocation has no file bytes. The fixture validates
GNU support and relocation behavior; it is independent of retail code.

[The repository-owned decision](decision.json) pins the GNU assembler, ld and
objcopy to exact members of Debian's amd64 `binutils-mips-linux-gnu` 2.40-2cross2
binary package, including copyright metadata. Package metadata identifies
`Source: binutils-mipsen (10+c2)` and `Built-Using: binutils (= 2.40-2)`.
The matching source wrapper, original binutils source and Debian patch archives
are retained locally and hash-checked on every real command. Debian's primary
[package page](https://packages.debian.org/bookworm/binutils-mips-linux-gnu) and
[source package page](https://packages.debian.org/bookworm/binutils-source)
provide the distribution links. The actual linker reports GPL v3 or later.
The pinned immutable Docker runtime and exact invocation are retained in the
source receipt. These bindings establish package/source provenance, not a
locally reproduced binutils build or retail-toolchain identity. Compiler/runtime
binaries, package archives and generated ELF artifacts stay private.

Reproduce the fresh real child using the already installed local inputs:

```sh
python3 tools/linker_layout.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/linker-layout-new
```

Run the real positive and artifact/provenance controls into a new directory:

```sh
python3 tools/linker_layout_recipe/controls.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/linker-layout-controls-new
```

[The controls receipt](controls.json) records positive exit 0; displaced text,
wrong alignment, incorrect NOBITS size, wrong entry, wrong output flags, wrong
accessor relocation, wrong native GNU object tag and wrong HI/LO carry all
exit 1; absent decision exits 2. These negatives mutate private copies of
produced artifacts. They verify located checker diagnostics and are not
compiler-generated negative builds. The missing-provenance control selects an
absent path inside the control process without deleting repository evidence.
Public fixtures also reject wrong PT_LOAD permissions/mapping, unsupported
relocations and missing sections, and prevent absent evidence from hiding
known layout/archive contradictions.

The fast deterministic public seam is:

```sh
tools/check.sh test_linker_layout
pyright tools/linker_layout.py tools/linker_layout_recipe tools/test_linker_layout.py
```

[The retained check log](checks.log) records 17 tests passing and zero Pyright
errors/warnings. The original red loop reported the absent public checker; the
source-built default-entry control subsequently demonstrates the concrete
contract failure the new checker prevents. Whole-suite and final independent
Standards/Spec review belong to the integrated issue #5 delivery.
