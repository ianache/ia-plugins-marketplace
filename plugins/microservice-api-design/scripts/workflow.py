#!/usr/bin/env python3
"""Auditable local workflow controls; requires PyYAML. No external services."""
import argparse, datetime, json, pathlib, sys, hashlib
import yaml
from validate_pathmap import resolve,resolve_openapi,load_map,validate

SKILLS=['microservice-reconstruction-analyzer','microservice-boundary-architecture-designer','api-integration-contract-designer','microservice-functionality-designer','microservice-evolution-planner','microservice-codebase-handoff']
# (id, title, skill, dependencies, output, entry gate)
SCENARIOS={
 'greenfield':[
 ('T01','Service boundaries',SKILLS[1],[],'to-be/service-boundaries.md','G0'),
 ('T02','Architecture To-Be',SKILLS[1],['T01'],'to-be/service-architecture.md','G0'),
 ('T03','API/integration contracts',SKILLS[2],['T02'],'to-be/api-integration-design.md','G1'),
 ('T03C','C4 architecture view',SKILLS[1],['T02'],'docs/c4-architecture.md','G1'),
 ('T03E','Event contracts',SKILLS[2],['T03'],'events/event-contracts.md','G1'),
 ('T03F','Functionality design FDT',SKILLS[3],['T03','T03C','T03E'],'functionalities/fdt-manifest.yaml','G2'),
 ('T04','Evolution assessment (N/A documented)',SKILLS[4],['T03F'],'evolution/impact-analysis.md','G2'),
 ('T05','Codebase handoff',SKILLS[5],['T04'],'handoff/codebase-handoff.yaml','G3')],
 'brownfield':[
 ('T01','As-Is reconstruction',SKILLS[0],[],'as-is/architecture-reconstruction.md','G0'),
 ('T02','Boundary reconciliation',SKILLS[1],['T01'],'to-be/service-boundaries.md','G0'),
 ('T03','Architecture assessment',SKILLS[1],['T02'],'to-be/service-architecture.md','G1'),
 ('T03C','C4 architecture view',SKILLS[1],['T03'],'docs/c4-architecture.md','G1'),
 ('T04','Contract inventory',SKILLS[2],['T03'],'to-be/api-integration-design.md','G1'),
 ('T04E','Event contracts',SKILLS[2],['T04'],'events/event-contracts.md','G1'),
 ('T04F','Functionality design FDT',SKILLS[3],['T04','T03C','T04E'],'functionalities/fdt-manifest.yaml','G2'),
 ('T05','Documentation-only impact',SKILLS[4],['T04F'],'evolution/impact-analysis.md','G2'),
 ('T06','KB/codebase reconciliation handoff',SKILLS[5],['T05'],'handoff/codebase-handoff.yaml','G3')],
 'evolution':[
 ('T01','As-Is reconstruction',SKILLS[0],[],'as-is/architecture-reconstruction.md','G0'),
 ('T02','Service boundary evolution',SKILLS[1],['T01'],'to-be/service-boundaries.md','G0'),
 ('T03','Architecture To-Be',SKILLS[1],['T02'],'to-be/service-architecture.md','G1'),
 ('T03C','C4 architecture view',SKILLS[1],['T03'],'docs/c4-architecture.md','G1'),
 ('T04','API/integration evolution',SKILLS[2],['T03'],'to-be/api-integration-design.md','G1'),
 ('T04E','Event contracts',SKILLS[2],['T04'],'events/event-contracts.md','G1'),
 ('T04F','Functionality design FDT',SKILLS[3],['T04','T03C','T04E'],'functionalities/fdt-manifest.yaml','G2'),
 ('T05','Impact and migration',SKILLS[4],['T04F'],'evolution/impact-analysis.md','G2'),
 ('T06','Codebase handoff',SKILLS[5],['T05'],'handoff/codebase-handoff.yaml','G3')]
}
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
    if not plan.get('design_root'): fail('missing design_root')
    if not plan.get('pathmap_version'): fail('missing pathmap_version')
    for t in tasks:
        for output in t['outputs']:
            if not pathlib.Path(output).is_absolute(): fail('output must be resolved by pathmap')
            if output==t.get('openapi_output'):
                if pathlib.Path(output).resolve()!=resolve_openapi(plan['workspace_root'],plan.get('service'),plan.get('codebase_service')): fail('openapi output not at codebase path')
            else: validate(plan['workspace_root'], t['document_type'], output, plan.get('service'), plan.get('codebase_service'))
    graph={t['id']:t.get('depends_on',[]) for t in tasks}
    for t in tasks:
        if t['skill'] not in SKILLS: fail('unknown skill: '+t['skill'])
        if t.get('gate') not in GATES: fail('unknown gate')
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

def check_workspace_root(ws):
    # design/ debe colgar de la raiz del proyecto, no del arbol de control (campo orchestrator_root de pathmap.json)
    ctl=pathlib.PurePosixPath(load_map()['orchestrator_root']).parts[:2]
    parts=ws.parts
    for i in range(len(parts)-len(ctl)+1):
        if tuple(x.lower() for x in parts[i:i+len(ctl)])==tuple(x.lower() for x in ctl):
            fail('workspace_root no puede estar dentro de '+'/'.join(ctl)+'/ (zona de control); use la raiz del proyecto, p. ej. --workspace-root .')

def init(args):
    r=pathlib.Path(args.run); workspace_root=pathlib.Path(args.workspace_root).resolve(); check_workspace_root(workspace_root); design_root=workspace_root/'design'; pathmap=load_map()
    if r.exists(): fail('el run ya existe: '+str(r))
    task_specs=SCENARIOS[args.scenario]
    tasks=[{'id':tid,'title':title,'skill':skill,'depends_on':deps,'inputs':['scope-manifest.yaml'] if not deps else [str(resolve(workspace_root,pathmap['output_files'][next(z[4] for z in task_specs if z[0]==d)],pathlib.Path(next(z[4] for z in task_specs if z[0]==d)).name,args.service,args.codebase_service)) for d in deps], 'document_type':pathmap['output_files'][out], 'pathmap_version':pathmap['version'], 'output_path':str(resolve(workspace_root,pathmap['output_files'][out],pathlib.Path(out).name,args.service,args.codebase_service)), 'outputs':[str(resolve(workspace_root,pathmap['output_files'][out],pathlib.Path(out).name,args.service,args.codebase_service))], 'acceptance':['source-references-present','reviewed-output-present','pathmap-valid'],'gate':gate,'priority':'high','estimate':None} for tid,title,skill,deps,out,gate in task_specs]
    if args.scenario in pathmap['openapi']['scenarios']:
        oas=str(resolve_openapi(workspace_root,args.service,args.codebase_service))
        for x in tasks:
            if x['skill']==SKILLS[2]: x['outputs'].append(oas); x['openapi_output']=oas
    # init atomico: todas las validaciones (p. ej. codebase/<servicio>) ocurren arriba; solo ahora se toca el disco
    r.mkdir(parents=True,exist_ok=False); workspace_root.mkdir(parents=True,exist_ok=True); design_root.mkdir(parents=True,exist_ok=True)
    save(r/'execution-plan.yaml',{'codebase_service':args.codebase_service,'schema_version':'2.0','run_id':r.name,'scope_ref':args.scope,'scenario':args.scenario,'mode':'PLAN_ONLY','revision':1,'service':args.service,'design_root':str(design_root),'workspace_root':str(workspace_root),'pathmap_version':pathmap['version'],'tasks':tasks})
    save(r/'task-ledger.yaml',{'schema_version':'2.0','run_id':r.name,'entries':[{'task_id':t['id'],'skill':t['skill'],'status':'PENDING','attempt':0,'updated_at':None,'actor':None,'evidence':[],'reason':None} for t in tasks],'history':[]})
    save(r/'gate-register.yaml',{'schema_version':'2.0','run_id':r.name,'gates':[{'id':g,'status':'PENDING_APPROVAL' if g=='G0' else 'NOT_READY','approver':None,'decided_at':None,'evidence':[]} for g in GATES]})
    save(r/'scope-manifest.yaml',{'schema_version':'2.0','scope_ref':args.scope,'scenario':args.scenario,'sources':[],'missing_sources':['Add approved DSP/SSP and KB references before G0 approval']})
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
        if next(x for x in g['gates'] if x['id']==task['gate'])['status']!='APPROVED': fail('task gate not approved')
    if new in ('NEEDS_REVIEW','DONE'):
        if not args.evidence: fail('evidence required')
        if not all(pathlib.Path(out).is_file() and pathlib.Path(out).stat().st_size>0 for out in task['outputs']): fail('required outputs missing/empty')
    if new=='DONE' and task['skill']=='microservice-functionality-designer':
        from fdt_validate import validate_manifest
        issues=validate_manifest(next(pathlib.Path(out) for out in task['outputs'] if pathlib.Path(out).name=='fdt-manifest.yaml'))
        if issues: fail('FDT validation failed: '+'; '.join(issues))
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
        required={
            'G1':[t['id'] for t in p['tasks'] if t['gate']=='G0'],
            'G2':[t['id'] for t in p['tasks'] if t['gate']=='G1'],
            'G3':[t['id'] for t in p['tasks'] if t['gate']=='G2'],
            'G4':[t['id'] for t in p['tasks'] if t['gate']=='G3'],
        }[args.gate]
        if any(next(e for e in l['entries'] if e['task_id']==t)['status']!='DONE' for t in required): fail('required tasks not DONE')
        if args.gate=='G4':
            validate_handoff(next(pathlib.Path(o) for t in p['tasks'] for o in t['outputs'] if pathlib.Path(o).name=='codebase-handoff.yaml'))
        prev={'G1':'G0','G2':'G1','G3':'G2','G4':'G3'}[args.gate]
        if next(x for x in g['gates'] if x['id']==prev)['status']!='APPROVED': fail('previous gate not approved')
    item.update(status='APPROVED',approver=args.actor,decided_at=now(),evidence=[args.evidence]);save(r/'gate-register.yaml',g);status(r);print(args.gate,'APPROVED (recorded claim; external identity not verified)')
def contract(args):
    c=load(args.file)
    if not isinstance(c,dict): fail('contract must be mapping')
    for key in ('schema_version','source_refs','bounded_contexts','services','api_contracts','integration_contracts'):
        if key not in c: fail('missing contract key: '+key)
    bc={x['id'] for x in c['bounded_contexts']}; service_ids={x['id'] for x in c['services']}
    if len(service_ids)!=len(c['services']): fail('duplicate service IDs')
    for s in c['services']:
        if not s.get('bounded_context_ids') or any(x not in bc for x in s['bounded_context_ids']): fail('service with invalid BC ownership')
    for kind in ('api_contracts','integration_contracts'):
        for x in c[kind]:
            if x.get('service_id') not in service_ids: fail(kind+' references unknown service')
    print('service contract structurally valid (not semantic approval)')
def validate_handoff(path):
    data=load(path)
    if not isinstance(data,dict) or not isinstance(data.get('handoff'),dict): fail('missing handoff mapping')
    h=data['handoff']
    for key in ('service_id','scenario','knowledge_base','source_repository','architecture','artifacts','controls'):
        if not h.get(key): fail('handoff missing '+key)
    if h['scenario'] not in SCENARIOS: fail('unknown handoff scenario')
    kb=h['knowledge_base']; repo=h['source_repository']
    if not kb.get('target','').startswith('codebase/'): fail('KB target must be codebase/<service>')
    for key in ('project','target_branch','source_ref','source_commit'):
        if not repo.get(key): fail('repository missing '+key)
    if not h['architecture'].get('adr_refs'): fail('ADR references required')
    if not isinstance(h['artifacts'],list) or not h['artifacts']: fail('artifacts required')
    for artifact in h['artifacts']:
        for key in ('id','source','target','action','validation'):
            if not artifact.get(key): fail('artifact missing '+key)
        if pathlib.PurePosixPath(artifact['target']).is_absolute() or '..' in pathlib.PurePosixPath(artifact['target']).parts: fail('unsafe target path')
    if h['controls'].get('require_human_approval') is not True: fail('human approval required')
    print('handoff structurally valid; ADR compliance and external approvals NOT verified')

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init');a.add_argument('run');a.add_argument('--scope',required=True);a.add_argument('--scenario',choices=sorted(SCENARIOS),required=True);a.add_argument('--workspace-root',default='.');a.add_argument('--codebase-service',help='carpeta del servicio dentro de codebase/ si difiere del id');a.add_argument('--service',required=True,help='id del microservicio; destino design/microservices/<servicio>/')
    a=sub.add_parser('check');a.add_argument('run')
    a=sub.add_parser('status');a.add_argument('run')
    a=sub.add_parser('transition');a.add_argument('run');a.add_argument('--task',required=True);a.add_argument('--to',required=True,choices=sorted(STATES));a.add_argument('--actor',required=True);a.add_argument('--reason',required=True);a.add_argument('--evidence')
    a=sub.add_parser('approve-gate');a.add_argument('run');a.add_argument('--gate',required=True);a.add_argument('--actor',required=True);a.add_argument('--evidence',required=True)
    a=sub.add_parser('validate-contract');a.add_argument('file')
    a=sub.add_parser('validate-handoff');a.add_argument('file')
    args=ap.parse_args()
    try:
        if args.cmd=='init':init(args)
        elif args.cmd=='check':check(pathlib.Path(args.run));print('DAG, ledger and gates structurally valid')
        elif args.cmd=='status':print(status(pathlib.Path(args.run)))
        elif args.cmd=='transition':transition(args)
        else:
            if args.cmd=='approve-gate':gate(args)
            elif args.cmd=='validate-handoff':validate_handoff(args.file)
            else:contract(args)
    except (ValueError,KeyError,FileNotFoundError,yaml.YAMLError) as ex:
        print('ERROR:',ex,file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
