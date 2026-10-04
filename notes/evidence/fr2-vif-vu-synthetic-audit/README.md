# Synthetic VIF latch and VU stop/resume audit

The pinned public PS2Recomp software passes 4,096 VIF latch cases, 1,024 packet
ordering cases and 4,096 VU E-stop/resume cases. Clearing the first E bit
breaks the expected first stop in all 4,096 VU cases. Both process invocations
return zero with empty stderr: the mutant invocation succeeds only when its
changed behavior is detected. See [result.json](result.json) and the authored
[probe.cpp](probe.cpp).

Each VIF latch case supplies synthetic TOPS/BASE/OFFSET/ITOPS and DBF values.
The native MSCAL/MSCNT handlers latch TOP and ITOP before updating TOPS and
DBF. The order experiment submits MSCNT, then BASE/OFFSET, then another
MSCNT; the first latch retains the old TOPS and the later latch observes the
new base. This is a mechanism check with supplied state, not a reconstruction
of the game's preceding state.

The VU experiment uses authored NOP/E, an integer delay-slot write, XTOP,
XITOP and a second stop. It covers all 1,024 TOP values at four synthetic
start PCs. The first E pair executes its next pair before stopping; the saved
PC is the following pair. Resume reads the newly supplied TOP/ITOP and stops
at the second E boundary. The expected first-stop predicate checks PC, the
delay-slot integer write and untouched XTOP/XITOP destinations. The E-clear
mutant tests sensitivity to that boundary. No original game VU program or
other game routine is executed.

## Source and execution bounds

The public revision is
[`ran-j/PS2Recomp` c5a9d02573410a2085a4b4b831b0b68ba3515440](https://github.com/ran-j/PS2Recomp/tree/c5a9d02573410a2085a4b4b831b0b68ba3515440).
Firecrawl retrieved the pinned
[VIF interpreter](https://github.com/ran-j/PS2Recomp/blob/c5a9d02573410a2085a4b4b831b0b68ba3515440/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp)
and [VU core](https://github.com/ran-j/PS2Recomp/blob/c5a9d02573410a2085a4b4b831b0b68ba3515440/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp).
After Jev screening, both retrieved texts matched the local pinned source
apart from surrounding whitespace. Both native build-source files also equal
the pristine source. The library was built from the separate four-patch EE
experiment tree; this probe does not invoke those EE arithmetic patches.
Public source excerpts in the Jev receipt retain that project's GPL v3
attribution; its license is preserved in [tools/recomp/LICENSE](../../../tools/recomp/LICENSE).

The probe links the saved native runtime library, with an authored main.
A native symbol inventory excludes all 4,746 generated guest entry names,
the game registration table, InitWindow and InitAudioDevice. No generated
game object or registration object is a link input. No GS drawing command,
window initialization, audio initialization or game runner is invoked. The
binary and full symbol inventory remain ignored under
`.scratch/mesh/codex-root/vif-vu-synthetic-01/`. Constructor inspection found
memory allocation and CPU GS lookup initialization only.

[build-record.json](build-record.json) pins native library hashes, compile
flags and inputs. The linker reported nine deployment-target warnings: saved
library objects target macOS 26.4 while the probe link defaulted to 26.0.
The successful runs establish behavior on this host only; the compile log
retains these warnings. The saved [run_probe.py](run_probe.py), run from the repo
root, reuses that exact scratch probe only after its binary hash matches the
symbol preflight. It asserts process status, stderr and exact expected counts.
The first scratch version repeated 1,024 ordering scenarios four times; its
source and results remain preserved and the final ordering count is 1,024.

## Judgment and limits

The Jev gate remains **escalate**, safe-to-apply 0.23: all four claims were
verified, with two needing review. The exact request/result is preserved in
[jev-gate.json](jev-gate.json); [manual-disposition.json](manual-disposition.json)
records direct source/symbol/process checks. No unchanged judgment was retried.
Full source-screen receipts remain in ignored scratch, with their immutable
hashes and complete returned judgments in
[source-screen-receipts.json](source-screen-receipts.json).

This does not prove hardware behavior, scheduling/concurrency, every VIF/VU
instruction or E-bit interaction, the game's actual TOP state, rendered
output, semantic equivalence of the generated game, or whole-game completion.
