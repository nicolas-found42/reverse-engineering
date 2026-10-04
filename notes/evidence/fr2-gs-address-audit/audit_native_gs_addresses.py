"""Compile pinned public GS address helpers and compare synthetic coordinates."""
import array,hashlib,json,re,subprocess,sys
from pathlib import Path
r=Path('.scratch/mesh/codex-root');up=r/'PS2Recomp';out=r/'gs-address-native-01';assert not out.exists();out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
commit=subprocess.run(['git','-C',str(up),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip();assert commit=='c5a9d02573410a2085a4b4b831b0b68ba3515440'
headers=['ps2_gs_psmct32.h','ps2_gs_psmct16.h','ps2_gs_psmt8.h','ps2_gs_psmt4.h'];include=up/'ps2xRuntime/include';pins=[]
for n in headers:
 rel='ps2xRuntime/include/runtime/gs/'+n;p=up/rel;head=subprocess.run(['git','-C',str(up),'show','HEAD:'+rel],check=True,capture_output=True).stdout;assert p.read_bytes()==head;pins.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
source=r/'github-raw-GSTables.cpp';assert sha(source)=='a9a226297ede32b89177d7bdb04e9d8e21728e7d55799405f6112e97fe4969e8';text=source.read_text();shapes={32:(8,8,64,32),16:(16,8,64,64),8:(16,16,128,64),4:(32,16,128,128)};tables={}
for bits,(bw,bh,pw,ph) in shapes.items():
 vals=[]
 for name,rows,cols in [(f'_blockTable{bits}',ph//bh,pw//bw),(f'columnTable{bits}',bh,bw)]:
  m=re.search(r'\b'+name+rf'\[{rows}\]\[{cols}\]\s*=\s*\{{(.*?)\}};',text,re.S);assert m;nums=list(map(int,re.findall(r'\d+',re.sub(r'//[^\n]*','',m.group(1)))));assert len(nums)==rows*cols;vals.append([nums[n*cols:(n+1)*cols] for n in range(rows)])
 tables[bits]=vals
harness='\n'.join('#include "runtime/gs/'+n+'"' for n in headers)+r'''
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
'''
cpp=out/'probe.cpp';cpp.write_text(harness);binary=out/'probe';command=['clang++','-std=c++20','-O1','-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(include.resolve()),str(cpp),'-o',str(binary)];build=subprocess.run(command,capture_output=True,text=True,timeout=60);(out/'build.stdout').write_text(build.stdout);(out/'build.stderr').write_text(build.stderr);assert build.returncode==0
runs=[]
for label,arg in [('actual','0'),('mutant','1')]:
 p=out/(label+'.bin')
 with p.open('wb') as f:proc=subprocess.run([str(binary.resolve()),arg],stdout=f,stderr=subprocess.PIPE,timeout=60)
 (out/(label+'.stderr')).write_bytes(proc.stderr);assert proc.returncode==0 and not proc.stderr
 result=array.array('I');result.frombytes(p.read_bytes());assert result.itemsize==4;counts={};mismatches={};examples=[];at=0
 for bits,(bw,bh,pw,ph) in shapes.items():
  blocks,cols=tables[bits];counts[str(bits)]=0;mismatches[str(bits)]=0
  for width in ([1,2,4,8] if bits>=16 else [2,4,8]):
   for base in [0,1,31,32,33,16383]:
    for y in range(ph*2):
     for x in range(pw*2):
      page=(y//ph)*(width*64//pw)+x//pw
      offset=page*pw*ph+blocks[(y%ph)//bh][(x%pw)//bw]*bw*bh+cols[y%bh][x%bw]
      expected=(base*512+offset) if bits==4 else (base*256+offset*(bits//8));actual=result[at];at+=1;counts[str(bits)]+=1
      if actual!=expected:
       mismatches[str(bits)]+=1
       if len(examples)<4:examples.append({'bits':bits,'base':base,'buffer_width':width,'x':x,'y':y,'actual':actual,'expected':expected})
 assert at==len(result)
 assert (not any(mismatches.values())) if label=='actual' else mismatches==counts
 runs.append({'kind':label,'exit_code':proc.returncode,'values':at,'counts':counts,'mismatches':mismatches,'example_mismatches':examples,'output_sha256':sha(p),'stderr_bytes':len(proc.stderr)})
receipt={'schema_version':1,'status':'pass','upstream_commit':commit,'header_pins':pins,'reference_source':{'path':str(source),'sha256':sha(source),'public_revision':'81526d4dc7cc70e4ae75abb35a789417456c6d43'},'harness':{'path':str(cpp),'sha256':sha(cpp)},'compile':{'command':command,'exit_code':build.returncode,'binary_sha256':sha(binary),'undefined_behavior_sanitizer':True},'runs':runs,'scope':'Only four pinned C++ address helper functions executed with synthetic coordinates and explicit buffer bases; public table page/block/column oracle. No original game routine, GS device, renderer, emulator, or linked runner executed. No CLUT/mip/timing/color/hardware/whole-game equivalence claim. Indexed buffer_width1 and0 are outside this measured profile.'}
(out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
