"""Run only an authored fixture against the pinned public VIF/DMA implementation."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();out=root/'.scratch/mesh/codex-root/vif-header-synthetic-01'
up=root/'.scratch/mesh/codex-root/PS2Recomp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
revision=subprocess.run(['git','-C',str(up),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
assert revision=='c5a9d02573410a2085a4b4b831b0b68ba3515440'
source_paths=['ps2xRuntime/src/lib/ps2_memory.cpp','ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp','ps2xRuntime/include/runtime/ps2_memory.h']
pins=[]
for rel in source_paths:
 p=up/rel;assert p.read_bytes()==subprocess.run(['git','-C',str(up),'show','HEAD:'+rel],check=True,capture_output=True).stdout
 assert p.read_bytes()==(root/'.scratch/mesh/codex-root/PS2Recomp-fpu-01'/rel).read_bytes()
 pins.append({'path':str(p.relative_to(root)),'sha256':sha(p),'pristine_and_library_build_source_equal':True})
build=json.loads((root/'notes/evidence/fr2-vif-vu-synthetic-audit/build-record.json').read_text());libraries=[]
for row in build['libraries']:
 p=root/row['path'];assert sha(p)==row['sha256'];libraries.append(p)
command=['clang++','-std=c++20','-O1','-mmacosx-version-min=26.4','-DUSE_SSE2NEON']
for rel in build['includes']:command.extend(['-I',str(root/rel)])
command.extend([str(out/'probe.cpp'),*[str(p) for p in libraries]])
for framework in build['frameworks']:command.extend(['-framework',framework])
command.extend(['-o',str(out/'probe')])
compiled=subprocess.run(command,capture_output=True,text=True,timeout=60)
(out/'compile.log').write_text(compiled.stdout+compiled.stderr)
assert compiled.returncode==0,(compiled.returncode,compiled.stderr)
symbols=subprocess.run(['nm','-a',str(out/'probe')],check=True,capture_output=True,text=True).stdout
(out/'symbols.txt').write_text(symbols)
names=set(re.findall(r'\bsub_[A-Za-z0-9_]+',(root/'.scratch/mesh/codex-root/recomp-fpu-01/register_functions.cpp').read_text()))
assert len(names)==4746 and not [n for n in names if n in symbols]
for forbidden in ['g_ps2RecompiledFunctionTable','InitWindow','InitAudioDevice','mainLoop']:assert forbidden not in symbols
preflight={'binary_sha256':sha(out/'probe'),'guest_names_checked_absent':4746,'guest_registration_display_audio_symbols_absent':True,'symbol_log_sha256':sha(out/'symbols.txt'),'review':'PS2Memory constructor/initialize only allocate/reset memory; authored PS2Memory read/write, VIF parser and deferred three-tag DMA path only. No VU program, GIF drawing command or original game data.'}
(out/'binary-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
proc=subprocess.run([str(out/'probe')],capture_output=True,text=True,timeout=60)
(out/'run.stdout').write_text(proc.stdout);(out/'run.stderr').write_text(proc.stderr)
assert proc.returncode==0 and proc.stderr=='',(proc.returncode,proc.stderr)
got=json.loads(proc.stdout)
expected={'contiguous_cases':1024,'fragmented_unchanged_memory_cases':3072,'TTE_chain_cases':1024,'TTE_cleared_negative_cases':1024,'TOP_flag_negative_different':1023,'TOP_flag_base_zero_equivalent':1,'one_byte_golden_negative_cases':1024,'VU_callbacks':0}
assert got==expected,(got,expected)
result={'schema_version':1,'status':'observed_public_parser_fragmentation_limit','public_revision':revision,'source_pins':pins,'probe_source_sha256':sha(out/'probe.cpp'),'runner_sha256':sha(out/'run_probe.py'),'compile':{'command':command,'exit_code':compiled.returncode,'log_sha256':sha(out/'compile.log'),'libraries':build['libraries']},'binary_preflight':preflight,'process':{'command':[str(out/'probe')],'exit_code':proc.returncode,'stderr_bytes':len(proc.stderr),'stdout_sha256':sha(out/'run.stdout'),'counts':got},'mapping':'Five authored qwords contain u32 labels 1..20; direct unmasked V4-32 at offset0 with MODE0 and CYCLE4/4 writes qword q to (TOPS+q)&1023. Qword3.Z is label15. Whole16384-byte VU data memory compared, untouched bytes A5.','input_profiles':['One contiguous 88-byte NOP+UNPACK+80-byte payload buffer','8-byte prefix then one80-byte payload buffer','8-byte prefix then five16-byte payload buffers','8-byte prefix then twenty4-byte payload buffers','Authored CNT5→REF1→END0 DMA chain, with tag upper NOP+UNPACK, data labels and zero REF, TTE enabled'],'Jev_disposition':'r096 pre-execution gate escalation (safe_to_apply0.14, composite0.62625) and three unsupported claims preserved. Evidence then included public source excerpts, while probe was in diff only and no execution existed. Manual bounded execution followed source, binary and library checks; no production change. A different result-backed verification can assess observations.','limits':['Observed public software, not GS/VIF hardware conformance or original-game state. All labels, DMA tags and TOPS inputs authored; no original routines/payload or runner linked/executed.','Fragmented direct parser entry loses this UNPACK; tested TTE DMA chain concatenates tag upper bytes and payload and passes. This does not establish that original game chains suffer fragmentation.','One V4-32 command, fixed unmasked MODE0/CYCLE4/4, TOPS0..1023 only; no general VIF format/mask/mode/scheduling correctness claim.','The existing linked runtime archive came from a four-EE-patch experiment tree; all tested public VIF/memory files match pristine exactly.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'result_sha256':sha(out/'result.json'),'counts':got}))
