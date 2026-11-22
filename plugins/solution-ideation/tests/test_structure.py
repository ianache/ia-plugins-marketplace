import unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestPlugin(unittest.TestCase):
 def test_manifest(self):
  d=json.loads((ROOT/'.claude-plugin/plugin.json').read_text());self.assertEqual(d['name'],'solution-ideation')
 def test_skills_and_resources(self):
  dirs=list((ROOT/'skills').iterdir());self.assertEqual(len(dirs),7)
  for d in dirs:
   self.assertTrue((d/'SKILL.md').exists())
   for f in ('references/contract.md','references/gate-checklist.md','references/technical-guidance.md','templates/deliverable.md','templates/gate-evidence.json','scripts/validate.py','examples/README.md','assets/README.md'):self.assertTrue((d/f).is_file(),f'{d.name}/{f}')
 def test_json(self):
  for p in ROOT.rglob('*.json'):json.loads(p.read_text())
 def test_frontmatter(self):
  for p in (ROOT/'skills').glob('*/SKILL.md'):
   s=p.read_text();self.assertTrue(s.startswith('---\n'));self.assertIn('\nname:',s);self.assertIn('\ndescription:',s)
if __name__=='__main__':unittest.main()
