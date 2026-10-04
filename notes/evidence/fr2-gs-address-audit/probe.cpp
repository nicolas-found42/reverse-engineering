#include "runtime/gs/ps2_gs_psmct32.h"
#include "runtime/gs/ps2_gs_psmct16.h"
#include "runtime/gs/ps2_gs_psmt8.h"
#include "runtime/gs/ps2_gs_psmt4.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
int main(int argc,char** argv){
 if(argc!=2)return 2;
 const bool mutant=argv[1][0]=='1';
 const std::array<uint32_t,6> bases={0,1,31,32,33,16383};
 const std::array<uint32_t,4> widths={1,2,4,8};
 for(uint32_t bits:{32u,16u,8u,4u}){
  uint32_t xmax=(bits>=16?128:256),ymax=(bits==32?64:bits==16?128:bits==8?128:256);
  for(uint32_t width:widths){if(bits<=8 && width==1)continue;
   for(uint32_t base:bases)for(uint32_t y=0;y<ymax;y++)for(uint32_t x=0;x<xmax;x++){
    uint32_t a=bits==32?GSPSMCT32::addrPSMCT32(base,width,x,y):bits==16?GSPSMCT16::addrPSMCT16(base,width,x,y):bits==8?GSPSMT8::addrPSMT8(base,width,x,y):GSPSMT4::addrPSMT4(base,width,x,y);
    if(mutant)a^=1u;
    if(std::fwrite(&a,sizeof(a),1,stdout)!=1)return 3;
   }
  }
 }
 return std::ferror(stdout)?4:0;
}
