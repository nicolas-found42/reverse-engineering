# EE candidate `001fbfb8` reconciliation

A fresh isolated project accepted one provisional candidate. The CFG body is 276 bytes (`001fbfb8–001fc0cb`). The zero word at `001fc0cc` is beyond reachable control flow and remains unowned; the 280-byte adjacent interval remains a boundary hypothesis. The candidate has no saved Ghidra incoming reference. Its raw neighbor call at `001fc100` in the adjacent undefined span targets this seed, but is not a saved Ghidra xref.

After saving and reopening, the export contains 3,839 generated functions and zero failures. The candidate body/name/manifest and evidence inventory match the single-seed result. All 3,838 previous entries, body ranges, instruction bytes, references, and generated C hashes are unchanged. Hashes and checks appear in [001fbfb8-reconciliation.json](001fbfb8-reconciliation.json).

This proves only a bounded CFG candidate was added and exported. It does not establish original identity, semantics, runtime reachability, or that adjacent code is a source-level function boundary.
