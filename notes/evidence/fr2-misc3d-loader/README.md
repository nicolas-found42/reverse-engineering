# misc3d loader source and exact static frontier (#37)

The new loader child remains **incomplete**. It now binds the complete saved
loader body to an isolated project and executes readable hand-written source
against synthetic service contracts. A separately compiled terminal candidate
is byte-identical for eight bytes, with **zero new ownership or matching credit**.
#37, #35 and #24 remain incomplete; the existing 60-byte ADR-0005 match and
previous common/NOBITS checks are unchanged.

The [fixed decision](decision.json) binds raw inventory, isolated observation,
loader/header/terminal sources, synthetic harness and Ghidra script by content
identity. The terminal child also binds its linker and source-build recipe.
No retail bytes, generated decompiler/assembly source, compiler or object
payload is committed. Source identifiers and the callable terminal seam are
inferred, and do not identify original declarations or translation units.

## Reproduce the red-capable frontier

```sh
python3 tools/misc3d_loader.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35/reconciled-inventory.json \
  notes/evidence/fr2-misc3d-loader/isolated-project.json \
  --output .scratch/evidence/misc3d-loader-fresh
```

The command exits 2 with `bounded_static_status: pass`, successful synthetic
source execution and four fixed required unknowns. It never claims #37 complete.
Available corpus/source/body/provenance contradictions exit 1 even when other
required evidence is absent. Caller arguments cannot remove the fixed unknowns
or award ownership. This receipt is the specific reproducible symptom being
investigated, not a failure of the former bounded lifecycle-byte child.

The [fresh frontier control](frontier-control.json) and
[ten executed controls](controls.json) retain the outcomes and original private
receipt hashes. All expected exit codes were observed. Source changes recompile
real hand-written source: replacing the optional pointer store with zero fails
its retail comparison, and changing the loader's flag update fails the actual
synthetic call/state harness. The layout control changes the private ELF section
address and fails the same terminal comparator. Missing decision evidence stays
incomplete; changed isolated provenance fails, including when the raw inventory
is missing. Synthetic success supplies no retail runtime evidence.

```sh
python3 tools/misc3d_loader_recipe/controls.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35/reconciled-inventory.json \
  notes/evidence/fr2-misc3d-loader/isolated-project.json \
  --output .scratch/evidence/misc3d-loader-controls-fresh
```

## Measured body and dependency use

The [isolated saved-project receipt](isolated-project.json) and
[raw-word reconciliation](observation.json) agree on six disjoint instruction
ranges, totaling 536 bytes:

| Start | Exclusive end | Bytes | Disposition |
| --- | --- | ---: | --- |
| `0012c218` | `0012c220` | 8 | Remote terminal; ownership unresolved |
| `001d1408` | `001d143c` | 52 | Main loader candidate |
| `001d1440` | `001d157c` | 316 | Main loader candidate |
| `001d1580` | `001d15b4` | 52 | Main loader candidate |
| `001d15b8` | `001d15cc` | 20 | Main loader candidate |
| `001d15d0` | `001d1628` | 88 | Main loader candidate |

Every saved instruction in the loader and three inspected dependencies is
compared to the pinned executable before retaining its body metadata. Each
fresh saved incoming direct-call set is reconciled against all aligned allocated
executable JAL words. Other saved incoming reference kinds require an explicit
incomplete disposition. The envelope and holes receive no comparison or credit.
The J at `001d1610` reaches the remote terminal; that terminal returns with A0
stored to `0028f23c` in its delay slot. This cell is outside the five misc3d
NOBITS cells, and has no new layout/ownership claim.

The callee at `0011ed90` preserves the loader's A0 name pointer in S0. Its normal
return retains the low word of the packed database id in V0, stores that value
to its GP id cell and returns. The loader consumes that low word in the store at
`001d1460`. The prior decompiler's `void` rendering does not establish a void
return ABI. This is an argument/return-use observation, not a reconstruction or
ownership grant for the 6,196-byte dependency.

The fixed GP/direct scan observes 29 loads/stores across the five misc3d cells,
including 11 stores: five loader result stores, five reset stores and one release
sentinel store. It finds no other opcode using an exact five-cell GP displacement,
and no aligned literal equal to a cell address. The implemented scan covers
fixed GP offsets and aligned allocated words. It does not resolve computed,
transitively derived or unaligned aliases; its bounded absence cannot establish
alias closure or eliminate sibling callers.

Reproduce the isolated observation without opening the primary project for
writing. Use a fresh destination; do not reuse or delete an existing project.

```sh
mkdir -p ghidra-project/misc3d-loader-fresh
cp -R /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35-copy/fr2.gpr \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35-copy/fr2.rep \
  ghidra-project/misc3d-loader-fresh/
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home \
  .scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC/support/analyzeHeadless \
  "$PWD/ghidra-project/misc3d-loader-fresh" fr2 -readOnly \
  -process SLES_517.05 -noanalysis -scriptPath "$PWD/tools/misc3d_loader_recipe" \
  -postScript InspectMisc3dLoader.java "$PWD/.scratch/misc3d-loader-isolated.json"
```

REA's current session was inspected; no target was open. Existing retained
R5900 exports and the supplied isolated project were reused instead of starting
another whole-image import. The primary project remains untouched.

## Source outputs and limits

The [hand-written loader](../../../reconstruction/ee/app3d/misc3d_loader.c)
implements sentinel validation, database load, all five result stores, required
resource failures, the 64-bit flag update at object offset 56, resource consumers
and the final optional terminal call. The host harness executes six scenarios:
loaded resources, absent optional resources, each of three required failures and
already-loaded sentinel failure. It checks imported call order, intermediate
cell visibility, flag preservation and preservation of the existing final
optional pointer when lookup returns -1. It executes reconstructed source with
synthetic services; there is no guest execution or retail behavioral equivalence.

The [terminal source receipt](terminal-source.json) records real ee-gcc2.96
`-G8 -O2 -fno-optimize-sibling-calls` output linked at `0012c218`. Its independently
compared eight bytes are identical. The original loader's noncontiguous body
includes this code; introducing an inferred callable seam is a source design
choice, not proof of the historical function boundary. The GNU binutils 2.40
linker is still a substitution and historical compiler identity remains open.

```sh
python3 tools/misc3d_loader_recipe/source_build.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/misc3d-loader-terminal-fresh
```

The public terminal CLI validates the fixed source/linker/recipe decision before
building, binds corpus and validation-tool identities, and retains source,
compiler/tool/runtime, object, prepared-object, linked output and comparison
identities. Absent corpus/tools/decision is incomplete. An available incompatible
corpus or changed fixed source takes precedence and fails. The readable main
loader has only host-source contract evidence; its full retail output remains
unestablished.

The initial hypotheses and their tested dispositions were:

1. The noncontiguous body included a remote terminal hidden by envelope-based
   reasoning. Confirmed by fresh ranges and the exact raw J target.
2. The decompiler's void return hid the database-id return contract. Confirmed
   by raw return/store instructions and the caller's V0 use.
3. Exact GP address materializations supplied a missing alias domain. Refuted
   within the implemented bounded scan; computed aliases remain unknown.
4. A historical compiler mismatch could prevent full loader byte reproduction.
   Unresolved: the terminal output matches an exploratory profile, and the main
   loader was tested through synthetic services. That does not identify the
   compiler or measure a full-loader mismatch.

Required remaining work is full main-loader source/output comparison, independent
range attribution, complete relevant alias/consumer domains and dependency
allocation/lifetime closure. The next evidenced source/data group is the remote
terminal's `0028f23c` optional-pointer consumers, joined to the actual loader
return and resource-object allocation contract. Neither adjacency nor these
candidate outputs resolve it.

## Verification

```sh
tools/check.sh test_misc3d_loader test_misc3d_lifecycle \
  test_misc3d_lifecycle_observation test_misc3d_contract
pyright tools/misc3d_loader.py tools/misc3d_loader_recipe/source_build.py \
  tools/misc3d_loader_recipe/controls.py tools/test_misc3d_loader.py
python3 tools/ip_rails.py --tree
```

The [focused log](focused-tests.log) records 45 tests passing, and
[Pyright](pyright.log) records zero errors. The root integration performs the
whole-suite check after combining independent work. The
[Jev verification](jev-verification.json) retains all distributions: five claims
verified, none contradicted/unsupported, with one low-confidence range-count
claim marked for review. Its original judgment is preserved for independent
disposition; a majority-support result alone does not settle that review.
