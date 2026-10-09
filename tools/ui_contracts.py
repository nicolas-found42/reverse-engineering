"""Bounded structure-only decoder for the PAL UI script line grammar.

This is a hand-written data decoder, not an exported program listing. It models
only the line grammar measured in all 45 corpus ``.ui`` records: ASCII with
CRLF line breaks, blank lines, ``//`` comment lines, ``:TAG value`` records,
and one ``:S{*****>>>`` ... ``:E}*****<<<`` container block per file outside
the texture-manifest profile. It does not assign layout, rendering, or
behavioral semantics to the parsed values, and it is not bound to an EE
loader/consumer address: the consumer half is explicitly incomplete.
"""

import re

_TAG = re.compile(r"[A-Za-z][A-Za-z0-9_]*")

from dataclasses import dataclass, field


class InvalidUI(ValueError):
    """The input is outside the measured supported UI script profile."""


@dataclass(frozen=True)
class UIRecord:
    tag: str
    value: str
    line_number: int


@dataclass(frozen=True)
class UIBlock:
    records: tuple
    line_start: int
    line_end: int
    depth: int


@dataclass(frozen=True)
class UIScript:
    records: tuple
    blocks: tuple
    tags: frozenset = field(default=frozenset())


def parse_ui_script(data: bytes) -> UIScript:
    """Parse one corpus-profile UI script into tagged records and blocks."""
    if not isinstance(data, bytes):
        raise InvalidUI("UI script input must be bytes")
    if b"\0" in data:
        raise InvalidUI("UI script contains an embedded NUL")
    if b"\r" in data.replace(b"\r\n", b""):
        raise InvalidUI("UI script contains a bare carriage return")
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise InvalidUI("UI script is outside the ASCII profile") from exc

    records: list[UIRecord] = []
    blocks: list[UIBlock] = []
    stack: list[tuple[list[UIRecord], int]] = []
    pending_tag: str | None = None
    pending_parts: list[str] = []
    pending_line = 0

    def commit() -> None:
        assert pending_tag is not None
        record = UIRecord(
            tag=pending_tag,
            value=" ".join(pending_parts).strip(),
            line_number=pending_line,
        )
        records.append(record)
        if pending_tag == "S":
            frame: list[UIRecord] = [record]
            stack.append((frame, pending_line))
        elif pending_tag == "E":
            if not stack:
                raise InvalidUI(f"line {pending_line}: E without S")
            frame, block_start = stack.pop()
            frame.append(record)
            blocks.append(
                UIBlock(
                    records=tuple(frame),
                    line_start=block_start,
                    line_end=pending_line,
                    depth=len(stack) + 1,
                )
            )
        elif stack:
            stack[-1][0].append(record)

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        if not line.startswith(":"):
            if pending_tag is None:
                raise InvalidUI(f"line {line_number}: expected :TAG value")
            if not line:
                raise InvalidUI(
                    f"line {line_number}: expected :TAG value"
                )  # unreachable; kept for clarity
            pending_parts.append(line)
            continue
        if pending_tag is not None:
            commit()
            pending_tag = None
            pending_parts = []
        body = line[1:]
        match = _TAG.match(body)
        if match is None:
            raise InvalidUI(f"line {line_number}: malformed tag")
        pending_tag = match.group(0)
        pending_line = line_number
        rest = body[match.end() :].strip()
        pending_parts = [rest] if rest else []
    if pending_tag is not None:
        commit()
    if stack:
        raise InvalidUI("unterminated S block")
    if not records:
        raise InvalidUI("UI script has no records")
    ordered = tuple(sorted(blocks, key=lambda b: (b.line_start, b.depth)))
    return UIScript(
        records=tuple(records),
        blocks=ordered,
        tags=frozenset(r.tag for r in records),
    )
