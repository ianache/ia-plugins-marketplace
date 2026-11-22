#!/usr/bin/env python3
"""Auditable local workflow controls; requires PyYAML. No external services."""
import argparse, datetime, json, pathlib, sys, hashlib
import yaml
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))  # funciona también con python -I
from validate_pathmap import resolve, verify, data

SKILLS=['ddd-domain-discovery','ddd-bounded-context-designer','ddd-context-map-designer','ddd-tactical-model-designer','ddd-domain-event-designer','ddd-domain-contract-validator']
ORCH='ddd-design-orchestrator'
# last column = completion gate (approval needs the task DONE); entry gate is always the previous gate, so a task never waits on the gate it must close.
TASKS=[('T01','Domain discovery',SKILLS[0],[], 'domain-discovery.md','G1'),('T02','Bounded contexts',SKILLS[1],['T01'],'bounded-contexts.md','G1'),('T03','Context map',SKILLS[2],['T02'],'context-map.md','G1'),('T04','Tactical model',SKILLS[3],['T02','T03'],'tactical-model.md','G2'),('T05','Domain events',SKILLS[4],['T03','T04'],'domain-events.md','G2'),('T06','Contract validation',SKILLS[5],['T03','T04','T05'],'domain-design-contract.yaml','G3'),('T07','Pack consolidation',ORCH,['T06'],'domain-design-pack.md','G4')]
EXTRA_OUTPUTS={'T06':['CFR-domain-validation.md']}
def entry_gate(g): return GATES[GATES.index(g)-1]
STATES={'PENDING','READY','IN_PROGRESS','BLOCKED','NEEDS_REVIEW','DONE','FAILED'}
TRANS={'PENDING':{'READY','BLOCKED'},'READY':{'IN_PROGRESS','BLOCKED'},'IN_PROGRESS':{'NEEDS_REVIEW','FAILED','BLOCKED'},'NEEDS_REVIEW':{'DONE','FAILED','BLOCKED'},'FAILED':{'READY'},'BLOCKED':{'READY'},'DONE':set()}
GATES=['G0','G1','G2','G3','G4']
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p):
    with open(p,encoding='utf-8') as f: return yaml.safe_load(f)
def save(p,obj):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(obj,sort_keys=False,allow_unicode=True),encoding='utf-8')
def fail(s): raise ValueError(s)
def files(r): return [r/x for x in ('execution-plan.yaml','task-ledger.yaml','gate-register.yaml')]
def check(r):
    plan,ledger,gates=map(load,files(r)); tasks=plan['tasks']; ids=[t['id'] for t in tasks]
    if len(ids)!=len(set(ids)) or not ids: fail('duplicate/empty task IDs')
    if not plan.get('workspace_root'): fail('missing workspace_root')
    if plan.get('pathmap_version')!=data()['pathmap_version']: fail('pathmap version mismatch')
    for task in tasks:
        for output in task['outputs']:
            expected=str(resolve(plan['workspace_root'],output,output))
            if task.get('output_paths',{}).get(output)!=expected: fail('output pathmap mismatch: '+output)
    graph={t['id']:t.get('depends_on',[]) for t in tasks}
    for t in tasks:
        if t['skill'] not in SKILLS+[ORCH]: fail('unknown skill: '+t['skill'])
        if t.get('gate') not in GATES or t.get('entry_gate') not in GATES: fail('unknown gate')
        if GATES.index(t['entry_gate'])>=GATES.index(t['gate']): fail('gate cycle: '+t['id']+' enters on '+t['entry_gate']+' but completes '+t['gate'])
        for d in graph[t['id']]:
            if GATES.index(next(x for x in tasks if x['id']==d)['gate'])>GATES.index(t['entry_gate'])+1: fail('gate cycle: '+t['id']+' depends on later gate via '+d)
        if not t.get('inputs') or not t.get('outputs') or not t.get('acceptance'): fail('missing contract fields: '+t['id'])
        for d in graph[t['id']]:
            if d not in graph: fail('missing dependency '+d)
    visiting=set(); done=set()
    def visit(x):
        if x in visiting: fail('cycle at '+x)
        if x in done: return
        visiting.add(x)
        for d in graph[x]: visit(d)
        visiting.remove(x);done.add(x)
    for x in graph: visit(x)
    entries=ledger['entries']; eids=[e['task_id'] for e in entries]
    if set(eids)!=set(ids) or len(eids)!=len(ids): fail('ledger tasks mismatch')
    if any(e['status'] not in STATES for e in entries): fail('invalid task status')
    gs={g['id']:g for g in gates['gates']}
    if set(gs)!=set(GATES): fail('gate mismatch')
    if any(g['status'] not in ('NOT_READY','PENDING_APPROVAL','APPROVED','REJECTED') for g in gs.values()): fail('invalid gate status')
    if any(g['status']=='APPROVED' and not all(g.get(k) for k in ('approver','decided_at','evidence')) for g in gs.values()): fail('unsubstantiated gate approval')
    return plan,ledger,gates

def init(args):
    r=pathlib.Path(args.run);
    workspace=pathlib.Path(args.workspace).resolve()
    if not r.resolve().is_relative_to(workspace/data()['orchestrator_root'].strip('/')): fail('run must be inside '+data()['orchestrator_root'].strip('/'))
    r.mkdir(parents=True,exist_ok=False)
    tasks=[{'id':tid,'title':title,'skill':skill,'depends_on':deps,'inputs':['scope-manifest.yaml'] if not deps else [next(z[4] for z in TASKS if z[0]==d) for d in deps], 'outputs':[out]+EXTRA_OUTPUTS.get(tid,[]), 'output_paths':{o:str(resolve(workspace,o,o)) for o in [out]+EXTRA_OUTPUTS.get(tid,[])}, 'document_type':out, 'pathmap_version':data()['pathmap_version'], 'acceptance':['source-references-present','reviewed-output-present'],'entry_gate':entry_gate(gate),'gate':gate,'priority':'high','estimate':None} for tid,title,skill,deps,out,gate in TASKS]
    save(r/'execution-plan.yaml',{'schema_version':'2.0','run_id':r.name,'scope_ref':args.scope,'mode':'PLAN_ONLY','revision':1,'workspace_root':str(workspace),'pathmap_version':data()['pathmap_version'],'tasks':tasks})
    save(r/'task-ledger.yaml',{'schema_version':'2.0','run_id':r.name,'entries':[{'task_id':t['id'],'skill':t['skill'],'status':'PENDING','attempt':0,'updated_at':None,'actor':None,'evidence':[],'reason':None} for t in tasks],'history':[]})
    save(r/'gate-register.yaml',{'schema_version':'2.0','run_id':r.name,'gates':[{'id':g,'status':'PENDING_APPROVAL' if g=='G0' else 'NOT_READY','approver':None,'decided_at':None,'evidence':[]} for g in GATES]})
    save(r/'scope-manifest.yaml',{'schema_version':'2.0','scope_ref':args.scope,'sources':[],'missing_sources':['Add approved DSP/SSP and KB references before G0 approval']})
    status(r); print('initialized',r)
def status(r):
    p,l,g=check(r); counts={s:sum(e['status']==s for e in l['entries']) for s in sorted(STATES)}
    pending=[x['id'] for x in g['gates'] if x['status']!='APPROVED']
    (r/'run-status.md').write_text('# Run '+p['run_id']+'\n\nScope: '+p['scope_ref']+'\n\nProgress: '+str(counts['DONE'])+'/'+str(len(l['entries']))+'\n\nStates: '+json.dumps(counts)+'\n\nGates pending: '+', '.join(pending)+'\n\nBlocked tasks: '+', '.join(e['task_id'] for e in l['entries'] if e['status']=='BLOCKED')+'\n',encoding='utf-8')
    return counts

def transition(args):
    r=pathlib.Path(args.run); p,l,g=check(r); task=next((t for t in p['tasks'] if t['id']==args.task),None)
    if not task: fail('unknown task')
    e=next(e for e in l['entries'] if e['task_id']==args.task); old=e['status']; new=args.to
    if new not in TRANS[old]: fail('forbidden transition '+old+' -> '+new)
    if not args.actor or not args.reason: fail('actor and reason required')
    if new in ('READY','IN_PROGRESS'):
        if any(next(x for x in l['entries'] if x['task_id']==d)['status']!='DONE' for d in task['depends_on']): fail('dependencies not DONE')
        if next(x for x in g['gates'] if x['id']==task['entry_gate'])['status']!='APPROVED': fail('task entry gate not approved')
    if new in ('NEEDS_REVIEW','DONE'):
        if not args.evidence: fail('evidence required')
        if not all(verify(p['workspace_root'],out,task['output_paths'][out]) for out in task['outputs']): fail('required outputs missing/empty')
    if new=='DONE' and old!='NEEDS_REVIEW': fail('must pass review')
    if new=='IN_PROGRESS': e['attempt']+=1
    e.update(status=new,updated_at=now(),actor=args.actor,reason=args.reason)
    if args.evidence: e['evidence'].append(args.evidence)
    l['history'].append({'task_id':args.task,'from':old,'to':new,'at':e['updated_at'],'actor':args.actor,'reason':args.reason,'evidence':args.evidence})
    save(r/'task-ledger.yaml',l); status(r); print(args.task,old,'->',new)
def gate(args):
    r=pathlib.Path(args.run);p,l,g=check(r)
    item=next((x for x in g['gates'] if x['id']==args.gate),None)
    if not item: fail('unknown gate')
    if item['status']=='APPROVED': fail('already approved')
    if not args.actor or not args.actor.startswith('human:') or not args.evidence: fail('human actor (human:<nombre>) and evidence required')
    if args.gate=='G0':
        m=load(r/'scope-manifest.yaml')
        if not m.get('sources') or m.get('missing_sources'): fail('scope sources incomplete')
    else:
        required={'G1':['T01','T02','T03'],'G2':['T04','T05'],'G3':['T06'],'G4':['T07']}[args.gate]
        if any(next(e for e in l['entries'] if e['task_id']==t)['status']!='DONE' for t in required): fail('required tasks not DONE')
        prev={'G1':'G0','G2':'G1','G3':'G2','G4':'G3'}[args.gate]
        if next(x for x in g['gates'] if x['id']==prev)['status']!='APPROVED': fail('previous gate not approved')
    item.update(status='APPROVED',approver=args.actor,decided_at=now(),evidence=[args.evidence]);save(r/'gate-register.yaml',g);status(r);print(args.gate,'APPROVED (recorded claim; external identity not verified)')
PATTERNS={'partnership','shared-kernel','customer-supplier','conformist','anticorruption-layer','acl','open-host-service','ohs','published-language','separate-ways','big-ball-of-mud'}
def norm(x): return str(x).strip().lower().replace('_','-').replace(' ','-')
def contract(args):
    c=load(args.file)
    if not isinstance(c,dict): fail('contract must be mapping')
    for key in ('schema_version','run_id','source_refs','bounded_contexts','context_relationships','aggregates','entities','value_objects','domain_events','integration_contract_candidates','approval'):
        if key not in c: fail('missing contract key: '+key)
    contexts=c['bounded_contexts']; ids=[x['id'] for x in contexts]
    if len(ids)!=len(set(ids)): fail('duplicate context IDs')
    for a in c['aggregates']:
        if a.get('bounded_context_id') not in ids: fail('aggregate without owning context')
    for rel in c['context_relationships']:
        if rel.get('upstream') not in ids or rel.get('downstream') not in ids: fail('relationship has unknown context')
        if norm(rel.get('pattern')) not in PATTERNS: fail('unknown relationship pattern: '+str(rel.get('pattern')))
    for kind in ('entities','value_objects','domain_events'):
        for x in c[kind]:
            if not isinstance(x,dict) or x.get('bounded_context_id') not in ids: fail(kind+' item without owning context')
    ap=c['approval']
    if not isinstance(ap,dict) or ap.get('status') not in ('PENDING','APPROVED','REJECTED'): fail('invalid approval status')
    if ap['status']=='APPROVED':
        if not ap.get('actor') or not ap.get('evidence'): fail('APPROVED requires actor and evidence')
        gr=pathlib.Path(args.run)/'gate-register.yaml' if args.run else None
        if gr is None: fail('APPROVED requires --run to verify gate G3 in gate-register.yaml')
        g3=next((x for x in load(gr)['gates'] if x['id']=='G3'),None)
        if not g3 or g3['status']!='APPROVED': fail('APPROVED contract but gate G3 is not approved')
    print('contract valid (structure, patterns, ownership, approval); not a semantic review')
def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init');a.add_argument('run');a.add_argument('--scope',required=True);a.add_argument('--workspace',default='.')
    a=sub.add_parser('check');a.add_argument('run')
    a=sub.add_parser('status');a.add_argument('run')
    a=sub.add_parser('transition');a.add_argument('run');a.add_argument('--task',required=True);a.add_argument('--to',required=True,choices=sorted(STATES));a.add_argument('--actor',required=True);a.add_argument('--reason',required=True);a.add_argument('--evidence')
    a=sub.add_parser('approve-gate');a.add_argument('run');a.add_argument('--gate',required=True);a.add_argument('--actor',required=True);a.add_argument('--evidence',required=True)
    a=sub.add_parser('validate-contract');a.add_argument('file');a.add_argument('--run',help='run directory with gate-register.yaml; required when approval is APPROVED')
    args=ap.parse_args()
    try:
        if args.cmd=='init':init(args)
        elif args.cmd=='check':check(pathlib.Path(args.run));print('DAG, ledger and gates structurally valid')
        elif args.cmd=='status':print(status(pathlib.Path(args.run)))
        elif args.cmd=='transition':transition(args)
        else:
            if args.cmd=='approve-gate':gate(args)
            else:contract(args)
    except (ValueError,KeyError,FileNotFoundError,yaml.YAMLError) as ex:
        print('ERROR:',ex,file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
