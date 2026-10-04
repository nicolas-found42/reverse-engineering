# `00200d10` isolated experiment command record

All source inputs were the ELF `games/ford-racing-2/extracted/SLES_517.05`, final-3841 export in `.scratch/mesh/codex-audit/ee-union-final-01/reopened-export`, and `tools/ghidra/experimental/CreateEeClosureCandidate.java`. The project-tree digest for clean copies matched the source `ghidra-project/codex-audit-ee-union-04` at `697c7290ec71ba4bb87be917c804cc058a4b1624732afbf3e8b71c210bca74cc` over nine files.

The first headless invocation omitted `JAVA_HOME`:

```sh
.scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless .scratch/mesh/codex-audit/ee-00200d10-candidate-01/project fr2 -process SLES_517.05 -noanalysis -scriptPath tools/ghidra -postScript CreateEeClosureCandidate.java .scratch/mesh/codex-audit/ee-00200d10-candidate-01/candidate.json games/ford-racing-2/extracted/SLES_517.05 .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/manifest.json .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/inventory.json -log .scratch/mesh/codex-audit/ee-00200d10-candidate-01/run.log
```

It stopped before Ghidra: macOS reported “Unable to locate a Java Runtime.” The next command set `JAVA_HOME` to the installed OpenJDK 27 but still supplied the parent script directory rather than `tools/ghidra/experimental`:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless .scratch/mesh/codex-audit/ee-00200d10-candidate-01/project fr2 -process SLES_517.05 -noanalysis -scriptPath tools/ghidra -postScript CreateEeClosureCandidate.java .scratch/mesh/codex-audit/ee-00200d10-candidate-01/candidate.json games/ford-racing-2/extracted/SLES_517.05 .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/manifest.json .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/inventory.json -log .scratch/mesh/codex-audit/ee-00200d10-candidate-01/run.log
```

It stopped at script validation with “Script not found.” Supplying the nested script path while keeping the project under hidden `.scratch` failed before project opening because Ghidra rejects project path components starting with `.`. That command and its log are `run-retry01.log`.

After copying the untouched source project to a non-hidden `ghidra-project` directory, the initial guard failed before the candidate transaction. It compared exporter `blocks` rows as function bodies; `001f36a0` disproved that assumption. The failure JSON is `candidate.json`, with `run-retry02.log`.

The next fresh-copy run reconstructed old function bodies from inventory instruction-address rows and reached the candidate. It rolled back because the expected `AddressSet` ended at the start byte `00200dd8`, not the last byte `00200ddb` of its 4-byte instruction. The command was:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless ghidra-project/codex-audit-ee-00200d10-candidate-02 fr2 -process SLES_517.05 -noanalysis -scriptPath tools/ghidra/experimental -postScript CreateEeClosureCandidate.java .scratch/mesh/codex-audit/ee-00200d10-candidate-01/candidate-attempt02.json games/ford-racing-2/extracted/SLES_517.05 .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/manifest.json .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/inventory.json -log .scratch/mesh/codex-audit/ee-00200d10-candidate-01/run-attempt02.log
```

An instrumented fresh-copy run recorded Ghidra's actual computed body `00200d10-00200ddb` and the incorrect expected body `00200d10-00200dd8`; it rolled back before function creation. See `candidate-attempt03.json` and `run-attempt03.log`.

The corrected single-candidate invocation succeeded on a fourth fresh copy:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless ghidra-project/codex-audit-ee-00200d10-candidate-04 fr2 -process SLES_517.05 -noanalysis -scriptPath tools/ghidra/experimental -postScript CreateEeClosureCandidate.java .scratch/mesh/codex-audit/ee-00200d10-candidate-01/candidate-attempt04.json games/ford-racing-2/extracted/SLES_517.05 .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/manifest.json .scratch/mesh/codex-audit/ee-union-final-01/reopened-export/inventory.json -log .scratch/mesh/codex-audit/ee-00200d10-candidate-01/run-attempt04.log
```

It reported `EE_CLOSURE_CANDIDATE_OK entry=00200d10 body_bytes=204 function_count_delta=1` and `candidate-attempt04.json` has `created_single_bounded_candidate`.

The first combined export invocation pre-created the output directory; `ExportDecompilation` correctly refused to overwrite it. The same invocation still succeeded at `ExportEvidence` and `ExportCoverage`. Its log is `export.log`. A separate fresh output path then completed a full 3,842-function pseudocode export:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless ghidra-project/codex-audit-ee-00200d10-candidate-04 fr2 -process SLES_517.05 -noanalysis -scriptPath tools/ghidra -postScript ExportDecompilation.java .scratch/mesh/codex-audit/ee-00200d10-candidate-01/decompilation 30 -log .scratch/mesh/codex-audit/ee-00200d10-candidate-01/decompile-export.log
```

It reported `processed=3842 generated=3842 failed=0`. The saved inventory and coverage from the prior combined export are under `exported/`. The ordinary manifest verifier passed:

```sh
python3 tools/verify_decompilation.py --manifest .scratch/mesh/codex-audit/ee-00200d10-candidate-01/decompilation/manifest.json --static-export .scratch/mesh/codex-audit/ee-00200d10-candidate-01/exported/inventory.json --executable games/ford-racing-2/extracted/SLES_517.05 --output .scratch/mesh/codex-audit/ee-00200d10-candidate-01/decompilation-verifier.json
```

The independent inventory/C/coverage comparison passed:

```sh
python3 .scratch/mesh/codex-audit/ee-00200d10-candidate-01/reconcile_00200d10.py
```

It reported `PASS_RECONCILIATION`; its durable JSON is `reconciliation.json`. No game was run and no emulator was used.
