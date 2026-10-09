# Static RPC argument inference scope

The RPC handoff inventory uses a fixed 600-byte lookback within the unique
`.text` section before each aligned JAL candidate. This is a byte count, not
an instruction count. The scope belongs to the repository and public decoder
callers cannot override it. The target JAL and its complete delay slot must
both lie within the section and file bounds; malformed candidate locations
remain unresolved.

The decoder includes the target call's delay-slot argument writes. It tracks
only the documented constant-building instructions (LUI, ORI, ADDIU and
ADDU/DADDU moves); unsupported register writers invalidate their destinations.
Earlier calls invalidate caller-saved state after their own delay slots.
Branches, unmodeled transfers/traps and unclassified extensions leave the
interval unresolved instead of inventing a reachable instruction sequence.
The zero register always holds zero.

These rules establish bounded static candidates, not observed execution,
registration order, ownership duration or synchronization. A missing or
unresolved binding leaves the parent RPC inventory incomplete and gives no
new matched-byte credit. Conflicting registration candidates stay unresolved
and are retained in deterministic order. A known handler cannot fill gaps in
the queue or send/reply addresses and sizes; only complete static candidates
can be bound. The fixed STREAM contract additionally requires the recorded
transfer size for both directions; a different size remains unresolved.

Reproduce the public report, decoder and CLI controls with:

```sh
bash tools/check.sh test_rpc_handoff_inventory
```
