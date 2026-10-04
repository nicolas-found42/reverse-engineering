# Static VIF upload mapping

This evidence maps the two pinned CNT/END DMA chains to the eight DVP overlay code ranges. It is a static packet reconstruction; it does not establish that either caller ran or that DMA completed.

The verifier accepts only one bounded CNT tag followed by an exact END tag. With tag transfer enabled, the supported TTE header is a NOP followed by one MPG command; the CNT body then contains VU payload bytes and bounded NOP/MPG pairs. Other DMA tags, reserved/IRQ flags, VIF commands, address/count overflows, malformed bounds, and extra or unmatched MPG spans are refused. The parser holds payload bytes in memory for comparison and the public result emits hashes and locations, not payload data.

The DVP encoding basis is pinned to `ps2dev/binutils-gdb` revision `3eb45ea37f0efd498d1de3cf9562de07197aefa8`. `opcodes/dvp-opc.c:1454-1455` defines MPG opcode `0x4a`; `1759-1773` decodes NUM, with zero representing 256; `2041-2058` gives the variable command length; `gas/config/tc-dvp.c:806-818` converts the MPG location from dwords to byte addresses by multiplying by eight. Local source clone: `.scratch/mesh/codex-root/binutils-dvp`.

The pinned executable is `games/ford-racing-2/extracted/SLES_517.05`, SHA-256 `216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`. Raw instruction guards cover the complete byte spans for `0022fd48`, `00114fe0`, `001f4138`, `001f4468`, and `001f40d8`; the VIF channel pointer table at `0024d0b8` is guarded as words `10008000, 10009000`. They support only conditional ownership: if the respective call paths run, the first packet is submitted through VIF1 and the second through VIF0. The helper's guarded code retains CHCR bit `0x40`, installs CHCR bits `0x105`, and uses the checked packet pointers. No runtime event is observed.

| Overlay | Conditional DMA channel | VU byte range | MPG pairs | Payload bytes | Packet VA = overlay LMA | Packet file offset = overlay source offset |
|---:|---|---:|---:|---:|---:|---:|
| 0 | VIF1 | `[0, 2048)` | 256 | 2,048 | `0x217bf0` | 1,149,936 |
| 1 | VIF1 | `[2048, 4096)` | 256 | 2,048 | `0x2183f8` | 1,151,992 |
| 2 | VIF1 | `[4096, 6144)` | 256 | 2,048 | `0x218c00` | 1,154,048 |
| 3 | VIF1 | `[6144, 8192)` | 256 | 2,048 | `0x219408` | 1,156,104 |
| 4 | VIF1 | `[8192, 10240)` | 256 | 2,048 | `0x219c10` | 1,158,160 |
| 5 | VIF1 | `[10240, 12288)` | 256 | 2,048 | `0x21a418` | 1,160,216 |
| 6 | VIF1 | `[12288, 12464)` | 22 | 176 | `0x21ac20` | 1,162,272 |
| 7 | VIF0 | `[0, 1120)` | 140 | 1,120 | `0x21acf0` | 1,162,480 |

The first CNT packet begins at `0x217be0`, transfers QWC 782, and ends at the END tag at `0x21acd0`. The second begins at `0x21ace0`, transfers QWC 70, and ends at `0x21b150`. All eight payloads match `parse_overlays` on VU address, length, ELF load address, exact source file offset, bytes, and SHA-256. Totals are 1,698 instruction pairs and 13,584 payload bytes. The seven VIF1 chunks cover `[0, 12464)`; the VIF0 chunk covers `[0, 1120)`.

The machine result is [result.json](result.json). The final targeted run passed 25 tests; its full log is [tests.log](tests.log). The parser and verifier are [ps2_vif.py](/Users/Nicolas/Documents/github/hermes/reverse-engineering/tools/ps2_vif.py), [verify_vif.py](/Users/Nicolas/Documents/github/hermes/reverse-engineering/tools/verify_vif.py), and [test_ps2_vif.py](/Users/Nicolas/Documents/github/hermes/reverse-engineering/tools/test_ps2_vif.py). Run from the repository root with:

```sh
PYTHONPATH=tools python3 -m unittest test_ps2_vif test_ps2_vu test_ps2_executables -v
python3 tools/verify_vif.py --output .scratch/mesh/codex-vif/reproduced
```

Jev's source verification is [jev-source-verification.json](jev-source-verification.json); it verified the MPG count/location encoding and exact eight-span mapping, and contradicted the claim that static bytes prove runtime rendering. The negative-control verification is [jev-negative-controls-verification.json](jev-negative-controls-verification.json). The final patch review and completion gate are [jev-final-gate.json](jev-final-gate.json): the exact-span and static-scope claims were accepted, while the overall review returned `escalate` (`safe_to_apply=0.56`) for low-confidence blast-radius/test-gap rubrics. Treat Jev as review evidence, not approval.
