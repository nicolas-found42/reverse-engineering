//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.framework.Application;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Creates a scratch-only provisional function over an exact, already-decoded 72-byte span. */
public class CreateProvisionalLeafCandidate extends GhidraScript {
  static final String EXE_SHA="216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
  static final String BASELINE_MANIFEST_SHA="39302b3579c4c88f688a962fc794a6f9c6d652730c4f09794e7a40b29001192e";
  static final String SOURCE_BASIS_SHA="9c60c34dba5d57e9ef956a1a9559323ab58c12a8a65adadbc4d854ee10f15a21";
  static final int FILE_OFFSET=0x12b180;
  static final int SPAN_BYTES=72;
  static final String RAW_SPAN="f0ffbd270000a4af0100a3930200a2930000a593c21803000300a49340190300c2100200c228050025104300802a05002b20040025104500c0230400251044000800e0031000bd27";

  String sha(byte[] b)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}
  void require(boolean v,String m){if(!v)throw new IllegalStateException(m);}
  String bytes(Address a,int n)throws Exception{byte[] b=new byte[n];currentProgram.getMemory().getBytes(a,b);return HexFormat.of().formatHex(b);}
  String functionBodies(FunctionManager fm){
    StringBuilder out=new StringBuilder();
    for(Function f:fm.getFunctions(true)){
      out.append(f.getEntryPoint()).append(':');
      AddressRangeIterator ranges=f.getBody().getAddressRanges();
      while(ranges.hasNext()){AddressRange r=ranges.next();out.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}
      out.append('\n');
    }
    return out.toString();
  }
  Map<String,String> instructionMap()throws Exception{
    Map<String,String> out=new TreeMap<>();
    for(Instruction i:currentProgram.getListing().getInstructions(true))out.put(i.getAddress().toString(),bytes(i.getAddress(),i.getLength()));
    return out;
  }
  Map<String,String> dataMap(){
    Map<String,String> out=new TreeMap<>();
    for(Data d:currentProgram.getListing().getDefinedData(true))out.put(d.getAddress().toString(),d.getLength()+":"+d.getDataType().getPathName());
    return out;
  }
  String memoryHash()throws Exception{
    MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[65536];
    for(MemoryBlock b:currentProgram.getMemory().getBlocks())if(b.isInitialized()){
      d.update(b.getName().getBytes(StandardCharsets.UTF_8));d.update(b.getStart().toString().getBytes(StandardCharsets.UTF_8));
      long at=0;while(at<b.getSize()){int n=(int)Math.min(buf.length,b.getSize()-at);currentProgram.getMemory().getBytes(b.getStart().add(at),buf,0,n);d.update(buf,0,n);at+=n;}
    }
    return HexFormat.of().formatHex(d.digest());
  }
  String ownerAt(Address a,FunctionManager fm){Function f=fm.getFunctionContaining(a);return f==null?null:f.getEntryPoint().toString();}
  JsonObject refsAt(Address a){
    JsonObject o=new JsonObject();JsonArray refs=new JsonArray();
    for(Reference r:currentProgram.getReferenceManager().getReferencesTo(a)){JsonObject x=new JsonObject();x.addProperty("from",r.getFromAddress().toString());x.addProperty("type",r.getReferenceType().toString());x.addProperty("source",r.getSource().toString());refs.add(x);}
    o.add("references",refs);return o;
  }
  String decompile(Function f)throws Exception{
    DecompInterface d=new DecompInterface();
    try{d.setSimplificationStyle("decompile");d.toggleCCode(true);d.toggleSyntaxTree(true);require(d.openProgram(currentProgram),"decompiler open failed: "+d.getLastMessage());DecompileResults r=d.decompileFunction(f,60,monitor);require(r.decompileCompleted()&&r.getDecompiledFunction()!=null,"candidate decompile failed: "+r.getErrorMessage());return r.getDecompiledFunction().getC();}
    finally{d.dispose();}
  }
  JsonArray rows(Map<String,String> m){JsonArray a=new JsonArray();for(Map.Entry<String,String> e:m.entrySet()){JsonObject o=new JsonObject();o.addProperty("entry",e.getKey());o.addProperty("body_ranges",e.getValue());a.add(o);}return a;}
  byte[] readU32Payload(Path p)throws Exception{byte[] b=Files.readAllBytes(p);require(b.length>=52,"input executable shorter than ELF header");return b;}
  JsonObject sectionMap(byte[] elf){
    ByteBuffer b=ByteBuffer.wrap(elf).order(ByteOrder.LITTLE_ENDIAN);
    require(elf[0]==0x7f&&elf[1]=='E'&&elf[2]=='L'&&elf[3]=='F'&&elf[4]==1&&elf[5]==1,"candidate input is not ELF32 little-endian");
    int shoff=b.getInt(32),shentsize=Short.toUnsignedInt(b.getShort(46)),shnum=Short.toUnsignedInt(b.getShort(48)),shstr=Short.toUnsignedInt(b.getShort(50));
    require(shentsize==40&&shstr<shnum&&shoff>=0&&shoff+(long)shentsize*shnum<=elf.length,"unsupported/invalid ELF section table");
    int stringHeader=shoff+shstr*shentsize;int strOff=b.getInt(stringHeader+16),strSize=b.getInt(stringHeader+20);
    require(strOff>=0&&strSize>=0&&strOff+(long)strSize<=elf.length,"invalid ELF section string table");
    JsonObject found=null;
    for(int i=0;i<shnum;i++){
      int h=shoff+i*shentsize,nameOff=b.getInt(h);if(nameOff<0||nameOff>=strSize)continue;
      int begin=strOff+nameOff,end=begin;while(end<strOff+strSize&&elf[end]!=0)end++;
      String name=new String(elf,begin,end-begin,StandardCharsets.US_ASCII);if(!name.equals(".user_section_uncommon"))continue;
      JsonObject x=new JsonObject();x.addProperty("name",name);x.addProperty("type",b.getInt(h+4));x.addProperty("flags",b.getInt(h+8));x.addProperty("address",Integer.toUnsignedString(b.getInt(h+12),16));x.addProperty("file_offset",Integer.toUnsignedString(b.getInt(h+16),16));x.addProperty("size",Integer.toUnsignedString(b.getInt(h+20),16));found=x;break;
    }
    require(found!=null,"pinned ELF section .user_section_uncommon missing");
    require(found.get("address").getAsString().equals("22a180")&&found.get("file_offset").getAsString().equals("12b180")&&found.get("size").getAsString().equals("27f4")&&found.get("flags").getAsInt()==6,"ELF section mapping differs from pinned candidate mapping: "+found);
    return found;
  }
  public void run()throws Exception{
    String[] args=getScriptArgs();require(args.length==3,"outputDir executablePath baselineManifest");
    Path out=Paths.get(args[0]).toAbsolutePath();require(!Files.exists(out),"output directory already exists");Files.createDirectories(out.resolve("functions"));
    Path exe=Paths.get(args[1]).toAbsolutePath(),baseline=Paths.get(args[2]).toAbsolutePath();
    Path scriptPath=Paths.get(getSourceFile().getAbsolutePath());String scriptSha=sha(Files.readAllBytes(scriptPath));
    String normalized=Files.readString(scriptPath).replace(SOURCE_BASIS_SHA,"0000000000000000000000000000000000000000000000000000000000000000");
    require(sha(normalized.getBytes(StandardCharsets.UTF_8)).equals(SOURCE_BASIS_SHA),"candidate script self-hash guard mismatch");
    byte[] elf=readU32Payload(exe);require(sha(elf).equals(EXE_SHA)&&EXE_SHA.equals(currentProgram.getExecutableSHA256()),"PAL executable hash mismatch");
    require("r5900:LE:32:default".equals(currentProgram.getLanguageID().toString()),"program language is not R5900 little-endian");
    require(sha(Files.readAllBytes(baseline)).equals(BASELINE_MANIFEST_SHA),"baseline manifest hash mismatch");
    JsonObject baselineJson=JsonParser.parseString(Files.readString(baseline)).getAsJsonObject();JsonArray baselineRows=baselineJson.getAsJsonArray("functions");require(baselineRows.size()==3837,"expected 3,837 original entries");
    Set<String> baselineEntries=new TreeSet<>();
    for(JsonElement rowElement:baselineRows){JsonObject row=rowElement.getAsJsonObject();require(row.has("entry")&&!row.get("entry").isJsonNull(),"baseline function row lacks an entry");String entry=row.get("entry").getAsString();Address entryAddress=toAddr(entry);require(entryAddress.toString().equals(entry),"baseline entry is not canonical: "+entry);require(baselineEntries.add(entry),"duplicate baseline entry: "+entry);}
    require(baselineEntries.size()==3837,"baseline entry set does not contain 3,837 unique entries");
    Path nativePath=Application.getOSFile("Decompiler","decompile").toPath().toRealPath();require(Files.isRegularFile(nativePath),"native decompiler executable is missing: "+nativePath);String nativeSha=sha(Files.readAllBytes(nativePath));
    JsonObject section=sectionMap(elf);
    Address start=toAddr("0022a180"),last=toAddr("0022a1c7"),endExclusive=toAddr("0022a1c8");
    MemoryBlock block=currentProgram.getMemory().getBlock(start);require(block!=null&&block.getName().equals(".user_section_uncommon")&&block.isInitialized()&&block.isExecute(),"Ghidra loaded section mismatch");
    require(block.getStart().equals(start),"candidate is not at the start of the loaded section");
    byte[] raw=hexBytes(RAW_SPAN);require(raw.length==SPAN_BYTES,"internal raw span size mismatch");
    require(Arrays.equals(Arrays.copyOfRange(elf,FILE_OFFSET,FILE_OFFSET+SPAN_BYTES),raw),"PAL file-offset bytes mismatch");
    require(bytes(start,SPAN_BYTES).equals(RAW_SPAN),"loaded Ghidra bytes differ from raw PAL span");
    require(sha(raw).equals("c5a281fb5648f92c515ee4e524f9b7b6514add1f3d162237ca78c54094b0f7a9"),"span hash mismatch");
    FunctionManager fm=currentProgram.getFunctionManager();Map<String,String> beforeBodies=new TreeMap<>();
    for(Function f:fm.getFunctions(true)){StringBuilder ranges=new StringBuilder();AddressRangeIterator it=f.getBody().getAddressRanges();while(it.hasNext()){AddressRange r=it.next();ranges.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}beforeBodies.put(f.getEntryPoint().toString(),ranges.toString());}
    require(beforeBodies.size()==3837,"unexpected baseline function count");require(beforeBodies.keySet().equals(baselineEntries),"pre-candidate Ghidra function-entry set differs from pinned baseline manifest");
    Map<String,String> beforeInstructions=instructionMap();Map<String,String> beforeData=dataMap();String beforeMemory=memoryHash();
    require(fm.getFunctionAt(start)==null,"function already exists at candidate entry");
    for(int off=0;off<SPAN_BYTES;off++)require(fm.getFunctionContaining(start.add(off))==null,"candidate span overlaps prior function at "+start.add(off));
    JsonObject neighborsBefore=new JsonObject();
    for(Address a:new Address[]{start.subtract(4),start,endExclusive,endExclusive.add(4)}){String owner=ownerAt(a,fm);neighborsBefore.addProperty(a.toString(),owner);}
    JsonObject entryRefsBefore=refsAt(start);
    JsonArray startRefs=entryRefsBefore.getAsJsonArray("references");
    require(startRefs.size()==1,"candidate must retain the one observed non-code ELF metadata reference at section start");
    JsonObject startRef=startRefs.get(0).getAsJsonObject();
    require("_elfSectionHeaders::00000264".equals(startRef.get("from").getAsString())&&"DATA".equals(startRef.get("type").getAsString())&&"IMPORTED".equals(startRef.get("source").getAsString()),"candidate incoming reference is not the pinned ELF-section-header DATA reference");
    JsonArray instructionRows=new JsonArray();
    for(int off=0;off<SPAN_BYTES;off+=4){Address a=start.add(off);Instruction ins=currentProgram.getListing().getInstructionAt(a);require(ins!=null&&ins.getLength()==4,"expected existing 4-byte instruction missing at "+a);require(bytes(a,4).equals(RAW_SPAN.substring(off*2,off*2+8)),"instruction/raw-word mismatch at "+a);JsonObject row=new JsonObject();row.addProperty("address",a.toString());row.addProperty("instruction",ins.toString());row.addProperty("bytes",bytes(a,4));instructionRows.add(row);}
    require(currentProgram.getListing().getInstructionContaining(last).getAddress().equals(toAddr("0022a1c4")),"last word is not the jr delay-slot instruction");
    AddressSet body=new AddressSet(start,last);require(body.getNumAddresses()==SPAN_BYTES,"candidate body range size mismatch");
    Function candidate=fm.createFunction("candidate_leaf_0022a180",start,body,SourceType.ANALYSIS);
    require(candidate!=null&&candidate.getEntryPoint().equals(start),"FunctionManager did not create candidate at exact entry");
    require(candidate.getBody().getNumAddresses()==SPAN_BYTES&&candidate.getBody().contains(start)&&candidate.getBody().contains(last),"candidate function body differs from exact 72-byte span");
    for(int off=0;off<SPAN_BYTES;off+=4)require(candidate.getBody().contains(start.add(off)),"candidate body missing instruction "+start.add(off));
    Map<String,String> afterBodies=new TreeMap<>();for(Function f:fm.getFunctions(true)){StringBuilder ranges=new StringBuilder();AddressRangeIterator it=f.getBody().getAddressRanges();while(it.hasNext()){AddressRange r=it.next();ranges.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}afterBodies.put(f.getEntryPoint().toString(),ranges.toString());}
    require(afterBodies.size()==beforeBodies.size()+1&&afterBodies.containsKey(start.toString()),"entry count did not increase by exactly one candidate");
    for(Map.Entry<String,String> e:beforeBodies.entrySet())require(e.getValue().equals(afterBodies.get(e.getKey())),"an original function body changed at "+e.getKey());
    require(beforeInstructions.equals(instructionMap()),"instruction listing changed; this candidate must not disassemble or alter existing instructions");
    require(beforeData.equals(dataMap()),"defined data code units changed");require(beforeMemory.equals(memoryHash()),"initialized program memory changed");
    JsonObject entryRefsAfter=refsAt(start);require(entryRefsBefore.toString().equals(entryRefsAfter.toString()),"creating the candidate changed references to its entry");
    JsonObject neighborsAfter=new JsonObject();
    for(Address a:new Address[]{start.subtract(4),start,endExclusive,endExclusive.add(4)}){String owner=ownerAt(a,fm);neighborsAfter.addProperty(a.toString(),owner);}
    require(ownerAt(start,fm).equals(start.toString())&&ownerAt(last,fm).equals(start.toString()),"candidate ownership missing at body endpoints");
    for(Address a:new Address[]{start.subtract(4),endExclusive,endExclusive.add(4)})require(Objects.equals(neighborsBefore.get(a.toString()).isJsonNull()?null:neighborsBefore.get(a.toString()).getAsString(),ownerAt(a,fm)),"neighbor ownership changed at "+a);
    String c=decompile(candidate);byte[] cBytes=c.getBytes(StandardCharsets.UTF_8);Files.write(out.resolve("functions/candidate_leaf_0022a180.c"),cBytes,StandardOpenOption.CREATE_NEW);
    JsonArray inventoryRows=new JsonArray();
    for(Function f:fm.getFunctions(true)){JsonObject row=new JsonObject();row.addProperty("entry",f.getEntryPoint().toString());row.addProperty("name",f.getName());row.addProperty("body_bytes",f.getBody().getNumAddresses());row.addProperty("source_type",f.getSymbol().getSource().toString());row.addProperty("provisional_candidate",f.getEntryPoint().equals(start));inventoryRows.add(row);}
    JsonObject inventory=new JsonObject();inventory.addProperty("schema_version",1);inventory.addProperty("executable_sha256",EXE_SHA);inventory.addProperty("language",currentProgram.getLanguageID().toString());inventory.addProperty("original_entry_count",beforeBodies.size());inventory.addProperty("inventory_count_after",afterBodies.size());inventory.add("functions",inventoryRows);inventory.addProperty("claim_limits","Local scratch inventory with one explicitly provisional function candidate; original function identity and reachability are unproved.");
    Files.writeString(out.resolve("inventory.json"),new GsonBuilder().setPrettyPrinting().create().toJson(inventory)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    JsonObject manifest=new JsonObject();manifest.addProperty("schema_version",1);manifest.addProperty("status","provisional-static-candidate");manifest.addProperty("program",currentProgram.getName());manifest.addProperty("language",currentProgram.getLanguageID().toString());manifest.addProperty("ghidra_version",getGhidraVersion());manifest.addProperty("native_decompiler_path",nativePath.toString());manifest.addProperty("native_decompiler_sha256",nativeSha);manifest.addProperty("executable_sha256",EXE_SHA);manifest.addProperty("script_sha256",scriptSha);manifest.addProperty("source_basis_sha256",SOURCE_BASIS_SHA);manifest.addProperty("baseline_manifest_sha256",BASELINE_MANIFEST_SHA);manifest.addProperty("original_entry_count",beforeBodies.size());manifest.addProperty("inventory_entry_count_after",afterBodies.size());manifest.addProperty("candidate_entry","0022a180");manifest.addProperty("candidate_name",candidate.getName());manifest.addProperty("candidate_source_type","ANALYSIS");manifest.addProperty("candidate_body_start","0022a180");manifest.addProperty("candidate_body_end_inclusive","0022a1c7");manifest.addProperty("candidate_body_bytes",candidate.getBody().getNumAddresses());manifest.addProperty("candidate_is_original_identity",false);manifest.addProperty("candidate_runtime_reachability","unproved; no direct call/branch or aligned file-backed pointer found; one imported ELF-section-header DATA reference targets the section start");manifest.addProperty("section_file_mapping_verified",true);manifest.add("elf_section",section);manifest.addProperty("pal_file_offset","0012b180");manifest.addProperty("pal_raw_span_hex",RAW_SPAN);manifest.addProperty("pal_span_sha256",sha(raw));manifest.addProperty("preexisting_listing_instruction_count",beforeInstructions.size());manifest.addProperty("post_candidate_listing_instruction_count",beforeInstructions.size());manifest.addProperty("instruction_listing_unchanged",true);manifest.addProperty("defined_data_units_unchanged",true);manifest.addProperty("initialized_memory_sha256_before",beforeMemory);manifest.addProperty("initialized_memory_sha256_after",memoryHash());manifest.add("candidate_instructions",instructionRows);manifest.add("neighbor_owners_before",neighborsBefore);manifest.add("neighbor_owners_after",neighborsAfter);manifest.add("incoming_entry_reference",entryRefsAfter);manifest.addProperty("original_function_bodies_unchanged",true);manifest.addProperty("original_entry_set_unchanged_except_candidate_addition",true);manifest.addProperty("candidate_c_sha256",sha(cBytes));manifest.addProperty("candidate_c_bytes",cBytes.length);manifest.addProperty("claim_limits","Provisional entry/body hypothesis only; not an original symbol/name, call-site recovery, runtime-use claim, renderer contract, or whole-game source equivalence.");
    Files.writeString(out.resolve("manifest.json"),new GsonBuilder().setPrettyPrinting().create().toJson(manifest)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    println("PROVISIONAL_LEAF_OK entry=0022a180 bytes=72 original_entries=3837 new_entries="+fm.getFunctionCount()+" listing_unchanged=true memory_unchanged=true");
  }
  byte[] hexBytes(String h){byte[] b=new byte[h.length()/2];for(int i=0;i<b.length;i++)b[i]=(byte)Integer.parseInt(h.substring(i*2,i*2+2),16);return b;}
}
