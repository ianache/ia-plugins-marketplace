import argparse,json,pathlib,sys,datetime
SKILLS=['dm-schema-reconstruction-analyzer','dm-data-boundary-designer','dm-logical-model-designer','dm-physical-model-designer','dm-database-migration-designer','dm-data-design-validator']
# (skill index, completion gate number). El número de gate es fijo por skill: G1 As-Is, G2 ownership, G3 lógico, G4 físico, G5 migración, G6 validación.
# Cada escenario usa solo los que aplican; una tarea entra por el gate de cierre de la anterior (G0 la primera), nunca por su propio gate.
STEPS={'greenfield':[(2,2),(3,3),(4,4),(5,5),(6,6)],'brownfield':[(1,1),(2,2),(6,6)],'evolution':[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6)]}
SCHEMA='2'  # versión del formato de la corrida; una corrida con otra versión se rechaza
STATES={'PENDING','IN_PROGRESS','NEEDS_REVIEW','DONE','BLOCKED','FAILED'}
TRANS={'PENDING':{'IN_PROGRESS','BLOCKED'},'IN_PROGRESS':{'NEEDS_REVIEW','FAILED','BLOCKED'},'NEEDS_REVIEW':{'DONE','FAILED','BLOCKED'},'FAILED':{'IN_PROGRESS'},'BLOCKED':{'IN_PROGRESS'},'DONE':set()}
def paths(a):
 w=pathlib.Path(a.workspace).resolve();pm=json.loads((pathlib.Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'));return w/pm['orchestrator_root'].strip('/')/a.run_id,w/pm['deliverable_root'].format(run_id=a.run_id).strip('/')
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['init','check','status','approve-gate','transition','complete']);ap.add_argument('--workspace',default='.');ap.add_argument('--run-id',required=True);ap.add_argument('--scenario',choices=list(STEPS));ap.add_argument('--gate');ap.add_argument('--actor');ap.add_argument('--evidence');ap.add_argument('--task');ap.add_argument('--to');ap.add_argument('--reason');a=ap.parse_args();r,d=paths(a)
 if a.command=='init':
  if r.exists():raise ValueError('run ya existe: no sobrescribir')
  if not a.scenario:raise ValueError('scenario requerido')
  r.mkdir(parents=True);d.mkdir(parents=True,exist_ok=True)
  tasks=[]
  for i,(si,g) in enumerate(STEPS[a.scenario],1):
   tasks.append({'id':f'T{i:02d}','skill':SKILLS[si-1],'depends_on':[f'T{i-1:02d}'] if i>1 else [],'state':'PENDING','entry_gate':'G0' if i==1 else f'G{STEPS[a.scenario][i-2][1]}','completion_gate':f'G{g}','evidence':[]})
  save(r/'execution-plan.json',{'schema_version':SCHEMA,'scenario':a.scenario,'tasks':tasks,'design_root':str(d),'history':[]})
  save(r/'gate-register.json',{'G0':{'approved':False,'actor':None,'evidence':None},**{f'G{g}':{'approved':False,'actor':None,'evidence':None} for _,g in STEPS[a.scenario]}})
  save(r/'scope-manifest.json',{'scenario':a.scenario,'sources':[],'adr_refs':[],'service_ids':[],'bounded_context_ids':[],'schema_ids':[]})
  print('INITIALIZED',r,d);return
 if not r.exists():raise ValueError('run no existe')
 plan=load(r/'execution-plan.json');gates=load(r/'gate-register.json');scope=load(r/'scope-manifest.json');tasks=plan['tasks']
 if plan.get('schema_version')!=SCHEMA:raise ValueError(f"corrida con schema_version {plan.get('schema_version')!r}; este CLI usa {SCHEMA!r}. Crear una corrida nueva con init")
 if a.command=='check':
  assert all(t['skill'] in SKILLS for t in tasks)
  assert all(t['state'] in STATES for t in tasks), 'estado de tarea invalido'
  seen=set()
  for t in tasks:
   assert all(dep in seen for dep in t['depends_on']), 'DAG invalido'
   assert t['entry_gate'] in gates and t['completion_gate'] in gates
   seen.add(t['id'])
  print('CHECK OK',len(tasks),'tasks');return
 if a.command=='status':
  print(json.dumps({'scenario':plan['scenario'],'tasks':tasks,'gates':gates},ensure_ascii=False,indent=2));return
 if a.command in ('transition','complete'):
  to='DONE' if a.command=='complete' else a.to
  t=next((x for x in tasks if x['id']==a.task),None)
  if not t:raise ValueError('tarea desconocida')
  if to not in STATES:raise ValueError('estado destino requerido: '+', '.join(sorted(STATES)))
  if to not in TRANS[t['state']]:raise ValueError(f"transicion no permitida: {t['state']} -> {to}")
  if not a.actor:raise ValueError('actor requerido')
  reason=a.reason or ('revision completada' if to=='DONE' else None)
  if not reason:raise ValueError('motivo (--reason) requerido')
  if to=='IN_PROGRESS':
   if not gates[t['entry_gate']]['approved']:raise ValueError('gate de entrada no aprobado')
   if any(next(x for x in tasks if x['id']==dep)['state']!='DONE' for dep in t['depends_on']):raise ValueError('dependencias incompletas')
  ev=None
  if to in ('NEEDS_REVIEW','DONE'):
   if not a.evidence or not pathlib.Path(a.evidence).exists():raise ValueError('evidencia debe existir')
   ev=str(pathlib.Path(a.evidence).resolve());t['evidence'].append(ev)
  old=t['state'];t['state']=to
  plan.setdefault('history',[]).append({'task':t['id'],'from':old,'to':to,'actor':a.actor,'reason':reason,'evidence':ev,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  save(r/'execution-plan.json',plan);print(t['id'],old,'->',to);return
 if a.command=='approve-gate':
  if a.gate not in gates:raise ValueError('gate desconocido')
  if not a.actor or not a.actor.startswith('human:') or not a.evidence:raise ValueError('actor humano y evidencia requeridos')
  if a.gate=='G0':
   if not scope['sources'] or not scope['adr_refs']:raise ValueError('G0 requiere fuentes y ADR')
  else:
   order=sorted(gates,key=lambda g:int(g[1:]));prior=order[order.index(a.gate)-1]
   if not gates[prior]['approved']:raise ValueError('gate previo pendiente')
   required=[t for t in tasks if t['completion_gate']==a.gate]
   if not required or any(t['state']!='DONE' for t in required):raise ValueError('tareas del gate incompletas')
  gates[a.gate]={'approved':True,'actor':a.actor,'evidence':a.evidence,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()};save(r/'gate-register.json',gates);print('APPROVED',a.gate)
if __name__=='__main__':
 try:main()
 except (ValueError,AssertionError) as e:print('ERROR:',e,file=sys.stderr);sys.exit(2)
