#!/usr/bin/env python3
"""Control de plan/gates; no ejecuta skills ni autentica aprobadores.

Comandos: init, status, start, complete, approve (alias approve-gate), check.
"""
import argparse, datetime, json, sys
from pathlib import Path
SKILLS=['mobile-application-reconstruction-analyzer','mobile-architecture-designer','mobile-navigation-state-designer','mobile-api-offline-integration-designer','mobile-evolution-release-planner','mobile-development-handoff']
PM=json.loads((Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))  # fuente unica: assets/pathmap.json
GATES=['G1','G2','G3','G4','G5','G6']
SCENARIOS={'greenfield':[1,2,3,5],'brownfield':[0,1,2,3,5],'evolution':[0,1,2,3,4,5]}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def roots(workspace,run_id):
    ws=Path(workspace).resolve()
    return ws/PM['orchestrator_root'].strip('/')/run_id, ws/PM['deliverable_root'].format(run_id=run_id).strip('/')
def init(workspace,run_id,scenario):
    scenario=scenario.lower()
    if scenario not in SCENARIOS: raise ValueError('escenario inválido: '+scenario)
    if not run_id.replace('-','').replace('_','').isalnum(): raise ValueError('run-id inválido')
    op,design=roots(workspace,run_id)
    if op.exists(): raise FileExistsError('run-id ya existe')
    op.mkdir(parents=True);design.mkdir(parents=True,exist_ok=True)
    tasks=[{'skill':SKILLS[i],'gate':GATES[i],'status':'pending','outputs':[]} for i in SCENARIOS[scenario]]
    state={'run_id':run_id,'scenario':scenario,'gates':{'G0':{'status':'pending_human_review'}},'tasks':tasks}
    save(op/'state.json',state)
    save(op/'execution-plan.json',{'tasks':tasks,'design_root':str(design)})
    save(op/'gate-register.json',state['gates'])
    save(op/'scope-manifest.yaml',{'schema_version':'2.0','run_id':run_id,'scenario':scenario,'sources':[],'missing_sources':['Agregar fuentes aprobadas (DSP/SSP, KB, repositorios) antes de aprobar G0']})
    print(json.dumps({'operational':str(op),'deliverables':str(design),'tasks':len(tasks)},indent=2))
def scope_ready(op):
    # G0 solo se aprueba con alcance y fuentes verificadas en scope-manifest.yaml (requiere PyYAML)
    try: import yaml
    except ImportError: sys.exit('PyYAML es necesario para aprobar G0: python -m pip install PyYAML')
    f=op/'scope-manifest.yaml'
    if not f.is_file(): sys.exit('Falta scope-manifest.yaml; G0 no se puede aprobar')
    m=yaml.safe_load(f.read_text(encoding='utf-8')) or {}
    src=m.get('sources')
    if not isinstance(src,list) or not src or not all(isinstance(x,str) and x.strip() for x in src): sys.exit('G0 requiere sources completas en scope-manifest.yaml')
    if m.get('missing_sources'): sys.exit('G0 bloqueado: hay missing_sources pendientes en scope-manifest.yaml')
def load(workspace,run_id):
    op,design=roots(workspace,run_id)
    if not (op/'state.json').is_file(): sys.exit('Unknown run')
    return op,design,json.loads((op/'state.json').read_text(encoding='utf-8'))
def persist(op,s):
    save(op/'state.json',s); save(op/'gate-register.json',s['gates'])
    save(op/'execution-plan.json',{'tasks':s['tasks'],'design_root':json.loads((op/'execution-plan.json').read_text(encoding='utf-8'))['design_root']})
def approved(s,g): return s['gates'].get(g,{}).get('status')=='approved'
def task_of(s,skill):
    t=next((t for t in s['tasks'] if t['skill']==skill),None)
    if not t: sys.exit('Task not part of scenario')
    return t
def approve(op,s,gate,actor,evidence):
    if not actor.strip().startswith('human:') or not evidence.strip(): sys.exit('Actor (human:<nombre>) and evidence required')
    if gate=='G0': scope_ready(op)
    else:
        t=next((t for t in s['tasks'] if t['gate']==gate),None)
        if not t or t['status']!='done': sys.exit('Gate task incomplete or skipped')
    s['gates'][gate]={'status':'approved','actor':actor,'evidence':evidence,'at':now()}
def start(s,skill):
    t=task_of(s,skill)
    if t['status']!='pending': sys.exit('Task not pending')
    i=s['tasks'].index(t); prior='G0' if i==0 else s['tasks'][i-1]['gate']
    if not approved(s,prior): sys.exit('Prerequisite gate not approved: '+prior)
    t['status']='in_progress'
def complete(s,design,skill,evidence):
    t=task_of(s,skill)
    if t['status']!='in_progress': sys.exit('Task not in progress')
    ev=Path(evidence)
    if not ev.is_file() or not ev.resolve().is_relative_to(design.resolve()): sys.exit('Evidence must be existing file inside design/mobile/<run-id>')
    t.update(status='done',outputs=[str(ev)])
def check(s):
    bad=[t['skill'] for t in s['tasks'] if t['status']=='done' and not approved(s,t['gate'])]
    return {'unapproved_completed_gates':bad,'ready_for_handoff':approved(s,'G0') and all(t['status']=='done' and approved(s,t['gate']) for t in s['tasks'])}
def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
    for command in ('init','status','start','complete','approve','check'):
        a=sub.add_parser(command,aliases=['approve-gate'] if command=='approve' else []); a.add_argument('--workspace',default='.'); a.add_argument('--run-id',required=True)
        if command=='init': a.add_argument('--scenario',type=str.lower,choices=list(SCENARIOS),required=True)
        if command in ('start','complete'): a.add_argument('--task',required=True,choices=SKILLS)
        if command=='complete': a.add_argument('--evidence',required=True)
        if command=='approve': a.add_argument('--gate',required=True,choices=['G0',*GATES]); a.add_argument('--actor',required=True); a.add_argument('--evidence',required=True)
    a=p.parse_args(argv); cmd='approve' if a.command=='approve-gate' else a.command
    if cmd=='init': init(a.workspace,a.run_id,a.scenario); return
    op,design,s=load(a.workspace,a.run_id)
    if cmd=='status': print(json.dumps(s,indent=2,ensure_ascii=False)); return
    if cmd=='check': print(json.dumps(check(s))); return
    if cmd=='approve': approve(op,s,a.gate,a.actor,a.evidence)
    elif cmd=='start': start(s,a.task)
    else: complete(s,design,a.task,a.evidence)
    persist(op,s); print('OK')
if __name__=='__main__': main()
