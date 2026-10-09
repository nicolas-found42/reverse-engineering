# Audio census disposition (issue #27)

Reproduce the pinned census counts from the committed
[`variant-census.json`](variant-census.json) (classifier
`c8abdab114c9bb3dd6986cd42afb9e910024d32c`, index fix
`cc6baa0f615d861baef3a6de7fe0642d8c17a9e9`) with:

```sh
python3 -c 'import json; d = json.load(open("notes/evidence/fr2-audio-contracts/variant-census.json")); print("corpus:", d["corpus_id"][:8]); print("banks:", {k: v["banks"] for k, v in d["variants"]["bank"].items()}); print("streams:", {k: v["streams"] for k, v in d["variants"]["stream"].items()}); print("playlists:", {k: (v["files"], v["lines"]) for k, v in d["variants"]["playlist"].items()})'
```

Re-measure every count against the unchanged PAL corpus and re-check the
registry and tool-source pins with:

```sh
sh tools/check.sh test_audio_census
python3 tools/publish_gate.py --body notes/evidence/fr2-audio-contracts/README.md
```

Covers (green, `tools/test_audio_census.py`, 6 tests):
- 27 bank pairs → loop-repeat (26) / speech-marker (1, `speech`); every span
  in exactly one `verify_audio.terminator` class, uniform per bank.
- 20 stream pairs → stereo-32k (2ch, 44100 Hz, 32768 interleave, flag-free).
- 6 playlists → music-list (5 `.mbf`, 21 lines) / speech-list (1 `.sbf`, 99 lines);
  every music line resolves to a corpus `.mih` stem; 120 lines total.
- Corpus pin `corpus_id`
  `e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab`
  + tool-source hashes in
  `notes/evidence/fr2-audio-contracts/variant-census.json`.

Incomplete consumer contracts (deferred):
| Item | Falsifier | Next action |
|---|---|---|
| EE loader/upload/playback binding (0x13fb28/0x13fd00/0x1408d8) | Named function absent from Ghidra export or byte range differs | Re-verify ranges against export, then bind spans/rates/channels per variant |
| Music registry playback (0x1424f0) | Registry entry not referenced by consumer call site | Disassemble call sites, bind playlist→stream selection |
| Loop/repeat runtime semantics (206 spans) | IOP playback ignores repeat/loop-start flags | Trace IOP module playback of a loop-repeat span |
| `.mih` word1 / words 6..15 meaning | Counterexample stream with same payload but different word1 | Keep opaque; carried verbatim, no claim |

Negative controls live in `tools/test_audio_verifier.py` (wrong spans/rates/looping fail).
