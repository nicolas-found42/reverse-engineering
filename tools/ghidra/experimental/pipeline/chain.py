"""Run the single-seed pipeline repeatedly over feasible frontier seeds (lowest address first). Static only.
usage: chain.py PREV_PROJECT_NAME BASE_EXPORT_DIR MAX_SEEDS  -> appends to chain-log.jsonl; stops at MAX or when no feasible seed remains."""
import json,os,subprocess,sys,re
from pathlib import Path
PIPE=Path(__file__).resolve().parent;D=Path(os.environ.get('FR2_WORK','.scratch/mesh/codex-audit/frontier-3845-01'));proj,export,maxn=sys.argv[1],sys.argv[2],int(sys.argv[3])
log=D/'chain-log.jsonl';blocked_p=D/'blocked.json';blocked=json.loads(blocked_p.read_text()) if blocked_p.exists() else {}
def sh(*a):return subprocess.run(a,capture_output=True,text=True)
done=0
while done<maxn:
 r=sh(sys.executable,str(PIPE/'scan.py'),export,str(D/'scan-chain.json'));assert r.returncode==0,r.stderr
 rows=json.loads((D/'scan-chain.json').read_text())['undefined_or_unowned_direct_transfers']
 cands=sorted((x['target'] for x in rows if x['op']=='jal' and x['target'] not in blocked))
 picked=None
 for t in cands:
  r=sh(sys.executable,str(PIPE/'cfg_seed.py'),t,export)
  if r.returncode!=0:blocked[t]={'why':'cfg_seed error','detail':r.stderr[-300:]};continue
  c=json.loads((D/f'cfg-{t}.json').read_text())
  why=None
  if c['rejects']:why='rejects: '+'; '.join(f"{x['address']} {x['why']}" for x in c['rejects'][:3])
  elif c['gap_words']:why=f"{len(c['gap_words'])} unreachable gap words inside span"
  elif c['next_word_state']!='undefined' and c['next_word_state']!='owned '+c['span']['end_exclusive']:why='next word state: '+c['next_word_state']
  elif f"{int(c['span']['end_exclusive'],16)-8:08x}" not in c['returns']:why='no return at end-8: '+str(c['returns'])
  elif any(e['kind']=='jump' and not e.get('tail_jump') and not (int(c['span']['start'],16)<=int(e['target'],16)<int(c['span']['end_exclusive'],16)) for e in c['edges']):why='J leaves the span but not to a saved entry'
  if why:blocked[t]={'why':why,'span_bytes':c['span']['bytes']};continue
  picked=t;break
 blocked_p.write_text(json.dumps(blocked,indent=1,sort_keys=True)+'\n')
 if not picked:print('no feasible seed remains; blocked:',len(blocked));break
 r=sh(str(PIPE/'do_seed.sh'),picked,proj,export)
 ok=r.returncode==0 and 'EXPORT_DIR=' in r.stdout
 entry={'seed':picked,'ok':ok,'tail':r.stdout[-600:] if not ok else '', 'stderr':r.stderr[-400:] if not ok else ''}
 if ok:
  m=re.search(r'EXPORT_DIR=(\S+)',r.stdout);export=m.group(1);proj=f'codex-audit-ee-{picked}-proposal-01';entry['export']=export;entry['project']=proj;done+=1
  f=json.loads((D/f'seed-{picked}/config.json').read_text());entry['words']=f['words'];entry['unresolved']=f['unresolved_callees']
 else:
  blocked[picked]={'why':'pipeline failure','detail':(r.stdout+r.stderr)[-500:]};blocked_p.write_text(json.dumps(blocked,indent=1,sort_keys=True)+'\n')
 log.open('a').write(json.dumps(entry)+'\n');print(json.dumps({k:v for k,v in entry.items() if k!='tail'}))
print('final',proj,export)
