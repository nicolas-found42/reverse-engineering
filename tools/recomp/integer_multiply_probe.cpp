// SPDX-License-Identifier: GPL-3.0-only
// Synthetic register-state probe; no game routine or emulator is called.
#include <array>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>

#include "multiply_templates.h"

using Function = void (*)(Context*, int, int, int);

struct Operation {
    const char* name;
    Function function;
    unsigned kind; // 0=MULT, 1=MULTU, 2=MULT1, 3=MADD
    unsigned bank;
};

Operation operations[] = {
    {"MULT_RD", generated_MULT_RD, 0, 0}, {"MULT_R0", generated_MULT_R0, 0, 0},
    {"MULTU_RD", generated_MULTU_RD, 1, 0}, {"MULTU_R0", generated_MULTU_R0, 1, 0},
    {"MULT1_RD", generated_MULT1_RD, 2, 1}, {"MULT1_R0", generated_MULT1_R0, 2, 1},
    {"MADD_RD", generated_MADD_RD, 3, 0}, {"MADD_R0", generated_MADD_R0, 3, 0},
};

struct RegisterMode { const char* name; int rs; int rt; int rd; bool same_sources; };
RegisterMode modes[] = {
    {"distinct", 1, 2, 3, false},
    {"rd_rs", 1, 2, 1, false},
    {"rd_rt", 1, 2, 2, false},
    {"same_sources", 1, 1, 3, true},
    {"all_alias", 1, 1, 1, true},
    {"rs_zero", 0, 2, 3, false},
    {"rt_zero", 1, 0, 3, false},
    {"both_sources_zero", 0, 0, 3, true},
    {"rd_zero", 1, 2, 0, false},
    {"rd_zero_same_sources", 1, 1, 0, true},
};

uint64_t sign_extend_word(uint32_t bits) {
    return (bits & 0x80000000u) ? (0xffffffff00000000ull | bits) : bits;
}

int64_t signed_word(uint32_t bits) {
    return std::bit_cast<int32_t>(bits);
}

uint64_t word_product(unsigned kind, uint32_t a, uint32_t b) {
    if (kind == 1) {
        const unsigned __int128 product = static_cast<unsigned __int128>(a) * b;
        return static_cast<uint64_t>(product);
    }
    const __int128 product = static_cast<__int128>(signed_word(a)) * signed_word(b);
    return static_cast<uint64_t>(static_cast<unsigned __int128>(product));
}

uint64_t madd_result(uint32_t a, uint32_t b, uint64_t hi, uint64_t lo) {
    const uint64_t accumulator = ((hi & 0xffffffffull) << 32) | (lo & 0xffffffffull);
    const __int128 product = static_cast<__int128>(signed_word(a)) * signed_word(b);
    const unsigned __int128 sum = static_cast<unsigned __int128>(accumulator)
                                + static_cast<unsigned __int128>(product);
    return static_cast<uint64_t>(sum); // architectural 64-bit modulo result
}

uint64_t upper_word(uint64_t result) { return sign_extend_word(static_cast<uint32_t>(result >> 32)); }
uint64_t lower_word(uint64_t result) { return sign_extend_word(static_cast<uint32_t>(result)); }

__m128i make_register(uint32_t low_word, uint64_t upper64) {
    return _mm_set_epi64x(static_cast<int64_t>(upper64), static_cast<int64_t>(sign_extend_word(low_word)));
}

void extract_register(__m128i value, uint64_t& low, uint64_t& high) {
    uint64_t lanes[2];
    _mm_storeu_si128(reinterpret_cast<__m128i*>(lanes), value);
    low = lanes[0];
    high = lanes[1];
}

bool matches_registers(const Context& actual, const Context& before, int rd, uint64_t rd_low) {
    for (int i = 0; i < 32; ++i) {
        if (i != rd || i == 0) {
            if (std::memcmp(&actual.r[i], &before.r[i], sizeof(__m128i)) != 0)
                return false;
        } else {
            uint64_t actual_low, actual_high, before_low, before_high;
            extract_register(actual.r[i], actual_low, actual_high);
            extract_register(before.r[i], before_low, before_high);
            if (actual_low != rd_low || actual_high != before_high)
                return false;
        }
    }
    return true;
}

bool run_case(const Operation& op, uint32_t a, uint32_t b, const RegisterMode& mode,
              uint64_t accumulatorSeed) {
    Context ctx{};
    for (int i = 0; i < 32; ++i)
        ctx.r[i] = make_register(static_cast<uint32_t>(0xa5100000u + i),
                                 0xfedc000000000000ull + static_cast<uint64_t>(i));
    // A nonzero register-zero sentinel catches a broken GPR[0] source or destination path.
    ctx.r[0] = _mm_set_epi64x(0x123456789abcdef0ll, 0x0badf00d76543210ll);
    ctx.r[1] = make_register(a, 0x1122334455667788ull);
    if (mode.rs == mode.rt && mode.rs != 0)
        ctx.r[mode.rs] = make_register(a, 0x1122334455667788ull);
    else if (mode.rt != 0)
        ctx.r[mode.rt] = make_register(b, 0x8877665544332211ull);
    ctx.hi = (accumulatorSeed & 0xffffffff00000000ull) | ((accumulatorSeed >> 7) & 0xffffffffull);
    ctx.lo = ((~accumulatorSeed) & 0xffffffff00000000ull) | (accumulatorSeed & 0xffffffffull);
    ctx.hi1 = (0x76543210ull << 32) | static_cast<uint32_t>(accumulatorSeed >> 17);
    ctx.lo1 = (0x89abcdefull << 32) | static_cast<uint32_t>(accumulatorSeed >> 3);
    const Context before = ctx;

    const uint32_t lhs = mode.rs == 0 ? 0 : a;
    const uint32_t rhs = mode.rt == 0 ? 0 : (mode.same_sources ? a : b);
    const uint64_t reference = op.kind == 3 ? madd_result(lhs, rhs, before.hi, before.lo)
                                            : word_product(op.kind, lhs, rhs);
    const uint64_t expected_lo = lower_word(reference);
    const uint64_t expected_hi = upper_word(reference);
    op.function(&ctx, mode.rd, mode.rs, mode.rt);

    const uint64_t expected_rd = (op.kind == 3 || op.kind == 0 || op.kind == 1 || op.kind == 2)
                                     ? expected_lo : 0;
    if (!matches_registers(ctx, before, mode.rd, expected_rd)) return false;
    if (op.bank == 0) {
        if (ctx.lo != expected_lo || ctx.hi != expected_hi) return false;
        if (ctx.lo1 != before.lo1 || ctx.hi1 != before.hi1) return false;
    } else {
        if (ctx.lo1 != expected_lo || ctx.hi1 != expected_hi) return false;
        if (ctx.lo != before.lo || ctx.hi != before.hi) return false;
    }
    return true;
}

int main() {
    constexpr uint32_t edges[] = {
        0, 1, 2, 3, 0x7fffffffu, 0x80000000u, 0xffffffffu, 0xfffffffeu,
        0x40000000u, 0xc0000000u, 0x0000ffffu, 0xffff0000u,
    };
    constexpr unsigned edgeCount = sizeof(edges) / sizeof(edges[0]);
    constexpr unsigned randomPairs = 20000;
    std::mt19937_64 random(0x1ee0626dULL);
    uint64_t checks[8]{};
    uint64_t mismatches[8]{};
    for (unsigned sample = 0; sample < edgeCount * edgeCount + randomPairs; ++sample) {
        const uint32_t a = sample < edgeCount * edgeCount ? edges[sample / edgeCount]
                                                           : static_cast<uint32_t>(random());
        const uint32_t b = sample < edgeCount * edgeCount ? edges[sample % edgeCount]
                                                           : static_cast<uint32_t>(random());
        const uint64_t accumulatorSeed = random();
        for (unsigned oi = 0; oi < 8; ++oi) {
            for (const auto& mode : modes) {
                ++checks[oi];
                RegisterMode invocation = mode;
                if (oi % 2 == 1) invocation.rd = 0; // _R0 templates are the rd==0 translator branch.
                if (!run_case(operations[oi], a, b, invocation, accumulatorSeed)) ++mismatches[oi];
            }
        }
    }
    std::printf("{\"names\":[");
    for (unsigned i = 0; i < 8; ++i) std::printf("%s\"%s\"", i ? "," : "", operations[i].name);
    std::printf("],\"checks\":[");
    for (unsigned i = 0; i < 8; ++i) std::printf("%s%llu", i ? "," : "", (unsigned long long)checks[i]);
    std::printf("],\"mismatches\":[");
    for (unsigned i = 0; i < 8; ++i) std::printf("%s%llu", i ? "," : "", (unsigned long long)mismatches[i]);
    std::printf("]}\n");
    for (uint64_t mismatch : mismatches) if (mismatch) return 1;
    return 0;
}
