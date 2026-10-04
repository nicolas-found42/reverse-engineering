#!/usr/bin/env python3
"""Walk the Ford Racing 2 PS2 disc image and dump the ISO9660 tree + SYSTEM.CNF.

Usage: .venv/bin/python tools/iso_walk.py   (or: uv run python tools/iso_walk.py — stdlib only)
Writes notes/iso-file-table.txt and prints a summary.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ps2iso import Ps2Iso  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "games/ford-racing-2/ford-racing-2.bin"
OUT = ROOT / "notes/iso-file-table.txt"


def main() -> None:
    iso = Ps2Iso(BIN)
    print(f"sectors: {iso.sector_count}")
    for d in iso.descriptors:
        vol = d["volume_id"].decode("ascii", "replace").strip()
        print(f"descriptor type={d['type']} lba={d['lba']} joliet={d['joliet']} volume_id={vol!r}")

    # SYSTEM.CNF from ISO root (non-Joliet names are uppercase short)
    root_entries = iso.read_dir(iso.root()["extent"], iso.root()["size"])
    syscnf = next((e for e in root_entries if e["name"] == "SYSTEM.CNF"), None)
    if syscnf:
        data = iso.read_bytes(syscnf["extent"], syscnf["size"])
        print("\n=== SYSTEM.CNF ===")
        print(data.decode("ascii", "replace"))
        print("=== /SYSTEM.CNF ===")

    # full listing
    files = []
    dirs = []
    for path, e in iso.walk(joliet=False):
        if e.get("error"):
            print(f"!! unreadable dir {path}: {e['error']}")
            continue
        if e["is_dir"]:
            dirs.append(path)
        else:
            files.append((path, e["size"], e["extent"]))

    total = sum(s for _, s, _ in files)
    print(f"\ndirs: {len(dirs)}  files: {len(files)}  total bytes: {total}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("# Ford Racing 2 (PS2) — ISO9660 file table\n")
        fh.write(f"# source: {BIN}\n")
        fh.write(f"# sectors: {iso.sector_count}\n")
        fh.write("# path\tsize_bytes\textent_lba\n")
        for path, size, extent in sorted(files):
            fh.write(f"{path}\t{size}\t{extent}\n")
        fh.write(f"# totals: {len(files)} files, {total} bytes\n")
    print(f"written: {OUT}")

    # print top-level entries
    for path, size, extent in sorted(files):
        if path.count("/") <= 1:
            print(f"{size:>10}  {path}")
    iso.close()


if __name__ == "__main__":
    main()
