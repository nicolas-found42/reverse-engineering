# Independent review: relocation-aware IRX crosswalk

## Outcome

I found no false-positive candidate in the reviewed crosswalk paths or in the exact pinned 24-module corpus. The 13 focused tests pass. The independent corpus scan sees 24 modules, with `.text` at ELF section index 2 in all of them; it found 746 loaded export-link sites, and all 746 are zero-symbol `R_MIPS_32` relocations whose `sh_info` target is section 2. No site was missing that profile. The raw link inputs and outputs remain metadata only; no module or game code was executed.

The exact raw relocation-info comparison `r_info == 2` in `ps2_irx_crosswalk.py` means symbol index zero and type `R_MIPS_32` for this ELF32 format. Although the code writes that as a magic number, the synthetic wrong-kind probe was rejected with “observed export pointer lacks its R_MIPS_32 relocation,” and the corpus scan independently confirms the contract for all 746 real slots.

## Boundary probes

The synthetic probes confirm the important distinctions:

- A zero-valued `R_MIPS_32` pointer becomes a candidate at relative offset zero after subtracting the explicit synthetic base.
- A genuine zero with no relocation ends the export table. A nonzero raw word after that sentinel is not interpreted as another export slot.
- If a relocated zero opens the table and a later nonzero word lacks `R_MIPS_32`, the crosswalk rejects it.
- A pointer site relocated by `HI16`/`LO16` rather than `R_MIPS_32` is rejected.
- A later pointer that wraps to zero at the explicit base is rejected as a false terminator.
- A relocation that alters an import stub is rejected because the parsed stub encoding no longer matches.

These checks are reproduced in `adversarial_probes.py` and `adversarial-probes.json`. The exact test log is `focused-tests.log`.

## Candidate identity and scope

The candidate key uses exact library bytes/name, exact packed 16-bit version, and import stub immediate ordinal against the export pointer position. Pinned `ps2sdk` source shows `IRX_VER(major, minor)` packs both version bytes; its loader’s `aLinkLibEntries` compares library name and major version, while `aLinkClient` uses the LI immediate as an index into the null-terminated pointer array. Thus the crosswalk’s full-version equality is intentionally stricter than the source loader’s major-version compatibility check. A minor-only difference can be reported as `no_candidate`; that does not mean the loader cannot bind it. The crosswalk explicitly avoids runtime binding or compatibility claims, so this is a conservative omission policy rather than a false match.

The `corpus()` route calls `verify_corpus` on the exact inventory and boundary records, reads only module slices returned by that verification, checks every slice length and SHA-256, prevents paths escaping the extracted root, then compares inventory and boundary bytes again. The saved scan is pinned to inventory SHA `ad865a50ff602156659bd4322f5ad60b5ff531e7c141535bd9e491c85aca96a2` and boundaries SHA `1891b2be5869d48da161388601788ae9849cbf9fd1c2229be413185ffe06c102`. I found no source/path/slice mismatch.

The loader source comparator is the local `ps2sdk` checkout at commit `ac92a9f657d2e531dd8f060250b07f2a5ac6dea5`; the existing source screen is [r073](../r073-source-screen.json). Its `aLinkClient` counts export pointers until null and reads each import stub’s immediate as a positional index. This is a software-source comparison, not proof of runtime behavior for this title.

## Commands and judgment dispositions

The passing focused command was `python3 -m unittest test_ps2_irx_crosswalk -v` from `tools/`. The first attempt from the repository root (`python3 -m unittest tools.test_ps2_irx_crosswalk -v`) failed to import `evidence_common` because the tests expect `tools/` on the import path; the corrected working-directory invocation passed all 13 tests. The `jgrep` query on the crosswalk returned no matching chunk, and jgrep could not index the pinned C source; direct source inspection and exact searches supplied the evidence.

Jev audited the five extracted corpus fields with no flags. Its six claim verification returned six `verified`, with two confidence-based `review` actions retained (the literal `r_info == 2` interpretation and full corpus provenance). The code review returned `escalate`, `safe_to_apply: 0.41`, limited by low confidence—this report keeps that escalation and does not treat Jev as approval. See `jev-receipt.json` for the recorded dispositions and usage.

This review does not establish runtime registration, load order, callable function semantics, or whole-game code coverage. It does not claim every `no_candidate` import is absent from the runtime.
