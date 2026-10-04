//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.nio.file.*;

/** Read-only: list every reference into the bytes of each seed span of a batch config (type, source, from, owner). Never starts a transaction. */
public class InspectSeedRefs extends GhidraScript {
    public void run() throws Exception {
        JsonObject c = JsonParser.parseString(Files.readString(Paths.get(getScriptArgs()[0]))).getAsJsonObject();
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace(); ReferenceManager rm = currentProgram.getReferenceManager(); FunctionManager fm = currentProgram.getFunctionManager();
        for (JsonElement se : c.getAsJsonArray("seeds")) {
            JsonObject s = se.getAsJsonObject(); long a = Long.parseUnsignedLong(s.get("start").getAsString(), 16), z = Long.parseUnsignedLong(s.get("end").getAsString(), 16);
            for (long pc = a; pc < z; pc++) for (Reference r : rm.getReferencesTo(sp.getAddress(pc))) {
                Function o = fm.getFunctionContaining(r.getFromAddress()); Instruction fi = currentProgram.getListing().getInstructionAt(r.getFromAddress());
                println("REF seed=" + s.get("entry").getAsString() + " to=" + r.getToAddress() + " from=" + r.getFromAddress() + " type=" + r.getReferenceType() + " source=" + r.getSource() + " fromFunc=" + (o == null ? "none" : o.getName()) + " fromInsn=" + (fi == null ? "none" : fi.toString()));
            }
        }
    }
}
