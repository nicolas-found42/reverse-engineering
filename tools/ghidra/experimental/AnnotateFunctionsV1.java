//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * Experimental guarded annotation (V1). One transaction applies a SHA-pinned plan of function plate comments and candidate
 * renames to saved functions. A rename is allowed only on a function whose name is still the default FUN_xxxxxxxx; a comment
 * only on a function without one. Afterwards every function's entry, body and instruction count must be unchanged and only
 * the planned names and comments may differ; any drift rolls the transaction back. No identity claim is made.
 */
public class AnnotateFunctionsV1 extends GhidraScript {
    private static final String EXE_SHA = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
    private static final String LANGUAGE = "r5900:LE:32:default";

    private void req(boolean ok, String message) { if (!ok) throw new IllegalStateException(message); }
    private String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)); }
    private Address at(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
    private String hex(long v) { return String.format("%08x", v); }

    private static final class Snap { String name; String body; long size; int instructions; String comment; }

    private Map<String,Snap> snapshot() {
        Map<String,Snap> out = new TreeMap<>(); Listing l = currentProgram.getListing();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            Snap s = new Snap(); s.name = f.getName(); s.body = f.getBody().toString(); s.size = f.getBody().getNumAddresses();
            int n = 0; for (Instruction i : l.getInstructions(f.getBody(), true)) n++; s.instructions = n; s.comment = f.getComment();
            out.put(hex(f.getEntryPoint().getOffset()), s);
        }
        return out;
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
            req(plan.get("schema_version").getAsInt() == 1 && EXE_SHA.equals(plan.get("executable_sha256").getAsString()), "plan schema or executable pin differs");
            JsonArray entries = plan.getAsJsonArray("entries");
            Map<String,Snap> before = snapshot();
            Set<String> seen = new HashSet<>(); Map<String,String> renames = new TreeMap<>(), comments = new TreeMap<>();
            for (JsonElement e : entries) {
                JsonObject o = e.getAsJsonObject(); String entry = o.get("entry").getAsString();
                req(seen.add(entry), "duplicate plan entry " + entry); req(before.containsKey(entry), "no saved function at " + entry);
                req(before.get(entry).comment == null || before.get(entry).comment.isEmpty(), "function already has a comment: " + entry);
                comments.put(entry, o.get("comment").getAsString());
                if (o.has("rename")) {
                    req(before.get(entry).name.equals("FUN_" + entry), "rename target is not a default-named function: " + entry);
                    renames.put(entry, o.get("rename").getAsString());
                }
            }
            Set<String> names = new HashSet<>(); for (Snap s : before.values()) names.add(s.name);
            for (String n : renames.values()) req(names.add(n), "rename would duplicate an existing function name: " + n);
            int tx = currentProgram.startTransaction("guarded function annotation of " + entries.size()); boolean commit = false;
            try {
                FunctionManager fm = currentProgram.getFunctionManager();
                for (String entry : comments.keySet()) {
                    Function f = fm.getFunctionAt(at(Long.parseUnsignedLong(entry, 16))); req(f != null, "function vanished at " + entry);
                    f.setComment(comments.get(entry));
                    if (renames.containsKey(entry)) f.setName(renames.get(entry), SourceType.USER_DEFINED);
                }
                Map<String,Snap> after = snapshot();
                req(after.keySet().equals(before.keySet()), "function set changed");
                for (String entry : before.keySet()) {
                    Snap b = before.get(entry), a = after.get(entry);
                    req(a.body.equals(b.body) && a.size == b.size && a.instructions == b.instructions, "function body changed at " + entry);
                    String expectName = renames.getOrDefault(entry, b.name); req(a.name.equals(expectName), "unplanned or missing name change at " + entry);
                    String expectComment = comments.containsKey(entry) ? comments.get(entry) : b.comment;
                    req(Objects.equals(a.comment, expectComment), "unplanned or missing comment change at " + entry);
                }
                commit = true;
            } finally { currentProgram.endTransaction(tx, commit); }
            status = "annotated"; out.addProperty("function_count_after", currentProgram.getFunctionManager().getFunctionCount());
            out.addProperty("comments_applied", comments.size()); out.addProperty("renames_applied", renames.size());
        } catch (Throwable t) {
            out.addProperty("failure", t.getClass().getSimpleName() + ": " + t.getMessage());
        } finally {
            out.addProperty("status", status);
            Files.writeString(Paths.get(args[0]), new GsonBuilder().setPrettyPrinting().create().toJson(out) + "\n");
        }
    }
}
