import json,struct,hashlib
from pathlib import Path
R=Path.cwd(); elf=(R/'games/ford-racing-2/extracted/SLES_517.05').read_bytes(); start=0x1ff038; end=0x1ff140
get=lambda pc: struct.unpack_from('<I',elf,0x1000+pc-0x100000)[0]
def st(w): return w-0x10000 if w&0x8000 else w
def bt(pc,w): return pc+4+(st(w&0xffff)<<2)
def dec(pc,w):
 op=w>>26; rs=w>>21&31; rt=w>>16&31; fn=w&63
 if op==0:
  if fn==8:return ('return' if rs==31 else 'computed_jump',None,None)
  if fn==9:return ('computed_call',None,pc+8)
  if fn in (12,13,48,49,50,51,52,54):return ('trap',None,None)
  if fn in (32,34,44,46):return ('arithmetic_trap',None,pc+4)
 if op in (8,24):return ('arithmetic_trap',None,pc+4)
 if op==2:return ('jump',((pc+4)&0xf0000000)|((w&0x3ffffff)<<2),None)
 if op==3:return ('call',((pc+4)&0xf0000000)|((w&0x3ffffff)<<2),pc+8)
 if op in (4,5,6,7,20,21,22,23):
  if op in (6,7,22,23) and rt!=0:return ('unsupported',None,None)
  typ='conditional_likely' if op>=20 else 'conditional'; return (typ,bt(pc,w),pc+8)
 if op==1:
  if rt in (8,9,10,11,12,14):return ('trap',None,None)
  if rt not in (0,1,2,3,16,17,18,19):return ('unsupported',None,None)
  return ('conditional_likely' if rt in (2,3,18,19) else 'conditional',bt(pc,w),pc+8)
 if op in (16,17,18,19) and rs==8:return ('cop_branch_likely' if rt&2 else 'cop_branch',bt(pc,w),pc+8)
 return ('linear',None,pc+4)
words={pc:get(pc) for pc in range(start,end,4)}
pending=[(start,False)]; seen={}; edges=[]; rejects=[]; delays=set()
while pending:
 pc,isdelay=pending.pop()
 if pc in seen:
  if seen[pc]!=isdelay:rejects.append({'address':f'{pc:08x}','why':'both delay-slot and ordinary context'})
  continue
 if pc not in words:rejects.append({'address':f'{pc:08x}','why':'reachable outside source/comment max interval'});continue
 seen[pc]=isdelay;w=words[pc];kind,target,fall=dec(pc,w)
 if isdelay:
  if kind not in ('linear','arithmetic_trap'):rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':'control/trap instruction in delay slot','kind':kind})
  continue
 if kind=='unsupported':rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':'unsupported branch encoding'});continue
 if kind in ('computed_call','computed_jump'):
  rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':'computed transfer in candidate body','kind':kind});continue
 if kind=='trap':rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':'syscall/break in body'});continue
 if kind in ('linear','arithmetic_trap'):
  pending.append((fall,False));continue
 delay=pc+4;delays.add(delay);e={'site':f'{pc:08x}','word':f'{w:08x}','kind':kind,'delay':f'{delay:08x}'}
 if target is not None:e['target']=f'{target:08x}'
 if fall is not None:e['fallthrough']=f'{fall:08x}'
 edges.append(e)
 if kind in ('conditional','conditional_likely','cop_branch','cop_branch_likely'):
  pending.extend(((delay,True),(target,False),(fall,False)))
  if kind.endswith('likely'):e['not_taken_annuls_delay']=True
 elif kind=='call': pending.extend(((delay,True),(fall,False)))
 elif kind=='jump': pending.extend(((delay,True),(target,False)))
 elif kind=='return':pending.append((delay,True))
 elif kind=='unconditional_branch':pending.extend(((delay,True),(target,False)))
rows=[{'address':f'{pc:08x}','word':f'{words[pc]:08x}','kind':dec(pc,words[pc])[0],'reachable':pc in seen,'delay':seen.get(pc)} for pc in range(start,end,4)]
nonzero=[x for x in rows if int(x['word'],16)!=0]
res={'span':{'start':f'{start:08x}','end':f'{end:08x}','bytes':end-start,'sha256':hashlib.sha256(elf[0x1000+start-0x100000:0x1000+end-0x100000]).hexdigest()},'raw_words':rows,'reachable_count':len(seen),'reachable_addresses':[f'{x:08x}' for x in sorted(seen)],'edges':edges,'rejects':rejects,'unreachable_nonzero':[x for x in nonzero if not x['reachable']],'zero_words':[x['address'] for x in rows if int(x['word'],16)==0],'instruction_class_counts':{k:sum(1 for x in rows if x['kind']==k) for k in sorted({x['kind'] for x in rows})},'terminal_return_sites':[e['site'] for e in edges if e['kind']=='return'],'scope':'Read-only raw-word structural walk. PS2Recomp interval is used only as maximum exploration window; no identity/semantic claim.'}
out=R/'.scratch/mesh/codex-audit/frontier-3844-01/cfg-001ff038.json';out.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:res[k] for k in ['span','reachable_count','edges','rejects','unreachable_nonzero','zero_words','terminal_return_sites']},indent=2))
