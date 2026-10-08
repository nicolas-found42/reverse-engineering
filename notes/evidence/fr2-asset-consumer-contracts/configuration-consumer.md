# Track configuration consumer contract

The PAL executable has a static configuration path rooted at function
`0x00130190`. It constructs a path from a track directory, a `configs` child,
and a configuration name, then reads records into an initialized settings
structure. Its default structure writes, keyed lookups and formatted `FOG`
read are distinct paths: the file does not define every setting's default.
The function is called from track resource setup at `0x0012d4b8`.

The bounded grammar supported here is the one present in all 16 `.cfg` archive
records. Active records use `KEY: value`; blank lines and `//` comment lines
are ignored. `FOG` has one finite binary32 token followed by three signed
decimal 32-bit tokens. `CAR_HEADLIGHT_STRENGTH`, `TRACK_WETNESS`,
`SUN_FLARE_SIZE`, and `HEAT_HAZE_STRENGTH` each have one finite binary32 token.
Each key appears once in every member of the checked corpus. The decoder keeps
the parsed values typed but does not assign scene, color-channel, lighting, or
rendering meaning.

The contract is backed by the saved static export for PAL executable SHA-256
`216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95`, function
`0x00130190`, and its references to the path template, key probes, and `FOG`
conversion format. The static-export artifact is local and is not included in
this repository. The preserved code identity is the export SHA-256
`554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811bf26beaa6383`.

`tools/config_contracts.py` implements the handwritten parser. The corpus
consumer check rereads all expected `.cfg` files through the pinned archive
baseline, validates every member with that parser, and records only file
identities and key counts in the local receipt. It does not copy configuration
payloads into evidence. The supported claim ends at static parsing and the
measured PAL grammar; setting lifetimes, runtime selection, and rendered
effects remain unresolved.
