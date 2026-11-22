#!/usr/bin/env python3
"""Control de plan/gates local; no ejecuta Claude ni autentica aprobadores.

Comandos: init, status, start, complete, approve (alias approve-gate), check.
Compatibilidad: `workflow.py <run-id> [--workspace .] [--scenario X]` equivale a `init --run-id <run-id>`.
"""
import argparse,datetime,json,sys
from pathlib import Path
PM=json.loads((Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))  # fuente unica: assets/pathmap.json
# G0 alcance; G1 requerimientos; G2 pantallas; G3 sistema visual; G4 prototipo; G5 calidad; G6 handoff
TASKS=[('ux-requirements-flow-designer','G1'),('ui-screen-specification-designer','G2'),('ui-atomic-design-system-designer','G3'),('ui-prototype-generator','G4'),('ui-design-quality-validator','G5'),('ux-ui-development-handoff','G6')]
SKILLS=[t for t,_ in TASKS]; GATES=dict(TASKS)
SCENARIOS=['greenfield','brownfield','evolution']
COMMANDS={'init','status','start','complete','approve','approve-gate','check'}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def roots(workspace,run_id):
    base=Path(workspace)
    return base/PM['orchestrator_root'].strip('/')/run_id, base/PM['deliverable_root'].format(run_id=run_id).strip('/')
def init(workspace,run_id,scenario):
    scenario=scenario.lower()
    if scenario not in SCENARIOS: raise SystemExit('escenario inválido: '+scenario)
    op,design=roots(workspace,run_id)
    if op.exists() or design.exists(): raise SystemExit('run-id ya existe; no sobrescribir')
    op.mkdir(parents=True);design.mkdir(parents=True)
    (op/'plan.yaml').write_text('run_id: '+run_id+'\nscenario: '+scenario+'\nstatus: pending_G0\n',encoding='utf-8')
    save(op/'gate-register.json',{f'G{i}':{'status':'pending','approved_by':None,'evidence':[]} for i in range(7)})
    save(op/'state.json',{'run_id':run_id,'scenario':scenario,'tasks':{s:{'status':'pending','evidence':None} for s in SKILLS},'history':[]})
    save(op/'scope-manifest.yaml',{'schema_version':'2.0','run_id':run_id,'scenario':scenario,'sources':[],'missing_sources':['Agregar fuentes aprobadas (DSP/SSP, KB, repositorios) antes de aprobar G0']})
    print('Plan:',op,'\nEntregables:',design)
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
def approved(g,gate): return g[gate]['status']=='approved'
def check(s,g):
    bad=[t for t in SKILLS if s['tasks'][t]['status']=='done' and not approved(g,GATES[t])]
    return {'unapproved_completed_gates':bad,'ready_for_handoff':approved(g,'G0') and all(s['tasks'][t]['status']=='done' and approved(g,GATES[t]) for t in SKILLS)}
def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in COMMANDS and not argv[0].startswith('-'): argv=['init','--run-id',argv[0],*argv[1:]]  # modo anterior
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
    for command in ('init','status','start','complete','approve','check'):
        a=sub.add_parser(command,aliases=['approve-gate'] if command=='approve' else []); a.add_argument('--workspace',default='.'); a.add_argument('--run-id',required=True)
        if command=='init': a.add_argument('--scenario',type=str.lower,choices=SCENARIOS,default='greenfield')
        if command in ('start','complete'): a.add_argument('--task',required=True,choices=SKILLS)
        if command=='complete': a.add_argument('--evidence',required=True)
        if command=='approve': a.add_argument('--gate',required=True,choices=[f'G{i}' for i in range(7)]); a.add_argument('--actor',required=True); a.add_argument('--evidence',required=True)
    a=p.parse_args(argv); cmd='approve' if a.command=='approve-gate' else a.command
    if cmd=='init': init(a.workspace,a.run_id,a.scenario); return
    op,design=roots(a.workspace,a.run_id)
    if not (op/'state.json').is_file(): sys.exit('Unknown run')
    s=json.loads((op/'state.json').read_text(encoding='utf-8')); g=json.loads((op/'gate-register.json').read_text(encoding='utf-8'))
    if cmd=='status': print(json.dumps({'state':s,'gates':g},indent=2,ensure_ascii=False)); return
    if cmd=='check': print(json.dumps(check(s,g))); return
    if cmd=='approve':
        if not a.actor.strip().startswith('human:') or not a.evidence.strip(): sys.exit('Actor (human:<nombre>) and evidence required')
        if a.gate=='G0': scope_ready(op)
        else:
            t=next(t for t in SKILLS if GATES[t]==a.gate)
            if s['tasks'][t]['status']!='done': sys.exit('Gate task incomplete or skipped')
        g[a.gate].update(status='approved',approved_by=a.actor,evidence=[a.evidence],decided_at=now())
    else:
        t=a.task
        if cmd=='start':
            if s['tasks'][t]['status']!='pending': sys.exit('Task not pending')
            i=SKILLS.index(t); prior='G0' if i==0 else GATES[SKILLS[i-1]]
            if not approved(g,prior): sys.exit('Prerequisite gate not approved: '+prior)
            s['tasks'][t]['status']='in_progress'
        else:
            if s['tasks'][t]['status']!='in_progress': sys.exit('Task not in progress')
            ev=Path(a.evidence)
            if not ev.is_file() or not ev.resolve().is_relative_to(design.resolve()): sys.exit('Evidence must be existing file inside design/ux-ui/<run-id>')
            s['tasks'][t].update(status='done',evidence=str(ev))
    s['history'].append({'command':cmd,'at':now()}); save(op/'state.json',s); save(op/'gate-register.json',g); print('OK')
if __name__=='__main__': main()
