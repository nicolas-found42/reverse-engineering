#!/usr/bin/env python3
"""Reconcile one guarded 00200e70 candidate against the pinned 3843 export."""
import copy,hashlib,json,pathlib,sys
BASE=pathlib.Path('.scratch/mesh/codex-audit/ee-00200de0-candidate-01/export-3843')
NEW=pathlib.Path('.scratch/mesh/codex-audit/ee-00200e70-candidate-01/export-3844')
VERIFY=pathlib.Path('.scratch/evidence/decompilation/20261004T172545Z-69af2399c2f44b38865015890cbdd585/result.json')
ELF=pathlib.Path('games/ford-racing-2/extracted/SLES_517.05')
ENTRY='00200e70'; START=int(ENTRY,16); BODY_END=0x00201124; MAX_END=0x00201128
CALLS={'001fbfb8':{'001fc008','001fc02c'},'001fc118':{'001fc174','001fc1dc'}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def fail(msg):raise AssertionError(msg)
def check(out,name,cond,detail=None):
 out.append({'check':name,'passed':bool(cond),'detail':detail})
 if not cond:fail(name+(': '+str(detail) if detail is not None else ''))
def addr(x):return int(x,16)
def ranges(rows):return {(addr(r['start']),addr(r['end'])) for r in rows}
def subtract(intervals,lo,hi):
 o=set()
 for a,b in intervals:
  if b<lo or a>hi:o.add((a,b));continue
  if a<lo:o.add((a,lo-1))
  if b>hi:o.add((hi+1,b))
 return o
bm_path=BASE/'decompilation/manifest.json';bi_path=BASE/'inventory.json';bc_path=BASE/'coverage.json'
nm_path=NEW/'decompilation/manifest.json';ni_path=NEW/'inventory.json';nc_path=NEW/'coverage.json'
b=read(bi_path);n=read(ni_path);bc=read(bc_path);nc=read(nc_path);bm=read(bm_path);nm=read(nm_path);vr=read(VERIFY)
checks=[]
expected={'exe':'216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95','manifest':'3716978f8352119e6f413ba61305c4e0ae28f3bf9a3115ee36a26fec183486a8','inventory':'41bde5a7b57f0044d1a7276d762f24500bb50e8611e18ffd7de3ceddf8a14716','coverage':'5019d3e1919eee5ba7801ef7e06ef1c0146081132dfdb0128519f2d390d49e44'}
actual={'exe':sha(ELF),'manifest':sha(bm_path),'inventory':sha(bi_path),'coverage':sha(bc_path)}
check(checks,'pinned 3843 baseline and ELF hashes',actual==expected,actual)
check(checks,'3844 export identity and reusable verifier pass',n['program']==b['program'] and n['language']==b['language'] and n['executable_sha256']==expected['exe'] and vr['status']=='pass' and vr['details']['inventory_count']==3844 and vr['details']['processed_count']==3844,{'verifier':vr['status'],'inventory_count':n['inventory_count'],'processed':nm['processed'],'generated':nm['generated'],'failed':nm['failed']})
bf={r['entry']:r for r in b['functions']};nf={r['entry']:r for r in n['functions']}
check(checks,'one new function and no old entry removals',set(nf)-set(bf)=={ENTRY} and set(bf)<=set(nf),{'baseline':len(bf),'new':len(nf),'added':sorted(set(nf)-set(bf)),'removed':sorted(set(bf)-set(nf))})
new=nf[ENTRY]; newins=new['instructions']; actual_addrs=[addr(i['address']) for i in newins]
check(checks,'candidate identity and exact 692-byte / 173-word body',new['name']=='candidate_ee_'+ENTRY and new['size']==692 and len(newins)==173 and actual_addrs==list(range(START,BODY_END,4)),{'name':new['name'],'size':new['size'],'instructions':len(newins),'first':newins[0]['address'],'last':newins[-1]['address']})
exe=ELF.read_bytes(); raw_words=[]
for ins in newins:
 pc=addr(ins['address']); raw=exe[0x1000+pc-0x00100000:0x1000+pc-0x00100000+4]
 if ins['bytes']!=raw.hex():fail(f'candidate instruction differs from raw ELF at {ins["address"]}')
 raw_words.append(raw.hex())
check(checks,'all 173 candidate instruction words match raw ELF',len(raw_words)==173 and sum(len(bytes.fromhex(x)) for x in raw_words)==692,{'matched_words':len(raw_words),'matched_bytes':sum(len(bytes.fromhex(x)) for x in raw_words),'raw_sha256':hashlib.sha256(bytes.fromhex(''.join(raw_words))).hexdigest()})
check(checks,'terminal zero remains outside the function and undefined',not any(i['address']=='00201124' for i in newins) and any(addr(r['start'])<=0x00201124<=addr(r['end']) for block in nc['blocks'] if block['name']=='.text' for r in block['undefined_ranges']) and not any(addr(r['start'])<=0x00201124<=addr(r['end']) for block in nc['blocks'] if block['name']=='.text' for r in block['unowned_instruction_ranges']) and not any(d['address']=='00201124' for d in n.get('strings',[])),{'raw_word':exe[0x1000+0x00201124-0x00100000:0x1000+0x00201124-0x00100000+4].hex(),'candidate_last':newins[-1]['address']})
# All 3843 old functions keep identity, body/basic-block ranges, and every instruction address/text/byte.
ref_sites={(caller,site) for caller,sites in CALLS.items() for site in sites}; ref_deltas=[]; graph_deltas=[]; old_semantics=True
for entry,old in bf.items():
 cur=nf[entry]
 for key in ('name','size','blocks'):
  if old.get(key)!=cur.get(key):fail(f'old {key} changed at {entry}')
 oi=old['instructions'];ni=cur['instructions']
 if len(oi)!=len(ni):fail(f'old instruction count changed at {entry}')
 for a,c in zip(oi,ni):
  if any(a[k]!=c[k] for k in ('address','text','bytes')):fail(f'old instruction {a.get("address")} changed at {entry}')
  if a.get('references',[])!=c.get('references',[]):
   site=(entry,a['address'])
   if site not in ref_sites:fail(f'unexpected old reference delta at {entry}:{a["address"]}')
   if len(a['references'])!=len(c['references']):fail(f'reference count changed at {entry}:{a["address"]}')
   for oldref,newref in zip(a['references'],c['references']):
    if {k:v for k,v in oldref.items() if k!='function'}!={k:v for k,v in newref.items() if k!='function'}:fail(f'reference target/type changed at {entry}:{a["address"]}')
    if oldref.get('function')==newref.get('function'):fail(f'expected function annotation change absent at {entry}:{a["address"]}')
   ref_deltas.append({'caller':entry,'site':a['address'],'old':a['references'],'new':c['references']})
 old_callers=set(old['callers']);new_callers=set(cur['callers']);old_callees=set(old['callees']);new_callees=set(cur['callees'])
 expected_callers=old_callers|({ENTRY} if entry in {'00201610','00201720'} else set())
 expected_callees=old_callees|({ENTRY} if entry in CALLS else set())
 if new_callers!=expected_callers:fail(f'caller graph changed unexpectedly at {entry}')
 if new_callees!=expected_callees:fail(f'callee graph changed unexpectedly at {entry}')
 if expected_callers!=old_callers:graph_deltas.append({'entry':entry,'relation':'callers','old':sorted(old_callers),'new':sorted(new_callers)})
 if expected_callees!=old_callees:graph_deltas.append({'entry':entry,'relation':'callees','old':sorted(old_callees),'new':sorted(new_callees)})
check(checks,'all 3843 prior names, body ranges, blocks, and instruction text/bytes preserved',old_semantics,{'old_function_count':len(bf)})
check(checks,'exact four old callsite reference annotations resolve to new candidate',len(ref_deltas)==4 and {(r['caller'],r['site']) for r in ref_deltas}==ref_sites,ref_deltas)
check(checks,'exact reciprocal graph delta for two caller functions',len(graph_deltas)==2 and {(d['entry'],d['relation']) for d in graph_deltas}=={('001fbfb8','callees'),('001fc118','callees')},graph_deltas)
check(checks,'candidate caller set is the two provisional callers and there are no callees',set(new['callers'])==set(CALLS) and not new['callees'],{'callers':new['callers'],'callees':new['callees']})
# All 3843 old generated artifacts stay byte-identical except 4 callee-name substitutions (2 in each caller).
old_c=BASE/'decompilation/functions';new_c=NEW/'decompilation/functions';be={r['entry']:r for r in bm['functions']};ne={r['entry']:r for r in nm['functions']}
check(checks,'full 3844 export manifest reports every function generated',len(ne)==3844 and nm['processed']==3844 and nm['generated']==3844 and nm['failed']==0 and nm['status']=='generated',{'rows':len(ne),'processed':nm['processed'],'generated':nm['generated'],'failed':nm['failed'],'status':nm['status']})
changed=[]
for entry in be:
 oldbytes=(old_c/(entry+'.c')).read_bytes();newbytes=(new_c/(entry+'.c')).read_bytes()
 if hashlib.sha256(oldbytes).digest()!=hashlib.sha256(newbytes).digest():
  count=newbytes.count(b'candidate_ee_00200e70'); normalized=newbytes.replace(b'candidate_ee_00200e70',b'func_0x00200e70')
  if entry not in CALLS or normalized!=oldbytes or count!=2:fail(f'unexpected old C change at {entry}: replacements={count}')
  changed.append({'entry':entry,'old_bytes':len(oldbytes),'new_bytes':len(newbytes),'old_sha256':hashlib.sha256(oldbytes).hexdigest(),'new_sha256':hashlib.sha256(newbytes).hexdigest(),'only_change':'two func_0x00200e70 -> candidate_ee_00200e70 substitutions','replacement_count':count})
check(checks,'only the two expected old caller C outputs change, with two labels each',{r['entry'] for r in changed}==set(CALLS) and all(r['replacement_count']==2 for r in changed),changed)
check(checks,'new candidate C artifact matches manifest SHA and byte count',sha(new_c/(ENTRY+'.c'))==ne[ENTRY]['sha256'] and (new_c/(ENTRY+'.c')).stat().st_size==ne[ENTRY]['bytes'],ne[ENTRY])
# Inventory memory and string arrays are unchanged.
check(checks,'initialized memory metadata unchanged',b['memory']==n['memory'],{'blocks':len(b['memory'])})
check(checks,'string values and references unchanged',b.get('strings')==n.get('strings'),{'strings':len(b.get('strings',[]))})
check(checks,'coverage blocks and bookmarks unchanged',len(bc['blocks'])==len(nc['blocks']) and [x['name'] for x in bc['blocks']]==[x['name'] for x in nc['blocks']] and bc.get('bookmarks')==nc.get('bookmarks'),{'blocks':len(nc['blocks']),'bookmarks':len(nc.get('bookmarks',[]))})
# The only coverage classification change is the 692-byte owned body; the 4-byte zero stays undefined.
coverage_delta=[]
for oldblock,newblock in zip(bc['blocks'],nc['blocks']):
 if oldblock['name']!='.text':
  if oldblock!=newblock:fail('non-.text coverage changed: '+oldblock['name'])
  continue
 deltas={'instruction_count':173,'instruction_bytes':692,'function_instruction_bytes':692,'unowned_instruction_count':0,'unowned_instruction_bytes':0,'defined_data_bytes':0,'undefined_bytes':-692}
 for key,expected_delta in deltas.items():
  actual_delta=newblock[key]-oldblock[key]
  if actual_delta!=expected_delta:fail(f'.text {key} delta {actual_delta} != {expected_delta}')
  coverage_delta.append({'field':key,'old':oldblock[key],'new':newblock[key],'delta':actual_delta})
 if ranges(oldblock['unowned_instruction_ranges'])!=ranges(newblock['unowned_instruction_ranges']):fail('unowned instruction ranges changed')
 if subtract(ranges(oldblock['undefined_ranges']),START,BODY_END-1)!=ranges(newblock['undefined_ranges']):fail('undefined ranges changed outside candidate body')
check(checks,'coverage adds exactly 173 instructions / 692 owned bytes and leaves terminal zero undefined',len(coverage_delta)==7 and any(addr(r['start'])<=0x00201124<=addr(r['end']) for block in nc['blocks'] if block['name']=='.text' for r in block['undefined_ranges']),coverage_delta)
result={'schema_version':1,'status':'pass','scope':'one bounded provisional static candidate; not original identity, semantics, runtime reachability, behavior, or whole-game completeness','checks':checks,'check_count':len(checks),'passed_count':sum(x['passed'] for x in checks),'baseline':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [bm_path,bi_path,bc_path]},'new':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [nm_path,ni_path,nc_path]},'verifier_result':{'path':str(VERIFY),'sha256':sha(VERIFY),'status':vr['status']},'candidate':{'entry':ENTRY,'body_bytes':692,'instruction_words':173,'maximum_window_bytes':696,'terminal_zero_excluded':'00201124','incoming_callers':sorted(CALLS),'incoming_call_sites':sorted(f'{c}:{s}' for c,sites in CALLS.items() for s in sites)},'old_function_count':len(bf),'new_function_count':len(nf),'changed_old_C':changed,'callsite_reference_deltas':ref_deltas,'callgraph_deltas':graph_deltas,'coverage_delta':coverage_delta}
out=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.scratch/mesh/codex-audit/ee-00200e70-candidate-01/reconciliation-3843-3844.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'passed':sum(x['passed'] for x in checks),'old_functions':len(bf),'new_functions':len(nf),'changed_old_C':changed,'coverage_delta':coverage_delta,'output':str(out)}))
