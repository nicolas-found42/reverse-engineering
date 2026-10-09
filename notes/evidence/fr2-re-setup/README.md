# Local static RE setup verification

Established: [verification.json](verification.json) retains version/source pins,
nine configured stdio launches, native client discovery and synthetic Ghidra
analysis/rejection controls. The dedicated local token is omitted. No game code
was executed. Ghidra's host and EE extension are tested independently: the
synthetic ARM function decompiles to `value * 3 + 7`, and the EE language decodes
a synthetic `jr ra` instruction with P-code.

The native omp checks use an isolated auth/cache profile with exact copies of
only the three RE entries, and an unused synthetic model placeholder. Its local
`/mcp test` handler reports `agentInvoked: false`. Native Codex uses an ephemeral
app-server context and Claude uses `mcp get`; no model prompt is issued. Native
omp discovery predates the local bridge patch; all nine exact configured entry
launches are rechecked after it. Native Codex also rechecks decompilation.

The bridge patch binds project open and archive restore to the configured file
root. Actual rejected calls cover missing selectors, arbitrary scripts,
out-of-root create/open paths and restore input/output paths. The launcher pins
the patch and installed JAR. The old 8089 backend contained only a synthetic probe;
it was saved and stopped after the authenticated 8090 backend passed. The old
Ghidra installation and project are retained.

Not established: a universal process sandbox, read-only Ghidra editing, every
optional REA provider, real-game runtime behavior or completed reconstruction.
The full local completion command returns `incomplete`/exit 2, retains a fresh
60-byte source match, and leaves 3,506,988 load-image bytes unresolved. The portable
structural progress report independently earns zero fresh build credit.

Machine-specific logs, test drivers and build copies remain under ignored
`.scratch/setup-2026-10-08/`. Recheck discovery and current runtime controls with:

```sh
claude mcp get ghidra
claude mcp get rea
claude mcp get radare2
python3 tools/re_mcp.py status
re-python .scratch/setup-2026-10-08/pyghidra-rabbitizer-check.py
re-python .scratch/setup-2026-10-08/ee-synthetic-check.py
ctest --test-dir .scratch/setup-2026-10-08/ccc/build --output-on-failure
rea doctor --provider ghidra
r2 -n -N -q -c 'i;afl' .scratch/re-setup/probe
stdump identify games/ford-racing-2/extracted/IRX/STREAM.IRX
```

The full local command and installation/rollback details are in
[RE-SETUP](../../../docs/RE-SETUP.md). The recorded setup base revision is
`75c406a125534bce1229c5b7c3598f892e4cd3ab`; verification JSON SHA-256 is
`94f60b3056b167bf088d1f87a3a653bd6a35e9d817600b016344d5a4090ed579`. This snapshot includes explicit source/distribution pins rather
than treating that parent revision as the final commit identity.

## Advisory review disposition

[review.json](review.json) preserves the final Jev review distributions. The
documentation/config review escalated (`safe_to_apply: 0.23`; correctness
confidence 0.37; test-gap confidence 0.30). The core patch gate also escalated
(`safe_to_apply: 0.48`; test-gap confidence 0.25). Tests/freshness were verified
at confidence 0.92. Runtime controls were verified at 0.79 and native discovery
at 0.49, requiring review under the tool thresholds.

The combined claim about structural zero credit and the separate compiler run's
60-byte match was marked contradicted at 0.79 confidence. A direct deterministic
comparison confirms the structural report's matched/complete fields are all zero,
its game-owned category totals 60 bytes, its unresolved category totals
3,506,988 bytes, and the independent incomplete full run retains 60 matched bytes.
The distinction is recorded rather than treating the model disposition as an
accepted review. Human review is required before merging this change.

The first completion-gate attempt failed operationally with
`max_tokens_exceeded`; its input was reduced once while retaining raw core
hunks and actual evidence. The repaired gate's escalation stands.

After review, the new TSV decision tables were normalized from CRLF to LF,
and blank patch-context lines were expressed as unchanged remove/add pairs.
The decision-table pins and structural snapshot were remeasured, and the
reviewed patch hash was updated. Java source, the installed JAR, ownership
ranges and report measures are unchanged. The advisory dispositions stand.

The first real push rejected archived snapshots because index reconstruction
dropped already-tracked ignored files and older notes linked absent scratch
artifacts. Force-adding the exact archive file set and explicitly labeling those
references as local artifacts corrects both cases without skipping the link
check. A fresh staged snapshot preserves all 2,187 tracked paths and passes the
portable gates; 58 targeted tests pass, including the ignored-file regression.
The subsequent correction review also escalated on blast-radius confidence
0.07, despite correctness confidence 0.90 and composite 0.85725. Its distribution
is retained alongside the earlier whole-change dispositions.
