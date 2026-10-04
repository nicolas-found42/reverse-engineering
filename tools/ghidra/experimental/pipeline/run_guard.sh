#!/bin/zsh
# usage: run_guard.sh SEED PREV_PROJECT_NAME BASE_EXPORT_DIR   (fresh byte-identical project copy, V3 guard run once)
set -e
cd /Users/Nicolas/Documents/github/hermes/reverse-engineering
SEED=$1;PREV=$2;BASE=$3;D=$PWD/.scratch/mesh/codex-audit/frontier-3845-01;S=$D/seed-$SEED;NEW=codex-audit-ee-$SEED-proposal-01
if [ ! -e ghidra-project/$NEW ]; then
 (cd ghidra-project && find $PREV -type f | sort | xargs shasum -a 256 > $S/source-project-sha.txt && cp -R $PREV $NEW)
fi
diff <(awk '{print $1}' $S/source-project-sha.txt) <(cd ghidra-project && find $NEW -type f | sort | xargs shasum -a 256 | awk '{print $1}') > /dev/null && echo COPY_IDENTICAL || { echo "project copy differs from source hashes"; exit 3; }
CS=$(shasum -a 256 $S/config.json | cut -d' ' -f1);mkdir -p $D/guard $S/run;cp tools/ghidra/experimental/CreateEeCandidateV4.java $D/guard/
export JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home
set +e
.scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless $PWD/ghidra-project/$NEW fr2 -process SLES_517.05 -noanalysis -scriptPath $D/guard -postScript CreateEeCandidateV4.java $S/run/transaction-result.json $PWD/games/ford-racing-2/extracted/SLES_517.05 $BASE/decompilation/manifest.json $BASE/inventory.json $BASE/coverage.json $S/config.json $CS -log $S/run/transaction-ghidra.log > $S/run/transaction-console.log 2>&1
echo exit=$?
grep -E "EE_CLOSURE|rejected|Exception" $S/run/transaction-console.log | cut -c1-300 | head -3
python3 - <<P
import json;d=json.load(open('$S/run/transaction-result.json'));print(d['status'],d.get('failure'),d.get('function_count_after'))
json.dump({'argv':['analyzeHeadless','ghidra-project/$NEW','fr2','-process','SLES_517.05','-noanalysis','-scriptPath','$D/guard','-postScript','CreateEeCandidateV4.java','$S/run/transaction-result.json','<elf>','$BASE/decompilation/manifest.json','$BASE/inventory.json','$BASE/coverage.json','$S/config.json','$CS'],'source_project':'ghidra-project/$PREV (byte-identical copy)','config_sha256':'$CS'},open('$S/transaction-command.json','w'),indent=2)
P
