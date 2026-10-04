# PS2 IRX catalog review notes

Review scope: `tools/ps2_irx_catalog.py`, `tools/test_ps2_irx_catalog.py`, and the root-generated `.scratch/mesh/codex-root/iop-api-annotations-01.json`.

The focused test command passed seven tests at review time. Root later narrowed decimal literals to `0|[1-9][0-9]{0,2}` and reported eight focused tests passing. The prior hex-literal finding is retained as an audit trail: the only pinned SDK `exports.tab` header using hex was in `iop/security/secrman/src/exports.tab`, which also contains `#ifdef BUILDING_ARCADE_SECRMAN`; catalog generation excludes the whole file as preprocessor-dependent. Supporting hex alone would not admit that file under the stated policy.

Output/provenance review: the generated annotation corpus declares PS2SDK commit `ac92a9f657d2e531dd8f060250b07f2a5ac6dea5`, catalog digest `649c4dc1c9eaa3e663c89a329c3b839a1542150f54fe52403da4c2911ea11bf9`, 24 modules, 77 parsed tables, 14 excluded source files, and 748 import links (436 candidate names, 312 unresolved). Per-module rows carry source path, IRX SHA-256, module name, SDK commit, exact library/version/index, stub text offset, matching catalog source paths, and `original_identity_verified: false`. The root corpus limits candidate names to public SDK table candidates and explicitly disclaims original identity, runtime linking, and implementation semantics.

The CLI result generated directly by `annotate_irx` carries the IRX SHA-256 and module name. `main()` adds the SDK commit and per-file catalog provenance: each of 83 tracked `exports.tab` paths, byte count, SHA-256, and exclusions. It does not emit a single `catalog_sha256` field, but the source inventory plus pinned commit records the inputs. No incorrect annotation or provenance loss was observed. Existing concerns are coverage/documentation only; no source changes made by this audit.

The Jev JSON files in this directory retain the structured result fields, distributions, confidence/actions, claims, and usage summaries from the review calls. They are audit summaries transcribed from tool outputs, not signed provider envelopes.
