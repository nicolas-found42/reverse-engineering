"""Static single-seed walk; shared switch checks with the batch walker.

The legacy single-seed workflow keeps its undefined-only coverage restriction.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import seedlib

seedlib.load(sys.argv[2])
seedlib.unowned.clear()
result = seedlib.walk(sys.argv[1])
out = Path(os.environ.get('FR2_WORK', '.scratch/mesh/codex-audit/frontier-3845-01')) / f"cfg-{result['seed']}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'seed': result['seed'], 'reachable_count': result['reachable_count'],
                  'gap_word_count': len(result['gap_words']), 'jump_table_count': len(result['jump_tables']),
                  'reject_count': len(result['rejects']), 'output': str(out)}))
