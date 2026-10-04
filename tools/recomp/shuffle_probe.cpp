// SPDX-License-Identifier: GPL-3.0-only
// Synthetic register tests; contains no original game routine.
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <random>
#include "probe_translations.h"
int main(){
 using Fn=void(*)(Context*,int,int);
 Fn funcs[]={generated_PEXEW,generated_PEXCW,generated_PROT3W,generated_PROT3W_macro};
 const unsigned expected[4][4]={{2,1,0,3},{0,2,1,3},{1,2,0,3},{1,2,0,3}};
 uint64_t mismatches[4]={0,0,0,0};
 uint64_t checks[4]={0,0,0,0};
 std::mt19937 gen(5900);
 for(int sample=0;sample<10004;sample++){
  uint32_t lanes[4];
  for(unsigned i=0;i<4;i++) lanes[i]=sample<4?(i==unsigned(sample)?0xa5a55a5a:0):gen();
  for(unsigned op=0;op<4;op++)for(unsigned mode=0;mode<4;mode++){
   Context ctx{};ctx.r[0]=_mm_set1_epi32(0x11223344);
   const int rt=mode==2?0:1,rd=mode==0?1:(mode==3?0:2);
   ctx.r[1]=_mm_loadu_si128(reinterpret_cast<const __m128i*>(lanes));
   ctx.r[2]=_mm_set1_epi32(0xdeadbeef);
   uint32_t want[4],actual[4];
   for(unsigned i=0;i<4;i++)want[i]=rd==0?0x11223344u:(rt==0?0:lanes[expected[op][i]]);
   funcs[op](&ctx,rd,rt);
   _mm_storeu_si128(reinterpret_cast<__m128i*>(actual),ctx.r[rd]);
   checks[op]++;if(std::memcmp(want,actual,16))mismatches[op]++;
  }
 }
 std::printf("{\"checks\":[%llu,%llu,%llu,%llu],\"mismatches\":[%llu,%llu,%llu,%llu]}\n",(unsigned long long)checks[0],(unsigned long long)checks[1],(unsigned long long)checks[2],(unsigned long long)checks[3],(unsigned long long)mismatches[0],(unsigned long long)mismatches[1],(unsigned long long)mismatches[2],(unsigned long long)mismatches[3]);
 return mismatches[0]||mismatches[1]||mismatches[2]||mismatches[3]?1:0;
}
