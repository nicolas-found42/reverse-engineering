"""Derive a guard config for one seed from the cfg_seed walk + baseline export + raw ELF. Refuses anything outside the guard's supported shape."""
import json,hashlib,os,struct,sys
from pathlib import Path
R=Path.cwd();seed=sys.argv[1];D=R/Path(os.environ.get('FR2_WORK','.scratch/mesh/codex-audit/frontier-3845-01'));exp=Path(sys.argv[2]);out=Path(sys.argv[3])
cfg=json.loads((D/f'cfg-{seed}.json').read_text());inv=json.loads((exp/'inventory.json').read_text())
elf_p=R/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_p.read_bytes()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
get=lambda pc:struct.unpack_from('<I',elf,0x1000+pc-0x100000)[0]
s,e=int(cfg['span']['start'],16),int(cfg['span']['end_exclusive'],16)
nso=cfg['next_word_state'];assert cfg['seed']==cfg['span']['start']==seed and not cfg['rejects'] and not cfg['gap_words']
next_entry=nso.startswith('owned ');assert nso=='undefined' or (next_entry and nso.split()[1]==f'{e:08x}'),nso
assert f'{e-8:08x}' in cfg['returns'] and max(cfg['returns'])==f'{e-8:08x}' and get(e-8)==0x03e00008
for x in cfg['edges']:
 if x['kind']=='jump':assert x.get('tail_jump') or s<=int(x['target'],16)<e,x
entries={f['entry']:f for f in inv['functions']}
calls={c['site']:c['target'] for c in cfg['calls']};assert seed not in calls.values()
known=sorted({t for t in calls.values() if t in entries});unres=sorted({t for t in calls.values() if t not in entries})
incoming=[]
for f in inv['functions']:
 for i in f['instructions']:
  for r in i.get('references',[]):
   try:to=int(r['to'],16)
   except ValueError:continue
   if s<=to<e:
    assert r['to']==seed and r['type']=='UNCONDITIONAL_CALL',(f['entry'],i['address'],r)
    assert f['name'].startswith('candidate_ee_'),f['name']
    incoming.append({'site':i['address'],'owner_entry':f['entry'],'owner_name':f['name'],'owner_symbol_source':'ANALYSIS'})
incoming.sort(key=lambda x:x['site']);assert incoming
conf={'schema_version':1,'entry':seed,'start':f'{s:08x}','end':f'{e:08x}','words':(e-s)//4,'bytes':e-s,'window_sha256':cfg['span']['sha256'],'first_word':f'{get(s):08x}','delay_word':f'{get(e-4):08x}','next_word':f'{get(e):08x}',
 'baseline':{'executable_sha256':sha(elf_p),'manifest_sha256':sha(exp/'decompilation/manifest.json'),'inventory_sha256':sha(exp/'inventory.json'),'coverage_sha256':sha(exp/'coverage.json'),'inventory_count':len(entries)},
 'expected_calls':calls,'known_callees':known,'unresolved_callees':unres,'zero_words':cfg['zero_words_reached'],'likely_count':sum(1 for x in cfg['edges'] if x['kind']=='conditional_likely'),'computed_calls':cfg['computed_calls'],'tail_jumps':cfg['tail_jumps'],'delay_breaks':cfg['delay_breaks'],'next_word_function_entry':next_entry,'incoming':incoming}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(conf,indent=2)+'\n');print(json.dumps(conf)[:700]);print(sha(out))
