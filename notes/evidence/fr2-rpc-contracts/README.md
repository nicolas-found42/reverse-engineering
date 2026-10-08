# PAL EE-to-IOP handoff frontier and STREAM volume framing

Ticket #26 remains **incomplete**. This bounded child adds a reproducible
candidate inventory across all 24 pinned IOP modules and EE executable words,
and an executable STREAM command-0/channel-volume framing check. It grants no
matching-byte credit and no whole-protocol, audio-effect or runtime acceptance.

## Static binding and bounded record

The same-profile saved Ghidra exports provide these static observations. The
fixed raw identities and measured source ranges are committed in
`tools/rpc_profile.json`; the fresh command reads raw ELF bytes and rechecks
those identities/ranges and the named IOP handler symbols. Supplied historical
receipts cannot make the command pass.

| Binding | Observation | Evidence limit |
| --- | --- | --- |
| EE `0x00138188` | Candidate bind routine `0x001ed0f0`, service `0x12345`, client record `0x00359280`; polls its server field | Candidate SDK name, no observed registration |
| EE `0x00139658` | Candidate call routine `0x001ed2c0`, RPC command 0; EE send `0x00236440`, receive `0x00358380`, both `0x800` bytes; mode is caller supplied; callback `0x0013eac8` | Callback extent/behavior and full lifecycle unresolved |
| IOP `sce_adpcm_loop`, section offset `0xd494` | Registers service `0x12345`, handler `ProcessEECommand`, receive object `rpc_arg`, then RPC loop | Static call only, actual load base absent |
| IOP `ProcessEECommand`, offset `0xd410` | Command 0 routes to `AdpcmSetParam` at `0x11d44`; returns `aret` | Full reply fields not recovered |
| IOP symbol objects | `rpc_arg` and `aret` are each `0x800` bytes; `StreamBuffer` is 26,304 bytes (`48 * 0x224`) | Sizes and names are raw ELF symbol observations, not ownership proof |
| EE `0x00138330` and IOP `AdpcmSetParam` | Batch header is two little-endian halfwords: version 62, signed record count; each record is subcommand plus signed argument-halfword count followed by those halfwords | Unused transfer tail is opaque; other command arities unresolved |
| EE `0x0013c0c8` / IOP branch 2 | EE requires channel below 48, queues subcommand 2 with three halfwords; IOP branch calls `SOUND_SetChannelVolume` with those three halfwords and final argument 0 | Halfwords are channel and two volume inputs; no amplitude, scaling or audible-effect claim |

The EE owns the addresses of its static staging/send/reply buffers in the
static image. The IOP symbol objects are in its separate image. The transfer
is EE-to-IOP for the request and IOP-to-EE for the reply; the 2,048-byte lengths
agree with the IOP symbol sizes. The EE checks the client status before reuse;
its RPC mode is supplied by the caller. The IOP dispatcher can sleep when
`MS_IntrFlag` is set and later signals `gSem`. These are local synchronization
observations. The interrupt wakeup chain, callback, simultaneous callers,
actual ownership duration, and reply layout have not been established, so
AC15 and ticket criterion 2 do not pass in full.

The host decoder checks the supported volume record arity and channel bound;
it rejects out-of-transfer lengths, negative signed lengths/counts and wrong
static version. Structurally bounded other commands remain incomplete. A later
malformed volume record still fails even after an unknown record. An empty
batch is valid framing but cannot satisfy this volume child, so it is incomplete.
The opaque tail need not be zero: the EE caller transfers a fixed length even
when only part of the batch is used. These are reconstruction-side checks,
not a claim that the retail handler validates all hostile input.

## Reproduction

Use unchanged local inputs; no emulator or primary saved-project write occurs.
The local saved exports used to derive the binding are recorded with manifest
and selected function hashes in `source-evidence.json`. They are ignored
payloads, never public C/assembly. The current REA `open_binary` request for
STREAM failed with `unsupported ELF architecture`; the complete safe request
and error are retained in `rea-open-limit.json`. No native target was opened.
The local Ghidra exports remain the supported MIPS evidence route for this slice.

```sh
python3 tools/inventory_rpc_handoffs.py \
  /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted \
  --output .scratch/rpc-controls/inventory

tools/check.sh test_rpc_contracts

python3 - <<'PY'
from pathlib import Path
import struct
root = Path('.scratch/rpc-controls')
root.mkdir(parents=True, exist_ok=True)
controls = {
    'positive': (62, 2, 2, 3, 0, 120, 240, 2, 3, 47, 600, 700),
    'negative': (62, 1, 2, 4, 0, 120, 240, 0),
    'incomplete': (62, 1, 9, 2, 65535, 0),
}
for name, words in controls.items():
    (root / (name + '.bin')).write_bytes(
        struct.pack('<' + 'H' * len(words), *words).ljust(2048, b'\xa5'))
PY

python3 tools/check_rpc_contracts.py \
  --ee /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/SLES_517.05 \
  --stream /Users/Nicolas/Documents/github/hermes/reverse-engineering/games/ford-racing-2/extracted/IRX/STREAM.IRX \
  --packet .scratch/rpc-controls/positive.bin \
  --output .scratch/rpc-controls/positive
```

Replace `positive` in the packet/output paths with `negative` or `incomplete`
to reproduce exits 1 and 2; positive exits 0 for the **framing child only**.
Omit `--packet` for the absent-observation case (exit 2). Use the synthetic
positive packet as `--ee` and a nonexistent `--stream` for a known profile
mismatch (exit 1); the known EE contradiction wins over the absent handler.
Tests exercise these statuses through the public CLI and use ELF fixtures for
instruction-shaped inventory controls. No synthetic control is a retail RPC
observation. Positive receipt packet fields are synthetic and identified by hash.

The retained `inventory.json` is the full metadata-only candidate result:
127 EE direct bind/call-shaped words, 2,403 EE JALR-shaped words and 159 IOP
SIF-import-call-shaped words. These numbers are reproduced by the inventory
command above. All 24 module hashes match the prior export-recovery inventory.
Scanning aligned executable words does not prove valid decoded instructions or
reachability and can include embedded data. The raw numeric library versions
are preserved, including the sifcmd/sifman imports at version 257. Nothing
converts those imports into observed runtime registration or actual bases.

## Required frontier and next child

The complete handoff inventory is not derived yet. `inventory.json` retains
every candidate in this scan boundary and the named gaps; `parent_gaps` remains
nonempty in the volume check even when the child passes. Required remaining
work is service/client binding for the other EE candidates, IOP handler and
registration argument recovery, indirect/data-carried dispatch domains,
other STREAM subcommands, streaming shared records, DMA direction and length,
reply/callback layout and buffer ownership/lifetime. Absence from this bounded
scan is not proof that a protocol does not exist.

Next bounded child: recover the STREAM reply and completion callback at EE
`0x0013eac8`, join writes to IOP `aret` to EE reads of `0x00358380`, and establish
buffer reuse for blocking and asynchronous modes. Then cover the shared
`StreamBuffer` request/status protocol and individual sound/upload records in
coordination with #27. The volume framing child does not close #26 or #16.

Jev selection (`jev-selection.json`) selected volume but reported existence
**partial**, 0.62; its winner probability 1.0 is not proof of a full contract.
The bounded interpretation is retained. Final semantic claim verification and
patch gate retain complete safe requests/results separately. Exact lengths,
hashes, static compatibility and pass/fail/incomplete remain enforced by code.


The one-shot Jev patch gate escalated (safe-to-apply 0.41, limiting test-gap
confidence); it was not retried. The root orchestration agent independently
reviewed the handwritten checks, tests, profile and bounded claims. That review
accepted the framing/candidate scope and requested packet identity in failed
and incomplete receipts plus hashes for directly imported source dependencies.
Both traceability repairs were applied and rechecked: ten focused tests pass,
and all six CLI control dispositions retain the expected packet/source
identities. `independent-review.json` records that disposition. The gate's
original nine-test/671-test request remains a historical pre-repair observation.
