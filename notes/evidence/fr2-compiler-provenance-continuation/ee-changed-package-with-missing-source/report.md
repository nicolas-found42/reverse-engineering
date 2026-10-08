# compiler-provenance: fail

Invalid: selected compiler archive differs from its recorded pin

```json
{
  "target_version": "2.96-ee-001003-1",
  "source_archive": null,
  "inventory_status": "incomplete",
  "source_version": null,
  "version_relation": "unresolved",
  "members": {},
  "missing": [
    "source archive"
  ],
  "changed": [],
  "historical_binding_status": "incomplete",
  "redistribution_disposition": "unresolved",
  "matched_bytes": 0,
  "binding_reasons": [
    "No recorded distributor/source-build relation binds this source to the selected package.",
    "Selected compiler archive is missing or differs from its recorded pin."
  ],
  "limitations": [
    "A version-compatible source and notice inventory do not bind a historical binary.",
    "This audit grants no package permission or ownership/matching credit.",
    "No source candidate was built and no game code was executed by this audit."
  ],
  "selected_package": {
    "candidate": "ee-gcc2.96",
    "archive": "ee-gcc2.96.tar.xz",
    "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
    "observed": {
      "bytes": 49,
      "sha256": "896939d3dcb981b5ba3035802d05cd197bed420416b312c88f58d87d76274ffa"
    },
    "identity_status": "fail"
  }
}
```
