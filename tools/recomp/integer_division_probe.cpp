// SPDX-License-Identifier: GPL-3.0-only
// Synthetic widened arithmetic oracle; no game routine or input is used.
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <random>
#include "division_templates.h"
using Fn = void(*)(Context*,int,int);
Fn functions[] = {generated_DIV,generated_DIVU,generated_DIV1,generated_DIVU1};
const char* names[] = {"DIV","DIVU","DIV1","DIVU1"};
uint64_t extend(uint32_t bits) {
    return uint64_t(bits) | ((bits & 0x80000000u) ? 0xffffffff00000000ull : 0);
}
int64_t signed_word(uint32_t bits) {
    return int64_t(bits) - ((bits & 0x80000000u) ? 0x100000000ll : 0);
}
void reference(unsigned op,uint32_t a,uint32_t b,uint64_t& lo,uint64_t& hi) {
    if (op % 2 == 0) {
        const int64_t dividend=signed_word(a), divisor=signed_word(b);
        if (divisor == 0) {
            lo=dividend<0 ? 1 : UINT64_MAX; hi=extend(a);
        } else {
            // Widening makes INT32_MIN/-1 defined; extension takes low32 bits.
            lo=extend(uint32_t(dividend/divisor)); hi=extend(uint32_t(dividend%divisor));
        }
    } else if (b == 0) { lo=UINT64_MAX; hi=extend(a); }
    else {lo=extend(a/b); hi=extend(a%b);}
}
int main() {
    constexpr uint32_t edges[]={0,1,2,0x7fffffffu,0x80000000u,0xffffffffu,
                               0xfffffffeu,0x40000000u,0xc0000000u,17};
    std::mt19937 random(5900123);
    uint64_t checks[4]={},mismatches[4]={};
    for (int sample=0;sample<100100;sample++) {
        const uint32_t a=sample<100 ? edges[sample/10] : random();
        const uint32_t b=sample<100 ? edges[sample%10] : random();
        for (int mode=0;mode<6;mode++) for (unsigned op=0;op<4;op++) {
            Context ctx{};
            for (int i=0;i<32;i++) ctx.r[i]=_mm_set_epi32(0x12345678,0x4bad0000+i,0x7ed00000+i,0x5ab00000+i);
            // Registers are valid sign-extended words in their low64 lane.
            ctx.r[1]=_mm_set_epi64x(0x1234567812345678ll,static_cast<int64_t>(extend(a)));
            ctx.r[2]=_mm_set_epi64x(0x2345678923456789ll,static_cast<int64_t>(extend(b)));
            int rs=1,rt=2;
            if(mode==1) {rs=2;rt=1;}
            if(mode==2) rs=0;
            if(mode==3) rt=0;
            if(mode==4) {rs=1;rt=1;}
            if(mode==5) {rs=0;rt=0;}
            uint32_t aa=rs==0 ? 0 : rs==1 ? a : b;
            uint32_t bb=rt==0 ? 0 : rt==1 ? a : b;
            ctx.hi=0x1111222233334444ull;ctx.lo=0x2222333344445555ull;
            ctx.hi1=0x3333444455556666ull;ctx.lo1=0x4444555566667777ull;
            Context before=ctx;uint64_t expected_lo=0,expected_hi=0;
            reference(op,aa,bb,expected_lo,expected_hi);
            functions[op](&ctx,rs,rt);checks[op]++;
            bool failed=std::memcmp(ctx.r,before.r,sizeof(ctx.r))!=0;
            if(op<2) failed |= ctx.lo!=expected_lo || ctx.hi!=expected_hi || ctx.lo1!=before.lo1 || ctx.hi1!=before.hi1;
            else failed |= ctx.lo1!=expected_lo || ctx.hi1!=expected_hi || ctx.lo!=before.lo || ctx.hi!=before.hi;
            if(failed) mismatches[op]++;
        }
    }
    std::printf("{\"names\":[");for(int i=0;i<4;i++)std::printf("%s\"%s\"",i?",":"",names[i]);
    std::printf("],\"checks\":[");for(int i=0;i<4;i++)std::printf("%s%llu",i?",":"",(unsigned long long)checks[i]);
    std::printf("],\"mismatches\":[");for(int i=0;i<4;i++)std::printf("%s%llu",i?",":"",(unsigned long long)mismatches[i]);
    std::printf("]}\n");
    for(unsigned i=0;i<4;i++)if(mismatches[i])return 1;
    return 0;
}
