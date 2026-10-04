# Runtime: pass

Offline replay of four real unattended debugger captures. The capture process opened windows; it was not headless. All local emulator processes exited and the exact original preferences/breakpoint state were restored. See [runtime-captures.json](runtime-captures.json) for observed register/code/state identities and [runtime-result.json](runtime-result.json) for full provenance/comparison results.

| Event | Record | Guest output | Bytes | SHA-256 |
| --- | ---: | --- | ---: | --- |
| raw-1 | 311 | `00397e80` | 1032 | `4d11203d78dda69ed9a7b615cfcda867f1cf979f36765470c20eaef34f1f5da7` |
| zlib-1 | 830 | `00748e80` | 332320 | `afaa4c5ab9c8dc81529f5300de568b8b8d8dc499fd9e9fa9c11e7fa6ed9f9c18` |
| raw-2 | 311 | `00397e80` | 1032 | `4d11203d78dda69ed9a7b615cfcda867f1cf979f36765470c20eaef34f1f5da7` |
| zlib-2 | 830 | `00748e80` | 332320 | `afaa4c5ab9c8dc81529f5300de568b8b8d8dc499fd9e9fa9c11e7fa6ed9f9c18` |

Each branch repeat came from a separate cold boot. Entry/branch/actual caller return observations are bound to complete savestates. Returned pointers index guest EE RAM; no host virtual address is used. All full logical output bytes match independent DAT extraction; no transformation or guest mutation was applied. Repeated full memory hashes differ while output hashes agree. These recorded observations cover two boot assets on this executable, not exhaustive gameplay.
