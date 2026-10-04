#include "runtime/gs/gs_cpu_backend.h"
#include <vector>
#include <cstdint>
#include <cstring>
#include <cstdio>
int main(){
 std::vector<uint8_t> vram(4u*1024u*1024u);
 GSCpuBackend backend;backend.Initialize(vram.data(),vram.size());
 for(uint32_t bits:{32u,16u,8u,4u})for(uint32_t bw:{0u,1u}){
  uint32_t width=bits>=16?64:128,height=bits==32?64:bits==16?128:bits==8?128:256;
  uint32_t psm=bits==32?0:bits==16?2:bits==8?19:20;
  std::vector<uint8_t> data(width*height*bits/8);
  for(uint32_t pixel=0;pixel<width*height;pixel++){
   uint32_t label=(pixel*2654435761u)^(pixel>>5)^0x91a2b3c4u;
   if(bits==4)data[pixel/2]|=static_cast<uint8_t>((label&15u)<<((pixel&1u)*4));
   else for(uint32_t b=0;b<bits/8;b++)data[pixel*(bits/8)+b]=static_cast<uint8_t>(label>>(8*b));
  }
  std::fill(vram.begin(),vram.end(),0);
  GSTransferCommand transfer;transfer.direction=0;transfer.bitbltbuf.dbp=33;transfer.bitbltbuf.dbw=bw;transfer.bitbltbuf.dpsm=psm;transfer.trxreg.rrw=width;transfer.trxreg.rrh=height;
  backend.BeginTransfer(transfer);backend.UploadImage(data.data(),data.size());
  if(std::fwrite(vram.data(),1,vram.size(),stdout)!=vram.size())return 2;
 }
 return std::ferror(stdout)?3:0;
}
