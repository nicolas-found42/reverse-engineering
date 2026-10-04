#include "runtime/gs/gs_cpu_backend.h"

#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

void require(bool condition, const char *message)
{
    if (!condition)
        throw std::runtime_error(message);
}

int main()
{
    try
    {
        std::vector<uint8_t> vram(4 * 1024 * 1024);
        GSCpuBackend backend;
        backend.Initialize(vram.data(), vram.size());

        constexpr std::array<uint32_t, 3> bases = {32, 64, 96};
        constexpr std::array<uint32_t, 3> colors = {
            0x800000ff, 0x8000ff00, 0x80ff0000};
        constexpr uint64_t miptbp1 = 64ull | (1ull << 14) |
                                     (96ull << 20) | (1ull << 34);

        for (uint32_t level = 0; level < 3; ++level)
        {
            const uint32_t size = 8u >> level;
            for (uint32_t y = 0; y < size; ++y)
                for (uint32_t x = 0; x < size; ++x)
                    backend.WriteVram(0, bases[level], 1, x, y,
                                      colors[level]);
        }

        uint32_t total = 0;
        uint32_t fixedMismatches = 0;
        uint32_t redirects = 0;
        uint32_t qCases = 0;
        uint32_t qMismatches = 0;
        std::cout << "[";

        // Preserve the original 10 fixed-LOD and TEX0-redirection cases.
        for (uint32_t fst : {0u, 1u})
        {
            for (uint32_t target = 0; target < 3; ++target)
            {
                const uint32_t redirectCount = target == 0 ? 1u : 2u;
                for (uint32_t redirect = 0; redirect < redirectCount;
                     ++redirect)
                {
                    GSPrimitiveBatch batch{};
                    batch.vertexCount = 2;
                    auto &state = batch.state;
                    auto &context = state.context;
                    state.prim.type = GS_PRIM_SPRITE;
                    state.prim.tme = true;
                    state.prim.fst = fst;
                    state.textureWidth = redirect ? (8u >> target) : 8;
                    state.textureHeight = state.textureWidth;
                    context.tex0.tbp0 = redirect ? bases[target] : bases[0];
                    context.tex0.tbw = 1;
                    context.tex0.psm = 0;
                    context.tex0.tw = redirect ? 3 - target : 3;
                    context.tex0.th = context.tex0.tw;
                    context.tex0.tcc = 1;
                    context.tex0.tfx = 1;
                    context.frame.fbp = 128;
                    context.frame.fbw = 1;
                    context.frame.psm = 0;
                    context.scissor = {0, 1, 0, 1};
                    context.zbuf.zmask = true;
                    context.test = 1ull << 17;
                    context.tex1 = 1ull | (2ull << 2) | (2ull << 6) |
                                   (static_cast<uint64_t>(target * 16u) << 32);
                    context.miptbp1 = miptbp1;

                    batch.vertices[0].x = 0;
                    batch.vertices[0].y = 0;
                    batch.vertices[1].x = 2;
                    batch.vertices[1].y = 2;
                    for (auto &vertex : batch.vertices)
                    {
                        vertex.q = 1;
                        vertex.r = 128;
                        vertex.g = 128;
                        vertex.b = 128;
                        vertex.a = 128;
                        vertex.u = 8;
                        vertex.v = 8;
                        vertex.s = 0.0625f;
                        vertex.t = 0.0625f;
                    }

                    for (uint32_t y = 0; y < 2; ++y)
                        for (uint32_t x = 0; x < 2; ++x)
                            backend.WriteVram(0, 4096, 1, x, y, 0);
                    backend.Submit(batch);
                    const uint32_t actual = backend.ReadVram(0, 4096, 1, 0, 0);
                    const uint32_t sourceExpected =
                        colors[redirect ? target : 0];
                    require(actual == sourceExpected,
                            "observed fixed-mode TEX0 plane");
                    for (uint32_t y = 0; y < 2; ++y)
                        for (uint32_t x = 0; x < 2; ++x)
                            require(backend.ReadVram(0, 4096, 1, x, y) == actual,
                                    "four fixed-mode output pixels");

                    if (!redirect && target > 0)
                    {
                        require(actual != colors[target],
                                "manual fixed-LOD disagreement detected");
                        ++fixedMismatches;
                    }
                    if (redirect)
                    {
                        require(actual == colors[target],
                                "redirected plane readable");
                        ++redirects;
                    }

                    if (total++)
                        std::cout << ",";
                    std::cout << "{\"mode\":\"fixed\",\"fst\":" << fst
                              << ",\"fixed_LOD\":" << target
                              << ",\"TEX0_redirect\":" << redirect
                              << ",\"actual_rgba\":" << actual
                              << ",\"manual_expected_rgba\":"
                              << colors[target]
                              << ",\"TEX1\":" << context.tex1
                              << ",\"MIPTBP1\":" << context.miptbp1
                              << "}";
                }
            }
        }
        require(total == 10 && fixedMismatches == 4 && redirects == 4,
                "original fixed-mode case cardinalities");

        // LCM=0 with L=0,K=0: for homogeneous per-sprite Q, the Sony
        // manual predicts LOD 0/1/2 for Q 1/0.5/0.25 even with UV coords.
        constexpr std::array<float, 3> qValues = {1.0f, 0.5f, 0.25f};
        for (uint32_t fst : {0u, 1u})
        {
            for (uint32_t expectedLod = 0; expectedLod < 3; ++expectedLod)
            {
                GSPrimitiveBatch batch{};
                batch.vertexCount = 2;
                auto &state = batch.state;
                auto &context = state.context;
                state.prim.type = GS_PRIM_SPRITE;
                state.prim.tme = true;
                state.prim.fst = fst;
                state.textureWidth = 8;
                state.textureHeight = 8;
                context.tex0.tbp0 = bases[0];
                context.tex0.tbw = 1;
                context.tex0.psm = 0;
                context.tex0.tw = 3;
                context.tex0.th = 3;
                context.tex0.tcc = 1;
                context.tex0.tfx = 1;
                context.frame.fbp = 128;
                context.frame.fbw = 1;
                context.frame.psm = 0;
                context.scissor = {0, 1, 0, 1};
                context.zbuf.zmask = true;
                context.test = 1ull << 17;
                context.tex1 = (2ull << 2) | (2ull << 6); // LCM=0,L=0,K=0
                context.miptbp1 = miptbp1;

                batch.vertices[0].x = 0;
                batch.vertices[0].y = 0;
                batch.vertices[1].x = 2;
                batch.vertices[1].y = 2;
                for (auto &vertex : batch.vertices)
                {
                    vertex.q = qValues[expectedLod];
                    vertex.r = 128;
                    vertex.g = 128;
                    vertex.b = 128;
                    vertex.a = 128;
                    vertex.u = 8;
                    vertex.v = 8;
                    vertex.s = 0.0625f;
                    vertex.t = 0.0625f;
                }

                for (uint32_t y = 0; y < 2; ++y)
                    for (uint32_t x = 0; x < 2; ++x)
                        backend.WriteVram(0, 4096, 1, x, y, 0);
                backend.Submit(batch);
                const uint32_t actual = backend.ReadVram(0, 4096, 1, 0, 0);
                bool uniform = true;
                for (uint32_t y = 0; y < 2; ++y)
                    for (uint32_t x = 0; x < 2; ++x)
                        uniform = uniform &&
                                  backend.ReadVram(0, 4096, 1, x, y) == actual;
                const bool mismatch = actual != colors[expectedLod];
                if (mismatch)
                    ++qMismatches;
                ++qCases;
                if (total++)
                    std::cout << ",";
                std::cout << "{\"mode\":\"q_based\",\"fst\":" << fst
                          << ",\"q\":" << qValues[expectedLod]
                          << ",\"manual_Q_LOD\":" << expectedLod
                          << ",\"TEX0_redirect\":0,\"actual_rgba\":" << actual
                          << ",\"manual_expected_rgba\":"
                          << colors[expectedLod]
                          << ",\"four_pixels_uniform\":" << uniform
                          << ",\"TEX1\":" << context.tex1
                          << ",\"MIPTBP1\":" << context.miptbp1 << "}";
            }
        }
        require(qCases == 6 && total == 16, "Q-sweep case cardinalities");
        std::cout << "]\n";
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
