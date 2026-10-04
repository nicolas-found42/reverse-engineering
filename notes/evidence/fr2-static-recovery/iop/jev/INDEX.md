# IOP Jev receipts

| Receipt | Tool | Result | Disposition |
| --- | --- | --- | --- |
| `irx-import-encoding-verify.json` | `jev_verify` | Source-structure claim verified at 0.78 confidence / review; exact parser profile verified at 0.97; corpus byte counts verified at 1.00. | Kept the upstream result at review. Exact on-disc words were independently counted on all 748 stubs and 166 terminators. |
| `irx-gate-final.json` | `jev_gate` | `escalate`; 3 claims auto-verified, one parser failure-mode claim unsupported at 0.37 confidence, import ABI claim needs review at 0.71. Patch review also escalated on confidence and test-gap rubrics. | Preserve the escalation. No Jev auto-approval is claimed. The actual code was supplied as unified diffs; the corpus and 14-test checks ran independently. |
| `irx-gate-02-before-abi-tightening.json` | `jev_gate` | `escalate` | Prior iteration before exact stub/terminator validation. Retained as history, not as final review. |
| `irx-gate-03-invalid-diff-input.json` | `jev_gate` | `escalate` | Earlier call passed an invalid diff command output. Retained to avoid discarding the exact result; superseded by the final unified-diff review. |

`jev` judgments are advisory. The source excerpt from `frno7/iopmod` had a screen recommendation of review; manual inspection found ordinary C format declarations/comments and no agent-directed instructions. The final implementation and its unresolved limitations are reviewable in `tools/ps2_irx.py`, `tools/verify_irx.py`, the immutable result, and the tests.
