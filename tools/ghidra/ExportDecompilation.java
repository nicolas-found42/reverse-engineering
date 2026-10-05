// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Read-only batch pseudocode export; success records are not equivalence proofs. */
public class ExportDecompilation extends GhidraScript {
    private String hash(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args.length > 3)
            throw new IllegalArgumentException("output directory [timeout seconds] [comma-separated entry addresses]");
        int timeout = args.length > 1 ? Integer.parseInt(args[1]) : 30;
        if (timeout < 1 || timeout > 600) throw new IllegalArgumentException("timeout outside 1..600");
        Set<String> selected = new HashSet<>();
        if (args.length > 2) {
            for (String token : args[2].split(",", -1)) {
                String address = token.trim().toLowerCase(Locale.ROOT);
                if (!address.matches("[0-9a-f]{8}"))
                    throw new IllegalArgumentException("Selected addresses must be eight hexadecimal digits");
                selected.add(address);
            }
        }
        Path out = Paths.get(args[0]).toAbsolutePath();
        Files.createDirectories(out.getParent());
        Files.createDirectory(out); // never overwrite a previous run
        Path sources = Files.createDirectory(out.resolve("functions"));
        JsonObject manifest = new JsonObject();
        manifest.addProperty("schema_version", 1);
        manifest.addProperty("program", currentProgram.getName());
        manifest.addProperty("language", currentProgram.getLanguageID().toString());
        manifest.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        manifest.addProperty("ghidra_version", getGhidraVersion());
        manifest.addProperty("inventory_count", currentProgram.getFunctionManager().getFunctionCount());
        manifest.addProperty("timeout_seconds", timeout);
        manifest.addProperty("scope", selected.isEmpty() ? "all saved functions" : "selected entry addresses");
        manifest.addProperty("status", "incomplete");
        manifest.addProperty("terminal_reason", "export did not finish");
        manifest.addProperty("claim_limits", "Generated pseudocode only. Successful decompilation does not prove recovered original source, correct types, complete code discovery, recompilability, or behavioral equivalence.");
        JsonArray rows = new JsonArray();
        manifest.add("functions", rows);
        DecompInterface decompiler = new DecompInterface();
        // Opt-in: FR2_DECOMP_OPTIONS=program loads the program's decompiler options, which respect read-only and constant data.
        boolean programOptions = "program".equals(System.getenv("FR2_DECOMP_OPTIONS"));
        manifest.addProperty("decompiler_options", programOptions ? "program" : "default");
        if (programOptions) {
            DecompileOptions options = new DecompileOptions();
            options.grabFromProgram(currentProgram);
            decompiler.setOptions(options);
        }
        int successes = 0, failures = 0;
        Set<String> visited = new HashSet<>();
        boolean normalCompletion = false;
        try {
            decompiler.setSimplificationStyle("decompile");
            decompiler.toggleCCode(true);
            decompiler.toggleSyntaxTree(true);
            if (!decompiler.openProgram(currentProgram))
                throw new IllegalStateException("Cannot open decompiler: " + decompiler.getLastMessage());
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                monitor.checkCancelled();
                String entry = f.getEntryPoint().toString();
                if (!selected.isEmpty() && !selected.contains(entry)) continue;
                visited.add(entry);
                JsonObject row = new JsonObject();
                row.addProperty("entry", entry);
                row.addProperty("name", f.getName());
                row.addProperty("body_bytes", f.getBody().getNumAddresses());
                row.addProperty("external", f.isExternal());
                row.addProperty("thunk", f.isThunk());
                rows.add(row);
                long started = System.nanoTime();
                try {
                    DecompileResults result = decompiler.decompileFunction(f, timeout, monitor);
                    row.addProperty("completed", result.decompileCompleted());
                    row.addProperty("message", result.getErrorMessage());
                    DecompiledFunction df = result.getDecompiledFunction();
                    if (!result.decompileCompleted() || df == null || df.getC() == null || df.getC().isBlank()) {
                        row.addProperty("status", "failed");
                        failures++;
                    } else {
                        String filename = entry + ".c";
                        byte[] bytes = df.getC().getBytes(StandardCharsets.UTF_8);
                        Path temporary = Files.createTempFile(sources, entry + "-", ".partial");
                        try {
                            Files.write(temporary, bytes, StandardOpenOption.TRUNCATE_EXISTING);
                            Files.move(temporary, sources.resolve(filename), StandardCopyOption.ATOMIC_MOVE);
                        } finally {
                            Files.deleteIfExists(temporary);
                        }
                        row.addProperty("status", "generated");
                        row.addProperty("path", "functions/" + filename);
                        row.addProperty("sha256", hash(bytes));
                        row.addProperty("bytes", bytes.length);
                        successes++;
                    }
                } catch (Exception e) {
                    row.addProperty("status", "failed");
                    row.addProperty("message", e.getClass().getSimpleName() + ": " + e.getMessage());
                    failures++;
                }
                row.addProperty("milliseconds", (System.nanoTime() - started) / 1000000);
                if (rows.size() % 100 == 0) println("DECOMP_PROGRESS processed=" + rows.size() + " generated=" + successes + " failed=" + failures);
            }
            normalCompletion = true;
            manifest.addProperty("terminal_reason", "function iteration finished");
        } catch (Exception e) {
            manifest.addProperty("terminal_reason", e.getClass().getSimpleName() + ": " + e.getMessage());
            throw e;
        } finally {
            try {
                decompiler.dispose();
            } catch (Exception cleanup) {
                normalCompletion = false;
                manifest.addProperty("cleanup_warning", cleanup.getClass().getSimpleName() + ": " + cleanup.getMessage());
            }
            Set<String> missing = new TreeSet<>(selected);
            missing.removeAll(visited);
            JsonArray absent = new JsonArray();
            for (String entry : missing) absent.add(entry);
            manifest.add("missing_selected_entries", absent);
            manifest.addProperty("status", normalCompletion && failures == 0 && missing.isEmpty() ? "generated" : "incomplete");
            manifest.addProperty("processed", rows.size());
            manifest.addProperty("generated", successes);
            manifest.addProperty("failed", failures);
            Files.writeString(out.resolve("manifest.json"), new GsonBuilder().setPrettyPrinting().create().toJson(manifest) + "\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        }
        println("DECOMP_EXPORT processed=" + rows.size() + " generated=" + successes + " failed=" + failures + " output=" + out);
    }
}
