# External schemas

[recomp-v1.json](recomp-v1.json) is the complete JSON content of the
[recomp.fyi v1 schema](https://recomp.fyi/schema/v1.json), retrieved 2026-10-08.
The source attributes it to recomp.board under **CC BY 4.0**. Web display line
prefixes were removed; JSON formatting differs from the HTTP response. No
schema rules were changed. The schema is a separately licensed resource, not
MIT-licensed project code.

`repository_hygiene.py` validates the schema keywords this version uses and
fails if an unknown validation keyword appears. It performs no remote lookup
in CI. Discovery metadata carries the published schema URL in `$schema`.
