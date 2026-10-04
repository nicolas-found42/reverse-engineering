#!/usr/bin/env python3
"""Decode a .ptg sprite to PNG (grayscale) and prove the layout.

Layout (validated on gear0): 
  header 0x20 bytes: [count u32][? u32][? u32][stride u32=0x20][cell u32=0x20][w u32][h u32][1 u32]
  then a 1024-byte table region (idx<<24 | 0xE3E3E3 entries) — role TBD
  then the image: rows of w bytes + (stride-w) 0xDD pad bytes, h rows.
"""
import sys
from pathlib import Path

from format_contracts import sprite

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"
OUT = ROOT / "notes/ptg-renders"


def render(path: Path):
    data = path.read_bytes()
    parsed = sprite(data)
    w, h, stride = parsed['width'], parsed['height'], parsed['stride']
    start = parsed['payload_span'][0]
    rows = [data[start + row * stride:start + row * stride + w] for row in range(h)]
    return (w, h), rows, True, (parsed['header'][0], stride, parsed['header'][4],
                               hex(parsed['table_span'][0]), hex(start))


def write_png(rows, w, h, out: Path) -> None:
    from PIL import Image  # pyright: ignore[reportMissingImports] — optional legacy PNG dependency

    img = Image.new("L", (w, h), 0)
    px = img.load()
    for y, row in enumerate(rows):
        for x, v in enumerate(row):
            px[x, y] = v
    img = img.resize((w * 8, h * 8), Image.NEAREST)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def main() -> None:
    targets = sys.argv[1:] or ["gear0", "gear1", "Desert_C"]
    for t in targets:
        hits = sorted(FILES.rglob(f"{t}.ptg;1"))
        if not hits:
            print(f"{t}: not found")
            continue
        p = hits[0]
        (w, h), rows, pad_ok, meta = render(p)
        out = OUT / f"{p.name.replace(';1','')}.png"
        write_png(rows, w, h, out)
        print(f"{p.name}: {w}x{h} pad_ok={pad_ok} meta={meta} -> {out}")


if __name__ == "__main__":
    main()
