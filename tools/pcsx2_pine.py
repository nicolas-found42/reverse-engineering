"""Read-only PINE queries and savestate capture for the measured PCSX2 v2.6.3 build.

Protocol source: PCSX2/pcsx2 tag v2.6.3, pcsx2/PINE.cpp.
Register layout: pcsx2/SaveState.cpp and pcsx2/R5900.h at the same tag.
No memory writes, patches, stubs, or host address translation are used.
"""

from pathlib import Path
import socket
import struct
import zipfile

from evidence_common import Invalid, identity
from format_contracts import require

REGISTERS = "zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp s8 ra".split()


class Pine:
    def __init__(self, path: Path):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        try:
            self.socket.connect(str(path))
        except OSError:
            self.socket.close()
            raise

    def close(self):
        self.socket.close()

    def receive(self, length: int) -> bytes:
        result = bytearray()
        while len(result) < length:
            block = self.socket.recv(length - len(result))
            if not block:
                raise Invalid("PINE closed a partial reply")
            result.extend(block)
        return bytes(result)

    def request(self, payload: bytes) -> bytes:
        self.socket.sendall(struct.pack("<I", len(payload) + 4) + payload)
        length = struct.unpack("<I", self.receive(4))[0]
        require(5 <= length <= 450000, "invalid PINE reply length")
        reply = self.receive(length - 4)
        require(reply[0] == 0, "PINE rejected command")
        return reply[1:]

    def text(self, opcode: int) -> str:
        reply = self.request(bytes([opcode]))
        require(len(reply) >= 4, "truncated PINE string reply")
        length = struct.unpack_from("<I", reply)[0]
        require(
            len(reply) == 4 + length and reply[-1:] == b"\0", "invalid PINE string span"
        )
        return reply[4:-1].decode("utf-8")

    def status(self) -> int:
        reply = self.request(b"\x0f")
        require(len(reply) == 4, "invalid PINE status span")
        status = struct.unpack("<I", reply)[0]
        require(status in {0, 1, 2}, "unknown PINE emulator status")
        return status

    def save(self, slot: int):
        require(0 <= slot <= 255, "invalid savestate slot")
        require(self.status() == 1, "capture requires paused guest execution")
        require(self.request(bytes([9, slot])) == b"", "unexpected save-state reply")

    def read(self, address: int, length: int) -> bytes:
        require(
            0 <= address <= 32 * 1024 * 1024
            and 0 <= length <= 32 * 1024 * 1024 - address,
            "guest EE span out of range",
        )
        output = bytearray()
        while len(output) < length:
            count = min(10000, (length - len(output)) // 8)
            if not count:
                count = min(10000, length - len(output))
                stride, opcode = 1, 0
            else:
                stride, opcode = 8, 3
            payload = b"".join(
                bytes([opcode])
                + struct.pack("<I", address + len(output) + index * stride)
                for index in range(count)
            )
            reply = self.request(payload)
            require(len(reply) == count * stride, "partial PINE memory reply")
            output.extend(reply)
        return bytes(output)


def read_state(path: Path):
    try:
        with zipfile.ZipFile(path) as saved:
            version = saved.read("PCSX2 Savestate Version.id")
            require(
                version == b"\x00\x00\x55\x9av2.6.3".ljust(36, b"\0"),
                "unsupported PCSX2 savestate build/layout",
            )
            require(
                saved.getinfo("eeMemory.bin").file_size == 32 * 1024 * 1024,
                "invalid EE memory size",
            )
            require(
                saved.getinfo("PCSX2 Internal Structures.dat").file_size
                <= 16 * 1024 * 1024,
                "oversized internal structures",
            )
            memory = saved.read("eeMemory.bin")
            internal = saved.read("PCSX2 Internal Structures.dat")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise Invalid(f"invalid PCSX2 savestate: {exc}") from exc
    tag = b"cpuRegs".ljust(32, b"\0")
    # Locate the exact tag once, then validate the bound before reading the fixed CPU layout.
    start = internal.find(tag)
    require(
        start >= 0 and internal.find(tag, start + 1) < 0,
        "missing/ambiguous cpuRegs tag",
    )
    start += 32
    pc_offset = 32 * 16 + 2 * 16 + 32 * 4 + 8
    require(start + pc_offset + 4 <= len(internal), "truncated CPU register block")
    registers = {
        name: struct.unpack_from("<I", internal, start + index * 16)[0]
        for index, name in enumerate(REGISTERS)
    }
    raw = {
        name: internal[start + index * 16 : start + (index + 1) * 16].hex()
        for index, name in enumerate(REGISTERS)
    }
    return memory, {
        "pc": struct.unpack_from("<I", internal, start + pc_offset)[0],
        "registers": registers,
        "registers_128bit_le": raw,
        "state_identity": identity(path),
        "build": "v2.6.3",
    }
