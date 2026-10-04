from pathlib import Path
import json,hashlib,struct
root=Path.cwd();base=root/'.scratch/mesh/codex-audit/ee-00200e70-candidate-01/export-3844/decompilation';run=root/'.scratch/mesh/codex-audit/frontier-3844-01/export-3845';new=run/'decompilation'
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
bm=load(base/'manifest.json');nm=load(new/'manifest.json');bi=load(base.parent/'inventory.json');ni=load(run/'inventory.json')
old={r['entry']:r for r in bm['functions']};now={r['entry']:r for r in nm['functions']};assert len(old)==3844 and len(now)==3845 and set(now)-set(old)=={'001ff038'}
for directory,rows in [(base,old),(new,now)]:
 for entry,row in rows.items():
  b=(directory/row['path']).read_bytes();assert sha(b)==row['sha256'],entry
changes={}
for entry,a in old.items():
 b=now[entry];before=(base/a['path']).read_bytes();after=(new/b['path']).read_bytes()
 for k in ('entry','name','external','thunk','completed','status','body_bytes'):assert a[k]==b[k],(entry,k)
 if before!=after:
  assert entry=='00200d10';assert before.replace(b'func_0x001ff038',b'candidate_ee_001ff038')==after
  changes[entry]=before.count(b'func_0x001ff038')
assert changes=={'00200d10':1}
of={r['entry']:r for r in bi['functions']};nf={r['entry']:r for r in ni['functions']}
for entry,a in of.items():
 b=nf[entry]
 for k in ('name','size','blocks'):assert a[k]==b[k],(entry,k)
 assert [(i['address'],i['text'],i['bytes']) for i in a['instructions']]==[(i['address'],i['text'],i['bytes']) for i in b['instructions']],entry
elf=(root/'games/ford-racing-2/extracted/SLES_517.05').read_bytes();h=struct.unpack_from('<16sHHIIIIIHHHHHH',elf);segs=[]
for n in range(h[10]):
 t,off,va,_,length,*_=struct.unpack_from('<8I',elf,h[5]+n*h[9])
 if t==1:segs.append((va,va+length,off))
f=nf['001ff038'];assert f['size']==264 and {int(i['address'],16) for i in f['instructions']}==set(range(0x1ff038,0x1ff140,4))
for ins in f['instructions']:
 a=int(ins['address'],16);offsets=[off+a-start for start,end,off in segs if start<=a and a+4<=end];assert len(offsets)==1;off=offsets[0];assert elf[off:off+4].hex()==ins['bytes']
assert bi['memory']==ni['memory'] and bi['strings']==ni['strings']
res={'schema_version':1,'status':'pass','baseline_functions':3844,'candidate_functions':3845,'all_C_artifact_hashes_recomputed':len(old)+len(now),'old_C_substitution_counts':changes,'all_old_function_names_sizes_blocks_and_instruction_text_bytes_preserved':True,'new_candidate_words_checked_against_unique_ELF_PT_LOAD':66,'memory_block_and_string_inventory_equal':True,'candidate_manifest_sha256':sha((new/'manifest.json').read_bytes()),'candidate_inventory_sha256':sha((run/'inventory.json').read_bytes()),'scope':'Static provisional structural candidate only; no original source identity, semantic, runtime, call-closure or game completeness claim.'}
(root/'.scratch/mesh/codex-root/root-ee-3845-validation-01.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
