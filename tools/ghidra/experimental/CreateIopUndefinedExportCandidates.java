// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Bounded flow-following experiment for relocation-backed IOP export seeds
 * that were undefined in the baseline listing. Each attempted candidate is
 * isolated in a transaction and rejected/rolled back unless an existing CFG
 * body exactly matches the bounded, statically traversed instruction set.
 * Run only on a copied project with -noanalysis. Accepted candidates are saved
 * to that copy, so do not invoke in -readOnly mode.
 */
public class CreateIopUndefinedExportCandidates extends GhidraScript {
    private static final int MAX_SPAN=0x800; // explicit 2 KiB per-seed decode ceiling
    private static final int MAX_INSNS=512;
    private String hex(byte[] b){return HexFormat.of().formatHex(b);}
    private String sha(byte[] b)throws Exception{return hex(MessageDigest.getInstance("SHA-256").digest(b));}
    private void require(boolean v,String m){if(!v)throw new IllegalStateException(m);}
    private long u32(byte[] b,int p){return (b[p]&255L)|((b[p+1]&255L)<<8)|((b[p+2]&255L)<<16)|((b[p+3]&255L)<<24);}
    private int u16(byte[] b,int p){return (b[p]&255)|((b[p+1]&255)<<8);}
    private JsonArray ranges(AddressSetView set){JsonArray a=new JsonArray();for(AddressRange r:set.getAddressRanges()){JsonObject x=new JsonObject();x.addProperty("start",r.getMinAddress().toString());x.addProperty("end",r.getMaxAddress().toString());x.addProperty("bytes",r.getLength());a.add(x);}return a;}
    private JsonObject textProof(byte[] b)throws Exception{
        require(b.length>=52&&b[0]==0x7f&&b[1]=='E'&&b[2]=='L'&&b[3]=='F'&&b[4]==1&&b[5]==1&&u16(b,16)==0xff80&&u16(b,18)==8,"raw input ELF profile mismatch");
        long shoff=u32(b,32);int es=u16(b,46),n=u16(b,48),str=u16(b,50);require(es>=40&&n>0&&str<n&&shoff+(long)es*n<=b.length,"section header table invalid");int nh=Math.toIntExact(shoff+(long)es*str);long no=u32(b,nh+16),ns=u32(b,nh+20);require(no+ns<=b.length,"section name table invalid");
        int ti=-1,to=-1,ts=-1;Map<Long,Integer> rels=new HashMap<>();
        for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);long name=u32(b,h);require(name<ns,"section name offset invalid");int a=Math.toIntExact(no+name),z=a;while(z<no+ns&&b[z]!=0)z++;String sn=new String(b,a,z-a,StandardCharsets.US_ASCII);if(sn.equals(".text")){require(ti<0,"multiple .text sections");ti=i;to=Math.toIntExact(u32(b,h+16));ts=Math.toIntExact(u32(b,h+20));require(u32(b,h+12)==0&&(u32(b,h+8)&4)!=0,"raw .text not executable base-zero");}}
        require(ti>=0&&to>=0&&ts>=0&&(long)to+ts<=b.length,".text section invalid");
        for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);if((int)u32(b,h+4)!=9||(int)u32(b,h+28)!=ti)continue;long off=u32(b,h+16),sz=u32(b,h+20);int ent=(int)u32(b,h+36);require(ent==8&&sz%8==0&&off+sz<=b.length,".rel.text malformed");for(int at=0;at<sz;at+=8){int p=Math.toIntExact(off)+at;long site=u32(b,p);require(!rels.containsKey(site),"duplicate .rel.text site");rels.put(site,(int)u32(b,p+4));}}
        JsonObject o=new JsonObject();o.addProperty("text_offset",to);o.addProperty("text_size",ts);o.addProperty("text_sha256",sha(Arrays.copyOfRange(b,to,to+ts)));o.addProperty("text_section_index",ti);o.add("relocations",new Gson().toJsonTree(rels));return o;
    }
    private String blockSha(MemoryBlock b)throws Exception{MessageDigest md=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[65536];long off=0;while(off<b.getSize()){int n=(int)Math.min(buf.length,b.getSize()-off);b.getBytes(b.getStart().add(off),buf,0,n);md.update(buf,0,n);off+=n;}return hex(md.digest());}
    private Map<String,String> instructionState(){Map<String,String> m=new TreeMap<>();for(Instruction i:currentProgram.getListing().getInstructions(true))try{m.put(i.getAddress().toString(),hex(i.getBytes()));}catch(Exception e){throw new RuntimeException(e);}return m;}
    private Map<String,String> dataState(){Map<String,String> m=new TreeMap<>();for(Data d:currentProgram.getListing().getDefinedData(true))m.put(d.getAddress()+"|"+d.getLength()+"|"+d.getDataType().getPathName(),d.getMaxAddress().toString());return m;}
    private Map<String,String> memoryState()throws Exception{Map<String,String> m=new TreeMap<>();for(MemoryBlock b:currentProgram.getMemory().getBlocks())if(b.isInitialized()){MessageDigest md=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[65536];long off=0;while(off<b.getSize()){int n=(int)Math.min(buf.length,b.getSize()-off);b.getBytes(b.getStart().add(off),buf,0,n);md.update(buf,0,n);off+=n;}m.put(b.getName()+"@"+b.getStart(),hex(md.digest()));}return m;}
    private Set<String> functionRows(FunctionManager fm){Set<String>s=new TreeSet<>();for(Function f:fm.getFunctions(true))s.add(f.getEntryPoint()+"|"+f.getName()+"|"+ranges(f.getBody()));return s;}
    private AddressSet instructionSet(AddressSetView body){AddressSet s=new AddressSet();for(Instruction i:currentProgram.getListing().getInstructions(body,true))s.addRange(i.getAddress(),i.getMaxAddress());return s;}
    private boolean inside(AddressSetView s,long textSize){if(s.isEmpty())return false;for(AddressRange r:s.getAddressRanges())if(r.getMinAddress().getOffset()<0||r.getMaxAddress().getOffset()>=textSize)return false;return true;}
    private void enqueue(Address a,Address start,Address end,ArrayDeque<Address> q)throws Exception{
        if(a==null)throw new IllegalStateException("unresolved flow/fallthrough edge");
        if(a.getOffset()<start.getOffset()||a.getOffset()>end.getOffset()||(a.getOffset()&3)!=0)throw new IllegalStateException("flow leaves bounded forward .text span at "+a);
        q.add(a);
    }
    private JsonObject auditAndCreate(JsonObject seed,byte[] raw,JsonObject proof,MemoryBlock text,FunctionManager fm)throws Exception{
        long target=seed.get("target_text_offset").getAsLong(),site=seed.get("relocation_site_text_offset").getAsLong(),table=seed.get("table_text_offset").getAsLong();int ordinal=seed.get("ordinal").getAsInt();
        JsonObject result=new JsonObject();result.addProperty("target_text_offset",String.format("%08x",target));result.addProperty("relocation_site_text_offset",String.format("%08x",site));result.addProperty("library",seed.get("library").getAsString());result.addProperty("ordinal",ordinal);
        if((target&3)!=0||target>=text.getSize()||site!=table+20L+4L*ordinal){result.addProperty("status","rejected_seed_arithmetic");return result;}
        byte[] txt=Arrays.copyOfRange(raw,proof.get("text_offset").getAsInt(),proof.get("text_offset").getAsInt()+proof.get("text_size").getAsInt());
        int relInfo=findRel(raw,proof.get("text_section_index").getAsInt(),site);long add=u32(txt,Math.toIntExact(site));
        if((relInfo>>>8)!=0||(relInfo&255)!=2||((add+0x1000L)&0xffffffffL)!=((target+0x1000L)&0xffffffffL)||u32(txt,Math.toIntExact(table))!=0x41c00000L){result.addProperty("status","rejected_pointer_proof");return result;}
        Address start=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(target);Address end=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(Math.min(text.getSize()-1,target+MAX_SPAN-1));
        if(fm.getFunctionAt(start)!=null){result.addProperty("status","already_saved_function_entry");return result;}
        if(fm.getFunctionContaining(start)!=null){result.addProperty("status","already_function_owned");return result;}
        if(currentProgram.getListing().getInstructionAt(start)!=null){result.addProperty("status","already_decoded_after_other_export_seed");return result;}
        if(currentProgram.getListing().getDefinedDataContaining(start)!=null){result.addProperty("status","rejected_existing_defined_data");return result;}

        int tx=currentProgram.startTransaction("bounded relocation-backed undefined export seed");boolean commit=false;
        try{
            Map<String,String> beforeInstructions=instructionState(),beforeData=dataState(),beforeMemory=memoryState();Set<String> beforeFunctions=functionRows(fm);int beforeCount=fm.getFunctionCount();
            AddressSet allowed=new AddressSet(start,end);Set<Long> visited=new TreeSet<>(),newlyDecoded=new TreeSet<>(),delaySlots=new HashSet<>();ArrayDeque<Address> queue=new ArrayDeque<>();queue.add(start);int steps=0;
            while(!queue.isEmpty()){
                monitor.checkCancelled();Address at=queue.remove();long off=at.getOffset();if(!visited.add(off))continue;
                if(++steps>MAX_INSNS)throw new IllegalStateException("bounded flow exceeded instruction-count ceiling");
                if(!allowed.contains(at))throw new IllegalStateException("flow address outside allowed range");
                if(fm.getFunctionContaining(at)!=null||fm.getFunctionAt(at)!=null)throw new IllegalStateException("flow collides with saved function at "+at);
                Instruction ins=currentProgram.getListing().getInstructionAt(at);
                if(ins==null){if(currentProgram.getListing().getDefinedDataContaining(at)!=null)throw new IllegalStateException("flow collides with defined data at "+at);
                    Map<String,String> beforeDecode=instructionState();AddressSet one=new AddressSet(at,at.add(3));DisassembleCommand cmd=new DisassembleCommand(new AddressSet(at),allowed,false);cmd.enableCodeAnalysis(false);
                    if(!cmd.applyTo(currentProgram,monitor))throw new IllegalStateException("bounded linear-flow disassembly failed at "+at+": "+cmd.getStatusMsg());
                    AddressSet decoded=new AddressSet(cmd.getDisassembledAddressSet());AddressSet escaped=new AddressSet(decoded);escaped.delete(allowed);if(!escaped.isEmpty())throw new IllegalStateException("disassembler escaped bounded .text span at "+at+" decoded="+ranges(decoded));
                    ins=currentProgram.getListing().getInstructionAt(at);if(ins==null||ins.getLength()!=4)throw new IllegalStateException("seed did not decode to an aligned MIPS word at "+at);
                    Map<String,String> afterDecode=instructionState();for(Map.Entry<String,String> row:afterDecode.entrySet())if(!beforeDecode.containsKey(row.getKey())){Address fresh=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(row.getKey());if(!allowed.contains(fresh))throw new IllegalStateException("linear decoder added instruction outside allowed span at "+fresh);newlyDecoded.add(fresh.getOffset());}
                    for(String old:beforeDecode.keySet())if(!Objects.equals(beforeDecode.get(old),afterDecode.get(old)))throw new IllegalStateException("linear decoder changed pre-existing instruction at "+old);
                }
                if(ins.getLength()!=4||(off&3)!=0)throw new IllegalStateException("non-word code unit in IOP .text at "+at);
                byte[] rawBytes=new byte[4];currentProgram.getMemory().getBytes(at,rawBytes);if(!Arrays.equals(rawBytes,Arrays.copyOfRange(txt,Math.toIntExact(off),Math.toIntExact(off+4))))throw new IllegalStateException("decoded instruction bytes differ from pinned raw .text at "+at);
                if(delaySlots.contains(off))continue;
                long word=u32(txt,Math.toIntExact(off));FlowType flow=ins.getFlowType();
                if(word==0x03e00008L){Address delay=at.add(4);delaySlots.add(delay.getOffset());enqueue(delay,start,end,queue);continue;} // jr ra; delay slot only
                if(flow.isCall()){
                    Address delay=at.add(4);delaySlots.add(delay.getOffset());enqueue(delay,start,end,queue);enqueue(ins.getFallThrough(),start,end,queue);continue;
                }
                if(flow.isJump()){
                    Address delay=at.add(4);delaySlots.add(delay.getOffset());enqueue(delay,start,end,queue);Address[] flows=ins.getFlows();
                    if(flows.length==0||flow.isComputed())throw new IllegalStateException("unresolved computed jump at "+at);
                    for(Address f:flows)enqueue(f,start,end,queue);
                    if(flow.isConditional())enqueue(ins.getFallThrough(),start,end,queue);
                    continue;
                }
                if(flow.hasFallthrough()){enqueue(ins.getFallThrough(),start,end,queue);continue;}
                if(flow.isTerminal())continue;
                Address[] flows=ins.getFlows();if(flows.length>0){for(Address f:flows)enqueue(f,start,end,queue);continue;}
                throw new IllegalStateException("instruction has no bounded static successor or terminal return at "+at+" "+ins);
            }
            AddressSet traversed=new AddressSet();for(long off:visited)traversed.addRange(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off),currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off+3));
            AddressSetView body=CreateFunctionCmd.getFunctionBody(currentProgram,start,monitor);AddressSet bodyInstructions=instructionSet(body);AddressSet missed=new AddressSet(bodyInstructions);missed.delete(traversed);AddressSet absent=new AddressSet(traversed);absent.delete(bodyInstructions);
            boolean overlap=false;JsonArray collisions=new JsonArray();for(Function f:fm.getFunctions(true)){AddressSetView hit=f.getBody().intersect(body);if(!hit.isEmpty()){overlap=true;JsonObject c=new JsonObject();c.addProperty("entry",f.getEntryPoint().toString());c.add("ranges",ranges(hit));collisions.add(c);}}
            result.add("traversed_ranges",ranges(traversed));result.add("computed_body_ranges",ranges(body));result.add("computed_body_collisions",collisions);result.add("body_missing_traversed_ranges",ranges(absent));result.add("body_extra_instruction_ranges",ranges(missed));
            if(body.isEmpty()||!body.contains(start)||!inside(body,text.getSize())||overlap||!missed.isEmpty()||!absent.isEmpty())throw new IllegalStateException("computed function body does not exactly equal bounded CFG instruction traversal");
            for(Instruction i:currentProgram.getListing().getInstructions(true)){} // force listing materialization before global delta check
            Map<String,String> afterInstructions=instructionState(),afterData=dataState(),afterMemory=memoryState();Set<String> added=new TreeSet<>(afterInstructions.keySet());added.removeAll(beforeInstructions.keySet());Set<String> expected=new TreeSet<>();for(long off:newlyDecoded)expected.add(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off).toString());
            if(!added.equals(expected))throw new IllegalStateException("global instruction listing delta differs from exact newly decoded CFG words: expected="+expected+" actual="+added);
            for(String a:beforeInstructions.keySet())if(!Objects.equals(beforeInstructions.get(a),afterInstructions.get(a)))throw new IllegalStateException("pre-existing instruction changed at "+a);
            if(!beforeData.equals(afterData))throw new IllegalStateException("defined-data listing changed");if(!beforeMemory.equals(afterMemory))throw new IllegalStateException("initialized memory changed");
            boolean overlapNew=false;AddressSet bodySet=new AddressSet(body);for(Function f:fm.getFunctions(true))if(!f.getBody().intersect(bodySet).isEmpty())overlapNew=true;if(overlapNew)throw new IllegalStateException("candidate CFG overlaps a saved function body");
            String name=String.format("IOP_EXPORT_%08X_PROVISIONAL",target);CreateFunctionCmd create=new CreateFunctionCmd(name,start,body,SourceType.ANALYSIS);if(!create.applyTo(currentProgram,monitor))throw new IllegalStateException("CreateFunctionCmd failed: "+create.getStatusMsg());Function made=fm.getFunctionAt(start);
            if(made==null||!made.getBody().equals(body)||made.getSymbol().getSource()!=SourceType.ANALYSIS)throw new IllegalStateException("created function differs from bounded body/source");
            if(fm.getFunctionCount()!=beforeCount+1)throw new IllegalStateException("function count delta not exactly +1");Set<String> rows=functionRows(fm);if(rows.size()!=beforeFunctions.size()+1||!rows.containsAll(beforeFunctions))throw new IllegalStateException("existing function entry/name/body set changed");
            result.addProperty("new_instruction_count",newlyDecoded.size());result.add("new_instruction_addresses",new Gson().toJsonTree(expected));result.add("created_function",functionRow(made));result.addProperty("status","created_bounded_provisional_cfg_candidate");result.addProperty("claim_limits","Relocation-backed export seed and bounded CFG disassembly only. Original function identity, exact true extent, correct decoding, runtime reachability, registration, and semantics remain unproved.");commit=true;
        }catch(Exception e){result.addProperty("status","rejected_bounded_flow");result.addProperty("reason",e.getClass().getSimpleName()+": "+e.getMessage());}
        finally{currentProgram.endTransaction(tx,commit);}
        return result;
    }
    private int findRel(byte[] b,int textIndex,long site)throws Exception{long shoff=u32(b,32);int es=u16(b,46),n=u16(b,48),hits=0,found=0;for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);if((int)u32(b,h+4)!=9||(int)u32(b,h+28)!=textIndex)continue;long off=u32(b,h+16),sz=u32(b,h+20);int ents=(int)u32(b,h+36);if(ents!=8||sz%8!=0||off+sz>b.length)continue;for(int p=0;p<sz;p+=8){int at=Math.toIntExact(off)+p;if(u32(b,at)==site){hits++;found=(int)u32(b,at+4);}}}require(hits==1,"export pointer slot lacks unique .rel.text record");return found;}
    private JsonObject functionRow(Function f){JsonObject o=new JsonObject();o.addProperty("entry",f.getEntryPoint().toString());o.addProperty("name",f.getName());o.addProperty("body_bytes",f.getBody().getNumAddresses());o.add("body_ranges",ranges(f.getBody()));return o;}
    public void run()throws Exception{
        String[] args=getScriptArgs();require(args.length==3||args.length==4,"Expected output JSON, raw ELF path, seed manifest, optional one target offset");byte[] raw=Files.readAllBytes(Paths.get(args[1]));String rawHash=sha(raw);JsonObject manifest=JsonParser.parseString(Files.readString(Paths.get(args[2]),StandardCharsets.UTF_8)).getAsJsonObject();JsonObject module=manifest.getAsJsonObject("modules").getAsJsonObject(currentProgram.getName());require(module!=null&&module.get("module_sha256").getAsString().equals(rawHash)&&rawHash.equals(currentProgram.getExecutableSHA256()),"program/raw/seed identity mismatch");
        require("MIPS:LE:32:default".equals(currentProgram.getLanguageID().toString())&&"default".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString()),"Ghidra language/compiler mismatch");JsonObject proof=textProof(raw);require(proof.get("text_size").getAsInt()==module.get("text_size").getAsInt()&&proof.get("text_sha256").getAsString().equals(module.get("text_sha256").getAsString()),"raw text proof differs from seed metadata");
        MemoryBlock text=null;for(MemoryBlock b:currentProgram.getMemory().getBlocks())if(b.getName().equals(".text")){require(text==null,"multiple Ghidra .text blocks");text=b;}require(text!=null&&text.isInitialized()&&text.isExecute()&&text.getStart().getOffset()==0&&text.getSize()==proof.get("text_size").getAsLong()&&blockSha(text).equals(proof.get("text_sha256").getAsString()),"Ghidra .text mapping/hash mismatch");
        FunctionManager fm=currentProgram.getFunctionManager();int initialFunctionCount=fm.getFunctionCount();Set<String> initialFunctionRows=functionRows(fm);JsonArray rows=new JsonArray();TreeMap<String,JsonObject> unique=new TreeMap<>();for(JsonElement e:module.getAsJsonArray("entries")){JsonObject seed=e.getAsJsonObject();if(!"undefined".equals(seed.get("listing_status").getAsString()))continue;unique.putIfAbsent(seed.get("target_text_offset").getAsString(),seed);}
        // A previous multi-seed process rolled back accepted candidates when a
        // later seed was rejected. Require one explicit seed per invocation
        // whenever this module has more than one undefined export target.
        require(args.length==4||unique.size()<=1,"multi-seed invocation rejected before mutation; supply exactly one target text offset");
        String selected=args.length==4?args[3].toLowerCase(Locale.ROOT):null;boolean foundSelected=selected==null;
        for(JsonObject seed:unique.values()){String target=String.format("%08x",seed.get("target_text_offset").getAsLong());if(selected!=null&&!selected.equals(target))continue;foundSelected=true;monitor.checkCancelled();rows.add(auditAndCreate(seed,raw,proof,text,fm));}
        require(foundSelected,"selected target offset is not an undefined export seed for this module");
        TreeMap<String,Integer> counts=new TreeMap<>();int persistedCreated=0;JsonArray persistenceChecks=new JsonArray();for(JsonElement e:rows){JsonObject row=e.getAsJsonObject();String s=row.get("status").getAsString();counts.put(s,counts.getOrDefault(s,0)+1);if(s.equals("created_bounded_provisional_cfg_candidate")){String addr=row.get("created_function").getAsJsonObject().get("entry").getAsString();Function saved=fm.getFunctionAt(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addr));boolean present=saved!=null&&saved.getName().equals(row.get("created_function").getAsJsonObject().get("name").getAsString());JsonObject check=new JsonObject();check.addProperty("entry",addr);check.addProperty("present_after_all_candidates",present);persistenceChecks.add(check);if(present)persistedCreated++;else row.addProperty("persistence_status","created_then_absent_after_later_candidates");}}
        boolean functionSetPreserved=true;Set<String> currentRows=functionRows(fm);for(String row:initialFunctionRows)if(!currentRows.contains(row))functionSetPreserved=false;
        JsonObject out=new JsonObject();out.addProperty("schema_version",1);out.addProperty("program",currentProgram.getName());out.addProperty("executable_sha256",rawHash);out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString());out.addProperty("ghidra_version",getGhidraVersion());out.addProperty("seed_manifest_sha256",sha(Files.readAllBytes(Paths.get(args[2]))));out.addProperty("decode_policy","Flow follows only bounded forward .text addresses starting at a relocation-backed R_MIPS_32/symbol-zero export seed. Each undefined instruction is decoded as a single four-byte word; calls do not follow callees; MIPS delay slots are explicitly included; `jr ra` terminates after its delay slot. Maximum candidate span 0x800 bytes and 512 instructions. Any unresolved computed jump, out-of-range edge, code/data/function collision, byte/listing/memory change outside exact new words, or body/traversal mismatch rolls back that seed transaction.");out.addProperty("candidate_count",rows.size());if(selected!=null)out.addProperty("selected_target_text_offset",selected);out.addProperty("function_count_before",initialFunctionCount);out.addProperty("function_count_after",fm.getFunctionCount());out.addProperty("accepted_candidate_count",counts.getOrDefault("created_bounded_provisional_cfg_candidate",0));out.addProperty("accepted_candidates_persisted_after_all_attempts",persistedCreated);out.addProperty("function_count_delta_matches_persisted_candidate_count",fm.getFunctionCount()==initialFunctionCount+persistedCreated);out.addProperty("all_preexisting_function_rows_preserved",functionSetPreserved);out.add("persistence_checks",persistenceChecks);out.add("disposition_counts",new Gson().toJsonTree(counts));out.add("target_results",rows);out.addProperty("claim_limits","Static bounded disassembly and provisional CFG bodies only. This does not prove original function identity, true extent, correct decoding, runtime reachability, registration, or source semantics.");Path p=Paths.get(args[0]);Files.createDirectories(p.toAbsolutePath().getParent());Files.writeString(p,new GsonBuilder().setPrettyPrinting().create().toJson(out)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);println("IOP_UNDEFINED_EXPORT_CANDIDATES program="+currentProgram.getName()+" dispositions="+counts);
    }
}
