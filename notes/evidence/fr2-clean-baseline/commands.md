# Exact commands and receipt identities (merged revision `d14fe24278ad66a479ccd4d70ede7150a5521fef`)

All commands ran in a clean detached checkout of `d14fe24278ad66a479ccd4d70ede7150a5521fef`. Corpus/tool inputs are existing local files, not included in the checkout or publication. Use a fresh output directory to reproduce; do not overwrite the original receipts. The pre-merge snapshot command set is retained in commands-717f78d.md.

## A0 — incomplete

```sh
python3 tools/completion.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/20261009T031130Z-c255981757964f84a88b184cded1dd7f/result.json`
SHA-256: `ebb63100132f995d4fa34c53fb08780a6a868f07c3159c679f1c2b9224b2cda7`

## C00 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/matching_ranges.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/ranges
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/ranges/20261009T031130Z-d36b4adf12b14d96b1896c68e1af13aa/result.json`
SHA-256: `aaaf1f3751fd66816161a1b297419944d9055bde525f23274beb99ec2b53b12d`

## C01 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/verify_formats.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/archive
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/archive/20261009T031131Z-0051657b822f4ba59481108608f8ec5b/result.json`
SHA-256: `9b27da7598232a95f8de38d49eb078a7e249470da71cc0ee13ec27166f0ecb63`

## C02 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/verify_vu.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/vu
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/vu/20261009T031132Z-8d26b268500740eda5d4707df590f4b3/result.json`
SHA-256: `9fd7ae82888f00f6d399085a27d977835b782a2f03ce40ad0f2685793b75ce34`

## C03 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/verify_asset_contracts.py archive /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.HDR /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.DAT --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/assets
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/assets/20261009T031132Z-6876bfbf3232452bbb360f1e4e0a185c/result.json`
SHA-256: `58e8d6367d0d12e04ff250fcefee948406cc3b66645fab6aed20c86d8675efc1`

## C04 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/compiler_probe_recipe/run.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/compiler
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/compiler/20261009T031134Z-bb1453700c914230bf511b60b38badb1/result.json`
SHA-256: `79a462229687cde5864bba62add52b58d3597ecc6cf17136e13b291c0d457492`

## C05 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/misc3d_contract.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_cell
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_cell/20261009T031203Z-649e8a29307d4ceeb774f6fcb584e5ab/result.json`
SHA-256: `f2b685bb2a1a02e8b77e2b509f4d3160cce516bc33d54ffd0934476acd820417`

## C06 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/misc3d_lifecycle.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_lifecycle
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_lifecycle/20261009T031205Z-4b1309edfb55494a81e0a1695ae34aa6/result.json`
SHA-256: `acad7a42ebf557c7355e36691450e6c220a2122fb987a908e027562996f45f24`

## C07 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/check_rpc_contracts.py --ee /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --stream /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/IRX/STREAM.IRX --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/rpc
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/rpc/20261009T031210Z-040519e7f33a4c3b8df4101de881371b/result.json`
SHA-256: `0c116b500b0e289f47f4365d76137e69486cb044cacd35f56c3404034359177d`

## C08 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/linker_layout.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/layout
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/layout/20261009T031210Z-15458544edfd41dc9ad9b84bf529db8e/result.json`
SHA-256: `92e214af585c6ed44d96207a09521fc75560181c4cca520f36b5c30c6080e20f`

## C09 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/inventory_rpc_handoffs.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/rpc_inventory
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/rpc_inventory/20261009T031213Z-71a760efa2db4297ad9c6a36af408aa6/result.json`
SHA-256: `bde305de84cae2486bf94bd5d1635efd57909eec2bb2676028680257d4a1a581`

## C10 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean-merged/tools/misc3d_loader_recipe/source_build.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_terminal
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/merged-aggregate2/children-2dbd9f6171da4f5a9ace57c86c99e82c/misc3d_terminal/20261009T031213Z-f1effaf35f1249a18fccb51f1983de02/result.json`
SHA-256: `011c979467d0155bf6364a6b49a598b615eaebfe32776cd99937899c00038e11`
