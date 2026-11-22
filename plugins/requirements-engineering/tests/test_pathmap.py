import importlib.util,pathlib,tempfile,unittest
P=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'validate_pathmap.py'
s=importlib.util.spec_from_file_location('pathmap',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PathMapTests(unittest.TestCase):
 def test_routes(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'requirements/context-packs/user-stories/US-001.md';p.parent.mkdir(parents=True);p.write_text('---\ntype: US\n---\n# US\n')
   self.assertTrue(m.validate(d,'US',p)[0]);self.assertFalse(m.validate(d,'ADR',p)[0]);self.assertFalse(m.validate(d,'US',pathlib.Path(d)/'requirements/US-001.md')[0])
 def test_unmapped(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'requirements/unknown.md';p.parent.mkdir();p.write_text('---\ntype: XYZ\n---\n')
   self.assertFalse(m.validate(d,'XYZ',p)[0])
class ImpAndBusinessBaseline(unittest.TestCase):
 def test_imp_maps(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'requirements/impact-analysis/IMP-001.md';p.parent.mkdir(parents=True)
   p.write_text('---'+chr(10)+'type: IMP'+chr(10)+'---'+chr(10))
   self.assertTrue(m.validate(d,'IMP',p)[0])
 def test_business_types_belong_to_business_knowledge(self):
  with tempfile.TemporaryDirectory() as d:
   for ty,dr in (('BR','business/rules'),('IMD','business/information-model'),('TRM','business/terms')):
    p=pathlib.Path(d)/dr/(ty+'-001.md');p.parent.mkdir(parents=True)
    p.write_text('---'+chr(10)+'type: '+ty+chr(10)+'---'+chr(10))
    self.assertFalse(m.validate(d,ty,p)[0])
class DspRoute(unittest.TestCase):
 def test_dsp(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'requirements/scope-packs/DSP-001-x.md';p.parent.mkdir(parents=True)
   p.write_text('---'+chr(10)+'type: DSP'+chr(10)+'---'+chr(10))
   self.assertTrue(m.validate(d,'DSP',p)[0])
if __name__=='__main__':unittest.main()
