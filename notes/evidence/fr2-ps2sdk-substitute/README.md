# ps2sdk source build as an SDK substitute

The bootstrap sections below record the historical 2026-10-08 source build and
upstream interface sample. The current consumer delivery at the end adds four
recorded substitute ranges and two actual reconstructed consumer groups. Neither
delivery supplies game-owned matching credit or completes AC11.

## Pinned inputs

- ps2sdk: [ps2dev/ps2sdk](https://github.com/ps2dev/ps2sdk) commit
  `2c670453980fcc3fe46ead6399b730b12c8556eb`, license `LICENSE` (Academic
  Free License 2.0). The upstream tree has no GitHub release tags.
- EE/IOP/DVP toolchain: official [ps2dev/ps2dev release v2.0.0](https://github.com/ps2dev/ps2dev/releases/tag/v2.0.0), asset
  `ps2dev-ubuntu-24.04-arm.tar.gz`, SHA-256
  `ed69330f235d421754196acf866f8590e5f92e8b92571f1c7e05e853900e7622`.
  This is a permitted open-source toolchain bundle, not a matching compiler.
- Build container: `ubuntu:24.04` for `linux/arm64`, resolved image digest
  `sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
- Upstream ps2sdk's external source dependencies resolved during this build:
  lwIP `77dcd25a72509eb83f72b033d219b1d40cd8eb95` and FatFs
  `18cc3d9e07473a6aa3d783a66224b243a7b4974c`. Their licenses remain with
  their respective upstream source trees.

The toolchain reports GCC 15.2.0 for both `mips64r5900el-ps2-elf-gcc` and
`mipsel-none-elf-gcc`. It is suitable for building the substitute only. The
game-matching profile remains the separately investigated era `ee-gcc`.

## Build recipe

Keep the downloaded source, toolchain archive, and all generated files outside
the repository. Set `REPO` to this checkout and `WORK` to an external scratch
directory, then run this setup to obtain the exact inputs and verify their
identity:

```sh
mkdir -p "$WORK/toolchain" "$WORK/build"
git clone --no-checkout https://github.com/ps2dev/ps2sdk.git "$WORK/ps2sdk"
git -C "$WORK/ps2sdk" checkout --detach 2c670453980fcc3fe46ead6399b730b12c8556eb
curl -L --fail --show-error \
  -o "$WORK/toolchain/ps2dev-ubuntu-24.04-arm.tar.gz" \
  https://github.com/ps2dev/ps2dev/releases/download/v2.0.0/ps2dev-ubuntu-24.04-arm.tar.gz
echo 'ed69330f235d421754196acf866f8590e5f92e8b92571f1c7e05e853900e7622  '"$WORK/toolchain/ps2dev-ubuntu-24.04-arm.tar.gz" | shasum -a 256 -c -
cp "$REPO/notes/evidence/fr2-ps2sdk-substitute/download_dependencies.pinned.sh" \
  "$WORK/ps2sdk/download_dependencies.sh"
```

Run the clean source build and the linked interface sample inside the observed
Ubuntu ARM64 image. The source, dependencies, and build outputs stay mounted at
the external `WORK` path:

```sh
docker run --rm --platform linux/arm64 \
  -v "$WORK/toolchain:/toolchain:ro" \
  -v "$WORK/ps2sdk:/src" \
  -v "$WORK/build:/out" \
  -w /src \
  ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55 \
  bash -lc '
set -eux
apt-get update
apt-get install -y --no-install-recommends build-essential make perl python3 ca-certificates git
tar -xzf /toolchain/ps2dev-ubuntu-24.04-arm.tar.gz -C /opt
export PS2DEV=/opt/ps2dev
export PS2SDKSRC=/src
export PS2SDK=/out/ps2sdk
export PATH="$PS2DEV/bin:$PS2DEV/ee/bin:$PS2DEV/iop/bin:$PS2DEV/dvp/bin:$PATH"
cd /src
make clean
make -j1
test "$(git -C common/external_deps/lwip rev-parse HEAD)" = 77dcd25a72509eb83f72b033d219b1d40cd8eb95
test "$(git -C common/external_deps/fatfs rev-parse HEAD)" = 18cc3d9e07473a6aa3d783a66224b243a7b4974c
make install
python3 -c "from pathlib import Path; import sys; print('installed file count:', sum(path.is_file() for path in Path(sys.argv[1]).rglob('*')))" "$PS2SDK"
cd "$PS2SDK/samples/debug/helloworld"
make -B
'
```

The serial build is intentional: ps2sdk documents directory-level parallel
build corruption. The checked-in `download_dependencies.pinned.sh` replaces
ps2sdk's moving branch fetches with exact commits and exits if an existing
checkout differs or has tracked modifications. Do not treat these dependencies
as game-specific SDK attribution. The interface smoke source is the upstream
`ee/debug/samples/helloworld/helloworld.c`.

`make -B` forces the compile and link even when the output already exists. That
sample calls `sceSifInitRpc`, `init_scr`, `scr_printf`, and related
declared interfaces and links the SDK's debug and C runtime libraries. Retain
the resulting ELF and logs only in the external evidence directory; do not
track generated libraries, object files, or ELFs.

Reproduce the installed output counts in the receipt against the external
install after linking the sample:

```sh
python3 - "$PS2SDK" <<'PY'
from collections import Counter
from pathlib import Path
import json, sys
root = Path(sys.argv[1])
files = [path for path in root.rglob('*') if path.is_file()]
counts = Counter(path.suffix.lower() for path in files)
print(json.dumps({
    'files': len(files), 'archives': counts['.a'], 'irx': counts['.irx'],
    'headers': counts['.h'],
}, sort_keys=True))
PY
sha256sum "$PS2SDK/samples/debug/helloworld/helloworld.elf"
```

## Local build receipt

On 2026-10-08 the full clean source build completed with exit status 0. The
install contained 681 files. After separately compiling and linking the
interface sample, the external output tree contained 718 files, including 55
static archives, 211 SDK IRXs, 273 headers, and the sample object and ELF. The
smoke sample compiled and linked successfully. Its ELF SHA-256 is
`30590eb0a67a8ae5bcfb8bfaffd87738336b0a18cebbe9cef68e4192bd816386`; the ELF
remains in the external SDK evidence directory.

The sanitized machine-readable receipt is
[`build-receipt.json`](build-receipt.json). The pinned dependency fetcher in
[`download_dependencies.pinned.sh`](download_dependencies.pinned.sh) is part
of the build recipe.

The source-built archives and IRXs are substitute artifacts for this recipe.
They do not identify which retail bytes they would replace. This worktree has
no local retail corpus payload; its aggregate range child reported incomplete
for missing inputs. No substitute ranges were attributed, and the run credited
zero matched bytes. ADR-0005 still requires every available corpus load-image
range to remain unresolved until measured attribution evidence is recorded.

## Ledger and fixtures

An identical substitute fixture is reported with disposition `substitute, not
matched`; its bytes do not enter `matched_bytes` or `matched_fraction`. A
corrupted substitute remains failed and likewise earns zero matched bytes.
When no boundary decision has classified any corpus range, the range inventory
and aggregate report say `no ranges attributed as substitute`; every load-image
byte remains mixed/unresolved under ADR-0005. The source-build output count is
not a retail range count.

- Positive accounting fixture: `tools/test_matching.py`,
  `test_a_substitute_region_never_inflates_the_matched_fraction`.
- Negative accounting fixture: `tools/test_matching.py`,
  `test_a_failed_substitute_stays_out_of_the_matched_denominator`.
- Incomplete corpus fixture: `tools/test_matching_ranges.py`,
  `test_absent_image_is_incomplete_and_section_only_file_cannot_prove_load_layout`.

No game-owned bytes, actual substitute address ranges, full ELF, EE source-built
game, or 24-module game rebuild is claimed by this evidence.

## Current actual consumer delivery — 2026-10-09

The hand-written [consumer source](../../../reconstruction/ee/system/sdk_consumers.c)
reconstructs two bounded retail paths: the DMA descriptor/submission/polling
routine at `0x0011b780` and the counter/semaphore routine at `0x0020c940`.
These are source candidates with inferred names, not credited matching units.
The three file-state words retain their measured initialized values and addresses.

The [consumer contract](kernel-consumer-contract.json) binds the complete
instruction hashes, source/header/build inputs and accepted source-verification
judgments. [Original interpretation uncertainty and independent review](consumer-dispositions.json)
remain visible: the first Jev interpretation judgments were verified but required
review (support/confidence 0.66/0.49 and 0.80/0.70). Independent instruction and
caller checks resolved them, including the integer return that tail callers
propagate. [Source verification](source-verification.json) separately supports
the resulting implementation. The program checks these retained, source-bound
judgments through `judgment_contract.py`; changed evidence, invalid judgments
and missing inputs cannot silently pass. Probabilities never determine byte credit.

`kernel_substitutes.py` snapshots the pinned SDK Git source and compiles only
`kernel.S` plus the actual consumer source. It consumes neither installed SDK
objects nor retail code as build inputs. The link binds SignalSema, FlushCache,
sceSifDmaStat and sceSifSetDma at their four recorded addresses and has no
undefined symbols. Its orphan check rejects unexpected code/data inputs.
The output verifier checks each wrapper, initialized cell, consumer placement
and direct interface transfer. The [scoped build receipt](scoped-build-receipt.json)
records source, dependency, tool, command and output identities.

The build reuses the pinned archive and SDK checkout described above. Its modern
n32 ABI keeps the tested 32-bit pointer/descriptor and integer argument/return
contracts; it does not identify the retail compiler or full original ABI.
The host controls use native pointers and therefore test logic at the kernel
boundary; the cross-build separately asserts the target descriptor is 16 bytes.
The image in `tools/kernel_substitute_recipe/Dockerfile` adds exact Ubuntu MPC,
MPFR and GMP runtime versions to the pinned base. Their package copyright
notices, the SDK Academic Free License and build artifacts remain in the external
build directory, with hashes in the receipt. Dependency licenses are preserved.

Reproduce from this checkout with the existing local SDK input root:

```sh
docker build --platform linux/arm64 -t fr2-ps2sdk-kernel-runtime tools/kernel_substitute_recipe
python3 tools/kernel_substitutes.py games/ford-racing-2 \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/sdk \
  --output .scratch/issue12/reproduced-build
# Use consumer.elf from the fresh receipt's build_directory.
python3 tools/kernel_substitute_recipe/experiments.py games/ford-racing-2 \
  <build-directory>/consumer.elf --output .scratch/issue12/reproduced-controls
tools/check.sh test_kernel_substitutes test_substitute_ranges test_matching_ranges
```

The command requires the recorded immutable runtime image identity. A rebuilt
image with another identity remains unavailable until its inputs are reviewed;
the mutable tag does not select the accepted image.

[Host and real-output controls](control-receipt.json) run 90 representative
boundary cases, five source mutations, and changed/missing/shifted/uncalled
interface controls. Negative source cases include a reversed semaphore
condition, wrong cache operation, reversed DMA pointers, missing polling and
submission for a zero byte count. Nonpositive sizes make no kernel calls;
negative transaction IDs and statuses retain the measured absence of retry or
success validation. No guest hardware observation is inferred.

[Semantic controls](semantic-controls.json) retain six labeled claims: all six
verdict labels matched the independently stated expectations, but three needed
review under the fixed threshold. The one batched call used 4,105 input and 382
output tokens and took 327 ms as measured around the tool invocation. This is a
six-case diagnostic sample, not a calibrated accuracy guarantee. No reported
provider charge or Jev-1.13 price was available from the current model listing,
so billed cost remains unmeasured. Reproduce the semantic request using its
retained `request` via `node tools/jev_call.mjs --run <dir> --id <id> --tool
jev_verify --args <request.json>`; the original response is retained, not rerun
to seek a preferred outcome.

All 64 wrapper bytes are **substitute, not matched**, including their identical
retail encodings. The current load ledger retains 60 game-owned bytes and
3,506,924 unresolved bytes; reproduce with `python3 tools/matching_ranges.py
corpus games/ford-racing-2 --output <dir>`. The aggregate gains a fresh independent
substitute child and keeps AC11 incomplete; a child failure makes AC11 fail.
Run the usual completion recipe with the additional `--sdk-work` path above.
Full required EE/IOP substitute/interface coverage, whole-game builds and guest
cache/DMA/semaphore behavior remain unresolved. Issue #12 stays open.

Independent spec review found that call-target checks alone allowed consumer instructions to be removed. The final verifier pins both entire consumer section hashes from the fixed permitted recipe; the additional mutation preserves every J/JAL target while removing other instructions and is rejected. These pins establish substitute build integrity, not original game matching.
