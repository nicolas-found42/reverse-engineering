# Issue #2 spec review

**Result: no open spec findings.** Scope matches the issue: the work repairs the static exporter, maps loader stages, captures and compares real raw/zlib loads, adds bounded archive/bank/model/sprite contracts, and accounts for the complete measured PAL corpus. No scope creep found. The complete 3,446-function export, six instruction-backed loader stages, clean table correlation, two raw/zlib repeats, all 990 extracted files, 27 bank pairs, 56 models, eight gear regressions, and all 548 PTGs are accounted for. Unsupported PTGs remain listed. The README correctly discloses that PCSX2 opened debugger windows; the capture was unattended, not headless.

Review findings and resolutions:

- **Resolved — export binding.** The spec requires loader evidence “tied to ... source hashes.” `verify_static` now checks the loader map’s export SHA-256 against the complete export and binds the executable/corpus identities.
- **Resolved — semantic uncertainty.** The spec says “contradictions stop acceptance and unresolved required claims remain incomplete.” Original Jev outputs and distributions remain intact; reasoner resolutions bind the exact claims, executable, export, and audit identities. The six full-body reviews accept the required loader claims, and the static gate rejects contradicted claims.
- **Resolved — replay status and partial results.** The spec requires “offline replay cannot stand in for a fresh capture” and “partial failures preserve prior successful evidence.” Runtime replay marks itself `fresh_capture: false` and `milestone_eligible: false`; a separately indexed capture result records `fresh_capture: true` and binds the exact manifest consumed by replay. Failed/incomplete runs preserve completed comparisons.
- **Resolved — capture description.** The original screen audit’s inaccurate “headless” premise remains byte-for-byte intact. A linked disposition note corrects that premise and the user-facing docs accurately disclose debugger windows and focus behavior.

Validation artifacts report all three real verifiers passing, the separate fresh capture passing, 15 discovered tests passing (including five pre-existing research tests), and Pyright reporting zero errors. Synthetic tests remain distinct from real integration evidence.
