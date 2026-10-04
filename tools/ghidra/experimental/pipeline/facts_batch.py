import json,collections,os,sys,glob,re
S=os.environ.get('FR2_WORK','.scratch/mesh/codex-audit/frontier-3845-01')+'/batch-%s/'%sys.argv[1]
c=json.load(open(S+'config.json'));t=json.load(open(S+'run/transaction-result.json'));r=json.load(open(S+'reconciliation.json'));x=json.load(open(S+'root-export-check.json'));k=json.load(open(S+'root-config-check.json'));rep=json.load(open(S+'config-report.json'))
seeds=c['seeds'];K=len(seeds);pad=sum(len(s.get('padding_words',[])) for s in seeds)
print('K',K,'span words',sum(s['words'] for s in seeds),'padding',pad,'body words',sum(s['words'] for s in seeds)-pad,'decoded_pre',rep['decoded_words'],'with_incoming',rep['with_incoming'],'incoming_sites',sum(len(s['incoming']) for s in seeds),'checker',k['seed_count'],k['words_checked'],k['incoming_sites'])
print('next',rep['next_states'])
print('unresolved targets',len({u for s in seeds for u in s['unresolved_callees']}),'batch links',sum(len(s['batch_callees']) for s in seeds),'known',sum(len(s['known_callees']) for s in seeds))
tails=[v.split('|')[1] for q in t['seeds'] for v in q.get('tail_jumps_with_flow_type',{}).values()]
terminal=sum(1 for s in seeds if f"{int(s['end'],16)-8:08x}" in s['tail_jumps'])
print('tails',len(tails),dict(collections.Counter(tails)),'ending in tail jump',terminal,'breaks',sum(len(s['delay_breaks']) for s in seeds),'ccalls',sum(len(s['computed_calls']) for s in seeds),'likely',sum(s['likely_count'] for s in seeds))
oth=sum(len(q['non_call_references_into_entry']) for q in t['seeds']);print('non_call refs',oth,'seeds with',sum(1 for q in t['seeds'] if q['non_call_references_into_entry']))
print(t['function_count_after'],r['passed_count'],r['check_count'],'changedC',len(r['changed_old_C']),'warn',r['verifier_result']['warning_comment_count'],x['all_C_artifact_hashes_recomputed'])
print([ (d['field'],d['delta']) for d in r['coverage_delta']])
ch=collections.Counter()
for q in r['changed_old_C']:ch.update(q['non_label_change_categories'])
print(dict(ch),json.load(open(S+'exclude.json')))
for f in sorted(glob.glob(S+'failed-attempt-*/transaction-result.json')):
    fl=json.load(open(f))['failure'];print(f.split('/')[-2],collections.Counter(re.sub(r'[0-9a-f]{8}','X',m)[:70] for m in re.findall(r'SEED_FAILURE [0-9a-f]+: ([^|]{0,90})',fl)).most_common(3))
