# Independent final spec-axis disposition

Reviewed source: **`9c4f9fac9f7060959dfa73b8ea5a8e235943671a`**. Repair diff: `fe44c0c...9c4f9f`; full integration scope: `e8b6541...9c4f9f`. Live #5/#8/#22/#26/#35 were reread on2026-10-08; all remain open. Root checkout was clean. No root edits, push, guest execution or judgment retry occurred during this review.

**Bounded publication is supported.** F1/F2/F3 are repaired for their concrete combined-input cases; no remaining bounded implementation defect or scope creep was found. This does not complete any of those full tickets or spec#5.

Controlling spec#5 decision2 says **“A contradiction or mismatch takes precedence over missing evidence.”** The changed code now defers absent prerequisites while inspecting available fixed evidence. Qt libraries are checked before missing Core/legacy plugin can stop preflight; lifecycle identities are checked despite absent observation/previous provenance; RPC reads available EE/STREAM independently and checks available packet framing; observation and frontier CLIs similarly inspect available contradictory inputs. Missing-only cases remain incomplete.

Independent executed checks:

- All five changed public regression modules passed: **53 tests**, no skips.
- The eight-module command from the retained README passed: **88 tests**, no skips in this fresh run. The retained historical command log's three skips remain a historical observation.
- Reexecuted all seven retained real RPC/frontier CLI commands at this SHA: positive/malformed/unsupported packets returned0/1/2; missingEE with those packets returned2/1/2; all24-module frontier returned2. Reexecuted F3 returned1 with `stream static profile identity mismatch`.
- All seven retained real receipts' existing source/raw-input hashes and lengths match current files. Their fixed EE/STREAM identities and packet identities remain bound; fresh independent receipt paths and SHA-256 values are in `spec-axis-final-evidence/controls.json` beside this note. Those fresh commands use metadata-only output directories outside the repo.

## Disposition of the new Jev contradictions

The gate remains **escalate**, `safe_to_apply:0.15`, composite`0.561625`. No result, threshold or distribution was rewritten. Each adverse claim was investigated against current code and executed controls:

| Contradicted claim | Jev confidence | Independent disposition |
| --- | ---: | --- |
| Lifecycle missing observation/previous provenance cannot hide changed available source; missing-source plus changed sibling fails; missing-only incomplete |0.51| **Supported for these bounded cases.** Direct source checks and guarded public CLI regressions passed. Current provenance catches prior incompleteness, examines present identities, then reports missing. Changed sibling identity appears in the failed CLI receipt. |
| Observation changed executable/wrong boundary/bad saved instruction fails despite absent metadata/counterpart; missing-only incomplete |0.67| **Supported.** All four observation CLI controls passed, including actual subprocess changedEE/wrong-boundary cases and the synthetic raw-instruction contradiction under the public main seam. Present input hashes are retained. |
| RPC missingEE+changedSTREAM fails; malformed packet fails despite missingEE; valid/unsupported remain incomplete; identities recorded |0.49| **Supported.** Public subprocess F3 and packet regression controls passed. Fresh real static controls independently reproduce1/2/2 for missingEE malformed/valid/unsupported; retained and fresh input identities verified. |
| Frontier changed pinnedSTREAM or malformedROM fails despite missingEE; missing-only incomplete |0.73| **Supported.** Three public subprocess controls passed; diagnostics name the changed pinnedSTREAM or malformedROM. Fresh real fixed24 inventory remains incomplete. |

These executed observations resolve the four claim contradictions for the stated cases; they do not imply a universal absence of every possible prerequisite-ordering bug or supply whole-parent acceptance. The original numerical escalation remains preserved as a separate judgment, with this stronger independent reasoning disposition.

## Full-parent requirements remain incomplete

- #8 criterion1 **“Bind candidate package/runtime/source identities”** and criterion4's exact claimed pin remain incomplete: corresponding compiler source/patch/package provenance is unresolved in#21, and aggregateAC05 still needs relevant IOP probes.
- #22 criteria1–3 require every actually used component's exact source/package/build/notices and source/offer disposition. Static roots/library pins and refusal satisfy bounded criterion4, not that full closure or #14 runtime qualification.
- #26 criterion1 **“complete required handoff inventory”** and criterion2's ownership/lifetime/synchronization/outputs remain incomplete. Candidate scans and volume framing neither close#26 nor#16.
- #35 criterion2 explicitly requires **“caller argument/return use”**; sibling consumer evidence, loader/computed aliases and new ownership remain unresolved. Structural64-byte boundary and336 compared code bytes are bounded candidates. Only the existing **60 bytes** retain attribution;276 additional identical candidates get **zero new credit**. Five NOBITS cells contribute20 layout bytes and zero file-byte matches. #37 retains follow-up gaps rather than completing#35.
- SpecAC32 requires **“A clean real-corpus aggregate run passes the reconstruction criteria”** and says **“No required incomplete result is described as complete.”** Full EE/IOP/asset/VU interfaces, licensing closure, two clean complete builds and final aggregate acceptance remain outstanding.

Earlier detailed exact#35 and initial defect reproductions remain in `spec-axis-review.md`. Historical dirty-tree lifecycle builds are identified as historical source-output evidence, not fresh whole-parent acceptance at this SHA.
