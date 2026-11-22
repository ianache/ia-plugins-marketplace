import tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from workflow import init
class TestWorkflow(unittest.TestCase):
    def test_scenarios(self):
        for s,n in [('Greenfield',4),('Brownfield',5),('Evolution',6)]:
            with tempfile.TemporaryDirectory() as t:
                init(t,'case-01',s)
                self.assertTrue((Path(t)/'.comsatel/mobile-application-design/runs/case-01/state.json').is_file())
                self.assertTrue((Path(t)/'design/mobile/case-01').is_dir())
                import json
                self.assertEqual(len(json.loads((Path(t)/'.comsatel/mobile-application-design/runs/case-01/state.json').read_text())['tasks']),n)
if __name__=='__main__':unittest.main()
