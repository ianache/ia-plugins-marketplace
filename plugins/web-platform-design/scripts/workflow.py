#!/usr/bin/env python3
"""Planificador local: no ejecuta skills ni autentica aprobaciones."""
import argparse, json, pathlib, sys, datetime
SKILLS={
 "reconstruction":"web-application-reconstruction-analyzer",
 "architecture":"web-platform-architecture-designer",
 "composition":"web-component-composition-designer",
 "integration":"web-bff-api-integration-designer",
 "evolution":"web-evolution-planner",
 "handoff":"web-development-handoff"}
GATES={"reconstruction":"G1","architecture":"G2","composition":"G3","integration":"G4","evolution":"G5","handoff":"G6"}
SCENARIOS={"greenfield":["architecture","composition","integration","handoff"],"brownfield":["reconstruction","architecture","composition","integration","handoff"],"evolution":["reconstruction","architecture","composition","integration","evolution","handoff"]}
PM=json.loads((pathlib.Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))  # fuente unica: assets/pathmap.json
def paths(w,r): return pathlib.Path(w)/PM['orchestrator_root'].strip('/')/r, pathlib.Path(w)/PM['deliverable_root'].format(run_id=r).strip('/')
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def scope_ready(rd):
 # G0 solo se aprueba con alcance y fuentes verificadas en scope-manifest.yaml (requiere PyYAML)
 try: import yaml
 except ImportError: sys.exit('PyYAML es necesario para aprobar G0: python -m pip install PyYAML')
 f=rd/'scope-manifest.yaml'
 if not f.is_file(): sys.exit('Falta scope-manifest.yaml; G0 no se puede aprobar')
 m=yaml.safe_load(f.read_text(encoding='utf-8')) or {}
 src=m.get('sources')
 if not isinstance(src,list) or not src or not all(isinstance(x,str) and x.strip() for x in src): sys.exit('G0 requiere sources completas en scope-manifest.yaml')
 if m.get('missing_sources'): sys.exit('G0 bloqueado: hay missing_sources pendientes en scope-manifest.yaml')
def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
 for command in ('init','status','start','complete','approve','check'):
  a=sub.add_parser(command);a.add_argument('--workspace',required=True);a.add_argument('--run-id',required=True)
  if command=='init': a.add_argument('--scenario',required=True,type=str.lower,choices=SCENARIOS)
  if command in ('start','complete'): a.add_argument('--task',required=True,choices=SKILLS)
  if command=='complete': a.add_argument('--evidence',required=True)
  if command=='approve': a.add_argument('--gate',required=True,choices=['G0',*GATES.values()]);a.add_argument('--actor',required=True);a.add_argument('--evidence',required=True)
 a=p.parse_args();rd,dd=paths(a.workspace,a.run_id);sf=rd/'state.json'
 if a.command=='init':
  if sf.exists(): sys.exit('Run already exists')
  rd.mkdir(parents=True);dd.mkdir(parents=True)
  tasks=SCENARIOS[a.scenario];state={'scenario':a.scenario,'run_id':a.run_id,'tasks':{t:{'status':'pending','evidence':None} for t in tasks},'gates':{},'history':[],'design_path':str(dd)}
  save(sf,state);save(rd/'scope-manifest.yaml',{'schema_version':'2.0','run_id':a.run_id,'scenario':a.scenario,'sources':[],'missing_sources':['Agregar fuentes aprobadas (DSP/SSP, KB, repositorios) antes de aprobar G0']});save(rd/'execution-plan.yaml',{'tasks':tasks,'gates':['G0']+[GATES[t] for t in tasks]});print(str(dd));return
 if not sf.exists():sys.exit('Unknown run')
 s=json.loads(sf.read_text());tasks=list(s['tasks']);
 if a.command=='status': print(json.dumps(s,indent=2));return
 if a.command=='check':
  bad=[t for t in tasks if s['tasks'][t]['status']=='done' and GATES[t] not in s['gates']];print(json.dumps({'unapproved_completed_gates':bad,'ready_for_handoff':all(s['tasks'][t]['status']=='done' and GATES[t] in s['gates'] for t in tasks)}));return
 if a.command=='approve':
  if not a.actor.strip().startswith('human:') or not a.evidence.strip():sys.exit('Actor (human:<nombre>) and evidence required')
  if a.gate=='G0': scope_ready(rd)
  if a.gate!='G0':
   prior=[t for t in tasks if GATES[t]==a.gate]
   if not prior or s['tasks'][prior[0]]['status']!='done':sys.exit('Gate task incomplete or skipped')
  s['gates'][a.gate]={'actor':a.actor,'evidence':a.evidence,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 else:
  t=a.task
  if t not in tasks:sys.exit('Task not part of scenario')
  i=tasks.index(t)
  if a.command=='start':
   if s['tasks'][t]['status']!='pending':sys.exit('Task not pending')
   prior='G0' if i==0 else GATES[tasks[i-1]]
   if prior not in s['gates']:sys.exit('Prerequisite gate not approved: '+prior)
   s['tasks'][t]['status']='in_progress'
  else:
   if s['tasks'][t]['status']!='in_progress':sys.exit('Task not in progress')
   evidence=pathlib.Path(a.evidence)
   if not evidence.is_file() or not evidence.resolve().is_relative_to(dd.resolve()):sys.exit('Evidence must be existing file inside design/web/<run-id>')
   s['tasks'][t].update(status='done',evidence=str(evidence))
 s['history'].append({'command':a.command,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});save(sf,s);print('OK')
if __name__=='__main__':main()
