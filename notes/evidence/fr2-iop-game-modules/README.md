# IOP game modules: STREAM.IRX and LGDEV.IRX

The two IRX files without a Sony SDK stamp are the candidates for game or third-party IOP code. The other nine standalone IRX files are stock modules.

## What the modules are

- **STREAM.IRX** is the module `multi_streamer` (string "MultiStream v6.2"), 282 saved functions. It is **not stripped**: it has an ELF `.symtab` (490 symbols) and an ECOFF `.mdebug` section.
- **LGDEV.IRX** is `LgDev_tb_rb_Driver` ("Version 1.08 ( Wheel Joystick )"), a USB wheel driver, 166 saved functions. Its symbol table holds no names, so every function is `FUN_…`. It exports 19 slots of library `lgdev` v264; 16 match function entries and 3 point at the reserved offset.

## STREAM's debug symbols, cross-checked

`tools/ecoff_mdebug.py` reads the `.mdebug` section; `tools/iop_symbols.py` pairs it with the `.symtab`. The section's regions tile its 38,504 bytes exactly, which independently fixes the record sizes. Checks that can fail, all passing on the real module:

- 211 of 211 procedure descriptors match a function symbol by name.
- Within each object file the procedure addresses differ from the linked addresses by one constant: `entry.c` 0, `bgm_r2s.s` 256, `stream.c` 576. A non-constant offset would reject the pairing.
- Procedure sizes equal symbol sizes, 211 of 211.
- The debug frame size equals the `addiu sp,sp,-N` in the procedure's own prologue for 210 of 211. The exception is `_BgmRaw2Spu`, an assembly routine with no debug frame.

The `.mdebug` content is small: 211 procedures (209 in `stream.c`), 216 end markers, 10 statics, 5 files, 5 labels. It has **no parameters, local variables, struct or member types**, so no types are recovered from it.

## Import names

All 71 import stubs have a symbol at the stub address. Of the SDK catalog's 32 candidate names for STREAM, **32 are confirmed and 0 contradicted**; 39 stubs that the exact-version catalog left unnamed now have names (libsd 261 and others). This is a measured accuracy of the catalog's exact-version rule on this module, nothing more: whether index-to-name mappings hold across other SDK versions is untested (the pinned catalog has only one library with two versions). All 102 functions of STREAM that call imports now carry named imports, against 31 before.

## Annotation

`tools/iop_function_profile.py` joins exact relocation sites (jump relocations to stubs, `lui`/`addiu` pairs to strings) with the module's tables; `tools/iop_annotation_plan.py` writes plate comments: calls, every matching role tag, strings, export slot, debug file and frame. `AnnotateFunctionsV2.java` is the V1 guard with the executable hash and language passed as pinned arguments. STREAM: 211 comments, 0 renames, reconciliation 8 of 8. LGDEV: 114 comments, 0 renames, 8 of 8. The pseudocode is identical once comments are stripped.

A first STREAM run was **rejected** by the guard: the plan wanted to rename a function that already had a real name. The plan now renames only default-named functions, and the run was repeated on a fresh project copy. STREAM ends with no renames: its names were already original.

## Role tags and Jev

A first rule picked one role per function by priority. Jev's batch classifier, given the same call lists on a stratified sample of 46, agreed with the rules on 27 of its 30 auto-accepted answers, and the disagreements were almost all mixed-import functions where Jev declined to pick one role and the rule's priority order had forced one. The plan therefore lists every matching tag. Jev's sample is 46 of 143 import-calling functions; the other batches were not run. See `jev-receipts.json` and `jev-role-crosscheck-sample.json`.

## Not established

STREAM's RPC thread registers `ProcessEECommand` (id `0x12345`), which handles one command. The main EE request path polls a shared `StreamBuffer` of 0x224-byte records. No EE call site was mapped to an IOP handler name, and no type was recovered for the shared record. Only 6 STREAM functions and 1 LGDEV function reference strings by relocation, so string-derived names are rare. LGDEV has no names in its symbol table; none are claimed. The nine stock Sony modules were not annotated.

## Review record

`jev_gate` on the change returned **escalate** (safe_to_apply 0.17; limiting rubric: test gap; composite 0.56). Six of seven claim checks verified. The seventh, a deliberate overclaim that the IOP work recovers variable and struct types, was contradicted at 0.99, which is the correct answer and the other reason for the escalation. The guard claim went to review (0.68).

Negative controls for the V2 guard's new arguments, each on a fresh project copy: `negative-control-wrong-exe-pin.json` (rejected, "pinned executable identity mismatch") and `negative-control-wrong-language.json` (rejected, "program language differs from the pinned language"). The real rename-target rejection described above is the third. The drift checks have no deliberately failing run.
