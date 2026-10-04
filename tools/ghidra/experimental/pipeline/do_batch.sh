#!/bin/zsh
# usage: do_batch.sh BATCH_NAME SEEDS_JSON PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)
# config (+ independent checks), V5 guard once on a byte-identical project copy, export, verify, reconcile. Static only.
set -e
source ${0:A:h}/env.sh
NAME=$1;SEEDS=$2;PREV=$3;BASE=$4;S=$D/batch-$NAME;mkdir -p $S/run
EXC=""; [ -f $S/exclude.json ] && EXC=$S/exclude.json
$PYTHON $PIPE/make_batch_config.py $BASE $S/config.json $SEEDS $S/config-report.json $EXC | cut -c1-400
$PYTHON $PIPE/check_batch_config_root.py $S/config.json $BASE $S/root-config-check.json > /dev/null && echo CONFIG_CHECK_PASS
NEWP=codex-audit-ee-batch-$NAME-proposal-01
if [ ! -e ghidra-project/$NEWP ]; then tree_sha ghidra-project/$PREV > $S/source-project-sha.txt && cp -R ghidra-project/$PREV ghidra-project/$NEWP; fi
diff $S/source-project-sha.txt <(tree_sha ghidra-project/$NEWP) > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs (path+hash records)"; exit 3; }
CS=$(shasum -a 256 $S/config.json | cut -d' ' -f1);mkdir -p $D/v5guard;cp tools/ghidra/experimental/CreateEeCandidateV5.java $D/v5guard/
set +e
$GHIDRA_HEADLESS $PWD/ghidra-project/$NEWP fr2 -process SLES_517.05 -noanalysis -scriptPath $PWD/$D/v5guard -postScript CreateEeCandidateV5.java $PWD/$S/run/transaction-result.json $PWD/games/ford-racing-2/extracted/SLES_517.05 $PWD/$BASE/decompilation/manifest.json $PWD/$BASE/inventory.json $PWD/$BASE/coverage.json $PWD/$S/config.json $CS -log $PWD/$S/run/transaction-ghidra.log > $S/run/transaction-console.log 2>&1
echo exit=$?; set -e
$PYTHON - <<P
import json;d=json.load(open('$S/run/transaction-result.json'));print(d['status'],str(d.get('failure'))[:1500],d.get('function_count_after'))
json.dump({'argv':['analyzeHeadless','ghidra-project/$NEWP','fr2','-process','SLES_517.05','-noanalysis','-scriptPath','$D/v5guard','-postScript','CreateEeCandidateV5.java','$S/run/transaction-result.json','<elf>','$BASE/decompilation/manifest.json','$BASE/inventory.json','$BASE/coverage.json','$S/config.json','$CS'],'source_project':'ghidra-project/$PREV (byte-identical copy)','config_sha256':'$CS'},open('$S/transaction-command.json','w'),indent=1)
P
grep -q "created_batch_bounded_candidates" $S/run/transaction-result.json
N=$($PYTHON -c "import json;print(json.load(open('$S/run/transaction-result.json'))['function_count_after'])")
$PIPE/export_verify.sh ghidra-project/$NEWP $S/export-$N | tail -1
$PYTHON $PIPE/post_batch.py $S/config.json $BASE $S/export-$N $($PYTHON -c "import json;print(json.load(open('$S/verify-stdout.json'))['result'])") $S/reconciliation.json $S/root-export-check.json
echo "EXPORT_DIR=$S/export-$N"
