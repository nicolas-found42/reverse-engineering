//@category Analysis
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * Experimental data-driven BATCH EE candidate guard (V5). One transaction creates K provisional functions from a SHA-pinned
 * schema-2 config. Per seed it keeps the V4 checks (pinned computed calls, tail J to saved entries, BREAK in a branch-likely
 * delay slot, next-word states) and allows spans over already-decoded unowned instructions; global reference and call-graph
 * deltas are checked against the union of all seeds. Do not run until the parent has reviewed this source, the config and the
 * exact baseline copy. This adds no source identity claim; it checks raw-word CFG hypotheses and rolls back on drift.
 */
public class CreateEeCandidateV5 extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final long TEXT_VA = 0x00100000L, TEXT_FILE = 0x1000L, TEXT_SIZE = 0x00117bd4L;
    private int INVENTORY_COUNT;
    private static final String LANGUAGE = "r5900:LE:32:default";
    // ---- V5 batch-specific state and methods ----
    private String MANIFEST_SHA, INVENTORY_SHA, COVERAGE_SHA, WINDOW_SHA, ENTRY;
    private long START, END, MAX_END, FIRST_WORD, DELAY_WORD, NEXT_WORD;
    private int WORDS, BYTES, LIKELY_COUNT;
    private final Map<String,String> EXPECTED_CALLS = new TreeMap<>(), TAIL_JUMPS = new TreeMap<>();
    private final Set<Long> ZERO_WORDS = new TreeSet<>();
    private final Set<String> COMPUTED_CALLS = new TreeSet<>(), DELAY_BREAKS = new TreeSet<>();
    private String TAIL_REF_TYPE = "UNCONDITIONAL_JUMP";
    private final List<SeedCfg> SEEDS = new ArrayList<>();
    private final Map<String,String> TAIL_FLOW = new TreeMap<>();
    private final Set<Long> PADDING = new TreeSet<>();
    private final Map<String,SwitchPin> SWITCHES = new TreeMap<>();

    private static final class SwitchPin {
        String site, table, guard, tableSha; int count; final List<Long> targets = new ArrayList<>();
        final Map<Long,String> referenceSources = new TreeMap<>();
    }

    private static final class SeedCfg {
        String entry, windowSha, nextState; long start, end, firstWord, delayWord, nextWord; int words, bytes, likely;
        final Map<String,String> calls = new TreeMap<>(), tails = new TreeMap<>(); final Set<Long> zeros = new TreeSet<>(), decoded = new TreeSet<>();
        final Set<String> known = new TreeSet<>(), batch = new TreeSet<>(), unresolved = new TreeSet<>(), ccalls = new TreeSet<>(), breaks = new TreeSet<>();
        final List<JsonObject> incoming = new ArrayList<>(); final Set<Long> padding = new TreeSet<>(); final Set<String> preOther = new TreeSet<>(); JsonObject cfg; byte[] raw;
        final Map<String,SwitchPin> switches = new TreeMap<>();
    }
    private long hx(JsonObject o, String k) { return Long.parseUnsignedLong(o.get(k).getAsString(), 16); }
    private void use(SeedCfg c) {
        ENTRY = c.entry; START = c.start; END = c.end; MAX_END = c.end; WORDS = c.words; BYTES = c.bytes; WINDOW_SHA = c.windowSha;
        FIRST_WORD = c.firstWord; DELAY_WORD = c.delayWord; NEXT_WORD = c.nextWord; LIKELY_COUNT = c.likely;
        EXPECTED_CALLS.clear(); EXPECTED_CALLS.putAll(c.calls); TAIL_JUMPS.clear(); TAIL_JUMPS.putAll(c.tails);
        SWITCHES.clear(); SWITCHES.putAll(c.switches);
        ZERO_WORDS.clear(); ZERO_WORDS.addAll(c.zeros); PADDING.clear(); PADDING.addAll(c.padding); COMPUTED_CALLS.clear(); COMPUTED_CALLS.addAll(c.ccalls); DELAY_BREAKS.clear(); DELAY_BREAKS.addAll(c.breaks);
    }
    private void loadConfig(byte[] cb) {
        JsonObject c = JsonParser.parseString(new String(cb, StandardCharsets.UTF_8)).getAsJsonObject();
        req(c.get("schema_version").getAsInt() == 2, "unsupported config schema (batch guard needs schema 2)");
        JsonObject base = c.getAsJsonObject("baseline");
        req(EXE_SHA.equals(base.get("executable_sha256").getAsString()), "config executable pin differs from guard constant");
        MANIFEST_SHA = base.get("manifest_sha256").getAsString(); INVENTORY_SHA = base.get("inventory_sha256").getAsString(); COVERAGE_SHA = base.get("coverage_sha256").getAsString();
        INVENTORY_COUNT = base.get("inventory_count").getAsInt();
        Set<String> entries = new TreeSet<>();
        for (JsonElement se : c.getAsJsonArray("seeds")) {
            JsonObject o = se.getAsJsonObject(); SeedCfg s = new SeedCfg();
            s.entry = o.get("entry").getAsString(); s.start = hx(o, "start"); s.end = hx(o, "end"); s.words = o.get("words").getAsInt(); s.bytes = o.get("bytes").getAsInt();
            s.windowSha = o.get("window_sha256").getAsString(); s.firstWord = hx(o, "first_word"); s.delayWord = hx(o, "delay_word"); s.nextWord = hx(o, "next_word");
            s.nextState = o.get("next_state").getAsString(); s.likely = o.get("likely_count").getAsInt();
            req(s.entry.equals(hex(s.start)) && s.end - s.start == s.bytes && s.bytes == s.words * 4L && (s.start & 3) == 0, "config span arithmetic is inconsistent for " + s.entry);
            req(Arrays.asList("undefined", "function_entry", "batch_entry", "unowned_instruction").contains(s.nextState), "unsupported next_state for " + s.entry);
            for (Map.Entry<String,JsonElement> e : o.getAsJsonObject("expected_calls").entrySet()) s.calls.put(e.getKey(), e.getValue().getAsString());
            for (Map.Entry<String,JsonElement> e : o.getAsJsonObject("tail_jumps").entrySet()) s.tails.put(e.getKey(), e.getValue().getAsString());
            for (JsonElement e : o.getAsJsonArray("zero_words")) s.zeros.add(Long.parseUnsignedLong(e.getAsString(), 16));
            for (JsonElement e : o.getAsJsonArray("known_callees")) s.known.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("batch_callees")) s.batch.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("unresolved_callees")) s.unresolved.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("computed_calls")) s.ccalls.add(e.getAsString());
            if (o.has("jump_tables")) for (JsonElement e : o.getAsJsonArray("jump_tables")) {
                JsonObject p = e.getAsJsonObject(); SwitchPin pin = new SwitchPin();
                pin.site = p.get("site").getAsString(); pin.table = p.get("table").getAsString(); pin.guard = p.get("guard_site").getAsString();
                pin.count = p.get("count").getAsInt(); pin.tableSha = p.get("table_sha256").getAsString();
                long site = Long.parseUnsignedLong(pin.site,16), table = Long.parseUnsignedLong(pin.table,16), guard = Long.parseUnsignedLong(pin.guard,16);
                req(site>=s.start&&site+8<=s.end&&(site&3)==0&&guard>=s.start&&guard<site&&(guard&3)==0&&site-guard<=56,"switch instruction interval differs from supported profile for "+s.entry);
                req(pin.count>=1&&pin.count<=256&&(table&3)==0,"unsupported switch count/alignment for "+s.entry);
                for (JsonElement t : p.getAsJsonArray("targets")) { long a=Long.parseUnsignedLong(t.getAsString(),16); req(a>=s.start&&a<s.end&&(a&3)==0,"switch target leaves exact candidate span for "+s.entry); pin.targets.add(a); }
                req(pin.targets.size()==pin.count&&s.switches.put(pin.site,pin)==null,"switch count or duplicate site differs for "+s.entry);
            }
            for (JsonElement e : o.getAsJsonArray("delay_breaks")) s.breaks.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("decoded_ranges")) { JsonArray r = e.getAsJsonArray(); long a = Long.parseUnsignedLong(r.get(0).getAsString(), 16), z = Long.parseUnsignedLong(r.get(1).getAsString(), 16); for (long pc = a; pc < z; pc += 4) s.decoded.add(pc); }
            for (JsonElement e : o.getAsJsonArray("incoming")) s.incoming.add(e.getAsJsonObject());
            if (o.has("padding_words")) for (JsonElement e : o.getAsJsonArray("padding_words")) { long pw = Long.parseUnsignedLong(e.getAsString(), 16); req(pw >= s.start && pw < s.end && (pw & 3) == 0 && !s.decoded.contains(pw), "padding word is outside the span, misaligned or pinned as a decoded body word: " + hex(pw)); s.padding.add(pw); }
            req(!s.known.contains(s.entry) && !s.batch.contains(s.entry) && !s.unresolved.contains(s.entry), "self-call is not supported by this guard");
            Set<String> targets = new TreeSet<>(s.calls.values()); Set<String> declared = new TreeSet<>(s.known); declared.addAll(s.batch); declared.addAll(s.unresolved);
            req(targets.equals(declared), "config call targets differ from the known+batch+unresolved declarations for " + s.entry);
            req(entries.add(s.entry), "duplicate seed entry " + s.entry);
            SEEDS.add(s);
        }
        req(!SEEDS.isEmpty(), "config has no seeds");
        Set<String> all = new TreeSet<>(entries);
        for (SeedCfg s : SEEDS) for (String b : s.batch) req(all.contains(b), "batch callee is not a seed of this batch: " + b);
        for (int i = 0; i < SEEDS.size(); i++) for (int j = i + 1; j < SEEDS.size(); j++) req(SEEDS.get(i).end <= SEEDS.get(j).start || SEEDS.get(j).end <= SEEDS.get(i).start, "seed spans overlap: " + SEEDS.get(i).entry + " " + SEEDS.get(j).entry);
    }
    private long T0 = System.currentTimeMillis();
    private void phase(String name) { println("PHASE " + name + " t+" + (System.currentTimeMillis() - T0) / 1000 + "s"); }
    private boolean liveInstruction(long pc) { return currentProgram.getListing().getInstructionAt(at(pc)) != null; }
    private boolean nextWordOk(SeedCfg c) {
        FunctionManager fm = currentProgram.getFunctionManager(); Address a = at(c.end); Listing l = currentProgram.getListing();
        switch (c.nextState) {
            case "undefined": return l.getInstructionAt(a) == null && l.getDefinedDataContaining(a) == null && fm.getFunctionContaining(a) == null;
            case "unowned_instruction": return l.getInstructionAt(a) != null && fm.getFunctionContaining(a) == null;
            case "function_entry": case "batch_entry": { Function f = fm.getFunctionAt(a); return f != null && f.getEntryPoint().equals(a) && l.getInstructionAt(a) != null; }
            default: return false;
        }
    }
    private void checkCoverageStates(JsonObject coverage) {
        req(EXE_SHA.equals(coverage.get("executable_sha256").getAsString()), "coverage executable identity mismatch");
        JsonObject block = null; for (JsonElement e : coverage.getAsJsonArray("blocks")) { JsonObject b = e.getAsJsonObject(); if (".text".equals(b.get("name").getAsString())) block = b; }
        req(block != null, "coverage has no .text block");
        Set<Long> undefined = new HashSet<>(), unowned = new HashSet<>();
        for (JsonElement e : block.getAsJsonArray("undefined_ranges")) { JsonObject r = e.getAsJsonObject(); long a = Long.parseUnsignedLong(r.get("start").getAsString(), 16), z = Long.parseUnsignedLong(r.get("end").getAsString(), 16); for (long x = a; x <= z; x++) undefined.add(x); }
        for (JsonElement e : block.getAsJsonArray("unowned_instruction_ranges")) { JsonObject r = e.getAsJsonObject(); long a = Long.parseUnsignedLong(r.get("start").getAsString(), 16), z = Long.parseUnsignedLong(r.get("end").getAsString(), 16); for (long x = a; x <= z; x++) unowned.add(x); }
        for (SeedCfg s : SEEDS) {
            for (long pc = s.start; pc < s.end; pc += 4) {
                if (s.padding.contains(pc)) continue;
                Set<Long> want = s.decoded.contains(pc) ? unowned : undefined;
                for (long x = pc; x < pc + 4; x++) req(want.contains(x), "baseline coverage state differs from the pinned state at " + hex(x) + " (" + s.entry + ")");
            }
            if (s.nextState.equals("undefined")) for (long x = s.end; x < s.end + 4; x++) req(undefined.contains(x), "baseline next word is not undefined for " + s.entry);
            if (s.nextState.equals("unowned_instruction")) for (long x = s.end; x < s.end + 4; x++) req(unowned.contains(x), "baseline next word is not an unowned instruction for " + s.entry);
        }
    }
    private void preSeed(SeedCfg s, byte[] elf) throws Exception {
        use(s); FunctionManager fm = currentProgram.getFunctionManager(); Listing l = currentProgram.getListing();
        long file = TEXT_FILE + START - TEXT_VA; byte[] raw = Arrays.copyOfRange(elf, Math.toIntExact(file), Math.toIntExact(file + BYTES)); s.raw = raw;
        req(sha(raw).equals(WINDOW_SHA), "candidate span SHA mismatch for " + ENTRY);
        String lastKind=flowKind(word(raw,raw.length-8));
        boolean switchLast=!s.switches.isEmpty()&&Arrays.asList("jump","unconditional_branch","computed_jump").contains(lastKind);
        req(word(raw, 0) == FIRST_WORD && word(raw, raw.length - 4) == DELAY_WORD && (word(raw, raw.length - 8) == 0x03e00008L || (s.tails.containsKey(hex(END - 8)) && (word(raw, raw.length - 8) >>> 26) == 2) || switchLast), "candidate initial/terminal/delay words differ from exact pins for " + ENTRY);
        for(SwitchPin pin:s.switches.values())checkSwitchMemory(pin,elf);
        for(SwitchPin pin:s.switches.values()) {
            Instruction dispatch=l.getInstructionAt(at(Long.parseUnsignedLong(pin.site,16)));
            for(long target:pin.targets)pin.referenceSources.put(target,"ANALYSIS");
            if(dispatch!=null)for(Reference ref:dispatch.getReferencesFrom())if(ref.getReferenceType().isFlow()) {
                long target=ref.getToAddress().getOffset();
                req(ref.getReferenceType()==RefType.COMPUTED_JUMP&&pin.targets.contains(target),"pre-existing switch flow references differ from pinned targets at "+pin.site+" type="+ref.getReferenceType()+" target="+hex(target));
                pin.referenceSources.put(target,ref.getSource().toString());
            }
        }
        req(bytes(at(START), raw.length).equals(HexFormat.of().formatHex(raw)), "loaded program bytes differ from exact ELF candidate span for " + ENTRY);
        long nf = file + BYTES; byte[] next = Arrays.copyOfRange(elf, Math.toIntExact(nf), Math.toIntExact(nf + 4));
        req(word(next, 0) == NEXT_WORD && bytes(at(END), 4).equals(HexFormat.of().formatHex(next)), "pinned next word differs for " + ENTRY);
        for (long pc = START; pc < END; pc += 4) {
            Address a = at(pc); boolean dec = s.decoded.contains(pc); Instruction i = l.getInstructionAt(a);
            if (s.padding.contains(pc)) { req(word(raw, Math.toIntExact(pc - START)) == 0, "padding word is not zero at " + hex(pc)); continue; }
            if (dec) req(i != null && i.getLength() == 4 && l.getInstructionContaining(a).getAddress().equals(a) && fm.getFunctionContaining(a) == null, "pinned decoded word is not an unowned 4-byte instruction at " + hex(pc));
            else req(i == null && l.getInstructionContaining(a) == null && l.getDefinedDataContaining(a) == null && fm.getFunctionContaining(a) == null, "pinned undefined word is not undefined at " + hex(pc));
        }
        req(fm.getFunctionAt(at(START)) == null && fm.getFunctionContaining(at(START)) == null, "candidate entry already belongs to a function: " + ENTRY);
        switch (s.nextState) {
            case "function_entry": req(nextWordOk(s), "pinned next saved function entry is absent for " + ENTRY); break;
            case "undefined": case "unowned_instruction": req(nextWordOk(s), "next word is not in its pinned baseline state for " + ENTRY); break;
            default: break;
        }
        for (JsonObject inc : s.incoming) {
            long pc = Long.parseUnsignedLong(inc.get("site").getAsString(), 16); long fo = TEXT_FILE + pc - TEXT_VA;
            long w = word(Arrays.copyOfRange(elf, Math.toIntExact(fo), Math.toIntExact(fo + 4)), 0), target = ((pc + 4) & 0xf0000000L) | ((w & 0x03ffffffL) << 2);
            req((w >>> 26) == 3 && target == START, "pinned incoming site does not decode to a JAL to the entry from raw ELF bytes at " + hex(pc));
        }
        JsonObject cfg = traverse(raw); s.cfg = cfg;
        Set<String> expIntra = expectedIntraRefs(s), preCalls = new TreeSet<>(), preIntra = new TreeSet<>();
        classifyRefs(s, preCalls, preIntra, s.preOther);
        req(expIntra.containsAll(preIntra), "pre-existing intra-span references of " + ENTRY + " are not a subset of the raw CFG branch edges: " + preIntra);
        req(cfg.get("instruction_count_including_delay_slots").getAsInt() == WORDS - PADDING.size(), "raw CFG is not the exact pinned word count for " + ENTRY);
        checkCandidateFlowProfile(cfg, raw);
    }
    private void checkSwitchMemory(SwitchPin pin, byte[] elf) throws Exception {
        long site=Long.parseUnsignedLong(pin.site,16),guard=Long.parseUnsignedLong(pin.guard,16),table=Long.parseUnsignedLong(pin.table,16);
        byte[] gb=new byte[4],jb=new byte[4];currentProgram.getMemory().getBytes(at(guard),gb);currentProgram.getMemory().getBytes(at(site),jb);
        long gw=word(gb,0),jw=word(jb,0);int index=(int)(gw>>>21)&31,flag=(int)(gw>>>16)&31,jreg=(int)(jw>>>21)&31;
        req((jw>>>26)==0&&(jw&0x1fffff)==8&&jreg!=0&&jreg!=31,"pinned switch is not an exact non-return JR at "+pin.site);
        req((gw>>>26)==11&&(gw&65535)==pin.count&&index!=0&&flag!=0&&index!=flag,"pinned switch bound/count differs at "+pin.guard);
        long shoff=word(elf,32);int stride=(elf[46]&255)|((elf[47]&255)<<8),count=(elf[48]&255)|((elf[49]&255)<<8);
        req(stride==40&&shoff+(long)stride*count<=elf.length,"ELF section table differs from supported map");
        long file=-1;int matches=0;
        for(int n=0;n<count;n++) {
            int off=Math.toIntExact(shoff+(long)n*stride);long type=word(elf,off+4),flags=word(elf,off+8),address=word(elf,off+12),offset=word(elf,off+16),size=word(elf,off+20);
            if(type==1&&(flags&2)!=0&&(flags&4)==0&&address<=table&&table+4L*pin.count<=address+size){file=offset+table-address;matches++;}
        }
        req(matches==1&&file>=0&&file+4L*pin.count<=elf.length,"pinned switch table has no unique ELF data-section mapping at "+pin.table);
        MemoryBlock block=currentProgram.getMemory().getBlock(at(table));
        req(block!=null&&block.isInitialized()&&!block.isExecute()&&block.contains(at(table+4L*pin.count-1)),"pinned switch table does not fit an initialized data block at "+pin.table);
        byte[] raw=Arrays.copyOfRange(elf,Math.toIntExact(file),Math.toIntExact(file+4L*pin.count)),memory=new byte[pin.count*4];
        req(currentProgram.getMemory().getBytes(at(table),memory)==memory.length&&Arrays.equals(memory,raw)&&sha(raw).equals(pin.tableSha),"pinned switch table memory/ELF/hash differs at "+pin.site);
        for(int n=0;n<pin.count;n++)req(word(raw,n*4)==pin.targets.get(n),"pinned ordered switch targets differ from table words at "+pin.site);
    }
    // Outside references may point only to the entry or from the pinned table
    // word corresponding exactly to an in-span case target.
    private void classifyRefs(SeedCfg s, Set<String> callSites, Set<String> intra, Set<String> other) {
        ReferenceManager rm = currentProgram.getReferenceManager();
        for (long pc = s.start; pc < s.end; pc++) for (Reference r : rm.getReferencesTo(at(pc))) {
            long from = r.getFromAddress().getOffset(); boolean inSpan = from >= s.start && from < s.end; String type = r.getReferenceType().toString();
            if (type.equals("UNCONDITIONAL_CALL") && pc == s.start) callSites.add(canonical(r.getFromAddress()));
            else if (inSpan) intra.add(canonical(r.getFromAddress()) + "|" + hex(pc) + "|" + type);
            else {
                boolean pinnedTableWord=false;
                for(SwitchPin pin:s.switches.values())for(int index=0;index<pin.count;index++)if(from==Long.parseUnsignedLong(pin.table,16)+4L*index&&pc==pin.targets.get(index)&&type.equals("DATA"))pinnedTableWord=true;
                req(pc == s.start || pinnedTableWord, "reference into the interior of " + s.entry + " from outside the span at " + hex(pc) + " from " + r.getFromAddress() + " type " + type); other.add(referenceKey(r));
            }
        }
    }
    private Set<String> expectedIntraRefs(SeedCfg s) {
        use(s); Set<String> out = new TreeSet<>();
        for (String k : expectedNewFlowReferences(s.cfg)) { String[] p = k.split("\\|"); long t = Long.parseUnsignedLong(p[1], 16); if (!p[2].equals("UNCONDITIONAL_CALL") && t >= s.start && t < s.end) out.add(p[0] + "|" + p[1] + "|" + p[2]); }
        return out;
    }
    private Set<String> expectedBatchFlowReferences() {
        Set<String> out = new TreeSet<>();
        for (SeedCfg s : SEEDS) { use(s); for (String k : expectedNewFlowReferences(s.cfg)) { long site = Long.parseUnsignedLong(k.substring(0, 8), 16); if (!s.decoded.contains(site)||k.contains("|COMPUTED_JUMP|")) out.add(k); } }
        return out;
    }
    private void checkBatchDeltas(Set<String> beforeRefs, Map<String,Set<String>> beforeCalled, Map<String,Set<String>> beforeCallers) throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager(); ReferenceManager rm = currentProgram.getReferenceManager();
        Set<String> afterRefs = referenceSnapshot(); Set<String> additions = new TreeSet<>(afterRefs); additions.removeAll(beforeRefs);
        Set<String> expectedAdditions=expectedBatchFlowReferences();expectedAdditions.removeAll(beforeRefs);
        req(additions.equals(expectedAdditions), "new reference set differs from the exact raw CFG flow edges of newly decoded words and pinned switch targets: " + additions);
        for (String ref : beforeRefs) req(afterRefs.contains(ref), "old global reference removed or changed: " + ref);
        Map<String,Set<String>> expCalled = new TreeMap<>(), expCallers = new TreeMap<>();
        for (Map.Entry<String,Set<String>> e : beforeCalled.entrySet()) expCalled.put(e.getKey(), new TreeSet<>(e.getValue()));
        for (Map.Entry<String,Set<String>> e : beforeCallers.entrySet()) expCallers.put(e.getKey(), new TreeSet<>(e.getValue()));
        for (SeedCfg s : SEEDS) { expCalled.put(s.entry, new TreeSet<>()); expCallers.put(s.entry, new TreeSet<>()); }
        for (SeedCfg s : SEEDS) {
            Set<String> callees = new TreeSet<>(s.known); callees.addAll(s.batch);
            for (String t : callees) { expCalled.get(s.entry).add(t); expCallers.get(t).add(s.entry); }
            for (Map.Entry<String,String> tj : s.tails.entrySet()) if ("CALL_TERMINATOR".equals(TAIL_FLOW.get(tj.getKey()))) { expCalled.get(s.entry).add(tj.getValue()); expCallers.get(tj.getValue()).add(s.entry); }
            for (JsonObject inc : s.incoming) if (!inc.get("owner_entry").isJsonNull()) { String o = inc.get("owner_entry").getAsString(); expCalled.get(o).add(s.entry); expCallers.get(s.entry).add(o); }
        }
        Map<String,Set<String>> afterCalled = calledGraph(), afterCallers = callerGraph();
        req(afterCalled.keySet().equals(expCalled.keySet()), "function set of the call graph differs from the expected set");
        for (String f : expCalled.keySet()) {
            req(Objects.equals(expCalled.get(f), afterCalled.get(f)), "callee graph differs from the expected batch delta at " + f + ": expected " + expCalled.get(f) + " actual " + afterCalled.get(f));
            req(Objects.equals(expCallers.get(f), afterCallers.get(f)), "caller graph differs from the expected batch delta at " + f + ": expected " + expCallers.get(f) + " actual " + afterCallers.get(f));
        }
        for (SeedCfg s : SEEDS) {
            for (String u : s.unresolved) { Address a = at(Long.parseUnsignedLong(u, 16)); req(fm.getFunctionAt(a) == null && fm.getFunctionContaining(a) == null, "unresolved outgoing callee was created/claimed at " + u); }
            // Every reference into the span's bytes must be exactly the pinned incoming call sites.
            Set<String> found = new TreeSet<>(), pinned = new TreeSet<>(), otherNow = new TreeSet<>(), intraNow = new TreeSet<>();
            classifyRefs(s, found, intraNow, otherNow);
            req(otherNow.equals(s.preOther), "non-call references into " + s.entry + " changed: before " + s.preOther + " after " + otherNow);
            req(intraNow.equals(expectedIntraRefs(s)), "intra-span branch references of " + s.entry + " differ from the raw CFG: " + intraNow);
            for (JsonObject inc : s.incoming) {
                String site = inc.get("site").getAsString(); pinned.add(site);
                Function owner = fm.getFunctionContaining(at(Long.parseUnsignedLong(site, 16)));
                if (inc.get("owner_entry").isJsonNull()) req(owner == null, "incoming site pinned as unowned now belongs to " + owner + " at " + site);
                else req(owner != null && canonical(owner.getEntryPoint()).equals(inc.get("owner_entry").getAsString()), "incoming site owner differs from pin at " + site);
            }
            req(found.equals(pinned), "complete references-to-every-byte scan differs from the pinned incoming call sites for " + s.entry + ": " + found);
        }
    }
    private void runBatch(byte[] elf, String cfgSha, Map<String,String> beforeInstructions, Map<String,String> beforeData, String beforeMemory, Map<String,String> beforeFunctions, Set<String> beforeRefs, Map<String,Set<String>> beforeCalled, Map<String,Set<String>> beforeCallers, JsonObject out) throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager(); Listing l = currentProgram.getListing();
        int tx = currentProgram.startTransaction("guarded EE batch of " + SEEDS.size()); boolean commit = false;
        try {
            Set<Long> newWords = new TreeSet<>();
            for (SeedCfg s : SEEDS) {
                use(s);
                for (long pc = START; pc < END; pc += 4) {
                    monitor.checkCancelled(); if (s.padding.contains(pc)) continue; Address a = at(pc);
                    if (!s.decoded.contains(pc)) {
                        DisassembleCommand dc = new DisassembleCommand(new AddressSet(a), new AddressSet(a, a.add(3)), false); dc.enableCodeAnalysis(false);
                        req(dc.applyTo(currentProgram, monitor), "single-word disassembly failed at " + hex(pc) + ": " + dc.getStatusMsg()); newWords.add(pc);
                    }
                    Instruction i = l.getInstructionAt(a); long fo = TEXT_FILE + pc - TEXT_VA; byte[] fb = Arrays.copyOfRange(elf, Math.toIntExact(fo), Math.toIntExact(fo + 4));
                    req(i != null && i.getLength() == 4 && bytes(a, 4).equals(HexFormat.of().formatHex(fb)) && Arrays.equals(fb, Arrays.copyOfRange(s.raw, Math.toIntExact(pc - START), Math.toIntExact(pc - START + 4))), "decoded/raw ELF bytes mismatch at " + hex(pc));
                }
            }
            phase("disassembly");
            for (SeedCfg s : SEEDS) { use(s); for (SwitchPin pin:s.switches.values()) {
                checkSwitchMemory(pin,elf);
                Instruction dispatch=l.getInstructionAt(at(Long.parseUnsignedLong(pin.site,16)));
                req(dispatch!=null,"switch dispatch is not decoded for "+s.entry);
                for(long target:new TreeSet<>(pin.targets)) {
                    boolean exists=false;for(Reference ref:dispatch.getReferencesFrom())if(ref.getReferenceType()==RefType.COMPUTED_JUMP&&ref.getToAddress().equals(at(target)))exists=true;
                    if(!exists)dispatch.addOperandReference(0,at(target),RefType.COMPUTED_JUMP,SourceType.ANALYSIS);
                }
            } }
            List<String> flowFailures = new ArrayList<>();
            for (SeedCfg s : SEEDS) { use(s); try { checkDecoderFlow(s.cfg); } catch (Exception e) { flowFailures.add("SEED_FAILURE " + s.entry + ": " + e.getMessage()); } }
            req(flowFailures.isEmpty(), "DECODER_FLOW_FAILURES " + flowFailures.size() + " " + String.join(" | ", flowFailures.subList(0, Math.min(flowFailures.size(), 400))));
            phase("decoder-flow");
            for (SeedCfg s : SEEDS) {
                use(s); Address start = at(START);
                AddressSet expected = new AddressSet(); for (JsonElement a : s.cfg.getAsJsonArray("instruction_addresses")) { Address ia = at(Long.parseUnsignedLong(a.getAsString(), 16)); expected.addRange(ia, ia.add(3)); }
                req(expected.getNumAddresses() == BYTES - 4L * PADDING.size(), "CFG body instruction ranges do not cover exactly the pinned body bytes for " + ENTRY);
                AddressSetView body = CreateFunctionCmd.getFunctionBody(currentProgram, start, monitor);
                req(body.equals(expected), "Ghidra-computed body differs from raw CFG contiguous body for " + ENTRY + ": actual=" + rangeSummary(body) + " expected=" + rangeSummary(expected));
                CreateFunctionCmd create = new CreateFunctionCmd("candidate_ee_" + ENTRY, start, body, SourceType.ANALYSIS);
                req(create.applyTo(currentProgram, monitor), "CreateFunctionCmd failed for " + ENTRY + ": " + create.getStatusMsg());
                Function made = fm.getFunctionAt(start);
                req(made != null && made.getName().equals("candidate_ee_" + ENTRY) && made.getSymbol().getSource() == SourceType.ANALYSIS && made.getBody().equals(expected), "created candidate identity/body differs for " + ENTRY);
            }
            phase("functions-created"); Map<String,String> now = instructionSnapshot(); phase("instruction-snapshot");
            for (String a : beforeInstructions.keySet()) req(Objects.equals(now.get(a), beforeInstructions.get(a)), "old instruction bytes changed at " + a);
            Set<String> added = new TreeSet<>(now.keySet()); added.removeAll(beforeInstructions.keySet());
            Set<String> expectedAdded = new TreeSet<>(); for (long pc : newWords) expectedAdded.add(hex(pc));
            req(added.equals(expectedAdded), "listing delta differs from the exact set of newly decoded words (" + added.size() + " vs " + expectedAdded.size() + ")");
            req(dataSnapshot().equals(beforeData), "defined data changed"); req(memoryHash().equals(beforeMemory), "initialized memory changed");
            Map<String,String> fnow = functionSnapshot(); for (Map.Entry<String,String> e : beforeFunctions.entrySet()) req(Objects.equals(fnow.get(e.getKey()), e.getValue()), "old function name/source/body changed at " + e.getKey());
            req(fm.getFunctionCount() == INVENTORY_COUNT + SEEDS.size(), "function count did not increase by exactly the batch size");
            for (SeedCfg s : SEEDS) req(nextWordOk(s), "next word after " + s.entry + " is not in its pinned state after creation");
            phase("state-checks"); checkBatchDeltas(beforeRefs, beforeCalled, beforeCallers); phase("batch-deltas");
            for (SeedCfg s : SEEDS) { Function p = fm.getFunctionAt(at(s.start)); req(p != null && p.getName().equals("candidate_ee_" + s.entry) && p.getBody().getNumAddresses() == s.bytes - 4L * s.padding.size(), "candidate absent or altered before transaction commit: " + s.entry); }
            commit = true;
        } finally { currentProgram.endTransaction(tx, commit); }
        JsonArray summary = new JsonArray();
        for (SeedCfg s : SEEDS) {
            JsonObject o = new JsonObject(); o.addProperty("entry", s.entry); o.addProperty("words", s.words); o.addProperty("padding_words", s.padding.size()); o.addProperty("decoded_preexisting_words", s.decoded.size()); o.addProperty("incoming_sites", s.incoming.size()); o.addProperty("next_state", s.nextState); JsonArray orr = new JsonArray(); for (String k : s.preOther) orr.add(k); o.add("non_call_references_into_entry", orr); JsonObject tf = new JsonObject(); for (Map.Entry<String,String> tj : s.tails.entrySet()) tf.addProperty(tj.getKey(), tj.getValue() + "|" + TAIL_FLOW.getOrDefault(tj.getKey(), "?")); o.add("tail_jumps_with_flow_type", tf); summary.add(o); }
        out.add("seeds", summary);
    }
    public void run() throws Exception {
        String[] args = getScriptArgs(); req(args.length == 7, "Expected outputJson, rawElf, finalManifest, finalInventory, finalCoverage, config, configSha256");
        Path output = Paths.get(args[0]).toAbsolutePath(), exe = Paths.get(args[1]).toAbsolutePath(), mp = Paths.get(args[2]).toAbsolutePath(), ip = Paths.get(args[3]).toAbsolutePath(), cp = Paths.get(args[4]).toAbsolutePath(), cfgp = Paths.get(args[5]).toAbsolutePath();
        req(!Files.exists(output), "output already exists; refusing overwrite"); byte[] elf = Files.readAllBytes(exe), mb = Files.readAllBytes(mp), ib = Files.readAllBytes(ip), cb = Files.readAllBytes(cp), cfgb = Files.readAllBytes(cfgp);
        JsonObject out = new JsonObject(); out.addProperty("schema_version", 2); out.addProperty("config_sha256", sha(cfgb)); out.addProperty("executable_sha256", sha(elf)); out.addProperty("baseline_manifest_sha256", sha(mb)); out.addProperty("baseline_inventory_sha256", sha(ib)); out.addProperty("baseline_coverage_sha256", sha(cb)); out.addProperty("language", currentProgram.getLanguageID().toString()); out.addProperty("ghidra_version", getGhidraVersion());
        try {
            req(sha(cfgb).equals(args[6]), "config SHA-256 differs from the pinned command argument"); loadConfig(cfgb); out.addProperty("seed_count", SEEDS.size());
            req(EXE_SHA.equals(sha(elf)) && EXE_SHA.equals(currentProgram.getExecutableSHA256()), "pinned executable identity mismatch"); req(MANIFEST_SHA.equals(sha(mb)), "baseline manifest hash mismatch"); req(INVENTORY_SHA.equals(sha(ib)), "baseline inventory hash mismatch"); req(COVERAGE_SHA.equals(sha(cb)), "baseline coverage hash mismatch"); req(LANGUAGE.equals(currentProgram.getLanguageID().toString()), "program is not R5900 little-endian");
            JsonObject manifest = JsonParser.parseString(new String(mb, StandardCharsets.UTF_8)).getAsJsonObject(), inventory = JsonParser.parseString(new String(ib, StandardCharsets.UTF_8)).getAsJsonObject(), coverage = JsonParser.parseString(new String(cb, StandardCharsets.UTF_8)).getAsJsonObject();
            MemoryBlock text = currentProgram.getMemory().getBlock(at(TEXT_VA)); req(text != null && text.getName().equals(".text") && text.isInitialized() && text.isExecute() && text.getStart().getOffset() == TEXT_VA && text.getSize() == TEXT_SIZE, "loaded .text block differs from exact ELF map");
            phase("config-and-pins"); checkBaseline(manifest, inventory); phase("baseline"); checkCoverageStates(coverage); phase("coverage-states");
            Map<String,String> functions = functionSnapshot(), instructions = instructionSnapshot(), data = dataSnapshot(); String memory = memoryHash(); Set<String> refsBefore = referenceSnapshot(); Map<String,Set<String>> calledBefore = calledGraph(), callersBefore = callerGraph();
            phase("snapshots");
            List<String> failures = new ArrayList<>();
            for (SeedCfg s : SEEDS) { try { preSeed(s, elf); } catch (Exception e) { failures.add("SEED_FAILURE " + s.entry + ": " + e.getMessage()); } }
            req(failures.isEmpty(), "PRE_CHECK_FAILURES " + failures.size() + " " + String.join(" | ", failures.subList(0, Math.min(failures.size(), 400))));
            phase("pre-seed-checks");
            runBatch(elf, sha(cfgb), instructions, data, memory, functions, refsBefore, calledBefore, callersBefore, out);
            out.addProperty("status", "created_batch_bounded_candidates"); out.addProperty("function_count_after", currentProgram.getFunctionManager().getFunctionCount()); out.addProperty("old_function_snapshot_preserved", true); out.addProperty("initialized_memory_preserved", true); out.addProperty("defined_data_preserved", true);
            out.addProperty("scope", "Static provisional candidates only. No original function identity, semantics, runtime reachability, or whole-game completeness is established.");
        } catch (Exception e) { out.addProperty("status", "rejected_or_failed"); out.addProperty("failure", e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage())); write(output, out); throw e; }
        write(output, out); println("EE_BATCH_CANDIDATES_OK seeds=" + SEEDS.size() + " function_count_delta=" + SEEDS.size());
    }

    private static final class Node {
        final long pc; final boolean delay;
        Node(long p, boolean d) { pc=p; delay=d; }
    }
    private static final class Edge {
        long pc, target, fall; String kind;
        Edge(long p, long t, long f, String k) { pc=p;target=t;fall=f;kind=k; }
    }
    private void req(boolean b, String m) { if (!b) throw new IllegalStateException(m); }
    private String hex(long v) { return String.format(Locale.ROOT, "%08x", v); }
    private String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private Address at(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
    private String bytes(Address a, int n) throws Exception { byte[] b=new byte[n]; currentProgram.getMemory().getBytes(a,b); return HexFormat.of().formatHex(b); }
    private long word(byte[] b, int i) { return (b[i]&255L)|((b[i+1]&255L)<<8)|((b[i+2]&255L)<<16)|((b[i+3]&255L)<<24); }
    private long wordAt(byte[] b,long pc) { return word(b,Math.toIntExact(pc-START)); }
    private long branchTarget(long pc,long w) { int imm=(short)(w&0xffff); return pc+4L+((long)imm<<2); }
    private String canonical(Address a) { return hex(a.getOffset()); }
    private String rangeSummary(AddressSetView set) { StringBuilder b=new StringBuilder();AddressRangeIterator it=set.getAddressRanges();while(it.hasNext()){AddressRange r=it.next();if(b.length()>0)b.append(',');b.append(canonical(r.getMinAddress())).append('-').append(canonical(r.getMaxAddress()));}return b.toString(); }

    private String memoryHash() throws Exception {
        MessageDigest d=MessageDigest.getInstance("SHA-256"); byte[] buf=new byte[65536];
        for(MemoryBlock b:currentProgram.getMemory().getBlocks()) if(b.isInitialized()) {
            d.update(b.getName().getBytes(StandardCharsets.UTF_8)); d.update(b.getStart().toString().getBytes(StandardCharsets.UTF_8));
            long off=0; while(off<b.getSize()) { int n=(int)Math.min(buf.length,b.getSize()-off); currentProgram.getMemory().getBytes(b.getStart().add(off),buf,0,n); d.update(buf,0,n); off+=n; }
        }
        return HexFormat.of().formatHex(d.digest());
    }
    private Map<String,String> functionSnapshot() {
        Map<String,String> m=new TreeMap<>();
        for(Function f:currentProgram.getFunctionManager().getFunctions(true)) {
            StringBuilder b=new StringBuilder(f.getName()).append('|').append(f.getSymbol().getSource()).append('|');
            AddressRangeIterator it=f.getBody().getAddressRanges(); while(it.hasNext()){AddressRange r=it.next();b.append(r.getMinAddress()).append('-').append(r.getMaxAddress()).append(',');}
            m.put(canonical(f.getEntryPoint()),b.toString());
        }
        return m;
    }
    private Map<String,String> instructionSnapshot() throws Exception {
        Map<String,String> m=new TreeMap<>(); for(Instruction i:currentProgram.getListing().getInstructions(true)) m.put(canonical(i.getAddress()),i.toString()+"|"+bytes(i.getAddress(),i.getLength())); return m;
    }
    private Map<String,String> dataSnapshot() {
        Map<String,String> m=new TreeMap<>(); for(Data d:currentProgram.getListing().getDefinedData(true)) m.put(canonical(d.getAddress()),d.getLength()+":"+d.getDataType().getPathName()); return m;
    }
    private JsonArray incomingCalls() {
        JsonArray a=new JsonArray(); ReferenceManager rm=currentProgram.getReferenceManager();
        for(long target=START;target<MAX_END;target++) for(Reference r:rm.getReferencesTo(at(target))) {
            JsonObject o=new JsonObject(); o.addProperty("to",hex(target)); o.addProperty("from",canonical(r.getFromAddress())); o.addProperty("type",r.getReferenceType().toString()); o.addProperty("source",r.getSource().toString()); a.add(o);
        }
        return a;
    }
    private void checkBaseline(JsonObject manifest, JsonObject inventory) throws Exception {
        req(INVENTORY_COUNT==inventory.get("inventory_count").getAsInt() && INVENTORY_COUNT==manifest.get("inventory_count").getAsInt(),"baseline inventory/manifest count changed");
        req(LANGUAGE.equals(inventory.get("language").getAsString()) && LANGUAGE.equals(manifest.get("language").getAsString()),"baseline language mismatch");
        req(EXE_SHA.equals(inventory.get("executable_sha256").getAsString()) && EXE_SHA.equals(manifest.get("executable_sha256").getAsString()),"baseline executable identity mismatch");
        JsonArray fs=inventory.getAsJsonArray("functions"); req(fs.size()==INVENTORY_COUNT,"inventory function rows do not equal pinned count");
        Map<String,JsonObject> expected=new TreeMap<>(); for(JsonElement e:fs){JsonObject f=e.getAsJsonObject();expected.put(f.get("entry").getAsString(),f);}
        FunctionManager fm=currentProgram.getFunctionManager(); req(fm.getFunctionCount()==INVENTORY_COUNT,"live function count differs from the baseline snapshot");
        Map<String,String> live=functionSnapshot(); req(live.size()==INVENTORY_COUNT && expected.size()==INVENTORY_COUNT,"function entry inventory cardinality mismatch");
        for(Map.Entry<String,JsonObject> e:expected.entrySet()) {
            String entry=e.getKey(); JsonObject row=e.getValue(); Function f=fm.getFunctionAt(at(Long.parseUnsignedLong(entry,16)));
            req(f!=null && f.getName().equals(row.get("name").getAsString()),"live function identity/name mismatch at "+entry);
            req(f.getBody().getNumAddresses()==row.get("size").getAsLong(),"live function body size differs from inventory at "+entry);
            AddressSet expectedBody=new AddressSet();
            for(JsonElement ie:row.getAsJsonArray("instructions")){JsonObject ir=ie.getAsJsonObject();Address ia=at(Long.parseUnsignedLong(ir.get("address").getAsString(),16));expectedBody.addRange(ia,ia.add(3));}
            req(f.getBody().equals(expectedBody),"live function body ranges differ from exact inventory instruction addresses at "+entry);
            req(live.containsKey(entry),"live function snapshot missing inventory entry "+entry);
            for(JsonElement ie:row.getAsJsonArray("instructions")) {
                JsonObject ins=ie.getAsJsonObject(); Address a=at(Long.parseUnsignedLong(ins.get("address").getAsString(),16)); Instruction decoded=currentProgram.getListing().getInstructionAt(a);
                req(decoded!=null && bytes(a,decoded.getLength()).equals(ins.get("bytes").getAsString()),"baseline instruction bytes mismatch at "+ins.get("address").getAsString());
                req(decoded.toString().equals(ins.get("text").getAsString()),"baseline instruction text mismatch at "+ins.get("address").getAsString());
            }
        }
    }
    private String flowKind(long w) {
        int op=(int)(w>>>26), rs=(int)((w>>>21)&31), rt=(int)((w>>>16)&31), fn=(int)(w&63);
        if(op==0 && fn==8 && w==0x03e00008L)return "return";
        if(op==0 && fn==8)return "computed_jump"; if(op==0 && fn==9)return "computed_call";
        if(op==0 && (fn==13||fn==48||fn==49||fn==50||fn==51||fn==52||fn==54))return "unsupported_trap";
        if(op==0 && (fn==32||fn==34||fn==44||fn==46))return "unsupported_trap";
        if(op==8||op==24)return "unsupported_trap"; // ADDI and DADDI may take overflow exceptions.
        if(op==2)return "jump"; if(op==3)return "call";
        if(op==1) {
            if(rt==8||rt==9||rt==10||rt==11||rt==12||rt==14)return "unsupported_trap";
            if(rt==0||rt==1||rt==2||rt==3||rt==16||rt==17||rt==18||rt==19)return (rt==2||rt==3||rt==18||rt==19)?"conditional_likely":"conditional";
            return "unsupported_encoding";
        }
        if(op==4 && rs==0 && rt==0)return "unconditional_branch";
        if(op==4||op==5)return "conditional";
        if((op==6||op==7||op==22||op==23)&&rt!=0)return "unsupported_encoding";
        if(op==6||op==7)return "conditional";
        if(op==20||op==21||op==22||op==23)return "conditional_likely";
        if((op==16||op==17||op==18||op==19)&&rs==8)return ((rt&2)!=0)?"conditional_likely":"conditional";
        return "linear";
    }
    private boolean isTransfer(String k) { return k.equals("conditional")||k.equals("conditional_likely")||k.equals("unconditional_branch")||k.equals("call")||k.equals("jump")||k.equals("return"); }
    private JsonObject traverse(byte[] raw) {
        TreeMap<Long,Boolean> seen=new TreeMap<>(); ArrayDeque<Node> q=new ArrayDeque<>(); q.add(new Node(START,false)); JsonArray edges=new JsonArray(); JsonArray breaks=new JsonArray();
        while(!q.isEmpty()) {
            Node n=q.remove(); req(n.pc>=START&&n.pc<END&&(n.pc&3)==0,"CFG successor leaves exact max interval: "+hex(n.pc));
            Boolean old=seen.get(n.pc); if(old!=null){req(old==n.delay,"word reached both as delay and ordinary instruction: "+hex(n.pc));continue;}
            long w=wordAt(raw,n.pc); String k=flowKind(w); seen.put(n.pc,n.delay);
            if(n.delay){
                if(k.equals("unsupported_trap")&&(w>>>26)==0&&(w&63)==13&&DELAY_BREAKS.contains(hex(n.pc))&&flowKind(wordAt(raw,n.pc-4)).equals("conditional_likely")){breaks.add(hex(n.pc));continue;}
                req(k.equals("linear"),"control transfer in delay slot at "+hex(n.pc));continue;}
            boolean tail=false; long target=((n.pc+4)&0xf0000000L)|((w&0x03ffffffL)<<2), fall=n.pc+8;
            if(k.equals("linear")){q.add(new Node(n.pc+4,false));continue;}
            if(k.equals("computed_call"))req(COMPUTED_CALLS.contains(hex(n.pc)),"computed call is not pinned in the config at "+hex(n.pc));
            if(k.equals("computed_jump")) {
                SwitchPin pin=SWITCHES.get(hex(n.pc));req(pin!=null,"computed jump is not pinned at "+hex(n.pc));
                q.add(new Node(n.pc+4,true));JsonArray targets=new JsonArray();
                for(long t:pin.targets){req(t>=START&&t<END&&(t&3)==0,"switch target leaves exact interval at "+hex(n.pc));q.add(new Node(t,false));targets.add(hex(t));}
                JsonObject edge=new JsonObject();edge.addProperty("site",hex(n.pc));edge.addProperty("kind","switch");edge.add("targets",targets);edges.add(edge);continue;
            }
            if(k.equals("unsupported_trap")||k.equals("unsupported_encoding"))throw new IllegalStateException("unsupported computed/trap transfer at "+hex(n.pc)+" kind="+k);
            if(k.equals("conditional")||k.equals("conditional_likely")){target=branchTarget(n.pc,w);q.add(new Node(n.pc+4,true));q.add(new Node(target,false));q.add(new Node(fall,false));}
            else if(k.equals("unconditional_branch")){target=branchTarget(n.pc,w);q.add(new Node(n.pc+4,true));q.add(new Node(target,false));}
            else if(k.equals("call")||k.equals("computed_call")){q.add(new Node(n.pc+4,true));q.add(new Node(fall,false));}
            else if(k.equals("jump")){q.add(new Node(n.pc+4,true));if(target>=START&&target<END)q.add(new Node(target,false));else{req(hex(target).equals(TAIL_JUMPS.get(hex(n.pc))),"J leaves the span and is not a pinned tail jump at "+hex(n.pc));tail=true;}}
            else if(k.equals("return")){q.add(new Node(n.pc+4,true));}
            else throw new IllegalStateException("unhandled flow class at "+hex(n.pc)+" kind="+k);
            JsonObject e=new JsonObject();e.addProperty("site",hex(n.pc));e.addProperty("kind",k);if(tail)e.addProperty("tail_jump",true);
            if(k.equals("conditional")||k.equals("conditional_likely")||k.equals("unconditional_branch")||k.equals("jump")||k.equals("call"))e.addProperty("target",hex(target));
            if(k.equals("conditional")||k.equals("conditional_likely")||k.equals("call")||k.equals("computed_call"))e.addProperty("fallthrough",hex(fall));
            if(k.equals("conditional_likely"))e.addProperty("not_taken_annuls_delay_slot",true);edges.add(e);
        }
        req(seen.size()+PADDING.size()==(END-START)/4,"reachable CFG plus pinned padding does not cover every word in the exact interval: "+seen.size());
        Set<String> foundSwitches=new TreeSet<>();boolean terminal=false;
        for(JsonElement e:edges){JsonObject edge=e.getAsJsonObject();String k=edge.get("kind").getAsString();if(k.equals("switch"))foundSwitches.add(edge.get("site").getAsString());if(k.equals("return")||edge.has("tail_jump"))terminal=true;}
        req(foundSwitches.equals(SWITCHES.keySet()),"computed jump sites differ from pinned switch profile");
        req(SWITCHES.isEmpty()||terminal,"switch CFG has no return or tail terminal");
        for(SwitchPin pin:SWITCHES.values()) {
            long guard=Long.parseUnsignedLong(pin.guard,16),site=Long.parseUnsignedLong(pin.site,16);
            req(Boolean.FALSE.equals(seen.get(guard)),"switch bound is not reached in ordinary context at "+pin.guard);
            for(long pc=guard;pc<=site;pc+=4)req(seen.containsKey(pc),"switch bounds region is not fully reached at "+hex(pc));
            for(JsonElement e:edges){JsonObject edge=e.getAsJsonObject();if(edge.has("targets")){for(JsonElement t:edge.getAsJsonArray("targets")){long a=Long.parseUnsignedLong(t.getAsString(),16);req(!(guard<a&&a<=site+4),"flow bypasses switch bound at "+edge.get("site"));}}else if(edge.has("target")){long a=Long.parseUnsignedLong(edge.get("target").getAsString(),16);req(!(guard<a&&a<=site+4),"flow bypasses switch bound at "+edge.get("site"));}}
        }
        for(long pc=START;pc<END;pc+=4){req(seen.containsKey(pc)!=PADDING.contains(pc),"CFG reachability differs from the pinned padding set at "+hex(pc));}
        JsonArray addresses=new JsonArray();for(long pc:seen.keySet())addresses.add(hex(pc));
        JsonObject out=new JsonObject();out.addProperty("instruction_count_including_delay_slots",seen.size());out.addProperty("body_end_inclusive",hex(seen.lastKey()));out.add("instruction_addresses",addresses);out.add("edges",edges);out.add("delay_breaks",breaks);out.addProperty("branch_likely_scope","For conditional-likely branches, the static union includes the delay instruction on the taken path and the pc+8 successor on the not-taken path; the not-taken path annuls the delay instruction. This is a structural reachability union, not path-by-path execution.");return out;
    }
    private void checkCandidateFlowProfile(JsonObject cfg, byte[] raw) {
        Map<String,String> actualCalls=new TreeMap<>(); int likely=0;
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject edge=e.getAsJsonObject(); String kind=edge.get("kind").getAsString();
            if(kind.equals("call"))actualCalls.put(edge.get("site").getAsString(),edge.get("target").getAsString());
            if(kind.equals("conditional_likely"))likely++;

        }
        Set<String> ccalls=new TreeSet<>(); Map<String,String> tails=new TreeMap<>();
        for(JsonElement e:cfg.getAsJsonArray("edges")){JsonObject edge=e.getAsJsonObject();String kind=edge.get("kind").getAsString();
            if(kind.equals("computed_call"))ccalls.add(edge.get("site").getAsString());
            if(edge.has("tail_jump"))tails.put(edge.get("site").getAsString(),edge.get("target").getAsString());}
        Set<String> found=new TreeSet<>(); for(JsonElement e:cfg.getAsJsonArray("delay_breaks"))found.add(e.getAsString());
        req(ccalls.equals(COMPUTED_CALLS),"computed call sites differ from the pinned profile: "+ccalls);
        req(tails.equals(TAIL_JUMPS),"tail jump sites/targets differ from the pinned profile: "+tails);
        req(found.equals(DELAY_BREAKS),"delay-slot BREAK sites differ from the pinned profile: "+found);
        for(String t:tails.values()){Function tf=currentProgram.getFunctionManager().getFunctionAt(at(Long.parseUnsignedLong(t,16)));req(tf!=null,"tail jump target is not a saved function entry: "+t);}
        req(actualCalls.equals(EXPECTED_CALLS),"outgoing JAL sites/targets differ from the pinned raw profile");
        req(likely==LIKELY_COUNT,"branch-likely site count differs from the pinned profile; re-review taken-delay/not-taken-annul semantics");
        Set<Long> zeros=new TreeSet<>(); for(long pc=START;pc<END;pc+=4)if(wordAt(raw,pc)==0&&!PADDING.contains(pc))zeros.add(pc);
        req(zeros.equals(ZERO_WORDS),"reachable zero-word set differs from the pinned profile: "+zeros);
    }
    private Set<String> functionSet(Set<Function> functions) {
        Set<String> out=new TreeSet<>(); for(Function f:functions)out.add(canonical(f.getEntryPoint())); return out;
    }
    private Map<String,Set<String>> calledGraph() throws Exception {
        Map<String,Set<String>> out=new TreeMap<>(); for(Function f:currentProgram.getFunctionManager().getFunctions(true))out.put(canonical(f.getEntryPoint()),functionSet(f.getCalledFunctions(monitor))); return out;
    }
    private Map<String,Set<String>> callerGraph() throws Exception {
        Map<String,Set<String>> out=new TreeMap<>(); for(Function f:currentProgram.getFunctionManager().getFunctions(true))out.put(canonical(f.getEntryPoint()),functionSet(f.getCallingFunctions(monitor))); return out;
    }
    private Set<String> referenceSnapshot() {
        Set<String> out=new TreeSet<>();
        for(Instruction i:currentProgram.getListing().getInstructions(true))for(Reference r:i.getReferencesFrom())out.add(referenceKey(r));
        for(Data d:currentProgram.getListing().getDefinedData(true))for(Reference r:d.getReferencesFrom())out.add(referenceKey(r));
        return out;
    }
    private String referenceKey(Reference r) { return canonical(r.getFromAddress())+"|"+canonical(r.getToAddress())+"|"+r.getReferenceType()+"|"+r.getSource(); }
    private Set<String> expectedNewFlowReferences(JsonObject cfg) {
        Set<String> out=new TreeSet<>();
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject x=e.getAsJsonObject(); String k=x.get("kind").getAsString(); if(k.equals("return")||k.equals("computed_call"))continue;
            if(k.equals("switch")){SwitchPin pin=SWITCHES.get(x.get("site").getAsString());for(JsonElement t:x.getAsJsonArray("targets"))out.add(pin.site+"|"+t.getAsString()+"|COMPUTED_JUMP|"+pin.referenceSources.get(Long.parseUnsignedLong(t.getAsString(),16)));continue;}
            String type=(k.equals("call"))?"UNCONDITIONAL_CALL":x.has("tail_jump")?TAIL_FLOW.getOrDefault(x.get("site").getAsString(),TAIL_REF_TYPE):(k.equals("unconditional_branch")||k.equals("jump"))?"UNCONDITIONAL_JUMP":"CONDITIONAL_JUMP";
            out.add(x.get("site").getAsString()+"|"+x.get("target").getAsString()+"|"+type+"|DEFAULT");
        }
        return out;
    }
    private void checkDecoderFlow(JsonObject cfg) {
        for(JsonElement e:cfg.getAsJsonArray("edges")) {
            JsonObject edge=e.getAsJsonObject(); long pc=Long.parseUnsignedLong(edge.get("site").getAsString(),16); Instruction ins=currentProgram.getListing().getInstructionAt(at(pc));
            req(ins!=null,"raw CFG transfer has no decoded instruction at "+hex(pc)); FlowType actual=ins.getFlowType(); String kind=edge.get("kind").getAsString();
            Address[] targets=ins.getFlows();
            if(kind.equals("conditional")||kind.equals("conditional_likely")) {
                req(actual.isJump()&&actual.isConditional()&&targets.length==1,"Ghidra does not classify raw conditional branch consistently at "+hex(pc));
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra conditional target differs from raw-word target at "+hex(pc));
                req(ins.getFallThrough()!=null&&ins.getFallThrough().getOffset()==Long.parseUnsignedLong(edge.get("fallthrough").getAsString(),16),"Ghidra conditional fallthrough/delay-slot address differs at "+hex(pc));
            } else if(kind.equals("unconditional_branch")||kind.equals("jump")) {
                if(edge.has("tail_jump")) {
                    String fts=actual.toString(); req(((fts.equals("UNCONDITIONAL_JUMP")&&actual.isJump())||(fts.equals("CALL_TERMINATOR")&&actual.isTerminal()))&&!actual.isConditional()&&!actual.isComputed()&&targets.length==1&&targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra does not classify raw tail jump consistently at "+hex(pc)+" flow="+actual+" targets="+Arrays.toString(targets)+" insn="+ins); TAIL_FLOW.put(hex(pc),fts);
                } else
                req(actual.isJump()&&!actual.isConditional()&&!actual.isComputed()&&targets.length==1,"Ghidra does not classify raw direct jump consistently at "+hex(pc)+" flow="+actual+" targets="+Arrays.toString(targets)+" insn="+ins);
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra direct-jump target differs from raw-word target at "+hex(pc));
            } else if(kind.equals("call")) {
                req(actual.isCall()&&!actual.isComputed()&&targets.length==1,"Ghidra does not classify raw direct call consistently at "+hex(pc));
                req(targets[0].getOffset()==Long.parseUnsignedLong(edge.get("target").getAsString(),16),"Ghidra direct-call target differs from raw-word target at "+hex(pc));
                req(ins.getFallThrough()!=null&&ins.getFallThrough().getOffset()==Long.parseUnsignedLong(edge.get("fallthrough").getAsString(),16),"Ghidra direct-call fallthrough/delay-slot address differs at "+hex(pc)+" fall="+ins.getFallThrough()+" expected="+edge.get("fallthrough").getAsString()+" insn="+ins);
            } else if(kind.equals("computed_call")) {
                req(actual.isCall()&&actual.isComputed()&&targets.length==0,"Ghidra does not classify raw computed call consistently at "+hex(pc));
                req(ins.getFallThrough()!=null&&ins.getFallThrough().getOffset()==Long.parseUnsignedLong(edge.get("fallthrough").getAsString(),16),"Ghidra computed-call fallthrough/delay-slot address differs at "+hex(pc));
            } else if(kind.equals("switch")) {
                req(actual.isJump()&&actual.isComputed()&&!actual.isConditional(),"Ghidra switch classification differs at "+hex(pc));
                Set<Long> expected=new TreeSet<>(SWITCHES.get(hex(pc)).targets),found=new TreeSet<>();for(Address t:targets)found.add(t.getOffset());
                req(found.equals(expected),"Ghidra switch targets differ from pinned table at "+hex(pc));
            } else if(kind.equals("return")) {
                req(actual.isTerminal()&&ins.getMnemonicString().toLowerCase(Locale.ROOT).startsWith("jr"),"Ghidra return classification differs from exact JR RA word at "+hex(pc));
            }
        }
    }
    private void write(Path p,JsonObject o)throws Exception{Files.createDirectories(p.getParent());Files.writeString(p,new GsonBuilder().setPrettyPrinting().create().toJson(o)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);}
}
