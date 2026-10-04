# Ghidra warning-comment audit 01

Scope: `.scratch/mesh/codex-root/decompile-dispatch-all-3837-02` and immutable verifier result `.scratch/evidence/decompilation/20261004T111703Z-fcd58dd6cc524e5f8f1d89ed37ad1be3/result.json`. No generated pseudocode or full inventory is copied here.

Provenance: executable SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`; inventory SHA-256 `1253eed69b20d9d6ffcd9e585a0963faa9a4725d506e0d1babc47a4274fdf3b8`; manifest SHA-256 `b94a74ec4e82a4dcb93e60a2bcd66ab0ae644e54ea31fe2b2a6ba3879b1a35ad`; verifier-result SHA-256 `8166bfe8d56ac43c979b4d28d92c3a9bab18e039bb59818a4dece717f382670e`.

The export verifier reports 3,837/3,837 generated functions, zero decompile failures, and 606 warning comments over 430 function entries. Exact per-category affected-entry lists are retained in `details.warning_categories` in the immutable verifier result above.

| Warning text/category | Comments | Affected functions | Audit interpretation |
|---|---:|---:|---|
| Subroutine does not return | 463 | 315 | 462 comments immediately precede a call to `FUN_00105888`; the remaining one has that call within the next 400 source characters. `FUN_00105888` ends in an unconditional branch to an earlier address and has no return in the exported instruction inventory. This strongly supports a genuine fatal/log-then-spin helper, not 463 independent failures. |
| Overlapping global symbols | 77 | 77 | Symbol alias/name ambiguity; no behavior defect established. |
| Removing unreachable block | 49 | 42 | Control-flow cleanup annotation; at `FUN_00202a70`, the shown target `0x00202d88` is bypassed by a constant guard whose low-bit mask is 4, so that specific removal is consistent with the bytes. |
| Do-nothing infinite-loop block | 7 | 4 | Control-flow/spin-loop annotation. The warning itself does not distinguish intentional wait loops from lost effects. |
| Switch manually overridden (verifier's `other warning`) | 3 | 3 | Manual control-flow recovery; entries `001161a8`, `0017f510`, `001fbe48` each have register-indirect jumps and computed local targets in the static inventory. No target omission shown. |
| Type propagation did not settle | 3 | 3 | Analysis/type limit at `0011d748`, `001d1dd0`, `0020f9f0`; review types if a specific downstream issue appears, but no byte-backed repair found here. |
| Decompiler restarted for space | 2 | 2 | Resource/analysis diagnostic. |
| Heritage after dead-code removal | 1 | 1 | Analysis diagnostic at `00130430`; no independent output contradiction established. |
| Overlapping instruction decode | 1 | 1 | `001f36a0`; highest-value focused manual review, because it is the only instruction-integrity warning. |

The most-commented functions are `00161728` (32), `001d64a0` (13), `0012d4b8` (11), `00104c00` (9), `00109950`, `0015f0c0`, `001d8eb0`, and `00202a70` (6 each). The first four are dominated by the fatal-helper call annotations; `00202a70` has six comments from both unreachable blocks and loop/control-flow notes.

## Byte/CFG spot checks

* `001f36a0`: the ELF load-segment mapping gives adjacent file offsets `0xf46f0` and `0xf46f4`; bytes are `14004011` and `ffff4a25`, matching the inventory's `beq` and following `addiu`. Each is an aligned four-byte R5900 instruction. The branch's next word is its delay slot, and another loop branch targets that delay-slot address. The warning may reflect Ghidra delay-slot/control-flow ownership, but the supplied evidence does not show overlapping bytes or a safe decompiler correction. Keep as a targeted listing/CFG investigation only.
* `00202a70`: instructions at `0x00202d08`–`0x00202d20` load `0x00396df4` and `0x00396fc0`, OR them, and mask with 7 before `beq v0,zero,0x00202d88`. For those fixed values the mask is 4; the branch is not taken. This supports the unreachable-block warning and is not a repair candidate.
* `00105888`: its tail contains the unconditional branch from `0x00105abc` back to `0x00105aa8`, with no return instruction. The repeated non-return warning call sites are consistent with this helper's control flow.

No concrete static repair is recommended from this audit. The single instruction-overlap warning deserves focused Ghidra listing/CFG review, while all evidence here is insufficient to change the project or exported pseudocode. Warning annotations are diagnostics, not a count of semantic errors.

Jev receipts: `jev_classify` labeled the nine warning categories with auto decisions (total input 1,708 tokens; output 651); `jev_verify` checked four category/bytes/control-flow claims, all verified (0.94–0.99 confidence; input 2,848, output 566). These are triage/evidence checks, not substitutes for the raw-byte analysis. `jgrep` query “extracts warning comments from generated C and assigns them to categories” returned `tools/verify_decompilation.py:178–237` at p=0.92 (279,253 tokens indexed, $0.0117). The generated-C tree is hidden from jgrep's file discovery; no findings from that unsuccessful attempt were used.
`jev_find` ranked `overlap_001f36a0` first with probability 1.0 and `exists_verdict=answered` (input 1,213, output 152); this only supports prioritizing a focused review, not a repair claim.

## Isolated delay-slot investigation: `001f36a0`

A fresh, non-hidden copy of `ghidra-project/codex-root-dispatch-full-02` was used because Ghidra rejects project path components beginning with `.`. The failed first invocation used `.scratch/mesh/codex-audit/warnings/overlap-experiment-01/project-copy`; it exited 1 before opening a project with `Path element starting with '.' is not permitted`. No analysis ran. The successful experiment copied the same project into ignored `ghidra-project/warning-audit-exp01`, ran `-noanalysis`, and invoked a temporary probe script for only function `001f36a0`. Exact logs, probe script and private metadata JSON are in `.scratch/mesh/codex-audit/warnings/overlap-experiment-01/`.

The copied-project probe used Ghidra 12.1.3, language `r5900:LE:32:default`, and reports executable SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`. It decoded 43 instructions in the selected function and queried its basic blocks and decompilation. The resulting function artifact is byte-for-byte identical to the already exported one: SHA-256 `d33302df1a5d5c895fe6b987e12a92fea08299b7b69e5a364dd963928db35fe6`, 1,140 bytes. The overlap warning reproduces.

At `0x001f36f0`, the decoded unit is four-byte `beq`, bytes `14004011`, with a flow target at `0x001f3744`; at `0x001f36f4`, Ghidra reports a distinct four-byte `addiu`, bytes `ffff4a25`, and marks it as the `beq` delay-slot instruction. The `bgtz` at `0x001f373c` has the direct flow target `0x001f36f4` and its own delay slot at `0x001f3740`. Thus the branch target is the preceding branch's delay-slot instruction, while the machine bytes remain distinct and adjacent. Ghidra's `BasicBlockModel` maps target `0x001f36f4` to the block `0x001f36f0–0x001f36f7`, whose first address is `0x001f36f0`; the return target `0x001f3744` maps to its own block. This is consistent with the overlap diagnostic arising from control-flow ownership around a delay-slot target, but does not establish the exact internal warning cause.

Primary-source comparison: Firecrawl fetched the official Ghidra 12.1.3 release source at [`mips32Instructions.sinc`](https://raw.githubusercontent.com/NationalSecurityAgency/ghidra/Ghidra_12.1.3_build/Ghidra/Processors/MIPS/data/languages/mips32Instructions.sinc), HTTP 200, scrape ID `01a106b9-85eb-73c9-852e-77146f45401a`. The fetched text SHA-256 and local processor-language source SHA-256 are both `8f8acdf9a433ae072f212616335ebe5a9b7ff407e5850df8d7dcadd0d3fd290e`. The official `beq` and `bgtz` patterns each declare `delayslot(1)` before their conditional branch. This confirms the listing's delay-slot marking against the exact Ghidra release source used by the experiment.

The existing decompilation's 8-line cache-operation loop corresponds structurally to the raw unrolled block and the branch/decrement sequence, but the experiment does not prove runtime equivalence. The warning is reproducible; the distinct instructions and matching C output give no concrete static defect to repair. Do not patch or suppress the warning on this evidence.

Commands and outcomes:

```text
# failed before project open (hidden project-path component)
env JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home PATH=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home/bin:$PATH .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless .scratch/mesh/codex-audit/warnings/overlap-experiment-01/project-copy fr2 -process SLES_517.05 -noanalysis -scriptPath .scratch/mesh/codex-audit/warnings/overlap-experiment-01/scripts -postScript ProbeDelaySlot.java .scratch/mesh/codex-audit/warnings/overlap-experiment-01/probe-01.json
# exit 1: Path element starting with '.' is not permitted

# successful, isolated one-function run
env JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home PATH=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home/bin:$PATH .scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless ghidra-project/warning-audit-exp01 fr2 -process SLES_517.05 -noanalysis -scriptPath .scratch/mesh/codex-audit/warnings/overlap-experiment-01/scripts -postScript ProbeDelaySlot.java .scratch/mesh/codex-audit/warnings/overlap-experiment-01/probe-02.json
# exit 0; log probe-02.log
```

The fresh-run `jev_verify` checked five claims about isolation, hash reproduction, decoded slots/target, block mapping, and the official source; all five were verified with confidence 0.90–1.00 (input 3,312 tokens, output 638). The fetched-source `jev_screen` recommendation was `pass` (injection 0.02, relevance 0.95, substance 0.98). Search-result screens were retained in the private scratch logs; one low-substance Ghidra release-search result was skipped and not used.
