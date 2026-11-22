import unittest,sys,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_okf import validate
from workflow import init
class Tests(unittest.TestCase):
 def test_skills(self):
  skills=list((ROOT/'skills').glob('*/SKILL.md'));self.assertEqual(len(skills),7)
  for s in skills:
   for rel in ['references/contract.md','references/gate-checklist.md','references/technical-guidance.md']+([] if s.parent.name=='architecture-design-orchestrator' else ['templates/okf-artifact.md'])+['templates/output-manifest.json','scripts/validate.py','examples/README.md','assets/README.md']:
    self.assertTrue((s.parent/rel).is_file(),(s,rel))
 def test_workflow(self):
  with tempfile.TemporaryDirectory() as t:
   init(Path(t),'demo','brownfield');self.assertTrue((Path(t)/'.comsatel/architecture-design/runs/demo/state.json').exists());self.assertTrue((Path(t)/'architecture/adrs').exists());self.assertTrue((Path(t)/'architecture/asrs').exists());self.assertFalse((Path(t)/'architecture/demo').exists())
 def test_invalid_placeholder(self):
  self.assertTrue(validate(ROOT/'skills/architecture-decision-governor/templates/okf-artifact.md'))
if __name__=='__main__':unittest.main()
