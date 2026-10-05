"""Compare two exports around one guarded annotation. usage: check_annotation.py PLAN OLD_EXPORT NEW_EXPORT OUT_JSON
Functions, instruction bytes and text must be identical; names may change only as planned; pseudocode must match once
comments are stripped, planned names are mapped back and all whitespace is removed (a longer name re-wraps lines). Static only."""
import json,re,sys
from pathlib import Path
plan_p,old_p,new_p,out_p=sys.argv[1:5]
plan=json.loads(Path(plan_p).read_text());old=Path(old_p);new=Path(new_p)
renames={e['entry']:e['rename'] for e in plan['entries'] if 'rename' in e}
comments={e['entry'] for e in plan['entries']}
oi=json.loads((old/'inventory.json').read_text());ni=json.loads((new/'inventory.json').read_text())
checks=[]
def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
check('same function count',oi['inventory_count']==ni['inventory_count']==len(oi['functions'])==len(ni['functions']),{'old':oi['inventory_count'],'new':ni['inventory_count']})
of={f['entry']:f for f in oi['functions']};nf={f['entry']:f for f in ni['functions']}
check('same entries',set(of)==set(nf))
bad=[e for e in of if e in nf and (of[e]['instructions']!=nf[e]['instructions'] or of[e]['size']!=nf[e]['size'] or of[e]['blocks']!=nf[e]['blocks'])]
check('every function keeps size, blocks and instruction address/text/bytes',not bad,bad[:10])
badname=[e for e in of if e in nf and nf[e]['name']!=renames.get(e,of[e]['name'])]
check('names change only as planned',not badname,badname[:10])
check('planned renames present',all(nf[e]['name']==n for e,n in renames.items() if e in nf),len(renames))
rev={n:of[e]['name'] for e,n in renames.items() if e in of}
pat=re.compile('|'.join(re.escape(n) for n in sorted(rev,key=len,reverse=True))) if rev else None
COM=re.compile(r'/\*.*?\*/',re.S)
def norm(t,m=False):
    t=COM.sub('',t)
    if m and pat: t=pat.sub(lambda x:rev[x.group(0)],t)
    return ''.join(t.split())
differ=[];same=0;missing=[]
for e in of:
    po=old/'decompilation/functions'/f'{e}.c';pn=new/'decompilation/functions'/f'{e}.c'
    if not po.exists() or not pn.exists(): missing.append(e);continue
    if norm(po.read_text(errors='replace'))==norm(pn.read_text(errors='replace'),True):same+=1
    else:differ.append(e)
check('every function has a pseudocode file in both exports',not missing,missing[:10])
check('pseudocode identical after stripping comments and mapping planned names back',not differ,{'identical':same,'differ':len(differ),'examples':differ[:20]})
nm=json.loads((new/'decompilation/manifest.json').read_text())
check('new manifest reports every function generated',nm['failed']==0 and nm['generated']==nm['inventory_count'],{'generated':nm['generated'],'failed':nm['failed']})
res={'schema_version':1,'status':'pass' if all(c['passed'] for c in checks) else 'fail','plan_entries':len(plan['entries']),'renames':len(renames),'check_count':len(checks),'passed_count':sum(c['passed'] for c in checks),'checks':checks,
'scope':'name and comment annotation only; no identity, behavior or original-name claim'}
Path(out_p).write_text(json.dumps(res,indent=1)+'\n');print(res['status'],res['passed_count'],'/',res['check_count'])
sys.exit(0 if res['status']=='pass' else 1)
