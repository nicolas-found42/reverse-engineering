//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.JumpTable;
import ghidra.program.model.symbol.*;
import ghidra.framework.Application;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** Two byte-pinned, experimental computed-dispatch repairs. Run only on a copied project. */
public class VerifiedDispatchPairOverride extends GhidraScript {
  static final String EXE="216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
  static final String NATIVE="cd6d7e92061f7e47c7eaa86f82cb7045b4c3e624d1764832283f00b8dca57acd";
  static final String BASELINE_MANIFEST="39302b3579c4c88f688a962fc794a6f9c6d652730c4f09794e7a40b29001192e";

  static final String PATCH="2cbc7bcc430165a69661259517fd164f100ea95c6cd8de6d27191c866a347802";
  static final String SOURCE_BASIS_SHA256="dafbb368f61228a1764eb2b032ae584e2b267ea21797c9bc43620923871a97b0";
  static final String[] TARGETS_A={
    "001fbef8","001fbf0c","001fbf3c","001fbf60","001fbf60"
  };
  static final String[] TRUE_INDEX={
    "0","10","11","14","33","42","45","47","59","60","92","94"
  };

  String hash(byte[] b)throws Exception{
    StringBuilder s=new StringBuilder();
    for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));
    return s.toString();
  }

  String memoryHash()throws Exception{
    MessageDigest d=MessageDigest.getInstance("SHA-256");
    byte[] chunk=new byte[65536];
    for(MemoryBlock b:currentProgram.getMemory().getBlocks()){
      if(!b.isInitialized())continue;
      d.update(b.getName().getBytes(StandardCharsets.UTF_8));
      d.update(b.getStart().toString().getBytes(StandardCharsets.UTF_8));
      long offset=0;
      while(offset<b.getSize()){
        int n=(int)Math.min(chunk.length,b.getSize()-offset);
        currentProgram.getMemory().getBytes(b.getStart().add(offset),chunk,0,n);
        d.update(chunk,0,n);
        offset+=n;
      }
    }
    StringBuilder s=new StringBuilder();
    for(byte x:d.digest())s.append(String.format("%02x",x&255));
    return s.toString();
  }

  Map<String,String> instructionBytes()throws Exception{
    Map<String,String> out=new TreeMap<>();
    for(Instruction i:currentProgram.getListing().getInstructions(true))out.put(i.getAddress().toString(),bytes(i.getAddress(),i.getLength()));
    return out;
  }

  long[] textCoverage(){
    MemoryBlock text=currentProgram.getMemory().getBlock(".text");
    require(text!=null&&text.isInitialized()&&text.isExecute(),"expected initialized executable .text block missing");
    AddressSet extent=new AddressSet(text.getStart(),text.getEnd());
    AddressSet instructions=new AddressSet(),owned=new AddressSet(),data=new AddressSet();
    long count=0,unownedCount=0;
    for(Instruction i:currentProgram.getListing().getInstructions(extent,true)){
      instructions.addRange(i.getAddress(),i.getMaxAddress());
      count++;
      if(currentProgram.getFunctionManager().getFunctionContaining(i.getAddress())==null)unownedCount++;
      else owned.addRange(i.getAddress(),i.getMaxAddress());
    }
    for(Data d:currentProgram.getListing().getDefinedData(extent,true))data.addRange(d.getAddress(),d.getMaxAddress());
    AddressSet unowned=new AddressSet(instructions);unowned.delete(owned);
    AddressSet undefined=new AddressSet(extent);undefined.delete(instructions);undefined.delete(data);
    return new long[]{count,instructions.getNumAddresses(),owned.getNumAddresses(),unownedCount,
      unowned.getNumAddresses(),data.getNumAddresses(),undefined.getNumAddresses()};
  }

  Map<String,Integer> definedDataSpans(){
    Map<String,Integer> out=new TreeMap<>();
    for(Data d:currentProgram.getListing().getDefinedData(true))out.put(d.getAddress().toString(),d.getLength());
    return out;
  }

  JsonObject coverageJson(long[] v){
    JsonObject o=new JsonObject();
    o.addProperty("instruction_count",v[0]);
    o.addProperty("instruction_bytes",v[1]);
    o.addProperty("function_instruction_bytes",v[2]);
    o.addProperty("unowned_instruction_count",v[3]);
    o.addProperty("unowned_instruction_bytes",v[4]);
    o.addProperty("defined_data_bytes",v[5]);
    o.addProperty("undefined_bytes",v[6]);
    return o;
  }

  String fileHash(Path p)throws Exception{
    return hash(Files.readAllBytes(p));
  }

  String bytes(Address a,int n)throws Exception{
    byte[] b=new byte[n];
    currentProgram.getMemory().getBytes(a,b);
    StringBuilder s=new StringBuilder();
    for(byte x:b)s.append(String.format("%02x",x&255));
    return s.toString();
  }

  Address addr(String s){
    return toAddr(s);
  }

  void require(boolean v,String m){
    if(!v)throw new IllegalStateException(m);
  }

  JsonArray targetsToJson(List<Address> xs){
    JsonArray a=new JsonArray();
    for(Address x:xs)a.add(x.toString());
    return a;
  }

  JsonArray addedInstructions(AddressSetView added)throws Exception{
    JsonArray rows=new JsonArray();
    for(Instruction i:currentProgram.getListing().getInstructions(added,true)){
      JsonObject o=new JsonObject();
      o.addProperty("address",i.getAddress().toString());
      o.addProperty("text",i.toString());
      o.addProperty("bytes",bytes(i.getAddress(),i.getLength()));
      rows.add(o);
    }
    return rows;
  }

  String decompile(Function f)throws Exception{
    DecompInterface d=new DecompInterface();
    try{
      d.setSimplificationStyle("decompile");
      d.toggleCCode(true);
      d.toggleSyntaxTree(true);
      require(d.openProgram(currentProgram),"failed to open patched decompiler: "+d.getLastMessage());
      DecompileResults r=d.decompileFunction(f,120,monitor);
      require(r.decompileCompleted()&&r.getDecompiledFunction()!=null,"decompilation failed at "+f.getEntryPoint()+": "+r.getErrorMessage());
      return r.getDecompiledFunction().getC();
    }
    finally{
      d.dispose();
    }
  }

  void checkNoConflict(Address target,Function owner)throws Exception{
    MemoryBlock b=currentProgram.getMemory().getBlock(target);
    require(b!=null&&b.isInitialized()&&b.isExecute(),"target not initialized executable memory: "+target);
    Function prior=currentProgram.getFunctionManager().getFunctionContaining(target);
    require(prior==null||prior.getEntryPoint().equals(owner.getEntryPoint()),"target owned by another function: "+target);
    Instruction containing=currentProgram.getListing().getInstructionContaining(target);
    require(containing==null||containing.getAddress().equals(target),"target overlaps an existing instruction: "+target);
  }

  List<Address> readTargetTable(Address base,int count)throws Exception{
    List<Address> out=new ArrayList<>();
    for(int i=0;i<count;i++){
      long v=currentProgram.getMemory().getInt(base.add(4L*i))&0xffffffffL;
      out.add(addr(String.format("%08x",v)));
    }
    return out;
  }

  public void run()throws Exception{
    String[] args=getScriptArgs();
    require(args.length==4,"mode outputDir baselineManifest patchPath");
    String mode=args[0];
    require(mode.equals("positive")||mode.equals("permuted"),"mode must be positive or permuted");
    Path out=Paths.get(args[1]).toAbsolutePath();
    require(!Files.exists(out),"output directory already exists");
    Files.createDirectories(out.resolve("functions"));
    Path baseline=Paths.get(args[2]).toAbsolutePath();
    Path patch=Paths.get(args[3]).toAbsolutePath();
    require(EXE.equals(currentProgram.getExecutableSHA256()),"executable/PAL hash mismatch");
    require("r5900:LE:32:default".equals(currentProgram.getLanguageID().toString()),"language mismatch");
    Path nativePath=Application.getOSFile("Decompiler","decompile").toPath();
    String nativeSha=fileHash(nativePath);
    require(NATIVE.equals(nativeSha),"patched native hash mismatch: "+nativeSha);
    require(PATCH.equals(fileHash(patch)),"native source patch hash mismatch");
    Path scriptPath=Paths.get(getSourceFile().getAbsolutePath());
    String scriptSha=fileHash(scriptPath);
    String sourceBasis=Files.readString(scriptPath).replace(SOURCE_BASIS_SHA256,"0000000000000000000000000000000000000000000000000000000000000000");
    require(hash(sourceBasis.getBytes(StandardCharsets.UTF_8)).equals(SOURCE_BASIS_SHA256),"script source hash guard mismatch");
    require(fileHash(baseline).equals(BASELINE_MANIFEST),"baseline 3,837-entry manifest hash mismatch");
    JsonObject oldManifest=JsonParser.parseString(Files.readString(baseline)).getAsJsonObject();
    JsonArray oldRows=oldManifest.getAsJsonArray("functions");
    require(oldRows.size()==3837,"baseline inventory size mismatch");
    Set<String> expectedEntries=new TreeSet<>();
    for(JsonElement e:oldRows)expectedEntries.add(e.getAsJsonObject().get("entry").getAsString());
    FunctionManager fm=currentProgram.getFunctionManager();
    Set<String> beforeEntries=new TreeSet<>();
    for(Function f:fm.getFunctions(true))beforeEntries.add(f.getEntryPoint().toString());
    require(beforeEntries.size()==3837&&beforeEntries.equals(expectedEntries),"pre-experiment function-entry set differs from pinned baseline");
    Map<String,String> beforeInstructions=instructionBytes();
    long[] coverageBefore=textCoverage();
    long[] expectedCoverageBefore={247717,990868,859688,32795,131180,6,154938};
    require(Arrays.equals(coverageBefore,expectedCoverageBefore),"baseline .text coverage differs from the pinned listing profile: "+Arrays.toString(coverageBefore));
    Map<String,Integer> beforeData=definedDataSpans();
    String memoryHashBefore=memoryHash();
    Function fa=fm.getFunctionAt(addr("001fbe48")),fb=fm.getFunctionAt(addr("001161a8"));
    require(fa!=null&&fb!=null,"expected functions absent");
    long oldA=fa.getBody().getNumAddresses(),oldB=fb.getBody().getNumAddresses();
    require(oldA==232&&oldB==968,"unexpected pre-experiment body sizes: "+oldA+","+oldB);
    AddressSet beforeA=new AddressSet(fa.getBody()),beforeB=new AddressSet(fb.getBody());
    // FUN_001fbe48: source guarded five-entry selector and exact duplicate-bearing raw table.
    for(String at:new String[]{
      "001fbeb8","001fbec8","001fbed4"
    }
    ){
      Instruction i=currentProgram.getListing().getInstructionAt(addr(at));
      require(i!=null&&i.toString().equals("_sltiu v0,s3,0x5")&&bytes(addr(at),4).equals("0500622e"),"selector <5 guard mismatch at "+at);
    }
    Instruction ba=currentProgram.getListing().getInstructionAt(addr("001fbed8"));
    require(ba!=null&&ba.toString().equals("beq v0,zero,0x001fbf80")&&bytes(addr("001fbed8"),4).equals("29004010"),"selector exit branch mismatch");
    require(bytes(addr("001fbebc"),4).equals("7401038e")&&bytes(addr("001fbecc"),4).equals("4808028e"),"selector call-site context mismatch");
    Address dispatchA=addr("001fbef0");
    Instruction ja=currentProgram.getListing().getInstructionAt(dispatchA);
    require(ja!=null&&ja.toString().equals("jr a0")&&bytes(dispatchA,4).equals("08008000")&&bytes(addr("001fbef4"),4).equals("00000000"),"dispatch A opcode/delay mismatch");
    List<Address> rawA=readTargetTable(addr("0028b520"),5);
    for(int i=0;i<5;i++)require(rawA.get(i).toString().equals(TARGETS_A[i]),"dispatch A raw target mismatch at index "+i);
    String[] suppliedA=TARGETS_A.clone();
    if(mode.equals("permuted")){
      suppliedA=new String[]{
        TARGETS_A[0],TARGETS_A[2],TARGETS_A[1],TARGETS_A[3],TARGETS_A[4]
      }
      ;
    }
    ArrayList<Address> addressesA=new ArrayList<>();
    AddressSet allowedDecodeSpan=new AddressSet(addr("001fbef8"),addr("001fbf7f"));
    JsonArray beforeTargetsA=new JsonArray();
    for(Address t:rawA){
      checkNoConflict(t,fa);
      beforeTargetsA.add(t.toString());
      if(currentProgram.getListing().getInstructionAt(t)==null){
        require(currentProgram.getListing().getInstructionContaining(t)==null,"decode would overlap existing instruction at "+t);
        for(int at=0;at<=0x84;at+=4){
          Address instructionAddress=addr(String.format("%08x",0x001fbef8+at));
          if(currentProgram.getListing().getInstructionAt(instructionAddress)!=null)continue;
          AddressSet oneInstruction=new AddressSet(instructionAddress,instructionAddress.add(3));
          // Use an explicit one-address seed (rather than the convenience
          // constructor, which enables the default repeat-pattern behavior).
          // Flow and automatic analysis are both disabled so no neighboring
          // code can be added as a side effect of a table target.
          DisassembleCommand command=new DisassembleCommand(new AddressSet(instructionAddress),oneInstruction,false);
          command.enableCodeAnalysis(false);
          require(command.applyTo(currentProgram,monitor),"bounded one-instruction decode failed at "+instructionAddress+": "+command.getStatusMsg());
          require(allowedDecodeSpan.contains(command.getDisassembledAddressSet()),"decoder escaped exact dispatch target span at "+instructionAddress+" decoded="+command.getDisassembledAddressSet());
        }
      }
      require(currentProgram.getListing().getInstructionAt(t)!=null,"failed to decode raw table target "+t);
    }
    for(String t:suppliedA){
      Address a=addr(t);
      ja.addOperandReference(0,a,RefType.COMPUTED_JUMP,SourceType.USER_DEFINED);
      addressesA.add(a);
    }
    new JumpTable(dispatchA,addressesA,true,0).writeOverride(fa);
    CreateFunctionCmd.fixupFunctionBody(currentProgram,fa,monitor);
    AddressSet afterA=new AddressSet(fa.getBody());
    AddressSet addedA=afterA.subtract(beforeA);
    require(fa.getBody().getNumAddresses()==368,"dispatch A body must be 368 bytes after merge");
    JsonArray rowsA=addedInstructions(addedA);
    require(rowsA.size()==34,"dispatch A must add exactly 34 raw instructions");
    // Membership is exact and contiguous; the first target block at ef8 was already decoded but unowned.
    for(int a=0x001fbef8;a<=0x001fbf08;a+=4)require(addedA.contains(addr(String.format("%08x",a))),"missing added body byte at "+String.format("%08x",a));
    for(int a=0x001fbf0c;a<=0x001fbf7c;a+=4)require(addedA.contains(addr(String.format("%08x",a))),"missing added body byte at "+String.format("%08x",a));
    // FUN_001161a8: signed-byte index+1, unsigned <95 guard, exact 95-word table hash/targets.
    Address dispatchB=addr("00116508");
    Instruction jb=currentProgram.getListing().getInstructionAt(dispatchB);
    require(jb!=null&&jb.toString().equals("jr v1")&&bytes(dispatchB,4).equals("08006000")&&bytes(addr("0011650c"),4).equals("00000000"),"dispatch B opcode/delay mismatch");
    require(bytes(addr("001164e4"),4).equals("0000a383")&&bytes(addr("001164e8"),4).equals("01006324")&&bytes(addr("001164ec"),4).equals("5f00622c")&&bytes(addr("001164f0"),4).equals("09004010")&&bytes(addr("001164f4"),4).equals("0000a493"),"dispatch B signed-index/bounds/delay sequence mismatch");
    List<Address> rawB=readTargetTable(addr("002519b0"),95);
    StringBuilder tableBytesB=new StringBuilder();
    int trueCount=0;
    ArrayList<Address> suppliedB=new ArrayList<>();
    JsonArray tableRowsB=new JsonArray();
    Set<Integer> trueSet=new HashSet<>();
    for(String s:TRUE_INDEX)trueSet.add(Integer.parseInt(s));
    for(int i=0;i<95;i++){
      Address cell=addr("002519b0").add(4L*i);
      String cellBytes=bytes(cell,4);
      tableBytesB.append(cellBytes);
      String target=rawB.get(i).toString();
      String expected=trueSet.contains(i)?"00116510":"00116518";
      require(target.equals(expected),"dispatch B raw table target mismatch at index "+i);
      if(target.equals("00116510"))trueCount++;
      checkNoConflict(rawB.get(i),fb);
      suppliedB.add(rawB.get(i));
      JsonObject row=new JsonObject();
      row.addProperty("index",i);
      row.addProperty("cell",cell.toString());
      row.addProperty("raw_bytes",cellBytes);
      row.addProperty("target",target);
      tableRowsB.add(row);
    }
    require(trueCount==12&&hash(hexBytes(tableBytesB.toString())).equals("1f8efe77696be20978886ef81da47e6cfded771ac29ac74f153020aaf98ade12"),"dispatch B table count/hash mismatch");
    String[] permutedB=suppliedB.stream().map(Address::toString).toArray(String[]::new);
    for(String t:permutedB)jb.addOperandReference(0,addr(t),RefType.COMPUTED_JUMP,SourceType.USER_DEFINED);
    ArrayList<Address> addressesB=new ArrayList<>();
    for(String t:permutedB)addressesB.add(addr(t));
    new JumpTable(dispatchB,addressesB,true,0).writeOverride(fb);
    CreateFunctionCmd.fixupFunctionBody(currentProgram,fb,monitor);
    AddressSet afterB=new AddressSet(fb.getBody());
    AddressSet addedB=afterB.subtract(beforeB);
    require(fb.getBody().getNumAddresses()==976,"dispatch B body must be 976 bytes after merge");
    JsonArray rowsB=addedInstructions(addedB);
    require(rowsB.size()==2&&addedB.contains(addr("00116510"))&&addedB.contains(addr("00116514")),"dispatch B must add exact target/delay instructions only");
    require(bytes(addr("00116510"),4).equals("02000010")&&bytes(addr("00116514"),4).equals("01000224"),"dispatch B true-target bytes mismatch");
    Set<String> afterEntries=new TreeSet<>();
    for(Function f:fm.getFunctions(true))afterEntries.add(f.getEntryPoint().toString());
    require(afterEntries.equals(beforeEntries),"experiment changed the saved function entry set");
    Map<String,String> afterInstructions=instructionBytes();
    Set<String> expectedNewInstructions=new TreeSet<>();
    for(int at=0;at<=0x70;at+=4)expectedNewInstructions.add(String.format("%08x",0x001fbf0c+at));
    Set<String> actualNewInstructions=new TreeSet<>(afterInstructions.keySet());
    actualNewInstructions.removeAll(beforeInstructions.keySet());
    require(actualNewInstructions.equals(expectedNewInstructions),"listing gained instructions outside the 29 exact 001fbe48 table-target span instructions; actual="+actualNewInstructions+" expected="+expectedNewInstructions);
    Set<String> missingInstructions=new TreeSet<>(beforeInstructions.keySet());
    missingInstructions.removeAll(afterInstructions.keySet());
    require(missingInstructions.isEmpty(),"experiment removed previously defined instructions");
    for(String address:beforeInstructions.keySet())require(beforeInstructions.get(address).equals(afterInstructions.get(address)),"experiment changed pre-existing instruction bytes at "+address);
    Map<String,Integer> afterData=definedDataSpans();
    require(beforeData.equals(afterData),"experiment changed defined-data code units outside the verified function ownership edits");
    long[] coverageAfter=textCoverage();
    long[] expectedCoverageAfter={247746,990984,859832,32788,131152,6,154822};
    require(Arrays.equals(coverageAfter,expectedCoverageAfter),".text coverage delta differs from the pinned expected totals: "+Arrays.toString(coverageAfter));
    String memoryHashAfter=memoryHash();
    require(memoryHashBefore.equals(memoryHashAfter),"experiment changed initialized memory bytes");
    String cA=decompile(fa),cB=decompile(fb);
    require(!cB.contains("bad1abe1bad1ab1f")&&!cB.contains("Calculation of case label failed")&&cB.contains("PTR_default_002519b0")&&cB.contains("0x116510")&&cB.contains("0x116518"),"B table output lacks exact two-target mapping or retains failed case label");
    if(mode.equals("positive")){
      require(cA.contains("switch((int)uVar5)")&&cA.contains("default:")&&cA.contains("piVar1[0x2a]"),"positive A lacks bounded selector cases/default behavior");
    }
    else{
      require(cA.contains("PTR_case_0_0028b520")||cA.contains("0028b520"),"permuted A negative control did not fall back to pointer table");
    }
    Files.writeString(out.resolve("functions/001fbe48.c"),cA,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    Files.writeString(out.resolve("functions/001161a8.c"),cB,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    JsonObject m=new JsonObject();
    m.addProperty("schema_version",1);
    m.addProperty("mode",mode);
    m.addProperty("program",currentProgram.getName());
    m.addProperty("language",currentProgram.getLanguageID().toString());
    m.addProperty("executable_sha256",EXE);
    m.addProperty("patched_native_sha256",nativeSha);
    m.addProperty("source_patch_sha256",fileHash(patch));
    m.addProperty("script_sha256",scriptSha);
    m.addProperty("source_basis_sha256",SOURCE_BASIS_SHA256);
    m.addProperty("baseline_manifest_sha256",fileHash(baseline));
    m.addProperty("baseline_inventory_count",expectedEntries.size());
    m.addProperty("entry_set_unchanged",true);
    m.addProperty("instruction_listing_count_before",beforeInstructions.size());
    m.addProperty("instruction_listing_count_after",afterInstructions.size());
    m.add("text_coverage_before",coverageJson(coverageBefore));
    m.add("text_coverage_after",coverageJson(coverageAfter));
    m.addProperty("defined_data_spans_unchanged",true);
    JsonArray newListingRows=new JsonArray();
    for(String address:actualNewInstructions){JsonObject row=new JsonObject();row.addProperty("address",address);row.addProperty("bytes",afterInstructions.get(address));newListingRows.add(row);}
    m.add("new_listing_instructions",newListingRows);
    m.addProperty("memory_sha256_before",memoryHashBefore);
    m.addProperty("memory_sha256_after",memoryHashAfter);
    m.addProperty("initialized_memory_unchanged",true);
    m.addProperty("inventory_count_after",afterEntries.size());
    m.addProperty("entry_set_sha256",hash(String.join("\n",afterEntries).getBytes(StandardCharsets.UTF_8)));
    m.addProperty("dispatch_a_entry","001fbe48");
    m.addProperty("dispatch_a_selector_domain","0..4 (three sltiu checks and beq out when >=5)");
    m.add("dispatch_a_raw_targets",targetsToJson(rawA));
    m.add("dispatch_a_supplied_targets",targetsToJson(addressesA));
    m.addProperty("dispatch_a_body_bytes_before",oldA);
    m.addProperty("dispatch_a_body_bytes_after",fa.getBody().getNumAddresses());
    m.add("dispatch_a_added_instructions",rowsA);
    m.addProperty("dispatch_a_c_sha256",hash(cA.getBytes(StandardCharsets.UTF_8)));
    m.addProperty("dispatch_b_entry","001161a8");
    m.addProperty("dispatch_b_selector_domain","signed byte + 1; unsigned index < 95 before table read");
    m.addProperty("dispatch_b_table_sha256",hash(hexBytes(tableBytesB.toString())));
    m.add("dispatch_b_raw_table",tableRowsB);
    m.add("dispatch_b_supplied_targets",targetsToJson(addressesB));
    m.addProperty("dispatch_b_body_bytes_before",oldB);
    m.addProperty("dispatch_b_body_bytes_after",fb.getBody().getNumAddresses());
    m.add("dispatch_b_added_instructions",rowsB);
    m.addProperty("dispatch_b_c_sha256",hash(cB.getBytes(StandardCharsets.UTF_8)));
    m.addProperty("claim_limits","Isolated static experiment only; no runtime reachability, original source identity, or complete whole-game decompilation claim.");
    Files.writeString(out.resolve("experiment.json"),new GsonBuilder().setPrettyPrinting().create().toJson(m)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    println("PAIR_EXPERIMENT_OK mode="+mode+" entries="+afterEntries.size()+" bodies="+oldA+"->"+fa.getBody().getNumAddresses()+","+oldB+"->"+fb.getBody().getNumAddresses());
  }

  byte[] hexBytes(String h){
    byte[] b=new byte[h.length()/2];
    for(int i=0;i<b.length;i++)b[i]=(byte)Integer.parseInt(h.substring(i*2,i*2+2),16);
    return b;
  }
}
