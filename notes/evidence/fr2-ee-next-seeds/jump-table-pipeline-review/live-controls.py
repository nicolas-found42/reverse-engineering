import copy,hashlib,json,os,shutil,subprocess
from pathlib import Path

repo=Path.cwd();work=repo/'.scratch/fr2-option-b/live-controls-v4';work.mkdir(exist_ok=True)
base=repo/'ghidra-project/codex-audit-ee-gp-g2-proposal-01'
export=repo/'.scratch/mesh/codex-audit/frontier-3845-01/gp-g2/export-5454-po'
config=json.loads((repo/'.scratch/fr2-option-b/g4-config.json').read_text())
row=next(s for s in config['seeds'] if s['entry']=='001820f0')
source=(repo/'tools/ghidra/experimental/CreateEeCandidateV5.java').read_text()
def tree(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
baseline=tree(base);results=[]
for case in ('count','hash','ordered_targets','missing_pin','rollback_after_refs'):
    folder=work/case;folder.mkdir(exist_ok=True);project=repo/'ghidra-project'/f'codex-audit-ee-jt-control-{case}-v4-proposal-01'
    if project.exists():raise RuntimeError('control output already exists')
    shutil.copytree(base,project);assert tree(project)==baseline
    c=copy.deepcopy(config);c['seeds']=[copy.deepcopy(row)];pin=c['seeds'][0]['jump_tables'][0]
    if case=='count':pin['count']-=1;pin['targets']=pin['targets'][:-1]
    elif case=='hash':pin['table_sha256']='0'*64
    elif case=='ordered_targets':pin['targets']=pin['targets'][1:]+pin['targets'][:1]
    elif case=='missing_pin':c['seeds'][0]['jump_tables']=[]
    script=source
    if case=='rollback_after_refs':
        script=script.replace('List<String> flowFailures = new ArrayList<>();','req(false,"NEGATIVE_CONTROL_AFTER_SWITCH_REFERENCES");\n            List<String> flowFailures = new ArrayList<>();')
        script=script.replace('Set<Long> newWords = new TreeSet<>();', '\n'.join([
            'out.addProperty("before_functions_sha256",sha(new Gson().toJson(beforeFunctions).getBytes(StandardCharsets.UTF_8)));',
            'out.addProperty("before_instructions_sha256",sha(new Gson().toJson(beforeInstructions).getBytes(StandardCharsets.UTF_8)));',
            'out.addProperty("before_data_sha256",sha(new Gson().toJson(beforeData).getBytes(StandardCharsets.UTF_8)));',
            'out.addProperty("before_references_sha256",sha(new Gson().toJson(beforeRefs).getBytes(StandardCharsets.UTF_8)));',
            'out.addProperty("before_memory_sha256",beforeMemory);',
            'Set<Long> newWords = new TreeSet<>();']))
    scripts=folder/'scripts';scripts.mkdir();(scripts/'CreateEeCandidateV5.java').write_text(script)
    cfg=folder/'config.json';cfg.write_text(json.dumps(c,indent=2)+'\n');cfgsha=hashlib.sha256(cfg.read_bytes()).hexdigest()
    args=[str(repo/'.scratch/mesh/codex-geometry/ghidra-patched/support/analyzeHeadless'),str(project),'fr2','-process','SLES_517.05','-noanalysis','-scriptPath',str(scripts),'-postScript','CreateEeCandidateV5.java',str(folder/'result.json'),str(repo/'games/ford-racing-2/extracted/SLES_517.05'),str(export/'decompilation/manifest.json'),str(export/'inventory.json'),str(export/'coverage.json'),str(cfg),cfgsha,'-log',str(folder/'ghidra.log')]
    with (folder/'console.log').open('w') as log:
        p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'JAVA_HOME':'/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home'})
    if not (folder/'result.json').exists():raise RuntimeError(f'{case}: no result, see console log')
    result=json.loads((folder/'result.json').read_text());assert result['status']=='rejected_or_failed'
    if case=='rollback_after_refs':
        assert 'NEGATIVE_CONTROL_AFTER_SWITCH_REFERENCES' in result['failure'],result['failure']
        shutil.copyfile(repo/'.scratch/fr2-option-b/VerifyCandidateRollback.java',scripts/'VerifyCandidateRollback.java')
        verify=[args[0],str(project),'fr2','-process','SLES_517.05','-noanalysis','-readOnly','-scriptPath',str(scripts),'-postScript','VerifyCandidateRollback.java',str(folder/'result.json'),str(folder/'rollback-verified.json')]
        with (folder/'rollback-console.log').open('w') as log:subprocess.run(verify,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'JAVA_HOME':'/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home'})
        proof=json.loads((folder/'rollback-verified.json').read_text());assert proof['status']=='pass',proof
        result['negative_control_rollback_verified']=True
    expected={'count':'bound/count differs','hash':'memory/ELF/hash differs','ordered_targets':'ordered switch targets differ','missing_pin':'computed jump is not pinned'}
    if case in expected:assert expected[case] in result['failure'],result['failure']
    assert tree(base)==baseline
    results.append({'case':case,'status':'pass','failure':result['failure'],'project_copy_identical_before':True,'source_project_preserved':True,'rollback_verified':result.get('negative_control_rollback_verified',False),'guard_sha256':hashlib.sha256(script.encode()).hexdigest(),'config_sha256':cfgsha})
    (work/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print(case,'pass',flush=True)
