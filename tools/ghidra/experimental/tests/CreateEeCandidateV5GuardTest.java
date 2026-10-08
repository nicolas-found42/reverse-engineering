import com.google.gson.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.lang.reflect.*;
import java.util.*;

/** Executes the production guard with real Ghidra address/flow classes and
 * interface doubles. No program database or game bytes are loaded or changed. */
public class CreateEeCandidateV5GuardTest extends CreateEeCandidateV5 {
    private static final AddressSpace RAM = new GenericAddressSpace("ram", 32, AddressSpace.TYPE_RAM, 0);
    private final Map<Long,Instruction> instructions = new HashMap<>();
    private FlowType calleeFlow = RefType.UNCONDITIONAL_JUMP;
    private boolean calleePresent = true, calleeDecoded = true;
    private FlowType callFlow = RefType.CALL_TERMINATOR;
    private Address fallthrough = null;
    private Address[] targets = {a(0x2000)};
    private int length = 4;
    private static int checks;

    private static Address a(long pc) { return RAM.getAddress(pc); }
    @SuppressWarnings("unchecked")
    private static <T> T proxy(Class<T> type, InvocationHandler handler) {
        return (T)Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[]{type}, handler);
    }
    private static Object unexpected(Method method) { throw new AssertionError("Unexpected API: " + method); }
    private static void field(Object object, String name, Object value) throws Exception {
        Class<?> type = object.getClass();
        while (type != null) {
            try { Field f = type.getDeclaredField(name); f.setAccessible(true); f.set(object, value); return; }
            catch (NoSuchFieldException e) { type = type.getSuperclass(); }
        }
        throw new NoSuchFieldException(name);
    }
    private Object invoke(String name, Object... arguments) throws Exception {
        for (Method m : CreateEeCandidateV5.class.getDeclaredMethods()) if (m.getName().equals(name)) {
            m.setAccessible(true);
            try { return m.invoke(this, arguments); }
            catch (InvocationTargetException e) { throw (Exception)e.getCause(); }
        }
        throw new NoSuchMethodException(name);
    }
    private CreateEeCandidateV5GuardTest() {
        AddressFactory factory = new DefaultAddressFactory(new AddressSpace[]{RAM}, RAM);
        Instruction calleeInstruction = proxy(Instruction.class, (p,m,args) ->
            m.getName().equals("getFlowType") ? calleeFlow : unexpected(m));
        AddressSet calleeBody = new AddressSet(a(0x2000), a(0x2003));
        Function callee = proxy(Function.class, (p,m,args) ->
            m.getName().equals("getBody") ? calleeBody : unexpected(m));
        Listing listing = proxy(Listing.class, (p,m,args) -> {
            if (m.getName().equals("getInstructionAt")) return instructions.get(((Address)args[0]).getOffset());
            if (m.getName().equals("getInstructions")) {
                Iterator<Instruction> it = (calleeDecoded ? List.of(calleeInstruction) : List.<Instruction>of()).iterator();
                return proxy(InstructionIterator.class, (q,n,x) -> {
                    if (n.getName().equals("hasNext")) return it.hasNext();
                    if (n.getName().equals("next")) return it.next();
                    return unexpected(n);
                });
            }
            return unexpected(m);
        });
        FunctionManager manager = proxy(FunctionManager.class, (p,m,args) ->
            m.getName().equals("getFunctionAt") ? (calleePresent && args[0].equals(a(0x2000)) ? callee : null) : unexpected(m));
        currentProgram = proxy(Program.class, (p,m,args) -> {
            switch (m.getName()) {
                case "getAddressFactory": return factory;
                case "getListing": return listing;
                case "getFunctionManager": return manager;
                default: return unexpected(m);
            }
        });
        Instruction call = proxy(Instruction.class, (p,m,args) -> {
            switch (m.getName()) {
                case "getFlowType": return callFlow;
                case "getFallThrough": return fallthrough;
                case "getFlows": return targets;
                case "getLength": return length;
                default: return unexpected(m);
            }
        });
        instructions.put(0x1000L, call);
        instructions.put(0x1010L, call);
    }
    private static Object seed() throws Exception {
        Class<?> type = Class.forName("CreateEeCandidateV5$SeedCfg");
        Constructor<?> constructor = type.getDeclaredConstructor(); constructor.setAccessible(true);
        Object seed = constructor.newInstance();
        field(seed, "start", 0x1000L); field(seed, "end", 0x1020L); field(seed, "raw", new byte[32]);
        Field calls = type.getDeclaredField("calls"); calls.setAccessible(true);
        @SuppressWarnings("unchecked") Map<String,String> pins = (Map<String,String>)calls.get(seed);
        pins.put("00001000", "00002000"); pins.put("00001010", "00002000");
        Field zeros = type.getDeclaredField("zeros"); zeros.setAccessible(true);
        @SuppressWarnings("unchecked") Set<Long> zeroPins = (Set<Long>)zeros.get(seed);
        zeroPins.addAll(List.of(0x1008L, 0x1018L));
        return seed;
    }
    private void body(boolean accepted, String reason, Object seed, AddressSet body) throws Exception {
        boolean actual = (Boolean)invoke("bodyDeltaIsPinnedNoreturnNops", new AddressSet(a(0x1000), a(0x101f)), body, seed);
        check(actual == accepted, reason);
    }
    private static AddressSet omit(long first, long last) {
        AddressSet body = new AddressSet(a(0x1000), a(0x101f)); body.deleteRange(a(first), a(last)); return body;
    }
    private static void check(boolean ok, String reason) {
        checks++; if (!ok) throw new AssertionError(reason);
    }
    private void bodies() throws Exception {
        Object seed = seed(); AddressSet allowed = omit(0x1008, 0x100b);
        body(true, "complete pinned post-delay NOP", seed, allowed);
        AddressSet two = new AddressSet(allowed); two.deleteRange(a(0x1018), a(0x101b));
        body(true, "two independent omissions", seed, two);
        body(false, "no difference", seed, omit(0x1030, 0x1033));
        body(false, "architectural delay slot", seed, omit(0x1004, 0x1007));
        body(false, "following block", seed, omit(0x1008, 0x100f));
        for (long byteAddress = 0x1008; byteAddress <= 0x100b; byteAddress++)
            body(false, "partial NOP omission", seed, omit(byteAddress, byteAddress));
        AddressSet extra = new AddressSet(allowed); extra.add(a(0x1020));
        body(false, "extra byte", seed, extra);
        extra = new AddressSet(allowed);
        extra.add(new GenericAddressSpace("other",32,AddressSpace.TYPE_RAM,1).getAddress(0x1000));
        body(false, "another address space", seed, extra);
        body(false, "missing call site", seed, omit(0x1000, 0x100b));
        Field zeroField = seed.getClass().getDeclaredField("zeros"); zeroField.setAccessible(true);
        @SuppressWarnings("unchecked") Set<Long> zeros = (Set<Long>)zeroField.get(seed);
        zeros.remove(0x1008L); body(false,"missing zero pin",seed,allowed); zeros.add(0x1008L);
        Field callField = seed.getClass().getDeclaredField("calls"); callField.setAccessible(true);
        @SuppressWarnings("unchecked") Map<String,String> calls = (Map<String,String>)callField.get(seed);
        calls.remove("00001000"); body(false,"missing call pin",seed,allowed); calls.put("00001000","00002000");
        byte[] raw = new byte[32]; raw[8] = 1; field(seed,"raw",raw);
        body(false, "nonzero fallthrough", seed, allowed); field(seed,"raw",new byte[32]);
        for (FlowType flow : List.of(RefType.UNCONDITIONAL_CALL, RefType.COMPUTED_CALL_TERMINATOR,
                RefType.CONDITIONAL_CALL_TERMINATOR, RefType.JUMP_TERMINATOR)) {
            callFlow = flow; body(false, "unsupported call flow " + flow, seed, allowed);
        }
        callFlow = RefType.CALL_TERMINATOR;
        fallthrough = a(0x1008); body(false,"terminal fallthrough",seed,allowed); fallthrough = null;
        targets = new Address[]{a(0x2004)}; body(false,"changed target",seed,allowed);
        targets = new Address[]{a(0x2000),a(0x2004)}; body(false,"multiple targets",seed,allowed);
        targets = new Address[]{a(0x2000)};
        length = 8; body(false,"unsupported length",seed,allowed); length = 4;
        calleePresent = false; body(false,"missing callee",seed,allowed); calleePresent = true;
        calleeDecoded = false; body(false,"undecoded callee",seed,allowed); calleeDecoded = true;
        calleeFlow = RefType.TERMINATOR; body(false,"callee return",seed,allowed);
        calleeFlow = RefType.CALL_TERMINATOR; body(false,"callee terminal call",seed,allowed);
        calleeFlow = RefType.UNCONDITIONAL_JUMP;
        instructions.remove(0x1000L); body(false,"missing instruction",seed,allowed);
    }
    private static JsonObject edge(long site, String kind, Long target) {
        JsonObject edge = new JsonObject(); edge.addProperty("site",String.format("%08x",site)); edge.addProperty("kind",kind);
        if (target != null) edge.addProperty("target",String.format("%08x",target)); return edge;
    }
    private void terminal(boolean accepted, String kind, long target, String reason) throws Exception {
        field(this,"END",0x1034L);
        Map<Long,Boolean> seen = new TreeMap<>(); seen.put(0x102cL,false); seen.put(0x1030L,true);
        JsonArray edges = new JsonArray(); edges.add(edge(0x1024,"return",null)); edges.add(edge(0x102c,kind,target));
        try { invoke("checkSwitchTerminal",seen,edges); check(accepted,reason); }
        catch (IllegalStateException e) { check(!accepted,reason); }
    }
    private void terminals() throws Exception {
        terminal(true,"return",0x1024,"last return");
        terminal(true,"jump",0x1024,"shared JR RA");
        terminal(true,"unconditional_branch",0x1024,"shared JR RA branch");
        terminal(false,"jump",0x102c,"last case self-loop");
        terminal(false,"unconditional_branch",0x102c,"last case branch loop");
        terminal(false,"jump",0x1020,"jump to epilogue before JR RA");
        terminal(false,"call",0x1024,"call to return is unsupported");
        terminal(false,"switch",0x1024,"unpinned switch is unsupported");
        terminal(false,"jump",0x2000,"unpinned external terminal");
        JsonArray edges = new JsonArray(); edges.add(edge(0x1024,"return",null));
        try { invoke("checkSwitchTerminal",Map.of(0x102cL,false,0x1030L,true),edges); check(false,"missing terminal edge"); }
        catch (IllegalStateException e) { check(true,"missing terminal edge"); }
    }
    public static void main(String[] args) throws Exception {
        CreateEeCandidateV5GuardTest test = new CreateEeCandidateV5GuardTest(); test.bodies(); test.terminals();
        System.out.println("V5_GUARD_CONTROLS_OK checks=" + checks);
    }
}
