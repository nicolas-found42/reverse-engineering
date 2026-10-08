"""Bounded decoder for the PAL track-configuration grammar consumed by the EE loader.

This is a hand-written data decoder, not an exported program listing. It models
only the five key/value forms observed in all 16 corpus `.cfg` records and in
the static consumer at 0x00130190. It does not assign rendering semantics to
the numeric values.
"""

import math
import re
import struct


class InvalidConfig(ValueError):
    """The input is outside the measured supported track-configuration profile."""


FLOAT_KEYS = {
    "CAR_HEADLIGHT_STRENGTH",
    "TRACK_WETNESS",
    "SUN_FLARE_SIZE",
    "HEAT_HAZE_STRENGTH",
}
REQUIRED_KEYS = frozenset((*FLOAT_KEYS, "FOG"))
_INTEGER = re.compile(r"[+-]?[0-9]+\Z")


def _float32(token: str, key: str) -> float:
    try:
        value = float(token)
        if not math.isfinite(value):
            raise ValueError
        # The consumer passes these fields through binary32 values.
        value = struct.unpack("<f", struct.pack("<f", value))[0]
    except (OverflowError, ValueError, struct.error) as exc:
        raise InvalidConfig(f"{key}: invalid finite binary32 value") from exc
    return value


def parse_track_config(data: bytes) -> dict[str, float | tuple[float, int, int, int]]:
    """Parse one corpus-profile track config into typed field values.

    Blank lines and `//` comments are retained as ignored syntax. Active lines
    use `KEY: value`; each key occurs exactly once. `FOG` has one decimal
    binary32 and three signed decimal 32-bit integers. The remaining four keys
    each have one binary32 value.
    """
    if not isinstance(data, bytes):
        raise InvalidConfig("configuration input must be bytes")
    if b"\0" in data:
        raise InvalidConfig("configuration contains an embedded NUL")
    if b"\r" in data.replace(b"\r\n", b""):
        raise InvalidConfig("configuration contains a bare carriage return")
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise InvalidConfig("configuration is outside the ASCII profile") from exc

    parsed: dict[str, float | tuple[float, int, int, int]] = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        if ":" not in line:
            raise InvalidConfig(f"line {line_number}: expected KEY: value")
        key, raw_values = (part.strip() for part in line.split(":", 1))
        if key not in REQUIRED_KEYS:
            raise InvalidConfig(f"line {line_number}: unsupported key {key!r}")
        if key in parsed:
            raise InvalidConfig(f"line {line_number}: duplicate key {key}")
        values = raw_values.split()
        if key == "FOG":
            if len(values) != 4:
                raise InvalidConfig(f"line {line_number}: FOG requires four numeric fields")
            components = []
            for token in values[1:]:
                if not _INTEGER.fullmatch(token):
                    raise InvalidConfig(f"line {line_number}: FOG integer field is not decimal")
                value = int(token, 10)
                if not -(1 << 31) <= value < (1 << 31):
                    raise InvalidConfig(f"line {line_number}: FOG integer field exceeds signed 32-bit range")
                components.append(value)
            parsed[key] = (_float32(values[0], key), *components)
        else:
            if len(values) != 1:
                raise InvalidConfig(f"line {line_number}: {key} requires one numeric field")
            parsed[key] = _float32(values[0], key)

    missing = REQUIRED_KEYS - parsed.keys()
    if missing:
        raise InvalidConfig("missing required key(s): " + ", ".join(sorted(missing)))
    return parsed
