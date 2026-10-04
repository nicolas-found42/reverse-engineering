"""Find EE kernel syscall stubs and attach candidate names from the PS2SDK numbers.

A stub is the four words `addiu v1,zero,N; syscall; jr ra; nop`, the shape the
PS2SDK kernel library emits. The number-to-name table is read literally from the
SDK's `syscallnr.h`; aliases are all kept. A name is a candidate from the public
SDK, not a verified original symbol, and the game's kernel library version is
not known. Nothing is executed.
"""
import hashlib
import re
import subprocess
from pathlib import Path

from evidence_common import Invalid
from verify_text_denominator import WORD, _unlisted

SYSCALL = 0x0000000C
JR_RA = 0x03E00008
ADDIU_V1_ZERO = 0x2403
SDK_COMMIT = "ac92a9f657d2e531dd8f060250b07f2a5ac6dea5"
HEADER_PATH = "ee/kernel/include/syscallnr.h"
DEFINE = re.compile(r"#define\s+__NR_(\w+)\s+(.+)")
LITERAL = re.compile(r"(0[xX][0-9a-fA-F]+|[0-9]+)")
NEGATIVE = re.compile(r"\(\s*-\s*(0[xX][0-9a-fA-F]+|[0-9]+)\s*\)")
ALIAS = re.compile(r"__NR_(\w+)")


def parse_syscall_header(text: str) -> dict[int, list[str]]:
    """number -> every SDK name defined for it, in definition order."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    values: dict[str, int] = {}
    order: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        match = DEFINE.fullmatch(line)
        if not match:
            continue
        name, right = match[1], match[2].strip()
        if LITERAL.fullmatch(right):
            value = int(right, 0)
        elif NEGATIVE.fullmatch(right):
            value = -int(NEGATIVE.fullmatch(right)[1], 0)
        elif ALIAS.fullmatch(right) and ALIAS.fullmatch(right)[1] in values:
            value = values[ALIAS.fullmatch(right)[1]]
        else:
            raise Invalid(f"unsupported syscall number expression for {name}")
        values[name] = value
        order.append(name)
    table: dict[int, list[str]] = {}
    for name in order:
        table.setdefault(values[name], []).append(name)
    return table


def _signed16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def scan_stubs(data: bytes, static: dict, header_text: str) -> dict:
    details = _unlisted(data, static)
    names = parse_syscall_header(header_text)
    owner = {int(r['address'], 16): f['entry'] for f in static['functions'] for r in f['instructions']}
    footprint: dict[str, set[int]] = {}
    for address, entry in owner.items():
        footprint.setdefault(entry, set()).add(address)
    stubs, summary = [], dict.fromkeys(('stubs', 'saved_function', 'partial', 'unowned', 'unknown_number', 'ambiguous'), 0)
    for region in details['regions']:
        words = [int.from_bytes(data[region['offset'] + i:region['offset'] + i + WORD], 'little')
                 for i in range(0, region['bytes'] - region['bytes'] % WORD, WORD)]
        for index in range(len(words) - 3):
            first, rest = words[index], words[index + 1:index + 4]
            if first >> 16 != ADDIU_V1_ZERO or rest != [SYSCALL, JR_RA, 0]:
                continue
            address = region['address'] + index * WORD
            cells = {address + k * WORD for k in range(4)}
            owners = {owner[a] for a in cells if a in owner}
            if not owners:
                ownership = 'unowned'
            elif owners == {f'{address:08x}'} and footprint[f'{address:08x}'] == cells:
                ownership = 'saved_function'
            else:
                ownership = 'partial'
            number = _signed16(first & 0xFFFF)
            candidates = names.get(number, [])
            stubs.append({'address': f'{address:08x}', 'number': number, 'names': candidates, 'ownership': ownership})
            summary['stubs'] += 1
            summary[ownership] += 1
            summary['unknown_number'] += not candidates
            summary['ambiguous'] += len(candidates) > 1
    return {'executable_sha256': details['executable_sha256'], 'stubs': stubs, 'summary': summary,
            'whole_game_decompiled': False,
            'claim_limits': [
                'Names are candidates from the public PS2SDK syscall numbers, not verified original symbols.',
                'The kernel library version the game linked is not known; aliases are all listed.',
                'A stub shape and number establish a kernel call wrapper, not what the BIOS does.']}


def read_pinned_header(root: Path, commit: str = SDK_COMMIT) -> tuple[str, str]:
    """Return (text, sha256) of the SDK syscall header after proving it is the pinned Git object."""
    def git(*args: str) -> bytes:
        try:
            return subprocess.run(["git", "-C", str(root), *args], check=True,
                                  capture_output=True, timeout=30).stdout
        except subprocess.CalledProcessError as exc:
            raise Invalid("pinned SDK Git source is unavailable") from exc
    if git("rev-parse", "HEAD").decode().strip() != commit:
        raise Invalid("SDK revision differs from the pinned source")
    raw = (root / HEADER_PATH).read_bytes()
    if raw != git("show", f"{commit}:{HEADER_PATH}"):
        raise Invalid("SDK syscall header differs from the pinned Git object")
    return raw.decode(), hashlib.sha256(raw).hexdigest()
