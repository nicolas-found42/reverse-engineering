"""Measured structure of FR2 sound banks, music streams and playlists.

Verified for the unchanged PAL corpus only. Bank headers are
`[self_size, pad_size, count]` plus count 16-byte descriptors
`[span_bytes, reserved_zero, span_start, rate_hz]` and a zero tail whose length
equals word1. Every bank payload is PS-ADPCM spans in exactly one flag
progression: loop-repeat (`0,6,2*,3`) or speech-marker (`0,0*,1,7` with 0x77
filler). Music streams are stereo 44.1 kHz with 32768-byte interleave turns and
all-zero flags; `.mih` word1 and words 6..15 are opaque. Playlists are ASCII
`sounds\\...` lines; every music line resolves to a corpus `.mih` stem.

Rate, channel and interleave values are carried into consumer checks verbatim;
no audible-effect, SPU2 hardware, runtime or lifetime claim is made.
"""

import spu_adpcm as adpcm
from evidence_common import Invalid, sha256
from format_contracts import bank
from verify_audio import end_blocks, terminator

MAX_BYTES = 128 * 1024 * 1024

# EE static registry `sounds\<stem>:<group>:<base>:<count>`; counts re-checked
# against measured corpus descriptor/line counts by test_audio_census.py.
REGISTRY = {
    "banks": {
        "baya": {"group": 10, "base": 100, "count": 5},
        "bayb": {"group": 11, "base": 105, "count": 6},
        "bayc": {"group": 12, "base": 111, "count": 8},
        "car_gen": {"group": 8, "base": 40, "count": 51},
        "car1_snd": {"group": 0, "base": 0, "count": 5},
        "car2_snd": {"group": 1, "base": 5, "count": 5},
        "car3_snd": {"group": 2, "base": 10, "count": 5},
        "car4_snd": {"group": 3, "base": 15, "count": 5},
        "car5_snd": {"group": 4, "base": 20, "count": 5},
        "car6_snd": {"group": 5, "base": 25, "count": 5},
        "car7_snd": {"group": 6, "base": 30, "count": 5},
        "car8_snd": {"group": 7, "base": 35, "count": 5},
        "desa": {"group": 13, "base": 119, "count": 10},
        "desb": {"group": 14, "base": 129, "count": 10},
        "desc": {"group": 15, "base": 139, "count": 7},
        "flora": {"group": 16, "base": 146, "count": 5},
        "florb": {"group": 17, "base": 151, "count": 8},
        "florc": {"group": 18, "base": 159, "count": 5},
        "junga": {"group": 19, "base": 164, "count": 5},
        "jungb": {"group": 20, "base": 169, "count": 9},
        "jungc": {"group": 21, "base": 178, "count": 9},
        "oval2": {"group": 22, "base": 187, "count": 5},
        "oval3": {"group": 23, "base": 192, "count": 6},
        "speech": {"group": 0, "base": 0, "count": 99},
        "spring": {"group": 24, "base": 198, "count": 4},
        "spring2": {"group": 25, "base": 202, "count": 4},
        "ui_snds": {"group": 9, "base": 91, "count": 9},
    },
    "music": {
        "frontend": {"group": 0, "base": 0, "count": 1},
        "house": {"group": 1, "base": 1, "count": 7},
        "rock": {"group": 2, "base": 8, "count": 3},
        "seven": {"group": 3, "base": 11, "count": 9},
        "replay": {"group": 4, "base": 20, "count": 1},
    },
    "speech": {"group": 0, "base": 0, "count": 99},
}


class AudioProfileError(Invalid):
    """A universal audio relation failed."""


def flag_progression(span: bytes) -> str:
    """The measured full-span flag progression class, or 'other'."""
    blocks = len(span) // adpcm.BLOCK
    if blocks < 3 or len(span) % adpcm.BLOCK:
        return "other"
    flags = [span[i * adpcm.BLOCK + 1] for i in range(blocks)]
    if (
        flags[0] == 0
        and flags[1] == 6
        and flags[-1] == 3
        and all(f == 2 for f in flags[2:-1])
    ):
        return "loop-repeat"
    if flags[0] == 0 and flags[-2:] == [1, 7] and all(f == 0 for f in flags[1:-2]):
        return "speech-marker"
    return "other"


def classify_bank(msh: bytes, msb: bytes) -> dict:
    parsed = bank(msh, msb)
    progressions, rates, reserved = set(), set(), set()
    for d in parsed["descriptors"]:
        span = msb[d["sample_span"][0] : d["sample_span"][1]]
        progressions.add(flag_progression(span))
        rates.add(d["rate"])
        reserved.add(d["unknown"])
    if len(progressions) != 1 or "other" in progressions:
        raise AudioProfileError(
            f"bank spans leave the measured flag progressions: {sorted(progressions)}"
        )
    (variant,) = progressions
    first_span = msb[
        parsed["descriptors"][0]["sample_span"][0] : parsed["descriptors"][0][
            "sample_span"
        ][1]
    ]
    return {
        "variant": variant,
        "count": parsed["count"],
        "pad_size": parsed["unknown"],
        "rates_hz": sorted(rates),
        "descriptor_reserved": sorted(reserved),
        "terminator": terminator(first_span),
    }


def classify_stream(mih: bytes, mib: bytes) -> dict:
    fields = adpcm.mih_fields(mih)
    channels, rate, interleave = (
        fields["channels"],
        fields["rate"],
        fields["interleave"],
    )
    if (channels, rate, interleave) != (2, 44100, 32768):
        raise AudioProfileError(
            f"stream layout {(channels, rate, interleave)} leaves the measured stereo-32k profile"
        )
    streams = adpcm.deinterleave(mib, channels, interleave)
    for stream in streams:
        if end_blocks(stream):
            raise AudioProfileError(
                "music stream carries end flags; measured profile is flag-free"
            )
    return {
        "variant": "stereo-32k",
        "channels": channels,
        "rate_hz": rate,
        "interleave": interleave,
        "turns": fields["words"][5],
        "opaque_words": {
            "word1": fields["words"][1],
            "words6_15": fields["words"][6:16],
        },
    }


def playlist_lines(data: bytes) -> list[str]:
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise AudioProfileError(f"playlist is not ASCII text: {exc}") from exc
    if not text.endswith("\n") or "\r" in text or "\0" in text:
        raise AudioProfileError("playlist must be newline-terminated ASCII lines")
    lines = text.splitlines()
    if not lines or any(not line.startswith("sounds\\") for line in lines):
        raise AudioProfileError("playlist lines must name sounds\\ paths")
    return lines


def classify_playlist(data: bytes, name: str) -> dict:
    lines = playlist_lines(data)
    lowered = name.lower()
    if lowered.endswith(".mbf;1"):
        variant = "music-list"
    elif lowered.endswith(".sbf;1"):
        variant = "speech-list"
    else:
        raise AudioProfileError(f"playlist extension outside .mbf/.sbf: {name}")
    return {"variant": variant, "lines": len(lines), "sha256": sha256(data)}
