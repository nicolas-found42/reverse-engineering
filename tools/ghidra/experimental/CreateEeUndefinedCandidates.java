//@category Analysis
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.FlowType;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * A single-seed, rollback-on-mismatch experiment for one undefined EE .text
 * range. Invoke once per saved project state. The three boundaries are
 * hypotheses cross-checked against a pinned static recompilation artifact;
 * they are not recovered source identities or semantic claims.
 */
public class CreateEeUndefinedCandidates extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String BASELINE_SHA = "39302b3579c4c88f688a962fc794a6f9c6d652730c4f09794e7a40b29001192e";
    private static final String WINDOW_SHA = "edf31a53a1dd273f55d1c55703638db8e5dd0e2b7d2a6924874df0085f7aac4d";
    private static final long TEXT_VA = 0x00100000L;
    private static final long TEXT_FILE = 0x00001000L;
    private static final long TEXT_SIZE = 0x00117bd4L;
    private static final long WINDOW_VA = 0x001fbfb8L;
    private static final int WINDOW_BYTES = 704;
    private static final int MAX_INSTRUCTIONS = 176;
    private static final String BASELINE_LEAF = "0022a180";
    private static final Map<String,Long> END_EXCLUSIVE = Map.of(
        "001fbfb8", 0x001fc0d0L,
        "001fc0d0", 0x001fc118L,
        "001fc118", 0x001fc278L
    );
    private static final Map<String,String[]> SAVED_CALLERS = Map.of(
        "001fc0d0", new String[]{"001fbf20", "001fbf44", "001fbf68"}
    );
    private static final Map<String,Long> RAW_CLUSTER_CALLS = Map.of(
        "001fbfb8", 0x001fc100L,
        "001fc118", 0x001fc0f0L
    );
    private static final Map<String,Long> ACCEPTED_PRIOR_CANDIDATES = Map.of(
        "001fbfb8", 276L,
        "001fc0d0", 68L,
        "001fc118", 348L
    );

    private static final class Node {
        final Address address;
        final boolean delay;
        Node(Address a, boolean d) { address = a; delay = d; }
    }
    private static final class Span {
        final long fileOffset;
        final byte[] bytes;
        Span(long off, byte[] b) { fileOffset = off; bytes = b; }
    }

    private void require(boolean ok, String message) {
        if (!ok) throw new IllegalStateException(message);
    }
    private String sha(byte[] data) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
    }
    private String bytes(Address address, int length) throws Exception {
        byte[] data = new byte[length];
        currentProgram.getMemory().getBytes(address, data);
        return HexFormat.of().formatHex(data);
    }
    private long u32(byte[] data, int at) {
        return (data[at] & 255L) | ((data[at + 1] & 255L) << 8) |
               ((data[at + 2] & 255L) << 16) | ((data[at + 3] & 255L) << 24);
    }
    private long u32(ByteBuffer data, int at) { return Integer.toUnsignedLong(data.getInt(at)); }
    private int u16(ByteBuffer data, int at) { return Short.toUnsignedInt(data.getShort(at)); }
    private Address addr(long value) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value); }
    private String canonical(Address address) { return String.format(Locale.ROOT, "%08x", address.getOffset()); }

    private Span locateText(byte[] elf) throws Exception {
        require(elf.length >= 52 && elf[0] == 0x7f && elf[1] == 'E' && elf[2] == 'L' && elf[3] == 'F' &&
                elf[4] == 1 && elf[5] == 1, "input is not ELF32 little-endian");
        ByteBuffer b = ByteBuffer.wrap(elf).order(ByteOrder.LITTLE_ENDIAN);
        require(u16(b, 16) == 2 && u16(b, 18) == 8, "ELF is not the pinned MIPS executable profile");
        long shoff = u32(b, 32);
        int shentsize = u16(b, 46), shnum = u16(b, 48), shstrndx = u16(b, 50);
        require(shentsize >= 40 && shnum > 0 && shstrndx < shnum && shoff + (long) shentsize * shnum <= elf.length,
                "ELF section-header table is invalid");
        int stringHeader = Math.toIntExact(shoff + (long) shentsize * shstrndx);
        long stringOffset = u32(b, stringHeader + 16), stringSize = u32(b, stringHeader + 20);
        require(stringOffset + stringSize <= elf.length, "ELF section-name table is out of bounds");
        int found = 0;
        long fileOffset = -1, virtualAddress = -1, size = -1;
        for (int i = 0; i < shnum; i++) {
            int h = Math.toIntExact(shoff + (long) shentsize * i);
            long nameOffset = u32(b, h);
            require(nameOffset < stringSize, "section name index is out of range");
            int nameStart = Math.toIntExact(stringOffset + nameOffset), nameEnd = nameStart;
            while (nameEnd < stringOffset + stringSize && elf[nameEnd] != 0) nameEnd++;
            String name = new String(elf, nameStart, nameEnd - nameStart, StandardCharsets.US_ASCII);
            if (name.equals(".text")) {
                found++;
                require((u32(b, h + 8) & 4) != 0, "ELF .text is not executable");
                virtualAddress = u32(b, h + 12);
                fileOffset = u32(b, h + 16);
                size = u32(b, h + 20);
            }
        }
        require(found == 1 && virtualAddress == TEXT_VA && fileOffset == TEXT_FILE && size == TEXT_SIZE,
                "ELF .text mapping differs from pinned profile");
        long spanOffset = fileOffset + WINDOW_VA - virtualAddress;
        require(spanOffset >= 0 && spanOffset + WINDOW_BYTES <= elf.length &&
                WINDOW_VA + WINDOW_BYTES <= virtualAddress + size, "candidate window is not file-backed by .text");
        byte[] window = Arrays.copyOfRange(elf, Math.toIntExact(spanOffset), Math.toIntExact(spanOffset + WINDOW_BYTES));
        require(sha(window).equals(WINDOW_SHA), "raw 704-byte .text window hash mismatch");
        return new Span(spanOffset, window);
    }

    private Map<String,String> functionBodies(FunctionManager fm) {
        Map<String,String> result = new TreeMap<>();
        for (Function f : fm.getFunctions(true)) {
            StringBuilder ranges = new StringBuilder();
            AddressRangeIterator it = f.getBody().getAddressRanges();
            while (it.hasNext()) {
                AddressRange r = it.next();
                ranges.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');
            }
            result.put(f.getEntryPoint().toString(), f.getName() + "|" + f.getSymbol().getSource() + "|" + ranges);
        }
        return result;
    }
    private Map<String,String> instructionBytes() throws Exception {
        Map<String,String> result = new TreeMap<>();
        for (Instruction i : currentProgram.getListing().getInstructions(true))
            result.put(i.getAddress().toString(), HexFormat.of().formatHex(i.getBytes()));
        return result;
    }
    private Map<String,String> dataRows() {
        Map<String,String> result = new TreeMap<>();
        for (Data d : currentProgram.getListing().getDefinedData(true))
            result.put(d.getAddress().toString(), d.getLength() + ":" + d.getDataType().getPathName());
        return result;
    }
    private String memoryHash() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[65536];
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) if (block.isInitialized()) {
            digest.update(block.getName().getBytes(StandardCharsets.UTF_8));
            digest.update(block.getStart().toString().getBytes(StandardCharsets.UTF_8));
            long offset = 0;
            while (offset < block.getSize()) {
                int n = (int) Math.min(buffer.length, block.getSize() - offset);
                currentProgram.getMemory().getBytes(block.getStart().add(offset), buffer, 0, n);
                digest.update(buffer, 0, n);
                offset += n;
            }
        }
        return HexFormat.of().formatHex(digest.digest());
    }
    private AddressSet instructionSet(AddressSetView body) {
        AddressSet result = new AddressSet();
        for (Instruction i : currentProgram.getListing().getInstructions(body, true))
            result.addRange(i.getAddress(), i.getMaxAddress());
        return result;
    }
    private JsonArray ranges(AddressSetView set) {
        JsonArray result = new JsonArray();
        for (AddressRange r : set.getAddressRanges()) {
            JsonObject item = new JsonObject();
            item.addProperty("start", r.getMinAddress().toString());
            item.addProperty("end_inclusive", r.getMaxAddress().toString());
            item.addProperty("bytes", r.getLength());
            result.add(item);
        }
        return result;
    }
    private JsonArray refsTo(Address target) {
        JsonArray result = new JsonArray();
        for (Reference ref : currentProgram.getReferenceManager().getReferencesTo(target)) {
            JsonObject row = new JsonObject();
            row.addProperty("from", ref.getFromAddress().toString());
            row.addProperty("type", ref.getReferenceType().toString());
            row.addProperty("source", ref.getSource().toString());
            result.add(row);
        }
        return result;
    }
    private void enqueue(ArrayDeque<Node> queue, Address at, Address start, Address end, boolean delay) {
        require(at != null, "unresolved control-flow successor");
        require(at.getAddressSpace().equals(start.getAddressSpace()) && at.getOffset() >= start.getOffset() &&
                at.getOffset() <= end.getOffset() && (at.getOffset() & 3) == 0,
                "flow edge escapes exact candidate interval: " + at);
        queue.add(new Node(at, delay));
    }
    private JsonObject instructionRow(Instruction i) throws Exception {
        JsonObject row = new JsonObject();
        row.addProperty("address", i.getAddress().toString());
        row.addProperty("text", i.toString());
        row.addProperty("bytes", bytes(i.getAddress(), 4));
        return row;
    }
    private boolean isReturnWord(long word) { return word == 0x03e00008L; }

    private JsonObject verifyAndCreate(String selected, byte[] elf, Span raw, Path baselinePath) throws Exception {
        Long endValue = END_EXCLUSIVE.get(selected);
        require(endValue != null, "unsupported candidate entry; invoke with exactly one allowlisted seed");
        Address start = addr(Long.parseUnsignedLong(selected, 16));
        Address endExclusive = addr(endValue);
        Address last = endExclusive.subtract(1);
        int spanBytes = Math.toIntExact(endExclusive.getOffset() - start.getOffset());
        require(spanBytes > 0 && (spanBytes & 3) == 0 && spanBytes <= WINDOW_BYTES, "candidate interval size is invalid");
        JsonObject result = new JsonObject();
        result.addProperty("entry", selected);
        result.addProperty("maximum_hypothesis_end_exclusive", canonical(endExclusive));
        result.addProperty("maximum_hypothesis_interval_bytes", spanBytes);
        result.addProperty("window_file_offset", String.format(Locale.ROOT, "%08x", raw.fileOffset));
        result.addProperty("window_sha256", WINDOW_SHA);

        FunctionManager fm = currentProgram.getFunctionManager();
        Function seedFunction = fm.getFunctionAt(start);
        require(seedFunction == null && fm.getFunctionContaining(start) == null, "candidate entry already belongs to a saved function");
        for (int off = 0; off < spanBytes; off += 4) {
            Address a = start.add(off);
            require(fm.getFunctionContaining(a) == null, "candidate bytes overlap a saved function at " + a);
            require(currentProgram.getListing().getInstructionAt(a) == null &&
                    currentProgram.getListing().getInstructionContaining(a) == null,
                    "candidate bytes are already decoded at " + a);
            require(currentProgram.getListing().getDefinedDataContaining(a) == null,
                    "candidate bytes overlap defined data at " + a);
        }

        JsonArray savedRefs = refsTo(start);
        if (SAVED_CALLERS.containsKey(selected)) {
            String[] expected = SAVED_CALLERS.get(selected);
            Set<String> actualSites = new TreeSet<>();
            for (JsonElement e : savedRefs) {
                JsonObject ref = e.getAsJsonObject();
                require("UNCONDITIONAL_CALL".equals(ref.get("type").getAsString()), "saved incoming reference is not an unconditional call");
                actualSites.add(ref.get("from").getAsString());
            }
            Set<String> expectedSites = new TreeSet<>(Arrays.asList(expected));
            require(actualSites.equals(expectedSites), "saved incoming-call sites differ from exact pinned evidence: " + actualSites);
        }
        result.add("saved_incoming_references", savedRefs);
        if (RAW_CLUSTER_CALLS.containsKey(selected)) {
            long site = RAW_CLUSTER_CALLS.get(selected);
            int offset = Math.toIntExact(site - WINDOW_VA);
            long word = u32(raw.bytes, offset);
            require((word >>> 26) == 3, "expected raw JAL from neighboring candidate is absent");
            long target = ((site + 4) & 0xf0000000L) | ((word & 0x03ffffffL) << 2);
            require(target == start.getOffset(), "raw neighboring JAL target does not match candidate seed");
            JsonObject edge = new JsonObject();
            edge.addProperty("site", String.format(Locale.ROOT, "%08x", site));
            edge.addProperty("raw_word", String.format(Locale.ROOT, "%08x", word));
            edge.addProperty("target", String.format(Locale.ROOT, "%08x", target));
            edge.addProperty("source_status", "raw direct JAL decoded from adjacent undefined candidate interval; not a saved Ghidra reference");
            result.add("raw_neighbor_call", edge);
        }

        Map<String,String> beforeBodies = functionBodies(fm);
        Map<String,String> beforeInstructions = instructionBytes();
        Map<String,String> beforeData = dataRows();
        String beforeMemory = memoryHash();
        int beforeCount = fm.getFunctionCount();
        require(beforeCount >= 3838 && beforeCount <= 3841,
                "expected baseline 3,837 entries, one separate leaf, and zero to three accepted bounded candidates");
        JsonObject baseline = JsonParser.parseString(Files.readString(baselinePath, StandardCharsets.UTF_8)).getAsJsonObject();
        Set<String> baselineEntries = new TreeSet<>();
        for (JsonElement item : baseline.getAsJsonArray("functions")) baselineEntries.add(item.getAsJsonObject().get("entry").getAsString());
        Set<String> expectedEntries = new TreeSet<>(baselineEntries);
        expectedEntries.add(BASELINE_LEAF);
        int priorCandidateCount = 0;
        for (Map.Entry<String,Long> prior : ACCEPTED_PRIOR_CANDIDATES.entrySet()) {
            Address priorEntry = addr(Long.parseLong(prior.getKey(), 16));
            Function priorFunction = fm.getFunctionAt(priorEntry);
            if (priorFunction == null) continue;
            require(!prior.getKey().equals(selected), "selected candidate already exists; refusing a duplicate seed");
            String priorName = "candidate_ee_" + prior.getKey();
            AddressSetView priorBody = priorFunction.getBody();
            require(priorFunction.getName().equals(priorName) &&
                    priorFunction.getSymbol().getSource() == SourceType.ANALYSIS &&
                    priorBody.getNumAddresses() == prior.getValue() &&
                    priorBody.getMinAddress().equals(priorEntry) &&
                    priorBody.getMaxAddress().equals(priorEntry.add(prior.getValue() - 1)),
                    "pre-existing candidate identity/body differs from exact accepted profile at " + prior.getKey());
            expectedEntries.add(prior.getKey());
            priorCandidateCount++;
        }
        require(baselineEntries.size() == 3837 && beforeCount == 3838 + priorCandidateCount &&
                beforeBodies.keySet().equals(expectedEntries),
                "pre-candidate entry set is not pinned baseline + leaf + exact accepted candidate subset");

        int transaction = currentProgram.startTransaction("single guarded EE undefined candidate " + selected);
        boolean commit = false;
        try {
            AddressSet allowed = new AddressSet(start, last);
            TreeMap<Long,Boolean> visited = new TreeMap<>();
            TreeSet<Long> newlyDecoded = new TreeSet<>();
            ArrayDeque<Node> queue = new ArrayDeque<>();
            JsonArray instructionRows = new JsonArray();
            JsonArray outgoingEdges = new JsonArray();
            queue.add(new Node(start, false));
            int steps = 0;
            while (!queue.isEmpty()) {
                monitor.checkCancelled();
                Node node = queue.remove();
                Address at = node.address;
                require(allowed.contains(at), "reachable instruction is outside candidate interval at " + at);
                Boolean wasDelay = visited.get(at.getOffset());
                if (wasDelay != null) {
                    require(wasDelay == node.delay, "instruction is reached both as delay slot and ordinary flow at " + at);
                    continue;
                }
                require(++steps <= MAX_INSTRUCTIONS, "candidate CFG exceeds bounded instruction ceiling");
                Instruction ins = currentProgram.getListing().getInstructionAt(at);
                if (ins == null) {
                    require(currentProgram.getListing().getDefinedDataContaining(at) == null, "decode collides with defined data at " + at);
                    Map<String,String> beforeDecode = instructionBytes();
                    AddressSet oneWord = new AddressSet(at, at.add(3));
                    DisassembleCommand disassemble = new DisassembleCommand(new AddressSet(at), oneWord, false);
                    disassemble.enableCodeAnalysis(false);
                    require(disassemble.applyTo(currentProgram, monitor), "single-word disassembly failed at " + at + ": " + disassemble.getStatusMsg());
                    ins = currentProgram.getListing().getInstructionAt(at);
                    require(ins != null && ins.getLength() == 4, "single-word decoder did not produce one 4-byte instruction at " + at);
                    int decodedOffset = Math.toIntExact(at.getOffset() - WINDOW_VA);
                    long decodedWord = u32(raw.bytes, decodedOffset);
                    FlowType decodedFlow = ins.getFlowType();
                    Set<Address> permittedDecoderResults = new HashSet<>();
                    permittedDecoderResults.add(at);
                    if (decodedFlow.isCall() || decodedFlow.isJump() || isReturnWord(decodedWord)) {
                        Address architecturalDelay = at.add(4);
                        require(allowed.contains(architecturalDelay), "delay slot falls outside the exact candidate interval at " + architecturalDelay);
                        permittedDecoderResults.add(architecturalDelay);
                    }
                    Map<String,String> afterDecode = instructionBytes();
                    for (Map.Entry<String,String> row : afterDecode.entrySet()) {
                        if (!beforeDecode.containsKey(row.getKey())) {
                            Address added = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(row.getKey());
                            require(permittedDecoderResults.contains(added), "disassembler created an instruction beyond the seed word or its one architectural delay slot at " + added);
                            newlyDecoded.add(added.getOffset());
                        }
                    }
                    for (String old : beforeDecode.keySet()) require(Objects.equals(beforeDecode.get(old), afterDecode.get(old)),
                            "single-word disassembly changed pre-existing instruction at " + old);
                }
                require(ins.getLength() == 4 && (at.getOffset() & 3) == 0, "candidate instruction is not one aligned word at " + at);
                int wordOffset = Math.toIntExact(at.getOffset() - WINDOW_VA);
                require(bytes(at, 4).equals(HexFormat.of().formatHex(Arrays.copyOfRange(raw.bytes, wordOffset, wordOffset + 4))),
                        "decoded instruction bytes differ from exact ELF bytes at " + at);
                visited.put(at.getOffset(), node.delay);
                instructionRows.add(instructionRow(ins));
                long word = u32(raw.bytes, wordOffset);
                FlowType flow = ins.getFlowType();

                if (node.delay) {
                    require(!flow.isCall() && !flow.isJump() && !flow.isTerminal(), "control transfer in MIPS delay slot is outside this experiment's supported subset at " + at);
                    continue;
                }
                if (isReturnWord(word)) {
                    enqueue(queue, at.add(4), start, last, true);
                    continue;
                }
                if (flow.isCall()) {
                    Address delay = at.add(4);
                    enqueue(queue, delay, start, last, true);
                    Address fallthrough = ins.getFallThrough();
                    enqueue(queue, fallthrough, start, last, false);
                    Address[] targets = ins.getFlows();
                    require(targets.length == 1 && !flow.isComputed(), "call has no single statically decoded target at " + at);
                    JsonObject edge = new JsonObject();
                    edge.addProperty("site", at.toString()); edge.addProperty("kind", "call");
                    edge.addProperty("target", targets[0].toString()); edge.addProperty("followed", false);
                    outgoingEdges.add(edge);
                    continue;
                }
                if (flow.isJump()) {
                    require(!flow.isComputed(), "computed jump prevents a bounded successor set at " + at);
                    enqueue(queue, at.add(4), start, last, true);
                    Address[] targets = ins.getFlows();
                    require(targets.length > 0, "direct jump has no decoded target at " + at);
                    for (Address target : targets) enqueue(queue, target, start, last, false);
                    if (flow.isConditional()) enqueue(queue, ins.getFallThrough(), start, last, false);
                    continue;
                }
                if (flow.hasFallthrough()) {
                    enqueue(queue, ins.getFallThrough(), start, last, false);
                    continue;
                }
                throw new IllegalStateException("unsupported terminal/non-fallthrough instruction at " + at + ": " + ins);
            }

            AddressSet traversed = new AddressSet();
            for (long offset : visited.keySet()) traversed.addRange(addr(offset), addr(offset + 3));
            require(visited.containsKey(start.getOffset()), "bounded CFG did not retain its entry instruction");
            long lastVisited = visited.lastKey();
            AddressSet contiguousReachablePrefix = new AddressSet(start, addr(lastVisited + 3));
            require(traversed.equals(contiguousReachablePrefix), "bounded CFG has unreachable holes before its final reachable word: " + ranges(traversed));
            JsonArray trailingZeroPadding = new JsonArray();
            for (long at = lastVisited + 4; at < endExclusive.getOffset(); at += 4) {
                int offset = Math.toIntExact(at - WINDOW_VA);
                long word = u32(raw.bytes, offset);
                require(word == 0, "nonzero unvisited word remains inside maximum candidate interval at " + String.format(Locale.ROOT, "%08x", at));
                JsonObject padding = new JsonObject();
                padding.addProperty("address", String.format(Locale.ROOT, "%08x", at));
                padding.addProperty("raw_word", "00000000");
                padding.addProperty("classification", "unreachable zero word inside maximum boundary hypothesis; left unowned");
                trailingZeroPadding.add(padding);
            }
            AddressSetView functionBody = CreateFunctionCmd.getFunctionBody(currentProgram, start, monitor);
            AddressSet bodyInstructions = instructionSet(functionBody);
            require(bodyInstructions.equals(traversed), "Ghidra computed function instruction set differs from independently traversed CFG");
            require(functionBody.equals(traversed), "Ghidra computed function body includes bytes outside independently traversed CFG");
            for (Instruction i : currentProgram.getListing().getInstructions(true)) { /* materialize listing for exact delta check */ }
            Map<String,String> afterInstructions = instructionBytes();
            TreeSet<String> added = new TreeSet<>(afterInstructions.keySet());
            added.removeAll(beforeInstructions.keySet());
            TreeSet<String> expectedAdded = new TreeSet<>();
            for (long offset : newlyDecoded) expectedAdded.add(addr(offset).toString());
            require(added.equals(expectedAdded), "global instruction listing delta is not exactly newly decoded candidate CFG words");
            for (String old : beforeInstructions.keySet()) require(Objects.equals(beforeInstructions.get(old), afterInstructions.get(old)), "pre-existing instruction changed at " + old);
            require(beforeData.equals(dataRows()), "candidate decode changed defined-data code units");
            require(beforeMemory.equals(memoryHash()), "candidate changed initialized memory bytes");

            String name = "candidate_ee_" + selected;
            CreateFunctionCmd create = new CreateFunctionCmd(name, start, functionBody, SourceType.ANALYSIS);
            require(create.applyTo(currentProgram, monitor), "CreateFunctionCmd failed: " + create.getStatusMsg());
            Function made = fm.getFunctionAt(start);
            require(made != null && made.getName().equals(name) && made.getSymbol().getSource() == SourceType.ANALYSIS,
                    "created candidate entry/name/source type differs from requested ANALYSIS candidate");
            require(made.getBody().equals(functionBody), "created function body differs from measured CFG body");
            require(fm.getFunctionCount() == beforeCount + 1, "candidate did not add exactly one function");
            Map<String,String> afterBodies = functionBodies(fm);
            require(afterBodies.size() == beforeBodies.size() + 1, "function entry set did not grow by exactly one");
            for (Map.Entry<String,String> row : beforeBodies.entrySet())
                require(Objects.equals(row.getValue(), afterBodies.get(row.getKey())), "pre-existing function body changed at " + row.getKey());
            require(afterBodies.containsKey(start.toString()), "candidate function body not present before transaction commit");

            result.addProperty("status", "created_single_bounded_candidate");
            result.addProperty("candidate_name", name);
            result.addProperty("candidate_source_type", "ANALYSIS");
            result.addProperty("candidate_body_start", start.toString());
            result.addProperty("candidate_body_end_inclusive", addr(lastVisited + 3).toString());
            result.addProperty("candidate_body_bytes", functionBody.getNumAddresses());
            result.addProperty("candidate_maximum_hypothesis_end_exclusive", canonical(endExclusive));
            result.add("unreachable_zero_tail_left_unowned", trailingZeroPadding);
            result.add("candidate_body_ranges", ranges(functionBody));
            result.addProperty("visited_instruction_count", visited.size());
            result.add("candidate_instructions", instructionRows);
            result.add("outgoing_call_edges", outgoingEdges);
            result.add("traversal_ranges", ranges(traversed));
            result.addProperty("preexisting_function_count", beforeCount);
            result.addProperty("function_count_after_candidate", fm.getFunctionCount());
            result.addProperty("preexisting_function_names_sources_and_bodies_unchanged", true);
            result.addProperty("defined_data_unchanged", true);
            result.addProperty("initialized_memory_sha256_before", beforeMemory);
            result.addProperty("initialized_memory_sha256_after", memoryHash());
            result.addProperty("prior_instruction_listing_unchanged", true);
            result.addProperty("new_instruction_count", newlyDecoded.size());
            result.add("exact_instruction_delta_ranges", ranges(new AddressSet(bodyInstructions)));
            result.addProperty("identity_and_reachability", "provisional only; candidate names and boundaries are hypotheses, and runtime reachability/source identity are not established");
            result.addProperty("claim_limits", "Single bounded Ghidra candidate with exact raw-word mapping and CFG/body agreement. This does not prove semantics, correct function identity, source recovery, or whole-game completeness.");
            commit = true;
        } finally {
            currentProgram.endTransaction(transaction, commit);
        }
        Function persisted = fm.getFunctionAt(start);
        require(persisted != null && persisted.getName().equals(result.get("candidate_name").getAsString()) &&
                persisted.getBody().getNumAddresses() == result.get("candidate_body_bytes").getAsInt(),
                "candidate did not remain present after its single transaction committed");
        result.addProperty("candidate_present_after_commit", true);
        result.addProperty("function_count_after_commit", fm.getFunctionCount());
        return result;
    }

    public void run() throws Exception {
        String[] args = getScriptArgs();
        require(args.length == 4, "Expected outputJson, rawElf, baselineManifest, oneSeedAddress");
        Path output = Paths.get(args[0]).toAbsolutePath();
        Path executable = Paths.get(args[1]).toAbsolutePath();
        Path baselinePath = Paths.get(args[2]).toAbsolutePath();
        String selected = args[3].toLowerCase(Locale.ROOT).replaceFirst("^0x", "");
        require(selected.matches("[0-9a-f]{8}"), "seed address must be exactly eight hex digits");
        require(!Files.exists(output), "result output already exists");
        byte[] elf = Files.readAllBytes(executable);
        String elfSha = sha(elf);
        JsonObject out = new JsonObject();
        out.addProperty("schema_version", 1);
        out.addProperty("program", currentProgram.getName());
        out.addProperty("executable_path", executable.toString());
        out.addProperty("executable_sha256", elfSha);
        out.addProperty("language", currentProgram.getLanguageID().toString());
        out.addProperty("ghidra_version", getGhidraVersion());
        out.addProperty("baseline_manifest_path", baselinePath.toString());
        try {
            require(sha(elf).equals(EXE_SHA) && EXE_SHA.equals(currentProgram.getExecutableSHA256()), "pinned PAL executable identity mismatch");
            require("r5900:LE:32:default".equals(currentProgram.getLanguageID().toString()), "program is not R5900 little-endian");
            require(Files.isRegularFile(baselinePath) && sha(Files.readAllBytes(baselinePath)).equals(BASELINE_SHA), "baseline manifest identity mismatch");
            Span raw = locateText(elf);
            MemoryBlock text = currentProgram.getMemory().getBlock(addr(TEXT_VA));
            require(text != null && text.getName().equals(".text") && text.isInitialized() && text.isExecute() &&
                    text.getStart().getOffset() == TEXT_VA && text.getSize() == TEXT_SIZE, "loaded Ghidra .text block does not match exact ELF map");
            require(bytes(addr(WINDOW_VA), WINDOW_BYTES).equals(HexFormat.of().formatHex(raw.bytes)), "loaded Ghidra bytes differ from pinned ELF window");
            out.addProperty("elf_text_window_file_offset", String.format(Locale.ROOT, "%08x", raw.fileOffset));
            out.addProperty("elf_text_window_sha256", WINDOW_SHA);
            out.addProperty("elf_text_window_bytes", WINDOW_BYTES);
            out.add("candidate", verifyAndCreate(selected, elf, raw, baselinePath));
            out.addProperty("status", "created_single_bounded_candidate");
        } catch (Exception e) {
            out.addProperty("status", "rejected_or_failed");
            out.addProperty("failure", e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage()));
            Files.createDirectories(output.toAbsolutePath().getParent());
            Files.writeString(output, new GsonBuilder().setPrettyPrinting().create().toJson(out) + "\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
            throw e;
        }
        Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output, new GsonBuilder().setPrettyPrinting().create().toJson(out) + "\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        println("EE_UNDEFINED_CANDIDATE_OK seed=" + selected + " bytes=" + out.getAsJsonObject("candidate").get("candidate_body_bytes").getAsInt() + " new_function_count=1");
    }
}
