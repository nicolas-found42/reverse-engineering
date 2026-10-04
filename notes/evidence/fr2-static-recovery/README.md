# Ford Racing 2 static code recovery

This evidence records continued recovery of the unchanged PAL executable and its IOP and VU code. It provides reproducible parsers, pseudocode export checks, physical byte coverage, and preserved Jev judgments. The game is not fully decompiled: function discovery and types remain provisional, actual IOP allocation and linking remain unknown, and whole-game behavioral equivalence is unproved. A generated host executable now links statically, as described below.

The input executable is `games/ford-racing-2/extracted/SLES_517.05`, SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`. All work was static and offline after fetching tool research. Full generated game C, assembly, binaries, and Ghidra projects remain in ignored local scratch. This directory preserves metadata and judgments rather than those dumps.

The earlier integrated checkpoint is recorded in [the combined recovery bundle](../fr2-combined-recovery/README.md). That copied project exports 3,838 C artifacts with no decompiler API failures and 606 warning comments. This includes one explicitly provisional 72-byte leaf; the prior 3,837 artifacts are unchanged by that addition. The listed physical instruction inventory covers 941,916 bytes. The independent PS2Recomp translator emits 4,746 function units and a registration unit; all units compile into a local archive after the later four-patch experimental translator variant. [A static host link](../fr2-link-interface-audit/README.md) contains all 4,746 guest entry addresses and one definition of each registration global. The executable has not run; runtime fallbacks, VU execution and device behavior remain unproved.

The combined address accounting represents 1,227,700 physical address bytes through Ghidra instructions or translator instruction comments. The remaining EE gaps contain 1,483 zero-valued words (5,932 bytes); this does not classify them as padding. VU regions are accounted separately. Comment/address presence does not prove correct semantics, original function boundaries, reachability, or executable game coverage. The immutable checks and exact input identities are in the combined bundle.

The later [IOP relocation model](iop/relocation-model.md) applies 24,783 observed relocations to synthetic load images for all 24 measured modules. It agrees with the pinned public SDK arithmetic and strict corpus profile, but establishes neither the game's loader revision nor its runtime addresses. [Exact-version SDK annotations](../fr2-iop-api-catalog/README.md) supply 436 provisional names for 748 import stubs; 312 remain unresolved. These are candidate API names, not recovered original symbols.

A later [four-patch experimental translator variant](../fr2-fpu-static-audit/root-integration/README.md) adds bounded conversion, signed-zero min/max, and square-root repairs. All 4,746 regenerated function units and registration compile into a separately validated archive, and its integration checkpoint passed 252 Python tests. The corrected object-field checkpoint passed 270 tests. Its FPU patch review remains escalated; general EE floating-point rules and hardware behavior are unproved. [The integer-division matrix](../fr2-integer-division/README.md) and [FPU compare/branch audit](../fr2-fpu-control-audit/README.md) record additional bounded source checks. [The IOP gap audit](../fr2-iop-recovery-gap/README.md) identified 13 absent metadata entry starts. [Guarded entry recovery](../fr2-iop-entry-recovery/README.md) creates those provisional functions from existing instructions in an isolated database; 720 functions in the 13 affected modules export with zero API failures. Four old pseudocode files change because the base-zero function symbol replaces printed null pointers; no runtime call is established. The later [export-target recovery](../fr2-iop-export-recovery/README.md) saves and reopens a complete 24-module union of 2,388 generated functions with zero API failures. Its 147 added entries remain provisional, nine old C artifacts change, and warning counts rise from 91 to 106; all old function entries/names/bodies and memory bytes are preserved.

The latest [guarded EE candidate union](../fr2-ee-unresolved-audit/README.md) contains 3,841 generated functions with no API failures. Three exact CFG bodies add 692 function-owned bytes. Every prior function identity, body and instruction word is preserved; only one prior C artifact changes as three calls resolve to a provisional candidate. `.text` listing coverage increases by173 instructions / 692 bytes while unowned instruction totals and defined-data counts remain unchanged. Candidate identity, source types and semantic behavior remain unproved.

The [texture upload audit](../fr2-texture-upload-audit/README.md) statically interprets all 2,370 level-zero images across formats 1/3/4 in the unchanged 56-model baseline. This corrects the earlier universal eight-bit swizzle assumption on 230 direct-upload images and covers 469 four-bit images, including 19 with 256-entry palette blocks. The current full suite passes 297 tests; six texture files pass pyright with zero errors. Jev review escalation and all superseded/failing runs remain visible. Mips, render equivalence and whole-game completeness remain unresolved.

The [geometry VIF contract](../fr2-geometry-vif-contract/README.md) connects serialized stream pointers/counts to bounded packet fields. The [VU dispatch trace](../fr2-geometry-vu-dispatch/README.md) identifies MSCAL 0x5cc and its exact overlay bytes. TOP state, complete VIF unpack state, output units, vertex/index semantics, and runtime scheduling remain unproved.

## Historical baseline results and remaining limits

The rows below preserve the earlier baseline measurements. Subsequent counts and repairs are reported above and in their separate immutable bundles; baseline result files are not rewritten.

| Area | Measured result | What remains unresolved |
| --- | --- | --- |
| EE saved function export | The standard copied-project export contains 3,836 C artifacts for 3,837 function entries and one API failure. A guarded override in a private native tool copy produces 3,837 artifacts, zero API failures, and 608 warning comments. | Generated pseudocode is not recovered original source. The manual override is experimental. Warnings and provisional function boundaries require review. |
| EE physical byte inventory | 941,700 bytes of listed R5900 instructions match the ELF; 305,628 bytes remain outside that inventory, out of 1,247,328 bytes in physical executable regions. | Unlisted bytes include code, tables, padding, and VU code. These counts are byte accounting, not a percentage of game behavior recovered. |
| Synthetic VU overlays | 13,584 zero-filled placeholder bytes are excluded from physical code coverage only after validating the overlay table, actual load addresses, and ELF load mapping. | An overlay's VU address cannot identify its physical code bytes on its own. Nonzero or unmapped placeholders leave classification incomplete. |
| VU instruction recovery | All eight mapped chunks, 13,584 bytes and 1,698 instruction pairs, reassemble byte for byte with native DVP binutils. | Encoding agreement does not prove geometry meaning, timing, scheduling, or full runtime behavior. |
| VIF upload packets | Eight MPG payloads match the overlays on bytes, exact file offsets, and load addresses. Seven chunks cover VIF1/VU range `[0,12464)` and one covers VIF0/VU range `[0,1120)`. | Ownership is conditional on the guarded routines executing. No runtime transfer or completion was observed. See the [VIF evidence](vif/README.md). |
| Model section boundaries | All 56 archive-pinned model files reach exact EOF: 54 use the loader-derived 68-byte later header, two use an explicitly measured 60-byte legacy profile. | The current executable's loader does not show selecting that legacy profile. Vertex, index, animation, and renderer semantics remain unresolved. |
| Executable enumeration | The observed extracted tree contains the main EE ELF and 24 IOP modules, including 15 ROMDIR-embedded modules and nine loose IRX files. | ELF-magic enumeration does not discover raw, compressed, or dynamically created code and is not an independent archive-completeness oracle. |
| IOP pseudocode | All 24 modules imported and analyzed with the corrected MIPS language; 2,241 saved functions produced pseudocode, with 91 warning comments and no API errors. | Ghidra uses synthetic GP values, skips the custom module segment, and has no proven runtime load-base relocation model for these IRX files. See the IOP evidence. |

The six immutable result copies in `results/` retain their original status. The guarded saved-inventory export passes its narrow integrity check; physical code coverage is deliberately `incomplete`. Earlier failures remain in their original local result directories. A success in one check does not upgrade another check.

## Recovery tools

Run these commands from the repository root. Each verifier writes a fresh UTC and UUID result directory and returns 0 for `pass`, 1 for `fail`, or 2 for `incomplete`.

```sh
python3 tools/verify_executables.py games/ford-racing-2/extracted --output .scratch/evidence/executables
python3 tools/verify_sections.py corpus games/ford-racing-2
python3 tools/verify_code_inventory.py \
  --static-export .scratch/mesh/codex-helpers/data-table-static-inventory-01.json \
  --executable games/ford-racing-2/extracted/SLES_517.05
python3 tools/verify_decompilation.py \
  --manifest .scratch/mesh/codex-root/decompile-guarded-3837-01/manifest.json \
  --static-export .scratch/mesh/codex-helpers/data-table-static-inventory-01.json \
  --executable games/ford-racing-2/extracted/SLES_517.05
python3 tools/verify_vu.py games/ford-racing-2/extracted/SLES_517.05 \
  --objdump .scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump \
  --assembler .scratch/mesh/codex-root/binutils-dvp-build/gas/as-new
python3 tools/verify_vif.py --output .scratch/evidence/vif
```

The Ghidra scripts `ExportDecompilation.java` and `ExportCoverage.java` export the saved function inventory and initialized listing classifications. They expose gaps separately from decompiler status. The first script uses a fresh output directory, checks native completion, saves each generated artifact's byte count and hash, and keeps partial or cancelled runs incomplete.

The experimental script and native patch under `tools/ghidra/experimental/` recover the duplicate-target switch at `0017f510` only under exact executable, table, opcode, and generated-C guards. The loop reaches table entries 1 through 6; entries 3 and 6 share the target that sets argument 5. The native patch retains duplicates through clone and serialization. Unique-address overrides keep the original set-based behavior. A deliberately wrong duplicate order falls back rather than accepting the false selector ordering. This does not repair general backward normalization. The standard export's failure row remains preserved.

## Native tool provenance

The native macOS Ghidra decompiler was built from the Ghidra 12.1.3 release source with `make -j8 ghidra_opt CXX=clang++ ARCH_TYPE= OSDIR=mac_arm_64`. The baseline executable hash is `f028f42715840233c2685351e6a01ca291e4090aefc48e2e33fd2d9e5965a759`; the private duplicate-target experiment hash is `cd6d7e92061f7e47c7eaa86f82cb7045b4c3e624d1764832283f00b8dca57acd`. No patch was applied to the baseline release or original saved game project.

VU tools come from [ps2dev binutils DVP](https://github.com/ps2dev/binutils-gdb/tree/3eb45ea37f0efd498d1de3cf9562de07197aefa8), branch `dvp-v2.45.1`. The build follows [ps2toolchain DVP](https://github.com/ps2dev/ps2toolchain-dvp/tree/d8aa68a0295dcc480255826b1320857278ffdfc2), including `--with-system-zlib` to avoid the old bundled zlib's macOS SDK failure. From a separate build directory:

```sh
../binutils-dvp/configure --target=dvp --disable-nls --disable-gdb \
  --disable-gdbserver --disable-gprofng --disable-sim --disable-werror \
  --disable-gprof --without-zstd --disable-shared --with-system-zlib
make -j8 all-binutils all-gas MAKEINFO=true
```

The overlay layout follows `gas/config/tc-dvp.c`: each record has a name offset, load address, and VU address. The assembler creates synthetic space for the overlay section; actual code resides at the load address. An initial attempt disassembled those zero-filled placeholders and was rejected. A later mnemonic round trip exposed 90 branch operand mismatches and 11 rounded float mismatches. Converting absolute byte targets to signed instruction displacements and formatting binary32 literals with nine significant digits removed those mismatches without raw-opcode fallback.

The broader [tool research](tools-research.md) pins Emotion Engine Reloaded, splat, m2c, decomp.me, and PS2Recomp. Firecrawl requests and responses are retained in local research scratch. Their claimed capabilities were screened and checked with Jev; partial platform support remains qualified. The old `ps2img` implementation was inspected but not run: its pointer-to-int casts are unsafe on this host, and a modern compiler rejects its implicit declarations. The bounded ROMDIR parser supplies the required extraction metadata instead.

## Judgment record and independent checks

`jev/` preserves complete root receipts with exact arguments and results. `judgment-dispositions.json` indexes their outcomes. Jev is advisory: thresholds were not lowered, and unchanged evidence was not resubmitted merely to obtain a favorable judgment. Reviews and escalations remain visible. They are not automatic approval or deterministic proof.

The layout and arithmetic judgments were checked against instruction bytes, delay slots, allocation counts, and exact corpus EOF. A proposed 64-byte final model body was corrected to 60 bytes, and a stack relocation loop was found to consume no serialized input. The two legacy header profiles remain measured corpus interpretations rather than proven loader compatibility.

The executable-count judgment flagged the total of 25 as hallucinated. Direct enumeration established 15 embedded plus nine loose IOP modules plus one EE ELF; the contradictory judgment and its separate arithmetic disposition remain retained. VU ownership and saved-export completeness received some low-confidence reviews; their current claims remain conditional and bound to deterministic packet/register or manifest evidence. Whole-game source equivalence was deliberately tested as a negative claim and remains unsupported or contradicted.

The per-file parser review and native switch patch review escalated. Independent review found and fixed missing function-entry membership and missing ELF load-map checks; targeted negative tests cover both. Another review caught the native patch's alias hazard and overly broad unique-target behavior; the narrowed private implementation passed duplicate, unique-order, mismatch, and saved-project-reopen regressions. Those tests support the bounded experiment, not generic decompiler correctness.

The existing SDK environment passed the full Python suite after the recovery changes. The system Python run failed solely because the preexisting research battery imports `typesafe_sdk`, which is installed in the existing SDK environment. The final type check includes the recovery modules and tests; two VIF command-offset initialization warnings were corrected, and the relevant tests were rerun. Final counts, logs, source identities, and exact validation outcomes are recorded in the provenance index.

Two root screen calls used an unsupported `task` argument and returned schema errors. Those failures are retained; corrected calls use `purpose`. Some bounded source excerpts were viewed before the valid screen, so the receipt history does not claim perfect screening order. The corrected SDK register screen passed; the VIF source screen requested review and was resolved by inspecting the pinned C encoding definitions as data. No external instructions were followed.

## Work remaining for full source recovery

Classify the unowned instructions and undefined spans before creating more functions. Resolve IOP runtime relocation and GP against an independent loader implementation, then connect import ordinals to API catalogs. Review control-flow and type warnings against machine code. Recover VU data contracts and renderer scheduling, model geometry and animation consumers, and the remaining UI and asset grammars. Establish a reproducible compiler/runtime target, build recovered source, and test behavior against an independent oracle. Until those steps are evidenced, the active whole-game decompilation objective remains incomplete.

[Relocation-aware IOP export recovery](../fr2-iop-relocated-exports/README.md) exposes 746 export slots, including 450 hidden by unrelocated zero pointers. Two explicit synthetic bases produce identical normalized candidate edges: 582 unique, 15 ambiguous and 151 unmatched import stubs. Independent review checks every pointer relocation and malformed/null/import controls. Exact-version matching is intentionally narrower than the pinned loader's major-version policy; runtime allocation and provider selection remain unproved.

[The corrected object-float trace](../fr2-geometry-consumer-audit/root-correction/README.md) maps serialized row offsets `8,12,16,20` to runtime offsets `12,16,20,24`. All 113,812 mapped binary32 words across 28,453 rows and 56 models are finite. The earlier four-byte mapping error and supportive Jev judgments remain explicitly superseded. Input finiteness does not identify mesh planes or prove VU outputs.
