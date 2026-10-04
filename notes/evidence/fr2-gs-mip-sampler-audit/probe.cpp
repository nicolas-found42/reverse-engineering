#include "runtime/gs/gs_cpu_backend.h"
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
void require(bool p,const char*why){if(!p)throw std::runtime_error(why);}
int main(){try{
 std::vector<uint8_t> vram(4*1024*1024);GSCpuBackend backend;backend.Initialize(vram.data(),vram.size());
 constexpr std::array<uint32_t,3> bases={32,64,96},colors={0x800000ff,0x8000ff00,0x80ff0000};
 for(uint32_t level=0;level<3;level++)for(uint32_t y=0;y<(8u>>level);y++)for(uint32_t x=0;x<(8u>>level);x++)
  backend.WriteVram(0,bases[level],1,x,y,colors[level]);
 uint32_t total=0,manualMismatch=0,redirected=0;
 std::cout<<"[";
 for(uint32_t fst:{0u,1u})for(uint32_t target=0;target<3;target++)for(uint32_t redirect=0;redirect<(target==0?1u:2u);redirect++){
  GSPrimitiveBatch batch{};batch.vertexCount=2;auto&s=batch.state;auto&c=s.context;
  s.prim.type=GS_PRIM_SPRITE;s.prim.tme=true;s.prim.fst=fst;s.textureWidth=redirect?(8u>>target):8;s.textureHeight=s.textureWidth;
  c.tex0.tbp0=redirect?bases[target]:bases[0];c.tex0.tbw=1;c.tex0.psm=0;c.tex0.tw=redirect?3-target:3;c.tex0.th=c.tex0.tw;c.tex0.tcc=1;c.tex0.tfx=1;
  c.frame.fbp=128;c.frame.fbw=1;c.frame.psm=0;c.scissor={0,1,0,1};c.zbuf.zmask=true;c.test=1ull<<17;
  c.tex1=1ull|(2ull<<2)|(2ull<<6)|(uint64_t(target*16u)<<32); // Fixed LOD, MXL2, point mip nearest; K s7.4.
  c.miptbp1=64ull|(1ull<<14)|(96ull<<20)|(1ull<<34); // Explicit level1/2 bases and widths; MTBA0.
  batch.vertices[0].x=0;batch.vertices[0].y=0;batch.vertices[1].x=2;batch.vertices[1].y=2;
  for(auto&vertex:batch.vertices){vertex.q=1;vertex.r=128;vertex.g=128;vertex.b=128;vertex.a=128;vertex.u=8;vertex.v=8;vertex.s=0.0625f;vertex.t=0.0625f;}
  for(uint32_t y=0;y<2;y++)for(uint32_t x=0;x<2;x++)backend.WriteVram(0,4096,1,x,y,0);
  backend.Submit(batch);const uint32_t actual=backend.ReadVram(0,4096,1,0,0);
  const uint32_t sourceExpected=colors[redirect?target:0];require(actual==sourceExpected,"observed TEX0 plane");
  for(uint32_t y=0;y<2;y++)for(uint32_t x=0;x<2;x++)require(backend.ReadVram(0,4096,1,x,y)==actual,"four authored output pixels");
  if(!redirect&&target>0){require(actual!=colors[target],"manual fixed-LOD disagreement detected");++manualMismatch;}
  if(redirect){require(actual==colors[target],"redirected plane readable");++redirected;}
  if(total++)std::cout<<",";std::cout<<"{\"fst\":"<<fst<<",\"fixed_LOD\":"<<target<<",\"TEX0_redirect\":"<<redirect<<",\"actual_rgba\":"<<actual<<",\"manual_fixed_LOD_rgba\":"<<colors[target]<<",\"TEX1\":"<<c.tex1<<",\"MIPTBP1\":"<<c.miptbp1<<"}";
 }
 require(total==10&&manualMismatch==4&&redirected==4,"case cardinalities");std::cout<<"]\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
