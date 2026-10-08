// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.Reference;
import com.google.gson.*;
import java.nio.file.*;

/** Run only against an isolated project copy; emit metadata, never payload. */
public class ReconcileMisc3dBoundary extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected receipt path");
        FunctionManager fm = currentProgram.getFunctionManager();
        Address raw = toAddr(0x1d1840), old = toAddr(0x1d1844), end = toAddr(0x1d187f);
        Function candidate = fm.getFunctionAt(old);
        if (fm.getFunctionContaining(raw) != null || candidate == null
                || candidate.getBody().getNumAddresses() != 60
                || !candidate.getBody().getMinAddress().equals(old)
                || !candidate.getBody().getMaxAddress().equals(end))
            throw new IllegalStateException("Original ownership contradicts the recorded boundary");
        JsonObject receipt = new JsonObject();
        receipt.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        receipt.addProperty("language", currentProgram.getLanguageID().toString());
        receipt.addProperty("ghidra_version", getGhidraVersion());
        receipt.addProperty("original_entry", old.toString());
        receipt.addProperty("original_bytes", 60);
        receipt.addProperty("raw_load_previously_owned", false);
        JsonArray refs = new JsonArray();
        for (Address destination : new Address[]{raw, old}) {
            for (Reference r : getReferencesTo(destination)) {
                JsonObject row = new JsonObject();
                row.addProperty("from", r.getFromAddress().toString());
                row.addProperty("to", destination.toString());
                row.addProperty("type", r.getReferenceType().toString()); refs.add(row);
            }
        }
        receipt.add("incoming_saved_references", refs);
        fm.removeFunction(old);
        disassemble(raw);
        Function corrected = createFunction(raw, "inferred_misc3d_get_state_cc");
        if (corrected == null) throw new IllegalStateException("Complete flow body unavailable");
        // Creating from the raw load must recover the existing branch and delay-slot return.
        if (!corrected.getBody().getMinAddress().equals(raw)
                || !corrected.getBody().getMaxAddress().equals(end)
                || corrected.getBody().getNumAddresses() != 64)
            throw new IllegalStateException("Recovered flow does not close at the recorded return");
        receipt.addProperty("reconciled_entry", corrected.getEntryPoint().toString());
        receipt.addProperty("reconciled_end_exclusive", "001d1880");
        receipt.addProperty("reconciled_bytes", 64);
        receipt.addProperty("reconciled_instruction_count", 16);
        receipt.addProperty("status", "pass");
        receipt.addProperty("claim_limit", "Structural source-unit candidate; no original symbol or runtime reachability established. Read-only invocation discards this isolated copy's changes.");
        Path output = Paths.get(args[0]); Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output, new GsonBuilder().setPrettyPrinting().create().toJson(receipt) + "\n");
        println("MISC3D_BOUNDARY_RECONCILED entry=" + raw + " bytes=64");
    }
}
