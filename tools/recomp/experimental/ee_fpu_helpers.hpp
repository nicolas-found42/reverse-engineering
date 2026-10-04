// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef HERMES_EXPERIMENTAL_EE_FPU_HELPERS_H
#define HERMES_EXPERIMENTAL_EE_FPU_HELPERS_H

#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>

// Experimental, manual-derived helpers for three bounded EE FPU cases.
// They do not model EE custom arithmetic rounding, unsupported operands,
// or all FCR31 behavior. See README.md in this directory.
static inline int32_t Ps2FpuCvtWS(float value)
{
    uint32_t bits;
    std::memcpy(&bits, &value, sizeof(bits));
    if ((bits & 0x7f800000u) > 0x4e800000u)
        return (bits & 0x80000000u) ? INT32_MIN : INT32_MAX;
    // The exponent guard guarantees |value| < 2^31, so this cast is defined.
    return static_cast<int32_t>(value);
}

static inline float Ps2FpuMinS(float fs, float ft)
{
    if (fs == 0.0f && ft == 0.0f)
        return (std::signbit(fs) || std::signbit(ft)) ? -0.0f : 0.0f;
    return fs <= ft ? fs : ft;
}

static inline float Ps2FpuMaxS(float fs, float ft)
{
    if (fs == 0.0f && ft == 0.0f)
        return (std::signbit(fs) && std::signbit(ft)) ? -0.0f : 0.0f;
    return fs >= ft ? fs : ft;
}

static inline float Ps2FpuSqrtS(float value, uint32_t &fcr31)
{
    uint32_t bits;
    std::memcpy(&bits, &value, sizeof(bits));
    const uint32_t magnitude = bits & 0x7fffffffu;
    const uint32_t exponent = bits & 0x7f800000u;
    const uint32_t fraction = bits & 0x007fffffu;

    // NaN, infinity and denormal inputs are outside the documented data model;
    // retain the old host path for them in this experimental change.
    if (exponent == 0x7f800000u || (exponent == 0 && fraction != 0))
        return sqrtf(value);

    // SQRT.S sets I based on this instruction and explicitly clears D. Preserve
    // every other cause, sticky, condition, and control bit.
    fcr31 &= ~0x00030000u;
    if (magnitude == 0)
        return value; // preserve both signed zeros
    if (bits & 0x80000000u)
    {
        fcr31 |= 0x00020000u | 0x00000040u; // I cause and sticky I
        bits &= 0x7fffffffu;
        float absolute;
        std::memcpy(&absolute, &bits, sizeof(absolute));
        return sqrtf(absolute);
    }
    return sqrtf(value);
}

#endif
