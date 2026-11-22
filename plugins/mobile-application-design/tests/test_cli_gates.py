import json, subprocess, sys, tempfile, unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
WF = str(ROOT / 'scripts' / 'workflow.py')


def call(ws, *args, ok=True):
    p = subprocess.run([sys.executable, WF, *args, '--workspace', str(ws), '--run-id', 'r1'], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args, p.stdout, p.stderr)
    return p


class CliGatesTest(unittest.TestCase):
    def run_dir(self, ws):
        return Path(ws) / '.comsatel/mobile-application-design/runs/r1'

    def test_escenario_sin_distinguir_mayusculas(self):
        # D-12(a)
        for sc in ('greenfield', 'Greenfield', 'EVOLUTION'):
            with tempfile.TemporaryDirectory() as t:
                p = subprocess.run([sys.executable, WF, 'init', '--workspace', t, '--run-id', 'r1', '--scenario', sc], capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertEqual(json.loads((self.run_dir(t) / 'state.json').read_text())['scenario'], sc.lower())

    def test_ciclo_completo_con_gates_humanos(self):
        # D-12(b) y D-13: status/start/complete/approve/check con las reglas de web
        with tempfile.TemporaryDirectory() as t:
            call(t, 'init', '--scenario', 'greenfield')
            self.assertEqual(len(json.loads(call(t, 'status').stdout)['tasks']), 4)
            skill = json.loads(call(t, 'status').stdout)['tasks'][0]['skill']
            call(t, 'start', '--task', skill, ok=False)                                       # G0 sin aprobar
            call(t, 'approve', '--gate', 'G0', '--actor', 'human:x', '--evidence', 'e', ok=False)  # sin sources
            mf = self.run_dir(t) / 'scope-manifest.yaml'
            m = yaml.safe_load(mf.read_text()); m['sources'] = ['DSP-001']; m['missing_sources'] = []; mf.write_text(yaml.safe_dump(m))
            call(t, 'approve', '--gate', 'G0', '--actor', 'reviewer', '--evidence', 'e', ok=False)  # sin prefijo human:
            call(t, 'approve-gate', '--gate', 'G0', '--actor', 'human:x', '--evidence', 'e')
            call(t, 'start', '--task', skill)
            ev = Path(t) / 'design/mobile/r1/out.md'; ev.write_text('x')
            call(t, 'complete', '--task', skill, '--evidence', str(ev))
            self.assertFalse(json.loads(call(t, 'check').stdout)['ready_for_handoff'])
            call(t, 'approve', '--gate', 'G2', '--actor', 'human:x', '--evidence', 'e')
            self.assertEqual(json.loads((self.run_dir(t) / 'gate-register.json').read_text())['G2']['status'], 'approved')


if __name__ == '__main__':
    unittest.main()
