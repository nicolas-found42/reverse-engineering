# Standards review

Fixed point: `f20add331e6226bdf6308bbd52bcc70d107c44ff`. Reviewed staged/unstaged tracked changes against `HEAD`, plus the untracked `tools/capture_runtime.py` and `notes/evidence/fr2/README.md` and their supporting evidence files. No commit existed during review.

## Documented rules

No hard violations found. The issue tracker instructions are not contradicted by these local code/docs changes. The domain instructions say to proceed silently if glossary/ADR files are absent; the `.ps2` leading word remains explicitly unresolved. No triage-label changes occur.

The capture docs now accurately call the recorded run an unattended debugger capture, require `--allow-debugger-windows`, and distinguish it from offline verification, which opens no UI. This corrects the earlier “headless” wording.

## Review judgment calls

- **Preference guard race, low confidence:** `tools/capture_runtime.py::preferences` uses an atomic lock to exclude another instance of this capture tool and checks `pgrep` before taking that lock. PCSX2 itself does not honor that lock, so a normal PCSX2 session started after the process check could read or write the shared INI while this command changes/restores it. The README warns users to keep the desktop undisturbed and says the tool checks for an active session; no project rule requires stronger OS-wide exclusion. Consider rechecking after lock acquisition or clarifying the lock's scope if concurrent launches are a supported concern.
- **Cleanup wording, low confidence:** the `finally` block waits for/terminates the owned process before restoring the INI, breakpoint file, save slot, and backup; an interrupted process can leave the lock, as the README now documents. If a restoration filesystem operation itself raises, later paths are not attempted and the lock remains. That is a visible failed cleanup, not a documented coding-rule violation; the user can identify the leftover lock. The README's “ordinary failure paths” accurately covers caught capture failures, while this cleanup failure path is not described separately.

No clear baseline smell requires refactoring. `coverage()` in `tools/corpus_contract.py` still combines archive, manifest, extraction, and family accounting, but these form one corpus-coverage result. The shared parser changes reduce duplicated format logic. Other baseline smells (feature envy, data clumps, primitive obsession, repeated switches, shotgun surgery, speculative generality, message chains, middle man, refused bequest) are not apparent. These are heuristics, not project rules.

This is the Standards axis only; it does not certify functional correctness, evidence validity, or acceptance criteria.
