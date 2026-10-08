# FR2 compiler probe

`tools/compiler_probe.py` compiles one source file with each candidate described
in a JSON manifest, extracts `.text.<symbol>` with the candidate's GNU `objcopy`,
and compares the function bytes through `matching_diff.compare`. It writes an
immutable JSON receipt under `.scratch/evidence/compiler-probe/` by default.
Each receipt records source/reference identities, candidate executable hashes,
argv, return codes, function hashes, and per-candidate gate verdicts.

The manifest has `source`, `symbol`, `reference`, and `candidates` fields. Each
candidate has an `id`, `compile` argv array, `objcopy` argv array, and optional
`flags` array. The reference should be an independently attributed retail
function range, and the source should be a reconstruction candidate for that
same range. The local exploratory probe described below does not meet that bar:
its candidate C was hand-written from a retail instruction sequence and nearby
strings. Its match is diagnostic only; the repository contains no FR2 compiler
selection receipt.

Run the synthetic controls with:

```sh
tools/check.sh test_compiler_probe
```

The run status is `pass` only when exactly one candidate matches and every
candidate was executed without operational errors. If all candidates execute
and none match, the result is `fail`; byte mismatches are retained as expected
candidate results. Missing tools or multiple matches are `incomplete`. A compile
or extraction error also makes the aggregate `incomplete`, even if another
candidate matched. A unique match applies only to the specific evidenced
source, flags, and reference; it does not by itself identify the game's
original compiler.

## Local exploratory probe (not a compiler pin)

An external local experiment used the PAL executable hash
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95` and a
60-byte function entry at virtual address `0x001d1800`. The saved-function
inventory calls it `FUN_001d1800`, attributes it to
`../fr2/source/app3d/misc3d.c:188`, and records five callers. This attribution
is useful source-map evidence, but does not prove original authorship or
independently establish that the whole function range is game-owned. The
hand-written local candidate used the observed global access, callee, and
nearby strings; it was never added to this repository.

Using `-G8 -O2 -fno-optimize-sibling-calls`, GNU `ee-gcc2.96` emitted a linked
function matching all 60 retail bytes. The same exploratory command with GNU
`ee-gcc2.9-991111-01`, `ee-gcc3.2-030926`, and `ee-gcc3.2-040921` produced
nonmatching functions (64 bytes each). The official GNU `ee-gcc2.95.2-273a`,
`ee-gcc2.95.3-114`, and `ee-gcc2.95.3-136` drivers ran under Wine and compiled
the candidate after omitting `-fno-optimize-sibling-calls`, which these older
drivers reject. Each emitted a 68-byte nonmatch with `-G8 -O2`. All were linked
with open GNU binutils. This does not distinguish the original game compiler:
the source and profile are exploratory and selected while interpreting the
same retail function. A second independently evidenced function probe and
independent game-owned range attribution remain necessary for AC05.

The candidate distributions were taken from the public
[`decompme/compilers` GNU EE platform package](https://github.com/decompme/compilers)
and its official release assets. The x86 Windows 2.95
drivers used Wine 8 in a Debian Bookworm `linux/amd64` Docker image; 2.9, 2.96,
and 3.2 ran in the same Linux emulation profile with 32-bit libc. The compiler
invoked its bundled GNU `as` (`ee-as` for the native Linux distributions and
`as.exe` for the Windows distributions); no `ps2eeas.exe`, proprietary linker,
Sony SDK, or SN tool was invoked. The external receipts record distribution,
tool, source, and output hashes and exact argv. They remain under the ignored
local directory `spec-5-tools/compilers/`, because they depend on the private
retail corpus and inferred source. Only the bounded result above is retained
here.

For this local run, the source candidate SHA-256 was
`7a3b6e417dd3cb71cee3d5ffd36399cbd85eaa4aed49a273507d2938b02f2446`; the
reference SHA-256 was
`1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e`. The
manifest SHA-256 was `30386932dd2354066e9750668aa3a356f844e284703afab20b59fbb9773af3e2`.
Candidate compiler driver and linked-function hashes were:

| GNU candidate | Driver SHA-256 | Flags | Bytes | Linked-function SHA-256 |
| --- | --- | --- | ---: | --- |
| `ee-gcc2.9-991111-01` | `64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265` | `-G8 -O2` | 64 | `e54a7daa25ca8db663b12aa3bf17327ea0fe6b4b23838e71b867cb54383dfa60` |
| `ee-gcc2.95.2-273a` | `ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc` | `-G8 -O2` | 68 | `31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8` |
| `ee-gcc2.95.3-114` | `522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e` | `-G8 -O2` | 68 | `31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8` |
| `ee-gcc2.95.3-136` | `522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e` | `-G8 -O2` | 68 | `6611e74411e449673728a17e0a54312d978727f1196df62c093458e91253c618` |
| `ee-gcc2.96` | `b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b` | `-G8 -O2 -fno-optimize-sibling-calls` | 60 | `1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e` |
| `ee-gcc3.2-030926` | `8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951` | `-G8 -O2 -fno-optimize-sibling-calls` | 64 | `2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229` |
| `ee-gcc3.2-040921` | `a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a` | `-G8 -O2 -fno-optimize-sibling-calls` | 64 | `2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229` |

The external JSON receipt also pins each driver, bundled GNU compiler/assembler
files, linker, objcopy, runtime image, and the exact expanded phase argv. The
table is not a substitute for that private receipt and does not credit a match.
