# Declared load-image accounting

Reproduce the structural inventory from a clean checkout with declared local
inputs:

```sh
python3 tools/matching_ranges.py corpus games/ford-racing-2 --output .scratch/evidence/range-accounting
tools/check.sh test_matching_ranges
```

The corpus command reuses the corpus identity gate and pins all 24 IOP module
bytes against the retained IRX receipt. It partitions every EE/IOP PT_LOAD image
at allocated-section and initialized/zero-fill boundaries. Unnamed gaps stay
visible. Overlapping images or sections, section/file mapping drift, and
initialized bytes attributed to NOBITS fail. Allocated sections outside load
images are retained separately rather than silently omitted. The eight VU
program identities are also retained; their encoding and interfaces have their
own verifier.

The corpus inventory applies exactly one measured ADR-0005 range split:
`.text[0x001d1800, 0x001d183c)` is recorded as game-owned when the retail EE
bytes and the ADR-0005/source-map/saved-function evidence match their pinned
identities. The current reconstruction source identity is recorded separately;
changing candidate source does not erase corpus ownership. Every other
initialized and zero-fill range remains unresolved. The structural child
keeps `matched_bytes` at zero; only the aggregate can credit the 60-byte span
after checking its fresh compiler child receipt against the expected source,
output bytes, and ownership evidence. No other game behavior is implied. IOP
addresses remain relative to the link image.

`file` accepts synthetic fixtures at the same inventory boundary, marks their
authority as `structural_file_inventory`, and cannot confer corpus ownership
or completion.
The fixture controls exercise initialized bytes, zero-fill, unnamed gaps,
missing prerequisites, image/section overlap, and section/file mapping drift.
