# Read-only next-seed proposal: `001ff038` after the 3844 export

**Status:** source-only preflight for parent review. This is not a transaction guard. No Ghidra project was opened or changed, no game code was executed, and no recovery is claimed.

## Reconcile the earlier low-confidence lead

The 3844-function export still classifies `001ff038` as undefined: it has no function entry and no defined instruction. The exact prior caller remains `00200d10`, now named `candidate_ee_00200d10`; there is no baseline caller. A fresh exhaustive scan of saved function instruction words found exactly one opcode-3 JAL or opcode-2 J into undefined or unowned `.text`: the JAL at `00200dac` to `001ff038`. Its inventory bytes match the ELF at the unique mapping `.text` VA `00100000` → file offset `0x1000`, and the raw word `0c07fc0e` decodes to `001ff038`.

The prior crosswalk described the generated-comment interval `[001ff038,001ff140)` as 64 rows / 256 bytes. The byte endpoints span **264 bytes / 66 words**. The generated source has 64 rows because it omits two zero words, `001ff0a4` and `001ff0e8`. A fresh raw-word walk found five zero words in the span: `001ff084`, `001ff0a4`, `001ff0dc`, `001ff0e0`, and `001ff0e8`. All five are reachable in the structural walk. `001ff0a4` and `001ff0e8` are delay slots of ordinary conditional branches. Keep every zero word inside the inspected span; do not treat a zero as a boundary or assume a zero tail. The walk ends after the `JR RA` at `001ff138` and its nonzero delay word `27bd0060` at `001ff13c`. The following word at `001ff140` is `27bdff90`, outside the span.

## Bounded raw-word findings

The ELF slice is `[001ff038,001ff140)`, 264 bytes, SHA-256 `16d48e8843225c3e399cb0b062641b0199c6870d685c79badaf65c4c3cf8c3a1`. The structural walk reached 66/66 words. It found 55 linear instructions, five ordinary conditional branches, five direct JALs, and one `JR RA`. It found no recognized explicit trap, computed transfer, unsupported branch encoding, out-of-span edge, or unreachable nonzero word. There are no branch-likely instructions, so likely-branch annul behavior does not affect this candidate; the recorder/analysis should still state the union semantics if any appear in a later candidate.

The five outgoing JAL targets are `001ff270`, `001ffd70`, `001feb80`, `001fdb88`, and `001fc4e0`. In the current inventory only `001ffd70` and `001fc4e0` have saved function entries. The other three are unresolved from this export, so even a future guarded static candidate would not make this region call-closed. This is a material limitation and a reason to avoid any behavior claim.

Every byte in the 264-byte maximum span is currently Ghidra-undefined; there is no defined-unowned instruction range in it. The full saved-reference scan into the span finds only the entry JAL at `00200dac`; it finds no saved reference to an interior byte. The source-comment extent is only a maximum-window clue. It is not proof of original function identity or boundaries.

## Jev record

The initial `jev_decide` call failed argument validation (candidate IDs must begin with a lowercase letter; requirements maximum is three). It is preserved at `jev-decision.json`, SHA `f79be6ccb9730194d485cdabea28a920b4bdc6858e8a3adcefd908dc1b3b6749`. The corrected single call is `jev-decision-attempt02.json`, SHA `74aca112c5a6326fe1eaca3b160872c2db6a5fd9671d22c18b330e8a492b2595`: it weakly selected a source-only candidate proposal at 0.53 versus gather-more at 0.45, recommendation confidence 0.41. All three stated guardrail requirements were supported. This is advisory and not a decision to mutate a project.

The initial bounded claim check is preserved at `jev-verify.json`, SHA `c2628b7a016d255d05a9b16474e8aa4c3cd0fd7ebacf422e19fa1d9831225e67`. After completing explicit trap-field decoding and documenting all five zero words, a material evidence refresh was checked once at `jev-verify-updated.json`, SHA `a6385707c8f02689c713047a212f98f488e68d35f286ecd6765701ace0d1a92c`; it returned 3 verified, 0 contradicted, 0 unsupported, and no review flags. These judgments check only the bounded claims against the supplied static records.

## Pins and limits

- ELF: `games/ford-racing-2/extracted/SLES_517.05`, SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`.
- 3844 inventory: `.scratch/mesh/codex-audit/ee-00200e70-candidate-01/export-3844/inventory.json`, SHA-256 `b23698a1e4e6bfb61f7d4ca9932b80971f1eb4527f57bb5219d14196586c4a9d`.
- 3844 coverage: `.../export-3844/coverage.json`, SHA-256 `2ff0ed89839dc6e4e26f7c8b93f1df7ee111f3c1205385e8c52f2640f13df1f0`.
- PS2Recomp candidate comment source: `.scratch/mesh/codex-root/recomp-fpu-01/sub_001FF038_0x1ff038.cpp`, SHA-256 `1cae029129c7b9f92ebe33c79db60fa37e7c919edc7732b7819663240aa5dc37` (used only as the earlier maximum-window lead).
- 3844 decompilation manifest: `.../export-3844/decompilation/manifest.json`, SHA-256 `1e3f425e7c1a653183a284a240b28f6ff2b2918250b1e1882b0dade4cf9c4ef4`.
- Scan code/result: `scan.py` SHA-256 `9e543def4cabc1af9d544973e002d4d295f82a457ad146979f170722ba001e60`; `scan-result.json` SHA-256 `27b0ba0d8e3ee73851f420586a355b6b5241bf2d661389940dac80068b53c6ec`.
- Raw CFG code/result: `cfg_001ff038.py` SHA-256 `795363768add8e2b3633e2c01bb2a424d16c77660e59270690efe8a187d3d0e9`; `cfg-001ff038.json` SHA-256 `9c67b8a475331829f26a551fae1290f02fc001e79b937914f01422689d6c1146`.

These measurements support only a read-only candidate for parent review. They do not establish function identity, exact boundaries, semantics, runtime reachability, successful execution, or whole-game completeness. The sole incoming caller is provisional and three outgoing call destinations remain unresolved in the 3844 inventory.
