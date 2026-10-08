# Archive-derived asset consumer contracts

`tools/verify_asset_contracts.py` derives archive extensions and raw/zlib storage encodings from `FILES.HDR` and `FILES.DAT`. Those encodings are inventory facts; they do not count as logical body or format profiles.

The tool reads a fixed repository registry, `notes/asset-loader-registry.json`. Its SHA-256 is pinned in the checker. The registry pins the PAL corpus identity, required logical profiles, and each candidate loader/reference association by contract ID, asset type, function/address, claim ID, exact source-file SHA-256, and a concrete text anchor. The caller manifest may name only those fixed contracts and binding IDs. It cannot add a loader, change a binding, narrow the contract list, mark a candidate complete, or supply a replacement registry. A changed evidence file fails even when the old function token remains in the file.

The three model associations are explicitly `candidate_documentation`; they are not accepted semantic proof. Registry profiles separately retain unresolved geometry-body, PTG-body, texture mip/palette, audio playback, and other asset grammars. The completion gate remains incomplete while any profile is candidate or unresolved. A covered header or a successful independent structure verifier cannot clear a body or consumer blocker.

Run against the local PAL corpus:

```sh
python3 tools/verify_asset_contracts.py archive games/ford-racing-2/extracted/FILES.HDR games/ford-racing-2/extracted/FILES.DAT --output .scratch/evidence/asset-contracts
```

The retained [local corpus result](local-corpus-result.json) is **incomplete**. It inventories 15 archive extensions and reports all logical profile blockers; the archive alone does not pass the fixed PAL corpus identity unless `corpus_identity` matches the pinned executable, disc, header, and data hashes. UI (`.ui`), text/data (`.dat`), and configuration (`.cfg`) remain explicit unresolved contracts. No meanings are assigned to unclassified `.db`, `.mbf`, `.old`, or `.sbf` families.

The checker validates registry integrity, evidence-file identities, profile identity, and manifest consistency. It does not independently validate asset semantics, execute loaders, or establish runtime behavior. The [validation receipt](validation.json) records the focused and full-suite checks.
