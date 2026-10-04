#!/bin/zsh
# usage: do_seed.sh SEED PREV_PROJECT_NAME BASE_EXPORT_DIR(relative)  -> config, root check, guard, export, verify, reconcile
set -e
source ${0:A:h}/env.sh
SEED=$1;PREV=$2;BASE=$3;S=$D/seed-$SEED;mkdir -p $S/run
$PYTHON $PIPE/cfg_seed.py $SEED $BASE > /dev/null
$PYTHON $PIPE/make_seed_config.py $SEED $BASE $S/config.json | tail -1
$PYTHON $PIPE/check_seed_config_root_v4.py $S/config.json $BASE $S/root-config-check.json > /dev/null && echo CONFIG_CHECK_PASS
$PIPE/run_guard.sh $SEED $PREV $PWD/$BASE
grep -q "created_single_bounded_candidate" $S/run/transaction-result.json
N=$($PYTHON -c "import json;print(json.load(open('$S/run/transaction-result.json'))['function_count_after'])")
$PIPE/export_verify.sh ghidra-project/codex-audit-ee-$SEED-proposal-01 $S/export-$N | tail -1
$PYTHON $PIPE/post_seed.py $S/config.json $BASE $S/export-$N $($PYTHON -c "import json;print(json.load(open('$S/verify-stdout.json'))['result'])") $S/reconciliation.json $S/root-export-check.json
echo "EXPORT_DIR=$S/export-$N"
