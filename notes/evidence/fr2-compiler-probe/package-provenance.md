# Compiler package provenance disposition

AC31 remains incomplete for the exact EE compiler packages. Their public
availability, version strings, and matching output do not supply a
package-specific source or redistribution disposition. Archives and extracted
executables remain local. This is an evidence gap, not a finding that the
compiler is proprietary or unlawfully distributed.

The fixed recipe in `tools/compiler_probe_recipe/build.py` declares each
release archive URL and SHA-256. The local hashes matched those declarations.
The archive member-name inspection found no `COPYING`, `LICENSE`, `LICENCE`,
`COPYRIGHT`, or `README` basename. Reproduce those observations without
extracting or publishing a compiler:

```sh
PYTHONPATH=tools/compiler_probe_recipe python3 - <<'PY'
import hashlib, json, tarfile
from pathlib import Path
from build import DISTRIBUTIONS
root = Path('/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers')
names = {'copying', 'license', 'licence', 'copyright', 'readme'}
for candidate, (name, expected) in DISTRIBUTIONS.items():
    path = root / name
    with tarfile.open(path) as archive:
        notices = [member.name for member in archive
                   if Path(member.name).name.casefold() in names]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({'candidate': candidate, 'archive': name,
                      'sha256': actual, 'matches_pin': actual == expected,
                      'notice_members': notices}))
PY
```

The candidate that matches the first hand-written unit identifies itself as
`2.96-ee-001003-1`. Reproduce its version observation through the pinned
runtime wrapper:

```sh
/bin/bash tools/compiler_probe_recipe/docker-linux-exec.sh \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc \
  --version
```

The immutable [decompme package recipe](https://github.com/decompme/compilers/blob/bf4f879ea19fabdd97598bb6c9956eb8bc618aaa/platforms/ps2/ee-gcc2.96/Dockerfile#L233-L243)
downloads and extracts the archive. Its [configuration entry](https://github.com/decompme/compilers/blob/bf4f879ea19fabdd97598bb6c9956eb8bc618aaa/values.yaml#L2793-L2799)
names the package and download URL. Neither inspected file identifies an exact
source snapshot, applicable package notices, or a corresponding-source route.
The [decomp.me preset](https://www.decomp.me/preset/143) is usage metadata.

GCC's [official 2.96 notice](https://gcc.gnu.org/gcc-2.96.html) identifies 2.96
as a development codename rather than a formal release. The
[GNU Tools for Playstation project](https://sourceforge.net/projects/ps-gnu-tools/)
declares GPLv2, and the separate
[PS2 GCC 3.2.3 source tree](https://github.com/rickgaiser/gcc-ps2/tree/ps2-v3.2.3)
has a [GPLv2 COPYING file](https://github.com/rickgaiser/gcc-ps2/blob/ps2-v3.2.3/COPYING).
These sources support GNU GCC/GPL-family affiliation. They do not bind this
exact EE 2.96 package to that source tree or settle all package obligations.
Local execution was demonstrated; no compiler archive is redistributed here.

The next resolving evidence is a distributor/rightsholder record that binds
the declared archive hash or `2.96-ee-001003-1` package identity to applicable
notices and an exact source snapshot or verifiable corresponding-source offer,
including EE patches. A different GPL GCC release is insufficient. No upstream
contact was made and no proprietary SDK source was sought.

The full primary-source research, local command observations, and bounded
Jev verification/dispositions are retained at
`/Users/Nicolas/Documents/github/hermes/spec-5-context/continuation-20261008/toolchain-provenance/`.
Semantic verification did not confer dependency permission or byte credit.
