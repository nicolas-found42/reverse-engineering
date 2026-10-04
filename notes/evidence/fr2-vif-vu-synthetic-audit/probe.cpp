#include "runtime/ps2_memory.h"
#include "runtime/ps2_vu1.h"
#include "runtime/gs/gs_frontend.h"
#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>
#include <stdexcept>
void require(bool p,const char* m){if(!p)throw std::runtime_error(m);}
uint32_t command(uint32_t op,uint32_t imm=0){return (op<<24)|imm;}
uint32_t special(uint32_t op,uint32_t vi){return (0x40u<<25)|(vi<<16)|((op&0x7c)<<4)|(op&3)|0x3c;}
void pair(uint8_t* code,uint32_t pc,uint32_t lower,uint32_t upper){std::memcpy(code+pc,&lower,4);std::memcpy(code+pc+4,&upper,4);}
int main(int argc,char**){try{
 PS2Memory memory;require(memory.initialize(),"memory init");GS gs;
 uint64_t vif=0,orders=0,vu=0,negative=0;
 uint32_t gotTop=0,gotItop=0,gotPC=0,calls=0;
 memory.setVu1MscntCallback([&](uint32_t t,uint32_t i){gotTop=t;gotItop=i;++calls;});
 memory.setVu1MscalCallback([&](uint32_t pc,uint32_t t,uint32_t i){gotPC=pc;gotTop=t;gotItop=i;++calls;});
 for(uint32_t i=0;i<1024;i++)for(uint32_t dbf=0;dbf<2;dbf++)for(uint32_t op:{0x14u,0x17u}){
  auto&r=memory.vif1_regs;r={};r.base=i;r.ofst=1023-i;r.tops=i^0x155;r.itops=(i*37)&1023;r.stat=dbf<<7;
  calls=0;uint32_t cmd=command(op,op==0x14?17:0);memory.processVIF1Data(reinterpret_cast<uint8_t*>(&cmd),4);
  require(calls==1&&gotTop==(i^0x155)&&gotItop==((i*37)&1023),"VIF latch");
  require(r.top==gotTop&&r.itop==gotItop&&r.tops==(dbf?i:1023)&&((r.stat>>7)&1)==(dbf^1),"VIF advance");
  if(op==0x14)require(gotPC==136,"MSCAL pc");++vif;
  if(dbf==0&&op==0x14){
  r={};r.base=43;r.ofst=27;r.tops=i;r.itops=12;calls=0;
  uint32_t first=command(0x17);memory.processVIF1Data(reinterpret_cast<uint8_t*>(&first),4);require(gotTop==i,"old TOPS latch");
  uint32_t tail[]={command(3,i^0x2aa),command(2,0)};memory.processVIF1Data(reinterpret_cast<uint8_t*>(tail),8);
  require(r.tops==(i^0x2aa)&&((r.stat>>7)&1)==0&&gotTop==i,"post MSCNT base offset order");
  memory.processVIF1Data(reinterpret_cast<uint8_t*>(&first),4);require(gotTop==(i^0x2aa)&&calls==2,"later MSCNT TOP");++orders;
  }
 }
 uint8_t code[256],data[256]={};const uint32_t nop=0x8000033c,upper=0x2ff,E=0x40000000;
 for(uint32_t top=0;top<1024;top++)for(uint32_t start:{0u,8u,64u,128u}){
  for(uint32_t p=0;p<256;p+=8)pair(code,p,nop,upper);
  pair(code,start,nop,upper|(argc>1?0:E));
  // Independent synthetic IADDIU vi4,vi0,7 is encoded from its documented opcode.
  pair(code,start+8,(8u<<25)|(4u<<16)|7u,upper);
  pair(code,start+16,special(0x68,2),upper);pair(code,start+24,special(0x69,3),upper);
  pair(code,start+32,nop,upper|E);pair(code,start+40,nop,upper);
  pair(code,start+48,(8u<<25)|(5u<<16)|9u,upper);
  VU1Interpreter interp;
  interp.execute(code,256,data,256,gs,nullptr,start,0x77,0x88,32);
  bool stopped=interp.state().pc==start+16&&interp.state().vi[4]==7&&interp.state().vi[2]==0&&interp.state().vi[3]==0;
  if(argc>1){require(!stopped,"E clear mutant survived");++negative;continue;}
  require(stopped,"E-stop/delay/TPC");
  interp.resume(code,256,data,256,gs,nullptr,top,1023-top,32);
  require(interp.state().pc==start+48&&interp.state().vi[2]==static_cast<int>(top)&&interp.state().vi[3]==static_cast<int>(1023-top)&&interp.state().vi[5]==0,"resume XTOP/XITOP and second stop");
  ++vu;
 }
 std::cout<<"{\"vif_latch_cases\":"<<vif<<",\"packet_order_cases\":"<<orders<<",\"vu_stop_resume_cases\":"<<vu<<",\"negative_detected\":"<<negative<<"}\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
