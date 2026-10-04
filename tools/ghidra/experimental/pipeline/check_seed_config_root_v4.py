"""Independent root check of a V3 guard config: re-derives span/CFG/calls/zero words from raw ELF PT_LOAD bytes using a port of the guard classifier and compares with the config. Also checks baseline pins and incoming/owner facts from the inventory. No Ghidra, no execution of game code."""
from pathlib import Path
import struct,json,hashlib,sys,collections
r=Path.cwd();cfgp=Path(sys.argv[1]);exp=Path(sys.argv[2]);outp=Path(sys.argv[3])
C=json.loads(cfgp.read_text());elf_p=r/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_p.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(elf)==C['baseline']['executable_sha256']
for k,n in [('manifest_sha256','decompilation/manifest.json'),('inventory_sha256','inventory.json'),('coverage_sha256','coverage.json')]:assert sha((exp/n).read_bytes())==C['baseline'][k],k
phoff=struct.unpack_from('<I',elf,28)[0];ents,n=struct.unpack_from('<HH',elf,42);segs=[struct.unpack_from('<IIIIIIII',elf,phoff+i*ents) for i in range(n)]
def read(pc,size=4):
 h=[s for s in segs if s[0]==1 and s[2]<=pc and pc+size<=s[2]+s[4]];assert len(h)==1;s=h[0];return elf[s[1]+pc-s[2]:s[1]+pc-s[2]+size]
w=lambda pc:struct.unpack('<I',read(pc))[0]
START,END=int(C['start'],16),int(C['end'],16);assert C['entry']==C['start']
raw=read(START,END-START);assert len(raw)==C['bytes']==C['words']*4 and sha(raw)==C['window_sha256']
CC=set(C.get('computed_calls',[]));TJ=C.get('tail_jumps',{});DB=set(C.get('delay_breaks',[]))
assert w(START)==int(C['first_word'],16) and w(END-4)==int(C['delay_word'],16) and w(END-8)==0x03e00008 and w(END)==int(C['next_word'],16)
def flow(x):
 op=x>>26;rs=(x>>21)&31;rt=(x>>16)&31;fn=x&63
 if op==0 and fn==8 and x==0x03e00008:return 'return'
 if op==0 and fn==8:return 'computed_jump'
 if op==0 and fn==9:return 'computed_call'
 if op==0 and fn in (12,13,48,49,50,51,52,54,32,34,44,46):return 'unsupported_trap'
 if op in (8,24):return 'unsupported_trap'
 if op==2:return 'jump'
 if op==3:return 'call'
 if op==1:
  if rt in (8,9,10,11,12,14):return 'unsupported_trap'
  if rt in (0,1,2,3,16,17,18,19):return 'conditional_likely' if rt in (2,3,18,19) else 'conditional'
  return 'unsupported_encoding'
 if op==4 and rs==0 and rt==0:return 'unconditional_branch'
 if op in (4,5):return 'conditional'
 if op in (6,7,22,23) and rt!=0:return 'unsupported_encoding'
 if op in (6,7):return 'conditional'
 if op in (20,21,22,23):return 'conditional_likely'
 if op in (16,17,18,19) and rs==8:return 'conditional_likely' if (rt&2) else 'conditional'
 return 'linear'
ent0={f['entry'] for f in json.loads((exp/'inventory.json').read_text())['functions']}
seen={};edges=[];breaks=[];q=collections.deque([(START,False)])
while q:
 pc,d=q.popleft();assert START<=pc<END and pc%4==0
 if pc in seen:assert seen[pc]==d;continue
 x=w(pc);k=flow(x);seen[pc]=d
 if d:
  if k=='unsupported_trap' and x>>26==0 and x&63==13 and f'{pc:08x}' in DB and flow(w(pc-4))=='conditional_likely':breaks.append(f'{pc:08x}');continue
  assert k=='linear',(hex(pc),k);continue
 if k=='linear':q.append((pc+4,False));continue
 assert k not in('computed_jump','unsupported_trap','unsupported_encoding')
 if k=='computed_call':assert f'{pc:08x}' in CC,hex(pc)
 tgt=((pc+4)&0xf0000000)|((x&0x3ffffff)<<2);fall=pc+8;imm=struct.unpack('<h',struct.pack('<H',x&0xffff))[0];bt=pc+4+imm*4
 if k in('conditional','conditional_likely'):tgt=bt;q+=[(pc+4,True),(bt,False),(fall,False)]
 elif k=='unconditional_branch':tgt=bt;q+=[(pc+4,True),(bt,False)]
 elif k in('call','computed_call'):q+=[(pc+4,True),(fall,False)]
 elif k=='jump':
  q+=[(pc+4,True)]
  if START<=tgt<END:q+=[(tgt,False)]
  else:assert TJ.get(f'{pc:08x}')==f'{tgt:08x}' and f'{tgt:08x}' in ent0,hex(pc)
 elif k=='return':q+=[(pc+4,True)]
 edges.append((pc,k,tgt))
assert set(seen)==set(range(START,END,4)),'not every word reachable'
calls={f'{p:08x}':f'{t:08x}' for p,k,t in edges if k=='call'};assert calls==C['expected_calls']
inv=json.loads((exp/'inventory.json').read_text());ent={f['entry'] for f in inv['functions']};assert len(ent)==C['baseline']['inventory_count']
assert sorted({t for t in calls.values() if t in ent})==C['known_callees'] and sorted({t for t in calls.values() if t not in ent})==C['unresolved_callees']
assert sorted(f'{p:08x}' for p,k,t in edges if k=='computed_call')==sorted(CC) and {f'{p:08x}':f'{t:08x}' for p,k,t in edges if k=='jump' and not START<=t<END}==TJ and sorted(breaks)==sorted(DB)
assert sorted(pc for pc in seen if w(pc)==0)==sorted(int(z,16) for z in C['zero_words'])
assert sum(1 for p,k,t in edges if k=='conditional_likely')==C['likely_count']
cov=json.loads((exp/'coverage.json').read_text());tx=[b for b in cov['blocks'] if b['name']=='.text'][0]
und=lambda a:any(int(x['start'],16)<=a<=int(x['end'],16) for x in tx['undefined_ranges'])
assert all(und(a) for a in range(START,END)) and (und(END) if not C.get('next_word_function_entry') else True)
owned={int(i['address'],16) for f in inv['functions'] for i in f['instructions']};assert not any(START<=a<END for a in owned)
if C.get('next_word_function_entry'):assert f'{END:08x}' in ent and END in owned
else:assert END not in owned
# every raw JAL/J in all saved functions that reaches the span (independent of Ghidra references).
inc=[]
for f in inv['functions']:
 for i in f['instructions']:
  a=int(i['address'],16);x=w(a)
  if x>>26 in(2,3):
   t=((a+4)&0xf0000000)|((x&0x3ffffff)<<2)
   if START<=t<END:inc.append({'site':i['address'],'owner_entry':f['entry'],'owner_name':f['name'],'op':x>>26,'target':f'{t:08x}'})
assert [{k:v for k,v in i.items() if k in('site','owner_entry','owner_name')} for i in inc]==[{k:i[k] for k in('site','owner_entry','owner_name')} for i in C['incoming']] and all(i['target']==C['entry'] and i['op']==3 for i in inc)
res={'schema_version':1,'status':'pass','config_sha256':sha(cfgp.read_bytes()),'checker_sha256':sha(Path(__file__).read_bytes()),'entry':C['entry'],'span':[C['start'],C['end']],'words':C['words'],'edge_counts':dict(collections.Counter(k for p,k,t in edges)),'calls':calls,'computed_calls':sorted(CC),'tail_jumps':TJ,'delay_breaks':sorted(DB),'next_word_function_entry':bool(C.get('next_word_function_entry')),'known_callees':C['known_callees'],'unresolved_callees':C['unresolved_callees'],'zero_words':C['zero_words'],'incoming_raw_jal_sites':[i['site'] for i in inc],'scope':'Independent raw-byte re-derivation of the guard config. Structural union only; no identity, feasibility, execution, or call-closure beyond the listed callee states.'}
outp.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
