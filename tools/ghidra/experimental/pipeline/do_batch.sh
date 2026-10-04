#!/bin/zsh
# usage: do_batch.sh BATCH_NAME SEEDS_JSON PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)
# config (+ independent checks), V5 guard once on a byte-identical project copy, export, verify, reconcile. Static only.
set -e
cd /Users/Nicolas/Documents/github/hermes/reverse-engineering
NAME=$1;SEEDS=$2;PREV=$3;BASE=$4;D=.scratch/mesh/codex-audit/frontier-3845-01;S=$D/batch-$NAME;mkdir -p $S/run
EXC=""; [ -f $S/exclude.json ] && EXC=$S/exclude.json
python3 $D/make_batch_config.py $BASE $S/config.json $SEEDS $S/config-report.json $EXC | cut -c1-400
python3 .scratch/mesh/codex-root/check_batch_config_root.py $S/config.json $BASE $S/root-config-check.json > /dev/null && echo CONFIG_CHECK_PASS
NEWP=codex-audit-ee-batch-$NAME-proposal-01
if [ ! -e ghidra-project/$NEWP ]; then (cd ghidra-project && find $PREV -type f | sort | xargs shasum -a 256 > ../$S/source-project-sha.txt && cp -R $PREV $NEWP); fi
diff <(awk '{print $1}' $S/source-project-sha.txt) <(cd ghidra-project && find $NEWP -type f | sort | xargs shasum -a 256 | awk '{print $1}') > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs"; exit 3; }
CS=$(shasum -a 256 $S/config.json | cut -d' ' -f1);mkdir -p $D/v5guard;cp tools/ghidra/experimental/CreateEeCandidateV5.java $D/v5guard/
export JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home
set +e
.scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless $PWD/ghidra-project/$NEWP fr2 -process SLES_517.05 -noanalysis -scriptPath $PWD/$D/v5guard -postScript CreateEeCandidateV5.java $PWD/$S/run/transaction-result.json $PWD/games/ford-racing-2/extracted/SLES_517.05 $PWD/$BASE/decompilation/manifest.json $PWD/$BASE/inventory.json $PWD/$BASE/coverage.json $PWD/$S/config.json $CS -log $PWD/$S/run/transaction-ghidra.log > $S/run/transaction-console.log 2>&1
echo exit=$?; set -e
python3 - <<P
import json;d=json.load(open('$S/run/transaction-result.json'));print(d['status'],str(d.get('failure'))[:1500],d.get('function_count_after'))
json.dump({'argv':['analyzeHeadless','ghidra-project/$NEWP','fr2','-process','SLES_517.05','-noanalysis','-scriptPath','$D/v5guard','-postScript','CreateEeCandidateV5.java','$S/run/transaction-result.json','<elf>','$BASE/decompilation/manifest.json','$BASE/inventory.json','$BASE/coverage.json','$S/config.json','$CS'],'source_project':'ghidra-project/$PREV (byte-identical copy)','config_sha256':'$CS'},open('$S/transaction-command.json','w'),indent=1)
P
grep -q "created_batch_bounded_candidates" $S/run/transaction-result.json
N=$(python3 -c "import json;print(json.load(open('$S/run/transaction-result.json'))['function_count_after'])")
$D/export_verify.sh ghidra-project/$NEWP $S/export-$N | tail -1
python3 $D/post_batch.py $S/config.json $BASE $S/export-$N $(python3 -c "import json;print(json.load(open('$S/verify-stdout.json'))['result'])") $S/reconciliation.json $S/root-export-check.json
echo "EXPORT_DIR=$S/export-$N"
