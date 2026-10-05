//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.lang.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import com.google.gson.*;
import java.math.BigInteger;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * Experimental guarded gp context (V1). One transaction sets the gp register value over every initialized executable block of
 * the default address space. The value is pinned and must equal the ELF .reginfo gp_value read from program memory, and the
 * entry routine's only gp write must load it. Afterwards every function's entry, body, name, comment and instruction count, the
 * total instruction, data and symbol counts, and the function count must be unchanged, and gp must read back as the pinned
 * value at every function entry; any drift rolls the transaction back. No identity claim is made.
 */
public class SetGpContextV1 extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String LANGUAGE = "r5900:LE:32:default";
    private static final long GP = 0x295d70L;

    private void req(boolean ok, String message) { if (!ok) throw new IllegalStateException(message); }
    private String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private String hex(long v) { return String.format("%08x", v); }

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
        return new long[] { l.getNumInstructions(), l.getNumDefinedData(), currentProgram.getSymbolTable().getNumSymbols(),
            currentProgram.getFunctionManager().getFunctionCount() };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs(); req(args.length == 2, "Expected outputJson, rawElf");
        byte[] elf = Files.readAllBytes(Paths.get(args[1]));
        JsonObject out = new JsonObject(); out.addProperty("schema_version", 1); out.addProperty("executable_sha256", sha(elf));
        out.addProperty("language", currentProgram.getLanguageID().toString()); out.addProperty("ghidra_version", getGhidraVersion());
        out.addProperty("gp_value", hex(GP));
        String status = "rejected";
        try {
            req(EXE_SHA.equals(sha(elf)) && EXE_SHA.equals(currentProgram.getExecutableSHA256()), "pinned executable identity mismatch");
            req(LANGUAGE.equals(currentProgram.getLanguageID().toString()), "program is not R5900 little-endian");
            Memory mem = currentProgram.getMemory(); AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
            MemoryBlock reginfo = mem.getBlock(".reginfo"); req(reginfo != null && reginfo.getSize() == 24, ".reginfo block missing or not 24 bytes");
            long recorded = mem.getInt(reginfo.getStart().add(20), false) & 0xffffffffL;
            req(recorded == GP, ".reginfo gp_value " + hex(recorded) + " differs from the pinned gp");
            Function entry = currentProgram.getFunctionManager().getFunctionAt(space.getAddress(0x100008L));
            req(entry != null, "no entry function at 00100008");
            Register gp = currentProgram.getRegister("gp"); req(gp != null, "no gp register in this language");
            int gpWrites = 0; Map<Register,Long> known = new HashMap<>();
            for (Instruction i : currentProgram.getListing().getInstructions(entry.getBody(), true)) {
                String m = i.getMnemonicString(); Register r0 = i.getRegister(0), r1 = i.getRegister(1);
                if ("lui".equals(m) && r0 != null && i.getScalar(1) != null) known.put(r0.getBaseRegister(), (i.getScalar(1).getUnsignedValue() << 16) & 0xffffffffL);
                else if ("addiu".equals(m) && r0 != null && r1 != null && i.getScalar(2) != null && known.containsKey(r1.getBaseRegister()))
                    known.put(r0.getBaseRegister(), (known.get(r1.getBaseRegister()) + i.getScalar(2).getSignedValue()) & 0xffffffffL);
                else if ("move".equals(m) && r0 != null && r0.getBaseRegister().equals(gp.getBaseRegister())) {
                    gpWrites++; Long loaded = r1 == null ? null : known.get(r1.getBaseRegister());
                    req(loaded != null && loaded == GP, "the entry routine's gp move does not load the pinned value");
                }
            }
            req(gpWrites == 1, "entry routine does not have exactly one 'move gp,<reg>'");
            Map<String,String> before = snapshot(); long[] countsBefore = counts();
            ProgramContext ctx = currentProgram.getProgramContext(); BigInteger value = BigInteger.valueOf(GP);
            List<String> blocks = new ArrayList<>(); int tx = currentProgram.startTransaction("guarded gp context " + hex(GP)); boolean commit = false;
            try {
                for (MemoryBlock b : mem.getBlocks())
                    if (b.isExecute() && b.isInitialized() && b.getStart().getAddressSpace().equals(space)) {
                        ctx.setValue(gp, b.getStart(), b.getEnd(), value); blocks.add(b.getName());
                    }
                req(!blocks.isEmpty(), "no executable initialized block was found");
                Map<String,String> after = snapshot(); req(after.equals(before), "function snapshot changed");
                req(Arrays.equals(countsBefore, counts()), "instruction, data, symbol or function counts changed");
                for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                    RegisterValue rv = ctx.getRegisterValue(gp, f.getEntryPoint());
                    req(rv != null && rv.hasValue() && rv.getUnsignedValue().longValue() == GP, "gp not readable as the pinned value at " + f.getEntryPoint());
                }
                commit = true;
            } finally { currentProgram.endTransaction(tx, commit); }
            status = "applied"; out.addProperty("function_count_after", currentProgram.getFunctionManager().getFunctionCount());
            JsonArray names = new JsonArray(); for (String n : blocks) names.add(n); out.add("blocks", names);
        } catch (Throwable t) {
            out.addProperty("failure", t.getClass().getSimpleName() + ": " + t.getMessage());
        } finally {
            out.addProperty("status", status);
            Files.writeString(Paths.get(args[0]), new GsonBuilder().setPrettyPrinting().create().toJson(out) + "\n");
        }
    }
}
