from pathlib import Path
import struct,json,hashlib,collections
r=Path.cwd();src=r/'games/ford-racing-2/extracted/SLES_517.05';elf=src.read_bytes()
assert hashlib.sha256(elf).hexdigest()=='216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95'
assert elf[:6]==b'\x7fELF\x01\x01'
phoff=struct.unpack_from('<I',elf,28)[0];ents,n=struct.unpack_from('<HH',elf,42)
segments=[struct.unpack_from('<IIIIIIII',elf,phoff+i*ents) for i in range(n)]
def read(pc,size=4):
 hits=[s for s in segments if s[0]==1 and s[2]<=pc and pc+size<=s[2]+s[4]]
 assert len(hits)==1,(hex(pc),size,len(hits));s=hits[0]
 return elf[s[1]+pc-s[2]:s[1]+pc-s[2]+size]
start,end=0x1ff038,0x1ff140;raw=read(start,end-start)
assert hashlib.sha256(raw).hexdigest()=='16d48e8843225c3e399cb0b062641b0199c6870d685c79badaf65c4c3cf8c3a1'
assert struct.unpack('<I',read(end))[0]==0x27bdff90
baseline=r/'.scratch/mesh/codex-audit/ee-00200e70-candidate-01/export-3844'
pins={'decompilation/manifest.json':'1e3f425e7c1a653183a284a240b28f6ff2b2918250b1e1882b0dade4cf9c4ef4','inventory.json':'b23698a1e4e6bfb61f7d4ca9932b80971f1eb4527f57bb5219d14196586c4a9d','coverage.json':'2ff0ed89839dc6e4e26f7c8b93f1df7ee111f3c1205385e8c52f2640f13df1f0'}
for name,want in pins.items():assert hashlib.sha256((baseline/name).read_bytes()).hexdigest()==want
inv=json.loads((baseline/'inventory.json').read_text());functions={int(f['entry'],16):f for f in inv['functions']}
assert len(functions)==3844
caller=functions[0x200d10];site=next(i for i in caller['instructions'] if int(i['address'],16)==0x200dac)
assert caller['name']=='candidate_ee_00200d10' and bytes.fromhex(site['bytes'])==read(0x200dac)
w=struct.unpack('<I',read(0x200dac))[0];assert w==0x0c07fc0e and ((0x200db0&0xf0000000)|((w&0x3ffffff)<<2))==start
def classify(w):
 op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;fn=w&63
 if op==0 and fn in (8,9):return 'return' if w==0x03e00008 else 'reject'
 if (op==0 and fn in (12,13,48,49,50,51,52,54)) or (op==1 and rt in (8,9,10,11,12,14)):return 'reject'
 if op in (8,24) or (op==0 and fn in (32,34,44,46)):return 'reject'
 if op==3:return 'call'
 if op==2:return 'jump'
 if op in (4,5,6,7,20,21,22,23):
  assert op not in (20,21,22,23),'unexpected likely encoding'
  assert op not in (6,7) or rt==0
  return 'branch'
 if op==1 or (op in (16,17,18,19) and rs==8):return 'reject'
 return 'linear'
todo=collections.deque([(start,False)]);seen={};counts=collections.Counter();calls=[];returns=[]
while todo:
 pc,delay=todo.popleft();assert start<=pc<end and pc%4==0
 if pc in seen:assert seen[pc]==delay;continue
 seen[pc]=delay;w=struct.unpack('<I',read(pc))[0];kind=classify(w);assert kind!='reject'
 counts[kind]+=1
 if delay:assert kind=='linear';continue
 if kind=='linear':todo.append((pc+4,False));continue
 todo.append((pc+4,True))
 if kind=='branch':
  imm=struct.unpack('<h',struct.pack('<H',w&65535))[0];todo.extend([(pc+4+imm*4,False),(pc+8,False)])
 elif kind=='call':calls.append((pc,((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)));todo.append((pc+8,False))
 elif kind=='return':returns.append(pc)
 else:raise AssertionError('unexpected direct jump')
assert set(seen)==set(range(start,end,4)) and counts=={'linear':55,'branch':5,'call':5,'return':1}
assert returns==[0x1ff138] and read(0x1ff13c)==bytes.fromhex('6000bd27')
assert set(calls)=={(0x1ff08c,0x1ff270),(0x1ff0a8,0x1ffd70),(0x1ff0b0,0x1feb80),(0x1ff0fc,0x1fdb88),(0x1ff114,0x1fc4e0)}
zeros={pc for pc in seen if read(pc)==bytes(4)}
assert zeros=={0x1ff084,0x1ff0a4,0x1ff0dc,0x1ff0e0,0x1ff0e8}
assert {target for _,target in calls if target in functions}=={0x1ffd70,0x1fc4e0}
assert all(not start<=int(i['address'],16)<end for f in functions.values() for i in f['instructions'])
result={'schema_version':1,'status':'pass_static_structural_union','checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'ELF_sha256':hashlib.sha256(elf).hexdigest(),'method':'Root independent queue scan of raw words using unique ELF PT_LOAD mappings; fail on computed transfer, trap/arithmetic-trap, likely/REGIMM/cop-branch or control in delay slot.','window':{'start':f'{start:08x}','exclusive_end':f'{end:08x}','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'baseline_pins':pins,'reachable_instruction_words':len(seen),'classification_counts':dict(counts),'zero_words_reached':[f'{pc:08x}' for pc in sorted(zeros)],'delay_zero_words':[f'{pc:08x}' for pc in sorted(zeros) if seen[pc]],'return':'001ff138','return_delay_word':'27bd0060','excluded_next_word':'27bdff90','incoming_raw_JAL':{'site':'00200dac','word':'0c07fc0e','owner':'candidate_ee_00200d10'},'outgoing_calls':[{'site':f'{pc:08x}','target':f'{target:08x}','saved_entry':target in functions} for pc,target in calls],'scope':'Calls are not followed; structural reachability is not execution feasibility, original function identity, exact original boundaries or whole-game completeness. This checker does not open Ghidra or execute original game code.'}
(r/'.scratch/mesh/codex-root/root-ee-f038-cfg-validation-01.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
