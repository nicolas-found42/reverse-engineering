from pathlib import Path
import json,hashlib,struct
root=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
elf_path=root/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_path.read_bytes()
assert sha(elf_path)=='216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95'
head=struct.unpack_from('<16sHHIIIIIHHHHHH',elf);segments=[]
for n in range(head[10]):
 t,off,va,_,size,*_=struct.unpack_from('<8I',elf,head[5]+n*head[9])
 if t==1:segments.append((va,va+size,off))
export=root/'.scratch/evidence/static-export.json';assert sha(export)=='554f29697a3569e10b466e18caea5260d96b5a3a8741b586d811fa26beaa6383'
static=json.loads(export.read_text());assert static['inventory_count']==3446
instructions={i['address']:i for f in static['functions'] for i in f['instructions']}
paths=['notes/evidence/fr2-geometry-vif-preamble/selected-evidence.json','notes/evidence/fr2-geometry-vif-tag-audit/selected-evidence.json','notes/evidence/fr2-geometry-vif-tag-audit/render-path-mode-cycle-and-buffer-selector.json','notes/evidence/fr2-geometry-vu-consumer/anchors.json']
def walk(x):
 if isinstance(x,dict):
  if all(k in x for k in ('address','bytes','text')):yield x
  for value in x.values():yield from walk(value)
 elif isinstance(x,list):
  if len(x)>=3 and all(isinstance(y,str) for y in x[:3]) and len(x[0])==8:
   try:bytes.fromhex(x[0]);bytes.fromhex(x[2])
   except ValueError:pass
   else:yield {'address':x[0],'text':x[1],'bytes':x[2]}
  for value in x:yield from walk(value)
rows=[];unique=set()
for rel in paths:
 p=root/rel;document=json.loads(p.read_text())
 if 'raw_instruction_anchors' in document:node=document['raw_instruction_anchors']
 elif 'instruction_anchors' in document:node=document['instruction_anchors']
 else:node=[document['inline_cnt_layout']['raw_packet_instruction_anchors'],document['render_append_state_path'],document['scratchpad_producer_path']]
 anchors=list(walk(node))
 for anchor in anchors:
  a=int(anchor['address'],16);raw=bytes.fromhex(anchor['bytes']);assert len(raw)==4
  offsets=[off+a-start for start,end,off in segments if start<=a and a+len(raw)<=end];assert len(offsets)==1
  assert elf[offsets[0]:offsets[0]+4]==raw,(rel,anchor)
  item=instructions[anchor['address']];assert item['bytes']==anchor['bytes']
  assert item['text'].lstrip('_')==anchor['text'].lstrip('_'),(rel,item,anchor)
  unique.add(a)
 rows.append({'path':rel,'sha256':sha(p),'anchor_occurrences_checked':len(anchors)})
vu=json.loads((root/paths[-1]).read_text());overlay=root/vu['sources']['overlay5_bin_scratch_path'];blob=overlay.read_bytes()
assert sha(overlay)==vu['sources']['overlay5_bin_sha256'];base=int(vu['overlay_mapping']['section_base'],16)
for anchor in vu['overlay_mapping']['anchors']:
 a=int(anchor['address'],16);assert a==base+8*anchor['pair'];assert blob[a-base:a-base+8].hex()==anchor['raw_bytes']
c=root/vu['sources']['FUN_00128e88_saved_c_scratch_path'];assert sha(c)==vu['sources']['FUN_00128e88_saved_c_sha256']
result={'schema_version':1,'status':'pass','ELF_sha256':sha(elf_path),'static_export_sha256':sha(export),'checker_sha256':sha(Path(__file__)),'EE_anchor_files':rows,'EE_anchor_occurrences_checked':sum(r['anchor_occurrences_checked'] for r in rows),'unique_EE_instruction_addresses_checked':len(unique),'method':'Every bounded EE anchor matched a unique ELF PT_LOAD byte range and saved static instruction text; only Ghidra delay-slot underscore text prefix normalized. Seven VU pairs checked against original overlay bytes and base+8*pair arithmetic. No routines executed.','VU_overlay_sha256':sha(overlay),'VU_pair_anchors_checked':len(vu['overlay_mapping']['anchors']),'packet_saved_C_sha256':sha(c),'scope':'Byte/text anchor and source-pin validation only; annotation meaning, dynamic VIF/GS state and game execution are separate conditional inferences.','prior_failure_disposition':'Earlier anchor0010f9f0 claimed0000628c/lw v0; original ELF had0800668c/lw a2. The mismatch artifact remains in root-geometry-tag-anchor-mismatches-01.json; current source corrects it and adds0010f9f4 for intended cursor load. Root checker first assumed old handoff list-shaped export and failed before anchor checks; current pinned export has functions under a schema dictionary. Second scan recursively treated a list of writer function addresses as an instruction row and stopped; the scanner now walks only explicit anchor containers. No incorrect anchor was accepted by either failed attempt.'}
(root/'.scratch/mesh/codex-root/root-geometry-anchors-validation-01.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
