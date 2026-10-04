# Provisional 72-byte leaf candidate at `0x0022a180`

The isolated candidate experiment adds a temporary analysis function over exactly `0x0022a180..0x0022a1c7` (72 bytes, 18 existing instructions). It does not establish that this is an original function, that the original boundary ends at `0x0022a1c7`, or that any runtime path reaches it.

The span begins at the executable, allocated ELF section `.user_section_uncommon`: virtual address `0x0022a180`, file offset `0x0012b180`, size `0x27f4`, flags `6`. The PAL SHA-256 is `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`. The exact 72 bytes hash to `c5a281fb5648f92c515ee4e524f9b7b6514add1f3d162237ca78c54094b0f7a9`.

The existing instruction listing is function-shaped: it opens a 16-byte stack frame, saves `a0`, loads four bytes from the saved word, shifts/masks fields, combines them with ORs, and returns through `jr ra` with the stack restoration in its delay slot. The arithmetic supports this specific hypothesis:

```text
((b2 >> 3) & 31) | (((b1 >> 3) & 31) << 5) |
(((b0 >> 3) & 31) << 10) | ((b3 != 0) << 15)
```

Here `b0..b3` are the little-endian bytes of the input `uint32`. The channel packing is compatible with an A1R5G5B5-style interpretation, but that semantic label remains a hypothesis: Jev gave it a review disposition at 0.61 confidence. No renderer contract, original caller contract, or original symbol name has been recovered.

Reachability remains unproved. Raw reference scanning found no direct JAL/JALX target, conditional-branch target, or aligned pointer into this span. The only Ghidra incoming reference to the span start is `_elfSectionHeaders::00000264`, an imported ELF section-header DATA reference. Two unaligned byte-pattern matches inside `.user_section_init` cross instruction boundaries and are not pointers. These observations do not exclude every possible indirect or computed path.

`CreateProvisionalLeafCandidate.java` is bound to the executable SHA, R5900 language, ELF section mapping, raw bytes and span hash, the exact 3,837-entry baseline manifest hash and its entry set, existing 18 instruction words, and the one imported metadata reference. It creates only the explicitly named candidate using `SourceType.ANALYSIS`; it performs no disassembly or memory edits. It first requires the live Ghidra entry set to equal the entry set parsed from the pinned 3,837-row baseline manifest. It then checks that all pre-candidate function bodies and entries, every instruction byte and defined data unit, initialized memory, incoming reference, and outside neighbor ownership are unchanged by candidate creation. This compares bodies before versus after the candidate within the current project; it permits a combined run to begin from the same baseline entries with previously guarded body repairs. The manifest records the Ghidra version and resolved native decompiler path and SHA-256 used for generated C. The fresh promoted-script run reported:

```text
PROVISIONAL_LEAF_OK entry=0022a180 bytes=72 original_entries=3837 new_entries=3838 listing_unchanged=true memory_unchanged=true
```

The run used Ghidra 12.1.3 with a copied project, `-noanalysis -readOnly`; the baseline entry set matched exactly. The candidate C and inventory are isolated scratch output only; no whole-game output was changed. The native decompiler was `.scratch/ghidra-12.1.3/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/os/mac_arm_64/decompile` (SHA-256 `f028f42715840233c2685351e6a01ca291e4090aefc48e2e33fd2d9e5965a759`); the script does not pin that native binary. The generated files hash to:

- manifest: `196b90774919ba360430f1c30c2d42bcc09c524c2ede9c1c43ab51744a382ce9`
- inventory: `7e5b4d4ca3f9118ac7cbf701ed490f87c6a91b7ead9f2d62dfefb3a78790b6fc`
- candidate C: `2475bc5f1b389431e7fa2f6f9a6193a9381482b67476eb164080bf228957328f`

`argb1555_candidate.py` is a pure integer reference model, not an emulator. Synthetic tests exercise the input bounds, all values of each input byte, field placement, truncation transitions, alpha’s nonzero test, and combined channels. The normal top-level discovery command passed all 7 tests:

```sh
python3 -m unittest discover -s tools -p 'test_argb1555_candidate.py' -v
```

No game binary or original routine was executed.

## Durable files and source receipts

- Guarded Ghidra experiment: `tools/ghidra/experimental/CreateProvisionalLeafCandidate.java` (SHA-256 `6defa7cea739b32a7e5f88121cc862afae4192df4f16f8bb281200eddbab293a`)
- Pure arithmetic model: `tools/ghidra/experimental/argb1555_candidate.py` (SHA-256 `427befdce60dbd973a91bbe8d3a07cd812ad513e6df7ebc4c4e4955267a5adab`)
- Focused tests: `tools/ghidra/experimental/test_argb1555_candidate.py` (SHA-256 `cb116edb55cb8e8e8e7339ece600883a47557c4bd0d7b88dfb37ae25fc0435bf`)
- Top-level discovery shim: `tools/test_argb1555_candidate.py` (SHA-256 `950c9b081fe6c414a7a1b6917295f8faff4dc87a65241e75b5040aa18e0b6b9a`)
- Machine-readable reconstruction receipt: `notes/evidence/fr2-static-recovery/discovery/leaf-candidate-reconstruction.json`
- Machine-readable reference scan: `notes/evidence/fr2-static-recovery/discovery/leaf-candidate-reference-audit.json`
- Full isolated C/inventory and Ghidra output remain at `.scratch/mesh/codex-helpers/leaf-candidate-promoted-20261004/`.
- Earlier detailed disassembly and reference receipts remain under `.scratch/mesh/codex-helpers/`.

The candidate should be revisited only if a concrete call/data path or independent boundary evidence is found. The current evidence is enough to preserve a bounded arithmetic candidate, not to promote an original function identity or renderer behavior.

A promotion review with Jev escalated rather than auto-accepting the combined change (`safe_to_apply=0.25`, composite `0.8877`). It verified the reference-scan and synthetic-test claims, but assigned review-level confidence to the exact Ghidra-delta claims and marked one broad “all interpretation details remain unproved” claim unsupported. Treat that as an unresolved judgment on the wording, not as positive evidence for runtime use or original identity. The raw-byte and headless receipts above remain the concrete basis; interpretation and identity stay provisional.
