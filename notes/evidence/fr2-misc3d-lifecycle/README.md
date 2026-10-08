# Bounded misc3d lifecycle source outputs (#35)

The fresh child compares hand-written C outputs for six fixed code spans and
five tentative/MIPS small-common cells. Its bounded source/output verdict passes. **#35
and #24 remain incomplete:** loader contracts, computed aliases, new ownership
attribution and sibling caller use are unresolved. The existing ADR-0005
accessor keeps its 60 attributed matching bytes. The 276 additional identical
candidate bytes receive **zero new ownership or global matched credit**.
NOBITS occupies 20 layout bytes and contributes zero file-byte matches.

| Inferred source symbol | Address | Compared bytes | Attribution |
| --- | --- | ---: | --- |
| `fr2_misc3d_reset` | `001d17a8` | 28 | Candidate |
| `fr2_misc3d_release` | `001d17c8` | 56 | Candidate |
| `fr2_misc3d_get_database_id` | `001d1800` | 60 | Existing ADR-0005 split |
| `fr2_misc3d_get_state_cc` | `001d1840` | 64 | Candidate |
| `fr2_misc3d_get_state_d4` | `001d1880` | 64 | Candidate |
| `fr2_misc3d_get_state_d0` | `001d18c0` | 64 | Candidate |

[The decision](decision.json) binds exact source, observation and linker
identities, scoped contracts, dependency dispositions, falsifiers and next
observations. [The observation](observation.json) retains safe static metadata
and hashes. [The real source/output receipt](real_source_build.json) retains
exact source/object/prepared-object/link/comparison identities, command vectors,
compiler/tool identities, immutable Docker runtime identities and source revision
with the dirty-tree disposition. These are investigation receipts for the
recorded source hashes; final clean-revision acceptance requires a fresh child.
No compiler binary, retail payload, generated assembly or decompiler output is
published or used as reconstruction source.

Run the real public child on the unchanged corpus and existing tools:

```sh
python3 tools/misc3d_lifecycle.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/misc3d-lifecycle
```

The source/output check is fixed in the repository. It compares each code span
independently, requires exact placement and size, checks all five four-byte
MIPS small-common definitions before linking, and requires writable, allocated, aligned
NOBITS at `00290ac4`, `00290ac8`, `00290acc`, `00290ad0`, `00290ad4`.
Initialized storage cannot be hidden behind the linker's `NOLOAD` declaration.
Known available output mismatches take precedence over missing code/cells.
Missing fixed observation/decision/source provenance is incomplete; changed
source or evidence identities fail before tools execute.

The exploratory compiler remains ee-gcc2.96 with `-G8 -O2
-fno-optimize-sibling-calls`, and the linker remains the explicit GNU binutils
2.40 substitution. Only the sibling source additionally uses
`-falign-labels=16`; this emits the measured internal padding before each loaded
return path. Applying this flag to release produces a different 64-byte body,
so reset/release and siblings are separate source inputs. The original accessor
source and flags remain unchanged. These outputs do not identify the historical
toolchain; AC05 remains incomplete. [Failed hypotheses](experiments.json)
retain source/object identities and section sizes without instruction payloads.

Run real controls into a **new** output directory:

```sh
python3 tools/misc3d_lifecycle_recipe/controls.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --output .scratch/evidence/misc3d-lifecycle-controls
```

[The controls](controls.json) bind four receipts: real source build exits 0;
reversing the release sentinel condition in C and recompiling exits 1;
shifting the linked `state_cc` section four bytes exits 1; absent observation
provenance exits 2. The source negative retains fresh source/object/link and
per-span comparison hashes. The layout negative mutates section metadata in a
private ELF, and does not claim a compiler-generated layout mutation.
Synthetic fixture tests remain separate from real-corpus acceptance.

The raw load at `001d1840` was unowned; saved sibling entry `001d1844` owned only
60 following bytes. Copy the existing project to a **new isolated directory**:

```sh
mkdir -p ghidra-project/misc3d-lifecycle-copy
cp -R ghidra-project/codex-audit-ee-types-t2-proposal-01/fr2.gpr \
  ghidra-project/codex-audit-ee-types-t2-proposal-01/fr2.rep \
  ghidra-project/misc3d-lifecycle-copy/
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home \
  .scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC/support/analyzeHeadless \
  "$PWD/ghidra-project/misc3d-lifecycle-copy" fr2 -readOnly \
  -process SLES_517.05 -noanalysis -scriptPath "$PWD/tools/ghidra" \
  -postScript ReconcileMisc3dBoundary.java "$PWD/.scratch/misc3d-boundary.json" \
  -postScript ExportEvidence.java "$PWD/.scratch/misc3d-reconciled-inventory.json"
python3 tools/misc3d_lifecycle_observation.py games/ford-racing-2 \
  .scratch/issue-24/inventory.json .scratch/misc3d-reconciled-inventory.json \
  .scratch/misc3d-boundary.json --output .scratch/evidence/misc3d-lifecycle-observation
```

The first inventory is the unchanged original #24 export; reproduce it with
[the #24 recipe](../fr2-misc3d-cell/README.md) if absent. Ghidra creates a complete
64-byte flow body at `001d1840` in the isolated read-only transaction; its export
is captured before that transaction is discarded. The primary project is never
opened for writing. The observer rechecks every saved instruction against ELF,
requires both original and reconciled contiguous boundaries, and rejects a
measured direct/saved incoming reference to interior entry `001d1844`.
Its bounded scan finds no direct J/JAL or aligned literal incoming reference to
release or the three siblings. That absence does not establish dead code or
resolve computed references. No original identifier or runtime reachability is
inferred from this boundary correction.

The five GP words use signed word loads and four-byte stores. Reset writes `-1`
to all five; its observed caller invokes reset before the loader. Release tests
the database-id sentinel, passes the loaded word in A0 to external `00120aa8`,
then writes `-1`. The callee consumes A0 bits 20..23 as a descriptor-table index;
its entry-window/body hashes and normal return site are retained. The wrapper
ignores its return, and the original declaration/ownership remains unknown.
Siblings take no consumed incoming argument, test the same database-id cell and
return related words in V0 on the loaded path. Original state meanings remain
unresolved. No observed incoming sibling caller establishes consumer return use.
The error helper at `00105888` remains a separately mapped modules4 dependency;
its compilation declaration is a surrogate and establishes no error return.
Static lifecycle paths do not establish runtime ordering or thread safety.

This resolves #24's lack of source outputs for reset/release/siblings and extends
its common/NOBITS checks to the five cells. It does not resolve the noncontiguous
loader at `001d1408`, its dependency `0011ed90`, computed aliases or independent
ownership/caller evidence. The next EE group is the exact loader body and these
alias/consumer dependencies; it is tracked in [#37](https://github.com/nicolas-found42/reverse-engineering/issues/37),
a blocking prerequisite of #35 and a child of #23.

Validate the public fixture seam and tools:

```sh
tools/check.sh test_misc3d_lifecycle test_misc3d_contract \
  test_compiler_probe_recipe test_matching_ranges
pyright tools/misc3d_lifecycle.py tools/misc3d_lifecycle_observation.py \
  tools/misc3d_lifecycle_recipe/controls.py tools/test_misc3d_lifecycle.py \
  tools/misc3d_contract.py
PYTHON=/Users/Nicolas/Documents/github/hermes/coder-prompt-evals/.venv/bin/python \
PS2RECOMP_SOURCE_ROOT="$PWD/.scratch/mesh/codex-root/PS2Recomp" tools/check.sh
python3 tools/ip_rails.py --tree
```

[The suite log](whole-suite.log) records 683 tests passing with 22 skips; local
ignored mesh inventories and the declared installed translator are needed for
that run. The bounded source/control receipts are the applicable reconstruction
evidence; a passing synthetic suite does not complete #35 or whole-image gates.
[The Jev record](jev.json) retains the actual safe request, evidence hashes, full
result distributions and disposition. Jev escalated with a weak common/NOBITS
contradiction (confidence 0.22; contradicted 0.48 versus verified 0.46) and
`safe_to_apply: 0.08`. An independent reasoner verified all five raw symbol tables
(`SHN_MIPS_SCOMMON`, size/alignment four) and linked ELF section headers
(NOBITS, flags three, size/alignment four), resolving that bounded issue without
rewriting the original escalation. Exact byte checks remain authoritative.

The independent raw ELF crosscheck above can be reproduced directly, without
calling the lifecycle checker or its parser. It verifies the exact reviewed
object/link hashes before decoding ELF32 little-endian section and symbol
tables. Private artifact paths come from the preserved reviewed receipt:

```sh
python3 - <<'PY'
import hashlib, json, struct
from pathlib import Path
receipt = json.loads(Path('notes/evidence/fr2-misc3d-lifecycle/reviewed_source_build.json').read_text())

def load(name):
    record = receipt['details']['artifacts'][name]
    data = Path(record['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == record['sha256']
    assert data[:6] == b'\x7fELF\x01\x01'
    offset = struct.unpack_from('<I', data, 32)[0]
    stride, count, names = struct.unpack_from('<HHH', data, 46)
    assert stride == 40
    rows = [struct.unpack_from('<10I', data, offset + i * stride) for i in range(count)]
    strings = rows[names]
    section_names = data[strings[4]:strings[4] + strings[5]]
    return data, rows, section_names

for cell in ('db_id', 'state_c8', 'state_cc', 'state_d0', 'state_d4'):
    data, rows, _ = load(cell + '_object')
    found = []
    for row in rows:
        if row[1] != 2:
            continue
        assert row[9] == 16
        strings = rows[row[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for offset in range(row[4], row[4] + row[5], 16):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', data, offset)
            if names[name:].split(b'\0', 1)[0] == ('misc3d_' + cell).encode():
                found.append((value, size, info, index))
    assert found == [(4, 4, 17, 0xff03)], (cell, found)
    print(cell, 'MIPS small-common', found)

data, rows, names = load('linked_output')
for cell, address in (('db_id', 0x290ac4), ('state_c8', 0x290ac8),
                      ('state_cc', 0x290acc), ('state_d0', 0x290ad0), ('state_d4', 0x290ad4)):
    selected = [row for row in rows if names[row[0]:].split(b'\0', 1)[0]
                == ('.sbss.fr2_misc3d_' + cell).encode()]
    assert len(selected) == 1
    row = selected[0]
    assert (row[1], row[2], row[3], row[5], row[8]) == (8, 3, address, 4, 4)
    print(cell, 'NOBITS', hex(address), 'flags', row[2], 'size/alignment', row[5], row[8])
PY
```
