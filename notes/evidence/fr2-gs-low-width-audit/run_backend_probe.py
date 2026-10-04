"""Authored synthetic transfer experiment; never link or invoke guest code."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();out=root/'.scratch/mesh/codex-root/gs-backend-width-native-01'
up=root/'.scratch/mesh/codex-root/PS2Recomp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
revision=subprocess.run(['git','-C',str(up),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
assert revision=='c5a9d02573410a2085a4b4b831b0b68ba3515440'
source_paths=['ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp','ps2xRuntime/include/runtime/gs/ps2_gs_memory.h','ps2xRuntime/include/runtime/gs/gs_cpu_backend.h']
pins=[]
for rel in source_paths:
 p=up/rel;assert p.read_bytes()==subprocess.run(['git','-C',str(up),'show','HEAD:'+rel],check=True,capture_output=True).stdout
 pins.append({'path':str(p.relative_to(root)),'sha256':sha(p)})
build=json.loads((root/'notes/evidence/fr2-vif-vu-synthetic-audit/build-record.json').read_text())
libraries=[]
for row in build['libraries']:
 p=root/row['path'];assert sha(p)==row['sha256'];libraries.append(p)
# Source tree used to build the existing public runtime must match the tested files.
build_tree=root/'.scratch/mesh/codex-root/PS2Recomp-fpu-01'
for rel in source_paths:assert (build_tree/rel).read_bytes()==(up/rel).read_bytes()
command=['clang++','-std=c++20','-O1','-mmacosx-version-min=26.4','-DUSE_SSE2NEON']
for rel in build['includes']:command.extend(['-I',str(root/rel)])
command.extend([str(out/'probe.cpp'),*[str(p) for p in libraries]])
for framework in build['frameworks']:command.extend(['-framework',framework])
command.extend(['-o',str(out/'probe')])
compiled=subprocess.run(command,capture_output=True,text=True,timeout=60)
(out/'compile-recheck.log').write_text(compiled.stdout+compiled.stderr)
assert compiled.returncode==0,(compiled.returncode,compiled.stderr)
symbols=subprocess.run(['nm','-a',str(out/'probe')],check=True,capture_output=True,text=True).stdout
(out/'symbols-recheck.txt').write_text(symbols)
guest_names=set(re.findall(r'\bsub_[A-Za-z0-9_]+',(root/'.scratch/mesh/codex-root/recomp-fpu-01/register_functions.cpp').read_text()))
assert len(guest_names)==4746
assert not [n for n in guest_names if n in symbols]
for forbidden in ['g_ps2RecompiledFunctionTable','InitWindow','InitAudioDevice','mainLoop']:assert forbidden not in symbols
preflight={'binary_sha256':sha(out/'probe'),'generated_guest_names_checked_absent':4746,'registration_and_display_audio_entry_symbols_absent':True,'symbols_sha256':sha(out/'symbols-recheck.txt'),'source_review':'Probe only constructs and initializes CPU VRAM, submits direction-zero transfers, uploads synthetic labels and writes VRAM to stdout. Constructor/Initialize/Reset and transfer path reviewed; no draw/display/audio initialization invoked.'}
(out/'binary-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
with (out/'actual-vram.bin').open('wb') as f:proc=subprocess.run([str(out/'probe')],stdout=f,stderr=subprocess.PIPE,timeout=60)
(out/'run.stderr').write_bytes(proc.stderr)
assert proc.returncode==0 and proc.stderr==b'',(proc.returncode,proc.stderr)
native=(out/'actual-vram.bin').read_bytes();assert len(native)==8*4*1024*1024
reference=root/'.scratch/mesh/codex-root/github-raw-GSTables.cpp'
assert sha(reference)=='a9a226297ede32b89177d7bdb04e9d8e21728e7d55799405f6112e97fe4969e8'
text=reference.read_text();shapes={32:(8,8,64,32),16:(16,8,64,64),8:(16,16,128,64),4:(32,16,128,128)}
cases=[];at=0
for bits,(bw,bh,pw,ph) in shapes.items():
 tables=[]
 for name,rows,cols in [(f'_blockTable{bits}',ph//bh,pw//bw),(f'columnTable{bits}',bh,bw)]:
  match=re.search(r'\b'+name+rf'\[{rows}\]\[{cols}\]\s*=\s*\{{(.*?)\}};',text,re.S);assert match
  nums=list(map(int,re.findall(r'\d+',re.sub(r'//[^\n]*','',match.group(1)))));assert len(nums)==rows*cols
  tables.append([nums[n*cols:(n+1)*cols] for n in range(rows)])
 blocks,columns=tables;w=64 if bits>=16 else 128;h=ph*2
 for width in (0,1):
  actual=native[at:at+4*1024*1024];at+=len(actual);models=[]
  for label,effective in [('raw_PCSX2_width',width),('backend_max_width_1',max(width,1))]:
   expected=bytearray(len(actual))
   for y in range(h):
    for x in range(w):
     pixel=y*w+x;value=((pixel*2654435761)&0xffffffff)^(pixel>>5)^0x91a2b3c4
     page=(y//ph)*(effective*64//pw)+x//pw
     offset=page*pw*ph+blocks[(y%ph)//bh][(x%pw)//bw]*bw*bh+columns[y%bh][x%bw]
     nibble=33*512+offset*bits//4;byte=nibble//2
     if bits==4:
      shift=(nibble&1)*4;expected[byte]=(expected[byte]&~(15<<shift))|((value&15)<<shift)
     else:expected[byte:byte+bits//8]=(value&((1<<bits)-1)).to_bytes(bits//8,'little')
   mismatches=sum(a!=b for a,b in zip(actual,expected));first=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
   if label=='backend_max_width_1':assert mismatches==0,(bits,width,mismatches,first)
   else:assert (mismatches>0)==(bits>=16 and width==0),(bits,width,mismatches)
   models.append({'model':label,'effective_width':effective,'different_bytes':mismatches,'first_difference_byte':first,'expected_sha256':hashlib.sha256(expected).hexdigest()})
  # A changed golden byte must be detected in every otherwise matching backend model.
  expected[0]^=1;assert sum(a!=b for a,b in zip(actual,expected))==1
  cases.append({'PSM':{32:0,16:2,8:19,4:20}[bits],'bits':bits,'DBP':33,'DBW':width,'dimensions':[w,h],'uploaded_bytes':w*h*bits//8,'whole_vram_bytes_compared':len(actual),'actual_sha256':hashlib.sha256(actual).hexdigest(),'models':models,'one_byte_negative_control_different_bytes':1})
assert at==len(native)
result={'schema_version':1,'status':'observed_reference_disagreement','public_runtime_revision':revision,'public_runtime_source_pins':pins,'reference':{'path':str(reference.relative_to(root)),'sha256':sha(reference),'revision':'81526d4dc7cc70e4ae75abb35a789417456c6d43'},'authored_probe_sha256':sha(out/'probe.cpp'),'runner_sha256':sha(out/'run_probe.py'),'compile':{'command':command,'exit_code':compiled.returncode,'log_sha256':sha(out/'compile-recheck.log'),'libraries':build['libraries']},'binary_preflight':preflight,'process':{'command':[str(out/'probe')],'exit_code':proc.returncode,'stderr_bytes':len(proc.stderr),'stdout_bytes':len(native),'output_sha256':sha(out/'actual-vram.bin')},'cases':cases,'scope':'Synthetic labels only, one base block33 and two vertical pages at widths0/1 in four PSMs. Actual CPU upload path equals width-clamped model in all eight whole-memory comparisons. Raw-width model differs for zero-width CT32/CT16 only; indexed widths0/1 yield zero page-row stride in both. No original game routine or payload, generated runner, display/audio, GS hardware, rendering, dynamic game-state or whole-game equivalence claim. Runtime library was built from four-EE-patch experiment tree but tested source files match pristine public revision exactly.'}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':len(cases),'whole_vram_bytes_compared':len(native),'different_raw_width_cases':sum(any(m['different_bytes'] for m in c['models'] if m['model']=='raw_PCSX2_width') for c in cases),'runtime_exit_code':proc.returncode,'stderr_bytes':len(proc.stderr),'result_sha256':sha(out/'result.json')}))
