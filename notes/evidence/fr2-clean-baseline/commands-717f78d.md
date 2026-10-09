# Exact commands and receipt identities

All commands ran in clean detached checkout of `717f78df689be4e16ddc891b2def18cbda3ce79d`. Corpus/tool inputs are existing local files, not included in the checkout or publication. Use a fresh output directory to reproduce; do not overwrite the original receipts.

## A0 — incomplete

```sh
python3 tools/completion.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --compiler-tools /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/20261009T024336Z-912656da77d443829c8376b5200febdf/result.json`
SHA-256: `2aab9ae17f36311f6a91543b53efb673aa52955ddcc23e5385dbe6d26db5fdfb`

## C00 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/matching_ranges.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/ranges
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/ranges/20261009T024336Z-dbca1d0264664ba48e4e46b1745361ce/result.json`
SHA-256: `8feee4fdfe662c6aa2bdcb9c152f571af206c682b90cb032bbadf32bd7d7cda2`

## C01 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/verify_formats.py corpus /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/archive
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/archive/20261009T024337Z-bf9c848522c748d385416dbac96d7146/result.json`
SHA-256: `1a3260632e17b8ee729b3d9829a0336682febb39d3206029ff859ee64a4a07d8`

## C02 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/verify_vu.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --assembler /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/gas/as-new --objdump /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/mesh/codex-root/binutils-dvp-build/binutils/objdump --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/vu
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/vu/20261009T024339Z-d8b5ce850d674e29b778f8996c9b222d/result.json`
SHA-256: `d4391cfdb94b11c7d208cc2526c69f1e0d0f0c784f4bd757b8b661e1e1feaf85`

## C03 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/verify_asset_contracts.py archive /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.HDR /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/FILES.DAT --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/assets
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/assets/20261009T024339Z-0d113eb789c4490a84ed58c5ae4d3580/result.json`
SHA-256: `dd59f79854833c79e2de1838975b2b051674948d7cacb2666e14c85f20842fab`

## C04 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/compiler_probe_recipe/run.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/compiler
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/compiler/20261009T024341Z-6b5c98927c4346ad9eee08eed85dd79e/result.json`
SHA-256: `2b53b35fd263a9ddcd46f27e602546538931aeee4f6e0a308884557850adb96e`

## C05 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/misc3d_contract.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_cell
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_cell/20261009T024414Z-197b72910d9b4d6e999770cb6353c429/result.json`
SHA-256: `60cc5e32664d222cb28797cf601cf98a8bb927f50a82b18cb272795e8e91b7a4`

## C06 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/misc3d_lifecycle.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_lifecycle
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_lifecycle/20261009T024416Z-63e953a1949b45ada12822e4c35dce0d/result.json`
SHA-256: `7d780e9e22227a51fac0ea0d81c0c28b1b3367723e29009d0c5dcad94d6f1683`

## C07 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/check_rpc_contracts.py --ee /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 --stream /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/IRX/STREAM.IRX --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/rpc
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/rpc/20261009T024422Z-99a3427830e14e4abe2fdcdb5da18903/result.json`
SHA-256: `ad977ee7024ac558a1b3f5e910b70fb1c64a8395c3c8b93529c217eaefc3dfd9`

## C08 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/linker_layout.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/layout
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/layout/20261009T024422Z-8e1cfb3abaa34d23ae1446f2c7aa4270/result.json`
SHA-256: `cf22d5b8b9e7e4873ce81d302b96b690c58c0aadda0cdac504145fc9200a8409`

## C09 — incomplete

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/inventory_rpc_handoffs.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/rpc_inventory
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/rpc_inventory/20261009T024425Z-6a2f5d6375154052ae8b223fd4cde05f/result.json`
SHA-256: `2bd681a6afb005797dbe14901cf5b8746c0b89ec3c33c127e85c99b9e38f63f9`

## C10 — pass

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/clean/tools/misc3d_loader_recipe/source_build.py /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2 /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers --output /Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_terminal
```

Receipt: `/Users/Nicolas/Documents/github/hermes/reverse-engineering/.scratch/baseline-2026-10-08/aggregate/children-d04ebede20684192ace0526dc43b0eed/misc3d_terminal/20261009T024425Z-dfc51e9fb2cc4801ae4cfecb3f66d59e/result.json`
SHA-256: `d471565f569bd3bb14942fadbeaf4bbb48f943120a7930c50c4a8ccf9e90e9a6`
