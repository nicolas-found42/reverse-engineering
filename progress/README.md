# Progress report

[report.json](report.json) uses objdiff Report v2 for a structural load-image
inventory. All `matched_*` and `complete_*` measures are zero. The one locally
attributed 60-byte source unit is in `game-owned`; other ranges are tagged both
`mixed` and `unresolved`. Those categories overlap: do not add them to form a
denominator. No percentage or census of original functions is reported.

Code measures cover sections named `.text`, `.text.*`, `.init`, `.fini`, and
`.vutext`; remaining load-image storage, including zero-fill and unmapped bytes,
is carried by data measures. This is section accounting, not semantic recovery.

[provenance.json](provenance.json) binds the structural snapshot and source pins,
and identifies the archived compiler-summary source separately. Historical
60-byte match credit is not imported into this corpus-free export.

```sh
python3 tools/repository_hygiene.py generate
python3 tools/repository_hygiene.py check
```

CI uploads `report.json` as `SLES_517.05_report`, following the
[decomp.dev ingestion contract](https://github.com/encounter/decomp.dev/blob/main/crates/github/src/lib.rs).
Uploading an artifact does not register the repository on a hosted dashboard.
The format comes from [objdiff v3.8.2 report.proto](https://github.com/encounter/objdiff/blob/v3.8.2/objdiff-core/protos/report.proto).
