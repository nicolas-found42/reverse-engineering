#!/bin/zsh
# usage: do_annotate.sh NAME PLAN_JSON PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)
# one guarded annotation transaction on a byte-identical project copy, read-only export, verifier, comparison. Static only.
set -e
source ${0:A:h}/env.sh
NAME=$1;PLAN=$2;PREV=$3;BASE=$4;S=$D/annot-$NAME;mkdir -p $S/run
NEWP=codex-audit-ee-annot-$NAME-proposal-01
if [ ! -e ghidra-project/$NEWP ]; then tree_sha ghidra-project/$PREV > $S/source-project-sha.txt && cp -R ghidra-project/$PREV ghidra-project/$NEWP; fi
diff $S/source-project-sha.txt <(tree_sha ghidra-project/$NEWP) > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs (path+hash records)"; exit 3; }
PS=$(shasum -a 256 $PLAN | cut -d' ' -f1);mkdir -p $D/annotguard;cp tools/ghidra/experimental/AnnotateFunctionsV1.java $D/annotguard/
set +e
$GHIDRA_HEADLESS $PWD/ghidra-project/$NEWP fr2 -process SLES_517.05 -noanalysis -scriptPath $PWD/$D/annotguard -postScript AnnotateFunctionsV1.java $PWD/$S/run/annotation-result.json $PWD/games/ford-racing-2/extracted/SLES_517.05 $PWD/$PLAN $PS > $S/run/annotation-console.log 2>&1
echo exit=$?; set -e
$PYTHON -c "import json;d=json.load(open('$S/run/annotation-result.json'));print(d['status'],str(d.get('failure'))[:800],d.get('function_count_after'))"
grep -q '"status": "annotated"' $S/run/annotation-result.json
N=$($PYTHON -c "import json;print(json.load(open('$S/run/annotation-result.json'))['function_count_after'])")
$PIPE/export_verify.sh ghidra-project/$NEWP $S/export-$N | tail -1
$PYTHON $PIPE/check_annotation.py $PLAN $BASE $S/export-$N $S/reconciliation.json
echo "EXPORT_DIR=$S/export-$N"
