#!/bin/zsh
# usage: do_annotate_iop.sh MODULE(STREAM|LGDEV) PLAN_JSON PREV_PROJECT_NAME
# Needs IOP_HEADLESS (the Ghidra with the patched MIPS language the IOP project was made with).
# baseline export, one guarded V2 annotation transaction on a byte-identical project copy, export, reconciliation. Static only.
set -e
source ${0:A:h}/env.sh
: "${IOP_HEADLESS:?set IOP_HEADLESS to the patched Ghidra analyzeHeadless used for the IOP project}"
M=$1;PLAN=$2;PREV=$3;S=$D/iop-annot-$M;mkdir -p $S/run
RAW=games/ford-racing-2/extracted/IRX/$M.IRX
FOLDER=iop/inputs/standalone
NEWP=codex-audit-iop-annot-$M-proposal-01
export_ex() { # PROJECT OUTDIR
  mkdir -p $2
  $IOP_HEADLESS $PWD/ghidra-project/$1 $FOLDER -readOnly -process $M.IRX -noanalysis -scriptPath $PWD/tools/ghidra -postScript ExportDecompilation.java $PWD/$2/decompilation 30 -postScript ExportEvidence.java $PWD/$2/inventory.json > $2/../export-$(basename $2).log 2>&1
  grep -E "DECOMP_EXPORT|EVIDENCE_EXPORT_OK" $2/../export-$(basename $2).log | cut -c1-200
}
[ -e $S/base/inventory.json ] || export_ex $PREV $S/base
if [ ! -e ghidra-project/$NEWP ]; then tree_sha ghidra-project/$PREV > $S/source-project-sha.txt && cp -R ghidra-project/$PREV ghidra-project/$NEWP; fi
diff $S/source-project-sha.txt <(tree_sha ghidra-project/$NEWP) > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs (path+hash records)"; exit 3; }
PS=$(shasum -a 256 $PLAN | cut -d' ' -f1);EXE=$(shasum -a 256 $RAW | cut -d' ' -f1);mkdir -p $D/annotguard2;cp tools/ghidra/experimental/AnnotateFunctionsV2.java $D/annotguard2/
set +e
$IOP_HEADLESS $PWD/ghidra-project/$NEWP $FOLDER -process $M.IRX -noanalysis -scriptPath $PWD/$D/annotguard2 -postScript AnnotateFunctionsV2.java $PWD/$S/run/annotation-result.json $PWD/$RAW $PWD/$PLAN $PS $EXE MIPS:LE:32:default > $S/run/annotation-console.log 2>&1
echo exit=$?; set -e
$PYTHON -c "import json;d=json.load(open('$S/run/annotation-result.json'));print(d['status'],str(d.get('failure'))[:800],d.get('function_count_after'),d.get('comments_applied'),d.get('renames_applied'))"
grep -q '"status": "annotated"' $S/run/annotation-result.json
export_ex $NEWP $S/new
$PYTHON $PIPE/check_annotation.py $PLAN $S/base $S/new $S/reconciliation.json
echo "EXPORT_DIR=$S/new"
