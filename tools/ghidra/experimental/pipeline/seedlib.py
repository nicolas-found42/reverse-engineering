import json,struct,hashlib
from pathlib import Path
from jump_table import recognize, read_table
def load(export):
    global R,elf,inv,cov,text,undef,owned,entries,get,unowned
    R=Path.cwd();elf_p=R/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_p.read_bytes()
    exp=R/export;inv=json.loads((exp/'inventory.json').read_text());cov=json.loads((exp/'coverage.json').read_text())
    text=next(x for x in cov['blocks'] if x['name']=='.text');undef=set()
    for r in text['undefined_ranges']:undef.update(range(int(r['start'],16),int(r['end'],16)+1))
    unowned=set()
    for r in text['unowned_instruction_ranges']:unowned.update(range(int(r['start'],16),int(r['end'],16)+1))
    owned={int(i['address'],16):f['entry'] for f in inv['functions'] for i in f['instructions']};entries={f['entry'] for f in inv['functions']}

get=lambda pc:struct.unpack_from('<I',elf,0x1000+pc-0x100000)[0]
def st(w):return w-0x10000 if w&0x8000 else w
def bt(pc,w):return pc+4+(st(w&0xffff)<<2)
def dec(pc,w):
 op=w>>26;rs=w>>21&31;rt=w>>16&31;fn=w&63
 if op==0:
  if fn==8:return('return' if w==0x03e00008 else 'computed_jump',None,None)
  if fn==9:return('computed_call',None,pc+8)
  if fn in(13,48,49,50,51,52,54):return('trap',None,None)
  if fn in(32,34,44,46):return('arithmetic_trap',None,pc+4)
 if op in(8,24):return('arithmetic_trap',None,pc+4)
 if op==2:return('jump',((pc+4)&0xf0000000)|((w&0x3ffffff)<<2),None)
 if op==3:return('call',((pc+4)&0xf0000000)|((w&0x3ffffff)<<2),pc+8)
 if op in(4,5,6,7,20,21,22,23):
  if op in(6,7,22,23) and rt!=0:return('unsupported',None,None)
  if op==4 and rs==0 and rt==0:return('unconditional_branch',bt(pc,w),None)
  return('conditional_likely' if op>=20 else 'conditional',bt(pc,w),pc+8)
 if op==1:
  if rt in(8,9,10,11,12,14):return('trap',None,None)
  if rt not in(0,1,2,3,16,17,18,19):return('unsupported',None,None)
  return('conditional_likely' if rt in(2,3,18,19) else 'conditional',bt(pc,w),pc+8)
 if op in(16,17,18,19) and rs==8:return('conditional_likely' if rt&2 else 'conditional',bt(pc,w),pc+8)
 return('linear',None,pc+4)

def walk(seed_hex,LIMIT=0x2000):
    seed=int(seed_hex,16)
    pending=[(seed,False)];seen={};edges=[];rejects=[];delay_breaks=[];last_kind={};jump_tables=[]
    while pending:
     pc,d=pending.pop()
     if pc in seen:
      if seen[pc]!=d:rejects.append({'address':f'{pc:08x}','why':'both delay-slot and ordinary context'})
      continue
     if not(0x100000<=pc<0x217bd4 and pc%4==0) or abs(pc-seed)>LIMIT:rejects.append({'address':f'{pc:08x}','why':'outside bound'});continue
     if pc in owned:rejects.append({'address':f'{pc:08x}','why':'flows into saved function '+owned[pc]});continue
     if pc not in undef and pc not in unowned:rejects.append({'address':f'{pc:08x}','why':'neither undefined nor unowned-instruction in baseline coverage'});continue
     seen[pc]=d;w=get(pc);k,t,f=dec(pc,w)
     if d:
      if k=='trap' and (w>>26)==0 and (w&63)==13 and last_kind.get(pc-4) in('conditional_likely','cop_branch_likely'):delay_breaks.append(f'{pc:08x}');continue
      if k not in('linear','arithmetic_trap'):rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':'control/trap in delay slot','kind':k})
      continue
     if k=='computed_jump':
      found=recognize(get,pc,max(seed,0x100000))
      if found is not None:
       try:targets=read_table(elf,found['table'],found['count'])
       except (ValueError,struct.error):targets=[]
       if targets and all(0x100000<=a<0x217bd4 and a%4==0 and abs(a-seed)<=LIMIT and a not in owned and (a in undef or a in unowned) for a in targets):
        pin={key:f'{found[key]:08x}' for key in ('site','table','guard_site')}
        pin.update(count=found['count'],targets=[f'{a:08x}' for a in targets],table_sha256=hashlib.sha256(struct.pack(f'<{len(targets)}I',*targets)).hexdigest())
        jump_tables.append(pin);edges.append({'site':f'{pc:08x}','word':f'{w:08x}','kind':'switch','delay':f'{pc+4:08x}','targets':pin['targets']})
        pending.append((pc+4,True));pending.extend((a,False) for a in set(targets));continue
     if k in('unsupported','computed_jump','trap'):rejects.append({'address':f'{pc:08x}','word':f'{w:08x}','why':k});continue
     last_kind[pc]=k
     if k in('linear','arithmetic_trap'):pending.append((f,False));continue
     e={'site':f'{pc:08x}','word':f'{w:08x}','kind':k,'delay':f'{pc+4:08x}'}
     if t is not None:e['target']=f'{t:08x}'
     if f is not None:e['fallthrough']=f'{f:08x}'
     edges.append(e)
     if k in('conditional','conditional_likely','cop_branch','cop_branch_likely'):pending.extend(((pc+4,True),(t,False),(f,False)))
     elif k in('call','computed_call'):pending.extend(((pc+4,True),(f,False)))
     elif k=='jump' and t in owned:
      if f'{t:08x}' in entries:e['tail_jump']=True;pending.append((pc+4,True))
      else:rejects.append({'address':f'{pc:08x}','why':'J into the middle of saved function '+owned[t]})
     elif k in('jump','unconditional_branch'):pending.extend(((pc+4,True),(t,False)))
     elif k=='return':pending.append((pc+4,True))
    lo,hi=min(seen),max(seen)+4
    # The terminal exception for spans ending in an in-span jump exists only for
    # a shared return: when the last reachable word is an in-span jump or
    # unconditional branch, its exact target must be a reached return word. A
    # looping terminal transfer (notably the last case jumping to itself) is
    # rejected. This is a walk-level scope rule, not feasibility evidence.
    if jump_tables:
     lastw=get(hi-8);lop,lastt=dec(hi-8,lastw)[0],None
     if lop in('jump','unconditional_branch'):
      lastt=dec(hi-8,lastw)[1]
      rets={int(e['site'],16) for e in edges if e['kind']=='return'}
      if lastt is not None and lo<=lastt<hi and lastt not in rets:
       rejects.append({'address':f'{hi-8:08x}','target':f'{lastt:08x}','why':'terminal transfer is neither the last return, a pinned tail jump, nor a jump to a shared return'})
    # Every path into the dispatch must enter at its bounds instruction.
    for table in jump_tables:
     guard,site=int(table['guard_site'],16),int(table['site'],16)
     if seen.get(guard) is not False or any(a not in seen for a in range(guard,site+4,4)):
      rejects.append({'address':table['site'],'why':'switch bounds region is not fully reached'})
     for edge in edges:
      targets=edge.get('targets',[]) if edge['kind']=='switch' else [edge['target']] if 'target' in edge else []
      if any(guard<int(a,16)<=site+4 for a in targets):
       rejects.append({'address':edge['site'],'why':'flow bypasses switch bounds'})
    gaps=[pc for pc in range(lo,hi,4) if pc not in seen]
    res={'seed':f'{seed:08x}','span':{'start':f'{lo:08x}','end_exclusive':f'{hi:08x}','bytes':hi-lo,'sha256':hashlib.sha256(elf[0x1000+lo-0x100000:0x1000+hi-0x100000]).hexdigest()},'reachable_count':len(seen),'span_words':(hi-lo)//4,'gap_words':[{'address':f'{pc:08x}','word':f'{get(pc):08x}'} for pc in gaps],'next_word':f'{get(hi):08x}','next_word_state':'owned '+owned[hi] if hi in owned else 'undefined' if hi in undef else 'unowned_instruction' if hi in unowned else 'other','decoded_words':[f'{pc:08x}' for pc in sorted(seen) if pc in unowned],'span_unowned_words':sum(1 for pc in range(lo,hi,4) if pc in unowned),'edges':edges,'edge_counts':{k:sum(1 for e in edges if e['kind']==k) for k in sorted({e['kind'] for e in edges})},'computed_calls':[e['site'] for e in edges if e['kind']=='computed_call'],'tail_jumps':{e['site']:e['target'] for e in edges if e.get('tail_jump')},'delay_breaks':delay_breaks,'calls':[{'site':e['site'],'target':e['target'],'saved_entry':e['target'] in entries} for e in edges if e['kind']=='call'],'returns':[e['site'] for e in edges if e['kind']=='return'],'rejects':rejects,'zero_words_reached':[f'{pc:08x}' for pc in sorted(seen) if get(pc)==0],'scope':'Structural union walk; not feasible execution, identity, or exact original boundaries.'}
    res['jump_tables']=sorted(jump_tables,key=lambda t:t['site'])
    return res
