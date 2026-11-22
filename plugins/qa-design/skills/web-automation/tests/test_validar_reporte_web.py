"""Pruebas del validador de web-automation-report.yaml."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validar_reporte_web.py"
spec = importlib.util.spec_from_file_location("validar_reporte_web", SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

BASE = {
    "aut": "shell-principal",
    "framework": "PLAYWRIGHT",
    "casos": [{"id": "TC-SHELL-012", "estado": "AUTOMATED", "archivos": ["test/functional/playwright/tests/unidades.spec.ts"]}],
    "ejecucion": {"estado": "NOT_EXECUTED", "razon": "El MR aún no ha disparado el pipeline"},
}


def texto_de(datos):
    return yaml.safe_dump(datos, allow_unicode=True, sort_keys=False)


def hallazgos(datos):
    return v.validar(texto_de(datos), datos)


class ValidarReporteWeb(unittest.TestCase):
    def test_reporte_valido_sin_hallazgos(self):
        self.assertEqual(hallazgos(BASE), [])

    def test_ejecutado_sin_pipeline_falla(self):
        d = dict(BASE, ejecucion={"estado": "EXECUTED", "resultados": {"total": 1, "passed": 1, "failed": 0}})
        self.assertTrue(any("pipeline" in h for h in hallazgos(d)))

    def test_ejecutado_con_pipeline_y_resultados_pasa(self):
        d = dict(BASE, ejecucion={"estado": "EXECUTED", "pipeline": "https://ci.example/pipelines/42",
                                  "resultados": {"total": 1, "passed": 1, "failed": 0}})
        self.assertEqual(hallazgos(d), [])

    def test_no_ejecutado_sin_razon_falla(self):
        d = dict(BASE, ejecucion={"estado": "NOT_EXECUTED"})
        self.assertTrue(any("razon" in h for h in hallazgos(d)))

    def test_framework_invalido_falla(self):
        d = dict(BASE, framework="CYPRESS")
        self.assertTrue(any("framework" in h for h in hallazgos(d)))

    def test_id_que_no_es_tc_falla(self):
        d = dict(BASE, casos=[{"id": "AT-001", "estado": "AUTOMATED"}])
        self.assertTrue(any("TC válido" in h for h in hallazgos(d)))

    def test_caso_duplicado_falla(self):
        caso = {"id": "TC-SHELL-012", "estado": "AUTOMATED"}
        d = dict(BASE, casos=[caso, dict(caso)])
        self.assertTrue(any("duplicado" in h for h in hallazgos(d)))

    def test_estado_de_caso_invalido_falla(self):
        d = dict(BASE, casos=[{"id": "TC-SHELL-012", "estado": "PASS"}])
        self.assertTrue(any("estado inválido" in h for h in hallazgos(d)))

    def test_password_literal_falla(self):
        d = dict(BASE, casos=[{"id": "TC-SHELL-012", "estado": "AUTOMATED", "nota": "password: Hunter2025"}])
        self.assertTrue(any("secreto" in h for h in hallazgos(d)))

    def test_variable_de_entorno_no_es_secreto(self):
        d = dict(BASE, casos=[{"id": "TC-SHELL-012", "estado": "AUTOMATED", "nota": "password: ${TEST_PASSWORD}"}])
        self.assertEqual(hallazgos(d), [])

    def test_url_con_credenciales_falla(self):
        d = dict(BASE, ejecucion={"estado": "NOT_EXECUTED", "razon": "https://user:clave@qa.example.com"})
        self.assertTrue(any("credenciales" in h for h in hallazgos(d)))

    def test_cli_codigos_de_salida(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = Path(tmp) / "ok.yaml"
            ok.write_text(texto_de(BASE), encoding="utf8")
            self.assertEqual(v.main(["x", str(ok)]), 0)
            malo = Path(tmp) / "malo.yaml"
            malo.write_text(texto_de(dict(BASE, framework="X")), encoding="utf8")
            self.assertEqual(v.main(["x", str(malo)]), 1)
            self.assertEqual(v.main(["x", str(Path(tmp) / "no-existe.yaml")]), 2)


if __name__ == "__main__":
    unittest.main()
