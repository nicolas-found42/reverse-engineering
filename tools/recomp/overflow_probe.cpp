// SPDX-License-Identifier: GPL-3.0-only
#include <array>
#include <cstdint>
#include <cstdio>
#include <limits>
#include "overflow_macros_only.h"

struct Pair { int32_t a; int32_t b; };

static bool check_pair(int32_t a, int32_t b) {
    uint32_t add_got = 0, sub_got = 0;
    bool add_overflow = false, sub_overflow = false;
    ADD32_OV(a, b, add_got, add_overflow);
    SUB32_OV(a, b, sub_got, sub_overflow);

    const int64_t add_wide = static_cast<int64_t>(a) + static_cast<int64_t>(b);
    const int64_t sub_wide = static_cast<int64_t>(a) - static_cast<int64_t>(b);
    const uint32_t add_expected = static_cast<uint32_t>(add_wide);
    const uint32_t sub_expected = static_cast<uint32_t>(sub_wide);
    const bool add_expected_overflow = add_wide > std::numeric_limits<int32_t>::max() ||
                                       add_wide < std::numeric_limits<int32_t>::min();
    const bool sub_expected_overflow = sub_wide > std::numeric_limits<int32_t>::max() ||
                                       sub_wide < std::numeric_limits<int32_t>::min();
    if (add_got != add_expected || add_overflow != add_expected_overflow ||
        sub_got != sub_expected || sub_overflow != sub_expected_overflow) {
        std::fprintf(stderr,
                     "mismatch a=%d b=%d add=%08x/%d expected=%08x/%d sub=%08x/%d expected=%08x/%d\n",
                     a, b, add_got, add_overflow, add_expected, add_expected_overflow,
                     sub_got, sub_overflow, sub_expected, sub_expected_overflow);
        return false;
    }
    return true;
}

int main() {
    constexpr std::array<int32_t, 17> edge = {
        std::numeric_limits<int32_t>::min(), std::numeric_limits<int32_t>::min() + 1,
        -0x40000001, -0x40000000, -2, -1, 0, 1, 2, 0x3fffffff,
        0x40000000, std::numeric_limits<int32_t>::max() - 1,
        std::numeric_limits<int32_t>::max(), -0x7fffffff, 0x20000000,
        -0x20000000, 0x60000000
    };
    size_t checks = 0;
    for (int32_t a : edge) {
        for (int32_t b : edge) {
            if (!check_pair(a, b)) return 1;
            checks++;
        }
    }
    constexpr std::array<Pair, 8> directed = {{
        {2147483647, 1}, {-2147483647 - 1, -1}, {-2147483647 - 1, 1},
        {2147483647, -1}, {0, -2147483647 - 1}, {-1, -2147483647 - 1},
        {-2147483647 - 1, 2147483647}, {2147483647, -2147483647 - 1}
    }};
    for (const auto& pair : directed) {
        if (!check_pair(pair.a, pair.b)) return 1;
        checks++;
    }
    std::printf("ok: %zu add/sub edge-pair checks\n", checks);
    return 0;
}
