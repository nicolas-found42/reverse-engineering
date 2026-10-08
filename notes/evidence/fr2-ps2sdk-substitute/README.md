# ps2sdk source build as an SDK substitute

This evidence records a real build of the permitted open-source ps2sdk source.
It establishes a buildable substitute interface; it does **not** attribute any
retail address range to the SDK and supplies no matching credit.

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
