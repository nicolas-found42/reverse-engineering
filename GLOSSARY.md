# Ford Racing 2 reverse engineering

Recovered vocabulary for the PlayStation 2 PAL version of *Ford Racing 2*, limited to what has been measured on the unchanged corpus. Terms marked as unresolved name data whose meaning is not yet established.

## Corpus

**Corpus**:
The unchanged PAL SLES-517.05 disc contents (executable, archive header and data, extracted files) identified by SHA-256.
_Avoid_: Game files, dump

**Supported profile**:
A structural rule verified on the corpus with negative tests and a claim limited to what was measured.
_Avoid_: Format spec, decoder

**Unresolved**:
Data that has been measured but whose meaning is not established; it is retained and listed, never guessed.
_Avoid_: Unknown format, TODO

## Sound

**Bank**:
A paired sound header and payload file whose descriptors divide the payload into consecutive sample spans.
_Avoid_: Sound file

**Sample span**:
One descriptor's slice of a bank payload, made of whole 16-byte ADPCM blocks.
_Avoid_: Sample, clip

**End-marker block**:
A final ADPCM block flagged 7 whose 14 data bytes are all 0x77, preceded by a block flagged 1; it decodes to silence.
_Avoid_: Terminator, footer

**Music stream**:
A paired `.mib`/`.mih` file holding two interleaved ADPCM channels at 44,100 Hz.
_Avoid_: Song, track

**Interleave turn**:
One round of per-channel runs of 0x8000 bytes in a music stream; the header's sixth word (index 5) equals the number of turns.
_Avoid_: Frame, chunk

## Models

**Name pool**:
The packed run of NUL-terminated part names in a model file, referenced by the name tree.
_Avoid_: String table

**Name-pool end**:
The byte offset where the name pool ends; it equals the model's first 32-bit word.
_Avoid_: Leading count, count

**Geometry region**:
The part of a model file that begins at the next 16-byte boundary after the name-pool end; its layout is unresolved.
_Avoid_: Mesh data

## Sprites

**Gear sprite**:
A single-tile sprite showing the gear indicator; gear 0 is uppercase R and gear 1 is uppercase N.
_Avoid_: HUD icon

**Tile**:
A cell-sized square, 16 or 32 pixels, of an image stored in a PTG file, placed in row-major order.
_Avoid_: Block, chunk

**Tile extent record**:
A 16-byte entry per tile whose two floats give the fraction of the tile that lies inside the image; the remaining pointer value is unresolved.
_Avoid_: Tile header

**Tiled profile**:
The layout of PTG files whose last header word is 0xDDDDDDDD: a pointer record and a 64-byte descriptor block per tile, then 1,024 bytes of pixels per tile.
_Avoid_: Texture format
