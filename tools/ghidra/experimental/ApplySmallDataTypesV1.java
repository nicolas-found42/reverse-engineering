//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.lang.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * Experimental guarded small-data typing (V1). One transaction applies a SHA-pinned plan that gives scalar data types to
 * gp-relative globals and may mark literal-pool (.lit4) items constant through Ghidra's per-data mutability setting. It needs the gp
 * context from SetGpContextV1 at every function entry. An entry is applied only where the listing holds no instruction and
 * no defined data other than undefined bytes; an entry that meets other data is reported and left alone. Afterwards every
 * function's entry, body, name, comment and instruction count must be unchanged, instruction and symbol counts must be
 * unchanged, every applied address must hold the planned type and mutability, and no memory block flag may change; any drift
 * rolls the transaction back. No identity claim is made.
 */
public class ApplySmallDataTypesV1 extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String LANGUAGE = "r5900:LE:32:default";
    private static final long GP = 0x295d70L;

    private void req(boolean ok, String message) { if (!ok) throw new IllegalStateException(message); }
    private String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private Address at(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
    private String hex(long v) { return String.format("%08x", v); }

    private static DataType type(String name) {
        switch (name) {
            case "float": return new FloatDataType(); case "char": return new CharDataType(); case "uchar": return new UnsignedCharDataType();
            case "short": return new ShortDataType(); case "ushort": return new UnsignedShortDataType();
            default: throw new IllegalArgumentException("unplanned type name " + name);
        }
    }

    private Map<String,String> snapshot() {
        Map<String,String> out = new TreeMap<>(); Listing l = currentProgram.getListing();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            int n = 0; for (Instruction i : l.getInstructions(f.getBody(), true)) n++;
            out.put(hex(f.getEntryPoint().getOffset()), f.getName() + "|" + f.getBody() + "|" + n + "|" + f.getComment());
        }
        return out;
    }

    private long[] counts() {
        Listing l = currentProgram.getListing();
        return new long[] { l.getNumInstructions(), currentProgram.getSymbolTable().getNumSymbols(), currentProgram.getFunctionManager().getFunctionCount() };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs(); req(args.length == 4, "Expected outputJson, rawElf, planJson, planSha256");
        byte[] elf = Files.readAllBytes(Paths.get(args[1])), planBytes = Files.readAllBytes(Paths.get(args[2]));
        JsonObject out = new JsonObject(); out.addProperty("schema_version", 1); out.addProperty("plan_sha256", sha(planBytes)); out.addProperty("executable_sha256", sha(elf));
        out.addProperty("language", currentProgram.getLanguageID().toString()); out.addProperty("ghidra_version", getGhidraVersion());
        String status = "rejected";
        try {
            req(args[3].equals(sha(planBytes)), "plan hash differs from the supplied pin");
            req(EXE_SHA.equals(sha(elf)) && EXE_SHA.equals(currentProgram.getExecutableSHA256()), "pinned executable identity mismatch");
            req(LANGUAGE.equals(currentProgram.getLanguageID().toString()), "program is not R5900 little-endian");
            JsonObject plan = JsonParser.parseString(new String(planBytes, StandardCharsets.UTF_8)).getAsJsonObject();
            req(plan.get("schema_version").getAsInt() == 1 && "00295d70".equals(plan.get("gp_value").getAsString()), "plan schema or gp pin differs");
            Register gp = currentProgram.getRegister("gp"); ProgramContext ctx = currentProgram.getProgramContext();
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                RegisterValue rv = ctx.getRegisterValue(gp, f.getEntryPoint());
                req(rv != null && rv.hasValue() && rv.getUnsignedValue().longValue() == GP, "gp context missing at " + f.getEntryPoint());
            }
            Memory mem = currentProgram.getMemory(); Listing listing = currentProgram.getListing();
            JsonArray entries = plan.getAsJsonArray("entries");
            List<MemoryBlock> data = new ArrayList<>(); for (String n : new String[] { ".sdata", ".sbss", ".lit4" }) { MemoryBlock b = mem.getBlock(n); req(b != null, "missing block " + n); data.add(b); }
            Map<String,String> before = snapshot(); long[] countsBefore = counts();
            Map<String,Boolean> writeBefore = new TreeMap<>(); for (MemoryBlock b : mem.getBlocks()) writeBefore.put(b.getName(), b.isWrite());
            List<JsonObject> planned = new ArrayList<>(); Set<String> seen = new HashSet<>();
            for (JsonElement e : entries) {
                JsonObject o = e.getAsJsonObject(); String a = o.get("address").getAsString(); req(seen.add(a), "duplicate plan address " + a);
                Address ad = at(Long.parseUnsignedLong(a, 16)); int size = o.get("size").getAsInt(); type(o.get("type").getAsString());
                boolean inBlock = false; for (MemoryBlock b : data) inBlock |= b.contains(ad) && b.contains(ad.add(size - 1)); req(inBlock, "address outside the small-data blocks: " + a);
                planned.add(o);
            }
            MemoryBlock pool = mem.getBlock(".lit4");
            for (JsonObject o : planned) if (o.has("mutability")) {
                req("constant".equals(o.get("mutability").getAsString()), "unplanned mutability value");
                Address ad = at(Long.parseUnsignedLong(o.get("address").getAsString(), 16)); req(pool.contains(ad), "constant mutability planned outside .lit4");
            }
            int tx = currentProgram.startTransaction("guarded small-data typing of " + planned.size()); boolean commit = false;
            List<String> applied = new ArrayList<>(), conflicts = new ArrayList<>();
            try {
                for (JsonObject o : planned) {
                    String a = o.get("address").getAsString(); Address ad = at(Long.parseUnsignedLong(a, 16)); int size = o.get("size").getAsInt();
                    boolean clear = true;
                    for (int k = 0; k < size; k++) {
                        Address x = ad.add(k);
                        if (listing.getInstructionContaining(x) != null) clear = false;
                        Data d = listing.getDefinedDataContaining(x);
                        if (d != null && !(d.getDataType() instanceof Undefined)) clear = false;
                    }
                    if (!clear) { conflicts.add(a); continue; }
                    listing.clearCodeUnits(ad, ad.add(size - 1), false);
                    Data made = listing.createData(ad, type(o.get("type").getAsString())); applied.add(a);
                    if (o.has("mutability")) MutabilitySettingsDefinition.DEF.setChoice(made, MutabilitySettingsDefinition.CONSTANT);
                }
                Map<String,String> after = snapshot(); req(after.equals(before), "function snapshot changed");
                long[] countsAfter = counts(); req(Arrays.equals(countsBefore, countsAfter), "instruction, symbol or function counts changed");
                for (JsonObject o : planned) {
                    String a = o.get("address").getAsString(); if (conflicts.contains(a)) continue;
                    Data d = listing.getDefinedDataAt(at(Long.parseUnsignedLong(a, 16)));
                    req(d != null && d.getDataType().getName().equals(type(o.get("type").getAsString()).getName()) && d.getLength() == o.get("size").getAsInt(), "type not applied at " + a);
                    int expect = o.has("mutability") ? MutabilitySettingsDefinition.CONSTANT : MutabilitySettingsDefinition.NORMAL;
                    req(MutabilitySettingsDefinition.DEF.getChoice(d) == expect, "mutability not as planned at " + a);
                }
                for (MemoryBlock b : mem.getBlocks()) req(b.isWrite() == writeBefore.get(b.getName()), "memory block write flag changed on " + b.getName());
                commit = true;
            } finally { currentProgram.endTransaction(tx, commit); }
            status = "applied"; out.addProperty("function_count_after", currentProgram.getFunctionManager().getFunctionCount());
            out.addProperty("applied", applied.size()); out.addProperty("conflicts", conflicts.size());
            JsonArray c = new JsonArray(); for (String s : conflicts) c.add(s); out.add("conflict_addresses", c);
            int constants = 0; for (JsonObject o : planned) if (o.has("mutability") && !conflicts.contains(o.get("address").getAsString())) constants++;
            out.addProperty("marked_constant", constants);
        } catch (Throwable t) {
            out.addProperty("failure", t.getClass().getSimpleName() + ": " + t.getMessage());
        } finally {
            out.addProperty("status", status);
            Files.writeString(Paths.get(args[0]), new GsonBuilder().setPrettyPrinting().create().toJson(out) + "\n");
        }
    }
}
