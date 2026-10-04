# EE candidate `001fc0d0` reconciliation

A fresh copy of the combined Ghidra project received the reviewed dispatch overrides and provisional leaf, then one `candidate_ee_001fc0d0` seed. The single candidate transaction created a 68-byte CFG body (`001fc0d0–001fc113`). The raw zero word at `001fc114` falls after the return delay slot and remains unowned; the larger 72-byte span is only a boundary hypothesis.

The project was saved, reopened, and exported. The reopened manifest contains 3,839 generated functions with zero failures; the evidence inventory and listing coverage also report 3,839. The candidate JSON, reopened project inventory, generated C manifest, and C-file hash agree. All prior entries, names, body ranges, and instruction address/text/bytes remain unchanged. The only prior C-file change is `001fbe48.c`: its three known calls now resolve from `func_0x001fc0d0` to `candidate_ee_001fc0d0`. The exact changed lines and reference changes appear in [001fc0d0-reconciliation-check02.json](001fc0d0-reconciliation-check02.json).

Exact input, window, script, and output hashes are recorded in that result. The candidate is provisional: identity, behavior, runtime reachability, and whole-game completeness remain unproved. Earlier failed attempts and a flawed first reconciliation check were retained without replacing their results.
