# Ghidra bridge file-scope patch

[ghidra-mcp-6.0.0-file-scope.patch](ghidra-mcp-6.0.0-file-scope.patch) modifies
[upstream GhidraMCP](https://github.com/bethington/ghidra-mcp) v6.0.0 at commit
`8cd2078e10b9ba28b188cb84ce5b9051a904b995`. Its Apache-2.0 license is preserved
in [GHIDRA-MCP-LICENSE.txt](GHIDRA-MCP-LICENSE.txt).

Local modifications: headless `open_project` resolves its on-disk project path
through the existing file-root guard; `restore_project` resolves both its archive
input and destination parent before touching either path. Existing canonical
path/symlink resolution and access-denied responses are reused.

Build from that exact upstream revision in a separate source copy, apply this
patch with `git apply`, and rebuild the extension against Ghidra 12.1.4 using
`mvn clean package assembly:single -DskipTests -Dghidra.version=12.1.4` after
installing the required Ghidra JARs in the local Maven repository. The installed
extension properties must name the same Ghidra host version. Record the built
JAR path/hash in the ignored machine configuration; the launcher checks it at
startup. Native components require the bundled `support/gradle` build on macOS.

The [setup receipt](../../notes/evidence/fr2-re-setup/README.md) records actual
synthetic decompilation and rejected open/restore paths. This targeted correction
does not claim to audit every upstream tool as a general process sandbox.
