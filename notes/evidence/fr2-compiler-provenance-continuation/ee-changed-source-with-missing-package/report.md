# compiler-provenance: fail

Invalid: fixed source candidate differs from its recorded pin

```json
{
  "target_version": "2.96-ee-001003-1",
  "source_archive": {
    "bytes": 187,
    "sha256": "e586659d8aee7715900cd5d0f5882975b07b87dc5ccc413cd2d4009e7cf8a445"
  },
  "inventory_status": "incomplete",
  "source_version": null,
  "version_relation": "unresolved",
  "members": {},
  "missing": [
    "ee/gcc/version.c",
    "ee/gcc/COPYING",
    "ee/gcc/config/mips/elf64.h",
    "build.sh",
    "iop/gcc-2.8.1/version.c",
    "iop/gcc-2.8.1/COPYING",
    "iop/original/gcc-2.8.1.tar.gz",
    "iop/original/binutils-2.9.1.tar.gz",
    "iop/original/iop-gcc.patch",
    "iop/original/make-iop-gcc.sh"
  ],
  "changed": [
    "source archive"
  ],
  "historical_binding_status": "incomplete",
  "redistribution_disposition": "unresolved",
  "matched_bytes": 0,
  "binding_reasons": [
    "No recorded distributor/source-build relation binds this source to the selected package.",
    "Source version declaration is missing or malformed.",
    "Source candidate identity or required material is missing or changed.",
    "Selected compiler archive is missing or differs from its recorded pin."
  ],
  "limitations": [
    "A version-compatible source and notice inventory do not bind a historical binary.",
    "This audit grants no package permission or ownership/matching credit.",
    "No source candidate was built and no game code was executed by this audit."
  ],
  "notice_inventory": {
    "ee/gcc/COPYING": "missing",
    "iop/gcc-2.8.1/COPYING": "missing"
  },
  "selected_package": {
    "candidate": "ee-gcc2.96",
    "archive": "ee-gcc2.96.tar.xz",
    "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
    "observed": null,
    "identity_status": "incomplete"
  }
}
```
