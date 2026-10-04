#!/bin/zsh
# usage: do_seed.sh SEED PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)  -> config, root check, guard, export, verify, reconcile
set -e
cd /Users/Nicolas/Documents/github/hermes/reverse-engineering
SEED=$1;PREV=$2;BASE=$3;D=.scratch/mesh/codex-audit/frontier-3845-01;S=$D/seed-$SEED;mkdir -p $S/run
python3 $D/cfg_seed.py $SEED $BASE > /dev/null
python3 $D/make_seed_config.py $SEED $BASE $S/config.json | tail -1
python3 .scratch/mesh/codex-root/check_seed_config_root_v4.py $S/config.json $BASE $S/root-config-check.json > /dev/null && echo CONFIG_CHECK_PASS
$D/run_guard.sh $SEED $PREV $PWD/$BASE
grep -q "created_single_bounded_candidate" $S/run/transaction-result.json
N=$(python3 -c "import json;print(json.load(open('$S/run/transaction-result.json'))['function_count_after'])")
$D/export_verify.sh ghidra-project/codex-audit-ee-$SEED-proposal-01 $S/export-$N | tail -1
python3 $D/post_seed.py $S/config.json $BASE $S/export-$N $(python3 -c "import json;print(json.load(open('$S/verify-stdout.json'))['result'])") $S/reconciliation.json $S/root-export-check.json
echo "EXPORT_DIR=$S/export-$N"
