#!/bin/zsh
# usage: do_gp.sh NAME PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)
# one guarded gp-context transaction on a byte-identical project copy, read-only export, comparison. Static only.
set -e
source ${0:A:h}/env.sh
NAME=$1;PREV=$2;BASE=$3;S=$D/gp-$NAME;mkdir -p $S/run
NEWP=codex-audit-ee-gp-$NAME-proposal-01
if [ ! -e ghidra-project/$NEWP ]; then tree_sha ghidra-project/$PREV > $S/source-project-sha.txt && cp -R ghidra-project/$PREV ghidra-project/$NEWP; fi
diff $S/source-project-sha.txt <(tree_sha ghidra-project/$NEWP) > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs (path+hash records)"; exit 3; }
mkdir -p $D/gpguard;cp tools/ghidra/experimental/SetGpContextV1.java $D/gpguard/
set +e
$GHIDRA_HEADLESS $PWD/ghidra-project/$NEWP fr2 -process SLES_517.05 -noanalysis -scriptPath $PWD/$D/gpguard -postScript SetGpContextV1.java $PWD/$S/run/gp-result.json $PWD/games/ford-racing-2/extracted/SLES_517.05 > $S/run/gp-console.log 2>&1
echo exit=$?; set -e
$PYTHON -c "import json;d=json.load(open('$S/run/gp-result.json'));print(d['status'],str(d.get('failure'))[:800],d.get('function_count_after'))"
grep -q '"status": "applied"' $S/run/gp-result.json
N=$($PYTHON -c "import json;print(json.load(open('$S/run/gp-result.json'))['function_count_after'])")
$PIPE/export_verify.sh ghidra-project/$NEWP $S/export-$N | tail -1
PYTHONPATH=tools $PYTHON tools/gp_context_check.py $BASE $S/export-$N $S/reconciliation.json
echo "EXPORT_DIR=$S/export-$N"
