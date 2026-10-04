# Observed IOP import/export candidates

The [bounded crosswalk](../../../tools/ps2_irx_crosswalk.py) parses module ELF bytes and matches the literal library name, full version, and positional export ordinal. It preserves every observed provider when a tuple is ambiguous and leaves unmatched stubs unresolved. It requires the measured base-zero `.text` profile and rejects unaligned or out-of-text export offsets. These checks identify static candidates; they do not implement registration, relocation, loader order, or runtime binding.

The real-corpus run first used the existing exact 24-module inventory/ROMDIR verifier, then rechecked each module slice's size and hash before parsing it. The two inventory inputs are also checked for changes during traversal. [The result](corpus-result.json) records 748 import stubs, 28 export tables, and 296 export entries. There are 217 unique candidates, zero ambiguous candidates, and 531 stubs with no observed exact-version candidate. Every output edge explicitly has `runtime_binding_verified: false`. A missing exact match does not establish that the running game lacks a provider: firmware, other versions, and loader compatibility are outside this experiment.

An independent byte-level correlation against the copied historical Ghidra database gives a concrete source-recovery backlog. [The correlation metadata](export-listing-correlation.json) pins the module and coverage-receipt hashes for every export row. Among 296 positional rows, 181 point to saved function entries, 48 point to unowned decoded instructions, and 67 point to undefined listing bytes. Duplicate exports share targets: the corresponding distinct module/target counts are 181, 10, and 30, totaling 221. The raw `.text` hashes agree with Ghidra block hashes; the language/compiler identities are `MIPS:LE:32:default`/`default`. This is a listing classification, not proof of callable semantics, original boundaries, or runtime reachability. It refers to the historical 2,241-function database before the isolated entry/export candidates.

The full Python suite passes 261 tests in 42.301 seconds; [the complete log](full-python-suite.log) is retained. Nine [focused tests](focused-tests.log) pass. They falsify exact matching with separate library/version/ordinal mutations; preserve two-provider ambiguity; reject duplicate source keys, unaligned/out-of-range targets, and nonzero `.text` addresses; and test source-slice drift, path escape, and inventory changes after the prerequisite verifier. The latter filesystem tests inject a small synthetic verifier result to isolate the handoff between verification and candidate extraction; they do not substitute for the real 24-module run. [Pyright](pyright.log) reports zero errors, warnings, or informations.

Jev's original [r072 gate](r072-jev-gate.json) remains escalated. Its count claim is verified at 0.98; the scope/bounds claim is verified with low confidence at 0.41; its seven-test claim is unsupported at 0.92. The test output was supplied in the gate's `tests` field, but omitted from its separate verification `evidence` array. The exact original seven-test log is retained in [initial-seven-tests.log](initial-seven-tests.log), and the two later filesystem tests are recorded separately. Direct source inspection and native test execution establish those bounded facts; the model result has not been retried for a favorable verdict. The patch review's test-gap/blast-radius uncertainty remains open, so the crosswalk makes candidate-only claims.

The initial missing-module red test is retained. During CLI integration, the first run called the shared result writer with the wrong signature and raised `TypeError`; this was corrected to the repository's existing `write_result(output, check, action, inputs)` contract before the passing corpus run. An earlier scratch crosswalk agrees on the counts but is superseded by this reproducible tool. No module payload, decompiled game source, or credentials are included here; no original routine ran.

Reproduce the candidate metadata from the local extracted corpus:

```sh
python3 tools/ps2_irx_crosswalk.py games/ford-racing-2/extracted \
  --inventory .scratch/mesh/codex-root/executable-inventory-01.json \
  --boundaries .scratch/mesh/codex-root/executable-boundaries-01.json \
  --out .scratch/evidence/iop-observed-crosswalk
python3 -m unittest discover -s tools -p test_ps2_irx_crosswalk.py
```

The next recovery step is to inspect the 10 decoded export targets with no saved function and the 30 undefined targets, using exact module/table provenance and isolated, guarded Ghidra experiments. Their classifications do not authorize broad disassembly or automatic source-level naming.
