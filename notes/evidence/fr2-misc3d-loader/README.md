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

## Continuation: dependency ABI and reproducibility (2026-10-09)

The earlier integration could not run Docker and left the two-build proof
partial. On this continuation Docker was available. The unchanged recipe's
clean-build control failed: the comparison bytes agreed, but the object,
prepared object and linked output differed because GCC retained each build
directory in its source filename metadata. Naming the stages did not remove
that difference. Those historical receipts above are preserved.

The compiler recipe now compiles the basename `terminal.c` from each separate
build directory. Its Linux child wrapper maps the caller's working directory
inside the existing tool-root mount; callers outside that mount retain `/`.
The source is still copied and hashed, and compiler flags, runtime image pins
and the terminal comparison stay fixed. No metadata is stripped after compilation
to obtain reproducibility. Relative CLI tool-root paths are resolved before
building so that changing the compiler's working directory cannot redirect them.

Run the controls command above to reproduce the
[current control summary](20261009-controls.json). All thirteen expected exit
codes were observed, including the added raw dependency check. The
[two-clean-build receipt](20261009-reproducibility.json) records identical
object, prepared-object, linked-output and comparison identities in separate
directories. The [changed-source control](20261009-reproducibility-drift-detected.json)
still detects a different linked artifact. This proves reproducibility for the
bounded terminal candidate under the recorded tools, rather than a full-loader
match or historical compiler identity.

The new public child revalidates the database-name argument, low-word return
transformation, return-register preservation, loader result use and shared
object helper's indexed-pointer path from raw instructions:

```sh
python3 tools/misc3d_abi.py games/ford-racing-2 \
  --output .scratch/evidence/misc3d-abi-fresh
tools/check.sh test_misc3d_abi test_misc3d_loader test_misc3d_lifecycle \
  test_misc3d_lifecycle_observation test_misc3d_contract
pyright tools/misc3d_abi.py tools/test_misc3d_abi.py tools/misc3d_loader.py \
  tools/misc3d_loader_recipe/source_build.py \
  tools/misc3d_loader_recipe/controls.py tools/test_misc3d_loader.py
```

The [raw ABI receipt](20261009-dependency-abi.json) binds each checked instruction
site by hash. On the dependency's observed normal return tail, the low word is
`(old_id & 0xfff00000) | 0x00010000`, written to `0028f124` and consumed by the
loader at its `00290ac4` store. The object helper returns null for `-1`; its
non-sentinel path uses the resource's low sixteen bits to index four-byte
pointer slots through the table at context offset 236. Names and type
interpretations remain inferred. Table allocation, index bounds and pointer
lifetime are unresolved, and no ownership of this shared helper follows.

The loader frontier invokes this child and binds its checker identity in the
updated decision. An available ABI contradiction fails even if inventory or
isolated-project evidence is missing. Missing instruction sites stay incomplete;
the synthetic controls also exercise changed tag, index stride, delay-slot
argument and return-register restoration. Their success establishes checker
behavior, not acceptance of a different corpus. The
[focused log](20261009-focused.log) records 57 passing tests and
[Pyright](20261009-pyright.log) records zero errors.

The [current terminal build](20261009-real-terminal-source.json) remains an
eight-byte candidate comparison with zero new attributed matching bytes. The
[current frontier](20261009-full-frontier.json) still exits 2/incomplete with
the same four required unknowns. Complete main-loader source/output comparison,
independent range ownership, computed aliases and relevant sibling/lifetime
domains remain required for #37/#35/#24. This continuation does not close them.

The Standards and Spec reviews found no actionable defect in this continuation;
the Spec review retained the parent acceptance gaps. Jev's original ABI review,
six bounded patch packets and final gate escalated on low confidence without a
concrete finding. The final gate independently verified the test/control/status
claims. A [stronger independent review](20261009-review-disposition.json) checked
the selected raw sites, unchanged source/test identities, original private
receipts and both sets of actual build artifacts, then accepted the bounded
continuation. Original judgments and distributions remain intact in the retained
full resolution identified by hash; this is an independent disposition rather
than an automatic Jev pass or full issue acceptance.

## Diagnosis and full loader source (2026-10-09)

The previous frontier had two separate causes. Its child always raised
`Incomplete` after the available checks, and the behavioral C candidate had
never been compared as a complete EE loader build. A terminal match and host
service-contract pass could not discharge that source/output gap. The original
feedback loop exited 2 twice with `required loader/alias frontier remains
unresolved`; the retained historical receipts above remain valid observations
of that earlier implementation.

The [initial full-source control](20261009-main-source-initial-red.json) compiled
the earlier candidate and failed its main address/size check. The revised
hand-written C retains the initial unloaded sentinel, keeps the returned `d4`
identifier in a local, expresses the evidenced 64-bit flag member at byte
offset 56, and gives each required resource its success/error branches. It
uses the existing non-returning error declaration. No instruction arrays,
inline assembly, original-source identity or runtime equivalence are claimed.

The [full-source build](20261009-main-source.json) compares the five main saved
ranges, totaling 528 instruction bytes, and the separate eight-byte remote
leaf. The four main holes total 16 bytes and receive no matching credit. All
536 compared candidate bytes coincide with retail under `ee-gcc2.96`, `-G8
-O2`, the recorded immutable runtime image and binutils substitution. This is
an exploratory matching profile; historical compiler identity remains in #21.

```sh
python3 tools/misc3d_loader_recipe/loader_build.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/misc3d-main-source-fresh
python3 tools/misc3d_loader_recipe/loader_controls.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/misc3d-main-controls-fresh
```

The [real full-source controls](20261009-main-controls.json) cover changed flag
source, shifted main placement, missing decision, stale source identity,
stale identity together with missing tools, and two independent clean builds.
The recorded compiler, loader/terminal objects and prepared objects, linked
output and six comparison artifacts reproduce identically. The controls are
separate from corpus acceptance; their expected failure/incomplete cases do
not count as successful reconstructions.

The [lifetime contract](lifetime-contract.json) and
[revalidated result](20261009-lifetime.json) join the database context allocator,
resource-count-derived pointer-table allocation, lookup/index use and release.
The object lookup helper does not check generation, context activity or the
index against the table count. Its usable input contract therefore requires a
current lookup-derived ID and a live context. Release frees the table and
zeros the context; misc3d's release clears only its database ID. Four stored
resource IDs and the optional pointer are not all cleared. Their possible
post-release uses remain a parent caller-use question.

```sh
python3 tools/misc3d_lifetime.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35/reconciled-inventory.json \
  --output .scratch/evidence/misc3d-lifetime-fresh
python3 tools/misc3d_attribution.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35/reconciled-inventory.json \
  --output .scratch/evidence/misc3d-attribution-fresh
```

The [attribution evidence](loader-attribution-candidate.json) binds the main
loader's four `misc3d.c` diagnostics to actual startup caller edges and an
independent `backrend.c` diagnostic on another startup-orchestrator callee.
The immediate caller and orchestrator have no direct source-file diagnostic.
This remains a proposed local range split, with explicit evidential limits;
no additional ADR-0005 ownership or matching credit is granted here. The
remote leaf is a separate external tail callee with mixed ownership, and the
shared database dependency carries an independent `modules4/3d/3dobjdb.c`
source lead. Neither receives loader ownership. The
[semantic attribution check](20261009-attribution-judgment.json) verifies the
bounded corroboration claim, not an original-source or whole-image claim.

The [fresh lifecycle regression](20261009-preserved-lifecycle.json) recompiles
the previous accessor/reset/release/sibling group and rechecks all five NOBITS
cells. This preserves the existing 60-byte accessor comparison, the other
candidate comparisons and zero fabricated NOBITS file bytes.

## Complete bounded static disposition

The [current public summary](20261009-complete-static.json) identifies the full
private receipt by path, byte count and SHA-256. The full receipt retains the
per-site ledgers; the public summary is deliberately a summary, not a truncated
replacement for them. Reproduce the result with the original public child:

```sh
python3 tools/misc3d_loader.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/fr2-implementation-context/issue-35-evidence/issue-35/reconciled-inventory.json \
  notes/evidence/fr2-misc3d-loader/isolated-project.json \
  --output .scratch/evidence/misc3d-loader-static-fresh
python3 tools/misc3d_aliases.py games/ford-racing-2 \
  notes/evidence/fr2-misc3d-loader/isolated-aliases.json \
  --output .scratch/evidence/misc3d-aliases-fresh
```

The loader child now returns 0 only when its fixed required source, raw body,
ABI, lifetime, incoming and conditional-alias checks pass. Missing evidence
remains incomplete and available contradictions fail. Its decision pins both
alias helpers, the separate UI predicate helper and the fresh isolated export;
changing an imported predicate cannot bypass provenance. Mixed ownership is a
fixed recorded disposition, not a caller-selectable route to matching credit.
The [final original control suite](20261009-final-controls.json) observed every
expected exit code, including the now-passing bounded frontier.

The alias command scans 1,638,839 initialized allocated file bytes at every byte
offset, and 311,832 aligned executable words. It reconciles 27 direct transfers
to every scoped body/cell byte and records no pointer literals into that scope.
All 143 GP register sums have their immediate memory consumer and exact
per-cell naturally aligned overlap conditions. All 357 GP immediate-address
constructors have explicit local use/escape dispositions: 318 are saved
instructions and 39 are raw candidates conditional on execution. Their ledger
retains 625 memory-address uses, dynamic additions, stored values and
control/unsupported-effect escapes. A concrete initial address outside the
cells is never treated as proof that a derived pointer cannot reach them.

The device-table formulas expose conditional misc3d reads at indices 293–297,
or byte offsets 1172–1188 for the unscaled paths. Actual loop/callback paths
constrain some uses to the disjoint two-slot domain; other externally supplied
indices remain conditional may-alias. Three UI-table chains starting at
`00290a00` similarly record indices 49–53 and the walking-loop counts needed to
reach the cells. Every equation is conditioned on the actual path, alignment,
valid address and recorded argument/register-preservation preconditions. The
[scope judgment](20261009-alias-scope-judgment.json) supports retaining these
conditional dispositions and parent uncertainty; it does not certify a
universal runtime exclusion.

The current sibling consumer at `001d1628` reads `00290acc` and `00290ad0` into
A0/A1 and transfers to `001318a0`; its actual startup caller is included in the
expanded incoming domain. Its complete source/data reconstruction is the next
evidenced EE group. The loader/alias gaps retained by #24/#35 now have concrete
bounded dispositions. Those parents remain incomplete for their own range
ownership/caller-use review, possible post-release stale-ID/pointer use, open
runtime/index domains and remaining EE groups. Global dispatch work remains
in #25. No additional matched bytes, completed parent or guest behavior follows
from this static group.
