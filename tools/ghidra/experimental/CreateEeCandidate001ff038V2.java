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
 * Experimental single-seed 001ff038 candidate guard. Do not run until the parent has
 * reviewed this source and the exact baseline project copy. This adds no source
 * identity claim; it checks one raw-word CFG hypothesis and rolls back on drift.
 */
public class CreateEeCandidate001ff038V2 extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String MANIFEST_SHA = "1e3f425e7c1a653183a284a240b28f6ff2b2918250b1e1882b0dade4cf9c4ef4";
    private static final String INVENTORY_SHA = "b23698a1e4e6bfb61f7d4ca9932b80971f1eb4527f57bb5219d14196586c4a9d";
    private static final String COVERAGE_SHA = "2ff0ed89839dc6e4e26f7c8b93f1df7ee111f3c1205385e8c52f2640f13df1f0";
    private static final String WINDOW_SHA = "16d48e8843225c3e399cb0b062641b0199c6870d685c79badaf65c4c3cf8c3a1";
    private static final String ENTRY = "001ff038";
    private static final long START = 0x001ff038L, END = 0x001ff140L, MAX_END = 0x001ff140L;
    private static final long TEXT_VA = 0x00100000L, TEXT_FILE = 0x1000L, TEXT_SIZE = 0x00117bd4L;
    private static final int INVENTORY_COUNT = 3844;
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
        Map<String,String> m=new TreeMap<>(); for(Instruction i:currentProgram.getListing().getInstructions(true)) m.put(canonical(i.getAddress()),i.toString()+"|"+bytes(i.getAddress(),i.getLength())); return m;
    }
    private Map<String,String> dataSnapshot() {
        Map<String,String> m=new TreeMap<>(); for(Data d:currentProgram.getListing().getDefinedData(true)) m.put(canonical(d.getAddress()),d.getLength()+":"+d.getDataType().getPathName()); return m;
    }
    private JsonArray incomingCalls() {
        JsonArray a=new JsonArray(); ReferenceManager rm=currentProgram.getReferenceManager();
        for(long target=START;target<MAX_END;target++) for(Reference r:rm.getReferencesTo(at(target))) {
            JsonObject o=new JsonObject(); o.addProperty("to",hex(target)); o.addProperty("from",canonical(r.getFromAddress())); o.addProperty("type",r.getReferenceType().toString()); o.addProperty("source",r.getSource().toString()); a.add(o);
        }
        return a;
    }
    private void checkCoverage(JsonObject coverage) {
        req(EXE_SHA.equals(coverage.get("executable_sha256").getAsString()),"coverage executable identity mismatch");
        JsonObject block=null; for(JsonElement e:coverage.getAsJsonArray("blocks")){JsonObject b=e.getAsJsonObject();if(".text".equals(b.get("name").getAsString()))block=b;}
        req(block!=null,"coverage has no .text block");
        Set<Long> undefined=new HashSet<>();for(JsonElement e:block.getAsJsonArray("undefined_ranges")){JsonObject r=e.getAsJsonObject();long a=Long.parseUnsignedLong(r.get("start").getAsString(),16),b=Long.parseUnsignedLong(r.get("end").getAsString(),16);for(long x=a;x<=b;x++)undefined.add(x);}
        for(long pc=START;pc<END;pc++)req(undefined.contains(pc),"baseline coverage does not classify candidate byte as undefined at "+hex(pc));
    }
    private void checkBaseline(JsonObject manifest, JsonObject inventory) throws Exception {
        req(INVENTORY_COUNT==inventory.get("inventory_count").getAsInt() && INVENTORY_COUNT==manifest.get("inventory_count").getAsInt(),"baseline inventory/manifest count changed");
        req(LANGUAGE.equals(inventory.get("language").getAsString()) && LANGUAGE.equals(manifest.get("language").getAsString()),"baseline language mismatch");
        req(EXE_SHA.equals(inventory.get("executable_sha256").getAsString()) && EXE_SHA.equals(manifest.get("executable_sha256").getAsString()),"baseline executable identity mismatch");
        JsonArray fs=inventory.getAsJsonArray("functions"); req(fs.size()==INVENTORY_COUNT,"inventory function rows do not equal pinned count");
        Map<String,JsonObject> expected=new TreeMap<>(); for(JsonElement e:fs){JsonObject f=e.getAsJsonObject();expected.put(f.get("entry").getAsString(),f);}
        FunctionManager fm=currentProgram.getFunctionManager(); req(fm.getFunctionCount()==INVENTORY_COUNT,"live function count differs from final-3844 snapshot");
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
                req(decoded.toString().equals(ins.get("text").getAsString()),"baseline instruction text mismatch at "+ins.get("address").getAsString());
            }
        }
    }
    private String flowKind(long w) {
        int op=(int)(w>>>26), rs=(int)((w>>>21)&31), rt=(int)((w>>>16)&31), fn=(int)(w&63);
        if(op==0 && fn==8 && w==0x03e00008L)return "return";
        if(op==0 && fn==8)return "computed_jump"; if(op==0 && fn==9)return "computed_call";
        if(op==0 && (fn==12||fn==13||fn==48||fn==49||fn==50||fn==51||fn==52||fn==54))return "unsupported_trap";
        if(op==0 && (fn==32||fn==34||fn==44||fn==46))return "unsupported_trap";
        if(op==8||op==24)return "unsupported_trap"; // ADDI and DADDI may take overflow exceptions.
        if(op==2)return "jump"; if(op==3)return "call";
        if(op==1) {
            if(rt==8||rt==9||rt==10||rt==11||rt==12||rt==14)return "unsupported_trap";
            if(rt==0||rt==1||rt==2||rt==3||rt==16||rt==17||rt==18||rt==19)return (rt==2||rt==3||rt==18||rt==19)?"conditional_likely":"conditional";
            return "unsupported_encoding";
        }
        if(op==4 && rs==0 && rt==0)return "unconditional_branch";
        if(op==4||op==5)return "conditional";
        if((op==6||op==7||op==22||op==23)&&rt!=0)return "unsupported_encoding";
        if(op==6||op==7)return "conditional";
        if(op==20||op==21||op==22||op==23)return "conditional_likely";
        if((op==16||op==17||op==18||op==19)&&rs==8)return ((rt&2)!=0)?"conditional_likely":"conditional";
        return "linear";
    }
    private boolean isTransfer(String k) { return k.equals("conditional")||k.equals("conditional_likely")||k.equals("unconditional_branch")||k.equals("call")||k.equals("jump")||k.equals("return"); }
    private JsonObject traverse(byte[] raw) {
        TreeMap<Long,Boolean> seen=new TreeMap<>(); ArrayDeque<Node> q=new ArrayDeque<>(); q.add(new Node(START,false)); JsonArray edges=new JsonArray();
        while(!q.isEmpty()) {
            Node n=q.remove(); req(n.pc>=START&&n.pc<END&&(n.pc&3)==0,"CFG successor leaves exact max interval: "+hex(n.pc));
            Boolean old=seen.get(n.pc); if(old!=null){req(old==n.delay,"word reached both as delay and ordinary instruction: "+hex(n.pc));continue;}
            long w=wordAt(raw,n.pc); String k=flowKind(w); seen.put(n.pc,n.delay);
            if(n.delay){req(k.equals("linear"),"control transfer in delay slot at "+hex(n.pc));continue;}
            long target=((n.pc+4)&0xf0000000L)|((w&0x03ffffffL)<<2), fall=n.pc+8;
            if(k.equals("linear")){q.add(new Node(n.pc+4,false));continue;}
            if(k.equals("computed_call")||k.equals("computed_jump")||k.equals("unsupported_trap"))throw new IllegalStateException("unsupported computed/trap transfer at "+hex(n.pc)+" kind="+k);
            if(k.equals("conditional")||k.equals("conditional_likely")){target=branchTarget(n.pc,w);q.add(new Node(n.pc+4,true));q.add(new Node(target,false));q.add(new Node(fall,false));}
            else if(k.equals("unconditional_branch")){target=branchTarget(n.pc,w);q.add(new Node(n.pc+4,true));q.add(new Node(target,false));}
            else if(k.equals("call")){q.add(new Node(n.pc+4,true));q.add(new Node(fall,false));}
            else if(k.equals("jump")){q.add(new Node(n.pc+4,true));q.add(new Node(target,false));}
            else if(k.equals("return")){q.add(new Node(n.pc+4,true));}
            else throw new IllegalStateException("unhandled flow class at "+hex(n.pc)+" kind="+k);
            JsonObject e=new JsonObject();e.addProperty("site",hex(n.pc));e.addProperty("kind",k);
            if(k.equals("conditional")||k.equals("conditional_likely")||k.equals("unconditional_branch")||k.equals("jump")||k.equals("call"))e.addProperty("target",hex(target));
            if(k.equals("conditional")||k.equals("conditional_likely")||k.equals("call"))e.addProperty("fallthrough",hex(fall));
            if(k.equals("conditional_likely"))e.addProperty("not_taken_annuls_delay_slot",true);edges.add(e);
        }
        req(seen.size()==(END-START)/4,"reachable CFG does not cover every instruction word in the exact interval: "+seen.size());
        for(long pc=START;pc<END;pc+=4)req(seen.containsKey(pc),"CFG has an unreachable word inside exact candidate interval at "+hex(pc));
        JsonArray addresses=new JsonArray();for(long pc:seen.keySet())addresses.add(hex(pc));
        JsonObject out=new JsonObject();out.addProperty("instruction_count_including_delay_slots",seen.size());out.addProperty("body_end_inclusive",hex(seen.lastKey()));out.add("instruction_addresses",addresses);out.add("edges",edges);out.addProperty("branch_likely_scope","For conditional-likely branches, the static union includes the delay instruction on the taken path and the pc+8 successor on the not-taken path; the not-taken path annuls the delay instruction. This is a structural reachability union, not path-by-path execution.");return out;
    }
    private void checkCandidateFlowProfile(JsonObject cfg, byte[] raw) {
        Map<String,String> expectedCalls=new TreeMap<>();
        expectedCalls.put("001ff08c","001ff270"); expectedCalls.put("001ff0a8","001ffd70");
        expectedCalls.put("001ff0b0","001feb80"); expectedCalls.put("001ff0fc","001fdb88");
        expectedCalls.put("001ff114","001fc4e0");
        Map<String,String> actualCalls=new TreeMap<>(); int likely=0;
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject edge=e.getAsJsonObject(); String kind=edge.get("kind").getAsString();
            if(kind.equals("call"))actualCalls.put(edge.get("site").getAsString(),edge.get("target").getAsString());
            if(kind.equals("conditional_likely"))likely++;
        }
        req(actualCalls.equals(expectedCalls),"five outgoing JAL sites/targets differ from the pinned raw profile");
        req(likely==0,"unexpected branch-likely site; re-review taken-delay/not-taken-annul semantics");
        req(wordAt(raw,0x001ff084L)==0&&wordAt(raw,0x001ff0a4L)==0&&wordAt(raw,0x001ff0dcL)==0&&wordAt(raw,0x001ff0e0L)==0&&wordAt(raw,0x001ff0e8L)==0,"one of the five reachable zero words differs from pinned NOP bytes");
    }
    private Set<String> functionSet(Set<Function> functions) {
        Set<String> out=new TreeSet<>(); for(Function f:functions)out.add(canonical(f.getEntryPoint())); return out;
    }
    private Map<String,Set<String>> calledGraph() throws Exception {
        Map<String,Set<String>> out=new TreeMap<>(); for(Function f:currentProgram.getFunctionManager().getFunctions(true))out.put(canonical(f.getEntryPoint()),functionSet(f.getCalledFunctions(monitor))); return out;
    }
    private Map<String,Set<String>> callerGraph() throws Exception {
        Map<String,Set<String>> out=new TreeMap<>(); for(Function f:currentProgram.getFunctionManager().getFunctions(true))out.put(canonical(f.getEntryPoint()),functionSet(f.getCallingFunctions(monitor))); return out;
    }
    private Set<String> referenceSnapshot() {
        Set<String> out=new TreeSet<>();
        for(Instruction i:currentProgram.getListing().getInstructions(true))for(Reference r:i.getReferencesFrom())out.add(referenceKey(r));
        for(Data d:currentProgram.getListing().getDefinedData(true))for(Reference r:d.getReferencesFrom())out.add(referenceKey(r));
        return out;
    }
    private String referenceKey(Reference r) { return canonical(r.getFromAddress())+"|"+canonical(r.getToAddress())+"|"+r.getReferenceType()+"|"+r.getSource(); }
    private Set<String> expectedNewFlowReferences(JsonObject cfg) {
        Set<String> out=new TreeSet<>();
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject x=e.getAsJsonObject(); String k=x.get("kind").getAsString(); if(k.equals("return"))continue;
            String type=(k.equals("call"))?"UNCONDITIONAL_CALL":(k.equals("unconditional_branch")||k.equals("jump"))?"UNCONDITIONAL_JUMP":"CONDITIONAL_JUMP";
            out.add(x.get("site").getAsString()+"|"+x.get("target").getAsString()+"|"+type+"|DEFAULT");
        }
        return out;
    }
    private void checkReferenceAndCallGraphDeltas(Set<String> beforeRefs, Map<String,Set<String>> beforeCalled, Map<String,Set<String>> beforeCallers, JsonObject cfg) throws Exception {
        Set<String> afterRefs=referenceSnapshot(); Set<String> additions=new TreeSet<>(afterRefs); additions.removeAll(beforeRefs);
        req(additions.equals(expectedNewFlowReferences(cfg)),"new reference set differs from the exact raw CFG flow edges: "+additions);
        for(String ref:beforeRefs)req(afterRefs.contains(ref),"old global reference removed or changed: "+ref);
        Map<String,Set<String>> afterCalled=calledGraph(), afterCallers=callerGraph(); String entry=ENTRY, owner="00200d10";
        Set<String> expectedKnownCallees=new TreeSet<>(Arrays.asList("001ffd70","001fc4e0"));
        req(afterCalled.get(entry).equals(expectedKnownCallees),"candidate reciprocal callee graph differs from the two preexisting function targets");
        req(afterCallers.get(entry).equals(new TreeSet<>(Arrays.asList(owner))),"candidate caller graph differs from sole existing provisional caller");
        for(String old:beforeCalled.keySet()) {
            Set<String> expectedCallees=new TreeSet<>(beforeCalled.get(old));
            if(old.equals(owner))expectedCallees.add(entry);
            req(Objects.equals(expectedCallees,afterCalled.get(old)),"existing caller's callee graph changed unexpectedly at "+old);
            Set<String> expectedCallers=new TreeSet<>(beforeCallers.get(old));
            if(expectedKnownCallees.contains(old))expectedCallers.add(entry);
            req(Objects.equals(expectedCallers,afterCallers.get(old)),"existing callee's caller graph changed unexpectedly at "+old);
        }
        for(String unresolved:Arrays.asList("001ff270","001feb80","001fdb88")) {
            Address u=at(Long.parseUnsignedLong(unresolved,16));
            req(currentProgram.getFunctionManager().getFunctionAt(u)==null&&currentProgram.getFunctionManager().getFunctionContaining(u)==null,"unresolved outgoing callee was created/claimed at "+unresolved);
            req(currentProgram.getListing().getInstructionAt(u)==null&&currentProgram.getListing().getDefinedDataContaining(u)==null,"unresolved outgoing callee bytes were decoded/typed at "+unresolved);
        }
    }
    private void checkDecoderFlow(JsonObject cfg) {
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject edge=e.getAsJsonObject(); long pc=Long.parseUnsignedLong(edge.get("site").getAsString(),16); Instruction ins=currentProgram.getListing().getInstructionAt(at(pc));
            req(ins!=null,"raw CFG transfer has no decoded instruction at "+hex(pc)); FlowType actual=ins.getFlowType(); String kind=edge.get("kind").getAsString();
            Address[] targets=ins.getFlows();
            if(kind.equals("conditional")||kind.equals("conditional_likely")) {
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
    private AddressSet decodeAndCreate(byte[] elf, byte[] raw, JsonObject cfg, Map<String,String> beforeInstructions, Map<String,String> beforeData, String beforeMemory, Map<String,String> beforeFunctions, Set<String> beforeRefs, Map<String,Set<String>> beforeCalled, Map<String,Set<String>> beforeCallers, JsonArray calls) throws Exception {
        Address start=at(START), lastInstruction=at(Long.parseUnsignedLong(cfg.get("body_end_inclusive").getAsString(),16)); FunctionManager fm=currentProgram.getFunctionManager();
        req(lastInstruction.getOffset()==END-4,"raw CFG body end differs from exact 66-word / 264-byte body boundary");
        req(fm.getFunctionAt(start)==null&&fm.getFunctionContaining(start)==null,"candidate entry already belongs to a function");
        req(currentProgram.getListing().getInstructionAt(at(END))==null&&currentProgram.getListing().getDefinedDataContaining(at(END))==null&&fm.getFunctionContaining(at(END))==null,"next word at 001ff140 is already listed or owned");
        for(long pc=START;pc<END;pc+=4){Address a=at(pc);req(currentProgram.getListing().getInstructionAt(a)==null&&currentProgram.getListing().getInstructionContaining(a)==null,"candidate maximum span overlaps decoded instruction at "+hex(pc));req(currentProgram.getListing().getDefinedDataContaining(a)==null,"candidate maximum span overlaps defined data at "+hex(pc));req(fm.getFunctionContaining(a)==null,"candidate span overlaps saved function at "+hex(pc));}
        Set<String> sites=new TreeSet<>(); for(JsonElement e:calls){JsonObject r=e.getAsJsonObject();req("UNCONDITIONAL_CALL".equals(r.get("type").getAsString()),"reference into candidate interval is not an unconditional call");req(ENTRY.equals(r.get("to").getAsString()),"reference targets an interior candidate address");sites.add(r.get("from").getAsString());}
        req(calls.size()==1&&sites.equals(new TreeSet<>(Arrays.asList("00200dac"))),"complete references-to-every-byte scan differs from exactly one entry call");
        for(String site:sites){
            long pc=Long.parseUnsignedLong(site,16); byte[] loaded=new byte[4]; currentProgram.getMemory().getBytes(at(pc),loaded);
            long fileOffset=TEXT_FILE+pc-TEXT_VA; byte[] fileBytes=Arrays.copyOfRange(elf,Math.toIntExact(fileOffset),Math.toIntExact(fileOffset+4));
            req(Arrays.equals(loaded,fileBytes),"loaded incoming JAL bytes differ from pinned ELF at "+site);
            long w=word(fileBytes,0), target=((pc+4)&0xf0000000L)|((w&0x03ffffffL)<<2);
            req((w>>>26)==3&&target==START,"saved incoming call does not decode to candidate from raw ELF bytes at "+site);
            Function owner=fm.getFunctionContaining(at(pc));
            req(owner!=null&&owner.getEntryPoint().getOffset()==0x00200d10L&&owner.getName().equals("candidate_ee_00200d10")&&owner.getSymbol().getSource()==SourceType.ANALYSIS,"incoming callsite is not owned by pinned ANALYSIS candidate 00200d10");
            Instruction call=currentProgram.getListing().getInstructionAt(at(pc));
            req(call!=null&&call.getFlowType().isCall()&&call.getFlows().length==1&&call.getFlows()[0].getOffset()==START,"live incoming call instruction flow differs from the raw JAL");
            boolean found=false; for(Reference r:currentProgram.getReferenceManager().getReferencesTo(start)) if(r.getFromAddress().equals(at(pc))&&r.getReferenceType().toString().equals("UNCONDITIONAL_CALL")&&r.getSource()==SourceType.DEFAULT)found=true;
            req(found,"incoming JAL reference lacks exact DEFAULT disassembler-flow provenance");
        }
        AddressSet expected=new AddressSet(); for(JsonElement a:cfg.getAsJsonArray("instruction_addresses")){Address ia=at(Long.parseUnsignedLong(a.getAsString(),16));expected.addRange(ia,ia.add(3));} req(expected.getNumAddresses()==264,"CFG body instruction ranges do not cover exactly 66 words / 264 body bytes"); int tx=currentProgram.startTransaction("guarded single EE candidate "+ENTRY); boolean commit=false;
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
            req(fm.getFunctionCount()==INVENTORY_COUNT+1,"function count did not increase by exactly one");req(fm.getFunctionContaining(at(END))==null&&currentProgram.getListing().getInstructionAt(at(END))==null&&currentProgram.getListing().getDefinedDataContaining(at(END))==null,"next word at 001ff140 entered a function or listing");checkReferenceAndCallGraphDeltas(beforeRefs,beforeCalled,beforeCallers,cfg);commit=true;
        } finally { currentProgram.endTransaction(tx,commit); }
        Function persisted=fm.getFunctionAt(start);req(persisted!=null&&persisted.getName().equals("candidate_ee_"+ENTRY)&&persisted.getSymbol().getSource()==SourceType.ANALYSIS&&persisted.getBody().equals(expected),"candidate absent or altered after transaction commit");return expected;
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();req(args.length==5,"Expected outputJson, rawElf, finalManifest, finalInventory, finalCoverage");
        Path output=Paths.get(args[0]).toAbsolutePath(), exe=Paths.get(args[1]).toAbsolutePath(), mp=Paths.get(args[2]).toAbsolutePath(), ip=Paths.get(args[3]).toAbsolutePath(), cp=Paths.get(args[4]).toAbsolutePath();
        req(!Files.exists(output),"output already exists; refusing overwrite"); byte[] elf=Files.readAllBytes(exe), mb=Files.readAllBytes(mp), ib=Files.readAllBytes(ip), cb=Files.readAllBytes(cp);
        JsonObject out=new JsonObject();out.addProperty("schema_version",1);out.addProperty("entry",ENTRY);out.addProperty("executable_sha256",sha(elf));out.addProperty("baseline_manifest_sha256",sha(mb));out.addProperty("baseline_inventory_sha256",sha(ib));out.addProperty("baseline_coverage_sha256",sha(cb));out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("ghidra_version",getGhidraVersion());
        try {
            req(EXE_SHA.equals(sha(elf))&&EXE_SHA.equals(currentProgram.getExecutableSHA256()),"pinned executable identity mismatch");req(MANIFEST_SHA.equals(sha(mb)),"final-3844 manifest hash mismatch");req(INVENTORY_SHA.equals(sha(ib)),"final-3844 inventory hash mismatch");req(COVERAGE_SHA.equals(sha(cb)),"final-3844 coverage hash mismatch");req(LANGUAGE.equals(currentProgram.getLanguageID().toString()),"program is not R5900 little-endian");
            JsonObject manifest=JsonParser.parseString(new String(mb,StandardCharsets.UTF_8)).getAsJsonObject(), inventory=JsonParser.parseString(new String(ib,StandardCharsets.UTF_8)).getAsJsonObject(), coverage=JsonParser.parseString(new String(cb,StandardCharsets.UTF_8)).getAsJsonObject();
            MemoryBlock text=currentProgram.getMemory().getBlock(at(TEXT_VA));req(text!=null&&text.getName().equals(".text")&&text.isInitialized()&&text.isExecute()&&text.getStart().getOffset()==TEXT_VA&&text.getSize()==TEXT_SIZE,"loaded .text block differs from exact ELF map");
            long file=TEXT_FILE+START-TEXT_VA;byte[] raw=Arrays.copyOfRange(elf,Math.toIntExact(file),Math.toIntExact(file+END-START));
            req(raw.length==264&&sha(raw).equals(WINDOW_SHA),"candidate [001ff038,001ff140) SHA/length mismatch");
            req(word(raw,0)==0x27bdffa0L&&word(raw,raw.length-4)==0x27bd0060L&&word(raw,raw.length-8)==0x03e00008L,"candidate initial/terminal/delay words differ from exact pins");
            req(bytes(at(START),raw.length).equals(HexFormat.of().formatHex(raw)),"loaded program bytes differ from exact ELF candidate span");
            long nextFile=file+(END-START);byte[] next=Arrays.copyOfRange(elf,Math.toIntExact(nextFile),Math.toIntExact(nextFile+4));
            req(word(next,0)==0x27bdff90L&&bytes(at(END),4).equals(HexFormat.of().formatHex(next)),"pinned next word at 001ff140 differs or is unavailable; it remains outside the candidate span");
            checkBaseline(manifest,inventory);checkCoverage(coverage);Map<String,String> functions=functionSnapshot(),instructions=instructionSnapshot(),data=dataSnapshot();String memory=memoryHash();Set<String> refsBefore=referenceSnapshot();Map<String,Set<String>> calledBefore=calledGraph(),callersBefore=callerGraph();JsonArray refs=incomingCalls();JsonObject cfg=traverse(raw);req(cfg.get("instruction_count_including_delay_slots").getAsInt()==66,"raw CFG is not the exact 66-word body");checkCandidateFlowProfile(cfg,raw);
            AddressSet body=decodeAndCreate(elf,raw,cfg,instructions,data,memory,functions,refsBefore,calledBefore,callersBefore,refs);req(currentProgram.getListing().getInstructionAt(at(END))==null&&currentProgram.getListing().getDefinedDataContaining(at(END))==null&&currentProgram.getFunctionManager().getFunctionContaining(at(END))==null,"next word at 001ff140 must remain unowned and undecoded");
            out.addProperty("status","created_single_bounded_candidate");out.add("cfg",cfg);out.addProperty("call_graph_limit","five JALs: two resolve to preexisting functions, three unresolved targets remain uncreated");out.add("incoming_references",refs);out.addProperty("body_bytes",body.getNumAddresses());out.addProperty("body_interval_bytes",END-START);out.addProperty("excluded_next_word","001ff140");out.addProperty("excluded_next_word_hex","27bdff90");out.addProperty("function_count_after",currentProgram.getFunctionManager().getFunctionCount());out.addProperty("old_function_snapshot_preserved",true);out.addProperty("initialized_memory_preserved",true);out.addProperty("defined_data_preserved",true);out.addProperty("scope","Static provisional candidate only. No original function identity, semantics, runtime reachability, or whole-game completeness is established.");
        } catch(Exception e) { out.addProperty("status","rejected_or_failed");out.addProperty("failure",e.getClass().getSimpleName()+": "+String.valueOf(e.getMessage()));write(output,out);throw e; }
        write(output,out);println("EE_CLOSURE_CANDIDATE_OK entry="+ENTRY+" body_bytes=264 function_count_delta=1 next_word_excluded=001ff140");
    }
    private void write(Path p,JsonObject o)throws Exception{Files.createDirectories(p.getParent());Files.writeString(p,new GsonBuilder().setPrettyPrinting().create().toJson(o)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);}
}
