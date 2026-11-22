import unittest,subprocess,tempfile,pathlib,json,sys
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/workflow.py'
class WorkflowTest(unittest.TestCase):
 def call(self,workspace,scenario,command,*args,ok=True):
  p=subprocess.run([sys.executable,str(SCRIPT),command,'--workspace',workspace,'--run-id','case',*args],capture_output=True,text=True)
  self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr)
  return p
 def test_scenarios(self):
  for scenario in ['greenfield','brownfield','evolution']:
   with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as w:
    self.call(w,scenario,'init','--scenario',scenario)
    self.call(w,scenario,'check')
    self.call(w,scenario,'approve-gate','--gate','G0','--actor','human:reviewer','--evidence','MR-1',ok=False)
    scope=pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/scope-manifest.json';data=json.loads(scope.read_text());data['sources']=['example.md'];data['adr_refs']=['ADR-014'];scope.write_text(json.dumps(data))
    self.call(w,scenario,'approve-gate','--gate','G0','--actor','human:reviewer','--evidence','MR-1')
    evidence=pathlib.Path(w)/'evidence.txt';evidence.write_text('review')
    plan=json.loads((pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/execution-plan.json').read_text())
    for task in plan['tasks']:
     self.call(w,scenario,'transition','--task',task['id'],'--to','IN_PROGRESS','--actor','agent:dm','--reason','inicio')
     self.call(w,scenario,'transition','--task',task['id'],'--to','NEEDS_REVIEW','--actor','agent:dm','--reason','entrega','--evidence',str(evidence))
     self.call(w,scenario,'complete','--task',task['id'],'--actor','human:reviewer','--evidence',str(evidence))
     self.call(w,scenario,'approve-gate','--gate',task['completion_gate'],'--actor','human:reviewer','--evidence',str(evidence))
 def plan(self,w):
  return json.loads((pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/execution-plan.json').read_text())['tasks']
 def test_gate_numbers_are_fixed_per_skill(self):
  expected={'greenfield':['dm-data-boundary-designer','dm-logical-model-designer','dm-physical-model-designer','dm-database-migration-designer','dm-data-design-validator'],
            'brownfield':['dm-schema-reconstruction-analyzer','dm-data-boundary-designer','dm-data-design-validator'],
            'evolution':['dm-schema-reconstruction-analyzer','dm-data-boundary-designer','dm-logical-model-designer','dm-physical-model-designer','dm-database-migration-designer','dm-data-design-validator']}
  gate_of={'dm-schema-reconstruction-analyzer':'G1','dm-data-boundary-designer':'G2','dm-logical-model-designer':'G3','dm-physical-model-designer':'G4','dm-database-migration-designer':'G5','dm-data-design-validator':'G6'}
  for scenario,skills in expected.items():
   with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as w:
    self.call(w,scenario,'init','--scenario',scenario)
    tasks=self.plan(w)
    self.assertEqual(skills,[t['skill'] for t in tasks])
    self.assertEqual([gate_of[s] for s in skills],[t['completion_gate'] for t in tasks])
    self.assertEqual('G0',tasks[0]['entry_gate'])
    self.assertEqual([t['completion_gate'] for t in tasks[:-1]],[t['entry_gate'] for t in tasks[1:]])
 def test_greenfield_has_no_as_is_and_has_initial_migration(self):
  with tempfile.TemporaryDirectory() as w:
   self.call(w,'greenfield','init','--scenario','greenfield')
   skills=[t['skill'] for t in self.plan(w)]
   self.assertNotIn('dm-schema-reconstruction-analyzer',skills)
   self.assertIn('dm-database-migration-designer',skills)
 def test_gate_cannot_skip_previous_gate_of_the_scenario(self):
  with tempfile.TemporaryDirectory() as w:
   self.call(w,'brownfield','init','--scenario','brownfield')
   scope=pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/scope-manifest.json';d=json.loads(scope.read_text());d['sources']=['x.md'];d['adr_refs']=['ADR-1'];scope.write_text(json.dumps(d))
   self.call(w,'brownfield','approve-gate','--gate','G0','--actor','human:r','--evidence','MR-1')
   self.call(w,'brownfield','approve-gate','--gate','G6','--actor','human:r','--evidence','MR-1',ok=False)
   self.call(w,'brownfield','approve-gate','--gate','G2','--actor','human:r','--evidence','MR-1',ok=False)
   self.call(w,'brownfield','approve-gate','--gate','G1','--actor','agent:x','--evidence','MR-1',ok=False)
 def approved_run(self,w,scenario='evolution'):
  self.call(w,scenario,'init','--scenario',scenario)
  scope=pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/scope-manifest.json';d=json.loads(scope.read_text());d['sources']=['x.md'];d['adr_refs']=['ADR-1'];scope.write_text(json.dumps(d))
  self.call(w,scenario,'approve-gate','--gate','G0','--actor','human:r','--evidence','MR-1')
  ev=pathlib.Path(w)/'ev.txt';ev.write_text('x');return str(ev)
 def state(self,w,tid='T01'):
  return next(t for t in self.plan(w) if t['id']==tid)['state']
 def test_task_states_follow_the_allowed_transitions(self):
  with tempfile.TemporaryDirectory() as w:
   ev=self.approved_run(w)
   self.call(w,'evolution','complete','--task','T01','--actor','human:r','--evidence',ev,ok=False)
   self.call(w,'evolution','transition','--task','T01','--to','DONE','--actor','human:r','--reason','x','--evidence',ev,ok=False)
   self.call(w,'evolution','transition','--task','T01','--to','NEEDS_REVIEW','--actor','a','--reason','x','--evidence',ev,ok=False)
   self.call(w,'evolution','transition','--task','T01','--to','IN_PROGRESS','--actor','a','--reason','inicio')
   self.assertEqual('IN_PROGRESS',self.state(w))
   self.call(w,'evolution','transition','--task','T01','--to','NEEDS_REVIEW','--actor','a','--reason','entrega',ok=False)
   self.call(w,'evolution','transition','--task','T01','--to','BLOCKED','--actor','a','--reason','falta fuente')
   self.assertEqual('BLOCKED',self.state(w))
   self.call(w,'evolution','transition','--task','T01','--to','IN_PROGRESS','--actor','a','--reason','retomado')
   self.call(w,'evolution','transition','--task','T01','--to','NEEDS_REVIEW','--actor','a','--reason','entrega','--evidence',ev)
   self.call(w,'evolution','complete','--task','T01','--actor','human:r','--evidence',ev)
   self.assertEqual('DONE',self.state(w))
   self.call(w,'evolution','transition','--task','T01','--to','IN_PROGRESS','--actor','a','--reason','x',ok=False)
   hist=json.loads((pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/execution-plan.json').read_text())['history']
   self.assertEqual(['IN_PROGRESS','BLOCKED','IN_PROGRESS','NEEDS_REVIEW','DONE'],[h['to'] for h in hist])
 def test_task_needs_entry_gate_and_previous_task_done(self):
  with tempfile.TemporaryDirectory() as w:
   ev=self.approved_run(w)
   self.call(w,'evolution','transition','--task','T02','--to','IN_PROGRESS','--actor','a','--reason','x',ok=False)
 def test_old_runs_without_schema_version_are_rejected(self):
  with tempfile.TemporaryDirectory() as w:
   self.call(w,'evolution','init','--scenario','evolution')
   self.call(w,'evolution','check')
   path=pathlib.Path(w)/'.comsatel/data-modeling-database-design/runs/case/execution-plan.json';d=json.loads(path.read_text());del d['schema_version'];path.write_text(json.dumps(d))
   for cmd in ('check','status'):
    p=self.call(w,'evolution',cmd,ok=False)
    self.assertIn('schema_version',p.stderr)
if __name__=='__main__':unittest.main()


class ValidatorsTest(unittest.TestCase):
 def test_plantillas_ldm_pdm_dbm_dbr_pasan_validate_okf(self):
  # D-06: los skills mandan ejecutar validadores; deben existir y aceptar las plantillas del plugin
  root=pathlib.Path(__file__).resolve().parents[1]
  for t in ('ldm','pdm','dbm','dbr'):
   p=subprocess.run([sys.executable,str(root/'scripts/validate_okf.py'),str(root/'templates'/f'{t}-okf.md')],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
 def test_validate_okf_rechaza_tipo_no_registrado_y_skills_delegan(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as td:
   f=pathlib.Path(td)/'x.md';f.write_text((root/'templates/ldm-okf.md').read_text(encoding='utf-8').replace('type: LDM','type: ZZZ'),encoding='utf-8')
   self.assertNotEqual(subprocess.run([sys.executable,str(root/'scripts/validate_okf.py'),str(f)],capture_output=True).returncode,0)
  for v in root.glob('skills/dm-*/scripts/validate.py'):
   self.assertEqual(subprocess.run([sys.executable,str(v),str(root/'templates/ldm-okf.md')],capture_output=True).returncode,0,v)
  self.assertEqual(len(list(root.glob('skills/dm-*/scripts/validate.py'))),6)
