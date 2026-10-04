// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Isolated IOP export-target experiment. Creates functions only for exact
 * relocation-backed export targets that are already decoded as unowned code.
 * It does not disassemble undefined targets; those require a separate bounded
 * flow proof. Use on a fresh copied project with -noanalysis -readOnly.
 */
public class CreateIopExportTargetCandidates extends GhidraScript {
    private String hex(byte[] b) { return HexFormat.of().formatHex(b); }
    private String digest(byte[] b) throws Exception { return hex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private void require(boolean ok, String message) { if (!ok) throw new IllegalStateException(message); }
    private String blockDigest(MemoryBlock block) throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256"); byte[] buf=new byte[65536]; long off=0;
        while(off<block.getSize()){monitor.checkCancelled();int n=(int)Math.min(buf.length,block.getSize()-off);block.getBytes(block.getStart().add(off),buf,0,n);md.update(buf,0,n);off+=n;}
        return hex(md.digest());
    }
    private JsonArray ranges(AddressSetView set) {
        JsonArray a=new JsonArray(); for(AddressRange r:set.getAddressRanges()){JsonObject x=new JsonObject();x.addProperty("start",r.getMinAddress().toString());x.addProperty("end",r.getMaxAddress().toString());x.addProperty("bytes",r.getLength());a.add(x);}return a;
    }
    private AddressSet instructionAddresses(AddressSetView region) {
        AddressSet set=new AddressSet(); for(Instruction ins:currentProgram.getListing().getInstructions(region,true)) set.addRange(ins.getAddress(),ins.getMaxAddress()); return set;
    }
    private String listingState() throws Exception {
        StringBuilder s=new StringBuilder(); Listing l=currentProgram.getListing();
        for(MemoryBlock b:currentProgram.getMemory().getBlocks()) if(b.isInitialized()){
            AddressSet extent=new AddressSet(b.getStart(),b.getEnd());
            for(Instruction i:l.getInstructions(extent,true))s.append('I').append(i.getAddress()).append(':').append(hex(i.getBytes())).append('\n');
            for(Data d:l.getDefinedData(extent,true))s.append('D').append(d.getAddress()).append(':').append(d.getLength()).append(':').append(d.getDataType().getPathName()).append('\n');
        }
        return digest(s.toString().getBytes(StandardCharsets.UTF_8));
    }
    private boolean insideText(AddressSetView body,long size){if(body.isEmpty())return false;for(AddressRange r:body.getAddressRanges())if(r.getMinAddress().getOffset()<0||r.getMaxAddress().getOffset()>=size)return false;return true;}
    private Set<String> functionRows(FunctionManager fm) {
        Set<String> rows=new TreeSet<>(); for(Function f:fm.getFunctions(true))rows.add(f.getEntryPoint()+"|"+f.getName()+"|"+ranges(f.getBody())); return rows;
    }
    private JsonObject functionRow(Function f) {
        JsonObject x=new JsonObject();x.addProperty("entry",f.getEntryPoint().toString());x.addProperty("name",f.getName());x.addProperty("body_bytes",f.getBody().getNumAddresses());x.add("body_ranges",ranges(f.getBody()));return x;
    }
    private long u32(byte[] b,int p){return (b[p]&255L)|((b[p+1]&255L)<<8)|((b[p+2]&255L)<<16)|((b[p+3]&255L)<<24);}
    private int u16(byte[] b,int p){return (b[p]&255)|((b[p+1]&255)<<8);}
    private JsonObject rawTextProof(byte[] b) throws Exception {
        require(b.length>=52&&b[0]==0x7f&&b[1]=='E'&&b[2]=='L'&&b[3]=='F'&&b[4]==1&&b[5]==1&&u16(b,16)==0xff80&&u16(b,18)==8,"raw module is not ELF32LE ET_IOP/EM_MIPS");
        long shoff=u32(b,32);int es=u16(b,46),n=u16(b,48),str=u16(b,50);require(es>=40&&n>0&&str<n&&shoff+(long)es*n<=b.length,"ELF section header table invalid");
        int nh=Math.toIntExact(shoff+(long)es*str);long namesOff=u32(b,nh+16),namesSize=u32(b,nh+20);require(namesOff+namesSize<=b.length,"ELF section-name table invalid");
        int textIndex=-1,textOff=-1,textSize=-1,relCount=0;long textFlags=-1,textAddr=-1;List<Integer> relSections=new ArrayList<>();
        for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);long no=u32(b,h);require(no<namesSize,"ELF section-name offset invalid");int a=Math.toIntExact(namesOff+no),z=a;while(z<namesOff+namesSize&&b[z]!=0)z++;String name=new String(b,a,z-a,StandardCharsets.US_ASCII);int type=(int)u32(b,h+4);long flags=u32(b,h+8),addr=u32(b,h+12),off=u32(b,h+16),size=u32(b,h+20);
            if(name.equals(".text")){require(textIndex<0,"multiple .text sections");textIndex=i;textOff=Math.toIntExact(off);textSize=Math.toIntExact(size);textFlags=flags;textAddr=addr;}
        }
        require(textIndex>=0&&textAddr==0&&(textFlags&4)!=0&&textOff>=0&&textSize>=0&&(long)textOff+textSize<=b.length,"raw .text profile invalid");
        Map<Long,Integer> rels=new HashMap<>();
        for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);int type=(int)u32(b,h+4);long off=u32(b,h+16),size=u32(b,h+20);int info=(int)u32(b,h+28),ent=(int)u32(b,h+36);if(type!=9||info!=textIndex||size==0)continue;require(ent==8&&size%8==0&&off+size<=b.length,".rel.text entry profile invalid");relCount++;
            for(int at=0;at<size;at+=8){long site=u32(b,Math.toIntExact(off)+at);int ri=(int)u32(b,Math.toIntExact(off)+at+4);require(!rels.containsKey(site),"duplicate .rel.text site");rels.put(site,ri);}
        }
        JsonObject proof=new JsonObject();proof.addProperty("text_file_offset",textOff);proof.addProperty("text_size",textSize);proof.addProperty("text_section_index",textIndex);proof.addProperty("text_sha256",digest(Arrays.copyOfRange(b,textOff,textOff+textSize)));proof.addProperty("rel_text_section_count",relCount);proof.addProperty("rel_text_site_count",rels.size());return proof;
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();require(args.length==3,"Expected fresh output JSON, raw ELF input path, and pinned export-target seed JSON");
        String program=currentProgram.getName();byte[] raw=Files.readAllBytes(Paths.get(args[1]));String rawHash=digest(raw);
        JsonObject root=JsonParser.parseString(Files.readString(Paths.get(args[2]),StandardCharsets.UTF_8)).getAsJsonObject();
        JsonObject module=root.getAsJsonObject("modules").getAsJsonObject(program);
        require(module!=null,"program absent from pinned export-target seed set");
        require(currentProgram.getExecutableSHA256().equals(module.get("module_sha256").getAsString())&&rawHash.equals(module.get("module_sha256").getAsString()),"raw/program identity does not match seed manifest");
        JsonObject rawProof=rawTextProof(raw);byte[] rawText=Arrays.copyOfRange(raw,rawProof.get("text_file_offset").getAsInt(),rawProof.get("text_file_offset").getAsInt()+rawProof.get("text_size").getAsInt());
        require(rawProof.get("text_size").getAsInt()==module.get("text_size").getAsInt()&&rawProof.get("text_sha256").getAsString().equals(module.get("text_sha256").getAsString()),"raw ELF .text section differs from seed identity");
        require("MIPS:LE:32:default".equals(currentProgram.getLanguageID().toString()),"Ghidra language mismatch");
        require("default".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString()),"Ghidra compiler spec mismatch");
        MemoryBlock text=null;for(MemoryBlock b:currentProgram.getMemory().getBlocks())if(b.getName().equals(".text")){require(text==null,"multiple .text blocks");text=b;}
        require(text!=null&&text.isInitialized()&&text.isExecute()&&text.getStart().getOffset()==0,".text mapping is not initialized executable base-zero");
        require(text.getSize()==module.get("text_size").getAsLong()&&blockDigest(text).equals(module.get("text_sha256").getAsString()),".text differs from exact seed-pinned raw section");

        FunctionManager fm=currentProgram.getFunctionManager();Listing listing=currentProgram.getListing();
        Set<String> priorFunctions=functionRows(fm);String priorListing=listingState();String priorText=blockDigest(text);int priorCount=fm.getFunctionCount();
        JsonArray dispositions=new JsonArray(),created=new JsonArray();Map<String,Integer> counts=new TreeMap<>();
        for(JsonElement element:module.getAsJsonArray("entries")){
            monitor.checkCancelled();JsonObject seed=element.getAsJsonObject();
            if(!"unowned_instruction".equals(seed.get("listing_status").getAsString()))continue;
            String targetText=seed.get("target_text_offset").getAsString();
            long target=Long.parseLong(targetText);String disposition="rejected";String reason="";JsonObject item=new JsonObject();
            item.addProperty("target_text_offset",targetText);item.addProperty("relocation_site_text_offset",seed.get("relocation_site_text_offset").getAsString());item.addProperty("library",seed.get("library").getAsString());item.addProperty("ordinal",seed.get("ordinal").getAsInt());
            long site=Long.parseLong(seed.get("relocation_site_text_offset").getAsString());long table=Long.parseLong(seed.get("table_text_offset").getAsString());int ordinal=seed.get("ordinal").getAsInt();
            if((target&3)!=0||target>=text.getSize()||site!=table+20L+4L*ordinal||table<0||table>rawText.length-20||site<0||site>rawText.length-4||u32(rawText,Math.toIntExact(table))!=0x41c00000L){reason="target/pointer site outside aligned .text or raw export-table slot proof invalid";}
            else{
                int relInfo=findRelocationInfo(raw,rawProof,site);long addend=u32(rawText,Math.toIntExact(site));long relocated=(addend+0x1000L)&0xffffffffL;
                if((relInfo>>>8)!=0||(relInfo&255)!=2||relocated!=((target+0x1000L)&0xffffffffL)){reason="export target lacks exact R_MIPS_32/symbol-zero pointer proof";dispositions.add(item);counts.put(disposition,counts.getOrDefault(disposition,0)+1);continue;}
                Address entry=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(target);Instruction first=listing.getInstructionAt(entry);
                if(first==null){reason="seed no longer has a defined instruction";}
                else if(fm.getFunctionAt(entry)!=null){disposition="already_saved_entry";reason="entry already has saved function";}
                else if(fm.getFunctionContaining(entry)!=null){disposition="now_function_owned";reason="target is owned after earlier candidate or existing saved function";}
                else{
                    AddressSetView body=CreateFunctionCmd.getFunctionBody(currentProgram,entry,monitor);AddressSet decoded=instructionAddresses(body);
                    AddressSet uncovered=new AddressSet(body);uncovered.delete(decoded);AddressSet outside=new AddressSet(decoded);outside.delete(body);
                    boolean overlap=false;for(Function f:fm.getFunctions(true))if(!f.getBody().intersect(body).isEmpty()){overlap=true;break;}
                    item.add("proposed_body_ranges",ranges(body));item.addProperty("proposed_body_bytes",body.getNumAddresses());item.addProperty("body_matches_existing_instruction_addresses",uncovered.isEmpty()&&outside.isEmpty());
                    if(body.isEmpty()||!body.contains(entry)||!insideText(body,text.getSize())||!uncovered.isEmpty()||!outside.isEmpty()||overlap){reason="empty, incomplete, out-of-.text, or colliding existing CFG body";}
                    else{
                        int tx=currentProgram.startTransaction("provisional relocation-backed IOP export target");boolean commit=false;
                        try{
                            String name=String.format("IOP_EXPORT_%08X_PROVISIONAL",target);
                            CreateFunctionCmd cmd=new CreateFunctionCmd(name,entry,body,SourceType.ANALYSIS);
                            if(!cmd.applyTo(currentProgram,monitor))throw new IllegalStateException("CreateFunctionCmd failed: "+cmd.getStatusMsg());
                            Function made=fm.getFunctionAt(entry);
                            if(made==null||!made.getBody().equals(body)||made.getSymbol().getSource()!=SourceType.ANALYSIS)throw new IllegalStateException("created function identity/body/source mismatch");
                            if(fm.getFunctionCount()!=priorCount+created.size()+1)throw new IllegalStateException("function count delta mismatch");
                            Set<String> expected=new TreeSet<>(priorFunctions);expected.addAll(functionRowsFor(created));
                            Set<String> actual=functionRows(fm);if(actual.size()!=expected.size()+1||!actual.containsAll(expected))throw new IllegalStateException("unexpected existing function row mutation");
                            if(!priorListing.equals(listingState())||!priorText.equals(blockDigest(text)))throw new IllegalStateException("listing or .text bytes changed during function-only candidate creation");
                            item.add("function",functionRow(made));created.add(item.deepCopy());disposition="created_provisional_cfg_candidate";reason="existing decoded CFG only; no disassembly";commit=true;
                        }finally{currentProgram.endTransaction(tx,commit);}
                    }
                }
            }
            item.addProperty("disposition",disposition);item.addProperty("reason",reason);dispositions.add(item);counts.put(disposition,counts.getOrDefault(disposition,0)+1);
        }
        require(fm.getFunctionCount()==priorCount+created.size(),"final candidate function delta mismatch");
        require(!listingState().equals("")&&priorListing.equals(listingState()),"final listing differs from pre-target state");require(priorText.equals(blockDigest(text)),"final .text bytes changed");
        JsonObject out=new JsonObject();out.addProperty("schema_version",1);out.addProperty("program",program);out.addProperty("executable_sha256",rawHash);out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString());out.addProperty("ghidra_version",getGhidraVersion());out.addProperty("seed_manifest_sha256",digest(Files.readAllBytes(Paths.get(args[2]))));out.add("raw_text_relocation_proof",rawProof);out.addProperty("candidate_policy","Only raw export-table pointer slots with R_MIPS_32 symbol-zero relocation and exact synthetic-base target agreement. Create a function only when target is already an unowned decoded instruction and existing CFG body exactly equals decoded instruction addresses without overlap. Undefined seeds are deferred; no disassembly.");out.addProperty("function_count_before",priorCount);out.addProperty("function_count_after",fm.getFunctionCount());out.add("disposition_counts",new Gson().toJsonTree(counts));out.add("created_functions",created);out.add("target_dispositions",dispositions);out.addProperty("listing_sha256_unchanged",priorListing.equals(listingState()));out.addProperty("text_sha256_unchanged",priorText.equals(blockDigest(text)));out.addProperty("claim_limits","Candidate function extents are Ghidra CFG results over pre-decoded code, not proof of original source extent or runtime invocation. Undefined export targets are not included in this experiment.");
        Path outPath=Paths.get(args[0]);Files.createDirectories(outPath.toAbsolutePath().getParent());Files.writeString(outPath,new GsonBuilder().setPrettyPrinting().create().toJson(out)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
        println("IOP_EXPORT_TARGET_CANDIDATES program="+program+" created="+created.size()+" counts="+counts);
    }
    private int findRelocationInfo(byte[] b,JsonObject proof,long site) throws Exception {
        long shoff=u32(b,32);int es=u16(b,46),n=u16(b,48),str=u16(b,50);int nh=Math.toIntExact(shoff+(long)es*str);long namesOff=u32(b,nh+16);int hits=0,found=0;
        int textIndex=proof.get("text_section_index").getAsInt();
        for(int i=0;i<n;i++){int h=Math.toIntExact(shoff+(long)es*i);if((int)u32(b,h+4)!=9||(int)u32(b,h+28)!=textIndex)continue;long secOff=u32(b,h+16),secSize=u32(b,h+20);int ent=(int)u32(b,h+36);if(ent!=8||secSize%8!=0||secOff+secSize>b.length)continue;for(int at=0;at<secSize;at+=8){int p=Math.toIntExact(secOff)+at;if(u32(b,p)==site){hits++;found=(int)u32(b,p+4);}}}
        require(hits==1,"export pointer slot must have exactly one relocation record");return found;
    }
    private Set<String> functionRowsFor(JsonArray array){Set<String>s=new TreeSet<>();for(JsonElement e:array){JsonObject f=e.getAsJsonObject().getAsJsonObject("function");s.add(f.get("entry").getAsString()+"|"+f.get("name").getAsString()+"|"+f.getAsJsonArray("body_ranges"));}return s;}
}
