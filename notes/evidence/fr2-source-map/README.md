# Source map and annotation of saved functions

The executable names its own source files. Many functions pass a `__FILE__` string and a `__LINE__` value to a report routine. `tools/verify_source_map.py` reads these from the saved export and tests two layout predictions. A real source map must satisfy both.

## Result (export of 5,454 functions)

- 146 `.c` and `.cpp` units and 10 headers are referenced from code. 323 functions reference a unit path directly (455 count headers too).
- No two units have overlapping function address ranges in one memory block (0 of 146).
- Line numbers rise with address: 27 inversions in 144 consecutive function pairs (18.75%). A shuffle of the same numbers gives 47.8% (200 trials, seed 1).
- 188 more functions use only other strings. They are attributed to the unit whose string block holds those strings. On the functions that also name a path directly, this agrees for 267 of 288 decisive cases (92.7%); 24 tie.
- The EE kernel library stamp is `PsIIlibkernl2550` and the other Sony libraries are 2500 to 2550 (`sdk-stamps-result.json`). Stamps date the SDK libraries. They do not identify the game compiler.
- Only two IOP modules lack a Sony stamp, `STREAM.IRX` and `LGDEV.IRX`. They are the candidates for game or third-party IOP code. The other nine stamped files are stock Sony modules.

## Annotation of the Ghidra project

One guarded transaction (`tools/ghidra/experimental/AnnotateFunctionsV1.java`) on a byte-identical copy of the 5,454-function project added 665 plate comments and 112 renames. A rename needs a default name (`FUN_` or the batch guard's `candidate_ee_`). The 112 renames are syscall stubs that have exactly one meaningful SDK name. Each carries the prefix `ps2sdk_`. 25 stubs share an SDK name and stay unrenamed. Each comment says how the evidence was found and that it is not proof.

`annotation-reconciliation.json` passes 8 of 8 checks. All functions keep size, blocks and instruction bytes. Names change only as planned. The pseudocode of all 5,454 functions is identical once comments are removed, planned names are mapped back and whitespace is removed. The first comparison run found one function that differed only by a line re-wrap around a longer name; the normalization was widened and the same exports were compared again.

| Count | Before | After |
| --- | ---: | ---: |
| Functions with a non-default name | 1,606 | 1,645 |
| `undefined` type tokens | 23,229 | 23,229 |
| Unresolved `$gp` tokens | 241 | 241 |
| Call-site arity mismatches | 3,944 | 3,943 |

The annotation makes the code easier to read and to attribute. It does not change types.

## Jev

Jev verified two claims and contradicted the overclaim that the comments and names prove original names (0.98). It contradicted a third claim at 0.61 (`review`): that every renamed function has the prefix and the caveat comment. A direct check of plan and export shows 112 of 112 do. Both results stay in `jev-verify-result.json`. An earlier Jev review of the guard change that let `syscall` through escalated; see batch g2.

## Not established

A reference or a string position shows that code mentions or sits near a path. It does not show who wrote the function or in which file. The syscall names come from the open PS2SDK table. The game links Sony SDK 2.5.5 libraries, and numbers can differ. No original name, identity or behavior is claimed.
