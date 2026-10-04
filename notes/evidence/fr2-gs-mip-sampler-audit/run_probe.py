"""Authored synthetic transfer experiment; never link or invoke guest code."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();out=root/'.scratch/mesh/codex-root/gs-mip-sampler-native-01'
up=root/'.scratch/mesh/codex-root/PS2Recomp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
revision=subprocess.run(['git','-C',str(up),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
assert revision=='c5a9d02573410a2085a4b4b831b0b68ba3515440'
source_paths=['ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp','ps2xRuntime/include/runtime/gs/ps2_gs_memory.h','ps2xRuntime/include/runtime/gs/gs_cpu_backend.h','ps2xRuntime/include/runtime/gs/gs_types.h','ps2xRuntime/include/runtime/gs/gs_texture_page_cache.h']
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
preflight={'binary_sha256':sha(out/'probe'),'generated_guest_names_checked_absent':4746,'registration_and_display_audio_entry_symbols_absent':True,'symbols_sha256':sha(out/'symbols-recheck.txt'),'source_review':'Probe only initializes CPU VRAM, writes three authored constant color planes, submits authored sprites to CPU memory and reads four output pixels. Submit/DrawPrimitive/DrawSprite/SampleTexture/WritePixel reviewed; no display, presentation or audio initialization. Original guest names absent.'}
(out/'binary-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
proc=subprocess.run([str(out/'probe')],capture_output=True,text=True,timeout=60)
(out/'run.stdout').write_text(proc.stdout);(out/'run.stderr').write_text(proc.stderr)
assert proc.returncode==0 and proc.stderr=='',(proc.returncode,proc.stderr)
cases=json.loads(proc.stdout);assert len(cases)==10
colors=[0x800000ff,0x8000ff00,0x80ff0000]
for c in cases:
 assert c['actual_rgba']==colors[c['fixed_LOD'] if c['TEX0_redirect'] else 0]
 assert c['manual_fixed_LOD_rgba']==colors[c['fixed_LOD']]
 assert c['TEX1']==1|(2<<2)|(2<<6)|((c['fixed_LOD']*16)<<32)
 assert c['MIPTBP1']==64|(1<<14)|(96<<20)|(1<<34)
disagreements=[c for c in cases if not c['TEX0_redirect'] and c['actual_rgba']!=c['manual_fixed_LOD_rgba']]
assert len(disagreements)==4
result={'schema_version':1,'status':'observed_public_CPU_mip_selection_gap','public_revision':revision,'source_pins':pins,'authored_probe_sha256':sha(out/'probe.cpp'),'runner_sha256':sha(out/'run_probe.py'),'compile':{'command':command,'exit_code':compiled.returncode,'log_sha256':sha(out/'compile-recheck.log'),'libraries':build['libraries']},'binary_preflight':preflight,'process':{'command':[str(out/'probe')],'exit_code':proc.returncode,'stderr_bytes':len(proc.stderr),'stdout_sha256':sha(out/'run.stdout')},'cases':cases,'manual_visual_review':json.loads((out/'manual-lod-visual.json').read_text()),'fixed_LOD_reference_disagreements':len(disagreements),'scope':'Authored constant-color CT32 mip planes8x8/4x4/2x2 at blocks32/64/96, width1; LCM1,MXL2,MMIN2,MTBA0,K0/16/32. UV and ST sprites draw only into CPU VRAM, no display or original game. ActualCPU sampler reads TEX0level0 for all six unredirected cases, contrary to manual fixedLOD1/2 in four cases. Four TEX0 redirect controls prove green/blue planes can be read. This is bounded public backend behavior and manual reference, not observed hardware or original-game state.','prior_source_screen':'r095 source screen flagged injection probability0.56; source comments were manually treated as data, and complete function tail was inspected after initial bounded slice ended before final return. No unchanged screening retry.','limits':['Direct backend GSDrawState synthetic entry only; full original game frontend/submission/use not executed.','Constant-color, point-sampled CT32 fixedLOD integer cases only; no general filtering, palette, ST derivative, GS timing or full texture correctness claim.','No public runtime patch applied. The linked runtime archive is from the four-EE-patch experiment tree; testedGS files equal pristine pinned public source.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':len(cases),'fixed_LOD_reference_disagreements':len(disagreements),'result_sha256':sha(out/'result.json')}))
