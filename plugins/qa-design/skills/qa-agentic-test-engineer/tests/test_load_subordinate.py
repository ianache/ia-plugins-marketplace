"""Check load-automation-subordinate-traceable: los AT de TC rendimiento los produce loadtest-automation."""
import unittest

import yaml

from test_check_test_engineering import Pack, md


class LoadSubordinate(Pack):
    def make_load(self, report=None, test_type="rendimiento"):
        self.build()
        (self.d / "TC/TC-001.md").write_text(
            md({"id": "TC-001", "tsn": "TSN-001", "automation_status": "AUTOMATED",
                "tdr_refs": ["TDR-001"], "test_type": test_type}), encoding="utf8")
        (self.e / "automated-tests/AT-001.md").write_text(
            md({"id": "AT-001", "testcase_ref": "TC-001", "tda_refs": ["TDA-001"], "surface": "API"}), encoding="utf8")
        if report is not None:
            (self.e / "automated-tests" / "k6" / "position-enricher").mkdir(parents=True, exist_ok=True)
            rep = dict(report)
            rep.setdefault("k6", {"estado": "EXECUTED"})
            (self.e / "automated-tests/k6/position-enricher/loadtest-automation-report.yaml").write_text(
                yaml.safe_dump(rep, allow_unicode=True), encoding="utf8")

    def check(self):
        return self.res()["load-automation-subordinate-traceable"]

    def reporte(self, **over):
        base = {"criterio": "BASELINE", "casos": [{"id": "TC-001", "estado": "IMPLEMENTED"}]}
        base.update(over)
        return base

    def test_at_rendimiento_sin_reporte_falla(self):
        self.make_load(report=None)
        self.assertEqual(self.check(), "FAIL")

    def test_reporte_baseline_implementado_y_ejecutado_pasa(self):
        self.make_load(report=self.reporte())
        self.assertEqual(self.check(), "PASS")

    def test_reporte_aprobado_con_fuente_pasa(self):
        self.make_load(report=self.reporte(criterio="APROBADO DATA-04"))
        self.assertEqual(self.check(), "PASS")

    def test_criterio_ausente_falla(self):
        self.make_load(report=self.reporte(criterio=None))
        self.assertEqual(self.check(), "FAIL")

    def test_criterio_aprobado_sin_fuente_falla(self):
        self.make_load(report=self.reporte(criterio="APROBADO"))
        self.assertEqual(self.check(), "FAIL")

    def test_tc_no_implementado_falla(self):
        self.make_load(report=self.reporte(casos=[{"id": "TC-001", "estado": "BLOCKED_CLARIFICATION"}]))
        self.assertEqual(self.check(), "FAIL")

    def test_tc_ausente_del_reporte_falla(self):
        self.make_load(report=self.reporte(casos=[{"id": "TC-999", "estado": "IMPLEMENTED"}]))
        self.assertEqual(self.check(), "FAIL")

    def test_k6_no_ejecutado_falla(self):
        self.make_load(report=self.reporte(k6={"estado": "NOT_EXECUTED"}))
        self.assertEqual(self.check(), "FAIL")

    def test_at_no_rendimiento_no_exige_reporte_de_carga(self):
        self.make_load(report=None, test_type="positivo")
        self.assertEqual(self.check(), "PASS")

    def test_api_postman_ignora_los_tc_rendimiento(self):
        # Sin reporte de postman: el AT de rendimiento no debe exigirlo al check funcional.
        self.make_load(report=self.reporte())
        self.assertEqual(self.res()["api-automation-subordinate-traceable"], "PASS")


if __name__ == "__main__":
    unittest.main()
