#!/usr/bin/env python3
"""Minimal ISO9660 reader for PlayStation 2 MODE2/2352 raw CD images.

No external deps. Handles the common PS2 CD layout: sync + 4-byte header +
8-byte subheader + 2048 bytes user data (Mode 2 Form 1).
"""
from __future__ import annotations

import struct
from pathlib import Path

SECTOR = 2352


class Ps2Iso:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.fp = open(self.path, "rb")
        self.sector_count = self.path.stat().st_size // SECTOR
        self.descriptors: list[dict] = []  # parsed volume descriptors
        self._read_descriptors()

    # ---- low level -----------------------------------------------------
    def read_sector(self, lba: int) -> bytes:
        """Return the 2048 user bytes of sector `lba` (Mode 2 Form 1)."""
        self.fp.seek(lba * SECTOR)
        raw = self.fp.read(SECTOR)
        if len(raw) != SECTOR:
            raise EOFError(f"short read at LBA {lba}")
        # sync check
        if raw[:12] != b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00":
            raise ValueError(f"no sync pattern at LBA {lba}: {raw[:12].hex()}")
        sub = raw[16:24]
        form2 = bool(sub[2] & 0x20)
        if form2:
            return raw[24 : 24 + 2324]  # 2324-byte Form 2 payload
        return raw[24 : 24 + 2048]

    def read_bytes(self, lba: int, size: int) -> bytes:
        out = bytearray()
        while size > 0:
            chunk = self.read_sector(lba)
            take = min(size, 2048)
            out += chunk[:take]
            size -= take
            lba += 1
        return bytes(out)

    def close(self) -> None:
        self.fp.close()

    # ---- ISO9660 -------------------------------------------------------
    def _read_descriptors(self) -> None:
        for lba in range(16, 32):
            sec = self.read_sector(lba)
            dtype = sec[0]
            if sec[1:6] != b"CD001":
                break
            if dtype == 255:  # terminator
                break
            if dtype in (1, 2):
                self.descriptors.append(
                    {
                        "type": dtype,
                        "lba": lba,
                        "volume_id": sec[40:72],
                        "root_record": sec[156:190],
                        "joliet": dtype == 2 and self._looks_joliet(sec),
                        "raw": sec,
                    }
                )
            elif dtype == 0:
                continue

    @staticmethod
    def _looks_joliet(sec: bytes) -> bool:
        # Joliet SVD: escape sequences at offset 88 (1 byte) 89..90 ..91.. => %/@ etc.
        # Simpler: UCS-2BE volume id often has 0x00 bytes; check root dir name.
        root = sec[156:190]
        name_len = root[32]
        name = root[33 : 33 + name_len]
        return name_len >= 1 and name[0] == 0x00  # UCS-2BE starts with 0x00 for ASCII

    @staticmethod
    def parse_record(rec: bytes, joliet: bool = False, allow_dot: bool = False) -> dict | None:
        if len(rec) < 33 or rec[0] == 0:
            return None
        ext_attr = rec[1]
        extent = struct.unpack("<I", rec[2:6])[0]
        size = struct.unpack("<I", rec[10:14])[0]
        flags = rec[25]
        name_len = rec[32]
        name_raw = rec[33 : 33 + name_len]
        if name_len == 1 and name_raw in (b"\x00", b"\x01") and not allow_dot:
            return None  # dot entries
        if joliet:
            try:
                name = name_raw.decode("utf-16-be")
            except UnicodeDecodeError:
                name = name_raw.hex()
        else:
            name = name_raw.decode("ascii", "replace")
        if ";" in name:
            name = name.split(";")[0]
        return {
            "name": name,
            "extent": extent,
            "size": size,
            "is_dir": bool(flags & 0x02),
            "ext_attr": ext_attr,
        }

    def read_dir(self, lba: int, size: int, joliet: bool = False) -> list[dict]:
        data = self.read_bytes(lba, size)
        entries: list[dict] = []
        offset = 0
        while offset < len(data):
            rec_len = data[offset]
            if rec_len == 0:
                # advance to next sector boundary
                offset = (offset // 2048 + 1) * 2048
                if offset >= len(data):
                    break
                continue
            rec = data[offset : offset + rec_len]
            parsed = self.parse_record(rec, joliet)
            if parsed:
                entries.append(parsed)
            offset += rec_len
        return entries

    def root(self) -> dict:
        pvd = next(d for d in self.descriptors if d["type"] == 1)
        rec = self.parse_record(pvd["root_record"], False, allow_dot=True)
        assert rec is not None
        return rec

    def find_joliet_root(self) -> dict | None:
        svd = next((d for d in self.descriptors if d["joliet"]), None)
        if not svd:
            return None
        return self.parse_record(svd["root_record"], True, allow_dot=True)

    def walk(self, joliet: bool = False):
        """Yield (path, entry) depth-first from the root (or Joliet root)."""
        if joliet:
            root = self.find_joliet_root()
            if root is None:
                raise ValueError("no Joliet descriptor")
        else:
            root = self.root()
        stack = [("/", root)]
        seen_dirs = set()
        while stack:
            prefix, d = stack.pop()
            if d["extent"] in seen_dirs:
                continue
            seen_dirs.add(d["extent"])
            try:
                entries = self.read_dir(d["extent"], d["size"], joliet)
            except (ValueError, EOFError) as exc:
                yield prefix, {"name": "<unreadable>", "error": str(exc), "is_dir": False, "size": 0, "extent": 0}
                continue
            dirs = []
            for e in entries:
                path = prefix + e["name"]
                if e["is_dir"]:
                    dirs.append((path + "/", e))
                else:
                    yield path, e
            for dprefix, de in sorted(dirs, reverse=True):
                stack.append((dprefix, de))
