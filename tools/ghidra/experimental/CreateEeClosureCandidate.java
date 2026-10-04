//@category Analysis
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * Experimental single-seed candidate guard. Do not run until the parent has
 * reviewed this source and the exact baseline project copy. This adds no source
 * identity claim; it checks one raw-word CFG hypothesis and rolls back on drift.
 */
public class CreateEeClosureCandidate extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String MANIFEST_SHA = "93ec7a633c9602c53613700e5cb31b403dde10a3c54dbd7f63185562dc6bcf76";
    private static final String INVENTORY_SHA = "c72cf614099d5cea5aafb1a5e85606df0fe3165b43f628bc7f6bb25780468389";
    private static final String WINDOW_SHA = "361f88e28a2c5bd9e2642bc67448cef04d6a6065a83a1e32e8b211b22dbd4088";
    private static final String ENTRY = "00200d10";
    private static final long START = 0x00200d10L, END = 0x00200de0L;
    private static final long TEXT_VA = 0x00100000L, TEXT_FILE = 0x1000L, TEXT_SIZE = 0x00117bd4L;
    private static final int INVENTORY_COUNT = 3841;
    private static final String LANGUAGE = "r5900:LE:32:default";

    private static final class Node {
        final long pc; final boolean delay;
        Node(long p, boolean d) { pc=p; delay=d; }
    }
    private static final class Edge {
        long pc, target, fall; String kind;
        Edge(long p, long t, long f, String k) { pc=p;target=t;fall=f;kind=k; }
    }
    private void req(boolean b, String m) { if (!b) throw new IllegalStateException(m); }
    private String hex(long v) { return String.format(Locale.ROOT, "%08x", v); }
    private String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private Address at(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
    private String bytes(Address a, int n) throws Exception { byte[] b=new byte[n]; currentProgram.getMemory().getBytes(a,b); return HexFormat.of().formatHex(b); }
    private long word(byte[] b, int i) { return (b[i]&255L)|((b[i+1]&255L)<<8)|((b[i+2]&255L)<<16)|((b[i+3]&255L)<<24); }
    private long wordAt(byte[] b,long pc) { return word(b,Math.toIntExact(pc-START)); }
    private long branchTarget(long pc,long w) { int imm=(short)(w&0xffff); return pc+4L+((long)imm<<2); }
    private String canonical(Address a) { return hex(a.getOffset()); }
    private String rangeSummary(AddressSetView set) { StringBuilder b=new StringBuilder();AddressRangeIterator it=set.getAddressRanges();while(it.hasNext()){AddressRange r=it.next();if(b.length()>0)b.append(',');b.append(canonical(r.getMinAddress())).append('-').append(canonical(r.getMaxAddress()));}return b.toString(); }

    private String memoryHash() throws Exception {
        MessageDigest d=MessageDigest.getInstance("SHA-256"); byte[] buf=new byte[65536];
        for(MemoryBlock b:currentProgram.getMemory().getBlocks()) if(b.isInitialized()) {
            d.update(b.getName().getBytes(StandardCharsets.UTF_8)); d.update(b.getStart().toString().getBytes(StandardCharsets.UTF_8));
            long off=0; while(off<b.getSize()) { int n=(int)Math.min(buf.length,b.getSize()-off); currentProgram.getMemory().getBytes(b.getStart().add(off),buf,0,n); d.update(buf,0,n); off+=n; }
        }
        return HexFormat.of().formatHex(d.digest());
    }
    private Map<String,String> functionSnapshot() {
        Map<String,String> m=new TreeMap<>();
        for(Function f:currentProgram.getFunctionManager().getFunctions(true)) {
            StringBuilder b=new StringBuilder(f.getName()).append('|').append(f.getSymbol().getSource()).append('|');
            AddressRangeIterator it=f.getBody().getAddressRanges(); while(it.hasNext()){AddressRange r=it.next();b.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}
            m.put(canonical(f.getEntryPoint()),b.toString());
        }
        return m;
    }
    private Map<String,String> instructionSnapshot() throws Exception {
        Map<String,String> m=new TreeMap<>(); for(Instruction i:currentProgram.getListing().getInstructions(true)) m.put(canonical(i.getAddress()),bytes(i.getAddress(),i.getLength())); return m;
    }
    private Map<String,String> dataSnapshot() {
        Map<String,String> m=new TreeMap<>(); for(Data d:currentProgram.getListing().getDefinedData(true)) m.put(canonical(d.getAddress()),d.getLength()+":"+d.getDataType().getPathName()); return m;
    }
    private JsonArray incomingCalls() {
        JsonArray a=new JsonArray(); for(Reference r:currentProgram.getReferenceManager().getReferencesTo(at(START))) {
            JsonObject o=new JsonObject(); o.addProperty("from",canonical(r.getFromAddress())); o.addProperty("type",r.getReferenceType().toString()); o.addProperty("source",r.getSource().toString()); a.add(o);
        } return a;
    }
    private void checkBaseline(JsonObject manifest, JsonObject inventory) throws Exception {
        req(INVENTORY_COUNT==inventory.get("inventory_count").getAsInt() && INVENTORY_COUNT==manifest.get("inventory_count").getAsInt(),"baseline inventory/manifest count changed");
        req(LANGUAGE.equals(inventory.get("language").getAsString()) && LANGUAGE.equals(manifest.get("language").getAsString()),"baseline language mismatch");
        req(EXE_SHA.equals(inventory.get("executable_sha256").getAsString()) && EXE_SHA.equals(manifest.get("executable_sha256").getAsString()),"baseline executable identity mismatch");
        JsonArray fs=inventory.getAsJsonArray("functions"); req(fs.size()==INVENTORY_COUNT,"inventory function rows do not equal pinned count");
        Map<String,JsonObject> expected=new TreeMap<>(); for(JsonElement e:fs){JsonObject f=e.getAsJsonObject();expected.put(f.get("entry").getAsString(),f);}
        FunctionManager fm=currentProgram.getFunctionManager(); req(fm.getFunctionCount()==INVENTORY_COUNT,"live function count differs from final-3841 snapshot");
        Map<String,String> live=functionSnapshot(); req(live.size()==INVENTORY_COUNT && expected.size()==INVENTORY_COUNT,"function entry inventory cardinality mismatch");
        for(Map.Entry<String,JsonObject> e:expected.entrySet()) {
            String entry=e.getKey(); JsonObject row=e.getValue(); Function f=fm.getFunctionAt(at(Long.parseUnsignedLong(entry,16)));
            req(f!=null && f.getName().equals(row.get("name").getAsString()),"live function identity/name mismatch at "+entry);
            req(f.getBody().getNumAddresses()==row.get("size").getAsLong(),"live function body size differs from inventory at "+entry);
            AddressSet expectedBody=new AddressSet();
            for(JsonElement ie:row.getAsJsonArray("instructions")){JsonObject ir=ie.getAsJsonObject();Address ia=at(Long.parseUnsignedLong(ir.get("address").getAsString(),16));expectedBody.addRange(ia,ia.add(3));}
            req(f.getBody().equals(expectedBody),"live function body ranges differ from exact inventory instruction addresses at "+entry);
            req(live.containsKey(entry),"live function snapshot missing inventory entry "+entry);
            for(JsonElement ie:row.getAsJsonArray("instructions")) {
                JsonObject ins=ie.getAsJsonObject(); Address a=at(Long.parseUnsignedLong(ins.get("address").getAsString(),16)); Instruction decoded=currentProgram.getListing().getInstructionAt(a);
                req(decoded!=null && bytes(a,decoded.getLength()).equals(ins.get("bytes").getAsString()),"baseline instruction bytes mismatch at "+ins.get("address").getAsString());
            }
        }
    }
    private String flowKind(long w) {
        int op=(int)(w>>>26), rs=(int)((w>>>21)&31), rt=(int)((w>>>16)&31), fn=(int)(w&63);
        if(op==0 && fn==8 && w==0x03e00008L)return "return";
        if(op==0 && fn==8)return "computed_jump"; if(op==0 && fn==9)return "computed_call";
        if(op==2)return "jump"; if(op==3)return "call";
        if(op==1 && (rt==0||rt==1||rt==2||rt==3||rt==16||rt==17||rt==18||rt==19))return "conditional";
        if(op==4 && rs==0 && rt==0)return "unconditional_branch";
        if(op==4||op==5||op==6||op==7||op==20||op==21||op==22||op==23)return "conditional";
        if((op==16||op==17||op==18)&&rs==8)return "conditional";
        if((op==0&&(fn==12||fn==13))||(op==1&&(rt==8||rt==9||rt==10||rt==11||rt==12||rt==14)))return "unsupported_trap";
        return "linear";
    }
    private boolean isTransfer(String k) { return k.equals("conditional")||k.equals("unconditional_branch")||k.equals("call")||k.equals("jump")||k.equals("return"); }
    private JsonObject traverse(byte[] raw) {
        TreeMap<Long,Boolean> seen=new TreeMap<>(); ArrayDeque<Node> q=new ArrayDeque<>(); q.add(new Node(START,false)); JsonArray edges=new JsonArray();
        while(!q.isEmpty()) {
            Node n=q.remove(); req(n.pc>=START&&n.pc<END&&(n.pc&3)==0,"CFG successor leaves exact max interval: "+hex(n.pc));
            Boolean old=seen.get(n.pc); if(old!=null){req(old==n.delay,"word reached both as delay and ordinary instruction: "+hex(n.pc));continue;}
            long w=wordAt(raw,n.pc); String k=flowKind(w); seen.put(n.pc,n.delay);
            if(n.delay){req(k.equals("linear"),"control transfer in delay slot at "+hex(n.pc));continue;}
            long target=((n.pc+4)&0xf0000000L)|((w&0x03ffffffL)<<2), fall=n.pc+8;
            if(k.equals("linear")){q.add(new Node(n.pc+4,false));continue;}
            if(k.equals("conditional")){target=branchTarget(n.pc,w); q.add(new Node(n.pc+4,true));q.add(new Node(target,false));q.add(new Node(fall,false));}
            else if(k.equals("unconditional_branch")){target=branchTarget(n.pc,w);q.add(new Node(n.pc+4,true));q.add(new Node(target,false));}
            else if(k.equals("call")){q.add(new Node(n.pc+4,true));q.add(new Node(fall,false));}
            else if(k.equals("jump")){q.add(new Node(n.pc+4,true));q.add(new Node(target,false));}
            else if(k.equals("return")){q.add(new Node(n.pc+4,true));}
            else throw new IllegalStateException("unsupported computed/non-local transfer at "+hex(n.pc)+" kind="+k);
            JsonObject e=new JsonObject();e.addProperty("site",hex(n.pc));e.addProperty("kind",k);if(k.equals("conditional")||k.equals("unconditional_branch")||k.equals("jump")||k.equals("call"))e.addProperty("target",hex(target));if(k.equals("conditional")||k.equals("call")||k.equals("computed_call"))e.addProperty("fallthrough",hex(fall));edges.add(e);
        }
        req(seen.size()==51,"reachable CFG count differs from pinned 51-word hypothesis: "+seen.size());
        for(long pc=START;pc<=0x00200dd8L;pc+=4)req(seen.containsKey(pc),"CFG has an unreachable hole before terminal delay slot at "+hex(pc));
        req(!seen.containsKey(0x00200ddcL)&&wordAt(raw,0x00200ddcL)==0,"trailing zero word is not left unowned");
        JsonObject out=new JsonObject();out.addProperty("instruction_count_including_delay_slots",seen.size());out.addProperty("body_end_inclusive",hex(seen.lastKey()));out.add("edges",edges);out.addProperty("zero_suffix_left_unowned",hex(0x00200ddcL));return out;
    }
    private void checkDecoderFlow(JsonObject cfg) {
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject edge=e.getAsJsonObject(); long pc=Long.parseUnsignedLong(edge.get("site").getAsString(),16); Instruction ins=currentProgram.getListing().getInstructionAt(at(pc));
            req(ins!=null,"raw CFG transfer has no decoded instruction at "+hex(pc)); FlowType actual=ins.getFlowType(); String kind=edge.get("kind").getAsString();
            Address[] targets=ins.getFlows();
            if(kind.equals("conditional")) {
                req(actual.isJump()&&actual.isConditional()&&targets.length==1,"Ghidra does not classify raw conditional branch consistently at "+hex(pc));
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra conditional target differs from raw-word target at "+hex(pc));
                req(ins.getFallThrough()!=null&&ins.getFallThrough().getOffset()==Long.parseUnsignedLong(edge.get("fallthrough").getAsString(),16),"Ghidra conditional fallthrough/delay-slot address differs at "+hex(pc));
            } else if(kind.equals("unconditional_branch")||kind.equals("jump")) {
                req(actual.isJump()&&!actual.isConditional()&&!actual.isComputed()&&targets.length==1,"Ghidra does not classify raw direct jump consistently at "+hex(pc));
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra direct-jump target differs from raw-word target at "+hex(pc));
            } else if(kind.equals("call")) {
                req(actual.isCall()&&!actual.isComputed()&&targets.length==1,"Ghidra does not classify raw direct call consistently at "+hex(pc));
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra direct-call target differs from raw-word target at "+hex(pc));
                req(ins.getFallThrough()!=null&&ins.getFallThrough().getOffset()==Long.parseUnsignedLong(edge.get("fallthrough").getAsString(),16),"Ghidra direct-call fallthrough/delay-slot address differs at "+hex(pc));
            } else if(kind.equals("return")) {
                req(actual.isTerminal()&&ins.getMnemonicString().toLowerCase(Locale.ROOT).startsWith("jr"),"Ghidra return classification differs from exact JR RA word at "+hex(pc));
            }
        }
    }
    private AddressSet decodeAndCreate(byte[] elf, byte[] raw, JsonObject cfg, Map<String,String> beforeInstructions, Map<String,String> beforeData, String beforeMemory, Map<String,String> beforeFunctions, JsonArray calls) throws Exception {
        Address start=at(START), lastInstruction=at(0x00200dd8L), bodyEnd=lastInstruction.add(3); FunctionManager fm=currentProgram.getFunctionManager();
        req(fm.getFunctionAt(start)==null&&fm.getFunctionContaining(start)==null,"candidate entry already belongs to a function");
        for(long pc=START;pc<END;pc+=4){Address a=at(pc);req(currentProgram.getListing().getInstructionAt(a)==null&&currentProgram.getListing().getInstructionContaining(a)==null,"candidate maximum span overlaps decoded instruction at "+hex(pc));req(currentProgram.getListing().getDefinedDataContaining(a)==null,"candidate maximum span overlaps defined data at "+hex(pc));req(fm.getFunctionContaining(a)==null,"candidate span overlaps saved function at "+hex(pc));}
        Set<String> sites=new TreeSet<>(); for(JsonElement e:calls){JsonObject r=e.getAsJsonObject();req("UNCONDITIONAL_CALL".equals(r.get("type").getAsString()),"incoming reference is not an unconditional call");sites.add(r.get("from").getAsString());}
        req(sites.equals(new TreeSet<>(Arrays.asList("001fc018","001fc18c","001fc1fc"))),"saved incoming direct-call sites differ from pinned exact three");
        for(String site:sites){long pc=Long.parseUnsignedLong(site,16);byte[] loaded=new byte[4];currentProgram.getMemory().getBytes(at(pc),loaded);long fileOffset=TEXT_FILE+pc-TEXT_VA;byte[] fileBytes=Arrays.copyOfRange(elf,Math.toIntExact(fileOffset),Math.toIntExact(fileOffset+4));req(Arrays.equals(loaded,fileBytes),"loaded incoming JAL bytes differ from pinned ELF at "+site);long w=word(fileBytes,0);long target=((pc+4)&0xf0000000L)|((w&0x03ffffffL)<<2);req((w>>>26)==3&&target==START,"saved incoming call does not decode to candidate from raw ELF bytes at "+site);Function owner=fm.getFunctionContaining(at(pc));String expectedOwner=site.equals("001fc018")?"candidate_ee_001fbfb8":"candidate_ee_001fc118";req(owner!=null&&owner.getName().equals(expectedOwner)&&owner.getSymbol().getSource()==SourceType.ANALYSIS,"incoming callsite is not owned by its pinned provisional candidate: "+site);}
        AddressSet expected=new AddressSet(start,bodyEnd); int tx=currentProgram.startTransaction("guarded single EE candidate "+ENTRY); boolean commit=false;
        try {
            for(long pc=START;pc<=lastInstruction.getOffset();pc+=4){monitor.checkCancelled();Address a=at(pc);Instruction i=currentProgram.getListing().getInstructionAt(a);
                if(i==null){DisassembleCommand dc=new DisassembleCommand(new AddressSet(a),new AddressSet(a,a.add(3)),false);dc.enableCodeAnalysis(false);req(dc.applyTo(currentProgram,monitor),"single-word disassembly failed at "+hex(pc)+": "+dc.getStatusMsg());i=currentProgram.getListing().getInstructionAt(a);}
                else req(pc>START&&isTransfer(flowKind(wordAt(raw,pc-4))),"instruction unexpectedly existed outside a preceding transfer delay slot at "+hex(pc));
                long fileOffset=TEXT_FILE+pc-TEXT_VA;byte[] fileBytes=Arrays.copyOfRange(elf,Math.toIntExact(fileOffset),Math.toIntExact(fileOffset+4));req(i!=null&&i.getLength()==4&&bytes(a,4).equals(HexFormat.of().formatHex(fileBytes))&&Arrays.equals(fileBytes,Arrays.copyOfRange(raw,Math.toIntExact(pc-START),Math.toIntExact(pc-START+4))),"decoded/raw ELF bytes mismatch at "+hex(pc));}
            checkDecoderFlow(cfg);
            AddressSetView body=CreateFunctionCmd.getFunctionBody(currentProgram,start,monitor);req(body.equals(expected),"Ghidra-computed body differs from raw CFG contiguous body: actual="+rangeSummary(body)+" expected="+rangeSummary(expected));
            AddressSet decodedBody=new AddressSet();for(Instruction i:currentProgram.getListing().getInstructions(body,true))decodedBody.addRange(i.getAddress(),i.getMaxAddress());req(decodedBody.equals(expected),"decoded instruction set differs from raw CFG body");
            CreateFunctionCmd create=new CreateFunctionCmd("candidate_ee_"+ENTRY,start,body,SourceType.ANALYSIS);req(create.applyTo(currentProgram,monitor),"CreateFunctionCmd failed: "+create.getStatusMsg());Function made=fm.getFunctionAt(start);req(made!=null,"CreateFunctionCmd returned no function");req(made.getName().equals("candidate_ee_"+ENTRY)&&made.getSymbol().getSource()==SourceType.ANALYSIS,"created candidate identity/source type differs from provisional request");req(made.getBody().equals(expected),"created body differs from raw CFG body");
            Map<String,String> now=instructionSnapshot();for(String a:beforeInstructions.keySet())req(Objects.equals(now.get(a),beforeInstructions.get(a)),"old instruction bytes changed at "+a);
            for(String a:now.keySet())if(!beforeInstructions.containsKey(a))req(expected.contains(at(Long.parseUnsignedLong(a,16))),"listing delta escaped candidate body at "+a);
            req(dataSnapshot().equals(beforeData),"defined data changed");req(memoryHash().equals(beforeMemory),"initialized memory changed");
            Map<String,String> fnow=functionSnapshot();for(Map.Entry<String,String> e:beforeFunctions.entrySet())req(Objects.equals(fnow.get(e.getKey()),e.getValue()),"old function name/source/body changed at "+e.getKey());
            req(fm.getFunctionCount()==INVENTORY_COUNT+1,"function count did not increase by exactly one");commit=true;
        } finally { currentProgram.endTransaction(tx,commit); }
        Function persisted=fm.getFunctionAt(start);req(persisted!=null&&persisted.getName().equals("candidate_ee_"+ENTRY)&&persisted.getSymbol().getSource()==SourceType.ANALYSIS&&persisted.getBody().equals(expected),"candidate absent or altered after transaction commit");return expected;
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();req(args.length==4,"Expected outputJson, rawElf, finalManifest, finalInventory");
        Path output=Paths.get(args[0]).toAbsolutePath(), exe=Paths.get(args[1]).toAbsolutePath(), mp=Paths.get(args[2]).toAbsolutePath(), ip=Paths.get(args[3]).toAbsolutePath();
        req(!Files.exists(output),"output already exists; refusing overwrite"); byte[] elf=Files.readAllBytes(exe), mb=Files.readAllBytes(mp), ib=Files.readAllBytes(ip);
        JsonObject out=new JsonObject();out.addProperty("schema_version",1);out.addProperty("entry",ENTRY);out.addProperty("executable_sha256",sha(elf));out.addProperty("baseline_manifest_sha256",sha(mb));out.addProperty("baseline_inventory_sha256",sha(ib));out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("ghidra_version",getGhidraVersion());
        try {
            req(EXE_SHA.equals(sha(elf))&&EXE_SHA.equals(currentProgram.getExecutableSHA256()),"pinned executable identity mismatch");req(MANIFEST_SHA.equals(sha(mb)),"final-3841 manifest hash mismatch");req(INVENTORY_SHA.equals(sha(ib)),"final-3841 inventory hash mismatch");req(LANGUAGE.equals(currentProgram.getLanguageID().toString()),"program is not R5900 little-endian");
            JsonObject manifest=JsonParser.parseString(new String(mb,StandardCharsets.UTF_8)).getAsJsonObject(), inventory=JsonParser.parseString(new String(ib,StandardCharsets.UTF_8)).getAsJsonObject();
            MemoryBlock text=currentProgram.getMemory().getBlock(at(TEXT_VA));req(text!=null&&text.getName().equals(".text")&&text.isInitialized()&&text.isExecute()&&text.getStart().getOffset()==TEXT_VA&&text.getSize()==TEXT_SIZE,"loaded .text block differs from exact ELF map");
            long file=TEXT_FILE+START-TEXT_VA;byte[] raw=Arrays.copyOfRange(elf,Math.toIntExact(file),Math.toIntExact(file+END-START));req(raw.length==END-START&&sha(raw).equals(WINDOW_SHA),"candidate 208-byte window hash mismatch");req(bytes(at(START),raw.length).equals(HexFormat.of().formatHex(raw)),"loaded program bytes differ from ELF candidate span");
            checkBaseline(manifest,inventory);Map<String,String> functions=functionSnapshot(),instructions=instructionSnapshot(),data=dataSnapshot();String memory=memoryHash();JsonArray refs=incomingCalls();JsonObject cfg=traverse(raw);
            AddressSet body=decodeAndCreate(elf,raw,cfg,instructions,data,memory,functions,refs);
            out.addProperty("status","created_single_bounded_candidate");out.add("cfg",cfg);out.add("incoming_references",refs);out.addProperty("body_bytes",body.getNumAddresses());out.addProperty("function_count_after",currentProgram.getFunctionManager().getFunctionCount());out.addProperty("old_function_snapshot_preserved",true);out.addProperty("initialized_memory_preserved",true);out.addProperty("defined_data_preserved",true);out.addProperty("scope","Static provisional candidate only. No original function identity, semantics, runtime reachability, or whole-game completeness is established.");
        } catch(Exception e) { out.addProperty("status","rejected_or_failed");out.addProperty("failure",e.getClass().getSimpleName()+": "+String.valueOf(e.getMessage()));write(output,out);throw e; }
        write(output,out);println("EE_CLOSURE_CANDIDATE_OK entry="+ENTRY+" body_bytes=204 function_count_delta=1");
    }
    private void write(Path p,JsonObject o)throws Exception{Files.createDirectories(p.getParent());Files.writeString(p,new GsonBuilder().setPrettyPrinting().create().toJson(o)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);}
}
