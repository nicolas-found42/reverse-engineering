//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.pcode.JumpTable;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;
import ghidra.framework.Application;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;

/** Guarded, single-function jump-table override and export for the verified ELF dispatch. */
public class VerifiedJumpTableOverride extends GhidraScript {
  private static final String EXPECTED_EXECUTABLE_SHA256 = "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95";
  private static final String EXPECTED_NATIVE_SHA256 = "cd6d7e92061f7e47c7eaa86f82cb7045b4c3e624d1764832283f00b8dca57acd";
  private static final String ENTRY = "0017f510";
  private static final String BRANCH = "0017f5dc";
  private static final String TABLE = "0025cb60";
  private static final String TABLE_BYTES = "78f61700e8f51700f8f5170028f6170008f6170018f6170028f61700";
  private static final String[] TARGETS = {"0017f678", "0017f5e8", "0017f5f8", "0017f628", "0017f608", "0017f618", "0017f628"};

  private String hex(byte[] bytes) {
    StringBuilder out = new StringBuilder(bytes.length * 2);
    for (byte b : bytes) out.append(String.format("%02x", b & 0xff));
    return out.toString();
  }

  private void checkBytes(String address, String expected) throws Exception {
    byte[] bytes = new byte[expected.length() / 2];
    currentProgram.getMemory().getBytes(toAddr(address), bytes);
    if (!hex(bytes).equals(expected))
      throw new IllegalStateException("Machine-code guard failed at " + address + ": " + hex(bytes));
  }

  private boolean has(String c, String regex) {
    return Pattern.compile(regex, Pattern.DOTALL).matcher(c).find();
  }

  private String sha256(byte[] bytes) throws Exception {
    byte[] hash = MessageDigest.getInstance("SHA-256").digest(bytes);
    return hex(hash);
  }

  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 1) throw new IllegalArgumentException("output directory");
    Path output = Paths.get(args[0]).toAbsolutePath();
    Files.createDirectories(output.getParent());
    Files.createDirectory(output);

    String executableSha = currentProgram.getExecutableSHA256();
    if (!EXPECTED_EXECUTABLE_SHA256.equals(executableSha))
      throw new IllegalStateException("Executable SHA-256 guard failed: " + executableSha);
    if (!currentProgram.getLanguageID().toString().equals("r5900:LE:32:default"))
      throw new IllegalStateException("Expected R5900 language profile");
    Path nativePath = Application.getOSFile("Decompiler", "decompile").toPath();
    String nativeSha = sha256(Files.readAllBytes(nativePath));
    if (!EXPECTED_NATIVE_SHA256.equals(nativeSha))
      throw new IllegalStateException("Private native decompiler SHA-256 guard failed: " + nativeSha);
    Path scriptPath = Paths.get(getSourceFile().getAbsolutePath());
    String scriptSha = sha256(Files.readAllBytes(scriptPath));
    Path patchPath = scriptPath.getParent().resolve("ordered-jumptable-override.patch");
    String patchSha = sha256(Files.readAllBytes(patchPath));
    checkBytes(TABLE, TABLE_BYTES);
    checkBytes("0017f52c", "01001324"); // li s3,1
    checkBytes("0017f59c", "80881300"); // sll s1,s3,2
    checkBytes("0017f5d0", "2600023c"); // lui v0,0x26
    checkBytes("0017f5d4", "21105100"); // addu v0,v0,s1
    checkBytes("0017f5d8", "60cb428c"); // lw v0,-0x34a0(v0)
    checkBytes(BRANCH, "08004000");      // jr v0
    checkBytes("0017f6c8", "01007326"); // addiu s3,s3,1
    checkBytes("0017f6cc", "0700622a"); // slti v0,s3,7
    checkBytes("0017f6d0", "b3ff4014"); // bne v0,zero,loop
    checkBytes("0017f6d4", "80881300"); // delay-slot sll s1,s3,2
    checkBytes("0017f5f0", "01000524"); // selector 1 sets a1=1
    checkBytes("0017f600", "02000524"); // selector 2 sets a1=2
    checkBytes("0017f610", "03000524"); // selector 4 sets a1=3
    checkBytes("0017f620", "04000524"); // selector 5 sets a1=4
    checkBytes("0017f62c", "05000524"); // shared selectors 3 and 6 set a1=5

    Function function = getFunctionAt(toAddr(ENTRY));
    if (function == null || !function.getEntryPoint().equals(toAddr(ENTRY)))
      throw new IllegalStateException("Expected function entry not found: " + ENTRY);
    if (!function.getBody().contains(toAddr(BRANCH)))
      throw new IllegalStateException("Computed branch lies outside the guarded function body");
    Instruction dispatch = currentProgram.getListing().getInstructionAt(toAddr(BRANCH));
    if (dispatch == null || !dispatch.getFlowType().isComputed())
      throw new IllegalStateException("Expected computed branch not found: " + BRANCH);

    ArrayList<Address> destinations = new ArrayList<>();
    for (String target : TARGETS) {
      Address address = toAddr(target);
      if (currentProgram.getListing().getInstructionAt(address) == null)
        throw new IllegalStateException("Target instruction missing: " + target);
      dispatch.addOperandReference(0, address, RefType.COMPUTED_JUMP, SourceType.USER_DEFINED);
      destinations.add(address);
    }
    JumpTable table = new JumpTable(toAddr(BRANCH), destinations, true, 0);
    java.lang.reflect.Field overrideField = JumpTable.class.getDeclaredField("override");
    overrideField.setAccessible(true);
    Object basicOverride = overrideField.get(table);
    Address[] encodedTargets = (Address[]) basicOverride.getClass().getMethod("getDestinations").invoke(basicOverride);
    if (encodedTargets.length != TARGETS.length)
      throw new IllegalStateException("JumpTable API changed destination count: " + encodedTargets.length);
    for (int i = 0; i < TARGETS.length; i++)
      if (!encodedTargets[i].equals(toAddr(TARGETS[i])))
        throw new IllegalStateException("JumpTable API changed destination order at index " + i);
    table.writeOverride(function);

    DecompInterface decompiler = new DecompInterface();
    String c;
    try {
      decompiler.setSimplificationStyle("decompile");
      decompiler.toggleCCode(true);
      decompiler.toggleSyntaxTree(true);
      if (!decompiler.openProgram(currentProgram))
        throw new IllegalStateException("Cannot open decompiler: " + decompiler.getLastMessage());
      DecompileResults result = decompiler.decompileFunction(function, 60, monitor);
      if (!result.decompileCompleted() || result.getDecompiledFunction() == null)
        throw new IllegalStateException("Decompile failed: " + result.getErrorMessage());
      c = result.getDecompiledFunction().getC();
    } finally {
      decompiler.dispose();
    }

    List<String> assertionNames = Arrays.asList(
      "generated C initializes loop selector to one",
      "generated C scales selector by four",
      "generated C keeps upper bound guard",
      "selector 1 dispatches with argument 1",
      "selector 2 dispatches with argument 2",
      "selector 4 dispatches with argument 3",
      "selector 5 dispatches with argument 4",
      "shared-target selectors 3 and 6 dispatch with argument 5");
    List<Boolean> assertionResults = Arrays.asList(
      has(c, "uVar5\\s*=\\s*1;"),
      has(c, "iVar4\\s*=\\s*4;"),
      has(c, "6\\s*<\\s*uVar5"),
      has(c, "case\\s+4\\s*:\\s*uVar2\\s*=\\s*1;"),
      has(c, "case\\s+8\\s*:\\s*uVar2\\s*=\\s*2;"),
      has(c, "case\\s+0x10\\s*:\\s*uVar2\\s*=\\s*3;"),
      has(c, "case\\s+0x14\\s*:\\s*uVar2\\s*=\\s*4;"),
      has(c, "default\\s*:\\s*uVar2\\s*=\\s*5;"));
    for (int i=0; i<assertionResults.size(); i++)
      if (!assertionResults.get(i))
        throw new IllegalStateException("C validation failed: " + assertionNames.get(i));

    Path functions = Files.createDirectory(output.resolve("functions"));
    byte[] source = c.getBytes(StandardCharsets.UTF_8);
    Files.write(functions.resolve(ENTRY + ".c"), source);
    JsonObject manifest = new JsonObject();
    manifest.addProperty("schema_version", 1);
    manifest.addProperty("status", "generated");
    manifest.addProperty("program", currentProgram.getName());
    manifest.addProperty("executable_sha256", executableSha);
    manifest.addProperty("ghidra_version", getGhidraVersion());
    manifest.addProperty("language", currentProgram.getLanguageID().toString());
    manifest.addProperty("native_decompiler_path", nativePath.toAbsolutePath().toString());
    manifest.addProperty("native_decompiler_sha256", nativeSha);
    manifest.addProperty("script_sha256", scriptSha);
    manifest.addProperty("patch_sha256", patchSha);
    manifest.addProperty("function_entry", ENTRY);
    manifest.addProperty("function_name", function.getName());
    manifest.addProperty("computed_branch", BRANCH);
    manifest.addProperty("table_address", TABLE);
    manifest.addProperty("table_bytes_hex", TABLE_BYTES);
    manifest.addProperty("selector_domain", "s3=1..6; iVar4=s3*4 => 4,8,12,16,20,24");
    manifest.addProperty("override_destination_count", encodedTargets.length);
    manifest.addProperty("source_sha256", sha256(source));
    manifest.addProperty("claim_limits", "Guarded pseudocode export; not recovered original source or proof of whole-program equivalence.");
    JsonArray targetArray = new JsonArray();
    for (int i = 0; i < TARGETS.length; i++) {
      JsonObject target = new JsonObject();
      target.addProperty("table_index", i);
      target.addProperty("selector", i * 4);
      target.addProperty("target", TARGETS[i]);
      targetArray.add(target);
    }
    manifest.add("table_targets", targetArray);
    JsonArray checks = new JsonArray();
    for (int i=0; i<assertionNames.size(); i++) {
      JsonObject check = new JsonObject();
      check.addProperty("assertion", assertionNames.get(i));
      check.addProperty("passed", assertionResults.get(i));
      checks.add(check);
    }
    manifest.add("validation", checks);
    Files.writeString(output.resolve("manifest.json"), manifest.toString() + "\n", StandardCharsets.UTF_8);
    println("VERIFIED_OVERRIDE status=generated entry=" + ENTRY + " outputs=" + output + " destinations=" + encodedTargets.length);
  }
}
