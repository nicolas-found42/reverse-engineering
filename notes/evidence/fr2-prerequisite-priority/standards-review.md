# Final Standards-axis review

Baseline: `e8b65417bc5d80f4fb85c91dacefe761a6d9f236`.
Reviewed merged head: `9c4f9fac9f7060959dfa73b8ea5a8e235943671a`.
Repair delta: `fe44c0c0357fb988ee24b657dd0f473734bdf3b8...9c4f9fac9f7060959dfa73b8ea5a8e235943671a`.
Sources: repository `CODING_STANDARDS.md`, `AGENTS.md`, and the parent-supplied
advisory smell baseline. Compiler evidence includes this reviewer's authorship;
the parent independently inspected its raw/projection correspondence.

## Report (under 400 words)

**No remaining documented-standard violation or material advisory smell found
in the reviewed integration changes. Initial finding F1 is fixed.** The Qt
preflight collects missing library paths while checking available libraries
first. Missing Core plus changed Gui, and missing legacy plugin plus changed
Gui, now fail before runtime creation/guest launch. The changed Gui SHA-256 is
retained in the immutable CLI receipt.

I independently executed the five affected focused modules: **53 tests passed**.
The controls confirm these bounded facts:

- **Lifecycle:** available source hash mismatches fail despite absent current
  observation, previous provenance, or another source. Missing-only source
  evidence remains incomplete; CLI inputs retain available source, decision
  and observation identities.
- **Observation:** available changed EE, wrong boundary scalars, and saved
  instruction bytes differing from raw ELF fail despite absent metadata or a
  counterpart inventory. Missing-only remains incomplete; available input
  hashes are retained.
- **RPC:** missing EE does not hide changed STREAM or malformed packet framing.
  A valid or unsupported packet with missing EE remains incomplete. Available
  raw-image/packet identities are retained; full handoff scope does not pass.
- **Frontier:** changed pinned STREAM or malformed available ROM fails despite
  missing EE; missing-only is incomplete. Exact module pins and the unreconciled
  parent disposition remain fixed.

The new Jev gate remains **escalate**, safe-to-apply **0.15**, composite
**0.561625**. Its lifecycle, observation, RPC and frontier contradiction
judgments have confidence **0.51, 0.67, 0.49, 0.73**. Direct inspection and
executed controls support the listed bounded claims; this independent review
dispositions those uncertain judgments without changing the original gate,
its probabilities, thresholds or historical inputs. No retry was performed.

Measured counts name reproduction commands; guards retain their actual scope;
CLI callers cannot change the fixed acceptance profile. New source-output
identity remains separate from ownership credit. Compiler-source permission,
Qt qualification, loader/alias/caller work and complete RPC handoffs remain
incomplete. **This review does not approve whole spec #5 or confer dependency
permission.** No root edits, tracker writes or push occurred.

## Execution and evidence details

Independent command from the primary root:

```sh
tools/check.sh test_headless_oracle test_misc3d_lifecycle \
  test_misc3d_lifecycle_observation test_rpc_contracts test_rpc_handoff_inventory
git diff --check fe44c0c...9c4f9f
git diff --check e8b65417bc5d80f4fb85c91dacefe761a6d9f236...9c4f9fac9f7060959dfa73b8ea5a8e235943671a
```

The focused run completed with `Ran 53 tests ... OK`. The checks of both diffs
were clean. The log is
`/Users/Nicolas/Documents/github/hermes/fr2-implementation-context/standards-final-focused.log`,
SHA-256 `1116b1ac600490b11fdc6cdf5fa9df990bcb9e80ec0e56ee4a9b3f9a8dd4126d`.
The log retains actual in-process CLI diagnostics for Qt and lifecycle;
subprocess controls assert exit status and parse their generated immutable
receipts. All guest/tool launch paths in the prerequisite tests are guarded.
Observation/RPC/frontier subprocesses are static host checks, not guest
execution. I did not rerun the whole suite or real build children; the parent
is doing that separately.

Specific code/control correspondence:

| Domain | Inspected code | Executed control evidence |
| --- | --- | --- |
| Qt/F1 | `headless_oracle.verify_inputs` checks all available fixed framework libraries before deferred absence; `main` records available hashes | `OracleDependencyPreflight` combined missing-Core/changed-Gui and missing-plugin/changed-Gui tests return 1; expected changed-library fingerprint is a literal SHA-256 assertion |
| Lifecycle | `provenance` defers `Incomplete` from previous provenance/current missing paths while comparing available hashes; CLI filters missing receipt input files so available contradictions reach the check | `LifecycleProvenanceTests` source-vs-observation, source-vs-previous, missing-source-vs-sibling, missing-only controls pass; no compiler/tool process can start in CLI prerequisite tests |
| Observation | CLI checks available executable identity, boundary map and each available inventory's actual saved words before returning collected absence; `validate_boundary` is shared with reconciliation | `LifecycleObservationPriority` changed-EE, wrong-boundary, mismatching-instruction and missing-only controls pass; synthetic instruction fixture uses `elf_fixture` |
| RPC | CLI checks each available image's fixed hash and validates available packet framing before collected absence; available files appear in `write_result.inputs` | `StreamVolumeContracts` combined missing-EE/changed-STREAM and packet cases pass, with receipt identity assertions; retained real static-control commands/receipts in `rpc-controls.json` remain 0/1/2 and combined 2/1/2 |
| Frontier | `inventory_handoffs` checks available EE, ROM parsing and pinned modules while deferring absent inputs; main always reports unreconciled parent incomplete | `RpcFrontierPriority` changed-module, malformed-ROM and missing-only CLI controls pass and retain available input paths/fingerprints |

Raw gate files remain unchanged in
`notes/evidence/fr2-prerequisite-priority/`:

- `gate-result.json`: SHA-256 `57a391c2841c3547ec99a162f2cbfcefb436d5e8e9e66980937b130e8bcfafea`.
- `gate-input.json`: SHA-256 `7a281b5dee856b5a180069965751313ad90d8a2561c546ddc6900babdf7ad087`.

The original model/provider identity and complete probability distributions
remain in the raw result. This report is an independent reasoning disposition,
not a replacement semantic judgment or automatic gate acceptance.
