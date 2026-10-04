#!/bin/zsh
# usage: export_verify.sh PROJECT_DIR OUT_DIR  (read-only reopen, export, reusable verifier)
set -e
source ${0:A:h}/env.sh
P=$1;O=$2;mkdir -p $O
$GHIDRA_HEADLESS $PWD/$P fr2 -readOnly -process SLES_517.05 -noanalysis -scriptPath $PWD/tools/ghidra -postScript ExportDecompilation.java $PWD/$O/decompilation 30 -postScript ExportEvidence.java $PWD/$O/inventory.json -postScript ExportCoverage.java $PWD/$O/coverage.json -log $PWD/$O/../export-ghidra.log > $O/../export-console.log 2>&1
grep -E "DECOMP_EXPORT|EVIDENCE_EXPORT_OK|COVERAGE_EXPORT_OK" $O/../export-console.log | cut -c1-220
$PYTHON tools/verify_decompilation.py --manifest $O/decompilation/manifest.json --static-export $O/inventory.json --executable games/ford-racing-2/extracted/SLES_517.05 --output .scratch/evidence/decompilation > $O/../verify-stdout.json
cat $O/../verify-stdout.json | head -c 300
