from pathlib import Path
import json,hashlib,struct
root=Path.cwd();capture=root/'.scratch/mesh/codex-root/texture-independent-review/mip-loader-draw-object-identity-raw-02.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(capture)=='47224a61953f22773aa0cad8e497f393bcde5193b9a43c273cbbf50996a8ff46'
x=json.loads(capture.read_text());inventory=Path(x['inventory_path']);assert sha(inventory)==x['inventory_sha256']
inv=json.loads(inventory.read_text());assert inv['inventory_count']==3837
elf_path=root/'games/ford-racing-2/extracted/SLES_517.05';elf=elf_path.read_bytes();assert sha(elf_path)==x['executable_sha256']
h=struct.unpack_from('<16sHHIIIIIHHHHHH',elf);segs=[]
for n in range(h[10]):
 t,off,va,_,length,*_=struct.unpack_from('<8I',elf,h[5]+n*h[9])
 if t==1:segs.append((va,va+length,off))
functions={f['entry']:f for f in inv['functions']};seen=set();count=0
for entry,spans in x['instruction_spans'].items():
 saved={i['address']:i for i in functions[entry]['instructions']}
 for item in spans:
  a=int(item['address'],16);offsets=[off+a-start for start,end,off in segs if start<=a and a+4<=end];assert len(offsets)==1
  assert elf[offsets[0]:offsets[0]+4].hex()==item['bytes'],(entry,item)
  assert saved[item['address']]['bytes']==item['bytes'] and saved[item['address']]['text']==item['text'],(entry,item)
  seen.add(a);count+=1
macro=Path(x['pcpyld_reference']['path']);assert sha(macro)==x['pcpyld_reference']['sha256']
assert x['pcpyld_reference']['macro'] in macro.read_text()
pristine=root/'.scratch/mesh/codex-root/PS2Recomp/ps2xRuntime/include/ps2_runtime_macros.h'
assert x['pcpyld_reference']['macro'] in pristine.read_text()
result={'schema_version':1,'status':'pass','checker_sha256':sha(Path(__file__)),'capture_sha256':sha(capture),'inventory_sha256':sha(inventory),'ELF_sha256':sha(elf_path),'captured_instruction_occurrences_checked':count,'unique_instruction_addresses_checked':len(seen),'function_spans':{k:len(v) for k,v in x['instruction_spans'].items()},'PCPYLD_reference_header_sha256':sha(macro),'pristine_header_sha256':sha(pristine),'PCPYLD_definition_equals_pristine_public':True,'whole_headers_equal':macro.read_bytes()==pristine.read_bytes(),'method':'All saved bounded spans matched exact instruction bytes/text in pinned3837 inventory and unique original ELF PT_LOAD mappings. Root separately read group/table selection and TEX1 emission source, confirming slot bits23:20, group stride0x114, +ec pointer table, and TEX1 lowword+18/highword+14. Raw capture stays ignored.','checker_history':'First run passed all raw spans but incorrectly required the whole patched reference header to equal pristine. Header differences exist in separate EE macros; the exact PCPYLD definition is independently equal. Equality check narrowed to the used macro, and whole-header difference is recorded.','limits':'This validates bytes/text/pins and a static pointer relationship under valid handle/index/non-null paths. No actual object lifetime, draw submission or sampled level proof.'}
(root/'.scratch/mesh/codex-root/root-mip-identity-validation-01.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
