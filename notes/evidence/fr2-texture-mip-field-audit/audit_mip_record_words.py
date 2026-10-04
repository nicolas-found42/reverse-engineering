#!/usr/bin/env python3
"""Read-only static trace of serialized mip-record fields against the all-56 archive."""
from __future__ import annotations
import collections, hashlib, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from corpus_binding import Baseline
import ps2_container
GAME=ROOT/'games/ford-racing-2'
STATIC=ROOT/'.scratch/evidence/static-export.json'
GS=ROOT/'.scratch/mesh/codex-root/GSRegs-pinned.h'
EXEC=GAME/'extracted/SLES_517.05'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sum_low16(c):
  out=collections.Counter()
  for value,n in c.items(): out[value & 0xffff]+=n
  return out
def main():
  static_raw=STATIC.read_bytes(); static=json.loads(static_raw)
  fs={f['entry'].lower():f for f in static['functions']}
  expected={
    '0022ba30': {'0022bf38':('sw s1,-0x8(v1)','f8ff71ac')},
    '0022c660': {'0022c7a8':('jal 0x0022c9f0','7cb2080c'),'0022c7c0':('sh v1,0x2(s0)','020003a6')},
    '00222358': {'00222494':('jal 0x00222080','2088080c'),'00222498':('_lhu a0,0x2(s0)','02000496'),'0022249c':('lhu v1,0x4(s0)','04000396'),'002224a0':('sh v0,0x0(s0)','000002a6'),'002224ac':('lhu a3,0xc(s0)','0c000796'),'002224c8':('lw a1,0x8(s0)','0800058e'),'00222554':('sd v0,0x20(s5)','2000a2fe')},
    '00222080': {'002220a8':('addu a1,a1,a0','2128a400'),'002220b0':('_sw a1,-0x6e44(gp)','bc9185af')},
    '00222110': {'00222118':('sll a2,a2,0x10','00340600'),'0022213c':('or t4,t2,v0','25604201')},
  }
  checked={}
  for ent,anchors in expected.items():
    by={i['address'].lower():i for i in fs[ent]['instructions']}; checked[ent]={}
    for addr,(txt,bts) in anchors.items():
      i=by[addr]
      if (i['text'],i['bytes'])!=(txt,bts): raise AssertionError((ent,addr,i))
      checked[ent][addr]={'text':txt,'bytes':bts}
  base=Baseline(GAME); entries=base.entries('.ps2;1')
  records=0; words=[collections.Counter() for _ in range(4)]; levels=collections.Counter(); dimensions=collections.Counter(); perfmt=collections.Counter(); qflags=collections.Counter(); by_profile=collections.Counter(); sample=[]
  for e in entries:
    blob=e.load(); parsed=ps2_container.parse(blob)
    for item in parsed['textures']['items']:
      d=item['descriptor_offset']; field=struct.unpack_from('<Q',blob,d+0x38)[0]
      packed=bool(field & 0x100); qflags[packed]+=1
      fmt=item['format']; perfmt[fmt]+=1
      for level in range(item['mips']):
        off=d+0x40+16*level; rec=struct.unpack_from('<4I',blob,off); records+=1
        for j,w in enumerate(rec): words[j][w]+=1
        w,h=item['levels'][level+1]['width'],item['levels'][level+1]['height']
        dimensions[(fmt,packed,w,h)]+=1
        by_profile[(fmt,packed,rec[0]&0xffff,rec[0]>>16,rec[1]&0xffff,rec[1]>>16,rec[2],rec[3]&0xffff,rec[3]>>16)]+=1
        if len(sample)<12: sample.append({'file':e.path,'texture_index':item['index'],'format':fmt,'packed_flag':packed,'mip_level':level+1,'level_dimensions':[w,h],'record_file_offset':off,'words':[f'0x{x:08x}' for x in rec]})
  result={
    'schema_version':1,
    'scope':'Static instruction-field trace + archive-bound record statistics; does not execute game code or emulator.',
    'inputs':{'executable_sha256':sha(EXEC),'static_export_sha256':hashlib.sha256(static_raw).hexdigest(),'gsregs_source_sha256':sha(GS),'corpus_id':base.provenance['corpus_id'],'archive_profile':base.provenance['profile'],'archive_entries':len(entries)},
    'instruction_anchors':checked,
    'corpus':{'textures':dict(perfmt),'packed_flag_texture_counts':{'clear':qflags[False],'set':qflags[True]},'serialized_mip_records':records,'field_value_counts_by_word':[{f'0x{k:08x}':v for k,v in sorted(c.items())} for c in words], 'field_low16_counts':[dict(sorted(sum_low16(c).items())) for c in words], 'record_profile_counts':[{'format':k[0],'packed':k[1],'w0_low16_runtime_TBP_placeholder':k[2],'w0_high16_allocation_size':k[3],'w1_low16_MIPTBP_TBW':k[4],'w1_high16_unresolved':k[5],'w2_source_pointer_placeholder':f'0x{k[6]:08x}','w3_low16_BITBLTBUF_DBW':k[7],'w3_high16_unresolved':k[8],'count':n} for k,n in sorted(by_profile.items())], 'sample_records':sample},
    'field_map_limits':[
      'word0 low16: upload path overwrites it with FUN_00222080 return value at record offset +0; initially zero in every measured serialized record.',
      'word0 high16: FUN_00222358 reads offset +2 as allocation amount for FUN_00222080; FUN_0022c660 recomputes the same offset from FUN_0022c9f0 and stores it as a halfword.',
      'word1 low16: uploader reads offset +4 and uses it in packed MIPTBP1 fields; GSRegs field definition identifies TBW1/2/3 slots.',
      'word2: loader writes a source pointer at offset +8 and uploader reads full word at +8 as source argument to FUN_00222110.',
      'word3 low16: uploader reads offset +12 and passes it as FUN_00222110 parameter 4; helper assembles that argument into the GS BITBLTBUF descriptor field position for DBW.',
      'Only low halfwords of word1 and word3 are consumed by this traced uploader. This does not prove no other consumer uses their high halves.',
      'FUN_00222358 chooses its bit-8 PSM/BPP row once before the mip loop. It halves the selected upload dimensions per iteration and passes the same PSM/BPP values for base and mip calls. This is static control-flow evidence, not a rendering or hardware observation.',
      'Zero DBW values are retained as measured inputs; no claim is made that they are accepted by physical GS hardware or used by every alternate path.'
    ]
  }
  out=Path(__file__).with_name('independent-mip-record-word-audit.json'); out.write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({'status':'pass','output':str(out),'archive_entries':len(entries),'records':records,'textures':dict(perfmt),'word_counts':[len(c) for c in words],'record_profile_count':len(by_profile),'field_map_limits':result['field_map_limits']},indent=2))
if __name__=='__main__': main()
