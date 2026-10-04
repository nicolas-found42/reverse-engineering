#!/usr/bin/env python3
"""Scan FILES.DAT (and others) for known PS2/asset magics; sample histogram of leading u32s."""
import mmap
import struct
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "games/ford-racing-2/extracted"

MAGICS = {
    b"\x7fELF": "ELF",
    b"\x00\x00\x01\xbA": "PS2 icon.sys?",  # placeholder
    b"\x89PNG": "PNG",
    b"TIM2": "TIM2 texture",
    b"CLUT": "PS2 CLUT?",
    b"VAGp": "VAG audio",
    b"SSbd": "PS2 SSbd (sound bank)",
    b"SShd": "PS2 SShd (header)",
    b"PSS\0": "MPEG-PS stream? (PSS magic variants)",
    b"\x00\x00\x01\xba": "MPEG PS",
    b"\x00\x00\x01\xb3": "MPEG video ES",
    b"\x1f\x8b\x08": "gzip",
    b"LZSS": "LZSS?",
    b"CRILAYLA": "CRILAYLA",
    b"\x04\x22\x4d\x18": "lz4",
    b"SCE": "SCE?",
    b"\x54\x49\x4d\x32": "TIM2",
    b"\x2e\x50\x53\x53": ".PSS",
    b"PSMT4": "PSMT4",
    b"PSMT8": "PSMT8",
    b"IECS": "IECS?",
    b"BMD": "BMD?",
    b"MDL": "MDL?",
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00": "zerorun",
}


def scan(path: Path) -> None:
    print(f"=== {path.name} ({path.stat().st_size} bytes) ===")
    with path.open("rb") as fh:
        mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        for magic, label in MAGICS.items():
            if len(magic) < 4:
                continue
            count = 0
            pos = 0
            first = []
            while True:
                i = mm.find(magic, pos)
                if i < 0:
                    break
                count += 1
                if len(first) < 8:
                    first.append(i)
                pos = i + 1
                if count > 100000:
                    break
            if count:
                print(f"  {label:35s} {magic.hex():22s} count={count:<8d} first@{[hex(x) for x in first[:6]]}")
        mm.close()


if __name__ == "__main__":
    import sys

    targets = sys.argv[1:] or ["FILES.DAT"]
    for t in targets:
        scan(EX / t)
