# Experimental VU0 entry 0x268 model

This package contains a bounded, offline reference reconstruction of the code reached by VCALLMS immediate `0x4d` (byte VMA `0x268`) in Ford Racing 2's PAL executable. Treat the sine/cosine interpretation as a strong static and numerical hypothesis, not a symbol name or a hardware-verified result.

The model follows the 25 VU instruction pairs at indices `[77,102)`. It reads the exact raw binary32 LOI payload bit patterns recorded by the source guard and converts host test inputs once to binary32 to represent QMTC2 data transfer. It uses primitive binary32 operations with a toward-zero approximation for arithmetic results. Do not use that approximation as a complete model of VU execution.

The arithmetic model and source guard are experimental. They do not model VU accumulator/result latency, MAC/status/clip flags, exceptions, saturation, exact silicon rounding variation, COP2 interlocks, complete caller state, or E-bit execution control. No emulator or hardware result is implied.

From any working directory, run the numeric reference and source guard; both write results to stdout and create no output files:

```sh
python3 /path/to/reverse-engineering/tools/vu/vu268_reference.py
python3 /path/to/reverse-engineering/tools/vu/vu268_source_guard.py
```

Pass `--executable PATH` to check a different local executable; it must still match the pinned executable and source-span contract. The guard checks the executable hash, overlay identity/mapping, exact `[77,102)` byte-span digest, every LOI-bearing lower word and I flag, and equality with the model's constant table. Any mismatch fails closed.

Run unit tests from the repository root:

```sh
python3 -m unittest tools.test_vu0_reference
```

The private-executable integration test skips when the local game ELF is absent. Synthetic byte fixtures still exercise rejection of wrong executable identity, overlay mapping, pair-span bytes, LOI bits, and model-constant disagreement.
