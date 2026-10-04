// SPDX-License-Identifier: GPL-3.0-only
// Synthetic independent byte/word oracle; no game input or routine is used.
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <random>
#include "probe_translations.h"
using Fn=void(*)(Context*,int,int,int);
Fn funcs[]={generated_PCPYLD,generated_PCPYUD,generated_PCPYH,generated_PEXTLW,generated_PEXTUW,generated_PEXTLH,generated_PEXTLB,generated_PAND,generated_POR,generated_PNOR,generated_PXOR,generated_PSUBB,generated_PSUBW};
const char* names[]={"PCPYLD","PCPYUD","PCPYH","PEXTLW","PEXTUW","PEXTLH","PEXTLB","PAND","POR","PNOR","PXOR","PSUBB","PSUBW"};
void store(__m128i v,uint8_t* p){_mm_storeu_si128(reinterpret_cast<__m128i*>(p),v);}
__m128i load(const uint8_t* p){return _mm_loadu_si128(reinterpret_cast<const __m128i*>(p));}
uint32_t word(const uint8_t* p,int i){uint32_t v;std::memcpy(&v,p+4*i,4);return v;}
void putword(uint8_t* p,int i,uint32_t v){std::memcpy(p+4*i,&v,4);}
void ref(unsigned op,const uint8_t* a,const uint8_t* b,uint8_t* o){
 std::memset(o,0,16);
 switch(op){
 case 0: std::memcpy(o,b,8);std::memcpy(o+8,a,8);break;
 case 1: std::memcpy(o,a+8,8);std::memcpy(o+8,b+8,8);break;
 case 2: for(int i=0;i<8;i++){const uint8_t* x=b+(i<4?0:8);o[2*i]=x[0];o[2*i+1]=x[1];}break;
 case 3: for(int i=0;i<2;i++){putword(o,2*i,word(b,i));putword(o,2*i+1,word(a,i));}break;
 case 4: for(int i=0;i<2;i++){putword(o,2*i,word(b,i+2));putword(o,2*i+1,word(a,i+2));}break;
 case 5: for(int i=0;i<4;i++){o[4*i]=b[2*i];o[4*i+1]=b[2*i+1];o[4*i+2]=a[2*i];o[4*i+3]=a[2*i+1];}break;
 case 6: for(int i=0;i<8;i++){o[2*i]=b[i];o[2*i+1]=a[i];}break;
 case 7: for(int i=0;i<16;i++)o[i]=a[i]&b[i];break;
 case 8: for(int i=0;i<16;i++)o[i]=a[i]|b[i];break;
 case 9: for(int i=0;i<16;i++)o[i]=uint8_t(~(a[i]|b[i]));break;
 case 10:for(int i=0;i<16;i++)o[i]=a[i]^b[i];break;
 case 11:for(int i=0;i<16;i++)o[i]=uint8_t(a[i]-b[i]);break;
 case 12:for(int i=0;i<4;i++)putword(o,i,word(a,i)-word(b,i));break;
 }
}
int main(){
 constexpr int N=10012, M=8, O=13;
 uint64_t checks[O]={},mismatches[O]={}; std::mt19937 gen(5900);
 for(int sample=0;sample<N;sample++){
  uint8_t a[16],b[16];
  if(sample<4){std::memset(a,0,16);std::memset(b,0,16);a[4*sample]=0xa5;b[4*((sample+1)%4)]=0x5a;}
  else if(sample<12){std::memset(a,0,16);std::memset(b,0,16);if(sample%4==1)std::memset(a,0xff,16);if(sample%4==2)std::memset(b,1,16);if(sample%4==3){for(int i=0;i<16;i++){a[i]=(i%2)?0xff:0;b[i]=(i%2)?0:0xff;}}}
  else for(int i=0;i<16;i++){a[i]=uint8_t(gen());b[i]=uint8_t(gen());}
  for(int mode=0;mode<M;mode++)for(int op=0;op<O;op++){
   int rs=1,rt=2,rd=3;
   switch(mode){case 1:rs=1;rt=2;rd=1;break;case 2:rs=2;rt=1;rd=1;break;case 3:rs=1;rt=2;rd=0;break;case 4:rs=0;rt=2;rd=3;break;case 5:rs=1;rt=0;rd=3;break;case 6:rs=0;rt=0;rd=3;break;case 7:rs=1;rt=1;rd=1;break;}
   uint8_t aa[16],bb[16],zero[16]={},want[16],actual[16];
   std::memcpy(aa,rs==0?zero:(rs==1?a:b),16);std::memcpy(bb,rt==0?zero:(rt==1?a:b),16);
   Context ctx{};ctx.r[0]=_mm_set1_epi32(0x6badf00d);ctx.r[1]=load(a);ctx.r[2]=load(b);ctx.r[3]=_mm_set1_epi32(0xdeadbeef);
   uint8_t sentinel[16];store(ctx.r[0],sentinel);
   ref(op,aa,bb,want);funcs[op](&ctx,rd,rs,rt);store(ctx.r[rd],actual);
   if(rd==0)std::memcpy(want,sentinel,16);
   checks[op]++;if(std::memcmp(want,actual,16))mismatches[op]++;
  }
 }
 std::printf("{\"names\":[");for(int i=0;i<O;i++)std::printf("%s\"%s\"",i?",":"",names[i]);
 std::printf("],\"checks\":[");for(int i=0;i<O;i++)std::printf("%s%llu",i?",":"",(unsigned long long)checks[i]);
 std::printf("],\"mismatches\":[");for(int i=0;i<O;i++)std::printf("%s%llu",i?",":"",(unsigned long long)mismatches[i]);std::printf("]}\n");
 for(int i=0;i<O;i++)if(mismatches[i])return 1;return 0;
}
