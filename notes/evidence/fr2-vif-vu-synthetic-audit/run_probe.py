from pathlib import Path
import hashlib,json,subprocess
p=Path.cwd()/'.scratch/mesh/codex-root/vif-vu-synthetic-01'
assert (p/'probe').is_file(), 'Expected the saved synthetic-only probe at the fixed scratch path'
preflight=json.loads((p/'binary-preflight.json').read_text())
assert hashlib.sha256((p/'probe').read_bytes()).hexdigest()==preflight['binary_sha256']
records=[]
for argv,expected in [([str(p/'probe')],{'vif_latch_cases':4096,'packet_order_cases':1024,'vu_stop_resume_cases':4096,'negative_detected':0}),([str(p/'probe'),'e-clear'],{'vif_latch_cases':4096,'packet_order_cases':1024,'vu_stop_resume_cases':0,'negative_detected':4096})]:
 r=subprocess.run(argv,capture_output=True,text=True,timeout=60)
 assert r.returncode==0 and r.stderr=='',(r.returncode,r.stderr)
 got=json.loads(r.stdout);assert got==expected,(got,expected)
 records.append({'command':argv,'returncode':r.returncode,'stderr':r.stderr,'result':got})
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
r={'schema_version':1,'status':'pass','method':'Execute only pinned public software with authored synthetic VIF commands and VU nop/E-delay/VI-write/XTOP/XITOP pairs. No original game code or payload is linked or loaded. No GS drawing command, display initialization or game runner is invoked.','source_revision':'c5a9d02573410a2085a4b4b831b0b68ba3515440','probe_source_sha256':sha(p/'probe.cpp'),'native_binary_sha256':sha(p/'probe'),'public_runtime_source_pins':json.loads((p/'source-pins.json').read_text()),'binary_preflight':json.loads((p/'binary-preflight.json').read_text()),'process_records':records,'limits':['Observed deterministic software behavior only; no PS2 hardware, scheduling/concurrency, full VIF/VU correctness, original game packet state, or game completeness claim.','TOPS register values, BASE/OFFSET and DBF are supplied synthetically. Original preceding game state remains unresolved.','Baseline checks cover all 1024 possible TOP values at four distinct synthetic start PCs; they do not cover every VU instruction or E-bit interaction.','The linked library was built from the separate four-patch EE experiment source tree. Both VIF and VU core source files equal the pinned pristine public files; the tested mechanisms do not use those EE patches.']}
(p/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
