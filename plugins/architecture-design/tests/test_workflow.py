import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import workflow as w

SKILL=lambda n:'architecture-'+n
EXPECTED={
 'greenfield':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','development-handoff'],
 'brownfield':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','conformance-assessor','development-handoff'],
 'evolution':['context-and-evidence-designer','asr-and-solution-designer','decision-governor','conformance-assessor','evolution-governor','development-handoff'],
}
OMITTED={'greenfield':['G4','G5'],'brownfield':['G5'],'evolution':[]}

def manifest(path,task,tasks_by_id):
    t=tasks_by_id[task]
    path.write_text(json.dumps({'producer':t['skill'],'inputs':[],'outputs':[],'sources':[],'open_questions':[],'gate':t['gate'],'status':'pending_human_review'}))
    return path

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def run_dir(self,scenario,name='r1'):
        return w.init(self.root,name,scenario)

    def test_each_scenario_has_its_own_chain(self):
        for sc,names in EXPECTED.items():
            plan=json.loads((self.run_dir(sc,sc)/'execution-plan.json').read_text())
            self.assertEqual([t['skill'] for t in plan['tasks']],[SKILL(n) for n in names],sc)
            self.assertEqual([o['gate'] for o in plan['omissions']],OMITTED[sc],sc)

    def test_entry_gate_always_precedes_completion_gate(self):
        for sc in EXPECTED:
            plan=json.loads((self.run_dir(sc,sc)/'execution-plan.json').read_text())
            order=['G0','G1','G2','G3','G4','G5','G6']
            for t in plan['tasks']:
                self.assertLess(order.index(t['entry_gate']),order.index(t['gate']),(sc,t['id']))
            w.check(self.root/'.comsatel'/'architecture-design'/'runs'/sc)

    def test_continuous_governance_is_evolution(self):
        plan=json.loads((self.run_dir('continuous-governance','cg')/'execution-plan.json').read_text())
        self.assertEqual([t['skill'] for t in plan['tasks']],[SKILL(n) for n in EXPECTED['evolution']])
        self.assertEqual(plan['scenario'],'evolution')

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):w.init(self.root,'x','nope')

    def test_full_run_completes_every_scenario(self):
        for sc in EXPECTED:
            r=self.run_dir(sc,sc)
            plan=json.loads((r/'execution-plan.json').read_text());by={t['id']:t for t in plan['tasks']}
            with self.assertRaises(ValueError):w.approve_gate(r,'G0','human:a','ev')  # scope sources missing
            scope=json.loads((r/'scope-manifest.json').read_text());scope['sources']=['RCP-1'];scope['missing_sources']=[]
            (r/'scope-manifest.json').write_text(json.dumps(scope))
            w.approve_gate(r,'G0','human:a','ev')
            for t in plan['tasks']:
                w.transition(r,t['id'],'READY','agent:o','entry gate approved')
                w.transition(r,t['id'],'IN_PROGRESS','agent:o','start')
                m=manifest(self.root/(t['id']+'.json'),t['id'],by)
                w.transition(r,t['id'],'NEEDS_REVIEW','agent:o','done',manifest=m)
                w.transition(r,t['id'],'DONE','human:a','reviewed',manifest=m)
                if t['gate']=='G6':
                    for o in plan['omissions']:w.justify_omission(r,o['gate'],'no aplica en '+sc)
                w.approve_gate(r,t['gate'],'human:a','ev-'+t['gate'])
            gates=json.loads((r/'state.json').read_text())['gates']
            self.assertTrue(all(g['status']=='approved' for g in gates.values()),sc)

    def test_task_cannot_start_before_entry_gate(self):
        r=self.run_dir('greenfield')
        with self.assertRaises(ValueError):w.transition(r,'T01','READY','agent:o','too early')

    def test_gate_needs_its_tasks_done_and_previous_gate(self):
        r=self.run_dir('greenfield')
        scope=json.loads((r/'scope-manifest.json').read_text());scope['sources']=['x'];scope['missing_sources']=[]
        (r/'scope-manifest.json').write_text(json.dumps(scope));w.approve_gate(r,'G0','human:a','ev')
        with self.assertRaises(ValueError):w.approve_gate(r,'G1','human:a','ev')   # T01 not DONE
        with self.assertRaises(ValueError):w.approve_gate(r,'G2','human:a','ev')   # G1 pending

    def test_gates_need_human_actor(self):
        r=self.run_dir('greenfield')
        with self.assertRaises(ValueError):w.approve_gate(r,'G0','agent:o','ev')

    def test_manifest_must_match_task(self):
        r=self.run_dir('greenfield')
        scope=json.loads((r/'scope-manifest.json').read_text());scope['sources']=['x'];scope['missing_sources']=[]
        (r/'scope-manifest.json').write_text(json.dumps(scope));w.approve_gate(r,'G0','human:a','ev')
        w.transition(r,'T01','READY','a','r');w.transition(r,'T01','IN_PROGRESS','a','r')
        bad=self.root/'bad.json';bad.write_text(json.dumps({'producer':'other','inputs':[],'outputs':[],'sources':[],'open_questions':[],'gate':'G1','status':'x'}))
        with self.assertRaises(ValueError):w.transition(r,'T01','NEEDS_REVIEW','a','r',manifest=bad)
        with self.assertRaises(ValueError):w.transition(r,'T01','NEEDS_REVIEW','a','r')

    def test_handoff_blocked_until_omissions_justified(self):
        r=self.run_dir('greenfield')
        plan=json.loads((r/'execution-plan.json').read_text());by={t['id']:t for t in plan['tasks']}
        scope=json.loads((r/'scope-manifest.json').read_text());scope['sources']=['x'];scope['missing_sources']=[]
        (r/'scope-manifest.json').write_text(json.dumps(scope));w.approve_gate(r,'G0','human:a','ev')
        for t in plan['tasks']:
            w.transition(r,t['id'],'READY','a','r');w.transition(r,t['id'],'IN_PROGRESS','a','r')
            m=manifest(self.root/(t['id']+'.json'),t['id'],by)
            w.transition(r,t['id'],'NEEDS_REVIEW','a','r',manifest=m);w.transition(r,t['id'],'DONE','human:a','r',manifest=m)
            if t['gate']!='G6':w.approve_gate(r,t['gate'],'human:a','ev')
        with self.assertRaises(ValueError):w.approve_gate(r,'G6','human:a','ev')
        for o in plan['omissions']:w.justify_omission(r,o['gate'],'no aplica')
        w.approve_gate(r,'G6','human:a','ev')

if __name__=='__main__':unittest.main()
