# Fresh EE compiler panel acceptance audit

This audit ran the unchanged fixed four-unit/seven-candidate recipe at source
revision `e8b65417bc5d80f4fb85c91dacefe761a6d9f236`, on 2026-10-08. It reproduces
the corrected panel result: `ee-gcc2.96` is the sole candidate passing both the
pre-link diagnostic and exact linked comparison for every unit. All 28
combinations completed without operational gaps. The selected profile remains
bounded to these inferred C sources, flags, package members, runtime images and
GNU ld placement. AC05 and the historical package/source identity remain
incomplete, with zero additional matched-byte credit.

Reproduce the real-corpus check from the repository root:

```sh
python3 tools/compiler_probe_recipe/run.py \
  /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  --profile --output .scratch/evidence/compiler-profile-acceptance
```

[`acceptance.json`](acceptance.json) binds the fresh local result/report hashes,
source revision, command, source/build input identities, package members,
runtime images and per-unit metadata-file hashes. Each unit JSON retains the
executed compile/preparation/link/extraction argv, compiler driver's command
trace, return codes, object/output hashes, relocation diagnostics and located
failure offsets. These are safe metadata projections, not copies of the full
local result. Instruction-byte/word values and binary payloads are omitted;
the original local receipt is retained at the path and hash in the index.
Artifact paths are recoverable from the command arrays; their fingerprints
remain in `artifacts`. These projections grant no ownership credit or package
permission. Temporary paths and debug-object hashes can differ on reproduction.

The fresh receipt has `status: pass`, `profile_status: pass`,
`selected_id: ee-gcc2.96`, `ac05_status: incomplete`, and no operational gaps.
The CLI implementation maps that pass status to exit 0; the audit records the
receipt status rather than claiming an independently captured process exit.

| Unit | Reference bytes | Candidates passing both comparisons |
| --- | ---: | --- |
| Accessor | 60 | `ee-gcc2.96` |
| Misc3d reset | 28 | 2.9, all three 2.95 packages, and 2.96 |
| Entity-list setter | 60 | `ee-gcc2.96` |
| Parser lookup | 80 | `ee-gcc2.96` |

Reproduce the public positive, negative, ambiguous, contradictory,
changed-identity and missing-evidence controls:

```sh
tools/check.sh test_compiler_probe test_compiler_probe_recipe \
  test_compiler_output test_compiler_profile test_compiler_packages
```

The fresh [`focused-tests.log`](focused-tests.log) records 42 tests passing.
This audit ran the focused checks; it does not claim a fresh whole-suite run.
The raw static inventory remains local. Its SHA-256 matches the decision's
pin, and its caller/block metadata agrees with each added unit's recorded
metadata. The setter's 56-byte inventory body remains distinct from its
60-byte contiguous comparison extent. The original contradictory panel and
source-form trials remain retained in the sibling `independent-panel/` tree.

Reproduce the independent inventory check without emitting instructions:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('/Users/Nicolas/Documents/github/hermes/reverse-engineering')
decision = json.loads(Path('notes/evidence/fr2-compiler-probe/profile-units.json').read_text())
pin = decision['evidence_inputs']['static_inventory']
path = root / pin['path']
assert hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256']
functions = {f['entry']: f for f in json.loads(path.read_text())['functions']}
for unit in decision['units']:
    function = functions[unit['vaddr']]
    assert function['callers'] == unit['static_callers']
    assert function['blocks'] == unit['body_ranges']
    print(unit['id'], function['size'], unit['bytes'], 'metadata matches')
PY
```

## Exact ticket #8 disposition

The ticket text and linked provenance prerequisite remain unchanged. A panel
selection and a fully bound compiler/profile pin have separate dispositions:

1. **Incomplete for the full source binding.** Candidate archive hashes,
   installed driver/pass/assembler/spec member hashes, runtime identities,
   recorded flags, emitted assembly commands, link commands and reconstruction
   source/object/output hashes are bound for every probe. Exact corresponding
   compiler-source identities, EE patches and package notices are still absent
   under #21. A release-archive URL is not that compiler-source binding.
2. **Satisfied for the declared EE panel.** Three hand-written units beyond the
   accessor have independent source-map/static-reference/boundary evidence.
   The setter distinguishes argument/error-call ABI; the parser distinguishes
   loop and branch-likely scheduling; the reset exercises gp stores and delay
   slots but does not distinguish the older candidates. Independent static
   evidence predates the compiler trials; the inferred C forms were explored
   against retail and are not independent original-source recoveries.
3. **Satisfied at the declared check seams.** The known matching panel selects
   its declared candidate; all nonmatches have located diagnostics. The public
   fixture suite preserves missing tools/diagnostics/corpus, ambiguity,
   contradiction and changed/missing archive-member controls. No candidate was
   skipped in the real run.
4. **Partially satisfied; the full pin remains incomplete.** The pre-link
   diagnostic excludes only supported relocation fields, while the separate
   linked gate compares every byte. This supports the declared EE profile
   selection. It does not resolve the compiler-source identity in #21, prove
   the original compiler, or complete the GNU linker contract in #9. Relevant
   game-owned IOP probes are outside this EE ticket's panel and remain required
   for aggregate AC05.
5. **Satisfied.** Ambiguous/contradictory source-form trials and their limits
   remain visible. The new run does not rewrite earlier failures, infer
   dependency permission, or close the separate package-provenance ticket.

**#8 cannot validly close under the unchanged full acceptance text and open
#21 provenance dependency.** The bounded profile implementation and fresh
selection evidence are complete. Resolving the remaining pin requires a
distributor/rightsholder record or independently verifiable corresponding
source tying archive hash
`0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a`
or `2.96-ee-001003-1` to the exact source, EE patches, applicable notices and
terms. The [existing provenance disposition](../package-provenance.md)
states the unresolved evidence boundary; no new upstream contact or package
permission is claimed here.
