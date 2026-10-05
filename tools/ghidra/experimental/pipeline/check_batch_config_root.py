"""Independent root check of a schema-2 batch guard config. Re-derives every seed from raw ELF PT_LOAD bytes with a port of the guard
classifier/traversal, checks coverage states from the baseline coverage JSON, and rescans every decoded address for JAL/J into any seed.
No Ghidra, no execution of game code."""
from pathlib import Path
import struct,json,hashlib,sys,collections,bisect
r=Path.cwd();cfgp=Path(sys.argv[1]);exp=Path(sys.argv[2]);outp=Path(sys.argv[3])
C=json.loads(cfgp.read_text());assert C['schema_version']==2
elf_p=r/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(elf)==C['baseline']['executable_sha256']
for k,n in [('manifest_sha256','decompilation/manifest.json'),('inventory_sha256','inventory.json'),('coverage_sha256','coverage.json')]:assert sha((exp/n).read_bytes())==C['baseline'][k],k
phoff=struct.unpack_from('<I',elf,28)[0];ents,n=struct.unpack_from('<HH',elf,42);segs=[struct.unpack_from('<IIIIIIII',elf,phoff+i*ents) for i in range(n)]
def read(pc,size=4):
 h=[s for s in segs if s[0]==1 and s[2]<=pc and pc+size<=s[2]+s[4]];assert len(h)==1;s=h[0];return elf[s[1]+pc-s[2]:s[1]+pc-s[2]+size]
w=lambda pc:struct.unpack('<I',read(pc))[0]

def derive_switch(site, start):
 """Independent forward symbolic replay; does not import the generator recognizer."""
 floor=max(start,site-56)
 jump=w(site);jreg=(jump>>21)&31
 assert jump>>26==0 and jump&0x1fffff==8 and jreg not in(0,31)
 for guard in range(floor,site,4):
  gw=w(guard);index=(gw>>21)&31;flag=(gw>>16)&31;count=gw&0xffff
  if gw>>26!=11 or not(index and flag and index!=flag and 1<=count<=256):continue
  regs=[None]*32;regs[0]=('constant',0);regs[index]=('index',index)
  regs[flag]=('bound',index,count);branched=False;scaled=False;bad=False;load_site=None
  # All table-address definitions must occur after the bound. Definitions
  # before it require reaching-definition analysis, outside this profile.
  for pc in range(guard+4,site,4):
   x=w(pc);op=x>>26;rs=(x>>21)&31;rt=(x>>16)&31;rd=(x>>11)&31;fn=x&63
   imm=struct.unpack('<h',struct.pack('<H',x&65535))[0]
   if x==0:continue
   if op==4:
    if branched or scaled or {rs,rt}!={flag,0} or regs[flag]!=('bound',index,count) or pc+4+imm*4<=site+4:bad=True;break
    branched=True;continue
   if op==5 or (op==0 and fn in(8,9,12,13)):bad=True;break
   value=None;destination=None
   if op==15:
    if rs:bad=True;break
    destination=rt;value=('high',(x&65535)<<16)
   elif op==9:
    destination=rt
    if rt==rs and regs[rs] and regs[rs][0]=='high':value=('high',regs[rs][1]+imm)
   elif op==0 and fn==0:
    if rs:bad=True;break
    destination=rd
    if (x>>6)&31==2 and regs[rt]==('index',index) and branched:value=('scaled',index);scaled=True
   elif op==0 and fn==33:
    if x&0x7ff!=33:bad=True;break
    destination=rd
    for a,b in ((regs[rs],regs[rt]),(regs[rt],regs[rs])):
     if a and a[0]=='high' and b==('scaled',index):value=('base',a[1],index)
   elif op==35:
    destination=rt
    if regs[rs] and regs[rs][0]=='base' and branched:
     value=('dispatch',(regs[rs][1]+imm)&0xffffffff,count);load_site=pc
   elif op==0 and fn in(17,19,24,25,26,27):continue
   elif op==0 and fn in(2,3,4,6,7,10,11,16,18,20,22,23,32,34,35,36,37,38,39,42,43,44,45,46,47,56,58,59,60,62,63):destination=rd
   elif 8<=op<=14 or 32<=op<=39:destination=rt
   elif op in(40,41,43,44,45,46,63):continue
   else:bad=True;break
   if destination:regs[destination]=value
  result=regs[jreg]
  if not bad and branched and result and result[0]=='dispatch' and load_site is not None and all(w(pc)==0 for pc in range(load_site+4,site,4)):
   return {'site':f'{site:08x}','guard_site':f'{guard:08x}','table':f'{result[1]:08x}','count':result[2]}
 raise AssertionError(('switch instruction profile not rederived',hex(site)))

def verify_switch(pin, start, end):
 site=int(pin['site'],16);derived=derive_switch(site,start)
 assert all(pin[k]==derived[k] for k in derived),('switch profile differs',pin['site'])
 table=int(pin['table'],16);count=pin['count'];assert table%4==0
 shoff=struct.unpack_from('<I',elf,32)[0];stride,num=struct.unpack_from('<HH',elf,46);assert stride==40
 sections=[struct.unpack_from('<10I',elf,shoff+i*stride) for i in range(num)]
 matches=[s for s in sections if s[1]==1 and s[2]&2 and not s[2]&4 and s[3]<=table and table+4*count<=s[3]+s[5]]
 assert len(matches)==1,('switch table section mapping',pin['site'])
 raw=read(table,count*4);section=matches[0]
 assert raw==elf[section[4]+table-section[3]:section[4]+table-section[3]+count*4]
 targets=list(struct.unpack(f'<{count}I',raw));assert [f'{t:08x}' for t in targets]==pin['targets']
 assert sha(raw)==pin['table_sha256'],('switch table hash differs',pin['site'])
 assert all(start<=t<end and t%4==0 and t not in fn_addr for t in targets)
 return targets
def flow(x):
 op=x>>26;rs=(x>>21)&31;rt=(x>>16)&31;fn=x&63
 if op==0 and fn==8 and x==0x03e00008:return 'return'
 if op==0 and fn==8:return 'computed_jump'
 if op==0 and fn==9:return 'computed_call'
 if op==0 and fn in (13,48,49,50,51,52,54,32,34,44,46):return 'unsupported_trap'
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
inv=json.loads((exp/'inventory.json').read_text());ent={f['entry'] for f in inv['functions']};assert len(ent)==C['baseline']['inventory_count']
fn_addr={int(i['address'],16):f['entry'] for f in inv['functions'] for i in f['instructions']}
cov=json.loads((exp/'coverage.json').read_text());tx=[b for b in cov['blocks'] if b['name']=='.text'][0]
def rs_(rows):return [(int(x['start'],16),int(x['end'],16)) for x in rows]
UND=rs_(tx['undefined_ranges']);UNO=rs_(tx['unowned_instruction_ranges'])
def inr(rs,a):
 ks=[x[0] for x in rs];i=bisect.bisect_right(ks,a)-1;return i>=0 and rs[i][0]<=a<=rs[i][1]
UND.sort();UNO.sort()
seeds={s['entry']:s for s in C['seeds']};spans=sorted((int(s['start'],16),int(s['end'],16),s['entry']) for s in C['seeds'])
for a,b in zip(spans,spans[1:]):assert a[1]<=b[0],('overlap',a,b)
body={};checked=0;summary=[]
for s in C['seeds']:
 START,END=int(s['start'],16),int(s['end'],16);assert s['entry']==s['start'] and s['words']*4==s['bytes']==END-START
 raw=read(START,END-START);assert sha(raw)==s['window_sha256']
 PAD={int(x,16) for x in s.get('padding_words',[])}
 assert w(START)==int(s['first_word'],16) and w(END-4)==int(s['delay_word'],16) and w(END)==int(s['next_word'],16)
 JT={p['site']:p for p in s.get('jump_tables',[])};assert len(JT)==len(s.get('jump_tables',[]))
 assert w(END-8)==0x03e00008 or (f'{END-8:08x}' in s['tail_jumps'] and w(END-8)>>26==2) or (JT and flow(w(END-8)) in('jump','unconditional_branch','computed_jump'))
 CC=set(s['computed_calls']);TJ=s['tail_jumps'];DB=set(s['delay_breaks'])
 seen={};edges=[];breaks=[];switches={};q=collections.deque([(START,False)])
 while q:
  pc,d=q.popleft();assert START<=pc<END and pc%4==0
  if pc in seen:assert seen[pc]==d;continue
  x=w(pc);k=flow(x);seen[pc]=d
  if d:
   if k=='unsupported_trap' and x>>26==0 and x&63==13 and f'{pc:08x}' in DB and flow(w(pc-4))=='conditional_likely':breaks.append(f'{pc:08x}');continue
   assert k=='linear',(s['entry'],hex(pc),k);continue
  if k=='linear':q.append((pc+4,False));continue
  if k=='computed_jump':
   assert f'{pc:08x}' in JT,('computed jump not pinned',hex(pc))
   targets=verify_switch(JT[f'{pc:08x}'],START,END);switches[f'{pc:08x}']=targets
   q.append((pc+4,True));q.extend((t,False) for t in set(targets));edges.append((pc,'switch',None));continue
  assert k not in('computed_jump','unsupported_trap','unsupported_encoding'),(s['entry'],hex(pc),k)
  if k=='computed_call':assert f'{pc:08x}' in CC
  tgt=((pc+4)&0xf0000000)|((x&0x3ffffff)<<2);fall=pc+8;imm=struct.unpack('<h',struct.pack('<H',x&0xffff))[0];bt=pc+4+imm*4
  if k in('conditional','conditional_likely'):tgt=bt;q+=[(pc+4,True),(bt,False),(fall,False)]
  elif k=='unconditional_branch':tgt=bt;q+=[(pc+4,True),(bt,False)]
  elif k in('call','computed_call'):q+=[(pc+4,True),(fall,False)]
  elif k=='jump':
   q+=[(pc+4,True)]
   if START<=tgt<END:q+=[(tgt,False)]
   else:assert TJ.get(f'{pc:08x}')==f'{tgt:08x}' and f'{tgt:08x}' in ent,(s['entry'],hex(pc))
  elif k=='return':q+=[(pc+4,True)]
  edges.append((pc,k,tgt))
 assert set(switches)==set(JT),('switch sites differ',s['entry'])
 if JT:
  assert any(k=='return' or (k=='jump' and not START<=t<END) for p,k,t in edges),('switch has no return or tail terminal',s['entry'])
 for site,pin in JT.items():
  guard=int(pin['guard_site'],16);jr=int(site,16)
  assert seen.get(guard) is False and all(p in seen for p in range(guard,jr+4,4))
  destinations=[t for p,k,t in edges if k in('conditional','conditional_likely','unconditional_branch','jump','call')]
  destinations.extend(t for ts in switches.values() for t in ts)
  assert all(not guard<t<=jr+4 for t in destinations),('flow bypasses switch bound',site)
 assert set(seen)|PAD==set(range(START,END,4)) and not set(seen)&PAD and all(w(x)==0 for x in PAD),(s['entry'],'reachability differs from pinned padding')
 for pc in seen:body[pc]=s['entry']
 calls={f'{p:08x}':f'{t:08x}' for p,k,t in edges if k=='call'};assert calls==s['expected_calls']
 batch=set(seeds)
 assert sorted({t for t in calls.values() if t in ent})==s['known_callees']
 assert sorted({t for t in calls.values() if t not in ent and t in batch})==s['batch_callees']
 assert sorted({t for t in calls.values() if t not in ent and t not in batch})==s['unresolved_callees']
 assert sorted(f'{p:08x}' for p,k,t in edges if k=='computed_call')==sorted(CC) and {f'{p:08x}':f'{t:08x}' for p,k,t in edges if k=='jump' and not START<=t<END}==TJ and sorted(breaks)==sorted(DB)
 assert sorted(pc for pc in seen if w(pc)==0)==sorted(int(z,16) for z in s['zero_words'])
 assert sum(1 for p,k,t in edges if k=='conditional_likely')==s['likely_count']
 dec=set()
 for a,b in s['decoded_ranges']:dec.update(range(int(a,16),int(b,16),4))
 for pc in range(START,END,4):
  if pc in PAD:continue
  if pc in dec:assert all(inr(UNO,x) for x in range(pc,pc+4)),(s['entry'],'decoded word not unowned',hex(pc))
  else:assert all(inr(UND,x) for x in range(pc,pc+4)),(s['entry'],'undefined word not undefined',hex(pc))
  assert pc not in fn_addr
 ns=s['next_state']
 if ns=='undefined':assert all(inr(UND,x) for x in range(END,END+4)) and END not in fn_addr and f'{END:08x}' not in seeds
 elif ns=='unowned_instruction':assert all(inr(UNO,x) for x in range(END,END+4)) and END not in fn_addr and f'{END:08x}' not in seeds
 elif ns=='function_entry':assert f'{END:08x}' in ent and fn_addr.get(END)==f'{END:08x}'
 elif ns=='batch_entry':assert f'{END:08x}' in seeds
 else:raise AssertionError(ns)
 checked+=len(seen);summary.append({'entry':s['entry'],'words':len(seen),'edges':dict(collections.Counter(k for p,k,t in edges)),'next_state':ns,'decoded_words':len(dec)})
# Incoming: scan every decoded address (function instructions, unowned decoded, batch bodies) for JAL/J into any seed.
decoded=set(fn_addr)|set(body)
for a,b in UNO:decoded.update(range(a&~3 if a%4==0 else a-(a%4),b+1,4))
keys=[x[0] for x in spans];inc={e:[] for e in seeds}
for pc in sorted(p for p in decoded if 0x100000<=p<0x217bd4 and p%4==0):
 x=w(pc)
 op_=x>>26
 if op_ in(1,4,5,6,7,20,21,22,23) or (op_ in(16,17,18,19) and ((x>>21)&31)==8):
  if op_==1 and ((x>>16)&31) not in(0,1,2,3,16,17,18,19):continue
  imm=struct.unpack('<h',struct.pack('<H',x&0xffff))[0];t=pc+4+imm*4;i=bisect.bisect_right(keys,t)-1
  if i>=0:
   a,b,e=spans[i]
   assert not(a<=t<b and not(a<=pc<b)),('branch from outside into a seed',hex(pc),hex(t))
  continue
 if x>>26 not in(2,3):continue
 t=((pc+4)&0xf0000000)|((x&0x3ffffff)<<2);i=bisect.bisect_right(keys,t)-1
 if i<0:continue
 a,b,e=spans[i]
 if not(a<=t<b):continue
 if x>>26==2 and body.get(pc)==e:continue
 assert t==a and x>>26==3,(hex(pc),hex(t))
 inc[e].append({'site':f'{pc:08x}','owner_entry':fn_addr.get(pc) or body.get(pc),'owner_kind':'saved' if pc in fn_addr else 'batch' if pc in body else 'unowned_decoded'})
for e,s in seeds.items():assert sorted(inc[e],key=lambda x:x['site'])==sorted(({k:v for k,v in i.items()} for i in s['incoming']),key=lambda x:x['site']),(e,inc[e],s['incoming'])
res={'schema_version':1,'status':'pass','config_sha256':sha(cfgp.read_bytes()),'checker_sha256':sha(Path(__file__).read_bytes()),'seed_count':len(seeds),'words_checked':checked,'seeds':summary,'incoming_sites':sum(len(v) for v in inc.values()),'scope':'Independent raw-byte re-derivation of every seed in the batch config plus a rescan of all decoded addresses for direct calls into the seeds. Structural union only; no identity, feasibility, execution or call-closure claim beyond the listed callee states.'}
outp.write_text(json.dumps(res,indent=1)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='seeds'}))
