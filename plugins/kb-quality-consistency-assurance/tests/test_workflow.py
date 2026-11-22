import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_workflow import validate
class TestWorkflow(unittest.TestCase):
 def test_valid(self):
  self.assertEqual(validate({'nodes':[{'id':'T01','kind':'task','depends_on':[]},{'id':'G1','kind':'gate','depends_on':['T01'],'evaluates':['T01']},{'id':'T02','kind':'task','depends_on':['G1']}]}),[])
 def test_t02_g1_cycle(self):
  self.assertTrue(any('cycle' in x for x in validate({'nodes':[{'id':'T02','kind':'task','depends_on':['G1']},{'id':'G1','kind':'gate','depends_on':['T02'],'evaluates':['T02']}]})))
 def test_missing_producer(self):
  self.assertTrue(validate({'nodes':[{'id':'G1','kind':'gate','depends_on':[],'evaluates':['T01']}]}))
 def test_gate_before_producer(self):
  self.assertTrue(validate({'nodes':[{'id':'T01','kind':'task','depends_on':[]},{'id':'G1','kind':'gate','depends_on':[],'evaluates':['T01']}]}))
if __name__=='__main__':unittest.main()
