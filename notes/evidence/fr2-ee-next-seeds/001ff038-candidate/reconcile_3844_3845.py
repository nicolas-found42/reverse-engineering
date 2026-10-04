#!/usr/bin/env python3
"""Reconcile one guarded 001ff038 candidate against the pinned 3844 export (static, no game execution)."""
import hashlib,json,pathlib,sys
BASE=pathlib.Path('.scratch/mesh/codex-audit/ee-00200e70-candidate-01/export-3844')
NEW=pathlib.Path('.scratch/mesh/codex-audit/frontier-3844-01/export-3845')
VERIFY=pathlib.Path(sys.argv[2])
ELF=pathlib.Path('games/ford-racing-2/extracted/SLES_517.05')
ENTRY='001ff038';START=0x1ff038;END=0x1ff140
OWNER='00200d10';KNOWN={'001ffd70','001fc4e0'};UNRESOLVED=['001ff270','001feb80','001fdb88']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def addr(x):return int(x,16)
checks=[]
def check(name,cond,detail=None):
 checks.append({'check':name,'passed':bool(cond),'detail':detail})
 if not cond:raise AssertionError(name+(': '+json.dumps(detail)[:800] if detail is not None else ''))
def ranges(rows):return {(addr(r['start']),addr(r['end'])) for r in rows}
def contains(rs,x):return any(a<=x<=b for a,b in rs)
def subtract(rs,lo,hi):
 o=set()
 for a,b in rs:
  if b<lo or a>hi:o.add((a,b));continue
  if a<lo:o.add((a,lo-1))
  if b>hi:o.add((hi+1,b))
 return o
bm_p,bi_p,bc_p=BASE/'decompilation/manifest.json',BASE/'inventory.json',BASE/'coverage.json'
nm_p,ni_p,nc_p=NEW/'decompilation/manifest.json',NEW/'inventory.json',NEW/'coverage.json'
b,n,bc,nc,bm,nm,vr=read(bi_p),read(ni_p),read(bc_p),read(nc_p),read(bm_p),read(nm_p),read(VERIFY)
pins={'exe':'216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95','manifest':'1e3f425e7c1a653183a284a240b28f6ff2b2918250b1e1882b0dade4cf9c4ef4','inventory':'b23698a1e4e6bfb61f7d4ca9932b80971f1eb4527f57bb5219d14196586c4a9d','coverage':'2ff0ed89839dc6e4e26f7c8b93f1df7ee111f3c1205385e8c52f2640f13df1f0'}
act={'exe':sha(ELF),'manifest':sha(bm_p),'inventory':sha(bi_p),'coverage':sha(bc_p)}
check('pinned 3844 baseline and ELF hashes',act==pins,act)
check('3845 export identity and reusable verifier pass',n['program']==b['program'] and n['language']==b['language'] and n['executable_sha256']==pins['exe'] and vr['status']=='pass' and vr['details']['inventory_count']==3845 and vr['details']['processed_count']==3845,{'verifier':vr['status'],'inventory_count':n['inventory_count'],'processed':nm['processed'],'generated':nm['generated'],'failed':nm['failed']})
bf={r['entry']:r for r in b['functions']};nf={r['entry']:r for r in n['functions']}
check('exactly one new function and no removals',set(nf)-set(bf)=={ENTRY} and set(bf)<=set(nf) and len(bf)==3844 and len(nf)==3845,{'added':sorted(set(nf)-set(bf)),'removed':sorted(set(bf)-set(nf))})
new=nf[ENTRY];ins=new['instructions'];addrs=[addr(i['address']) for i in ins]
check('candidate identity and exact 264-byte / 66-word body',new['name']=='candidate_ee_'+ENTRY and new['size']==264 and len(ins)==66 and addrs==list(range(START,END,4)),{'name':new['name'],'size':new['size'],'instructions':len(ins),'blocks':new['blocks']})
exe=ELF.read_bytes();words=[]
for i in ins:
 pc=addr(i['address']);raw=exe[0x1000+pc-0x100000:0x1000+pc-0x100000+4]
 assert i['bytes']==raw.hex(),i['address'];words.append(raw)
check('all 66 candidate instruction words match raw ELF',len(words)==66,{'raw_sha256':hashlib.sha256(b''.join(words)).hexdigest()})
nxt=exe[0x1000+END-0x100000:0x1000+END-0x100000+4].hex()
tx=[blk for blk in nc['blocks'] if blk['name']=='.text'][0];bt=[blk for blk in bc['blocks'] if blk['name']=='.text'][0]
check('next word 001ff140 is 27bdff90 (bytes 90ffbd27), remains undefined and outside every function',nxt=='90ffbd27' and contains(ranges(tx['undefined_ranges']),END) and not contains(ranges(tx['unowned_instruction_ranges']),END) and not any(END==addr(i['address']) for f in nf.values() for i in f['instructions']),{'bytes':nxt})
for u in UNRESOLVED:
 x=addr(u)
 check(f'unresolved callee {u} remains uncreated and undefined',u not in nf and contains(ranges(tx['undefined_ranges']),x) and not any(addr(i['address'])==x for f in nf.values() for i in f['instructions']))
# Old functions: identity, blocks, instruction text/bytes preserved; reference/call-graph deltas exactly as predicted.
ref_deltas=[];graph_deltas=[]
for e,old in bf.items():
 cur=nf[e]
 for k in('name','size','blocks'):
  assert old.get(k)==cur.get(k),(e,k)
 assert len(old['instructions'])==len(cur['instructions']),e
 for a,c in zip(old['instructions'],cur['instructions']):
  assert all(a[k]==c[k] for k in('address','text','bytes')),(e,a['address'])
  if a.get('references',[])!=c.get('references',[]):
   ref_deltas.append({'caller':e,'site':a['address'],'old':a['references'],'new':c['references']})
 oc,nc_=set(old['callers']),set(cur['callers']);oe,ne_=set(old['callees']),set(cur['callees'])
 exp_callers=oc|({ENTRY} if e in KNOWN else set());exp_callees=oe|({ENTRY} if e==OWNER else set())
 assert nc_==exp_callers,(e,'callers');assert ne_==exp_callees,(e,'callees')
 if exp_callers!=oc:graph_deltas.append({'entry':e,'relation':'callers','added':ENTRY})
 if exp_callees!=oe:graph_deltas.append({'entry':e,'relation':'callees','added':ENTRY})
check('all 3844 prior names, sizes, blocks and instruction address/text/bytes preserved',True,{'old_function_count':len(bf)})
exp_ref={'caller':OWNER,'site':'00200dac','old':[{'to':ENTRY,'type':'UNCONDITIONAL_CALL'}],'new':[{'to':ENTRY,'type':'UNCONDITIONAL_CALL','function':ENTRY}]}
check('exactly one old reference annotation changes: 00200dac now resolves to the new function',ref_deltas==[exp_ref],ref_deltas)
check('exactly three reciprocal graph additions (owner callee; two known callees gain caller)',sorted((d['entry'],d['relation']) for d in graph_deltas)==sorted([(OWNER,'callees'),('001ffd70','callers'),('001fc4e0','callers')]),graph_deltas)
check('candidate caller set is the owner and callee set is the two preexisting targets',new['callers']==[OWNER] and set(new['callees'])==KNOWN,{'callers':new['callers'],'callees':new['callees']})
oldc,newc=BASE/'decompilation/functions',NEW/'decompilation/functions';be={r['entry']:r for r in bm['functions']};ne={r['entry']:r for r in nm['functions']}
check('3845 export manifest reports every function generated',len(ne)==3845 and nm['processed']==3845 and nm['generated']==3845 and nm['failed']==0 and nm['status']=='generated',{'rows':len(ne),'failed':nm['failed'],'status':nm['status']})
changed=[]
for e in be:
 ob=(oldc/(e+'.c')).read_bytes();nb=(newc/(e+'.c')).read_bytes()
 if ob!=nb:
  cnt=nb.count(b'candidate_ee_001ff038');norm=nb.replace(b'candidate_ee_001ff038',b'func_0x001ff038')
  assert norm==ob and cnt>0,('unexpected old C change',e)
  changed.append({'entry':e,'old_sha256':hashlib.sha256(ob).hexdigest(),'new_sha256':hashlib.sha256(nb).hexdigest(),'replacement_count':cnt,'only_change':'func_0x001ff038 -> candidate_ee_001ff038'})
check('every changed old C output differs only by label substitution; changed set equals the owner',{r['entry'] for r in changed}=={OWNER},changed)
check('new candidate C artifact matches manifest SHA and byte count',sha(newc/(ENTRY+'.c'))==ne[ENTRY]['sha256'] and (newc/(ENTRY+'.c')).stat().st_size==ne[ENTRY]['bytes'],ne[ENTRY])
check('initialized memory metadata unchanged',b['memory']==n['memory'],{'blocks':len(b['memory'])})
check('string values and references unchanged',b.get('strings')==n.get('strings'),{'strings':len(b.get('strings',[]))})
check('coverage blocks and bookmarks unchanged in identity',[x['name'] for x in bc['blocks']]==[x['name'] for x in nc['blocks']] and bc.get('bookmarks')==nc.get('bookmarks'))
cd=[]
for ob,nb in zip(bc['blocks'],nc['blocks']):
 if ob['name']!='.text':
  assert ob==nb,ob['name'];continue
 for k,d in {'instruction_count':66,'instruction_bytes':264,'function_instruction_bytes':264,'unowned_instruction_count':0,'unowned_instruction_bytes':0,'defined_data_bytes':0,'undefined_bytes':-264}.items():
  assert nb[k]-ob[k]==d,(k,nb[k]-ob[k]);cd.append({'field':k,'old':ob[k],'new':nb[k],'delta':nb[k]-ob[k]})
 assert ranges(ob['unowned_instruction_ranges'])==ranges(nb['unowned_instruction_ranges'])
 assert subtract(ranges(ob['undefined_ranges']),START,END-1)==ranges(nb['undefined_ranges'])
check('coverage adds exactly 66 instructions / 264 owned bytes; undefined ranges change only inside the body',len(cd)==7,cd)
res={'schema_version':1,'status':'pass','scope':'one bounded provisional static candidate; not original identity, semantics, runtime reachability, behavior, call-closure or whole-game completeness','checks':checks,'check_count':len(checks),'passed_count':sum(x['passed'] for x in checks),'baseline':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [bm_p,bi_p,bc_p]},'new':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [nm_p,ni_p,nc_p]},'verifier_result':{'path':str(VERIFY),'sha256':sha(VERIFY),'status':vr['status']},'old_function_count':len(bf),'new_function_count':len(nf),'changed_old_C':changed,'reference_deltas':ref_deltas,'callgraph_deltas':graph_deltas,'coverage_delta':cd}
out=pathlib.Path(sys.argv[1]);out.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'passed':res['passed_count'],'changed_old_C':[(c['entry'],c['replacement_count']) for c in changed],'out':str(out)}))
