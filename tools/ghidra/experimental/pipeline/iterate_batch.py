"""Run do_batch.sh repeatedly; when the guard rejects, drop the seed named by the failure (an 8-hex address inside a seed span) and retry. Each retry uses a fresh byte-identical project copy; failed attempts are archived. Static only."""
import json,os,re,subprocess,sys,shutil,time
from pathlib import Path
name,seeds,prev,base=sys.argv[1:5];maxit=int(sys.argv[5]) if len(sys.argv)>5 else 40
PIPE=Path(__file__).resolve().parent;D=Path(os.environ.get('FR2_WORK','.scratch/mesh/codex-audit/frontier-3845-01'));S=D/f'batch-{name}';proj=Path('ghidra-project')/f'codex-audit-ee-batch-{name}-proposal-01'
excl=json.loads((S/'exclude.json').read_text()) if (S/'exclude.json').exists() else []
for it in range(maxit):
 if proj.exists():shutil.rmtree(proj)
 shutil.rmtree(S/'run',ignore_errors=True)
 for f in S.glob('export-*'):shutil.rmtree(f)
 (S/'verify-stdout.json').unlink(missing_ok=True);(S/'run').mkdir(parents=True,exist_ok=True)
 r=subprocess.run([str(PIPE/'do_batch.sh'),name,seeds,prev,base],capture_output=True,text=True)
 (S/f'iteration-{it:02d}.out').write_text(r.stdout+r.stderr)
 res=json.loads((S/'run/transaction-result.json').read_text()) if (S/'run/transaction-result.json').exists() else {}
 if res.get('status')=='created_batch_bounded_candidates':
  print('guard ok at iteration',it,'excluded',len(excl));break
 fail=res.get('failure','');print('iteration',it,'failure:',fail[:200])
 cfg=json.loads((S/'config.json').read_text());spans=[(int(s['start'],16),int(s['end'],16),s['entry']) for s in cfg['seeds']]
 hits=sorted(set(re.findall(r'SEED_FAILURE ([0-9a-f]{8})',fail)))
 if not hits:
  tokens=[int(t,16) for t in re.findall(r'\b[0-9a-f]{8}\b',fail)];hit=None
  for t in tokens:
   for a,b,e in spans:
    if a<=t<b:hit=e;break
   if hit:break
  hits=[hit] if hit else []
 if not hits:print('no seed identified in the failure; stopping');sys.exit(2)
 hit=','.join(hits)
 arch=S/f'failed-attempt-{len(list(S.glob("failed-attempt-*")))+1:02d}';arch.mkdir()
 shutil.copy(S/'run/transaction-result.json',arch/'transaction-result.json');(arch/'NOTE.txt').write_text(f'Guard rejected before commit; seed {hit} excluded. Failure: {fail}\n')
 excl.extend(hits);(S/'exclude.json').write_text(json.dumps(sorted(set(excl)),indent=1)+'\n')
else:print('iteration limit reached');sys.exit(3)
