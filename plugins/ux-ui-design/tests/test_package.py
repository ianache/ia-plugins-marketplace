import unittest,subprocess,sys,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PluginTest(unittest.TestCase):
 def test_structure(self):subprocess.run([sys.executable,str(ROOT/'scripts/validate_plugin.py')],check=True)
 def test_scenarios(self):
  for scenario in ['Greenfield','Brownfield','Evolution']:
   with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),'lab-001','--workspace',tmp,'--scenario',scenario],check=True)
    base=Path(tmp);self.assertTrue((base/'.comsatel/ux-ui-design/runs/lab-001/gate-register.json').exists());self.assertTrue((base/'design/ux-ui/lab-001').exists())
    gates=json.loads((base/'.comsatel/ux-ui-design/runs/lab-001/gate-register.json').read_text());self.assertTrue(all(g['status']=='pending' for g in gates.values()))
if __name__=='__main__':unittest.main()
