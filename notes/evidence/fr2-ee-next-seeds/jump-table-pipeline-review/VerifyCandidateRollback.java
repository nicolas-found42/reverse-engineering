//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class VerifyCandidateRollback extends GhidraScript {
    private String hex(long a){return String.format(Locale.ROOT,"%08x",a);}
    private String sha(byte[] b)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}
    private String digest(Object o)throws Exception{return sha(new Gson().toJson(o).getBytes(StandardCharsets.UTF_8));}
    private String ref(Reference r){return hex(r.getFromAddress().getOffset())+"|"+hex(r.getToAddress().getOffset())+"|"+r.getReferenceType()+"|"+r.getSource();}
    public void run()throws Exception{
        String[] args=getScriptArgs();JsonObject expected=JsonParser.parseString(Files.readString(Paths.get(args[0]))).getAsJsonObject();
        Map<String,String> functions=new TreeMap<>(),instructions=new TreeMap<>(),data=new TreeMap<>();Set<String> references=new TreeSet<>();
        for(Function f:currentProgram.getFunctionManager().getFunctions(true)){
            StringBuilder value=new StringBuilder(f.getName()).append('|').append(f.getSymbol().getSource()).append('|');
            AddressRangeIterator it=f.getBody().getAddressRanges();while(it.hasNext()){AddressRange r=it.next();value.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}
            functions.put(hex(f.getEntryPoint().getOffset()),value.toString());
        }
        for(Instruction i:currentProgram.getListing().getInstructions(true)){
            byte[] bytes=new byte[i.getLength()];currentProgram.getMemory().getBytes(i.getAddress(),bytes);
            instructions.put(hex(i.getAddress().getOffset()),i.toString()+"|"+HexFormat.of().formatHex(bytes));
            for(Reference r:i.getReferencesFrom())references.add(ref(r));
        }
        for(Data d:currentProgram.getListing().getDefinedData(true)){
            data.put(hex(d.getAddress().getOffset()),d.getLength()+":"+d.getDataType().getPathName());
            for(Reference r:d.getReferencesFrom())references.add(ref(r));
        }
        MessageDigest memory=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[65536];
        for(MemoryBlock block:currentProgram.getMemory().getBlocks())if(block.isInitialized()){
            memory.update(block.getName().getBytes(StandardCharsets.UTF_8));memory.update(block.getStart().toString().getBytes(StandardCharsets.UTF_8));
            long offset=0;while(offset<block.getSize()){int count=(int)Math.min(buf.length,block.getSize()-offset);currentProgram.getMemory().getBytes(block.getStart().add(offset),buf,0,count);memory.update(buf,0,count);offset+=count;}
        }
        JsonObject result=new JsonObject();
        result.addProperty("functions",digest(functions).equals(expected.get("before_functions_sha256").getAsString()));
        result.addProperty("instructions",digest(instructions).equals(expected.get("before_instructions_sha256").getAsString()));
        result.addProperty("data",digest(data).equals(expected.get("before_data_sha256").getAsString()));
        result.addProperty("references",digest(references).equals(expected.get("before_references_sha256").getAsString()));
        result.addProperty("memory",HexFormat.of().formatHex(memory.digest()).equals(expected.get("before_memory_sha256").getAsString()));
        boolean pass=true;for(Map.Entry<String,JsonElement> e:result.entrySet())pass&=e.getValue().getAsBoolean();
        result.addProperty("status",pass?"pass":"fail");result.addProperty("function_count",functions.size());
        Files.writeString(Paths.get(args[1]),new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n");
        if(!pass)throw new IllegalStateException("rollback snapshot differs after reopening");
    }
}
