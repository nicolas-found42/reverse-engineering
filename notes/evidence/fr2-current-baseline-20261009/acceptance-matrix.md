# Current PAL SLES-517.05 acceptance matrix

Measured clean source `05a685a35ae429aaddacce1a7faceb6b6438ab44`; aggregate `A0` exits 2/incomplete.

Each row names its exact commands and receipt IDs below; full argv, SHA-256, requirement text and dependencies are in [acceptance-matrix.json](acceptance-matrix.json). A0 is fresh at this source; historical and structural reports do not supply fresh credit.

| Criterion | Observed status | Commands / receipts | Missing prerequisite | Falsifier | Linked tickets |
| --- | --- | --- | --- | --- | --- |
| AC01 — Identity and inventory. | pass | A0, C00, C01 | None for this bounded criterion | An altered/missing EE, IOP, VU, archive or extracted identity must fail or be incomplete. | [#5](https://github.com/nicolas-found42/reverse-engineering/issues/5) |
| AC02 — Aggregate result contract. | incomplete | A0 | Full passing reconstruction and handoff remain unimplemented. | A child exit/result/report mismatch, omitted AC or overwritten receipt must prevent acceptance. | [#33](https://github.com/nicolas-found42/reverse-engineering/issues/33) |
| AC03 — Non-steerable scope. | incomplete | A0 | Full build/receipt negative controls remain unimplemented. | A scope/skip/denominator override, stale receipt or omitted required input must never yield pass. | [#33](https://github.com/nicolas-found42/reverse-engineering/issues/33) |
| AC04 — Complete attribution. | incomplete | A0, C00 | Load-image inventory retained; all but the locally measured range remain unresolved. | An overlap, omitted load byte or contradictory game/SDK boundary invalidates the partition. | [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23), [#16](https://github.com/nicolas-found42/reverse-engineering/issues/16) |
| AC05 — Compiler probe. | incomplete | A0, C04 | Exploratory candidate comparison retained; independent ownership and additional EE/IOP distinguishing probes are still required. | A distinguishing source unit mismatch, ambiguous candidates or package/source identity drift invalidates the pin. | [#8](https://github.com/nicolas-found42/reverse-engineering/issues/8), [#21](https://github.com/nicolas-found42/reverse-engineering/issues/21) |
| AC06 — Linker and layout. | incomplete | A0, C08 | Fresh GNU accessor/cell placement, relocation and load-layout checks retained; full EE/IOP layout remains incomplete. | A shifted address, changed relocation target, wrong initialized data or NOBITS placement fails. | [#9](https://github.com/nicolas-found42/reverse-engineering/issues/9) |
| AC07 — First matching reconstruction. | pass | A0, C00, C04 | None for this bounded criterion | Changed accessor source or diagnostic placement must fail the 60-byte comparison. | [#11](https://github.com/nicolas-found42/reverse-engineering/issues/11) |
| AC08 — Full EE matching. | incomplete | A0, C05, C06, C10 | Fresh misc3d code/cell checks retained; full EE ownership, source and ABI/consumer coverage remain incomplete. | Any required missing unit or one changed attributed rebuilt EE word prevents full matching. | [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23), [#24](https://github.com/nicolas-found42/reverse-engineering/issues/24), [#35](https://github.com/nicolas-found42/reverse-engineering/issues/35), [#37](https://github.com/nicolas-found42/reverse-engineering/issues/37) |
| AC09 — Source integrity and interfaces. | incomplete | A0, C05, C06, C10 | Fresh misc3d code/cell checks retained; full EE ownership, source and ABI/consumer coverage remain incomplete. | A wrong caller signature, writer/alias, storage class or unresolved required ABI prevents acceptance. | [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23), [#24](https://github.com/nicolas-found42/reverse-engineering/issues/24), [#35](https://github.com/nicolas-found42/reverse-engineering/issues/35), [#37](https://github.com/nicolas-found42/reverse-engineering/issues/37) |
| AC10 — Discovery reconciliation. | incomplete | A0 | Reconcile every required unlisted span and computed dispatch. | A required unlisted span or computed dispatch target remains unaccounted for. | [#25](https://github.com/nicolas-found42/reverse-engineering/issues/25) |
| AC11 — Substitute outputs. | incomplete | A0 | Build pinned permitted substitutes with documented interfaces. | An undeclared/proprietary dependency, missing interface or substitute counted as matched prevents acceptance. | [#12](https://github.com/nicolas-found42/reverse-engineering/issues/12) |
| AC12 — Complete build. | incomplete | A0 | Clean source builds must produce EE and all 24 module outputs. | One missing EE/IOP output or source/build provenance binding prevents complete build. | [#32](https://github.com/nicolas-found42/reverse-engineering/issues/32) |
| AC13 — IOP matching. | incomplete | A0 | Attribute and rebuild all game-owned IOP ranges. | One missing attributed IOP range or altered rebuilt word prevents matching. | [#16](https://github.com/nicolas-found42/reverse-engineering/issues/16) |
| AC14 — IOP linking contracts. | incomplete | A0, C09 | Fresh all-module SIF table/candidate inventory retained; full module linking and provider contracts remain incomplete. | Wrong ordinal/version/provider/relocation or missing binding prevents contract acceptance. | [#16](https://github.com/nicolas-found42/reverse-engineering/issues/16), [#26](https://github.com/nicolas-found42/reverse-engineering/issues/26) |
| AC15 — EE/IOP handoffs. | incomplete | A0, C07, C09 | Fresh STREAM static binding retained; complete handoff ownership, synchronization, replies and other services remain incomplete. | Missing service/caller/handler, changed packet/state or unresolved ownership/lifetime prevents acceptance. | [#26](https://github.com/nicolas-found42/reverse-engineering/issues/26) |
| AC16 — VU encoding. | pass | A0, C00, C02 | None for this bounded criterion | One altered VU word or missing overlay must fail the exact encoding gate. | [#13](https://github.com/nicolas-found42/reverse-engineering/issues/13) |
| AC17 — VU entry and state maps. | incomplete | A0, C02 | Required entry/state interfaces remain unresolved. | A missing caller, overlay, entry or required VIF/DMA/TOP/mode/buffer state keeps the map incomplete. | [#13](https://github.com/nicolas-found42/reverse-engineering/issues/13) |
| AC18 — Archive completeness. | pass | A0, C01 | None for this bounded criterion | A missing extracted file, corrupt wrapper, overlap, short span or stale manifest must fail. | [#15](https://github.com/nicolas-found42/reverse-engineering/issues/15) |
| AC19 — Audio contracts. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | An unsupported bank/stream variant or wrong sample/rate/interleave/loop consumer keeps incomplete. | [#27](https://github.com/nicolas-found42/reverse-engineering/issues/27) |
| AC20 — PTG contracts. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | An unsupported body/tile/palette or wrong uppercase R/N profile prevents acceptance. | [#28](https://github.com/nicolas-found42/reverse-engineering/issues/28) |
| AC21 — Models and geometry. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | Malformed geometry counts/endpoints/strides or missing transfer/VU handoff prevents acceptance. | [#30](https://github.com/nicolas-found42/reverse-engineering/issues/30) |
| AC22 — Texture coverage. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | Wrong indices/dimensions/planes/upload sizes or missing mip/small-image variant prevents acceptance. | [#29](https://github.com/nicolas-found42/reverse-engineering/issues/29) |
| AC23 — Remaining asset grammars. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | Any archive file lacks a supported grammar or evidenced opaque consumer disposition. | [#31](https://github.com/nicolas-found42/reverse-engineering/issues/31) |
| AC24 — Contract evidence. | incomplete | A0, C01, C03 | Archive-derived contract catalog retained; required body/consumer/state semantics have not been proven by documentation coverage. | Changed consumer hash/profile, silent/contradictory evidence or required state omission cannot pass. | [#15](https://github.com/nicolas-found42/reverse-engineering/issues/15), [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23), [#26](https://github.com/nicolas-found42/reverse-engineering/issues/26) |
| AC25 — Headless oracle interface. | incomplete | A0 | Prove a bounded windowless/audio-free/focus-free lifecycle. | A UI/display/audio/focus-capable configuration must be refused before guest launch; failed cleanup prevents pass. | [#22](https://github.com/nicolas-found42/reverse-engineering/issues/22), [#14](https://github.com/nicolas-found42/reverse-engineering/issues/14) |
| AC26 — Behavioral observations. | incomplete | A0 | Compare original and rebuilt observations with identical inputs. | Mismatching scenario inputs/output/state or absent original/rebuilt observations prevents behavioral acceptance. | [#14](https://github.com/nicolas-found42/reverse-engineering/issues/14) |
| AC27 — Falsifiable gates. | incomplete | A0, C00, C04 | The current positive, mutation and placement controls cover one source unit only; controls for remaining acceptance gates are not complete. | A required mutation passes, or missing/malformed/no-match semantic evidence is accepted. | [#33](https://github.com/nicolas-found42/reverse-engineering/issues/33) |
| AC28 — Reproducibility. | incomplete | A0 | Compare two clean source builds in separate fresh work directories. | Credited outputs or normalized aggregate reports differ between two fresh separate builds. | [#34](https://github.com/nicolas-found42/reverse-engineering/issues/34) |
| AC29 — Honest progress ledger. | incomplete | A0, C00, C04 | The current partition conserves all load-image bytes, but only one 60-byte owned range is attributed and matched. | A zero/steered denominator, missing byte or discovery/substitute byte counted as matched prevents complete ledger. | [#23](https://github.com/nicolas-found42/reverse-engineering/issues/23), [#16](https://github.com/nicolas-found42/reverse-engineering/issues/16) |
| AC30 — Evidence and unresolved list. | incomplete | A0, C00, C01, C02, C03, C04, C05, C06, C07, C08, C09, C10 | These current child receipts support the bounded results above; required evidence and falsifiers for the remaining criteria are still incomplete. | A required claim lacks current reproducible evidence/disposition/falsifier or an escalation is overwritten. | [#33](https://github.com/nicolas-found42/reverse-engineering/issues/33) |
| AC31 — Public artifacts and licensing. | incomplete | A0, C04 | The exploratory compiler receipt records package provenance; redistribution terms remain unresolved and no compiler binaries are redistributed. | Tracked retail/generated/proprietary payload or unresolved required license/source binding prevents acceptance. | [#21](https://github.com/nicolas-found42/reverse-engineering/issues/21), [#22](https://github.com/nicolas-found42/reverse-engineering/issues/22) |
| AC32 — Final handoff. | incomplete | A0, C00, C01, C02, C03, C04, C05, C06, C07, C08, C09, C10 | Current child receipts and the aggregate are retained, but required final acceptance and handoff evidence remains incomplete. | Any required reconstruction criterion remains fail/incomplete or final ticket/map receipt is missing. | [#34](https://github.com/nicolas-found42/reverse-engineering/issues/34), [#5](https://github.com/nicolas-found42/reverse-engineering/issues/5) |

## Exact commands and receipt identities

### A0 — incomplete

Receipt `20261009T152126Z-718499d4bc88455280610996082435eb`; SHA-256 `45d1186f03ca0fd3dbda4baa3f2ead84fe5ed12d06d2a065eabefe4da8ea2e5d`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/completion.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate
```

### C00 — pass

Receipt `20261009T152126Z-c95f736589d44a6fb9e95fd3474db546`; SHA-256 `1f6928f7e6d9ab4e9b0a41e2a0068f73ddeb47cc883da641636965062cffd95e`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/matching_ranges.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/ranges
```

### C01 — pass

Receipt `20261009T152127Z-6a650f1953a84586a5b274f1598bf980`; SHA-256 `6d9b7671ebd7f020f53f5c4d8a4ac830469146a1134a92a5ff8a04c951a3b275`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/verify_formats.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/archive
```

### C02 — incomplete

Receipt `20261009T152129Z-8c0e315b74ca481481d29ee15f76a960`; SHA-256 `3b5248736296001b712d10d5ac944d946f31c2c4a978a3676a84e1c7c6e2b173`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/verify_vu.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/vu
```

### C03 — incomplete

Receipt `20261009T152129Z-6269624029164e3d8cf919e51071831b`; SHA-256 `8ef3cd8e00f7fdc846275b9f6b4b24817dc8f970334889f5b6f9cd14cbfbafd4`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/verify_asset_contracts.py archive /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.HDR /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.DAT --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/assets
```

### C04 — pass

Receipt `20261009T152132Z-853710317ed3414fabfb758bfa64070c`; SHA-256 `ace04f76001e6691cec03388f9cdd5d1c04c74bf8c518793815be5ebc0a47bc9`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/compiler_probe_recipe/run.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/compiler
```

### C05 — pass

Receipt `20261009T152224Z-2c586ca82ca94930a01760bc8cfd6888`; SHA-256 `a20ab80d9416d383d389ffc81df938a61bcc5bef8792a80fe09bb12f016fd0ff`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/misc3d_contract.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/misc3d_cell
```

### C06 — pass

Receipt `20261009T152228Z-1870e4be2a3049c1856a3807be6d0470`; SHA-256 `ec265b839a09b62248ab95383729b6cd6929659e85c903949e46e611ce822b63`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/misc3d_lifecycle.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/misc3d_lifecycle
```

### C07 — incomplete

Receipt `20261009T152239Z-791808e7466b4e1d96eec44dcd3450ea`; SHA-256 `27f6cc1071147f1f351dd02e8e079c2f40eb9870ccb41416f27a91b37cf13f68`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/check_rpc_contracts.py --ee /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --stream /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/IRX/STREAM.IRX --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/rpc
```

### C08 — pass

Receipt `20261009T152239Z-0651bce38fc74796a4b68f6e291cb679`; SHA-256 `b45b05671883fb589fc2408821c0981450c824b56e6dc09c1456cd8659e5d097`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/linker_layout.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/layout
```

### C09 — incomplete

Receipt `20261009T152244Z-0c5d7ddc4bb0498f95415d6ab4d19f8e`; SHA-256 `a2f95beb0ae7bdca672399e95fe054c3964be4a89dfac299568c9bb4641a457d`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/inventory_rpc_handoffs.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/rpc_inventory
```

### C10 — pass

Receipt `20261009T152244Z-de1b309484d54902b0c7b5e8b56af750`; SHA-256 `80c361b6681f682372be7bb9046bb8335c4f22fd6890e77c397106d6fce294a7`.

Working directory: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean`.

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/clean/tools/misc3d_loader_recipe/source_build.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-20261009/aggregate/children-e1e542cf3b2642ca9247389ff1d90b79/misc3d_terminal
```

