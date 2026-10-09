# Confirmed bounded shapes

This document indexes measured examples. It is not a library of assumed PS2
semantics, original-function names or independent confirmation from several tools.

## Database-id sentinel accessor

Corpus: PAL SLES-517.05, SHA-256
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`.
Range: `.text[0x001d1800, 0x001d183c)`, 60 bytes. The bounded behavior checks a
loaded/unloaded database-id sentinel, returns the loaded value or calls an error
helper outside that owned range. The global at `0x00290ac4` remains unresolved.

[The first-unit evidence](../notes/evidence/fr2-first-unit/README.md) records the
hand-written source, static callers, compiler recipe, exact-byte result and real
branch/placement negative controls. Reproduce the portable boundary controls:

```sh
tools/check.sh test_matching_ranges test_matching test_compiler_probe_recipe
```

Those tests check the bounded contract; they do not rerun the archived retail
compiler result. The real source-build command is in the evidence note.

## gp context and small-data accesses

The [gp-context evidence](../notes/evidence/fr2-gp-context/README.md) records
`gp = 0x295d70` from the ELF `.reginfo` value and the entry setup, with guarded
application and a wrong-pin negative control. The
[small-data evidence](../notes/evidence/fr2-small-data-types/README.md) records
access-width/sign/FPU constraints and the address-taken/mixed-width exclusions.
The main-thread observation does not prove that every thread uses that gp value
or recover original names. Reproduce the portable guard and planner controls:

```sh
tools/check.sh test_gp_context_check test_small_data_check test_small_data_plan
```

The original corpus measurement and guarded transaction commands remain in
those evidence bundles; the synthetic tests do not rerun their archived counts.

## Shapes still unresolved

No MMI/COP2, VIF-to-VU handoff, general prologue/epilogue or inferred original
function shape is promoted into this index without a corpus address, committed
measurement, reproduction command and falsifier. gp context and access-width
terminology are defined in the [glossary](../GLOSSARY.md); they do not alone prove
a global's original type or ownership.
