#!/usr/bin/env python3
"""Per-extension format fingerprint: sample files, dump heads + u32 interpretations."""
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"


def ext_of(name: str) -> str:
    base = name.rsplit("/", 1)[-1]
    if "." in base:
        return base.rsplit(".", 1)[1].split(";")[0].lower()
    return "(none)"


def main() -> None:
    by_ext = defaultdict(list)
    for p in sorted(FILES.rglob("*")):
        if p.is_file():
            by_ext[ext_of(p.name)].append(p)

    print(f"extensions: {len(by_ext)}")
    for ext, paths in sorted(by_ext.items(), key=lambda kv: -len(kv[1])):
        paths_sorted = sorted(paths, key=lambda p: p.stat().st_size)
        sample = paths_sorted[len(paths_sorted) // 2]  # median size
        head = sample.read_bytes()[:64]
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in head[:32])
        u32 = struct.unpack("<8I", head[:32]) if len(head) >= 32 else ()
        print(f"\n=== .{ext} ({len(paths)} files) sample={sample.name} ({sample.stat().st_size}B) ===")
        print(f"  head : {head[:32].hex(' ')}")
        print(f"  ascii: {asc}")
        if u32:
            print(f"  u32le: {[hex(x) for x in u32]}")
            print(f"  u32vals: {list(u32)}")
        # also show a small file if median is huge
        if len(paths_sorted) > 2 and paths_sorted[0].stat().st_size < 100:
            tiny = paths_sorted[0]
            th = tiny.read_bytes()[:32]
            ta = "".join(chr(b) if 32 <= b < 127 else "." for b in th)
            print(f"  smallest {tiny.name} ({tiny.stat().st_size}B): {th.hex(' ')} {ta}")


if __name__ == "__main__":
    main()
