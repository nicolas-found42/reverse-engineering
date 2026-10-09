// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import com.google.gson.*;
import java.nio.file.*;

/** Read-only reference metadata for every scoped instruction and data byte. */
public class InspectMisc3dAliases extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected output path");
        JsonObject root = new JsonObject();
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("ghidra_version", getGhidraVersion());
        JsonArray domains = new JsonArray();
        long[][] ranges = {{0x12c218,0x12c220},{0x1d1408,0x1d143c},
            {0x1d1440,0x1d157c},{0x1d1580,0x1d15b4},{0x1d15b8,0x1d15cc},
            {0x1d15d0,0x1d1628},{0x1d1628,0x1d17a8},{0x1d17a8,0x1d183c},
            {0x1d1840,0x1d1880},{0x1d1880,0x1d18c0},{0x1d18c0,0x1d1900},
            {0x290ac4,0x290ad8}};
        for (long[] range : ranges) {
            JsonObject domain = new JsonObject();
            domain.addProperty("start", String.format("%08x", range[0]));
            domain.addProperty("end_exclusive", String.format("%08x", range[1]));
            JsonArray references = new JsonArray();
            for (long address = range[0]; address < range[1]; address++) {
                for (Reference ref : getReferencesTo(toAddr(address))) {
                    JsonObject r = new JsonObject();
                    r.addProperty("from", ref.getFromAddress().toString());
                    r.addProperty("to", ref.getToAddress().toString());
                    r.addProperty("type", ref.getReferenceType().toString());
                    Function owner = getFunctionContaining(ref.getFromAddress());
                    if (owner != null) r.addProperty("saved_owner", owner.getEntryPoint().toString());
                    references.add(r);
                }
            }
            domain.add("incoming", references); domains.add(domain);
        }
        root.add("domains", domains);
        JsonArray related = new JsonArray();
        for (long entry : new long[]{0x108bf0,0x108d5c,0x108de4,0x108efc,
                0x10cdc8,0x175788,0x176300,0x1763a0,0x178650,0x17f700,0x1cc018}) {
            JsonObject row = new JsonObject();
            row.addProperty("entry", String.format("%08x", entry));
            JsonArray refs = new JsonArray();
            for (Reference ref : getReferencesTo(toAddr(entry))) {
                JsonObject r = new JsonObject();
                r.addProperty("from", ref.getFromAddress().toString());
                r.addProperty("type", ref.getReferenceType().toString());
                refs.add(r);
            }
            row.add("incoming", refs); related.add(row);
        }
        root.add("related_entry_incoming", related);
        JsonArray sums = new JsonArray(), unownedConstructors = new JsonArray();
        JsonArray unlistedConstructors = new JsonArray(), unlistedSums = new JsonArray();
        int constructorCount = 0;
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized() || !block.isExecute()) continue;
            for (long offset = 0; offset + 4 <= block.getSize(); offset += 4) {
                Address site = block.getStart().add(offset);
                int word = currentProgram.getMemory().getInt(site);
                int rs = (word >>> 21) & 31, rt = (word >>> 16) & 31;
                int rd = (word >>> 11) & 31, function = word & 63;
                int opcode = word >>> 26;
                if (rs == 28 && (opcode == 8 || opcode == 9 || opcode == 24 || opcode == 25)) {
                    constructorCount++;
                    if (getFunctionContaining(site) == null) unownedConstructors.add(site.toString());
                    if (getInstructionAt(site) == null) unlistedConstructors.add(site.toString());
                }
                if ((word >>> 26) != 0 || rd == 0 || (rs != 28 && rt != 28)
                        || (function != 32 && function != 33 && function != 44 && function != 45)) continue;
                JsonObject row = new JsonObject();
                row.addProperty("site", site.toString());
                if (getInstructionAt(site) == null) unlistedSums.add(site.toString());
                Function owner = getFunctionContaining(site);
                if (owner != null) row.addProperty("saved_owner", owner.getEntryPoint().toString());
                sums.add(row);
            }
        }
        root.add("gp_sum_saved_context", sums);
        root.add("gp_sum_unlisted_sites", unlistedSums);
        JsonObject constructors = new JsonObject();
        constructors.addProperty("candidate_count", constructorCount);
        constructors.add("unowned_sites", unownedConstructors);
        constructors.add("unlisted_sites", unlistedConstructors);
        root.add("gp_constructor_saved_context", constructors);
        root.addProperty("status", "pass");
        root.addProperty("limit", "All saved incoming references to scoped bytes; no execution or computed alias closure.");
        Path out = Paths.get(args[0]);
        Files.createDirectories(out.toAbsolutePath().getParent());
        Files.writeString(out, new GsonBuilder().setPrettyPrinting().create().toJson(root)+"\n");
        println("MISC3D_ALIAS_METADATA_PASS");
    }
}
