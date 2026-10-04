"""Independent port of the draft guard's flowKind/traverse plus constant extraction from the Java source. No Ghidra, no execution of game code."""
from pathlib import Path
import struct,json,hashlib,re,collections
r=Path.cwd();java=r/'.scratch/mesh/codex-audit/frontier-3844-01/guard-proposal/CreateEeCandidate001ff038V1.java'
J=java.read_text();assert hashlib.sha256(J.encode()).hexdigest()=='cd664ee0a13fe40ba2fb99c7121de0fafad36ac827a4eeb3348101fd79af9c10'
elf=(r/'games/ford-racing-2/extracted/SLES_517.05').read_bytes()
assert hashlib.sha256(elf).hexdigest()==re.search(r'EXE_SHA = "(\w+)"',J).group(1)
phoff=struct.unpack_from('<I',elf,28)[0];ents,n=struct.unpack_from('<HH',elf,42)
segs=[struct.unpack_from('<IIIIIIII',elf,phoff+i*ents) for i in range(n)]
def read(pc,size=4):
 hits=[s for s in segs if s[0]==1 and s[2]<=pc and pc+size<=s[2]+s[4]];assert len(hits)==1
 s=hits[0];return elf[s[1]+pc-s[2]:s[1]+pc-s[2]+size]
# Guard TEXT_* constants against the unique PT_LOAD mapping.
TEXT_VA=int(re.search(r'TEXT_VA = 0x([0-9a-fA-F]+)L',J).group(1),16);TEXT_FILE=int(re.search(r'TEXT_FILE = 0x([0-9a-fA-F]+)L',J).group(1),16)
text=[s for s in segs if s[0]==1 and s[2]==TEXT_VA];assert len(text)==1 and text[0][1]==TEXT_FILE
START=int(re.search(r'START = 0x([0-9a-fA-F]+)L',J).group(1),16);END=int(re.search(r'END = 0x([0-9a-fA-F]+)L',J).group(1),16);MAX_END=int(re.search(r'MAX_END = 0x([0-9a-fA-F]+)L',J).group(1),16)
assert (START,END,MAX_END)==(0x1ff038,0x1ff140,0x1ff140)
raw=read(START,END-START);assert len(raw)==264
assert hashlib.sha256(raw).hexdigest()==re.search(r'WINDOW_SHA = "(\w+)"',J).group(1)
w=lambda pc:struct.unpack('<I',read(pc))[0]
assert w(START)==0x27bdffa0 and w(END-4)==0x27bd0060 and w(END-8)==0x03e00008 and w(END)==0x27bdff90
assert all(f in J for f in ['0x27bdffa0L','0x27bd0060L','0x03e00008L','0x27bdff90L'])
def flow(x):
 op=x>>26;rs=(x>>21)&31;rt=(x>>16)&31;fn=x&63
 if op==0 and fn==8 and x==0x03e00008:return 'return'
 if op==0 and fn==8:return 'computed_jump'
 if op==0 and fn==9:return 'computed_call'
 if op==0 and fn in (12,13,48,49,50,51,52,54):return 'unsupported_trap'
 if op==0 and fn in (32,34,44,46):return 'unsupported_trap'
 if op in (8,24):return 'unsupported_trap'
 if op==2:return 'jump'
 if op==3:return 'call'
 if op==1:
  if rt in (8,9,10,11,12,14):return 'unsupported_trap'
  if rt in (0,1,2,3,16,17,18,19):return 'conditional_likely' if rt in (2,3,18,19) else 'conditional'
  return 'unsupported_encoding'
 if op==4 and rs==0 and rt==0:return 'unconditional_branch'
 if op in (4,5):return 'conditional'
 if op in (6,7,22,23) and rt!=0:return 'unsupported_encoding'
 if op in (6,7):return 'conditional'
 if op in (20,21,22,23):return 'conditional_likely'
 if op in (16,17,18,19) and rs==8:return 'conditional_likely' if (rt&2) else 'conditional'
 return 'linear'
seen={};edges=[];q=collections.deque([(START,False)])
while q:
 pc,d=q.popleft();assert START<=pc<END and pc%4==0
 if pc in seen:assert seen[pc]==d;continue
 x=w(pc);k=flow(x);seen[pc]=d
 if d:assert k=='linear';continue
 if k=='linear':q.append((pc+4,False));continue
 assert k not in('computed_call','computed_jump','unsupported_trap')
 tgt=((pc+4)&0xf0000000)|((x&0x3ffffff)<<2);fall=pc+8
 imm=struct.unpack('<h',struct.pack('<H',x&0xffff))[0];bt=pc+4+imm*4
 if k in('conditional','conditional_likely'):tgt=bt;q+= [(pc+4,True),(bt,False),(fall,False)]
 elif k=='unconditional_branch':tgt=bt;q+=[(pc+4,True),(bt,False)]
 elif k=='call':q+=[(pc+4,True),(fall,False)]
 elif k=='jump':q+=[(pc+4,True),(tgt,False)]
 elif k=='return':q+=[(pc+4,True)]
 else:raise AssertionError(k)
 edges.append({'site':pc,'kind':k,'target':tgt})
assert len(seen)==66 and set(seen)==set(range(START,END,4))
c=collections.Counter(e['kind'] for e in edges);assert c=={'conditional':5,'call':5,'return':1},c
# Guard's expected call table and zero words, parsed from the Java source.
exp=dict(re.findall(r'expectedCalls\.put\("(\w+)","(\w+)"\)',J));got={f"{e['site']:08x}":f"{e['target']:08x}" for e in edges if e['kind']=='call'}
assert exp==got,(exp,got)
zw=sorted(int(m,16) for m in re.findall(r'wordAt\(raw,0x([0-9a-f]+)L\)==0',J));assert zw==sorted(pc for pc in seen if w(pc)==0)==[0x1ff084,0x1ff0a4,0x1ff0dc,0x1ff0e0,0x1ff0e8]
# Expected new references and decoded flow targets (for review of the Ghidra-side checks).
refs=sorted(f"{e['site']:08x}|{e['target']:08x}|{'UNCONDITIONAL_CALL' if e['kind']=='call' else 'CONDITIONAL_JUMP'}|ANALYSIS" for e in edges if e['kind']!='return')
assert len(refs)==10
assert 'getAsInt()==66' in J and 'expected.getNumAddresses()==264' in J and 'raw.length==264' in J
jal=w(0x200dac);assert jal==0x0c07fc0e and ((0x200db0&0xf0000000)|((jal&0x3ffffff)<<2))==START
assert all(s in J for s in ['"00200dac"','0x00200d10L','candidate_ee_00200d10'])
res={'schema_version':1,'status':'pass','java_sha256':hashlib.sha256(J.encode()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'edge_counts':dict(c),'expected_new_reference_keys':refs,'zero_words':[f'{x:08x}' for x in zw],'scope':'Port of the draft guard classifier and constants against raw ELF PT_LOAD bytes. It does not validate Ghidra reference sources or decoded flow, which require a read-only Ghidra inspection.'}
(r/'.scratch/mesh/codex-root/root-ee-f038-guard-port-validation-02.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res)[:900])
