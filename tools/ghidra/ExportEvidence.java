// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.address.*;
import ghidra.program.model.block.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Read-only complete inventory; no decompiler or Python provider required. */
public class ExportEvidence extends GhidraScript {
    private String functionAt(Address a) {
        Function f = currentProgram.getFunctionManager().getFunctionContaining(a);
        return f == null ? null : f.getEntryPoint().toString();
    }
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected output JSON path");
        JsonObject root = new JsonObject();
        root.addProperty("schema_version", 1);
        root.addProperty("program", currentProgram.getName());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("ghidra_version", getGhidraVersion());
        root.addProperty("decompiler", "not used; native availability independent of disassembly");
        JsonArray memory = new JsonArray();
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            JsonObject o = new JsonObject();
            o.addProperty("name", b.getName()); o.addProperty("start", b.getStart().toString());
            o.addProperty("end", b.getEnd().toString()); o.addProperty("size", b.getSize());
            o.addProperty("execute", b.isExecute()); o.addProperty("initialized", b.isInitialized()); memory.add(o);
        }
        root.add("memory", memory);
        JsonArray functions = new JsonArray();
        FunctionManager fm = currentProgram.getFunctionManager();
        root.addProperty("inventory_count", fm.getFunctionCount());
        BasicBlockModel bm = new BasicBlockModel(currentProgram);
        for (Function f : fm.getFunctions(true)) {
            monitor.checkCancelled();
            JsonObject o = new JsonObject();
            o.addProperty("entry", f.getEntryPoint().toString()); o.addProperty("name", f.getName());
            o.addProperty("size", f.getBody().getNumAddresses());
            JsonArray callers = new JsonArray(), callees = new JsonArray(), instructions = new JsonArray(), blocks = new JsonArray();
            for (Function c : f.getCallingFunctions(monitor)) callers.add(c.getEntryPoint().toString());
            for (Function c : f.getCalledFunctions(monitor)) callees.add(c.getEntryPoint().toString());
            CodeBlockIterator bi = bm.getCodeBlocksContaining(f.getBody(), monitor);
            while (bi.hasNext()) {
                CodeBlock b = bi.next(); JsonObject v = new JsonObject();
                v.addProperty("start", b.getMinAddress().toString()); v.addProperty("end", b.getMaxAddress().toString()); blocks.add(v);
            }
            for (Instruction ins : currentProgram.getListing().getInstructions(f.getBody(), true)) {
                JsonObject v = new JsonObject(); v.addProperty("address", ins.getAddress().toString());
                v.addProperty("text", ins.toString());
                StringBuilder bytes = new StringBuilder(); for (byte b : ins.getBytes()) bytes.append(String.format("%02x", b & 255));
                v.addProperty("bytes", bytes.toString()); JsonArray refs = new JsonArray();
                for (Reference r : ins.getReferencesFrom()) {
                    JsonObject ref = new JsonObject(); ref.addProperty("to", r.getToAddress().toString());
                    ref.addProperty("type", r.getReferenceType().toString()); ref.addProperty("function", functionAt(r.getToAddress())); refs.add(ref);
                }
                v.add("references", refs); instructions.add(v);
            }
            o.add("callers", callers); o.add("callees", callees); o.add("blocks", blocks); o.add("instructions", instructions); functions.add(o);
        }
        root.add("functions", functions);
        JsonArray data = new JsonArray();
        for (Data d : currentProgram.getListing().getDefinedData(true)) {
            if (!d.hasStringValue()) continue;
            JsonObject o = new JsonObject(); o.addProperty("address", d.getAddress().toString());
            o.addProperty("value", String.valueOf(d.getValue())); JsonArray refs = new JsonArray();
            for (Reference r : getReferencesTo(d.getAddress())) {
                JsonObject v = new JsonObject(); v.addProperty("from", r.getFromAddress().toString());
                v.addProperty("function", functionAt(r.getFromAddress())); v.addProperty("type", r.getReferenceType().toString()); refs.add(v);
            }
            o.add("references", refs); data.add(o);
        }
        root.add("strings", data);
        Path out = Paths.get(args[0]); Files.createDirectories(out.toAbsolutePath().getParent());
        Files.writeString(out, new GsonBuilder().setPrettyPrinting().create().toJson(root) + "\n", StandardCharsets.UTF_8);
        println("EVIDENCE_EXPORT_OK functions=" + functions.size() + " inventory=" + fm.getFunctionCount());
    }
}
