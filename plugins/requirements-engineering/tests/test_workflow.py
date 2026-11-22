import importlib.util, json, pathlib, tempfile, unittest
P = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'workflow.py'
s = importlib.util.spec_from_file_location('wf', P); wf = importlib.util.module_from_spec(s); s.loader.exec_module(wf)


class A:
    def __init__(self, **k): self.__dict__.update(k)


class WorkflowTests(unittest.TestCase):
    def run_dir(self, scenario='greenfield', just=None):
        d = tempfile.TemporaryDirectory(); self.addCleanup(d.cleanup)
        r = pathlib.Path(d.name) / '.comsatel/requirements-engineering/runs/RUN-1'
        wf.init(A(run=str(r), scenario=scenario, workspace=d.name, justification=just))
        (pathlib.Path(d.name) / 'evidence.md').write_text('ok', encoding='utf-8')
        return r

    def test_no_gate_cycle_in_any_scenario(self):
        for sc in wf.SCENARIOS:
            r = self.run_dir(sc, 'solo impacto' if sc == 'impact-only' else None)
            for t in wf.check(r)[0]['tasks']:
                self.assertLess(wf.GATES.index(t['entry_gate']), wf.GATES.index(t['gate']))

    def test_full_chain_in_order(self):
        r = self.run_dir()
        wf.approve(A(run=str(r), gate='G0', actor='human:ana', evidence='evidence.md'))
        with self.assertRaises(ValueError): wf.approve(A(run=str(r), gate='G2', actor='human:ana', evidence='x'))  # G1 sin aprobar
        for tid in ['T01']:
            for to in ('READY', 'IN_PROGRESS', 'NEEDS_REVIEW', 'DONE'):
                wf.transition(A(run=str(r), task=tid, to=to, actor='agent', reason='r', evidence='evidence.md'))
        wf.approve(A(run=str(r), gate='G1', actor='human:ana', evidence='evidence.md'))
        with self.assertRaises(ValueError):  # T02 (US) exige G2 aprobado y G2 aún no lo está
            wf.transition(A(run=str(r), task='T02', to='READY', actor='agent', reason='r', evidence=None))
        wf.approve(A(run=str(r), gate='G2', actor='human:ana', evidence='evidence.md'))
        wf.transition(A(run=str(r), task='T02', to='READY', actor='agent', reason='r', evidence=None))

    def test_evidencia_debe_ser_archivo_existente_dentro_del_workspace(self):
        # D-21: texto libre, archivos inexistentes o fuera del workspace se rechazan; se guarda la ruta relativa
        r = self.run_dir()
        for malo in ('no-existe.md', 'x', 'texto libre', 'MR-12'):
            with self.assertRaises(ValueError, msg=malo):
                wf.approve(A(run=str(r), gate='G0', actor='human:ana', evidence=malo))
        with tempfile.TemporaryDirectory() as fuera:
            f = pathlib.Path(fuera) / 'ev.md'; f.write_text('x', encoding='utf-8')
            with self.assertRaises(ValueError):
                wf.approve(A(run=str(r), gate='G0', actor='human:ana', evidence=str(f)))
        wf.approve(A(run=str(r), gate='G0', actor='human:ana', evidence='evidence.md'))
        self.assertEqual(json.loads((r / 'gate-register.json').read_text(encoding='utf-8'))['gates'][0]['evidence'], ['evidence.md'])
        for to in ('READY', 'IN_PROGRESS'):
            wf.transition(A(run=str(r), task='T01', to=to, actor='agent', reason='r', evidence=None))
        with self.assertRaises(ValueError):
            wf.transition(A(run=str(r), task='T01', to='NEEDS_REVIEW', actor='agent', reason='r', evidence='no-existe.md'))

    def test_g2_is_a_human_gate_without_task(self):
        p = wf.check(self.run_dir())[0]
        self.assertEqual([t['gate'] for t in p['tasks']], ['G1', 'G3', 'G4', 'G5', 'G6'])
        self.assertNotIn('af-business-rules-modeler', [t['skill'] for t in p['tasks']])
        self.assertEqual(next(t for t in p['tasks'] if t['gate'] == 'G3')['entry_gate'], 'G2')

    def test_human_actor_required(self):
        r = self.run_dir()
        with self.assertRaises(ValueError): wf.approve(A(run=str(r), gate='G0', actor='agent', evidence='x'))

    def test_impact_only_needs_justification_and_skips_g3_g4(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / '.comsatel/requirements-engineering/runs/R'
            with self.assertRaises(ValueError): wf.init(A(run=str(r), scenario='impact-only', workspace=d, justification=None))
        r = self.run_dir('impact-only', 'análisis aislado')
        p = wf.check(r)[0]
        self.assertEqual([t['gate'] for t in p['tasks']], ['G1', 'G5', 'G6'])
        self.assertEqual(next(t for t in p['tasks'] if t['gate'] == 'G5')['entry_gate'], 'G2')

    def test_cycle_detected(self):
        r = self.run_dir()
        p = json.loads((r / 'execution-plan.json').read_text()); p['tasks'][1]['entry_gate'] = 'G3'
        (r / 'execution-plan.json').write_text(json.dumps(p))
        with self.assertRaises(ValueError): wf.check(r)


if __name__ == '__main__':
    unittest.main()
