# FR2 compiler probe

`tools/compiler_probe.py` compiles one source file with each candidate described
in a JSON manifest, extracts `.text.<symbol>` with the candidate's GNU `objcopy`,
and compares the function bytes through `matching_diff.compare`. It writes an
immutable JSON receipt under `.scratch/evidence/compiler-probe/` by default.
Each receipt records source/reference identities, candidate executable hashes,
argv, return codes, function hashes, and per-candidate gate verdicts.

The manifest has `source`, `symbol`, `reference`, and `candidates` fields. Each
candidate has an `id`, `compile` argv array, `objcopy` argv array, and optional
`flags` array. The reference must be an independently attributed retail function
range, and the source must be a reconstruction candidate for that same range.
The current corpus boundary inventory does not yet provide such a proven range
and function source pair, so this repository contains no FR2 compiler selection
receipt. A synthetic fixture only checks runner behavior.

Run the synthetic controls with:

```sh
tools/check.sh test_compiler_probe
```

The run status is `pass` only when exactly one candidate matches and every
candidate was executed. Any byte mismatch is `fail`; unavailable candidate
tools or missing function sections are `incomplete`. A unique match applies only
to the specific evidenced source, flags, and reference; it does not by itself
identify the game's original compiler.
