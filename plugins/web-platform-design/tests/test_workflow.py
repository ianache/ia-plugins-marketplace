import pathlib,subprocess,tempfile,unittest
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/workflow.py'
class WorkflowTest(unittest.TestCase):
 def call(self,w,*args,ok=True):
  p=subprocess.run(['python',str(SCRIPT),*args,'--workspace',str(w),'--run-id','r1'],capture_output=True,text=True)
  self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr);return p
 def fill_scope(self,w):
  import yaml
  f=w/'.comsatel/web-platform-design/runs/r1/scope-manifest.yaml';m=yaml.safe_load(f.read_text(encoding='utf-8'))
  m['sources']=['DSP-001'];m['missing_sources']=[];f.write_text(yaml.safe_dump(m),encoding='utf-8')
 def test_init_crea_scope_manifest_y_g0_lo_exige(self):
  # D-13: init crea el manifiesto; G0 exige sources completas
  import yaml
  with tempfile.TemporaryDirectory() as td:
   w=pathlib.Path(td);self.call(w,'init','--scenario','greenfield')
   m=yaml.safe_load((w/'.comsatel/web-platform-design/runs/r1/scope-manifest.yaml').read_text(encoding='utf-8'))
   self.assertEqual(m['sources'],[]);self.assertTrue(m['missing_sources'])
   p=self.call(w,'approve','--gate','G0','--actor','human:x','--evidence','e',ok=False);self.assertIn('sources',p.stderr+p.stdout)
   self.fill_scope(w);self.call(w,'approve','--gate','G0','--actor','human:x','--evidence','e')
 def test_escenario_sin_distinguir_mayusculas(self):
  # D-12(a)
  with tempfile.TemporaryDirectory() as td:
   self.call(pathlib.Path(td),'init','--scenario','Greenfield')
 def test_scenarios_and_gates(self):
  for scenario in ('greenfield','brownfield','evolution'):
   with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as td:
    w=pathlib.Path(td);self.call(w,'init','--scenario',scenario)
    self.call(w,'start','--task','architecture',ok=False)
    self.call(w,'approve','--gate','G0','--actor','human:reviewer','--evidence','scope-reviewed',ok=False)
    self.fill_scope(w)
    self.call(w,'approve','--gate','G0','--actor','human:reviewer','--evidence','scope-reviewed')
    import json
    s=json.loads((w/'.comsatel/web-platform-design/runs/r1/state.json').read_text());tasks=list(s['tasks'])
    for t in tasks:
     self.call(w,'start','--task',t)
     ev=w/'design/web/r1'/f'{t}.md';ev.write_text('evidence')
     self.call(w,'complete','--task',t,'--evidence',str(ev))
     gate={'reconstruction':'G1','architecture':'G2','composition':'G3','integration':'G4','evolution':'G5','handoff':'G6'}[t]
     self.call(w,'approve','--gate',gate,'--actor','human:reviewer','--evidence',str(ev))
    self.assertIn('"ready_for_handoff": true',self.call(w,'check').stdout)
 def test_approve_exige_prefijo_human(self):
  with tempfile.TemporaryDirectory() as td:
   w=pathlib.Path(td);self.call(w,'init','--scenario','greenfield')
   self.call(w,'approve','--gate','G0','--actor','reviewer','--evidence','x',ok=False)
if __name__=='__main__':unittest.main()
