# EE static coverage and undefined-call seed audit

This bounded static audit found one high-value seed for the next Ghidra pass:
the executable bytes at `0x001fbfb8–0x001fc277` (704 bytes) are classified as
undefined by the saved combined Ghidra coverage, even though a saved function
has three direct calls to `0x001fc0d0`. The current pinned PS2Recomp output
contains three adjacent functions that cover this exact range. That makes the
span a concrete Ghidra function-seed and decompilation candidate.

The three generated ranges are `0x001fbfb8–0x001fc0cf` (280 bytes),
`0x001fc0d0–0x001fc117` (72 bytes), and `0x001fc118–0x001fc277` (352 bytes).
They cover 176 words, and the raw words represented by generated instruction
comments match the original ELF. The emitter omits one all-zero NOP comment at
`0x001fc0ec`; the underlying input word is zero. The middle function’s
generated comments also reference the two neighboring generated functions,
`0x001fbfb8` and `0x001fc118`.

The direct calls appear at `0x001fbf20`, `0x001fbf44`, and `0x001fbf68` in
Ghidra function `0x001fbe48`. Its saved instruction references mark all three
as `UNCONDITIONAL_CALL` to `0x001fc0d0`, but the address is absent from the
saved Ghidra function entries. The 704-byte window hash from the original ELF
is recorded in [result.json](result.json).

The broader crosswalk did not find a nonzero instruction-word mismatch between
the saved Ghidra inventory and the overlapping generated instruction comments.
The 4,591 inventory instruction addresses without generated comments comprise
4,573 all-zero NOPs and the 18 nonzero instructions of the separate provisional
leaf at `0x0022a180`, which has no inbound caller in the saved inventory. Of
the 32,788 defined instruction bytes in `.text` that Ghidra does not assign to
a saved function, 728 word addresses lack generated instruction comments; all
728 source words are zero. These counts do not resolve the much larger set of
`.text` bytes Ghidra left undefined, since those bytes may be data.

The measured COP0/COP2 control-register operands fall in implemented translator
cases: `MFC0` uses registers 9, 12, and 28; `MTC0` uses 6 and 9; `CFC2` uses
18, 28, and 29; `CTC2` uses 28. The generated 4,746-function tree contains no
`unhandled`, `unsupported`, `unimplemented`, `not implemented`, `TODO_NAMED`,
or `throw std::runtime_error` marker. This marker scan is a bounded check for
explicit fallback text; it is not a semantic-equivalence proof.

The saved EE listing also has a separate executable `.vutext` block of 13,696
bytes with zero EE instructions. The Ghidra language in this export is
`r5900:LE:32:default`; VU decoding and microprogram recovery need their own
architecture-specific audit. The runtime has an idle-success VU0 fallback
when VU0 code/data pointers are absent or the requested start exceeds the code
buffer. The saved EE inventory contains 37 `VCALLMS` operations (33 target
index 77; the others target 0, 17, 45, and 61), no `VCALLMSR`, and eight
`VWAITQ` operations. The translator masks VCALLMS indices to nine bits, so the
address-bound check is not reached by those immediate calls; this audit does
not establish whether runtime VU state is correct or whether the null-pointer
fallback ever occurs.

## Reproduction

From the repository root, run:

```sh
python3 notes/evidence/fr2-ee-unresolved-audit/audit_static_coverage.py
```

The script verifies the pinned ELF, Ghidra inventory, and coverage hashes
before it scans generated files. It emits only bounded metadata. It fails if a
pin changes, if the candidate intervals differ, if candidate comments do not
line up with the original bytes, or if a missing comment inside the candidate
range corresponds to a nonzero source word. It does not copy generated C++
bodies into this evidence folder.

The generated source is from PS2Recomp base revision
`c5a9d02573410a2085a4b4b831b0b68ba3515440` with the working-tree patch set
identified in [source-pins.json](source-pins.json). The object-build receipt
reports 4,746 source files and 4,746 function files across 16 passing batches.
That proves compilation of those objects only.

## Jev and jgrep receipts

Jev Find selected `0x001fc0d0` as the clearest missing-code seed among the
bounded candidates. Jev Verify marked all four reported claims verified (no
review flags). Exact tool receipts are in [`jev/`](jev/). A behavior-first
jgrep query returned the VU0 execution and idle-success fallback implementation
at `ps2xRuntime/src/lib/ps2_runtime.cpp:1426–1448` (two hits including its
`vu0StartMicroProgram` wrapper); the exact query and result are recorded in
[`jev/jgrep-vu0.json`](jev/jgrep-vu0.json).

No game code was executed. The candidate functions are not committed as C
source, and this audit does not claim whole-game completeness, runtime
reachability, or semantic correctness.

## Bounded Ghidra candidate `001fc0d0`

A fresh isolated project copy accepted one candidate at `001fc0d0`. The bounded
control-flow body is 68 bytes (`001fc0d0–001fc113`): its return instruction at
`001fc10c` has `001fc110` as its delay slot. The next word, `001fc114`, is zero
and is unreachable in the traversed CFG, so it remains unowned. This is why the
72-byte adjacent PS2Recomp interval was treated only as a maximum boundary
hypothesis. The candidate name is explicitly provisional.

After saving and reopening that single-seed project, the complete Ghidra export
contained 3,839 generated functions and zero failures. The reopened inventory,
candidate JSON, function body size, generated C manifest, and candidate C hash
agree. Every prior function entry/name/body range and instruction
address/text/byte triple matched the previous combined export. The only prior C
change was `001fbe48.c`, where three calls to the previously unresolved address
now print the candidate name. The exact call sites, file hashes, and changed
lines are in [`recovery/001fc0d0-reconciliation-check02.json`](recovery/001fc0d0-reconciliation-check02.json).

The Java script and all failed/superseded attempts are retained locally under
`.scratch/mesh/codex-audit/ee-undefined-recovery-001fc0d0-*`. The durable
reconciliation report records the executable, ELF window, baseline, script,
inventory, coverage, and generated-C hashes. Attempts that rejected the hidden
project path, initial script compilation, a wrong `.text` size pin, an
architectural delay-slot decode, and an unreachable zero tail remain intact.

Jev reviewed the new script and escalated (`safe_to_apply=0.13`, low confidence
for correctness and test coverage). A separate claim check verified five
bounded run claims; two source-pin claims were marked `review` at low confidence.
Those review flags remain recorded in [`jev/jev-review-single-seed-script.json`](jev/jev-review-single-seed-script.json)
and [`jev/jev-verify-single-seed-result.json`](jev/jev-verify-single-seed-result.json).
I inspected the source pins directly at lines 26–39 and their enforcement at
lines 475–487; the target run also demonstrates those guards passing. These
judgments do not approve the script or establish whole-program correctness.

## Reopened three-candidate union

The three bounded CFG candidates were reconciled together in a saved and
reopened project. The final export contains 3,841 generated functions and no
failures. All 3,838 prior entries retain their names, identity flags, body
sizes, block rows, instruction addresses/text/bytes. The only prior reference
changes are the three saved calls to `001fc0d0`, and the only prior C file that
changes is `001fbe48.c` as those calls resolve to the provisional candidate.
The caller/callee set changes are also limited to the expected candidate
edges. The `.text` coverage delta is exactly the 692 newly owned candidate
bytes; unowned instruction totals, defined-data totals, memory blocks, and
string inventory remain unchanged. Caller/callee lists have 2,173 ordering-
only row differences, summarized by count and hash in the report.
Exact pins and checks are in [the three-seed union reconciliation](recovery/three-seed-union-reconciliation.md).

Each transaction handles one seed. The first seed was already present in its
independently validated saved project; two further seeds were added by
separate invocations after checking its exact allowlisted name, source type,
and body range. The updated transaction snapshot also includes all preexisting
function names and source types. Jev Review escalated on low confidence, and
Jev Verify flagged one reference claim for human review; both receipts and the
manual reference-row check are preserved with the reconciliation. Candidate
identities and reachability remain unproved.

## Independent persistence check

The root check rehashed every manifested C file in both the 3,838 baseline and
3,841 final exports, checked all prior manifest identities and inventory
body/instruction rows, and compared the 173 added words with unique ELF PT_LOAD
bytes. All memory-block and string inventory rows and all non-text coverage
blocks match. The only old C delta is the exact replacement of three
`func_0x001fc0d0` call names. Its first assertion used the wrong prior name
`FUN_001fc0d0` and failed; inspection of the actual file diff corrected that
check. The passing result is [root-union-validation.json](recovery/root-union-validation.json).

The cumulative Java source was reviewed directly: it requires the exact ELF,
language, section/window hashes and baseline entry set, allows only the exact
prior candidate subset, snapshots function names/source/body, preserves memory
and defined data, bounds each decode to a word plus its architectural delay
slot, rejects computed calls/jumps and conflicting delay roles, and commits
only one exact CFG body per invocation. This manual review retains Jev's low
confidence escalation; it is not an automatic approval or a semantic proof.
