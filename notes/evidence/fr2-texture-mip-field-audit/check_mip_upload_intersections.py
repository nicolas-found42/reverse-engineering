from pathlib import Path
import sys,json,re,struct,collections,hashlib
r=Path.cwd();sys.path.insert(0,str(r/'tools'))
from corpus_binding import Baseline
from ps2_container import parse
s=r/'.scratch/mesh/codex-root/github-raw-GSTables.cpp';text=s.read_text();assert hashlib.sha256(s.read_bytes()).hexdigest()=='a9a226297ede32b89177d7bdb04e9d8e21728e7d55799405f6112e97fe4969e8'
shapes={32:(8,8,64,32),16:(16,8,64,64),8:(16,16,128,64),4:(32,16,128,128)};tables={}
for bits,(bw,bh,pw,ph) in shapes.items():
 t=[]
 for name,rows,cols in [(f'_blockTable{bits}',ph//bh,pw//bw),(f'columnTable{bits}',bh,bw)]:
  m=re.search(r'\b'+name+rf'\[{rows}\]\[{cols}\]\s*=\s*\{{(.*?)\}};',text,re.S);assert m
  vals=list(map(int,re.findall(r'\d+',re.sub(r'//[^\n]*','',m.group(1)))));assert len(vals)==rows*cols;t.append([vals[y*cols:(y+1)*cols] for y in range(rows)])
 tables[bits]=t
def address(bits,x,y,width):
 bw,bh,pw,ph=shapes[bits];blocks,cols=tables[bits];page=(y//ph)*(width*64//pw)+x//pw
 return (page*pw*ph+blocks[y%ph//bh][x%pw//bw]*bw*bh+cols[y%bh][x%bw])*(bits//4)
profiles=collections.Counter();levelcounts=collections.Counter()
for entry in Baseline(r/'games/ford-racing-2').entries('.ps2;1'):
 b=entry.load()
 for item in parse(b)['textures']['items']:
  if item['format'] not in (3,4):continue
  d=item['descriptor_offset'];q=struct.unpack_from('<Q',b,d+0x38)[0]
  if not q&256:continue
  for n,level in enumerate(item['levels'][1:]):
   record=struct.unpack_from('<4I',b,d+0x40+16*n);w,h=level['width'],level['height'];profiles[(item['format'],w,h,record[3]&65535,record[1]&65535)]+=1;levelcounts[item['format']]+=1
rows=[]
for (fmt,w,h,dbw,tbw),count in sorted(profiles.items()):
 upload_bits=32 if fmt==3 else 16;read_bits=8 if fmt==3 else 4;written=set()
 for y in range(h//2):
  for x in range(w//2):
   a=address(upload_bits,x,y,dbw);written.update(range(a,a+upload_bits//4))
 sampled=[address(read_bits,x,y,tbw) for y in range(h) for x in range(w)];unwritten=sum(a not in written for a in sampled)
 rows.append({'format':fmt,'logical_dimensions':[w,h],'assumed_transfer_dimensions':[w//2,h//2],'serialized_DBW':dbw,'serialized_TBW':tbw,'mip_records':count,'written_nibbles':len(written),'sampled_pixels':len(sampled),'sampled_pixels_starting_outside_written_nibbles':unwritten,'uniform_base_zero_mapping_full_coverage':unwritten==0,'unique_sample_starts':len(set(sampled))})
result={'schema_version':1,'scope':'Conditional address-intersection experiment using public PCSX2 tables and serialized DBW/TBW words. Both bases normalized to zero. Does not claim correct actual TBP/DBP allocation or GS renderer/silicon behavior. No original game routine executed.','assumptions':['Mip transfer uses descriptor-selected packed format and halved dimensions.','Record+4 TBW and+12 DBW retained in this traced uploader.','Normalized upload and sample base are equal; no evidence of data from other writes included.'],'packed_indexed_mip_records':sum(levelcounts.values()),'profiles':rows,'records_in_incomplete_profiles':sum(x['mip_records'] for x in rows if not x['uniform_base_zero_mapping_full_coverage'])}
p=r/'.scratch/mesh/codex-root/mip-upload-intersections-01.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'packed_records':result['packed_indexed_mip_records'],'profiles':len(rows),'records_in_incomplete_profiles':result['records_in_incomplete_profiles'],'incomplete_profiles':[x for x in rows if not x['uniform_base_zero_mapping_full_coverage']]}))
