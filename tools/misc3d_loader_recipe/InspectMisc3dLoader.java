// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.Reference;
import com.google.gson.*;
import java.nio.file.*;

/** Metadata-only, isolated read-only saved-project observation. */
public class InspectMisc3dLoader extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected output path");
        JsonObject root = new JsonObject();
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("ghidra_version", getGhidraVersion());
        JsonArray functions = new JsonArray();
        for (long entry : new long[]{0x1d1408,0x11ed90,0x124f58,0x125068}) {
            Function f = currentProgram.getFunctionManager().getFunctionAt(toAddr(entry));
            if (f == null) throw new IllegalStateException("Required saved function missing");
            JsonObject row = new JsonObject(); row.addProperty("entry", f.getEntryPoint().toString());
            row.addProperty("bytes", f.getBody().getNumAddresses());
            JsonArray ranges = new JsonArray();
            AddressRangeIterator it = f.getBody().getAddressRanges();
            while (it.hasNext()) {
                AddressRange range = it.next(); JsonObject r = new JsonObject();
                r.addProperty("start", range.getMinAddress().toString());
                r.addProperty("end_exclusive", range.getMaxAddress().next().toString());
                ranges.add(r);
            }
            row.add("ranges", ranges); JsonArray refs = new JsonArray();
            for (Reference ref : getReferencesTo(f.getEntryPoint())) {
                JsonObject r = new JsonObject(); r.addProperty("from", ref.getFromAddress().toString());
                r.addProperty("type", ref.getReferenceType().toString()); refs.add(r);
            }
            row.add("incoming", refs); functions.add(row);
        }
        root.add("functions", functions); root.addProperty("status", "pass");
        root.addProperty("limit", "Saved function metadata only; no ownership, execution or complete alias proof.");
        Path out=Paths.get(args[0]); Files.createDirectories(out.toAbsolutePath().getParent());
        Files.writeString(out,new GsonBuilder().setPrettyPrinting().create().toJson(root)+"\n");
        println("MISC3D_LOADER_METADATA_PASS");
    }
}
