# compiler-iop-source-reconciliation: fail

Invalid: GNU download or candidate original archive differs

```json
{
  "source_archive": {
    "bytes": 77925391,
    "sha256": "b33ac7197cc8d4d28eb42275a05d800c126ff32ac3915624470ee55cdb5ee6ad"
  },
  "gnu_archives": {
    "gcc-2.8.1": {
      "url": "https://ftp.gnu.org/gnu/gcc/gcc-2.8.1.tar.gz",
      "bytes": 8447495,
      "sha256": "3b30fbfdf93e628373d90d174243f3267b0eec9ebe792bb64fd15b8828c2ea4c",
      "downloaded": null,
      "candidate_member_equal": false
    },
    "binutils-2.9.1": {
      "url": "https://ftp.gnu.org/gnu/binutils/binutils-2.9.1.tar.gz",
      "bytes": 5694541,
      "sha256": "58d01daa576d8779e064922171276795f00ff1388b1b0f87aa1a00eb0da6c6bb",
      "downloaded": {
        "bytes": 42,
        "sha256": "8a6254cae5c0ff3a1ad24cf9e17f9e95a3ad3918ceb10e41661ab32dda289a2a"
      },
      "candidate_member_equal": false
    }
  },
  "comparison": {},
  "missing": [
    "gcc-2.8.1"
  ],
  "changed": [
    "binutils-2.9.1"
  ],
  "historical_binding_status": "incomplete",
  "matched_bytes": 0,
  "limitations": [
    "Source derivation only; no compiler was built and no game code was executed.",
    "GCC 2.8.1 and its IOP retargeting patch do not bind the selected EE 2.96 package.",
    "Changed modern source files are retained as differences, not assumed behavior-preserving."
  ]
}
```
