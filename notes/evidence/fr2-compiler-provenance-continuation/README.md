# Historical compiler source continuation

Issue #21 remains incomplete. The newly inspected public source candidate is
useful for IOP source reconstruction, but its EE source explicitly reports
`2.9-ee-991111`, which differs from the selected probe package
`2.96-ee-001003-1`. Its license files cannot establish the selected package's
corresponding-source or redistribution disposition. Issue #8 and AC05/AC31
remain incomplete; no ownership or matched-byte accounting changes.

The public candidate is
[SSXModding/ps2-ee-toolchain at b595ded606227e93b8c4a447446c1d2ac093827d](https://github.com/SSXModding/ps2-ee-toolchain/tree/b595ded606227e93b8c4a447446c1d2ac093827d).
The fixed [source candidate decision](source-candidate.json) binds the ZIP
and selected source, notice, original archive and build-material member hashes.
No source archive, compiler binary or generated reconstruction is published here.

## Reproduce the source audit

These local inputs already exist under `.scratch/compiler-provenance-continuation/`.
For another environment, the immutable source URL and GNU download URLs are
recorded in the decision and reconciliation receipt. The check has no network,
dependency installation, or compiler execution step.

```sh
python3 tools/compiler_provenance.py \
  /Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers \
  .scratch/compiler-provenance-continuation/ssx-source.zip \
  --output .scratch/compiler-provenance-continuation/receipts
```

The actual command exits **2 (incomplete)**. Its retained
[result](ee-source-audit/result.json) reports a passing source/member inventory,
a passing selected binary archive hash, and a source-version mismatch. Even a
version-compatible source inventory without a recorded distributor/build
relation remains incomplete. Source-version text in a comment cannot count as
a declaration. Archive repacking, changed members and missing notices are
accounted independently. A changed selected archive is an available contradiction
and exits 1 (fail), including when the source input is absent. A missing selected
archive remains incomplete.

The fixed source snapshot's changed archive/member identity is also a failure,
independently of absent selected-package evidence. The [changed-source with
missing-package receipt](ee-changed-source-with-missing-package/result.json)
exits 1 and retains the missing selected-package observation. A source-version
mismatch in the unchanged recorded candidate remains incomplete because no
historical package/source relation was established. The public CLI regression
first reproduced the incorrect exit 2 in
[source-contradiction-red.log](source-contradiction-red.log), then passed with
the corrected exit 1.

The ZIP hashes to
`b33ac7197cc8d4d28eb42275a05d800c126ff32ac3915624470ee55cdb5ee6ad`.
REA `open_binary` admitted that same ZIP identity. Its subsequent
`inspect_artifact` returned `artifact_operation_failed` with reason `io`, so
it supplied no member or license conclusions. The committed checker uses
Python's format-aware ZIP inventory against the fixed hashes; the REA target
was closed afterwards.

## IOP source lineage

```sh
python3 tools/compiler_provenance_iop.py \
  .scratch/compiler-provenance-continuation/ssx-source.zip \
  .scratch/compiler-provenance-continuation \
  --output .scratch/compiler-provenance-continuation/iop-receipts
```

The actual command exits **0**, bounded to source reconciliation. It compares
the candidate's original tar members with independent direct GNU downloads:

| Source | GNU archive URL | Observed SHA-256 |
| --- | --- | --- |
| GCC 2.8.1 | [GNU GCC archive](https://ftp.gnu.org/gnu/gcc/gcc-2.8.1.tar.gz) | `3b30fbfdf93e628373d90d174243f3267b0eec9ebe792bb64fd15b8828c2ea4c` |
| binutils 2.9.1 | [GNU binutils archive](https://ftp.gnu.org/gnu/binutils/binutils-2.9.1.tar.gz) | `58d01daa576d8779e064922171276795f00ff1388b1b0f87aa1a00eb0da6c6bb` |

Both direct downloads equal the pinned candidate members. The tool applies the
pinned [IOP retargeting patch](https://github.com/SSXModding/ps2-ee-toolchain/blob/b595ded606227e93b8c4a447446c1d2ac093827d/iop/original/iop-gcc.patch)
to those original sources in a new temporary directory. Patch exit is zero.
Against the candidate's modernized source tree, it records 1,219 identical GCC
files and three changed files (`c-gperf.h`, `config.in`, `obstack.h`), plus an
additional `config.in~`; binutils has 2,083 identical files and one changed
`include/obstack.h`. The [receipt](iop-source-reconciliation/result.json)
retains each difference's source/candidate hashes. These differences are not
assumed to preserve compiler behavior.

The source-side notice observations are distinct from historical binary
permission. [GCC COPYING](https://github.com/SSXModding/ps2-ee-toolchain/blob/b595ded606227e93b8c4a447446c1d2ac093827d/iop/gcc-2.8.1/COPYING)
contains GPL version 2, and the retargeting patch's new target headers explicitly
declare GPL version 2 or later. Source/build materials can be retained and
investigated with their notices. This evidence establishes neither the exact
selected EE package's source nor a source-built IOP compiler match to FR2.
Its historical-binding status remains incomplete with zero matched bytes.

The candidate [build script](https://github.com/SSXModding/ps2-ee-toolchain/blob/b595ded606227e93b8c4a447446c1d2ac093827d/build.sh)
prescribes an i686 compiler with `gcc -m32`. The available Node image's arm64
host GCC rejects this specific flag. Reproduce the bounded host capability
observation with its immutable image ID:

```sh
docker run --rm --network none --entrypoint /bin/sh \
  sha256:dd5847a04b0deee391fa145f1f4c6d214196668b6bcc7988ebed67249f226844 \
  -c 'printf "int f(void) { return 1; }\n" | gcc -m32 -x c -c - -o /tmp/probe.o'
```

This command exits 1; [the actual log](iop-host-capability.log) retains the
unsupported-flag diagnostic. It does not establish that every possible source
build on this machine is unavailable. No compiler build or new dependency
installation was performed. A compatible source-build host, an evidenced IOP
unit/ABI/relocation profile, and compile-and-diff remain the next independent
work for an IOP matching claim.

## Controls and verification

The EE public CLI also has actual negative/incomplete receipts. The
`changed-package` tool root contains a public synthetic replacement for the
selected archive, and `missing-source.zip` is absent. [That run](ee-changed-package-with-missing-source/result.json)
exits 1 and retains both the missing source and changed accepted tool input.
The empty `missing-package` tool root with the same absent source
[exits 2](ee-missing-package-and-source/result.json). Reproduce both with
the source-audit command above using those roots and missing source path.

The IOP input controls run through the same public CLI above using
`.scratch/compiler-provenance-continuation/iop-wrong-download` and
`iop-missing-download` as the GNU root. The first contains only a deliberately
wrong binutils archive, leaving GCC absent; [its receipt](iop-changed-with-missing/result.json)
reports both the missing GCC and changed binutils, with the changed-input
diagnostic preserved. The empty-root [receipt](iop-missing/result.json)
reports both downloads missing. The changed-with-missing control exits **1**;
the wholly missing control exits **2**. Neither runs a patch. Fixed GNU archive,
source snapshot, patch or derived-tree contradictions are failures. Expected
modern source differences are recorded in the tool independently of caller
inputs; an additional/missing derived-tree difference fails that fixed profile.
This does not clear the separate historical compiler binding.

```sh
tools/check.sh test_compiler_provenance test_compiler_packages test_compiler_profile
pyright tools/compiler_provenance.py tools/compiler_provenance_iop.py tools/test_compiler_provenance.py
python3 tools/ip_rails.py --tree
```

The new source audit's initial import-missing red result is retained in
[tdd-red.log](tdd-red.log). The focused controls pass eleven tests; the related
command passes nineteen tests in [related-tests.log](related-tests.log).
[Typechecking](typecheck.log) reports zero errors/warnings/informations.
The tracked-tree IP check exited zero. These are bounded tooling checks;
the parent integration performs the complete suite and final independent
Standards/Spec review.

[Jev verification input](jev-verification-request.json) and
[unchanged output](jev-verification-result.json) retain four verified factual
claims, no contradicted/unsupported claims and no review dispositions. This
semantic judgment does not supply absent package binding, compiler-build,
runtime, or ownership evidence.

The [per-file Jev review](jev-review-result.json) remains escalated
(`safe_to_apply: 0.43`, composite `0.763`). It supplied low confidence on
IOP correctness and source-audit blast radius; it did not identify a specific
contradiction. Its [actual diff input](jev-review-request.json) is preserved
unchanged. The integration review subsequently requested public CLI controls
and changed-selected-package failure precedence; those changes and the new
receipts/tests are retained above. The verification and model review describe
their frozen pre-control inputs, including the earlier five-test result. Final
independent review and disposition belong to the parent integration; no model
approval is asserted. The Standards reviewer subsequently requested failure
semantics for fixed IOP source contradictions and public IOP CLI controls.
The repair above retains original receipts in the `*-before-fail-control/`
directories and supplies new source-reconciliation, changed-with-missing and
missing receipts. The matching source command exits 0, changed-with-missing
exits 1, and missing-only exits 2. Synthetic public tests also execute the IOP
CLI with a changed source ZIP (exit 1) and absent source ZIP (exit 2).
