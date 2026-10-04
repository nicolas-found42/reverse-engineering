#!/usr/bin/env python3
"""Decode a .ptg sprite to PNG (grayscale) and prove the layout.

Layout (validated on gear0): 
  header 0x20 bytes: [count u32][? u32][? u32][stride u32=0x20][cell u32=0x20][w u32][h u32][1 u32]
  then a 1024-byte table region (idx<<24 | 0xE3E3E3 entries) — role TBD
  then the image: rows of w bytes + (stride-w) 0xDD pad bytes, h rows.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "games/ford-racing-2/extracted/files"
OUT = ROOT / "notes/ptg-renders"


def render(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    count, a, b, stride, cell, w, h, one = struct.unpack_from("<8I", data, 0)
    # table: 256 x u32 entries of form (idx<<24 | 0xE3E3E3); find its start and end.
    table_start = None
    for i in range(0x20, min(len(data) - 4, 0x400)):
        if data[i : i + 3] == b"\xe3\xe3\xe3":
            table_start = i
            break
    if table_start is None:
        raise ValueError("no e3 table found")
    img_start = table_start + 1024
    if img_start + h * stride > len(data):
        raise ValueError(f"image region exceeds file: need {img_start + h*stride}, have {len(data)}, table at 0x{table_start:x}")
    rows = []
    for r in range(h):
        o = img_start + r * stride
        rows.append(data[o : o + w])
    # check padding bytes are DD
    pad_ok = True
    for r in range(h):
        o = img_start + r * stride + w
        pad = data[o : o + (stride - w)]
        if len(pad) and not all(x == 0xDD for x in pad):
            pad_ok = False
            break
    return (w, h), rows, pad_ok, (count, stride, cell, hex(table_start), hex(img_start))


def write_png(rows, w, h, out: Path) -> None:
    from PIL import Image

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
