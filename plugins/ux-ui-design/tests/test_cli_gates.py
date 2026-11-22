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
        return Path(ws) / '.comsatel/ux-ui-design/runs/r1'

    def test_escenario_sin_distinguir_mayusculas_y_modo_anterior(self):
        # D-12(a); el modo anterior `workflow.py <run-id>` sigue funcionando
        for sc in ('greenfield', 'Brownfield'):
            with tempfile.TemporaryDirectory() as t:
                self.assertEqual(subprocess.run([sys.executable, WF, 'init', '--workspace', t, '--run-id', 'r1', '--scenario', sc], capture_output=True).returncode, 0)
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(subprocess.run([sys.executable, WF, 'r1', '--workspace', t, '--scenario', 'greenfield'], capture_output=True).returncode, 0)
            self.assertTrue((self.run_dir(t) / 'scope-manifest.yaml').is_file())

    def test_ciclo_completo_con_gates_humanos(self):
        # D-12(b) y D-13
        with tempfile.TemporaryDirectory() as t:
            call(t, 'init', '--scenario', 'greenfield')
            call(t, 'start', '--task', 'ux-requirements-flow-designer', ok=False)
            call(t, 'approve', '--gate', 'G0', '--actor', 'human:x', '--evidence', 'e', ok=False)
            mf = self.run_dir(t) / 'scope-manifest.yaml'
            m = yaml.safe_load(mf.read_text()); m['sources'] = ['DSP-001']; m['missing_sources'] = []; mf.write_text(yaml.safe_dump(m))
            call(t, 'approve', '--gate', 'G0', '--actor', 'reviewer', '--evidence', 'e', ok=False)
            call(t, 'approve-gate', '--gate', 'G0', '--actor', 'human:x', '--evidence', 'e')
            call(t, 'start', '--task', 'ux-requirements-flow-designer')
            ev = Path(t) / 'design/ux-ui/r1/out.md'; ev.write_text('x')
            call(t, 'complete', '--task', 'ux-requirements-flow-designer', '--evidence', str(ev))
            call(t, 'start', '--task', 'ui-screen-specification-designer', ok=False)  # G1 sin aprobar
            call(t, 'approve', '--gate', 'G1', '--actor', 'human:x', '--evidence', 'e')
            call(t, 'start', '--task', 'ui-screen-specification-designer')
            self.assertEqual(json.loads((self.run_dir(t) / 'gate-register.json').read_text())['G1']['approved_by'], 'human:x')
            self.assertFalse(json.loads(call(t, 'check').stdout)['ready_for_handoff'])


if __name__ == '__main__':
    unittest.main()
