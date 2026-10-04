"""Derive a schema-2 batch guard config from raw ELF + baseline export for a list of seeds.
usage: make_batch_config.py EXPORT_DIR OUT_CONFIG SEEDS_JSON [REPORT_JSON]  (SEEDS_JSON: list of hex entries). Static only."""
import json,hashlib,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import seedlib
export,out,seeds_p=sys.argv[1],Path(sys.argv[2]),sys.argv[3];report_p=Path(sys.argv[4]) if len(sys.argv)>4 else None
seedlib.load(export);R=Path.cwd();exp=R/export
elf_p=R/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_p.read_bytes();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
get=seedlib.get;inv=seedlib.inv;owned=seedlib.owned;entries=seedlib.entries;unowned=seedlib.unowned
seeds=json.loads(Path(seeds_p).read_text())
excl=set(json.loads(Path(sys.argv[5]).read_text())) if len(sys.argv)>5 else set()
seeds=[x for x in seeds if x not in excl]
dropped={}
walks={}
for s in seeds:
 try:c=seedlib.walk(s)
 except Exception as e:dropped[s]='walk error '+str(e)[:60];continue
 end=int(c['span']['end_exclusive'],16)
 why=None
 if c['rejects']:why='rejects: '+c['rejects'][0]['why']
 elif any(x['word']!='00000000' for x in c['gap_words']):why='gaps with code'
 elif c['next_word_state'] not in('undefined','unowned_instruction') and c['next_word_state']!='owned '+c['span']['end_exclusive']:why='next '+c['next_word_state']
 elif not ((f'{end-8:08x}' in c['returns'] and max(c['returns'])==f'{end-8:08x}' and get(end-8)==0x03e00008) or (f'{end-8:08x}' in c['tail_jumps'] and (get(end-8)>>26)==2 and all(r<f'{end-8:08x}' for r in c['returns']))):why='terminal transfer is neither the last return nor a pinned tail jump'
 elif any(e['kind']=='jump' and not e.get('tail_jump') and not (int(c['span']['start'],16)<=int(e['target'],16)<end) for e in c['edges']):why='J leaves span'
 if not why and any(e['kind']=='call' and e['target']==c['span']['start'] for e in c['edges']):why='self-call (unsupported)'
 if why:dropped[s]=why;continue
 walks[s]=c
def spans(ws):return sorted((int(c['span']['start'],16),int(c['span']['end_exclusive'],16),s) for s,c in ws.items())
# Drop overlapping seeds (keep the earlier one).
changed=True
while changed:
 changed=False;sp=spans(walks)
 for a,b in zip(sp,sp[1:]):
  if b[0]<a[1]:
   dropped[b[2]]=f'overlaps {a[2]}';del walks[b[2]];changed=True;break
 if changed:continue
 # Incoming scan over every decoded address (function instructions, unowned decoded, batch bodies).
 fn_addr={int(i['address'],16):f['entry'] for f in inv['functions'] for i in f['instructions']}
 body={}
 for s,c in walks.items():
  a,b=int(c['span']['start'],16),int(c['span']['end_exclusive'],16)
  gapset={int(x['address'],16) for x in c['gap_words']}
  for pc in range(a,b,4):
   if pc not in gapset:body[pc]=s
 decoded=set(fn_addr)|set(unowned)|set(body)
 spanmap=[(int(c['span']['start'],16),int(c['span']['end_exclusive'],16),s) for s,c in walks.items()]
 import bisect
 starts=sorted(spanmap);keys=[x[0] for x in starts]
 incoming={s:[] for s in walks};bad=None
 for pc in sorted(p for p in decoded if 0x100000<=p<0x217bd4 and p%4==0):
  w=get(pc);op=w>>26
  if op in(1,4,5,6,7,20,21,22,23) or (op in(16,17,18,19) and ((w>>21)&31)==8):
   if op==1 and ((w>>16)&31) not in(0,1,2,3,16,17,18,19):continue
   imm=struct.unpack('<h',struct.pack('<H',w&0xffff))[0];t=pc+4+imm*4;i=bisect.bisect_right(keys,t)-1
   if i>=0:
    a,b,s2=starts[i]
    if a<=t<b and not (a<=pc<b):bad=(s2,f'branch from outside {pc:08x} into {t:08x}');break
   continue
  if op not in(2,3):continue
  t=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
  i=bisect.bisect_right(keys,t)-1
  if i<0:continue
  a,b,s=starts[i]
  if not(a<=t<b):continue
  if body.get(pc)==s and op==2:continue   # in-span J of the same seed
  if t!=a or op!=3:bad=(s,f'reference from {pc:08x} op{op} into {t:08x} (not a JAL to the entry)');break
  owner=fn_addr.get(pc) or body.get(pc)
  incoming[s].append({'site':f'{pc:08x}','owner_entry':owner,'owner_kind':'saved' if pc in fn_addr else 'batch' if pc in body else 'unowned_decoded'})
 if bad:
  dropped[bad[0]]=bad[1];del walks[bad[0]];changed=True
rows=[]
for a,b,s in sorted((int(c['span']['start'],16),int(c['span']['end_exclusive'],16),s) for s,c in walks.items()):
 c=walks[s];batch_entries=set(walks)
 calls={e['site']:e['target'] for e in c['edges'] if e['kind']=='call'}
 known=sorted({t for t in calls.values() if t in entries});bcal=sorted({t for t in calls.values() if t in batch_entries and t not in entries and t!=s})
 if s in calls.values():raise SystemExit(f'self-call {s}')
 unres=sorted({t for t in calls.values() if t not in entries and t not in batch_entries})
 ns=c['next_word_state'];e_=int(c['span']['end_exclusive'],16)
 if ns=='undefined' and f'{e_:08x}' in batch_entries:ns2='batch_entry'
 elif ns.startswith('owned'):ns2='function_entry'
 elif f'{e_:08x}' in batch_entries:ns2='batch_entry'
 else:ns2=ns
 dec=sorted(int(x,16) for x in c['decoded_words']);rng=[]
 for pc in dec:
  if rng and rng[-1][1]==pc:rng[-1][1]=pc+4
  else:rng.append([pc,pc+4])
 inc=sorted(incoming[s],key=lambda x:x['site'])
 for x in inc:
  if x['owner_entry'] is not None:
   x['owner_name']=None;
 rows.append({'entry':s,'start':c['span']['start'],'end':c['span']['end_exclusive'],'words':c['span_words'],'bytes':c['span']['bytes'],'window_sha256':c['span']['sha256'],'first_word':f'{get(a):08x}','delay_word':f'{get(b-4):08x}','next_word':f'{get(b):08x}','next_state':ns2,'likely_count':sum(1 for e in c['edges'] if e['kind']=='conditional_likely'),'expected_calls':calls,'known_callees':known,'batch_callees':bcal,'unresolved_callees':unres,'zero_words':c['zero_words_reached'],'padding_words':[x['address'] for x in c['gap_words']],'computed_calls':c['computed_calls'],'tail_jumps':c['tail_jumps'],'delay_breaks':c['delay_breaks'],'decoded_ranges':[[f'{x:08x}',f'{y:08x}'] for x,y in rng],'incoming':[{'site':x['site'],'owner_entry':x['owner_entry'],'owner_kind':x['owner_kind']} for x in inc]})
conf={'schema_version':2,'baseline':{'executable_sha256':sha(elf_p),'manifest_sha256':sha(exp/'decompilation/manifest.json'),'inventory_sha256':sha(exp/'inventory.json'),'coverage_sha256':sha(exp/'coverage.json'),'inventory_count':len(entries)},'seeds':rows}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(conf,indent=1)+'\n')
rep={'config':str(out),'config_sha256':sha(out),'seed_count':len(rows),'dropped':dropped,'seeds':[r['entry'] for r in rows],'total_words':sum(r['words'] for r in rows),'next_states':{k:sum(1 for r in rows if r['next_state']==k) for k in ('undefined','function_entry','batch_entry','unowned_instruction')},'with_incoming':sum(1 for r in rows if r['incoming']),'decoded_words':sum(sum((y-x)//4 for x,y in [(int(a,16),int(b,16)) for a,b in r['decoded_ranges']]) for r in rows)}
if report_p:report_p.write_text(json.dumps(rep,indent=1)+'\n')
print(json.dumps({k:v for k,v in rep.items() if k!='dropped'}),'dropped',len(dropped))
