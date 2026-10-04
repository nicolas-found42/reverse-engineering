from pathlib import Path
import struct,json,hashlib,collections
r=Path.cwd();elf=(r/'games/ford-racing-2/extracted/SLES_517.05').read_bytes();start,end=0x200e70,0x201124;off=0x1000+start-0x100000;raw=elf[off:off+end-start]
assert hashlib.sha256(elf[off:off+696]).hexdigest()=='9e1d5d1fed414999b4224049a3f654ab2f2503ca1488429fb3b4566d0c791d0c'
assert elf[off+692:off+696]==bytes(4)
for site in (0x1fc008,0x1fc02c,0x1fc174,0x1fc1dc):
 w=struct.unpack_from('<I',elf,0x1000+site-0x100000)[0];assert w>>26==3 and ((site+4)&0xf0000000)|((w&0x3ffffff)*4)==start
for name,want in [('decompilation/manifest.json','3716978f8352119e6f413ba61305c4e0ae28f3bf9a3115ee36a26fec183486a8'),('inventory.json','41bde5a7b57f0044d1a7276d762f24500bb50e8611e18ffd7de3ceddf8a14716'),('coverage.json','5019d3e1919eee5ba7801ef7e06ef1c0146081132dfdb0128519f2d390d49e44')]:
 assert hashlib.sha256((r/'.scratch/mesh/codex-audit/ee-00200de0-candidate-01/export-3843'/name).read_bytes()).hexdigest()==want
assert hashlib.sha256((r/'.scratch/mesh/codex-audit/ee-00200e70-cfg-3843-01/guard-proposal/CreateEeClosureCandidate00200e70V1.java').read_bytes()).hexdigest()=='846d590519f58c3444679ce7afcfe007a15949dcebb61e37697ffb6c3da3cf96'
todo=collections.deque([(start,False)]);seen={};transfers=[];likely=[];returns=[]
def classify(w):
 op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;fn=w&63
 if op==0 and fn in (8,9):return 'return' if w==0x03e00008 else 'reject'
 if op==3:return 'call'
 if op==2:return 'jump'
 if op in (4,5,6,7,20,21,22,23):return 'unconditional' if op==4 and rs==rt==0 else 'branch'
 if op==1 and rt in (0,1,2,3,16,17,18,19):return 'branch'
 if op in (16,17,18) and rs==8:return 'branch'
 if (op==0 and fn in (12,13)) or (op==1 and rt in (8,9,10,11,12,14)):return 'reject'
 return 'linear'
while todo:
 pc,delay=todo.popleft();assert start<=pc<end and pc%4==0
 if pc in seen:assert seen[pc]==delay;continue
 seen[pc]=delay;w=struct.unpack_from('<I',raw,pc-start)[0];kind=classify(w);assert kind!='reject'
 if delay:assert kind=='linear';continue
 if kind=='linear':todo.append((pc+4,False));continue
 todo.append((pc+4,True));transfers.append(kind)
 if kind in ('branch','unconditional'):
  imm=struct.unpack('<h',struct.pack('<H',w&65535))[0];target=pc+4+imm*4;todo.append((target,False))
  if kind=='branch':todo.append((pc+8,False))
  if w>>26 in (20,21,22,23):likely.append(f'{pc:08x}')
 elif kind=='call':todo.append((pc+8,False))
 elif kind=='jump':todo.append((((pc+4)&0xf0000000)|((w&0x3ffffff)*4),False))
 elif kind=='return':returns.append(f'{pc:08x}')
assert set(seen)==set(range(start,end,4)),len(seen)
assert set(likely)=={'00200ed8','00200ee4','00200ef0','00200f30','00200f58','00200f68','00200fa8','00200ffc','00201024','00201030','00201070','00201084'},likely
assert 'call' not in transfers and 'jump' not in transfers,transfers
assert returns==['0020111c'],returns
result={'schema_version':1,'status':'pass_static_structural_union','method':'Independent root raw-word scan through pinned ELF .text mapping','ELF_sha256':hashlib.sha256(elf).hexdigest(),'window_sha256':hashlib.sha256(raw).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reachable_instruction_words_including_delay_slots':len(seen),'control_transfer_counts':dict(collections.Counter(transfers)),'allowed_exact_JR_RA_return_sites':returns,'likely_branch_sites':sorted(likely),'scope':'Structural union of taken branch delay words and annulled-not-taken continuations. Calls not followed; only exact JR RA return permitted. No computed call/other register jump/trap/control in delay word accepted. This does not claim stepwise branch execution, return feasibility, original identity or runtime behavior.','Jev_review_disposition':'Source review safe_to_apply 0.03 escalation and combined-pin review retained. Exact pinned bytes and caller JALs independently checked before isolated project mutation.','checker_history':'Adapted the prior structural-union checker to the e70 window; exact twelve likely branches checked as a set, no outgoing calls/jumps permitted. The excluded terminal zero and four incoming JAL words are checked separately.'}
(r/'.scratch/mesh/codex-root/root-ee-e70-cfg-validation-01.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
