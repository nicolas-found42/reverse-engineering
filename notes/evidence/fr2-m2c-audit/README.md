# m2c explicit-context pointer-scale probe

This durable audit package uses only `synthetic.s`, a game-independent MIPS loop. It contains no game assembly or game decompilation output.

The test asks whether m2c `--context` type declarations repair the pointer scale produced after `lq`/`sq`-based pointer inference. It does not. An explicit `s128 *` function prototype produces output byte-for-byte identical to the no-context baseline: `var_5 += 0x10` and `var_4 += 0x10` remain on `s128 *`, so standard C pointer arithmetic advances 16 vector elements (256 bytes for 16-byte `s128`).

An explicit `unsigned char *` prototype makes the increments advance 16 bytes, but the output then reads and writes through `u8 *` (`temp_2 = *var_5; *var_4 = temp_2;`). That is a one-byte memory access, not a full 128-bit `lq`/`sq`; it is not a valid repair. The preserved Jev review disposition for this claim is in `jev-context-verification.json`; exact evidence is also visible directly in the generated `byte-pointer/stdout.c`.

The three comparison artifacts are `baseline.c`, `vector-pointer/stdout.c`, and `byte-pointer/stdout.c`. Context inputs, exact argument vectors, standard output, and standard error are stored per case. `metadata.json` records the input/output SHA-256 values and pinned m2c commit.

To reproduce against the pinned m2c checkout in this workspace, from the repository root run:

```sh
.scratch/mesh/codex-root/recomp-venv/bin/python \
  .scratch/mesh/codex-root/m2c/m2c.py \
  -t mipsee-gcc-c --no-cache --valid-syntax --stop-on-error \
  --context notes/evidence/fr2-m2c-audit/vector-pointer/context.h \
  notes/evidence/fr2-m2c-audit/synthetic.s

.scratch/mesh/codex-root/recomp-venv/bin/python \
  .scratch/mesh/codex-root/m2c/m2c.py \
  -t mipsee-gcc-c --no-cache --valid-syntax --stop-on-error \
  --context notes/evidence/fr2-m2c-audit/byte-pointer/context.h \
  notes/evidence/fr2-m2c-audit/synthetic.s
```

The m2c working tree remained pristine at the pinned commit. The existing pointer-scale audit at `.scratch/mesh/codex-root/m2c-pointer-audit/README.md` documents the late-pointer-typing path and the standalone C pointer arithmetic control. This test establishes only what these context declarations do to m2c's synthetic output; it does not claim a general m2c context limitation for every input.
