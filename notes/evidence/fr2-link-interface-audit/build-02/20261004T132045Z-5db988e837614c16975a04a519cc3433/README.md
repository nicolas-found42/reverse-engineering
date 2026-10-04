# Build 02 corrected evidence

This immutable result supersedes the immediately prior build-02 result only for its incorrect generated-function symbol count. The earlier count parser looked for unmangled symbol names; the native C++ names encode `sub_XXXXXXXX_` within the mangled identifier, so that parser incorrectly returned zero. The corrected `nm -gU` extraction finds **4,746 distinct guest entry addresses** across the 16 batch objects and registration object. The original result remains unchanged and is retained with its own hash.

The build outcome remains the measured successful link of an arm64 Mach-O runner, built with runtime, IOP, raylib 5.5, and all 17 generated object inputs. The runner was not executed. All other values are carried forward unchanged from the superseded result. The fresh direct measurement uses the exact same object input paths and records the raw `nm` output digest.
