# Native GS address helper parity

Four actual PS2Recomp C++ header helpers agree with an independently parsed
PCSX2 table oracle in 2,359,296 synthetic coordinate cases. The tested helpers
are `addrPSMCT32`, `addrPSMCT16`, `addrPSMT8`, and `addrPSMT4` from revision
`c5a9d02573410a2085a4b4b831b0b68ba3515440`. Each header's current bytes also
match its Git HEAD blob and the corresponding four-patch source copy.

The reference uses PCSX2 GSTables.cpp at revision
`81526d4dc7cc70e4ae75abb35a789417456c6d43`, raw source SHA256
`a9a226297ede32b89177d7bdb04e9d8e21728e7d55799405f6112e97fe4969e8`.
The public source was retrieved with Firecrawl and reconciled with raw GitHub
bytes in the [texture upload audit](../fr2-texture-upload-audit/README.md).

The probe includes and calls the actual headers. The Python oracle parses the
public block/column arrays and computes page, block and column offsets in the
appropriate units: bytes for CT32, CT16 and T8; nibbles for T4. The test covers
every coordinate in two-by-two-page domains, six block bases (`0,1,31,32,33,16383`),
and buffer widths `1,2,4,8` for CT32/CT16 or `2,4,8` for T8/T4. Width0 and indexed
width1 remain outside this experiment. Values beyond VRAM size are logical
address arithmetic only; wrap and memory accesses were not tested.

| Helper | Compared addresses | Actual mismatches | Mutant mismatches |
| --- | ---: | ---: | ---: |
| CT32 | 196,608 | 0 | 196,608 |
| CT16 | 393,216 | 0 | 393,216 |
| T8 | 589,824 | 0 | 589,824 |
| T4 | 1,179,648 | 0 | 1,179,648 |

The harness builds with undefined-behavior sanitization and recovery disabled.
Both invocations exit0 with empty sanitizer stderr. They dump address values;
the Python oracle checks agreement. The negative control flips one output bit
and every comparison detects that mismatch. The negative invocation is not
expected to exit1 because the comparison occurs outside that binary.

[result.json](result.json) retains exact sources, compiler arguments, binary
and output hashes, domains and counters. [probe.cpp](probe.cpp) and
[audit_native_gs_addresses.py](audit_native_gs_addresses.py) are authored
synthetic probes, not original game code. The original fresh run remains under
`.scratch/mesh/codex-root/gs-address-native-01/`; the script deliberately rejects
an existing output directory to preserve that result.

Jev verified all three bounded result/scope claims, while the patch review
escalated with `safe_to_apply=0.36` and low correctness/test-gap confidence.
[The exact gate](jev-gate.json) is preserved unchanged, with no favorable
retry or automatic acceptance. [Manual validation](manual-validation.json)
checks source identity, native status and stderr, independent units/base carry,
enumeration length and every mutant mismatch count.

Only arithmetic helpers executed with synthetic inputs. No original game
routine, GS device, renderer, emulator, or linked game runner was executed.
This does not prove transfers, CLUT/mip loading, color semantics, timing,
hardware behavior, or a fully decompiled game.
