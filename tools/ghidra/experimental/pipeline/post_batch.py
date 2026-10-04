#!/usr/bin/env python3
"""Config-driven reconciliation of one guarded batch against its pinned baseline export. Static only.
usage: post_batch.py CONFIG BASE_EXPORT NEW_EXPORT VERIFY_RESULT OUT_JSON ROOT_OUT_JSON"""
import hashlib,json,pathlib,sys,struct
cfgp,BASE,NEW,VERIFY,OUT,ROOT_OUT=[pathlib.Path(a) for a in sys.argv[1:7]];TXR=pathlib.Path(sys.argv[7]) if len(sys.argv)>7 else cfgp.parent/'run/transaction-result.json'
C=json.loads(cfgp.read_text());S=C['seeds'];K=len(S);N0=C['baseline']['inventory_count'];ELF=pathlib.Path('games/ford-racing-2/extracted/SLES_517.05')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());addr=lambda x:int(x,16)
checks=[]
def check(name,cond,detail=None):
 checks.append({'check':name,'passed':bool(cond),'detail':detail})
 if not cond:raise AssertionError(name+(': '+json.dumps(detail)[:900] if detail is not None else ''))
def ranges(rows):return sorted((addr(r['start']),addr(r['end'])) for r in rows)
def contains(rs,x):return any(a<=x<=b for a,b in rs)
def subtract_set(rs,remove):
 # rs: list of (a,b) inclusive; remove: sorted list of (a,b) inclusive, disjoint
 out=[]
 for a,b in rs:
  cur=a
  for x,y in remove:
   if y<cur or x>b:continue
   if x>cur:out.append((cur,x-1))
   cur=max(cur,y+1)
   if cur>b:break
  if cur<=b:out.append((cur,b))
 return out
bm_p,bi_p,bc_p=BASE/'decompilation/manifest.json',BASE/'inventory.json',BASE/'coverage.json';nm_p,ni_p,nc_p=NEW/'decompilation/manifest.json',NEW/'inventory.json',NEW/'coverage.json'
b,n,bc,nc,bm,nm,vr=read(bi_p),read(ni_p),read(bc_p),read(nc_p),read(bm_p),read(nm_p),read(VERIFY)
pins=C['baseline'];act={'executable_sha256':sha(ELF),'manifest_sha256':sha(bm_p),'inventory_sha256':sha(bi_p),'coverage_sha256':sha(bc_p)}
check('pinned baseline and ELF hashes equal the config pins',all(pins[k]==act[k] for k in act),act)
check('new export identity and reusable verifier pass',n['program']==b['program'] and n['language']==b['language'] and n['executable_sha256']==pins['executable_sha256'] and vr['status']=='pass' and vr['details']['inventory_count']==N0+K and vr['details']['processed_count']==N0+K,{'verifier':vr['status'],'inventory_count':n['inventory_count'],'processed':nm['processed'],'generated':nm['generated'],'failed':nm['failed']})
bf={r['entry']:r for r in b['functions']};nf={r['entry']:r for r in n['functions']};ent={s['entry'] for s in S}
check('exactly K new functions equal to the seed entries and no removals',set(nf)-set(bf)==ent and set(bf)<=set(nf) and len(bf)==N0 and len(nf)==N0+K,{'K':K})
exe=ELF.read_bytes();words_total=0;new_words=[];pre_words=[]
for s in S:
 st,en=addr(s['start']),addr(s['end']);f=nf[s['entry']];ins=f['instructions']
 pad={addr(x) for x in s.get('padding_words',[])};assert f['name']=='candidate_ee_'+s['entry'] and f['size']==s['bytes']-4*len(pad) and len(ins)==s['words']-len(pad) and [addr(i['address']) for i in ins]==[x for x in range(st,en,4) if x not in pad],s['entry']
 dec=set()
 for a,z in s['decoded_ranges']:dec.update(range(addr(a),addr(z),4))
 for i in ins:
  pc=addr(i['address']);raw=exe[0x1000+pc-0x100000:0x1000+pc-0x100000+4];assert i['bytes']==raw.hex(),(s['entry'],i['address'])
  (pre_words if pc in dec else new_words).append(pc)
 words_total+=s['words']-len(pad)
 nxt=struct.unpack('<I',exe[0x1000+en-0x100000:0x1000+en-0x100000+4])[0];assert nxt==int(s['next_word'],16)
check('every candidate has the pinned name, size, address list and raw-ELF-equal words',True,{'seeds':K,'words':words_total,'newly_decoded_words':len(new_words),'preexisting_decoded_words':len(pre_words)})
txb=[x for x in bc['blocks'] if x['name']=='.text'][0];txn=[x for x in nc['blocks'] if x['name']=='.text'][0]
UNDn,UNOn=ranges(txn['undefined_ranges']),ranges(txn['unowned_instruction_ranges'])
allfn_ins={addr(i['address']) for f in nf.values() for i in f['instructions']}
for s in S:
 en=addr(s['end']);ns=s['next_state']
 if ns=='undefined':ok=contains(UNDn,en) and en not in allfn_ins
 elif ns=='unowned_instruction':ok=contains(UNOn,en) and en not in allfn_ins
 elif ns=='function_entry':ok=f'{en:08x}' in bf and f'{en:08x}' in nf and any(i['address']==f'{en:08x}' for i in nf[f'{en:08x}']['instructions'])
 else:ok=f'{en:08x}' in ent and any(i['address']==f'{en:08x}' for i in nf[f'{en:08x}']['instructions'])
 assert ok,(s['entry'],ns)
check('every next word keeps its pinned state in the new export',True)
unres={u for s in S for u in s['unresolved_callees']}
check('unresolved callees remain uncreated and are not claimed by any function',all(u not in nf and addr(u) not in allfn_ins for u in unres),sorted(unres)[:20])
ref_deltas=[];graph_deltas=[]
exp_called={e:set(f['callees']) for e,f in ((e,bf[e]) for e in bf)};exp_callers={e:set(bf[e]['callers']) for e in bf}
for s in S:exp_called[s['entry']]=set();exp_callers[s['entry']]=set()
txr={r['entry']:r for r in json.loads(TXR.read_text())['seeds']}
for s in S:
 for t in set(s['known_callees'])|set(s['batch_callees']):exp_called[s['entry']].add(t);exp_callers[t].add(s['entry'])
 for site,v in txr[s['entry']].get('tail_jumps_with_flow_type',{}).items():
  tgt,flow=v.split('|')
  if flow=='CALL_TERMINATOR':exp_called[s['entry']].add(tgt);exp_callers[tgt].add(s['entry'])
 for i in s['incoming']:
  if i['owner_entry']:exp_called[i['owner_entry']].add(s['entry']);exp_callers[s['entry']].add(i['owner_entry'])
for e,old in bf.items():
 cur=nf[e]
 for k in('name','size','blocks'):assert old.get(k)==cur.get(k),(e,k)
 assert len(old['instructions'])==len(cur['instructions']),e
 for a,c in zip(old['instructions'],cur['instructions']):
  assert all(a[k]==c[k] for k in('address','text','bytes')),(e,a['address'])
  if a.get('references',[])!=c.get('references',[]):ref_deltas.append({'caller':e,'site':a['address'],'old':a['references'],'new':c['references']})
 assert set(cur['callers'])==exp_callers[e],(e,'callers',sorted(set(cur['callers'])^exp_callers[e])[:5]);assert set(cur['callees'])==exp_called[e],(e,'callees',sorted(set(cur['callees'])^exp_called[e])[:5])
 if exp_callers[e]!=set(old['callers']):graph_deltas.append({'entry':e,'relation':'callers','added':sorted(exp_callers[e]-set(old['callers']))})
 if exp_called[e]!=set(old['callees']):graph_deltas.append({'entry':e,'relation':'callees','added':sorted(exp_called[e]-set(old['callees']))})
for s in S:
 f=nf[s['entry']];assert set(f['callers'])==exp_callers[s['entry']] and set(f['callees'])==exp_called[s['entry']],(s['entry'],f['callers'],f['callees'])
check(f'all {N0} prior names, sizes, blocks and instruction address/text/bytes preserved',True,{'old_function_count':len(bf)})
tx_res=json.loads(TXR.read_text());other=[]
for srow in tx_res['seeds']:
 for k in srow.get('non_call_references_into_entry',[]):
  frm,to,typ,src=k.split('|');other.append({'from':frm,'to':to,'type':typ,'source':src})
fn_of={addr(i['address']):e for e,f in bf.items() for i in f['instructions']}
exp_refs=sorted([{'caller':i['owner_entry'],'site':i['site'],'to':s['entry'],'type':'UNCONDITIONAL_CALL'} for s in S for i in s['incoming'] if i['owner_kind']=='saved']+[{'caller':fn_of[addr(o['from'])],'site':o['from'],'to':o['to'],'type':o['type']} for o in other if addr(o['from']) in fn_of],key=lambda x:(x['caller'],x['site'],x['to']))
got=[]
for d in ref_deltas:
 for a_,b_ in zip(d['old'],d['new']):
  if a_!=b_:got.append({'caller':d['caller'],'site':d['site'],'to':b_['to'],'type':b_['type']})
got=sorted(got,key=lambda x:(x['caller'],x['site'],x['to']))
ok=exp_refs==got and all(len(d['old'])==len(d['new']) and all(a_==b_ or (('function' not in a_) and a_['to']==b_['to'] and a_['type']==b_['type'] and b_.get('function')==b_['to'] and b_['to'] in ent) for a_,b_ in zip(d['old'],d['new'])) for d in ref_deltas)
check('only the pinned call-site references and the guard-recorded non-call references to seed entries gain the new function annotation',ok,{'expected':len(exp_refs),'actual':len(got),'non_call_refs_recorded':len(other)})
check('call-graph deltas equal the config prediction for every old and new function',True,{'old_functions_with_graph_change':len(graph_deltas)})
oldc,newc=BASE/'decompilation/functions',NEW/'decompilation/functions';be={r['entry']:r for r in bm['functions']};ne={r['entry']:r for r in nm['functions']}
check('new export manifest reports every function generated',len(ne)==N0+K and nm['processed']==N0+K and nm['generated']==N0+K and nm['failed']==0 and nm['status']=='generated',{'rows':len(ne),'failed':nm['failed'],'status':nm['status']})
changed=[];squash=lambda t:b''.join(t.split());owners={i['owner_entry'] for s in S for i in s['incoming'] if i['owner_kind']=='saved'}
import re,difflib,collections
def norm_labels(t):
 cnt=0
 for s in S:
  for pat in (b'&LAB_'+s['entry'].encode(),b'candidate_ee_'+s['entry'].encode(),b'func_0x'+s['entry'].encode(),b'LAB_'+s['entry'].encode(),b'&DAT_'+s['entry'].encode(),b'DAT_'+s['entry'].encode()):
   cnt+=t.count(pat);t=t.replace(pat,b'SEED_'+s['entry'].encode())
 return t,cnt
TOK=re.compile(rb'\w+|\W');VARPAT=re.compile(rb'^([a-z]{1,2})(Var\d+|Stack_[0-9a-f]+|Gpffff[0-9a-f]+|G[0-9a-f]+)$');UND={b'undefined',b'undefined1',b'undefined2',b'undefined4',b'undefined8'};TYPES={b'code',b'int',b'uint',b'long',b'ulong',b'short',b'ushort',b'char',b'uchar'}
def classify_changes(no,nn):
 """Return (ok, categories) comparing label-normalized old and new text token by token, whitespace-insensitive."""
 ta=[t for t in TOK.findall(no) if not t.isspace()];tb=[t for t in TOK.findall(nn) if not t.isspace()];cats=collections.Counter()
 for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,ta,tb,autojunk=False).get_opcodes():
  if op=='equal':continue
  A,B=ta[i1:i2],tb[j1:j2]
  if op!='replace' or len(A)!=len(B):return False,cats
  for x,y in zip(A,B):
   if x in UND and y in TYPES:cats['type_retyped_undefined_to_typed']+=1
   elif VARPAT.match(x) and VARPAT.match(y) and VARPAT.match(x).group(2)==VARPAT.match(y).group(2) and x!=y:cats['auto_variable_prefix_renamed']+=1
   elif re.match(rb'^_?PTR_SEED_[0-9a-f]{8}_([0-9a-f]{8})$',y) and x in (re.match(rb'^(_?)PTR_SEED_[0-9a-f]{8}_([0-9a-f]{8})$',y).group(1)+b'PTR_LAB_'+re.match(rb'^_?PTR_SEED_[0-9a-f]{8}_([0-9a-f]{8})$',y).group(1),re.match(rb'^(_?)PTR_SEED_[0-9a-f]{8}_([0-9a-f]{8})$',y).group(1)+b'PTR_DAT_'+re.match(rb'^_?PTR_SEED_[0-9a-f]{8}_([0-9a-f]{8})$',y).group(1)):cats['pointer_label_renamed']+=1
   else:return False,cats
 return True,cats
changed=[];owners={i['owner_entry'] for s in S for i in s['incoming'] if i['owner_kind']=='saved'};cat_total=collections.Counter()
for e in be:
 ob=(oldc/(e+'.c')).read_bytes();nb=(newc/(e+'.c')).read_bytes()
 if ob!=nb:
  no,co=norm_labels(ob);nn,cn=norm_labels(nb);ok,cats=classify_changes(no,nn)
  assert ok and cn>0,('unexpected old C change',e,dict(cats))
  cat_total.update(cats)
  changed.append({'entry':e,'old_sha256':hashlib.sha256(ob).hexdigest(),'new_sha256':hashlib.sha256(nb).hexdigest(),'seed_label_occurrences_in_new':cn,'non_label_change_categories':dict(cats)})
check('every changed old C output differs only by seed label substitution, line re-wrap, decompiler retyping of undefined types, auto-variable prefix renames and pointer-label renames, and mentions a seed',all(c['seed_label_occurrences_in_new']>0 for c in changed),{'changed':len(changed),'owners_by_call':len(owners),'category_totals':dict(cat_total)})
check('new candidate C artifacts match their manifest SHA and byte counts',all(sha(newc/(s['entry']+'.c'))==ne[s['entry']]['sha256'] and (newc/(s['entry']+'.c')).stat().st_size==ne[s['entry']]['bytes'] for s in S))
check('initialized memory metadata unchanged',b['memory']==n['memory'])
def strings_ok():
 bs,ns=b.get('strings',[]),n.get('strings',[])
 if len(bs)!=len(ns):return False,0
 annotated=0
 for x,y in zip(bs,ns):
  if x['address']!=y['address'] or x['value']!=y['value'] or len(x['references'])!=len(y['references']):return False,annotated
  for r1,r2 in zip(x['references'],y['references']):
   if r1==r2:continue
   if {k:v for k,v in r1.items() if k!='function'}=={k:v for k,v in r2.items() if k!='function'} and 'function' not in r1 and r2.get('function') in ent:annotated+=1;continue
   return False,annotated
 return True,annotated
ok_s,ann_s=strings_ok()
check('string values and references unchanged, except that references from newly owned instructions gain a function annotation naming a new function',ok_s,{'strings':len(b.get('strings',[])),'reference_function_annotations_added':ann_s})
check('coverage block identity and bookmarks unchanged',[x['name'] for x in bc['blocks']]==[x['name'] for x in nc['blocks']] and bc.get('bookmarks')==nc.get('bookmarks'))
cd=[]
for ob_,nb_ in zip(bc['blocks'],nc['blocks']):
 if ob_['name']!='.text':assert ob_==nb_,ob_['name'];continue
 nw=len(new_words);pw=len(pre_words)
 for k,d in {'instruction_count':nw,'instruction_bytes':4*nw,'function_instruction_bytes':4*words_total,'unowned_instruction_count':-pw,'unowned_instruction_bytes':-4*pw,'defined_data_bytes':0,'undefined_bytes':-4*nw}.items():
  assert nb_[k]-ob_[k]==d,(k,nb_[k]-ob_[k],d);cd.append({'field':k,'old':ob_[k],'new':nb_[k],'delta':nb_[k]-ob_[k]})
 rm_new=sorted((pc,pc+3) for pc in new_words);rm_pre=sorted((pc,pc+3) for pc in pre_words)
 def merge(rs):
  out=[]
  for a,z in rs:
   if out and out[-1][1]+1>=a:out[-1]=(out[-1][0],max(out[-1][1],z))
   else:out.append((a,z))
  return out
 assert merge(subtract_set(ranges(ob_['undefined_ranges']),rm_new))==merge(ranges(nb_['undefined_ranges'])),'undefined ranges'
 assert merge(subtract_set(ranges(ob_['unowned_instruction_ranges']),rm_pre))==merge(ranges(nb_['unowned_instruction_ranges'])),'unowned ranges'
check('coverage deltas equal the config prediction and range changes occur only inside the bodies',len(cd)==7,cd)
res={'schema_version':1,'status':'pass','scope':'bounded provisional static candidates; not original identity, semantics, runtime reachability, behavior, call-closure beyond listed callee states, or whole-game completeness','config_sha256':sha(cfgp),'seed_count':K,'checks':checks,'check_count':len(checks),'passed_count':sum(x['passed'] for x in checks),'baseline':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [bm_p,bi_p,bc_p]},'new':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [nm_p,ni_p,nc_p]},'verifier_result':{'path':str(VERIFY),'sha256':sha(VERIFY),'status':vr['status'],'warning_comment_count':vr['details']['warning_comment_count']},'old_function_count':len(bf),'new_function_count':len(nf),'changed_old_C':changed,'reference_deltas':len(ref_deltas),'callgraph_deltas':graph_deltas,'coverage_delta':cd}
OUT.write_text(json.dumps(res,indent=1)+'\n')
for directory,rows in [(oldc,be),(newc,ne)]:
 for e,row in rows.items():assert sha(directory/(e+'.c'))==row['sha256'] and (directory/(e+'.c')).stat().st_size==row['bytes'],e
ROOT_OUT.write_text(json.dumps({'schema_version':1,'status':'pass','baseline_functions':len(bf),'candidate_functions':len(nf),'all_C_artifact_hashes_recomputed':len(be)+len(ne),'changed_old_C':[(c['entry'],c['seed_label_occurrences_in_new']) for c in changed],'new_words_checked_against_ELF':words_total,'candidate_manifest_sha256':sha(nm_p),'candidate_inventory_sha256':sha(ni_p),'warning_comment_count':vr['details']['warning_comment_count'],'scope':res['scope']},indent=1)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'passed':res['passed_count'],'changed_old_C':len(changed),'warnings':vr['details']['warning_comment_count']}))
