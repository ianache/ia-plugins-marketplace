import importlib.util
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validar_k6", ROOT / "scripts" / "validar_k6.py")
vk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vk)

K6_APROBADO = """// criterio: APROBADO DATA-04
import { tc01 as _unused } from './scenarios/TC-PE-01.js';
export { tc01 } from './scenarios/TC-PE-01.js';

export const options = {
  scenarios: {
    'TC-PE-01': { executor: 'constant-vus', vus: 5, duration: '30s', exec: 'tc01' },
  },
  thresholds: {
    // umbral-fuente: DATA-04
    'http_req_duration{tc:TC-PE-01}': ['p(95)<1000'],
  },
};
"""

K6_BASELINE = """// criterio: BASELINE
export { tc01 } from './scenarios/TC-PE-01.js';

export const options = {
  scenarios: {
    'TC-PE-01': { executor: 'constant-vus', vus: 5, duration: '30s', exec: 'tc01' },
  },
};
"""

MODULO = """import http from 'k6/http';
import { check } from 'k6';
import { config } from '../lib/config.js';

export function tc01() {
  const res = http.get(`${config.apiUrl}/${config.deployment}/actuator/health`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
"""

CONFIG = """export const config = {
  apiUrl: __ENV.API_URL,
  deployment: __ENV.DEPLOYMENT_NAME,
  token: __ENV.ACCESS_TOKEN,
};
"""


def suite(base, k6=K6_APROBADO, modulo=MODULO, config=CONFIG):
    (base / "scenarios").mkdir(parents=True)
    (base / "lib").mkdir()
    (base / "data").mkdir()
    (base / "k6.js").write_text(k6, encoding="utf8")
    (base / "scenarios" / "TC-PE-01.js").write_text(modulo, encoding="utf8")
    (base / "lib" / "config.js").write_text(config, encoding="utf8")
    (base / "data" / "entradas.json").write_text("[]", encoding="utf8")


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.base = pathlib.Path(t.name) / "test" / "load"
        self.base.mkdir(parents=True)

    def reglas(self):
        return {r for r, _, _ in vk.validar(self.base)}

    def mensajes(self, regla):
        return [m for r, _, m in vk.validar(self.base) if r == regla]


class Suite(Base):
    def test_suite_valida_sin_hallazgos(self):
        suite(self.base)
        self.assertEqual(vk.validar(self.base), [])

    def test_sin_k6js_es_L1(self):
        suite(self.base)
        (self.base / "k6.js").unlink()
        self.assertIn("L1", self.reglas())

    def test_sin_scenarios_es_L1(self):
        suite(self.base)
        shutil.rmtree(self.base / "scenarios")
        self.assertIn("L1", self.reglas())

    def test_modulo_con_nombre_no_tc_es_L1(self):
        suite(self.base)
        (self.base / "scenarios" / "TC-PE-01.js").rename(self.base / "scenarios" / "escenario.js")
        self.assertIn("L1", self.reglas())

    def test_sin_criterio_es_L4(self):
        suite(self.base, k6=K6_APROBADO.replace("// criterio: APROBADO DATA-04\n", ""))
        self.assertIn("L4", self.reglas())

    def test_baseline_con_umbral_es_L4(self):
        suite(self.base, k6=K6_BASELINE.replace("};\n", "  thresholds: { 'http_req_duration': ['p(95)<1000'] },\n};\n"))
        self.assertIn("L4", self.reglas())

    def test_baseline_sin_umbrales_pasa(self):
        suite(self.base, k6=K6_BASELINE)
        self.assertEqual(vk.validar(self.base), [])

    def test_umbral_sin_fuente_es_L4(self):
        suite(self.base, k6=K6_APROBADO.replace("    // umbral-fuente: DATA-04\n", ""))
        self.assertIn("L4", self.reglas())

    def test_exec_no_exportado_es_L3(self):
        suite(self.base, k6=K6_APROBADO.replace("exec: 'tc01'", "exec: 'tc99'"))
        self.assertIn("L3", self.reglas())

    def test_modulo_no_reexportado_es_L3(self):
        suite(self.base, k6=K6_APROBADO.replace("export { tc01 } from './scenarios/TC-PE-01.js';\n", ""))
        self.assertIn("L3", self.reglas())

    def test_import_npm_no_permitido_es_L2(self):
        suite(self.base, modulo=MODULO.replace("import { check } from 'k6';", "import { check } from 'lodash';"))
        self.assertIn("L2", self.reglas())

    def test_import_relativo_inexistente_es_L2(self):
        suite(self.base, modulo=MODULO + "import x from '../lib/no-existe.js';\n")
        self.assertIn("L2", self.reglas())

    def test_jslib_permitido(self):
        suite(self.base, modulo=MODULO.replace("import { check } from 'k6';",
                                               "import { check } from 'k6';\nimport { x } from 'https://jslib.k6.io/x/1.0.0/index.js';"))
        self.assertNotIn("L2", self.reglas())

    def test_url_literal_en_escenario_es_L5(self):
        suite(self.base, modulo=MODULO.replace("`${config.apiUrl}", "'http://10.0.0.5:8080'+`${config.apiUrl}"))
        self.assertIn("L5", self.reglas())

    def test_url_en_comentario_no_cuenta(self):
        suite(self.base, modulo="// ejemplo: https://qa.example.test\n" + MODULO)
        self.assertNotIn("L5", self.reglas())

    def test_bearer_literal_es_L5(self):
        suite(self.base, modulo=MODULO.replace("check(res", "const h = { Authorization: 'Bearer abcdefgh123456' };\n  check(res"))
        self.assertIn("L5", self.reglas())

    def test_password_literal_en_config_es_L5(self):
        suite(self.base, config=CONFIG + "export const pwd = { password: 'hunter2' };\n")
        self.assertIn("L5", self.reglas())

    def test_token_desde_env_no_es_secreto(self):
        suite(self.base)
        self.assertNotIn("L5", self.reglas())

    def test_open_a_datos_inexistentes_es_L6(self):
        suite(self.base, modulo=MODULO + "const d = open('../data/no-existe.json');\n")
        self.assertIn("L6", self.reglas())

    def test_open_a_datos_existentes_pasa(self):
        suite(self.base, modulo=MODULO + "const d = open('../data/entradas.json');\n")
        self.assertNotIn("L6", self.reglas())


class Cli(Base):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "validar_k6.py"), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_cli_0_sin_hallazgos(self):
        suite(self.base)
        self.assertEqual(self.run_cli(str(self.base)).returncode, 0)

    def test_cli_1_con_hallazgos(self):
        suite(self.base, k6=K6_APROBADO.replace("// criterio: APROBADO DATA-04\n", ""))
        self.assertEqual(self.run_cli(str(self.base)).returncode, 1)

    def test_cli_2_si_no_existe_el_directorio(self):
        self.assertEqual(self.run_cli(str(self.base / "no-existe")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
