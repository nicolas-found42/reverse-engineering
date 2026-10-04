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

/** Read-only exact listing, instruction ownership, and function-body coverage. */
public class ExportIopCoverage extends GhidraScript {
    private static final java.util.Map<String, String> INPUTS = new java.util.HashMap<>();
    static {
        INPUTS.put("CDVDFSV.irx", "b743eed34c13cc3bc35117dcbeea7e96a68956c7247753d1d390598ecd914861");
        INPUTS.put("CDVDMAN.irx", "0440edf8b1457ea321a16acace9b33c1ed17ebdd9b74576c76a75ff72aeb17ca");
        INPUTS.put("EESYNC.irx", "0cb97a16720ffa9b147e8e7689cb704de83330e03aaf53fcd719ea46b97ef59e");
        INPUTS.put("FILEIO.irx", "ffe84d90c36c80457fa92facf18ea3891317cd95a27142e594d1e3715b49c824");
        INPUTS.put("IOMAN.irx", "b0b6eff43cedd2176657bfacef75178e75fadc15bcf18984775fb78bb422740c");
        INPUTS.put("LGDEV.IRX", "d42471dd8145e2ba0dce371f1b66d6ba49a7a50834b2d322788bc7c6b0acfd4f");
        INPUTS.put("LIBSD.IRX", "89e2322522f30fe5631c2e6c72ef82ac948377f5005331989165a5751297bc10");
        INPUTS.put("LOADCORE.irx", "488187ab52ec98dc6c13ba53601ab016636c678a1469826461a6f8dd041f6b38");
        INPUTS.put("LOADFILE.irx", "12967a07fcb21ed067c19dfc9ed9e67f694594b1e04fd364987260fed541d71f");
        INPUTS.put("MCMAN.IRX", "7ff6f7af1d410b8b8d382d868ddcb8a5c996b5f0d037df42919f0ce6433183d5");
        INPUTS.put("MCSERV.IRX", "e2c86f0a108041f655a85b8d7c0b39edbf2a1e7c23037ecca481089a14be8bb2");
        INPUTS.put("MODLOAD.irx", "a2d1d57c78b94d5079206877564d03af7205db99e51a775573a8c0a8428f7519");
        INPUTS.put("PADMAN.IRX", "196044d9535e6d346ad5f2d1ea75be111d0cbe516fac5a7240a21b1a4f90fa4f");
        INPUTS.put("ROMDRV.irx", "0aa9eeacc3a400e4f22bef3844c89cfaea516d7dfd89b0fa1bb0e603ecb9ce1a");
        INPUTS.put("SDRDRV.IRX", "b49a26a7f1801689f84e7e4cc92a286eb7e0ba3c3d4fb7855c994e0d20e3afa2");
        INPUTS.put("SIFCMD.irx", "24f0d50f174f25083388cafffe334afc6afa9b0bb196181bb9be36030b53762f");
        INPUTS.put("SIFMAN.irx", "8edc7d0dbf0bfb8669c62544b0c915485ee022794adfdf5270e44d3df4dc05ec");
        INPUTS.put("SIO2MAN.IRX", "1964b83bcc8c0cab9dfcf9b9637e0e313e69c23fd5c73408fe889ace91f13708");
        INPUTS.put("STDIO.irx", "05051433d89083ff93a6a4399326790f10d8fc2ae90492e65516eb4560289081");
        INPUTS.put("STREAM.IRX", "8cc55823925e92dbe59f5b60617979528b6f0a4052968319de79d6a461d557e3");
        INPUTS.put("SYSCLIB.irx", "2e3b82ecc6bba3d8c14fb6a55c6d68ecb643de3094305608ecbcd260dd49f447");
        INPUTS.put("THREADMAN.irx", "479f4a2ebf58b3f4470ba454d81842cf36b3a6b3976bfb524382550e87c0ab2b");
        INPUTS.put("TIMEMANI.irx", "95c0df47fabd3e62553b320f88a084ed499df31d50c256a066b5c4937df71a35");
        INPUTS.put("USBD.IRX", "61821c2c182a5feaa931a7447426b097eec99b3b9d198e3a35b6f434e0960255");
    }
    private JsonArray ranges(AddressSetView set) {
        JsonArray result = new JsonArray();
        for (AddressRange range : set.getAddressRanges()) {
            JsonObject row = new JsonObject();
            row.addProperty("start", range.getMinAddress().toString());
            row.addProperty("end", range.getMaxAddress().toString());
            row.addProperty("bytes", range.getLength());
            result.add(row);
        }
        return result;
    }

    private String sha256(MemoryBlock block) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[65536];
        long offset = 0;
        while (offset < block.getSize()) {
            monitor.checkCancelled();
            int length = (int) Math.min(buffer.length, block.getSize() - offset);
            block.getBytes(block.getStart().add(offset), buffer, 0, length);
            digest.update(buffer, 0, length);
            offset += length;
        }
        StringBuilder text = new StringBuilder();
        for (byte value : digest.digest()) text.append(String.format("%02x", value & 0xff));
        return text.toString();
    }

    private long u32(byte[] b, int p) { return (b[p]&255L)|((b[p+1]&255L)<<8)|((b[p+2]&255L)<<16)|((b[p+3]&255L)<<24); }
    private int u16(byte[] b, int p) { return (b[p]&255)|((b[p+1]&255)<<8); }
    private String digest(byte[] b) throws Exception { return java.util.HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private Path rawPath(Path root, String name) throws Exception {
        try (java.util.stream.Stream<Path> paths=Files.walk(root)) {
            List<Path> hits=paths.filter(Files::isRegularFile).filter(p->p.getFileName().toString().equals(name)).toList();
            if (hits.size()!=1) throw new IllegalArgumentException("raw input directory must contain exactly one file named "+name+"; got "+hits.size());
            return hits.get(0);
        }
    }
    private JsonObject rawElfProof(Path path, String expectedHash) throws Exception {
        byte[] b=Files.readAllBytes(path);
        if (!digest(b).equals(expectedHash)) throw new IllegalArgumentException("raw ELF SHA-256 differs from pinned executable SHA-256");
        if (b.length<52 || b[0]!=0x7f || b[1]!='E' || b[2]!='L' || b[3]!='F' || b[4]!=1 || b[5]!=1 || b[6]!=1 || u16(b,16)!=0xff80 || u16(b,18)!=8)
            throw new IllegalArgumentException("raw input is not ELF32 little-endian ET_IOP/EM_MIPS");
        long shoff=u32(b,32); int es=u16(b,46), n=u16(b,48), str=u16(b,50);
        if (es<40 || n==0 || str>=n || shoff+(long)es*n>b.length) throw new IllegalArgumentException("raw ELF section table invalid");
        int nh=Math.toIntExact(shoff+(long)es*str); long no=u32(b,nh+16), ns=u32(b,nh+20);
        if (no+ns>b.length) throw new IllegalArgumentException("raw ELF section name table invalid");
        int textOff=-1,textSize=-1,modOff=-1,modSize=-1,tc=0,mc=0,tt=-1,tf=-1,mt=-1; long ta=-1;
        for (int i=0;i<n;i++) {
            int h=Math.toIntExact(shoff+(long)es*i); long nameOff=u32(b,h);
            if (nameOff>=ns) throw new IllegalArgumentException("raw ELF section name offset invalid");
            int a=Math.toIntExact(no+nameOff),z=a; while(z<no+ns&&b[z]!=0)z++;
            String name=new String(b,a,z-a,StandardCharsets.US_ASCII); int type=(int)u32(b,h+4); long flags=u32(b,h+8),addr=u32(b,h+12),off=u32(b,h+16),size=u32(b,h+20);
            if(name.equals(".text")){tc++;textOff=Math.toIntExact(off);textSize=Math.toIntExact(size);ta=addr;tt=type;tf=(int)flags;}
            if(name.equals(".iopmod")){mc++;modOff=Math.toIntExact(off);modSize=Math.toIntExact(size);mt=type;}
        }
        if(tc!=1||mc!=1||tt!=1||(tf&4)==0||ta!=0||textOff<0||textSize<0||(long)textOff+textSize>b.length||mt!=0x70000080||modSize<27||(long)modOff+modSize>b.length)
            throw new IllegalArgumentException("raw ELF .text/.iopmod section profile invalid");
        long entry=u32(b,modOff+4),declared=u32(b,modOff+12);
        if(entry>=textSize||(entry&3)!=0||declared!=textSize) throw new IllegalArgumentException("raw ELF .iopmod entry/text-size metadata mismatch");
        JsonObject proof=new JsonObject(); proof.addProperty("raw_path",path.toAbsolutePath().toString()); proof.addProperty("raw_sha256",digest(b));
        proof.addProperty("elf_type","0xff80"); proof.addProperty("machine",8); proof.addProperty("text_address",ta); proof.addProperty("text_file_offset",textOff);
        proof.addProperty("text_size",textSize); proof.addProperty("text_sha256",digest(Arrays.copyOfRange(b,textOff,textOff+textSize)));
        proof.addProperty("iopmod_section_type",String.format("0x%08x",mt)); proof.addProperty("iopmod_entry_address",entry); proof.addProperty("iopmod_text_bytes",declared); return proof;
    }
    private void requireGhidraProfile(JsonObject proof) throws Exception {
        if (!"MIPS:LE:32:default".equals(currentProgram.getLanguageID().toString())) throw new IllegalArgumentException("Ghidra language is not MIPS:LE:32:default");
        if (!"default".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString())) throw new IllegalArgumentException("Ghidra compiler spec is not default");
        MemoryBlock text=null;
        for(MemoryBlock block:currentProgram.getMemory().getBlocks()) if(block.getName().equals(".text")){if(text!=null)throw new IllegalArgumentException("multiple .text blocks");text=block;}
        if(text==null||!text.isInitialized()||!text.isExecute()||text.getStart().getOffset()!=0||text.getSize()!=proof.get("text_size").getAsLong()||!sha256(text).equals(proof.get("text_sha256").getAsString()))
            throw new IllegalArgumentException("Ghidra .text is not executable, base-zero, and exact raw ELF size/hash");
    }
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Expected fresh output directory and raw input directory");
        String expectedHash = INPUTS.get(currentProgram.getName());
        if (expectedHash == null || !expectedHash.equals(currentProgram.getExecutableSHA256()))
            throw new IllegalArgumentException("Program name/input hash is outside the pinned IOP corpus profile");
        JsonObject elfProof=rawElfProof(rawPath(Paths.get(args[1]),currentProgram.getName()),expectedHash);
        requireGhidraProfile(elfProof);
        Path out = Paths.get(args[0]);
        Files.createDirectories(out);

        JsonObject root = new JsonObject();
        root.addProperty("schema_version", 1);
        root.addProperty("program", currentProgram.getName());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("compiler_spec", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.add("raw_elf_metadata_proof",elfProof);
        root.addProperty("ghidra_version", getGhidraVersion());
        root.addProperty("function_count", currentProgram.getFunctionManager().getFunctionCount());
        root.addProperty("claim_limits", "Exact saved listing and function-body interval inventory only. Defined instructions/data are not proof of correct decoding or complete recovery; function extents are the current Ghidra database's extents, not asserted original extents.");

        JsonArray functions = new JsonArray();
        FunctionManager fm = currentProgram.getFunctionManager();
        for (Function function : fm.getFunctions(true)) {
            monitor.checkCancelled();
            JsonObject item = new JsonObject();
            item.addProperty("entry", function.getEntryPoint().toString());
            item.addProperty("name", function.getName());
            item.addProperty("body_bytes", function.getBody().getNumAddresses());
            item.add("body_ranges", ranges(function.getBody()));
            item.addProperty("source", function.getSymbol().getSource().toString());
            functions.add(item);
        }
        root.add("functions", functions);

        JsonArray blocks = new JsonArray();
        Listing listing = currentProgram.getListing();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            monitor.checkCancelled();
            AddressSet extent = new AddressSet(block.getStart(), block.getEnd());
            AddressSet instructions = new AddressSet(), instructionOwned = new AddressSet();
            AddressSet data = new AddressSet();
            long instructionCount = 0;
            for (Instruction ins : listing.getInstructions(extent, true)) {
                monitor.checkCancelled();
                instructions.addRange(ins.getAddress(), ins.getMaxAddress());
                instructionCount++;
                if (fm.getFunctionContaining(ins.getAddress()) != null)
                    instructionOwned.addRange(ins.getAddress(), ins.getMaxAddress());
            }
            for (Data item : listing.getDefinedData(extent, true))
                data.addRange(item.getAddress(), item.getMaxAddress());
            JsonObject row = new JsonObject();
            row.addProperty("name", block.getName());
            row.addProperty("start", block.getStart().toString());
            row.addProperty("end", block.getEnd().toString());
            row.addProperty("bytes", block.getSize());
            row.addProperty("execute", block.isExecute());
            row.addProperty("read", block.isRead());
            row.addProperty("write", block.isWrite());
            row.addProperty("block_bytes", block.getSize());
            row.addProperty("block_sha256", sha256(block));
            row.addProperty("instruction_count", instructionCount);
            row.addProperty("instruction_bytes", instructions.getNumAddresses());
            row.addProperty("function_owned_instruction_bytes", instructionOwned.getNumAddresses());
            row.addProperty("unowned_instruction_bytes", instructions.subtract(instructionOwned).getNumAddresses());
            row.addProperty("defined_data_bytes", data.getNumAddresses());
            row.addProperty("undefined_bytes", extent.subtract(instructions).subtract(data).getNumAddresses());
            row.add("instruction_ranges", ranges(instructions));
            row.add("function_owned_instruction_ranges", ranges(instructionOwned));
            row.add("unowned_instruction_ranges", ranges(instructions.subtract(instructionOwned)));
            row.add("defined_data_ranges", ranges(data));
            row.add("undefined_ranges", ranges(extent.subtract(instructions).subtract(data)));
            blocks.add(row);
        }
        root.add("blocks", blocks);

        JsonArray entrypoints = new JsonArray();
        for (String entry : new String[] {"0x0"}) {
            Address address = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(entry);
            JsonObject row = new JsonObject();
            row.addProperty("address", address.toString());
            Function function = fm.getFunctionAt(address);
            row.addProperty("saved_function", function != null);
            if (function != null) row.addProperty("function_name", function.getName());
            Instruction instruction = listing.getInstructionAt(address);
            row.addProperty("instruction", instruction != null);
            if (instruction != null) {
                row.addProperty("instruction_length", instruction.getLength());
                row.addProperty("instruction_text", instruction.toString());
                row.addProperty("instruction_bytes", instruction.getBytes().length == 0 ? "" : bytesHex(instruction.getBytes()));
            }
            AddressSetView proposedBody = CreateFunctionCmd.getFunctionBody(currentProgram, address, monitor);
            row.add("cfg_computed_body_ranges", ranges(proposedBody));
            row.addProperty("cfg_computed_body_bytes", proposedBody.getNumAddresses());
            JsonArray overlapOwners = new JsonArray();
            for (Function existing : fm.getFunctions(true)) {
                AddressSetView overlap = existing.getBody().intersect(proposedBody);
                if (!overlap.isEmpty()) {
                    JsonObject owner = new JsonObject();
                    owner.addProperty("entry", existing.getEntryPoint().toString());
                    owner.addProperty("name", existing.getName());
                    owner.add("overlap_ranges", ranges(overlap));
                    overlapOwners.add(owner);
                }
            }
            row.add("cfg_computed_body_overlaps", overlapOwners);
            JsonArray refs = new JsonArray();
            for (Reference ref : currentProgram.getReferenceManager().getReferencesTo(address)) {
                JsonObject reference = new JsonObject();
                reference.addProperty("from", ref.getFromAddress().toString());
                reference.addProperty("type", ref.getReferenceType().toString());
                reference.addProperty("source", ref.getSource().toString());
                refs.add(reference);
            }
            row.add("references_to_entry", refs);
            entrypoints.add(row);
        }
        root.add("offset_zero_entry", entrypoints.get(0));

        Path path = out.resolve(currentProgram.getName().replaceAll("[^A-Za-z0-9._-]", "_") + ".json");
        Files.writeString(path, new GsonBuilder().setPrettyPrinting().create().toJson(root) + "\n",
            StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        println("IOP_COVERAGE_OK program=" + currentProgram.getName() + " functions=" + functions.size() + " blocks=" + blocks.size() + " path=" + path);
    }

    private String bytesHex(byte[] bytes) {
        StringBuilder text = new StringBuilder();
        for (byte value : bytes) text.append(String.format("%02x", value & 0xff));
        return text.toString();
    }
}
