#!/usr/bin/env python3
"""Extract ISO files from the raw MODE2/2352 bin: strip the 304-byte sector overhead."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ps2iso import Ps2Iso  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "games/ford-racing-2/ford-racing-2.bin"
OUT = ROOT / "games/ford-racing-2/extracted"


def extract(iso: Ps2Iso, name: str, extent: int, size: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    remaining = size
    lba = extent
    with out.open("wb") as fh:
        while remaining > 0:
            take = min(remaining, 2048)
            fh.write(iso.read_sector(lba)[:take])
            remaining -= take
            lba += 1
    print(f"{name}: {size} bytes -> {out}")


def main() -> None:
    which = sys.argv[1:] or ["small"]
    iso = Ps2Iso(BIN)
    root = iso.root()
    entries = {e["name"]: e for e in iso.read_dir(root["extent"], root["size"]) if e}

    if "small" in which:
        for name in ("SYSTEM.CNF", "SLES_517.05", "FILES.HDR", "IRX/IOPRP255.IMG"):
            e = entries.get(name)
            if e is None:
                # subdirectory files
                continue
            extract(iso, name, e["extent"], e["size"], OUT / name)

    if "all" in which or "dat" in which:
        e = entries["FILES.DAT"]
        extract(iso, "FILES.DAT", e["extent"], e["size"], OUT / "FILES.DAT")

    if "irx" in which:
        # list /IRX directory entries and extract all
        irx = entries.get("IRX")
        if irx is None:
            # find by walking one level
            for path, en in iso.walk():
                if en["is_dir"] and path.rstrip("/").endswith("IRX"):
                    irx = en
                    break
        if irx:
            for e in iso.read_dir(irx["extent"], irx["size"]):
                if e and not e["is_dir"]:
                    extract(iso, "IRX/" + e["name"], e["extent"], e["size"], OUT / "IRX" / e["name"])
    iso.close()


if __name__ == "__main__":
    main()
