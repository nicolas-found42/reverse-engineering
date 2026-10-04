# Bounded level-zero texture upload interpretation

The unchanged 56-model baseline now yields 2,370 level-zero RGBA images: 350
format1, 1,551 format3, and 469 format4. The indexed-only verifier independently
records 2,020 index planes. These are static file interpretations under the
measured model upload contract. Mips, runtime render selection, CLUT state
changes, GS behavior, and complete game semantics remain unresolved.

## Static provenance

`0022f948` explicitly writes all 75 bytes of the five 15-byte format rows at
`232d90 + format*15`. The original file contains zero-filled table storage;
the values here come from immediate definitions and byte stores, not those
zero bytes. `00222358` selects primary row fields +9/+2 for direct upload and
alternate +12/+11 for descriptor bit8 set. For packed format3 this selects
PSMCT32/32 bits; for packed format4 it selects PSMCT16/16 bits. Sampling uses
PSMT8/PSMT4 respectively.

`00222110` builds BITBLTBUF with DBP at bit32, DBW at bit48 and DPSM at bit56;
TRXREG contains width at bit0 and height at bit32. Its QWC is
`(width*height*bits_per_pixel)>>7`, and the source pointer comes from texture
offset +28. Descriptor +38 contains source dimensions, transfer dimensions,
and bit8. Descriptor +30 holds TBW/DBW. The measured packed transfer has half
the source width and height; the measured direct transfer retains both.
`00127470` and `00228ed8` call this uploader. Other routines, including
`00220fe0`, select a different alternate format; this contract is specific to
the traced model path.

[Upload byte provenance](texture-upload-static-provenance-01.json) reconciles
1,068 instruction words in seven functions with the original ELF. The separate
[palette byte provenance](texture-palette-static-provenance-01.json) reconciles
539 words in four functions. Full original instruction listings and generated
C remain in ignored scratch. These records retain counts and hashes only.

## Address and palette mapping

PCSX2's public GS address tables at revision
`81526d4dc7cc70e4ae75abb35a789417456c6d43` supply a pinned, independently
maintained reference. Firecrawl retrieved GSLocalMemory.cpp/.h, GSTables.cpp,
GSBlock.h, and GSRegs.h. Fresh raw GitHub bytes for three headers/tables match
the Firecrawl text after trimming outer whitespace; hashes are in
[public source pins](texture-gs-public-raw-pins-01.json). The public source is
GPL-3.0-or-later. The authored decoder uses address arithmetic checked against
the tables; the complete tables remain in scratch.

Synthetic labels written at PSMCT32/16 addresses and read at PSMT8/4 addresses
give bijective maps for all 31 measured packed profiles. All 1,321 packed
format3 planes agree with the previous eight-bit formula; all 441 packed
format4 planes decode through a complete nibble permutation. The remaining
230 format3 and 28 format4 planes use direct linear indices. Among those 230
format3 planes, the old decoder gave different indices for 184, rejected 45
small images, and happened to agree for one. The old implementation and its
receipts are retained under [superseded/](superseded/) and in the
[baseline disposition](texture-linear8-baseline-disposition-01.json).

The loader swaps palette index bits3/4 for 256-entry A/C blocks and leaves
16-entry B blocks alone. `00222a38` uploads these as 16x16 or 8x2 PSMCT32.
Both upload shapes give raw color labels0..15 under the pinned T32/I4 CLUT
mapping. `0022c660` uses initializer field +10=0 for CPSM and leaves CSM/CSA
zero. Nineteen format4 images reference a 256-entry palette block; the bounded
decoder therefore accepts 64 or 1,024 palette bytes and selects the first16
raw colors. Stored alpha bytes are preserved.

## Validation and limitations

The focused texture run passes24 tests. The current full suite passes297 tests
with the existing TypeSafe SDK environment and pristine translator source
pin; pyright reports zero errors across six changed source/test files.
[Indexed corpus](indexed-corpus-result.json) and
[RGBA corpus](rgba-corpus-result.json) retain baseline input pins, counts, and
every output hash. No original uploader, game routine, GS, or emulator ran.

[Validation logs](validation/) preserve failures: the initial four-bit guard
rejected19 large palette blocks; a later CLI test retained a stale unsupported
expectation; a fixture overwrote its format byte; one suite used an environment
without TypeSafe SDK; another omitted the translator source setting; another
used patched source against pristine hash guards. `full-python-sdk-suite-25.log`
is the passing current full run. Earlier partial/failing runs are historical.

Jev screens of fetched public source retain their moderate injection-review
scores; manual inspection treated license text, preprocessor directives, and
source as data. The claim verification in
[r082](r082-texture-upload-durable-summary.json) retains low-confidence static
claims and contradictions of universal-uploader and whole-game claims.
Its exact broad original-code arguments remain in scratch with receipt hashes.
The later [patch gate](jev/r084-texture-patch-gate.json) escalated on test-gap
and blast-radius confidence, with `safe_to_apply=0.33`; no automatic acceptance
or favorable retry is asserted. Its test claim was unsupported by the model
although logs were provided in the tool's tests field. Direct log inspection
and the [independent source-table and palette review](independent-review/README.md)
supply the bounded manual checks; [the disposition](jev/r084-manual-disposition.json) records those
limits. This checkpoint does not establish a fully decompiled game.

The root reran both independent authored audit scripts and reproduced their
results exactly. They compare57,782,272 format3 and15,067,968 format4 index
bytes and all31 packed coordinate profiles. The corrected CLUT audit restores
all256 I8 labels and16 I4 labels for both palette upload shapes. Its unrelated
format4 row+14 error (2 instead of128) is retained as a superseded result; the
selected PSM/CPSM fields were unchanged. See
[root independent validation](root-independent-validation.json).

The separate [static mip byte-count audit](mip-upload-static-audit/README.md)
now reconciles all 56 archive-bound models: 4,941 levels, including 2,571 extra
mips, and 79,708,000 equal source/predicted-transfer bytes. This establishes
a descriptor and byte-count relationship. The decoder verified above still
covers level zero; full mip record address semantics and pixel decoding remain
open. The prior 54-file uppercase-glob result and incomplete abbreviated Jev
receipt remain explicitly historical.

## Later source change (PR review)

The hashes pinned in `source-pins.json` describe the sources as audited. After that, code review noted that `tools/ps2_container.py` accepted mip counts larger than an image can halve (a 1x1 texture with one mip produced a zero-byte level). The parser now rejects such descriptors, and `tools/test_ps2_textures.py` gained a regression test. Current SHA-256: `ps2_container.py` `d6782d76949eff05aa214b7d35bd5f1722a3109596bd765a2c55153923d331d0`, `test_ps2_textures.py` `7aa29e342cf1905d42e13185ad27294deacec0f2f3ad0583a815703397a5548d`. The real-corpus integration test (56 models, 2,370 textures, all level-0 images decoded) and the 25 texture and texture-index tests passed on the changed code, so no corpus texture used an over-long mip chain. The pins above were left as the audited record.
