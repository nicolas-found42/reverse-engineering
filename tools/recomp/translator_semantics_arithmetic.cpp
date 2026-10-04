#include <array>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <random>
#include <stdexcept>
#include <tuple>

struct Result64 { uint64_t bits; bool overflow; };
static Result64 dadd(uint64_t a, uint64_t b) {
    uint64_t r = a + b;
    bool ov = ((~(a ^ b) & (a ^ r)) >> 63) != 0;
    return {r, ov};
}
static Result64 dsub(uint64_t a, uint64_t b) {
    uint64_t r = a - b;
    bool ov = (((a ^ b) & (a ^ r)) >> 63) != 0;
    return {r, ov};
}
static Result64 daddi(uint64_t a, int16_t imm) {
    uint64_t b = static_cast<uint64_t>(static_cast<int64_t>(imm));
    uint64_t r = a + b;
    bool ov = ((~(a ^ b) & (a ^ r)) >> 63) != 0;
    return {r, ov};
}
static Result64 daddiu(uint64_t a, int16_t imm) {
    uint64_t b = static_cast<uint64_t>(static_cast<int64_t>(imm));
    return {a + b, false};
}
static bool ref_dadd(uint64_t a, uint64_t b, uint64_t& out) {
    __int128 x = static_cast<__int128>(std::bit_cast<int64_t>(a));
    __int128 y = static_cast<__int128>(std::bit_cast<int64_t>(b));
    __int128 z = x + y;
    out = static_cast<uint64_t>(z);
    return z > std::numeric_limits<int64_t>::max() || z < std::numeric_limits<int64_t>::min();
}
static bool ref_dsub(uint64_t a, uint64_t b, uint64_t& out) {
    __int128 x = static_cast<__int128>(std::bit_cast<int64_t>(a));
    __int128 y = static_cast<__int128>(std::bit_cast<int64_t>(b));
    __int128 z = x - y;
    out = static_cast<uint64_t>(z);
    return z > std::numeric_limits<int64_t>::max() || z < std::numeric_limits<int64_t>::min();
}
static void require(bool cond, const char* what) { if (!cond) throw std::runtime_error(what); }

struct AddiOutcome { bool exception; bool wrote; int64_t value; };
static AddiOutcome addi_model(int32_t src, int16_t imm, unsigned rt) {
    int64_t wide = static_cast<int64_t>(src) + static_cast<int64_t>(imm);
    bool ov = wide > INT32_MAX || wide < INT32_MIN;
    if (ov) return {true, false, 0}; // exception return precedes setter, even for rt=0
    return {false, rt != 0, rt != 0 ? static_cast<int64_t>(static_cast<int32_t>(wide)) : 0};
}
static void test_addi_zero() {
    for (auto [src, imm] : {std::pair<int32_t,int16_t>{INT32_MAX,1}, {INT32_MIN,-1}, {4,3}}) {
        auto zero = addi_model(src, imm, 0);
        bool expected_ov = (static_cast<int64_t>(src) + imm > INT32_MAX) || (static_cast<int64_t>(src) + imm < INT32_MIN);
        require(zero.exception == expected_ov, "ADDI rt=0 exception behavior");
        require(!zero.wrote, "ADDI rt=0 must not write");
        auto nonzero = addi_model(src, imm, 7);
        require(nonzero.exception == expected_ov, "ADDI normal destination exception behavior");
        require(nonzero.wrote == !expected_ov, "ADDI normal destination write behavior");
    }
}

int main() {
    constexpr std::array<uint64_t, 17> vals = {
        0, 1, 2, 0x7ffffffffffffffeull, 0x7fffffffffffffffull,
        0x8000000000000000ull, 0x8000000000000001ull,
        0xfffffffffffffffeull, 0xffffffffffffffffull,
        0x00000000ffffffffull, 0xffffffff00000000ull,
        0x5555555555555555ull, 0xaaaaaaaaaaaaaaaaull,
        0x0000000100000000ull, 0x00000000fffffffeull,
        0x7fff000000000000ull, 0x8000ffffffffffffull
    };
    size_t pairs = 0;
    for (uint64_t a : vals) for (uint64_t b : vals) {
        uint64_t out = 0;
        bool expected = ref_dadd(a, b, out);
        auto actual = dadd(a, b);
        require(actual.bits == out && actual.overflow == expected, "DADD edge-grid mismatch");
        expected = ref_dsub(a, b, out);
        actual = dsub(a, b);
        require(actual.bits == out && actual.overflow == expected, "DSUB edge-grid mismatch");
        auto unsigned_sum = daddiu(a, static_cast<int16_t>(b));
        uint64_t imm = static_cast<uint64_t>(static_cast<int64_t>(static_cast<int16_t>(b)));
        require(unsigned_sum.bits == a + imm && !unsigned_sum.overflow, "DADDIU modulo mismatch");
        ++pairs;
    }
    for (uint64_t a : vals) for (int32_t imm : {-32768, -1, 0, 1, 32767}) {
        uint64_t out = 0;
        bool expected = ref_dadd(a, static_cast<uint64_t>(static_cast<int64_t>(imm)), out);
        auto actual = daddi(a, static_cast<int16_t>(imm));
        require(actual.bits == out && actual.overflow == expected, "DADDI edge-grid mismatch");
        auto u = daddiu(a, static_cast<int16_t>(imm));
        require(u.bits == a + static_cast<uint64_t>(static_cast<int64_t>(imm)) && !u.overflow, "DADDIU immediate grid mismatch");
    }
    // Deterministic random coverage for bit-pattern overflow predicates.
    std::mt19937_64 rng(0x5eed1234);
    for (int i = 0; i < 100000; ++i) {
        uint64_t a = rng(), b = rng(), out = 0;
        bool expected = ref_dadd(a,b,out); auto actual=dadd(a,b);
        require(actual.bits==out && actual.overflow==expected, "DADD random mismatch");
        expected = ref_dsub(a,b,out); actual=dsub(a,b);
        require(actual.bits==out && actual.overflow==expected, "DSUB random mismatch");
        int16_t imm = static_cast<int16_t>(rng());
        expected=ref_dadd(a,static_cast<uint64_t>(static_cast<int64_t>(imm)),out);
        auto ai=daddi(a,imm); require(ai.bits==out && ai.overflow==expected, "DADDI random mismatch");
        auto au=daddiu(a,imm); require(au.bits==a+static_cast<uint64_t>(static_cast<int64_t>(imm)) && !au.overflow, "DADDIU random mismatch");
    }
    test_addi_zero();
    std::printf("PASS pairs=%zu randomized=100000 ADDI_zero_cases=3\n", pairs);
}
