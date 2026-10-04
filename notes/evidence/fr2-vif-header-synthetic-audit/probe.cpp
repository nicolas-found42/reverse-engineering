#include "runtime/ps2_memory.h"
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
void require(bool p,const char* why){if(!p)throw std::runtime_error(why);}
int main(){try{
 PS2Memory memory;require(memory.initialize(),"memory init");
 constexpr size_t bytes=16384;std::array<uint8_t,bytes> expected,untouched;
 untouched.fill(0xa5);std::array<uint32_t,22> packet{};
 packet[1]=0x6c058000;for(uint32_t i=0;i<20;i++)packet[i+2]=i+1;
 uint32_t callbacks=0;memory.setVu1MscalCallback([&](uint32_t,uint32_t,uint32_t){++callbacks;});
 memory.setVu1MscntCallback([&](uint32_t,uint32_t){++callbacks;});
 uint64_t contiguous=0,fragmented=0,dma=0,topDifferent=0,topEquivalent=0,tteNegative=0,goldenNegative=0;
 auto reset=[&](uint32_t top){memory.vif1_regs={};memory.vif1_regs.tops=top;
  uint32_t setup[]={0x05000000,0x01000404};memory.processVIF1Data(reinterpret_cast<uint8_t*>(setup),8);
  std::memcpy(memory.getVU1Data(),untouched.data(),bytes);};
 auto equal=[&](const auto&gold){return std::memcmp(memory.getVU1Data(),gold.data(),bytes)==0;};
 auto chain=[&](uint32_t chcr){
  // Authored CNT(5) -> REF(1) -> END(0). All tag/payload data is synthetic.
  const uint32_t tag[]={0x10000005,0,0,0x6c058000};
  for(uint32_t i=0;i<4;i++)memory.write32(0x1000+i*4,tag[i]);
  for(uint32_t i=0;i<20;i++)memory.write32(0x1010+i*4,packet[i+2]);
  const uint32_t rest[]={0x30000001,0x2000,0,0,0x70000000,0,0,0};
  for(uint32_t i=0;i<8;i++)memory.write32(0x1060+i*4,rest[i]);
  for(uint32_t i=0;i<4;i++)memory.write32(0x2000+i*4,0);
  memory.write32(0x10009020,0);memory.write32(0x10009030,0x1000);memory.write32(0x10009000,chcr);
  memory.processPendingTransfers();require((memory.read32(0x10009000)&0x100)==0,"DMA completion");
 };
 for(uint32_t top=0;top<1024;top++){
  expected=untouched;for(uint32_t q=0;q<5;q++)std::memcpy(expected.data()+((top+q)&1023)*16,packet.data()+2+q*4,16);
  reset(top);memory.processVIF1Data(reinterpret_cast<uint8_t*>(packet.data()),88);require(equal(expected),"contiguous TOPS mapping");++contiguous;
  require(*reinterpret_cast<uint32_t*>(memory.getVU1Data()+((top+3)&1023)*16+8)==15,"qword3 Z label");
  auto mutant=expected;mutant[0]^=1;require(!equal(mutant),"golden mutation detected");++goldenNegative;
  for(uint32_t chunk:{80u,16u,4u}){
   reset(top);memory.processVIF1Data(reinterpret_cast<uint8_t*>(packet.data()),8);
   for(uint32_t offset=8;offset<88;offset+=chunk)memory.processVIF1Data(reinterpret_cast<uint8_t*>(packet.data())+offset,chunk);
   require(equal(untouched)&&!equal(expected),"fragmented payload observation");++fragmented;
  }
  reset(top);chain(0x145);require(equal(expected),"TTE chain concatenation");++dma;
  reset(top);chain(0x105);require(equal(untouched)&&!equal(expected),"TTE-cleared negative control");++tteNegative;
  reset(top);packet[1]=0x6c050000;memory.processVIF1Data(reinterpret_cast<uint8_t*>(packet.data()),88);packet[1]=0x6c058000;
  if(top==0){require(equal(expected),"absolute/TOPS base zero equivalence");++topEquivalent;}
  else{require(!equal(expected),"TOP-relative flag change detected");++topDifferent;}
 }
 require(callbacks==0,"no VU callback execution");
 std::cout<<"{\"contiguous_cases\":"<<contiguous<<",\"fragmented_unchanged_memory_cases\":"<<fragmented<<",\"TTE_chain_cases\":"<<dma<<",\"TTE_cleared_negative_cases\":"<<tteNegative<<",\"TOP_flag_negative_different\":"<<topDifferent<<",\"TOP_flag_base_zero_equivalent\":"<<topEquivalent<<",\"one_byte_golden_negative_cases\":"<<goldenNegative<<",\"VU_callbacks\":"<<callbacks<<"}\n";
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
