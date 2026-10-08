# Archive-derived asset consumer contracts

`tools/verify_asset_contracts.py` derives its file-family denominator and raw/zlib storage variants from the archive itself. The manifest in `notes/asset-consumer-contracts.json` provides one explicit contract disposition for each observed extension. A contract records measured bounds, field effects, transformations, allocation/lifetime, handoffs, and unknowns; `complete` and `partial` claims must cite loader evidence whose function identifier appears in the cited repository note. Every observed storage variant must be marked `covered` or `unresolved`; undeclared families, unbound claims, and invented variants fail. A `complete` claim also fails if any consumer field remains marked unresolved or the `unknowns` list is nonempty, so a covered header cannot hide an unparsed body.

Run against the local PAL corpus:

```sh
python3 tools/verify_asset_contracts.py archive games/ford-racing-2/extracted/FILES.HDR games/ford-racing-2/extracted/FILES.DAT --output .scratch/evidence/asset-contracts
```

The retained [local corpus result](local-corpus-result.json) is **incomplete**, as expected: it found 15 archive extensions, and the model contract is partial while the other consumer contracts remain unresolved. The catalog names the model, geometry, texture-library, PTG, audio bank/music, UI, text/data, and configuration grammars explicitly. The model note binds `FUN_00123908`, `FUN_0011ed90`, and texture upload consumer `00222358` to existing loader/reference evidence. Structural measurements from existing audio and PTG verifiers are cited as structure evidence and do not pass as executable consumer evidence. In particular, no meanings are assigned to the unclassified `.dat`, `.db`, `.mbf`, `.old`, or `.sbf` families, and UI, configuration, text/data, audio, PTG, model geometry, texture mip, and lifetime gaps remain visible.

The checker is an archive inventory and evidence-binding gate. It does not validate asset semantics, execute loaders, or establish runtime behavior. The [validation receipt](validation.json) records the focused and whole-suite results and the local ignored prerequisites used by the isolated worktree.
