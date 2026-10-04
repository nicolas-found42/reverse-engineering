# PS2 decompilation tool research

Research date: 2026-10-04. This is tool selection evidence for a PlayStation 2 game decompilation project. Repository claims were fetched through the existing Firecrawl HTTP helper and passed through Jev screening before use. Repo-page snapshots show the default branch's latest commit at fetch time; commit links below pin the inspected revision.

## Recommendation

Use Ghidra with [Emotion Engine: Reloaded](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/tree/ae013ee1475dc970db4fdeba3ec88def6b933d43) as the primary broad static analysis/decompilation environment. The repository describes PS2 EE support, EE-specific MMI and VU0 macro disassembly/decompilation, STABS recovery for functions/types/globals, and PCSX2 save-state import. It also documents function decompilation failures and a suggested analyzer setting. Validate the actual game ELF, Ghidra version, opcodes, and recovered function coverage locally before treating output as complete.

Pair that with [splat](https://github.com/ethteck/splat/tree/1d09139b886f0bece632bd8f367ccc1d3318ca2a) for executable segmentation/configuration and generated assembly, if its PS2 segment model fits this binary. Splat explicitly lists PS2 among supported platforms and uses the MIPS dependency for PS2. It is a project organizer/splitter and disassembly workflow, not a C decompiler.

Use [decomp.me](https://github.com/decompme/decomp.me/tree/4ab701a379c15e039246c4b9204081c851bf29ea) and its separately versioned [compiler catalog](https://github.com/decompme/compilers/tree/bf4f879ea19fabdd97598bb6c9956eb8bc618aaa) for individual source-matching tasks. The compiler catalog contains both EE GCC and MWCC PS2 entries (including many MWCCPS2 builds), so this is a real PS2 option. Pick the matching compiler build and flags from the game's own evidence; a successful match proves an assembly match under those settings, not that the candidate is the original source. It does not discover missing code or provide full-program decompilation.

Try [m2c](https://github.com/matt-kempster/m2c/tree/708d2d2cb2698f091a92492b328f73b24209f72d) as an optional comparison on ordinary MIPS functions. It supports several MIPS ABI/targets (including MIPSEE EABI64) and emits C from assembler, but the reviewed README does not establish complete R5900/EE MMI coverage or game-toolchain equivalence. Treat unusual EE instructions and output quality as needing manual validation.

Keep [PS2Recomp](https://github.com/ran-j/PS2Recomp/tree/c5a9d02573410a2085a4b4b831b0b68ba3515440) as a separate experimental execution/recompilation track, not a source-recovery oracle. It decodes PS2/R5900-specific instructions and emits C++ for a runtime, but its README describes incomplete hardware emulation/stubs. It is GPL-3.0; review that license before incorporating code into a project with a different distribution model.

Do not choose [decomp-toolkit](https://github.com/encounter/decomp-toolkit/tree/0645e16511814920ffb05b25615dd71f1af73e4c) for PS2-specific work: it is explicitly a GameCube/Wii toolkit (MIT OR Apache-2.0). The old [ghidra_MIPSR5900](https://github.com/astrelsky/ghidra_MIPSR5900) repository is archived/deprecated and points users toward Emotion Engine: Reloaded.

These tools can materially increase machine-code coverage and help match reconstructed C to selected functions. They cannot alone establish that every module/overlay was found, every function was correctly identified, all EE/VU code is represented, or that pseudocode is faithful original source. A defensible completion claim needs an inventory of all game executables/modules, function-by-function statuses, explicit unclassified executable ranges, unresolved instructions, data/code boundary review, and separate behavioral validation.

## Candidates and inspected revisions

| Tool | License | Revision seen | Role and evidence-based fit |
| --- | --- | --- | --- |
| Ghidra Emotion Engine: Reloaded | Apache-2.0 | ae013ee1475dc970db4fdeba3ec88def6b933d43 | Best direct PS2 EE analysis/decompilation fit. README says it covers MMI/VU0 macro, STABS metadata, and save states; also warns some functions fail to decompile. |
| splat | MIT | 1d09139b886f0bece632bd8f367ccc1d3318ca2a | Binary splitting/configuration and disassembly workflow; PS2 listed, MIPS dependency required. |
| decomp.me | MIT | 4ab701a379c15e039246c4b9204081c851bf29ea | Collaborative function-matching workflow. |
| decomp.me compilers | README page points to bf4f879ea19fabdd97598bb6c9956eb8bc618aaa | bf4f879ea19fabdd97598bb6c9956eb8bc618aaa | Catalog values.yaml lists EE GCC and MWCC PS2 compiler ids; separate repo and license details should be checked for any redistribution of compiler binaries. |
| m2c | GPL-3.0 | 708d2d2cb2698f091a92492b328f73b24209f72d | Potential comparison decompiler for normal MIPS; exact R5900/MMI behavior unresolved. |
| PS2Recomp | GPL-3.0 | c5a9d02573410a2085a4b4b831b0b68ba3515440 | Experimental static recompiler/runtime. Not source recovery; incomplete emulation and integration scope matter. |
| decomp-toolkit | MIT OR Apache-2.0 | 0645e16511814920ffb05b25615dd71f1af73e4c | GameCube/Wii toolkit; no direct PS2 fit. |

## Jev dispositions

Fetched GitHub search snippets, repo pages, and decomp.me compiler-catalog page were screened before relying on them. Existing exact screen inputs/results are retained in jev-tools_research_*.json; the full Firecrawl request/response snapshots are in the sibling *-search.json and *-scrape.json files. The additional raw values.yaml page screen is jev-compilers-values-screen.json; result: **pass**, injection 0.04, substance 0.98, relevance 0.97. The screened YAML includes the PS2 compiler ids.

Jev rerank (jev-tool-rerank.json) ranked Emotion Engine: Reloaded first (0.94), then PS2Recomp (0.80), m2c (0.79), decomp.me (0.75), splat (0.67), old Ghidra plugin (0.57), and decomp-toolkit (0.09). This is an ordering signal, not an independent proof of each capability.

Jev classify (jev-tool-classify.json) auto-labeled splat as binary-split/disassembly, decomp-toolkit as other platform, decomp.me as function matching, Emotion Engine: Reloaded as direct PS2 decompiler, PS2Recomp as recompiler, and old plugin as obsolete/superseded. m2c was **review** (other-platform probability 0.73, direct-PS2-decompiler 0.19; confidence 0.67), so its exact target fit stays a manual caveat.

Jev verified the primary tool fit claims in jev-research-claim-verify.json. Six claims auto-passed with confidence 0.98–1.00; the m2c caveat was verified at 0.77 and remains manual review, consistent with the conservative wording.

## Exporter review

Read-only review target: tools/ghidra/ExportDecompilation.java. The existing claim-limit string correctly calls outputs generated pseudocode and says it does not prove original source recovery, type correctness, complete code discovery, recompilability, or behavior equivalence. The scope says all saved functions of the loaded Ghidra program; it must not be presented as all code in the game unless every executable and module/overlay was loaded and inventoried.

Material manifest issue: status and missing_selected_entries are set only after a normal loop exit, while the finally block writes the manifest even after cancellation or an exception. Seed status: incomplete before the try, record an explicit termination reason, calculate missing selected entries in finally, and only upgrade to generated after normal completion with no failed/missing rows. Jev verification of the cancellation/open-program claim was auto-supported (0.89 support, 0.84 confidence); the other four code assertions were judged verified but three remained in review below the 0.8 confidence threshold. Raw call receipts: jev-exporter-review.json, jev-exporter-verify.json. Jev review returned **escalate** (safe_to_apply 0.24; correctness confidence 0.26; blast-radius confidence 0), so do not describe this as a Jev-approved implementation.

Additional hardening: selected addresses are accepted as untrimmed exact strings, so normalize or report invalid tokens; stage each C file and atomically move it after a successful write, or delete partial output on exception. Per-function exception capture and no-overwrite output creation are sensible current behavior.

## Firecrawl evidence files

All fetched request arguments and response bodies are saved under this directory. The current Firecrawl client was .scratch/mesh/codex-root/firecrawl_fetch.py; it uses the configured credential without printing it. Key snapshots: ee-reloaded-scrape.json, splat-scrape.json, m2c-scrape.json, decompme-scrape.json, compilers-scrape.json, compilers-values.json, ps2recomp-scrape.json, and decomp-toolkit-scrape.json. Search result and args files are kept alongside them for provenance.
