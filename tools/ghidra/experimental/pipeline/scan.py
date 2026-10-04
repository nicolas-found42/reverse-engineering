import json, struct, hashlib
from pathlib import Path
root=Path.cwd(); import sys;exp=root/sys.argv[1]
elf=root/'games/ford-racing-2/extracted/SLES_517.05'
raw=elf.read_bytes(); invp=exp/'inventory.json'; covp=exp/'coverage.json'
inv=json.loads(invp.read_text()); cov=json.loads(covp.read_text())
text=next(x for x in cov['blocks'] if x['name']=='.text')
functions={f['entry']:f for f in inv['functions']}; owned={int(i['address'],16):f['entry'] for f in inv['functions'] for i in f['instructions']}
undefined=set(); unowned=set()
for r in text['undefined_ranges']: undefined.update(range(int(r['start'],16),int(r['end'],16)+1))
for r in text['unowned_instruction_ranges']: unowned.update(range(int(r['start'],16),int(r['end'],16)+1))
def word(pc): return struct.unpack_from('<I',raw,0x1000+pc-0x100000)[0]
def dest(pc,w): return (((pc+4)&0xf0000000)|((w&0x03ffffff)<<2))
refs={}
for f in inv['functions']:
 for i in f['instructions']:
  pc=int(i['address'],16); w=word(pc); op=w>>26
  if bytes.fromhex(i['bytes']) != raw[0x1000+pc-0x100000:0x1004+pc-0x100000]: raise Exception(f'byte mismatch {i["address"]}')
  if op not in (2,3): continue
  t=dest(pc,w)
  refs.setdefault((op,t),[]).append({'caller':f['entry'],'name':f['name'],'site':i['address'],'word':f'{w:08x}','ref_types':[x['type'] for x in i.get('references',[]) if int(x['to'],16)==t]})
rows=[]
for (op,t),sites in refs.items():
 if not 0x100000 <= t <= 0x217bd3: continue
 state=('function_entry' if f'{t:08x}' in functions else 'owned_instruction' if t in owned else 'unowned_instruction' if t in unowned else 'undefined' if t in undefined else 'other_or_data')
 if state in ('undefined','unowned_instruction'):
  rows.append({'op':'jal' if op==3 else 'j','target':f'{t:08x}','state':state,'target_word':f'{word(t):08x}' if t+4<=0x217bd4 else None,'caller_count':len({x['caller'] for x in sites}),'site_count':len(sites),'callers':sorted({x['caller'] for x in sites}),'sites':sites})
rows.sort(key=lambda x:(-x['site_count'],x['op'],x['target']))
result={'schema_version':1,'status':'read_only_raw_direct_transfer_frontier_3845','pins':{'executable_sha256':hashlib.sha256(raw).hexdigest(),'inventory_sha256':hashlib.sha256(invp.read_bytes()).hexdigest(),'coverage_sha256':hashlib.sha256(covp.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((exp/'decompilation/manifest.json').read_bytes()).hexdigest(),'inventory_count':len(functions),'mapping':'EE ELF .text VA 00100000 -> file offset 0x1000; range 00100000..00217bd3'},'undefined_or_unowned_direct_transfers':rows,'counts':{'rows':len(rows),'jal_targets':sum(x['op']=='jal' for x in rows),'j_targets':sum(x['op']=='j' for x in rows)}}
out=root/sys.argv[2]; out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'rows':[{k:r[k] for k in ('op','target','state','target_word','site_count','callers')} for r in rows]},indent=1))
