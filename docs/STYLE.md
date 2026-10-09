# Evidence and documentation style

Use the [glossary](../GLOSSARY.md) and accepted ADRs. Write what was measured,
which input it applies to, the exact reproduction command and the falsifier.
Separate independent observations from repeated views of the same source.

An evidence note should carry these parts:

- **Status:** pass, fail or incomplete, with the authority and limits of that result.
- **Established:** bounded claims supported by named inputs and measurements.
- **Not established:** unresolved questions and dependencies.
- **Reproduce:** exact commands, corpus/source/decision hashes and relevant revision.
- **Falsifier:** the observation or negative control that would invalidate the claim.

Use repository-relative links for portable documents. A private receipt path is
an external local dependency, not an artifact distributed with the repository.
Store structural hashes/offsets/counts; do not commit raw corpus bytes, dumps or
generated decompiler C/assembly. A missing index field remains missing.

“Matched” means exact game-owned bytes backed by the required fresh source-build
checks. A byte-identical mixed section, saved function, approximate reconstruction
or open-source substitute cannot increase that count. A 60/60 attributed fraction
is not a whole-game percentage. CI without the corpus checks retained bindings;
it does not repeat the retail compilation.

Generated navigation and progress files are regenerated together with
`python3 tools/repository_hygiene.py generate`. Their freshness check and tests
must fail on altered evidence, stale output and unsupported scope. Proposed
changes to a decision table need an evidence-backed pin update, not a new caller
argument to steer the gate.
