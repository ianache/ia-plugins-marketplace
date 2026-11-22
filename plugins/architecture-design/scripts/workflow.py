#!/usr/bin/env python3
"""Human-controlled workflow for architecture-design. Plans per scenario, persists task/gate state and
enforces ordering. It never executes skills and never approves a gate on its own behalf."""
import argparse,datetime,json,sys
from pathlib import Path

PREFIX='architecture-'
GATE_OF={'context-and-evidence-designer':'G1','asr-and-solution-designer':'G2','decision-governor':'G3',
         'conformance-assessor':'G4','evolution-governor':'G5','development-handoff':'G6'}
OPTIONAL={'conformance-assessor','evolution-governor'}
SCENARIOS={
 'greenfield':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','development-handoff'],
 'brownfield':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','conformance-assessor','development-handoff'],
 'evolution':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','conformance-assessor','evolution-governor','development-handoff'],
}
ALIASES={'continuous-governance':'evolution'}  # continuous governance reuses the evolution chain
GATES=['G0','G1','G2','G3','G4','G5','G6']
STATES={'PENDING','READY','IN_PROGRESS','NEEDS_REVIEW','DONE','BLOCKED','FAILED'}
TRANS={'PENDING':{'READY','BLOCKED'},'READY':{'IN_PROGRESS','BLOCKED'},'IN_PROGRESS':{'NEEDS_REVIEW','FAILED','BLOCKED'},
       'NEEDS_REVIEW':{'DONE','FAILED','BLOCKED'},'FAILED':{'READY'},'BLOCKED':{'READY'},'DONE':set()}
MANIFEST_KEYS=('producer','inputs','outputs','sources','open_questions','gate','status')
ROUTES={k:'./'+v for k,v in json.loads((Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))['document_types'].items()}  # fuente unica: assets/pathmap.json

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fail(m):raise ValueError(m)
ORCH_ROOT=json.loads((Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))['orchestrator_root'].strip('/')  # campo orchestrator_root de pathmap.json
def run_path(root,run):return Path(root)/ORCH_ROOT/run

def build_plan(scenario):
    names=SCENARIOS[scenario]
    gates=['G0']+[GATE_OF[n] for n in names]
    tasks=[]
    for i,n in enumerate(names):
        g=GATE_OF[n]
        tasks.append({'id':f'T{i+1:02d}','skill':PREFIX+n,'depends_on':[f'T{i:02d}'] if i else [],
                      'entry_gate':gates[i],'gate':g,'optional':n in OPTIONAL})
    omissions=[{'gate':GATE_OF[n],'skill':PREFIX+n,'justification':None} for n in GATE_OF if n in OPTIONAL and n not in names]
    return tasks,gates,omissions

def init(root,run,scenario):
    scenario=ALIASES.get(scenario,scenario)
    if scenario not in SCENARIOS:fail('unknown scenario: '+str(scenario))
    out=run_path(root,run);out.mkdir(parents=True,exist_ok=False)
    design=Path(root)/'architecture';design.mkdir(parents=True,exist_ok=True)
    (design/'adrs').mkdir(exist_ok=True);(design/'asrs').mkdir(exist_ok=True)
    tasks,gates,omissions=build_plan(scenario)
    state={'run_id':run,'scenario':scenario,'created_at':now(),'design_path':str(design),
           'pathmap':'assets/pathmap.md','pathmap_status':'v1.2.0_proposed_conventions',
           'gates':{g:{'status':'pending_human_approval','approver':None,'decided_at':None,'evidence':None} for g in gates},
           'tasks':[{'id':t['id'],'skill':t['skill'],'status':'PENDING','attempt':0,'history':[]} for t in tasks],
           'omissions':omissions}
    save(out/'execution-plan.json',{'run_id':run,'scenario':scenario,'tasks':tasks,'omissions':omissions,
                                    'gate_policy':'human approval required; no autoapproval'})
    save(out/'state.json',state)
    save(out/'scope-manifest.json',{'scenario':scenario,'sources':[],'adr_refs':[],
                                    'missing_sources':['Add approved sources before G0 approval']})
    save(out/'routing-contracts.json',{'pathmap_version':'1.2.0','document_type_paths':ROUTES,
        'policy':'orchestrator must supply per-artifact routing; block unknown types; explicit user override only'})
    return out

def check(r):
    plan=load(r/'execution-plan.json');state=load(r/'state.json')
    if plan['scenario'] not in SCENARIOS:fail('unknown scenario')
    ids=[t['id'] for t in plan['tasks']]
    if not ids or len(ids)!=len(set(ids)):fail('duplicate/empty task IDs')
    if [t['id'] for t in state['tasks']]!=ids:fail('state tasks mismatch')
    seen=set()
    for t in plan['tasks']:
        if not t['skill'].startswith(PREFIX) or t['skill'][len(PREFIX):] not in GATE_OF:fail('unknown skill: '+t['skill'])
        if t['gate']!=GATE_OF[t['skill'][len(PREFIX):]]:fail('gate does not match skill: '+t['id'])
        if t['entry_gate'] not in state['gates'] or t['gate'] not in state['gates']:fail('unknown gate in '+t['id'])
        if GATES.index(t['entry_gate'])>=GATES.index(t['gate']):
            fail(f"gate cycle: {t['id']} enters on {t['entry_gate']} but completes {t['gate']}")
        for d in t['depends_on']:
            if d not in seen:fail('invalid DAG at '+t['id'])
        seen.add(t['id'])
    if any(s['status'] not in STATES for s in state['tasks']):fail('invalid task status')
    if any(g['status'] not in ('pending_human_approval','approved') for g in state['gates'].values()):fail('invalid gate status')
    if any(g['status']=='approved' and not all(g.get(k) for k in ('approver','decided_at','evidence')) for g in state['gates'].values()):
        fail('unsubstantiated gate approval')
    return plan,state

def _task(plan,state,tid):
    t=next((x for x in plan['tasks'] if x['id']==tid),None)
    if not t:fail('unknown task')
    return t,next(x for x in state['tasks'] if x['id']==tid)

def _check_manifest(path,task):
    if not path or not Path(path).is_file():fail('output manifest required and must exist')
    m=load(path)
    if not isinstance(m,dict) or any(k not in m for k in MANIFEST_KEYS):fail('manifest missing keys')
    if m['producer']!=task['skill']:fail('manifest producer does not match task skill')
    if m['gate']!=task['gate']:fail('manifest gate does not match task gate')

def transition(r,tid,to,actor,reason,manifest=None):
    plan,state=check(r);task,entry=_task(plan,state,tid);old=entry['status']
    if to not in STATES:fail('unknown state')
    if to not in TRANS[old]:fail(f'forbidden transition {old} -> {to}')
    if not actor or not reason:fail('actor and reason required')
    by={s['id']:s for s in state['tasks']}
    if to in ('READY','IN_PROGRESS'):
        if any(by[d]['status']!='DONE' for d in task['depends_on']):fail('dependencies not DONE')
        if state['gates'][task['entry_gate']]['status']!='approved':fail('task entry gate not approved')
    if to in ('NEEDS_REVIEW','DONE'):_check_manifest(manifest,task)
    if to=='IN_PROGRESS':entry['attempt']+=1
    entry['status']=to
    entry['history'].append({'from':old,'to':to,'at':now(),'actor':actor,'reason':reason,'manifest':str(manifest) if manifest else None})
    save(r/'state.json',state);return old,to

def approve_gate(r,gate,actor,evidence):
    plan,state=check(r)
    if gate not in state['gates']:fail('unknown gate (not part of this scenario)')
    g=state['gates'][gate]
    if g['status']=='approved':fail('already approved')
    if not actor or not actor.startswith('human:') or not evidence:fail('human actor (human:<name>) and evidence required')
    active=list(state['gates'])
    if gate=='G0':
        m=load(r/'scope-manifest.json')
        if not m.get('sources') or m.get('missing_sources'):fail('scope sources incomplete')
    else:
        prev=active[active.index(gate)-1]
        if state['gates'][prev]['status']!='approved':fail(f'previous gate {prev} pending')
        by={s['id']:s for s in state['tasks']}
        required=[t['id'] for t in plan['tasks'] if t['gate']==gate]
        if any(by[t]['status']!='DONE' for t in required):fail('tasks of the gate not DONE')
        if gate=='G6' and any(not o.get('justification') for o in state['omissions']):
            fail('omitted conditional gates need a justification')
    g.update(status='approved',approver=actor,decided_at=now(),evidence=evidence)
    save(r/'state.json',state)

def justify_omission(r,gate,text):
    plan,state=check(r)
    o=next((x for x in state['omissions'] if x['gate']==gate),None)
    if not o:fail('gate is not an omitted conditional gate')
    if not text or not text.strip():fail('justification required')
    o['justification']=text.strip();save(r/'state.json',state)

def status(r):
    plan,state=check(r)
    done=sum(s['status']=='DONE' for s in state['tasks'])
    return {'scenario':state['scenario'],'progress':f"{done}/{len(state['tasks'])}",
            'tasks':{s['id']:s['status'] for s in state['tasks']},
            'gates':{g:v['status'] for g,v in state['gates'].items()},
            'omissions':[{'gate':o['gate'],'justified':bool(o['justification'])} for o in state['omissions']]}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init');a.add_argument('--root',type=Path,default=Path('.'));a.add_argument('--run-id',required=True)
    a.add_argument('--scenario',choices=sorted(list(SCENARIOS)+list(ALIASES)),required=True)
    for n in ('check','status'):
        a=sub.add_parser(n);a.add_argument('--root',type=Path,default=Path('.'));a.add_argument('--run-id',required=True)
    a=sub.add_parser('transition');a.add_argument('--root',type=Path,default=Path('.'));a.add_argument('--run-id',required=True)
    a.add_argument('--task',required=True);a.add_argument('--to',required=True,choices=sorted(STATES));a.add_argument('--actor',required=True)
    a.add_argument('--reason',required=True);a.add_argument('--manifest',type=Path)
    a=sub.add_parser('approve-gate');a.add_argument('--root',type=Path,default=Path('.'));a.add_argument('--run-id',required=True)
    a.add_argument('--gate',required=True);a.add_argument('--actor',required=True);a.add_argument('--evidence',required=True)
    a=sub.add_parser('justify-omission');a.add_argument('--root',type=Path,default=Path('.'));a.add_argument('--run-id',required=True)
    a.add_argument('--gate',required=True);a.add_argument('--text',required=True)
    x=ap.parse_args(argv)
    try:
        if x.cmd=='init':print(init(x.root,x.run_id,x.scenario));return 0
        r=run_path(x.root,x.run_id)
        if not r.exists():fail('run does not exist')
        if x.cmd=='check':check(r);print('plan, state and gates structurally valid')
        elif x.cmd=='status':print(json.dumps(status(r),ensure_ascii=False,indent=2))
        elif x.cmd=='transition':o,n=transition(r,x.task,x.to,x.actor,x.reason,x.manifest);print(x.task,o,'->',n)
        elif x.cmd=='approve-gate':approve_gate(r,x.gate,x.actor,x.evidence);print(x.gate,'APPROVED (recorded claim; identity not verified)')
        else:justify_omission(r,x.gate,x.text);print('omission of',x.gate,'justified')
    except (ValueError,FileNotFoundError,KeyError,json.JSONDecodeError) as e:
        print('ERROR:',e,file=sys.stderr);return 2
    return 0
if __name__=='__main__':sys.exit(main())
