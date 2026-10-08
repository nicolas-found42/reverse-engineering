# misc3d database-id cell: game-owned NOBITS layout and bounded ABI

Decided under issue #24: attribute `.sbss[0x00290ac4,0x00290ac8)` to the
misc3d game state. The cell is a signed four-byte value, with minimum alignment
four. It has no file payload. Rebuild its **layout**, and count zero matching
file bytes. Preserve ADR-0005's independently matched 60-byte accessor.
No ownership of the shared helper or surrounding misc3d code follows from this
decision. The complete-image partition remains conservative until a fresh
aggregate consumes this additional layout receipt.

The cell's local name `misc3d_db_id` is inferred. Direct GP accesses use
`gp = 0x00295d70`, displacement `-0x52ac`. The corpus-wide aligned executable
word scan finds 16 loads/stores, including three stores. Their sites, widths,
register numbers, saved owners and word hashes are retained in
[the observation](../../notes/evidence/fr2-misc3d-cell/observation.json).
The reproducing commands and search limits are in
[the evidence recipe](../../notes/evidence/fr2-misc3d-cell/README.md).
This is a bounded direct-access scan, not an exhaustive computed-alias analysis.

Startup clears the containing BSS range. Reset at `0x001d17a8` writes `-1`
at `0x001d17b0`; caller `0x001ccbd8` calls reset before loading the database.
The loader at `0x001d1408` stores the result of `0x0011ed90` at `0x001d1460`
in another call's delay slot. Release at `0x001d17c8` tests the sentinel,
passes the loaded value to `0x00120aa8`, then writes `-1` at `0x001d17ec`.
No saved direct caller of release is recorded. These instructions establish
static lifetime paths, not runtime ordering, successful initialization, or
thread safety. An initialized `int = -1` definition would contradict the
NOBITS/startup evidence.

The accessor takes no consumed input argument, loads a signed word and returns
it in V0 on the loaded path. Its saved callers pass V0 as A0 to database
consumers. On `-1` it calls `0x00105888` with A0 = source path, A1 = line 188
(set in the delay slot), and A2 = diagnostic/format pointer. The helper saves
additional general and floating argument registers and passes its save area to
a formatting call: a variadic interpretation is inferred. Its saved body has
no return and ends in a backward loop after reporting/cleanup calls. No error
return value is established. The accessor's existing `int report_error`
declaration is retained as the byte-matching compilation surrogate; it is not
evidence that the helper returns an integer. This declaration does not promise
that a call returns. The helper's original identifier and declared return type
remain unknown. Its separately mapped `modules4/system/ps2/asyncf.c` code is
outside the game-owned range.

The compiled cell object must contain one uninitialized common symbol, size
four, alignment four, and no allocated payload except ELF register metadata.
The linked section must have the recorded address/size, writable allocated
NOBITS storage and compatible alignment. Both checks are required: the linker
must not hide an initializer by discarding its bytes in a NOLOAD section.
The exploratory ee-gcc2.96/GNU binutils 2.40 profile remains an AC05-incomplete
profile, not an identification of the retail toolchain.

The next EE group is reset/release and the sibling accessors, starting from
the measured unowned load at `0x001d1840` preceding saved entry `0x001d1844`.
It is tracked in [#35](https://github.com/nicolas-found42/reverse-engineering/issues/35),
a child of #23 and a blocking dependency of #24.
The loader's saved body is noncontiguous and is not attributed by its envelope.
These are unresolved reconstruction dependencies; #24 stays incomplete until
its required dependency dispositions are established. A positive layout child
does not override that task-level status or complete parent #23.

**Falsifier:** a contradictory writer/alias, source attribution, access width,
or layout for any byte in this cell revokes the local ownership/layout decision.
A returning helper path or a contradictory caller invalidates the associated
ABI inference. Such evidence must be reconciled before broader acceptance.
