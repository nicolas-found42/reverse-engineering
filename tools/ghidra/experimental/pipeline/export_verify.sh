#!/bin/zsh
# usage: export_verify.sh PROJECT_DIR OUT_DIR  (read-only reopen, export, reusable verifier)
set -e
cd /Users/Nicolas/Documents/github/hermes/reverse-engineering
P=$1;O=$2;mkdir -p $O
export JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home
.scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless $PWD/$P fr2 -readOnly -process SLES_517.05 -noanalysis -scriptPath $PWD/tools/ghidra -postScript ExportDecompilation.java $PWD/$O/decompilation 30 -postScript ExportEvidence.java $PWD/$O/inventory.json -postScript ExportCoverage.java $PWD/$O/coverage.json -log $PWD/$O/../export-ghidra.log > $O/../export-console.log 2>&1
grep -E "DECOMP_EXPORT|EVIDENCE_EXPORT_OK|COVERAGE_EXPORT_OK" $O/../export-console.log | cut -c1-220
/opt/homebrew/opt/python@3.14/bin/python3.14 tools/verify_decompilation.py --manifest $O/decompilation/manifest.json --static-export $O/inventory.json --executable games/ford-racing-2/extracted/SLES_517.05 --output .scratch/evidence/decompilation > $O/../verify-stdout.json
cat $O/../verify-stdout.json | head -c 300
