"""Decode EE bind/call and IOP registration arguments from raw instruction words.

Static decoder only: tracks lui/ori/addiu/move constants in a bounded window
before each site and through its delay slot. Anything loaded from memory or computed otherwise stays
unresolved; the join reports those explicitly.
"""

import struct

from ps2_executables import parse_elf

_MASK = 0xFFFFFFFF
# Fixed byte scope: docs/adr/0007-static-rpc-argument-inference.md
_ARGUMENT_LOOKBACK_BYTES = 600


def _text(data: bytes):
    elf = parse_elf(data)
    sections = [s for s in elf["sections"] if s.get("name") == ".text"]
    if len(sections) != 1:
        raise ValueError("fixture must carry exactly one .text section")
    return sections[0]


def _signed_half(word: int) -> int:
    return struct.unpack(">h", struct.pack(">H", word & 0xFFFF))[0]


def jal_target(at: int, word: int) -> int | None:
    """MIPS JAL target for one instruction word, or None when not a JAL."""
    if word >> 26 != 3:
        return None
    return ((at + 4) & 0xF0000000) | ((word & 0x3FFFFFF) << 2)


def _regs_before_site(data: bytes, site: int) -> dict:
    """Trace a validated JAL plus delay slot within the fixed byte scope."""
    section = _text(data)
    base, offset, size = section["address"], section["offset"], section["size"]
    at = site - base
    if (
        site % 4
        or base % 4
        or at < 0
        or at + 8 > size
        or offset < 0
        or offset + size > len(data)
    ):
        return {}
    raw = data[offset : offset + size]
    if jal_target(site, struct.unpack_from("<I", raw, at)[0]) is None:
        return {}
    return _trace(raw, max(0, at - _ARGUMENT_LOOKBACK_BYTES), at + 8)


def _trace(text: bytes, start: int, end: int) -> dict:
    """Trace linear argument setup including the target call's delay slot.

    The target JAL is at end-8. Earlier calls clobber caller-saved registers
    after their delay slot; ambiguous transfers make this interval unresolved.
    """
    regs: dict[int, int] = {0: 0}
    clobber_after = None
    for offset in range(start, end, 4):
        word = struct.unpack_from("<I", text, offset)[0]
        op = word >> 26
        rs, rt, rd = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
        funct = word & 63
        if op == 3:
            if clobber_after is not None or offset == end - 4:
                return {}
            regs.pop(31, None)
            if offset != end - 8:
                clobber_after = offset + 4
        elif op in (1, 2, 4, 5, 6, 7, 20, 21, 22, 23):
            return {}
        elif op == 15:
            regs[rt] = ((word & 0xFFFF) << 16) & _MASK
        elif op == 13:
            if rs in regs:
                regs[rt] = (regs[rs] | (word & 0xFFFF)) & _MASK
            else:
                regs.pop(rt, None)
        elif op == 9:
            if rs in regs:
                regs[rt] = (regs[rs] + _signed_half(word)) & _MASK
            else:
                regs.pop(rt, None)
        elif op == 0:
            if funct in (8, 9, 12, 13, 48, 49, 50, 51, 52, 54):
                return {}
            if funct in (33, 45) and rt == 0 and rs in regs:
                regs[rd] = regs[rs]
            elif funct in (
                0,
                2,
                3,
                4,
                6,
                7,
                10,
                11,
                16,
                18,
                20,
                22,
                23,
                24,
                25,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                42,
                43,
                44,
                45,
                46,
                47,
                56,
                58,
                59,
                60,
                62,
                63,
            ):
                # R5900 MULT/MULTU can also write the encoded rd.
                regs.pop(rd, None)
            elif funct not in (15, 17, 19, 26, 27, 41):
                return {}
        elif op in (
            8,
            10,
            11,
            12,
            14,
            24,
            25,
            26,
            27,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            48,
            52,
            55,
            56,
            60,
        ):
            regs.pop(rt, None)
        elif op in (16, 17, 18):
            if rs == 8:  # coprocessor conditional branch
                return {}
            if rs in (0, 1, 2):  # transfers from coprocessor to GPR
                regs.pop(rt, None)
            elif rs not in (4, 5, 6):
                return {}
        elif op not in (40, 41, 42, 43, 44, 45, 46, 47, 49, 53, 57, 61, 63):
            # Unclassified extensions (including R5900 MMI) may write GPRs.
            return {}
        regs[0] = 0
        if clobber_after == offset:
            for register in (*range(1, 16), 24, 25, 26, 27, 28, 31):
                regs.pop(register, None)
            clobber_after = None
    return regs


def decode_bind_sites(data: bytes, site: int) -> list[dict]:
    """Decode one EE bind-candidate JAL site into client record + service id."""
    regs = _regs_before_site(data, site)
    record, service = regs.get(4), regs.get(5)
    if not isinstance(record, int) or not isinstance(service, int):
        return [
            {
                "site": site,
                "client_record": None,
                "service_id": None,
                "status": "unresolved",
            }
        ]
    return [{"site": site, "client_record": record, "service_id": service}]


def decode_call_sites(data: bytes, site: int) -> list[dict]:
    """Decode one EE call-candidate JAL site into command + buffer arguments."""
    regs = _regs_before_site(data, site)
    record, command = regs.get(4), regs.get(5)
    send = {"address": regs.get(7), "bytes": regs.get(8)}
    receive = {"address": regs.get(9), "bytes": regs.get(10)}
    callback = regs.get(11)
    row = {
        "site": site,
        "client_record": record,
        "command": command,
        "send": send,
        "receive": receive,
        "callback": callback,
    }
    if not isinstance(record, int) or not isinstance(command, int):
        row["status"] = "unresolved"
    return [row]


def decode_register_sites(data: bytes, site: int) -> list[dict]:
    """Decode one IOP register-candidate JAL site into service + handler + queue arguments."""
    regs = _regs_before_site(data, site)
    service, handler, queue = regs.get(5), regs.get(6), regs.get(7)
    row = {"site": site, "service_id": service, "handler": handler, "queue": queue}
    if not isinstance(service, int) or not isinstance(handler, int):
        row["status"] = "unresolved"
    return [row]


def join_handoffs(
    binds: list[dict], calls: list[dict], registers: list[dict]
) -> list[dict]:
    """Join EE bind/call groups to IOP registrations by service id.

    Each returned handoff binds one EE caller group to at most one IOP
    registration; a name-only or unbound group stays incomplete and a group
    whose handler address carries no symbol binding stays unresolved. Actual
    load bases and registration order stay unobserved.
    """
    by_service: dict[int, list[dict]] = {}
    for reg in registers:
        service = reg.get("service_id")
        if isinstance(service, int):
            by_service.setdefault(service, []).append(reg)
    handoffs = []
    for bind in binds:
        service = bind.get("service_id")
        record = bind.get("client_record")
        group = [
            c
            for c in calls
            if c.get("client_record") == record and not isinstance(c.get("status"), str)
        ]
        row: dict = {
            "service_id": service,
            "client_record": record,
            "bind_site": bind.get("site"),
            "call_sites": sorted(
                c.get("site") for c in group if isinstance(c.get("site"), int)
            ),
            "call_candidates": sorted(group, key=lambda call: call.get("site", 0)),
            "commands": sorted(
                {c.get("command") for c in group if isinstance(c.get("command"), int)}
            ),
        }
        candidates = by_service.get(service, []) if isinstance(service, int) else []
        candidates = sorted(
            candidates,
            key=lambda reg: (
                reg.get("module", ""),
                reg.get("site", 0),
                repr(reg.get("handler")),
                repr(reg.get("queue")),
            ),
        )
        reg = candidates[0] if candidates else None
        if candidates:
            row["registration_candidates"] = candidates
        identities = {
            (r.get("module"), r.get("handler"), r.get("queue")) for r in candidates
        }
        if reg is None:
            row["status"] = "incomplete"
            row["reason"] = "no IOP registration binds this service id"
        elif len(identities) > 1:
            row["status"] = "unresolved"
            row["reason"] = (
                "conflicting IOP registration candidates bind this service id"
            )
        elif record is None or not group:
            row["status"] = "incomplete"
            row["reason"] = "EE caller group is missing handler/state binding"
            row["register_site"] = reg.get("site")
        elif (
            not isinstance(reg.get("handler"), int)
            or not isinstance(reg.get("queue"), int)
            or any(
                not isinstance(call.get(direction, {}).get(field), int)
                for call in group
                for direction in ("send", "receive")
                for field in ("address", "bytes")
            )
        ):
            row["status"] = "incomplete"
            row["reason"] = (
                "registration queue or shared transfer buffer binding is unresolved"
            )
            row["register_site"] = reg.get("site")
        else:
            row["register_site"] = reg.get("site")
            row["module"] = reg.get("module")
            row["handler"] = reg.get("handler")
            row["queue"] = reg.get("queue")
            row["status"] = "bound"
        handoffs.append(row)
    return handoffs
