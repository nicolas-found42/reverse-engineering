# EE candidate `001fc118` reconciliation

A fresh isolated project accepted one provisional candidate. Its CFG body is 348 bytes (`001fc118–001fc273`), followed by an unreachable zero word at `001fc274` left unowned. The surrounding 352-byte interval is only a maximum boundary hypothesis. A raw JAL at `001fc0f0` in the adjacent undefined span targets this candidate; it is not a saved Ghidra incoming reference.

After saving and reopening, the project exports 3,839 generated functions and zero failures. The candidate body/name, evidence inventory, and generated C manifest agree. All previous function bodies, instruction bytes, reference lists, and C hashes are unchanged. Details and output pins are in [001fc118-reconciliation.json](001fc118-reconciliation.json).

The result establishes one bounded CFG candidate and its reopened export only. It does not establish identity, full source boundary, semantics, or runtime reachability.
