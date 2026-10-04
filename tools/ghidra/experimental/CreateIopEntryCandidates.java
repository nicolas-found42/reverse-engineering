// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Isolated experiment for metadata-declared IOPMOD entry zero. It only creates
 * a provisional function from the existing, already decoded CFG body, and
 * rolls back unless every pre-existing function/body, listing, and memory byte
 * remains unchanged. It never disassembles bytes.
 */
public class CreateIopEntryCandidates extends GhidraScript {
    private static final Map<String, String> INPUTS = new HashMap<>();
    static {
        INPUTS.put("CDVDMAN.irx", "0440edf8b1457ea321a16acace9b33c1ed17ebdd9b74576c76a75ff72aeb17ca");
        INPUTS.put("EESYNC.irx", "0cb97a16720ffa9b147e8e7689cb704de83330e03aaf53fcd719ea46b97ef59e");
        INPUTS.put("FILEIO.irx", "ffe84d90c36c80457fa92facf18ea3891317cd95a27142e594d1e3715b49c824");
        INPUTS.put("IOMAN.irx", "b0b6eff43cedd2176657bfacef75178e75fadc15bcf18984775fb78bb422740c");
        INPUTS.put("LOADCORE.irx", "488187ab52ec98dc6c13ba53601ab016636c678a1469826461a6f8dd041f6b38");
        INPUTS.put("LOADFILE.irx", "12967a07fcb21ed067c19dfc9ed9e67f694594b1e04fd364987260fed541d71f");
        INPUTS.put("MODLOAD.irx", "a2d1d57c78b94d5079206877564d03af7205db99e51a775573a8c0a8428f7519");
        INPUTS.put("ROMDRV.irx", "0aa9eeacc3a400e4f22bef3844c89cfaea516d7dfd89b0fa1bb0e603ecb9ce1a");
        INPUTS.put("SDRDRV.IRX", "b49a26a7f1801689f84e7e4cc92a286eb7e0ba3c3d4fb7855c994e0d20e3afa2");
        INPUTS.put("SIFMAN.irx", "8edc7d0dbf0bfb8669c62544b0c915485ee022794adfdf5270e44d3df4dc05ec");
        INPUTS.put("STDIO.irx", "05051433d89083ff93a6a4399326790f10d8fc2ae90492e65516eb4560289081");
        INPUTS.put("SYSCLIB.irx", "2e3b82ecc6bba3d8c14fb6a55c6d68ecb643de3094305608ecbcd260dd49f447");
        INPUTS.put("TIMEMANI.irx", "95c0df47fabd3e62553b320f88a084ed499df31d50c256a066b5c4937df71a35");
    }

    private String digest(byte[] bytes) throws Exception {
        byte[] hash = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder value = new StringBuilder();
        for (byte b : hash) value.append(String.format("%02x", b & 0xff));
        return value.toString();
    }
    private String blockDigest(MemoryBlock block) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[65536];
        long offset = 0;
        while (offset < block.getSize()) {
            monitor.checkCancelled();
            int length = (int) Math.min(buffer.length, block.getSize() - offset);
            block.getBytes(block.getStart().add(offset), buffer, 0, length);
            md.update(buffer, 0, length);
            offset += length;
        }
        return hex(md.digest());
    }
    private String hex(byte[] bytes) {
        StringBuilder value = new StringBuilder();
        for (byte b : bytes) value.append(String.format("%02x", b & 0xff));
        return value.toString();
    }
    private JsonArray ranges(AddressSetView set) {
        JsonArray out = new JsonArray();
        for (AddressRange r : set.getAddressRanges()) {
            JsonObject row = new JsonObject();
            row.addProperty("start", r.getMinAddress().toString());
            row.addProperty("end", r.getMaxAddress().toString());
            row.addProperty("bytes", r.getLength());
            out.add(row);
        }
        return out;
    }
    private String functionState(FunctionManager fm) {
        StringBuilder text = new StringBuilder();
        for (Function function : fm.getFunctions(true))
            text.append(function.getEntryPoint()).append('|').append(function.getName()).append('|')
                .append(ranges(function.getBody())).append('\n');
        return text.toString();
    }
    private Set<String> functionRows(FunctionManager fm, Address excludeEntry) {
        Set<String> rows = new TreeSet<>();
        for (Function function : fm.getFunctions(true)) {
            if (excludeEntry != null && function.getEntryPoint().equals(excludeEntry)) continue;
            rows.add(function.getEntryPoint() + "|" + function.getName() + "|" + ranges(function.getBody()));
        }
        return rows;
    }
    private JsonArray functionEntries(FunctionManager fm) {
        JsonArray entries = new JsonArray();
        for (Function function : fm.getFunctions(true)) {
            JsonObject row = new JsonObject();
            row.addProperty("entry", function.getEntryPoint().toString());
            row.addProperty("name", function.getName());
            row.addProperty("body_bytes", function.getBody().getNumAddresses());
            row.add("body_ranges", ranges(function.getBody()));
            entries.add(row);
        }
        return entries;
    }
    private JsonObject memoryState() throws Exception {
        JsonObject state = new JsonObject();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            state.addProperty(block.getName() + "@" + block.getStart(), blockDigest(block));
        }
        return state;
    }
    private String listingState() throws Exception {
        Listing listing = currentProgram.getListing();
        StringBuilder text = new StringBuilder();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            AddressSet extent = new AddressSet(block.getStart(), block.getEnd());
            for (Instruction ins : listing.getInstructions(extent, true)) {
                monitor.checkCancelled();
                text.append('I').append(ins.getAddress()).append(':').append(hex(ins.getBytes())).append('\n');
            }
            for (Data data : listing.getDefinedData(extent, true)) {
                monitor.checkCancelled();
                text.append('D').append(data.getAddress()).append(':').append(data.getLength())
                    .append(':').append(data.getDataType().getPathName()).append('\n');
            }
        }
        return digest(text.toString().getBytes(StandardCharsets.UTF_8));
    }
    private long u32(byte[] b, int p) {
        return (b[p] & 255L) | ((b[p+1] & 255L) << 8) | ((b[p+2] & 255L) << 16) | ((b[p+3] & 255L) << 24);
    }
    private int u16(byte[] b, int p) { return (b[p] & 255) | ((b[p+1] & 255) << 8); }
    private JsonObject rawElfProof(Path path, String expectedHash) throws Exception {
        byte[] b = Files.readAllBytes(path);
        if (!digest(b).equals(expectedHash)) throw new IllegalArgumentException("raw ELF SHA-256 differs from pinned executable SHA-256");
        if (b.length < 52 || b[0] != 0x7f || b[1] != 'E' || b[2] != 'L' || b[3] != 'F' ||
            b[4] != 1 || b[5] != 1 || b[6] != 1 || u16(b,16) != 0xff80 || u16(b,18) != 8)
            throw new IllegalArgumentException("raw input is not ELF32 little-endian ET_IOP/EM_MIPS");
        long shoff = u32(b,32); int shentsize = u16(b,46), shnum = u16(b,48), shstrndx = u16(b,50);
        if (shentsize < 40 || shnum == 0 || shstrndx >= shnum || shoff + (long)shentsize*shnum > b.length)
            throw new IllegalArgumentException("raw ELF section table is invalid");
        int namesHdr = Math.toIntExact(shoff + (long)shentsize*shstrndx);
        long namesOff = u32(b,namesHdr+16), namesSize = u32(b,namesHdr+20);
        if (namesOff + namesSize > b.length) throw new IllegalArgumentException("raw ELF section-name table is out of bounds");
        int textOff=-1, textSize=-1, modOff=-1, modSize=-1, textCount=0, modCount=0;
        long textAddr=-1; int textType=-1, textFlags=-1, modType=-1;
        for (int i=0;i<shnum;i++) {
            int h=Math.toIntExact(shoff+(long)shentsize*i); long no=u32(b,h);
            if (no >= namesSize) throw new IllegalArgumentException("raw ELF section name offset is invalid");
            int ns=Math.toIntExact(namesOff+no), ne=ns; while(ne < namesOff+namesSize && b[ne]!=0) ne++;
            String name=new String(b,ns,ne-ns,StandardCharsets.US_ASCII);
            int type=(int)u32(b,h+4); long flags=u32(b,h+8), addr=u32(b,h+12), off=u32(b,h+16), size=u32(b,h+20);
            if (name.equals(".text")) { textCount++; textOff=Math.toIntExact(off); textSize=Math.toIntExact(size); textAddr=addr; textType=type; textFlags=(int)flags; }
            if (name.equals(".iopmod")) { modCount++; modOff=Math.toIntExact(off); modSize=Math.toIntExact(size); modType=type; }
        }
        if (textCount!=1 || modCount!=1 || textType!=1 || (textFlags & 4)==0 || textAddr!=0 ||
            textOff<0 || textSize<0 || (long)textOff+textSize>b.length || modType!=0x70000080 || modSize<27 ||
            (long)modOff+modSize>b.length)
            throw new IllegalArgumentException("raw ELF .text/.iopmod section profile is invalid");
        long entry=u32(b,modOff+4), declaredText=u32(b,modOff+12);
        if (entry>=textSize || (entry&3)!=0 || declaredText!=textSize) throw new IllegalArgumentException("raw ELF .iopmod entry/text-size metadata mismatch");
        JsonObject proof=new JsonObject(); proof.addProperty("path",path.toAbsolutePath().toString()); proof.addProperty("sha256",digest(b));
        proof.addProperty("elf_type","0xff80"); proof.addProperty("machine",8); proof.addProperty("text_address",textAddr);
        proof.addProperty("text_file_offset",textOff); proof.addProperty("text_size",textSize); proof.addProperty("text_sha256",digest(Arrays.copyOfRange(b,textOff,textOff+textSize)));
        proof.addProperty("iopmod_section_type",String.format("0x%08x",modType)); proof.addProperty("iopmod_entry_address",entry);
        proof.addProperty("iopmod_text_bytes",declaredText); return proof;
    }
    private MemoryBlock checkedTextBlock(JsonObject proof) throws Exception {
        MemoryBlock text=null;
        for (MemoryBlock block:currentProgram.getMemory().getBlocks()) if (block.getName().equals(".text")) {
            if (text!=null) throw new IllegalArgumentException("multiple Ghidra .text blocks"); text=block;
        }
        if (text==null || !text.isInitialized() || !text.isExecute() || text.getStart().getOffset()!=0 ||
            text.getSize()!=proof.get("text_size").getAsLong() || !blockDigest(text).equals(proof.get("text_sha256").getAsString()))
            throw new IllegalArgumentException("Ghidra .text is not executable, base-zero, exact-size/hash raw ELF .text");
        return text;
    }
    private boolean insideText(AddressSetView body, long textSize) {
        if (body.isEmpty()) return false;
        for (AddressRange r:body.getAddressRanges()) if (r.getMinAddress().getOffset()<0 || r.getMaxAddress().getOffset()>=textSize) return false;
        return true;
    }
    private boolean sameJson(JsonObject a, JsonObject b) { return a.toString().equals(b.toString()); }

    public void run() throws Exception {
        if (getScriptArgs().length != 2) throw new IllegalArgumentException("Expected fresh result JSON path and raw ELF input path");
        String programName = currentProgram.getName();
        String expectedHash = INPUTS.get(programName);
        JsonObject result = new JsonObject();
        result.addProperty("program", programName);
        result.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        result.addProperty("language", currentProgram.getLanguageID().toString());
        result.addProperty("ghidra_version", getGhidraVersion());
        result.addProperty("compiler_spec", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        JsonObject rawProof = null; String guardError = null;
        try {
            if (!"MIPS:LE:32:default".equals(currentProgram.getLanguageID().toString())) throw new IllegalArgumentException("Ghidra language is not MIPS:LE:32:default");
            if (!"default".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString())) throw new IllegalArgumentException("Ghidra compiler spec is not default");
            rawProof = rawElfProof(Paths.get(getScriptArgs()[1]), expectedHash);
            if (rawProof.get("iopmod_entry_address").getAsLong()!=0) throw new IllegalArgumentException("raw ELF .iopmod entry is not address zero");
            checkedTextBlock(rawProof);
        } catch (Exception e) { guardError=e.getMessage(); }
        result.add("raw_elf_metadata_proof", rawProof);
        result.addProperty("method", "CreateFunctionCmd with existing CFG-computed body from already defined instructions; no disassembly; provisional ANALYSIS source");
        result.addProperty("claim_limits", "This experiment tests a metadata-declared entrypoint and a CFG-derived candidate extent only. It does not establish runtime invocation, original symbol/name, correct function extent, or source semantics.");
        if (expectedHash == null || !expectedHash.equals(currentProgram.getExecutableSHA256())) {
            result.addProperty("status", "rejected_input_identity");
        } else if (guardError != null) {
            result.addProperty("status", "rejected_profile_guard"); result.addProperty("guard_error", guardError);
        } else {
            FunctionManager fm = currentProgram.getFunctionManager();
            Listing listing = currentProgram.getListing();
            Address entry = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0);
            Function existing = fm.getFunctionAt(entry);
            result.addProperty("before_function_count", fm.getFunctionCount());
            result.add("before_functions_sha256", new JsonPrimitive(digest(functionState(fm).getBytes(StandardCharsets.UTF_8))));
            result.add("before_functions", functionEntries(fm));
            result.add("before_memory", memoryState());
            result.addProperty("before_listing_sha256", listingState());
            Instruction first = listing.getInstructionAt(entry);
            result.addProperty("entry_instruction_exists", first != null);
            if (first != null) {
                result.addProperty("entry_instruction", first.toString());
                result.addProperty("entry_instruction_bytes", hex(first.getBytes()));
            }
            if (existing != null) {
                result.addProperty("status", "already_has_saved_function");
            } else if (first == null || fm.getFunctionContaining(entry) != null) {
                result.addProperty("status", "rejected_entry_not_unowned_instruction");
            } else {
                AddressSetView body = CreateFunctionCmd.getFunctionBody(currentProgram, entry, monitor);
                result.add("proposed_body_ranges", ranges(body));
                result.addProperty("proposed_body_bytes", body.getNumAddresses());
                AddressSet bodyInstructions = new AddressSet();
                for (Instruction ins : listing.getInstructions(body, true)) {
                    monitor.checkCancelled();
                    bodyInstructions.addRange(ins.getAddress(), ins.getMaxAddress());
                }
                result.addProperty("proposed_body_instruction_bytes", bodyInstructions.getNumAddresses());
                AddressSet bodyWithoutInstructions = body.subtract(bodyInstructions);
                AddressSet instructionsOutsideBody = bodyInstructions.subtract(body);
                boolean exactInstructionSet = bodyWithoutInstructions.isEmpty() && instructionsOutsideBody.isEmpty();
                result.addProperty("candidate_body_exactly_equals_existing_instruction_addresses", exactInstructionSet);
                result.add("candidate_body_uncovered_ranges", ranges(bodyWithoutInstructions));
                result.add("instruction_addresses_outside_candidate_body", ranges(instructionsOutsideBody));
                boolean overlaps = false;
                JsonArray collisions = new JsonArray();
                for (Function f : fm.getFunctions(true)) {
                    AddressSetView overlap = f.getBody().intersect(body);
                    if (!overlap.isEmpty()) {
                        overlaps = true;
                        JsonObject item = new JsonObject();
                        item.addProperty("entry", f.getEntryPoint().toString());
                        item.addProperty("name", f.getName());
                        item.add("overlap_ranges", ranges(overlap));
                        collisions.add(item);
                    }
                }
                result.add("existing_body_collisions", collisions);
                if (body.isEmpty() || !insideText(body, rawProof.get("text_size").getAsLong()) || !body.contains(entry) || overlaps ||
                    !exactInstructionSet) {
                    result.addProperty("status", "rejected_body_empty_or_conflicting");
                } else {
                    JsonObject beforeMemory = memoryState();
                    String beforeListing = listingState();
                    int tx = currentProgram.startTransaction("isolated IOPMOD declared entry candidate");
                    boolean commit = false;
                    try {
                        Set<String> originalRows = functionRows(fm, null);
                        String candidateName = "IOPMOD_ENTRY_00000000_PROVISIONAL";
                        CreateFunctionCmd command = new CreateFunctionCmd(candidateName, entry, body, SourceType.ANALYSIS);
                        if (!command.applyTo(currentProgram, monitor))
                            throw new IllegalStateException("CreateFunctionCmd failed: " + command.getStatusMsg());
                        Function created = fm.getFunctionAt(entry);
                        if (created == null || !created.getBody().equals(body))
                            throw new IllegalStateException("created function body did not equal precomputed body");
                        if (created.getSymbol().getSource() != SourceType.ANALYSIS)
                            throw new IllegalStateException("created function source was not ANALYSIS");
                        if (fm.getFunctionCount() != result.get("before_function_count").getAsInt() + 1)
                            throw new IllegalStateException("function inventory delta was not exactly +1");
                        if (!originalRows.equals(functionRows(fm, entry)))
                            throw new IllegalStateException("pre-existing function entry/name/body set changed");
                        if (!sameJson(beforeMemory, memoryState())) throw new IllegalStateException("memory bytes changed");
                        if (!beforeListing.equals(listingState())) throw new IllegalStateException("defined listing changed");
                        result.addProperty("created_name", created.getName());
                        result.add("created_body_ranges", ranges(created.getBody()));
                        result.addProperty("created_body_bytes", created.getBody().getNumAddresses());
                        result.addProperty("after_function_count", fm.getFunctionCount());
                        result.add("after_functions", functionEntries(fm));
                        result.add("after_memory", memoryState());
                        result.addProperty("after_listing_sha256", listingState());
                        result.addProperty("status", "created_guarded_provisional_candidate");
                        commit = true;
                    } finally {
                        currentProgram.endTransaction(tx, commit);
                    }
                }
            }
        }
        Path path = Paths.get(getScriptArgs()[0]);
        Files.createDirectories(path.toAbsolutePath().getParent());
        Files.writeString(path, new GsonBuilder().setPrettyPrinting().create().toJson(result) + "\n",
            StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        println("IOP_ENTRY_EXPERIMENT program=" + programName + " status=" + result.get("status"));
    }
}
