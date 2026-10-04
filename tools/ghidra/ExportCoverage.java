// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Read-only listing coverage, including instructions outside saved functions. */
public class ExportCoverage extends GhidraScript {
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
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected fresh output JSON path");
        JsonObject root = new JsonObject();
        root.addProperty("schema_version", 1);
        root.addProperty("program", currentProgram.getName());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("ghidra_version", getGhidraVersion());
        root.addProperty("inventory_count", currentProgram.getFunctionManager().getFunctionCount());
        root.addProperty("claim_limits", "Listing classification only: undefined bytes need investigation; defined instructions/data and saved functions do not prove correct decoding or complete code discovery. VU/DVP interpretation is separate.");
        JsonArray blocks = new JsonArray();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            monitor.checkCancelled();
            AddressSet extent = new AddressSet(block.getStart(), block.getEnd());
            AddressSet instructions = new AddressSet(), owned = new AddressSet(), data = new AddressSet();
            long count = 0, unownedCount = 0;
            for (Instruction ins : listing.getInstructions(extent, true)) {
                monitor.checkCancelled();
                instructions.addRange(ins.getAddress(), ins.getMaxAddress());
                count++;
                if (fm.getFunctionContaining(ins.getAddress()) == null) unownedCount++;
                else owned.addRange(ins.getAddress(), ins.getMaxAddress());
            }
            for (Data item : listing.getDefinedData(extent, true)) {
                data.addRange(item.getAddress(), item.getMaxAddress());
            }
            AddressSet unowned = instructions.subtract(owned);
            AddressSet undefined = extent.subtract(instructions).subtract(data);
            JsonObject row = new JsonObject();
            row.addProperty("name", block.getName());
            row.addProperty("start", block.getStart().toString());
            row.addProperty("end", block.getEnd().toString());
            row.addProperty("bytes", block.getSize());
            row.addProperty("execute", block.isExecute());
            row.addProperty("instruction_count", count);
            row.addProperty("instruction_bytes", instructions.getNumAddresses());
            row.addProperty("function_instruction_bytes", owned.getNumAddresses());
            row.addProperty("unowned_instruction_count", unownedCount);
            row.addProperty("unowned_instruction_bytes", unowned.getNumAddresses());
            row.addProperty("defined_data_bytes", data.getNumAddresses());
            row.addProperty("undefined_bytes", undefined.getNumAddresses());
            row.add("unowned_instruction_ranges", ranges(unowned));
            row.add("undefined_ranges", ranges(undefined));
            blocks.add(row);
        }
        root.add("blocks", blocks);
        JsonArray bookmarks = new JsonArray();
        java.util.Iterator<Bookmark> iterator = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (iterator.hasNext()) {
            Bookmark bookmark = iterator.next();
            if (!bookmark.getTypeString().equals(BookmarkType.ERROR) && !bookmark.getTypeString().equals(BookmarkType.WARNING)) continue;
            JsonObject row = new JsonObject();
            row.addProperty("address", bookmark.getAddress().toString());
            row.addProperty("type", bookmark.getTypeString());
            row.addProperty("category", bookmark.getCategory());
            row.addProperty("comment", bookmark.getComment());
            bookmarks.add(row);
        }
        root.add("bookmarks", bookmarks);
        Path path = Paths.get(args[0]);
        Files.createDirectories(path.toAbsolutePath().getParent());
        Files.writeString(path, new GsonBuilder().setPrettyPrinting().create().toJson(root) + "\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        println("COVERAGE_EXPORT_OK blocks=" + blocks.size() + " bookmarks=" + bookmarks.size());
    }
}
