#!/usr/bin/env python3
"""Config-driven reconciliation of one guarded seed against its pinned baseline export. Static only.
usage: post_seed.py CONFIG BASE_EXPORT NEW_EXPORT VERIFY_RESULT OUT_JSON ROOT_OUT_JSON"""
import hashlib,json,pathlib,sys,struct
cfgp,BASE,NEW,VERIFY,OUT,ROOT_OUT=[pathlib.Path(a) for a in sys.argv[1:7]]
C=json.loads(cfgp.read_text());ENTRY=C['entry'];START=int(C['start'],16);END=int(C['end'],16);WORDS=C['words'];BYTES=C['bytes']
OWNERS={i['owner_entry'] for i in C['incoming']};KNOWN=set(C['known_callees'])|(set(C.get('tail_jumps',{}).values()) if C.get('tail_jump_in_callgraph') else set());UNRES=C['unresolved_callees'];N0=C['baseline']['inventory_count']
ELF=pathlib.Path('games/ford-racing-2/extracted/SLES_517.05')
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
bm_p,bi_p,bc_p=BASE/'decompilation/manifest.json',BASE/'inventory.json',BASE/'coverage.json';nm_p,ni_p,nc_p=NEW/'decompilation/manifest.json',NEW/'inventory.json',NEW/'coverage.json'
b,n,bc,nc,bm,nm,vr=read(bi_p),read(ni_p),read(bc_p),read(nc_p),read(bm_p),read(nm_p),read(VERIFY)
pins={'exe':C['baseline']['executable_sha256'],'manifest':C['baseline']['manifest_sha256'],'inventory':C['baseline']['inventory_sha256'],'coverage':C['baseline']['coverage_sha256']}
act={'exe':sha(ELF),'manifest':sha(bm_p),'inventory':sha(bi_p),'coverage':sha(bc_p)}
check('pinned baseline and ELF hashes equal the config pins',act==pins,act)
check('new export identity and reusable verifier pass',n['program']==b['program'] and n['language']==b['language'] and n['executable_sha256']==pins['exe'] and vr['status']=='pass' and vr['details']['inventory_count']==N0+1 and vr['details']['processed_count']==N0+1,{'verifier':vr['status'],'inventory_count':n['inventory_count'],'processed':nm['processed'],'generated':nm['generated'],'failed':nm['failed']})
bf={r['entry']:r for r in b['functions']};nf={r['entry']:r for r in n['functions']}
check('exactly one new function and no removals',set(nf)-set(bf)=={ENTRY} and set(bf)<=set(nf) and len(bf)==N0 and len(nf)==N0+1)
new=nf[ENTRY];ins=new['instructions']
check(f'candidate identity and exact {BYTES}-byte / {WORDS}-word body',new['name']=='candidate_ee_'+ENTRY and new['size']==BYTES and len(ins)==WORDS and [addr(i['address']) for i in ins]==list(range(START,END,4)),{'name':new['name'],'size':new['size'],'blocks':new['blocks']})
exe=ELF.read_bytes();words=[]
for i in ins:
 pc=addr(i['address']);raw=exe[0x1000+pc-0x100000:0x1000+pc-0x100000+4];assert i['bytes']==raw.hex(),i['address'];words.append(raw)
check(f'all {WORDS} candidate instruction words match raw ELF',len(words)==WORDS,{'raw_sha256':hashlib.sha256(b''.join(words)).hexdigest(),'config_window_sha256':C['window_sha256']})
nxt=struct.unpack('<I',exe[0x1000+END-0x100000:0x1000+END-0x100000+4])[0]
tx=[x for x in nc['blocks'] if x['name']=='.text'][0]
NE=C.get('next_word_function_entry')
if NE:check('next word after the span is the entry of a saved function in both exports and keeps its entry address and word',nxt==int(C['next_word'],16) and f'{END:08x}' in bf and f'{END:08x}' in nf and bf[f'{END:08x}']['instructions'][0]['address']==f'{END:08x}' and nf[f'{END:08x}']['instructions'][0]['address']==f'{END:08x}' and ENTRY!=f'{END:08x}',{'word':f'{nxt:08x}','next_function':bf.get(f'{END:08x}',{}).get('name')})
else:check('next word after the span matches the config, stays undefined, and is outside every function',nxt==int(C['next_word'],16) and contains(ranges(tx['undefined_ranges']),END) and not contains(ranges(tx['unowned_instruction_ranges']),END) and not any(END==addr(i['address']) for f in nf.values() for i in f['instructions']),{'word':f'{nxt:08x}'})
for u in UNRES:
 check(f'unresolved callee {u} remains uncreated and undefined',u not in nf and contains(ranges(tx['undefined_ranges']),addr(u)) and not any(addr(i['address'])==addr(u) for f in nf.values() for i in f['instructions']))
ref_deltas=[];graph_deltas=[]
for e,old in bf.items():
 cur=nf[e]
 for k in('name','size','blocks'):assert old.get(k)==cur.get(k),(e,k)
 assert len(old['instructions'])==len(cur['instructions']),e
 for a,c in zip(old['instructions'],cur['instructions']):
  assert all(a[k]==c[k] for k in('address','text','bytes')),(e,a['address'])
  if a.get('references',[])!=c.get('references',[]):ref_deltas.append({'caller':e,'site':a['address'],'old':a['references'],'new':c['references']})
 oc,nc_=set(old['callers']),set(cur['callers']);oe,ne_=set(old['callees']),set(cur['callees'])
 ec=oc|({ENTRY} if e in KNOWN else set());ee=oe|({ENTRY} if e in OWNERS else set())
 assert nc_==ec,(e,'callers',sorted(nc_^ec));assert ne_==ee,(e,'callees',sorted(ne_^ee))
 if ec!=oc:graph_deltas.append({'entry':e,'relation':'callers','added':ENTRY})
 if ee!=oe:graph_deltas.append({'entry':e,'relation':'callees','added':ENTRY})
check(f'all {N0} prior names, sizes, blocks and instruction address/text/bytes preserved',True,{'old_function_count':len(bf)})
exp_refs=sorted(({'caller':i['owner_entry'],'site':i['site'],'old':[{'to':ENTRY,'type':'UNCONDITIONAL_CALL'}],'new':[{'to':ENTRY,'type':'UNCONDITIONAL_CALL','function':ENTRY}]} for i in C['incoming']),key=lambda x:(x['caller'],x['site']))
check('only the pinned incoming call-site reference annotations change, and now resolve to the new function',sorted(ref_deltas,key=lambda x:(x['caller'],x['site']))==exp_refs,ref_deltas)
exp_graph=sorted([(o,'callees') for o in OWNERS]+[(k,'callers') for k in KNOWN])
check('exactly the predicted reciprocal graph additions',sorted((d['entry'],d['relation']) for d in graph_deltas)==exp_graph,graph_deltas)
check('candidate caller set equals the incoming owners and callee set equals the saved callees',set(new['callers'])==OWNERS and set(new['callees'])==KNOWN,{'callers':new['callers'],'callees':new['callees']})
oldc,newc=BASE/'decompilation/functions',NEW/'decompilation/functions';be={r['entry']:r for r in bm['functions']};ne={r['entry']:r for r in nm['functions']}
check('new export manifest reports every function generated',len(ne)==N0+1 and nm['processed']==N0+1 and nm['generated']==N0+1 and nm['failed']==0 and nm['status']=='generated',{'rows':len(ne),'failed':nm['failed'],'status':nm['status']})
changed=[]
for e in be:
 ob=(oldc/(e+'.c')).read_bytes();nb=(newc/(e+'.c')).read_bytes()
 if ob!=nb:
  cnt=nb.count(b'candidate_ee_'+ENTRY.encode());norm=nb.replace(b'candidate_ee_'+ENTRY.encode(),b'func_0x'+ENTRY.encode())
  squash=lambda t:b''.join(t.split())
  assert (norm==ob or squash(norm)==squash(ob)) and cnt>0,('unexpected old C change',e)
  changed.append({'entry':e,'old_sha256':hashlib.sha256(ob).hexdigest(),'new_sha256':hashlib.sha256(nb).hexdigest(),'replacement_count':cnt,'whitespace_reflow_only_beyond_label':norm!=ob})
check('every changed old C output differs only by label substitution (plus decompiler line reflow when the longer name wraps) and the changed set is within the incoming owners',{r['entry'] for r in changed}<=OWNERS and changed,changed)
check('new candidate C artifact matches manifest SHA and byte count',sha(newc/(ENTRY+'.c'))==ne[ENTRY]['sha256'] and (newc/(ENTRY+'.c')).stat().st_size==ne[ENTRY]['bytes'],ne[ENTRY])
check('initialized memory metadata unchanged',b['memory']==n['memory'])
check('string values and references unchanged',b.get('strings')==n.get('strings'),{'strings':len(b.get('strings',[]))})
check('coverage block identity and bookmarks unchanged',[x['name'] for x in bc['blocks']]==[x['name'] for x in nc['blocks']] and bc.get('bookmarks')==nc.get('bookmarks'))
cd=[]
for ob,nb in zip(bc['blocks'],nc['blocks']):
 if ob['name']!='.text':
  assert ob==nb,ob['name'];continue
 for k,d in {'instruction_count':WORDS,'instruction_bytes':BYTES,'function_instruction_bytes':BYTES,'unowned_instruction_count':0,'unowned_instruction_bytes':0,'defined_data_bytes':0,'undefined_bytes':-BYTES}.items():
  assert nb[k]-ob[k]==d,(k,nb[k]-ob[k]);cd.append({'field':k,'old':ob[k],'new':nb[k],'delta':nb[k]-ob[k]})
 assert ranges(ob['unowned_instruction_ranges'])==ranges(nb['unowned_instruction_ranges'])
 assert subtract(ranges(ob['undefined_ranges']),START,END-1)==ranges(nb['undefined_ranges'])
check(f'coverage adds exactly {WORDS} instructions / {BYTES} owned bytes; undefined ranges change only inside the body',len(cd)==7,cd)
res={'schema_version':1,'status':'pass','scope':'one bounded provisional static candidate; not original identity, semantics, runtime reachability, behavior, call-closure beyond listed callee states, or whole-game completeness','config_sha256':sha(cfgp),'checks':checks,'check_count':len(checks),'passed_count':sum(x['passed'] for x in checks),'baseline':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [bm_p,bi_p,bc_p]},'new':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [nm_p,ni_p,nc_p]},'verifier_result':{'path':str(VERIFY),'sha256':sha(VERIFY),'status':vr['status'],'warning_comment_count':vr['details']['warning_comment_count']},'old_function_count':len(bf),'new_function_count':len(nf),'changed_old_C':changed,'reference_deltas':ref_deltas,'callgraph_deltas':graph_deltas,'coverage_delta':cd}
OUT.write_text(json.dumps(res,indent=2)+'\n')
# Independent rehash of every C artifact against both manifests (not via the delta logic above).
for directory,rows in [(oldc,be),(newc,ne)]:
 for e,row in rows.items():assert sha(directory/(e+'.c'))==row['sha256'] and (directory/(e+'.c')).stat().st_size==row['bytes'],e
root={'schema_version':1,'status':'pass','baseline_functions':len(bf),'candidate_functions':len(nf),'all_C_artifact_hashes_recomputed':len(be)+len(ne),'changed_old_C':[(c['entry'],c['replacement_count']) for c in changed],'new_words_checked_against_ELF':WORDS,'candidate_manifest_sha256':sha(nm_p),'candidate_inventory_sha256':sha(ni_p),'warning_comment_count':vr['details']['warning_comment_count'],'scope':res['scope']}
ROOT_OUT.write_text(json.dumps(root,indent=2)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'passed':res['passed_count'],'changed_old_C':root['changed_old_C'],'warnings':root['warning_comment_count']}))
