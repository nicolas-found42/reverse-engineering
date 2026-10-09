"""Decode EE bind/call and IOP registration arguments from raw instruction words.

Static decoder only: tracks lui/ori/addiu/move constants in a bounded window
before each site. Anything loaded from memory or computed otherwise stays
unresolved; the join reports those explicitly.
"""

import struct

from ps2_executables import parse_elf

_MASK = 0xFFFFFFFF


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


def _regs_before_site(data: bytes, site: int, *, window: int = 600) -> dict:
    """Constant registers traced over the bounded window before one JAL site.

    window is default-only (600 words); no caller tunes it, so nothing is pinned.
    """
    section = _text(data)
    base, offset = section["address"], section["offset"]
    at = section["offset"] + site - base
    raw = data[offset : offset + section["size"]]
    return _trace(raw, max(0, at - offset - window), at - offset)


def _trace(text: bytes, start: int, end: int) -> dict:
    """Track constant registers over [start, end) text offsets."""
    regs: dict[int, int | None] = {}
    for offset in range(start, end, 4):
        word = struct.unpack_from("<I", text, offset)[0]
        op = word >> 26
        if op == 15:
            regs[(word >> 16) & 31] = ((word & 0xFFFF) << 16) & _MASK
        elif op == 13:
            rs, rt = (word >> 21) & 31, (word >> 16) & 31
            if rs == rt and isinstance(regs.get(rt), int):
                regs[rt] = (regs[rt] | (word & 0xFFFF)) & _MASK
            elif rt in regs:
                del regs[rt]
        elif op == 9:
            rs, rt = (word >> 21) & 31, (word >> 16) & 31
            if isinstance(regs.get(rs), int):
                regs[rt] = (regs[rs] + _signed_half(word)) & _MASK
            elif rs == 0:
                regs[rt] = _signed_half(word) & _MASK
            elif rt in regs:
                del regs[rt]
        elif op == 0 and word & 63 in (33, 45):
            rs, rt, rd = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
            if rt == 0 and rs == 0:
                regs[rd] = 0
            elif rt == 0 and isinstance(regs.get(rs), int):
                regs[rd] = regs[rs]
            elif rd in regs:
                del regs[rd]
        elif op == 35:
            regs.pop((word >> 16) & 31, None)
    return regs


def decode_bind_sites(data: bytes, site: int, *, window: int = 600) -> list[dict]:
    """Decode one EE bind-candidate JAL site into client record + service id."""
    regs = _regs_before_site(data, site, window=window)
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


def decode_call_sites(data: bytes, site: int, *, window: int = 600) -> list[dict]:
    """Decode one EE call-candidate JAL site into command + buffer arguments."""
    regs = _regs_before_site(data, site, window=window)
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


def decode_register_sites(data: bytes, site: int, *, window: int = 600) -> list[dict]:
    """Decode one IOP register-candidate JAL site into service + handler + queue arguments."""
    regs = _regs_before_site(data, site, window=window)
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
    by_service: dict[int, dict] = {}
    for reg in registers:
        service = reg.get("service_id")
        if isinstance(service, int) and service not in by_service:
            by_service[service] = reg
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
            "commands": sorted(
                {c.get("command") for c in group if isinstance(c.get("command"), int)}
            ),
        }
        reg = by_service.get(service) if isinstance(service, int) else None
        if reg is None:
            row["status"] = "incomplete"
            row["reason"] = "no IOP registration binds this service id"
        elif record is None or not group:
            row["status"] = "incomplete"
            row["reason"] = "EE caller group is missing handler/state binding"
            row["register_site"] = reg.get("site")
        else:
            row["register_site"] = reg.get("site")
            row["handler"] = reg.get("handler")
            row["queue"] = reg.get("queue")
            row["status"] = "bound"
        handoffs.append(row)
    return handoffs
