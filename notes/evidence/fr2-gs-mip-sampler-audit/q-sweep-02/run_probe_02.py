"""Authored synthetic Q-based LOD experiment; never link or invoke guest code."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();out=root/'.scratch/mesh/codex-root/gs-mip-sampler-native-02'
prior=root/'.scratch/mesh/codex-root/gs-mip-sampler-native-01'
up=root/'.scratch/mesh/codex-root/PS2Recomp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# 01 artifacts must be byte-identical to the preservation record before any 02 action.
pres=json.loads((out/'01-preservation-before.json').read_text())
for row in pres['files']:
 assert sha(root/pres['source_dir']/row['path'])==row['sha256'],row['path']
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
build_tree=root/'.scratch/mesh/codex-root/PS2Recomp-fpu-01'
for rel in source_paths:assert (build_tree/rel).read_bytes()==(up/rel).read_bytes()
command=['clang++','-std=c++20','-O1','-mmacosx-version-min=26.4','-DUSE_SSE2NEON']
for rel in build['includes']:command.extend(['-I',str(root/rel)])
command.extend([str(out/'probe.cpp'),*[str(p) for p in libraries]])
for framework in build['frameworks']:command.extend(['-framework',framework])
command.extend(['-o',str(out/'probe')])
compiled=subprocess.run(command,capture_output=True,text=True,timeout=120)
(out/'compile.log').write_text(compiled.stdout+compiled.stderr)
assert compiled.returncode==0,(compiled.returncode,compiled.stderr)
symbols=subprocess.run(['nm','-a',str(out/'probe')],check=True,capture_output=True,text=True).stdout
(out/'symbols.txt').write_text(symbols)
guest_names=set(re.findall(r'\bsub_[A-Za-z0-9_]+',(root/'.scratch/mesh/codex-root/recomp-fpu-01/register_functions.cpp').read_text()))
assert len(guest_names)==4746
assert not [n for n in guest_names if n in symbols]
for forbidden in ['g_ps2RecompiledFunctionTable','InitWindow','InitAudioDevice','mainLoop']:assert forbidden not in symbols
preflight={'binary_sha256':sha(out/'probe'),'generated_guest_names_checked_absent':4746,'registration_and_display_audio_entry_symbols_absent':True,'symbols_sha256':sha(out/'symbols.txt'),'source_review':'Probe initializes CPU VRAM, writes three authored constant color planes, submits authored sprites to CPU memory and reads four output pixels. Same GS entry points as 01 plus homogeneous per-vertex Q. No display, presentation or audio initialization; original guest names absent.'}
(out/'binary-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
proc=subprocess.run([str(out/'probe')],capture_output=True,text=True,timeout=60)
(out/'run.stdout').write_text(proc.stdout);(out/'run.stderr').write_text(proc.stderr)
assert proc.returncode==0 and proc.stderr=='',(proc.returncode,proc.stderr)
cases=json.loads(proc.stdout);assert len(cases)==16
colors=[0x800000ff,0x8000ff00,0x80ff0000]
fixed=[c for c in cases if c['mode']=='fixed'];qc=[c for c in cases if c['mode']=='q_based']
assert len(fixed)==10 and len(qc)==6
for c in fixed:
 assert c['actual_rgba']==colors[c['fixed_LOD'] if c['TEX0_redirect'] else 0]
 assert c['manual_expected_rgba']==colors[c['fixed_LOD']]
 assert c['TEX1']==1|(2<<2)|(2<<6)|((c['fixed_LOD']*16)<<32)
for c in qc:
 assert c['TEX1']==(2<<2)|(2<<6) and c['TEX1']&1==0
 assert c['manual_expected_rgba']==colors[c['manual_Q_LOD']]
 assert c['q']==[1.0,0.5,0.25][c['manual_Q_LOD']]
 assert c['four_pixels_uniform']==1
assert all(c['MIPTBP1']==64|(1<<14)|(96<<20)|(1<<34) for c in cases)
fixed_dis=[c for c in fixed if not c['TEX0_redirect'] and c['actual_rgba']!=c['manual_expected_rgba']]
q_dis=[c for c in qc if c['actual_rgba']!=c['manual_expected_rgba']]
q_base=[c for c in qc if c['actual_rgba']==colors[0]]
result={'schema_version':1,'public_revision':revision,'source_pins':pins,'authored_probe_sha256':sha(out/'probe.cpp'),'draft_original_probe_sha256':sha(out/'probe-draft-original.cpp'),'runner_sha256':sha(out/'run_probe_02.py'),'compile':{'command':command,'exit_code':compiled.returncode,'log_sha256':sha(out/'compile.log'),'libraries':build['libraries']},'binary_preflight':preflight,'process':{'command':[str(out/'probe')],'exit_code':proc.returncode,'stderr_bytes':len(proc.stderr),'stdout_sha256':sha(out/'run.stdout')},'cases':cases,'counts':{'total':len(cases),'fixed':len(fixed),'q_based':len(qc),'fixed_manual_disagreements':len(fixed_dis),'q_manual_disagreements':len(q_dis),'q_cases_equal_to_TEX0_base_plane':len(q_base),'manual_disagreements_total':len(fixed_dis)+len(q_dis)},'preserved_01_files_verified_before_run':len(pres['files']),'limits':['Direct backend GSDrawState synthetic entry only; no original game frontend/submission executed.','Expected levels derive from the manual LOD formula with homogeneous Q on both sprite vertices and L=0,K=0; sprite-specific hardware Q handling is not independently verified.','Constant-color point-sampled CT32 planes only; no filtering, derivative, hardware or original-game claim.','No production runtime patch applied.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'result_sha256':sha(out/'result.json')}))
