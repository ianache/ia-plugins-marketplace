"""Check web-automation-subordinate-traceable: los AT de superficie WEB se producen con web-automation."""
import unittest

import yaml

from test_check_test_engineering import Pack, md


class WebSubordinate(Pack):
    def make_web(self, report=None, ejecucion="EXECUTED"):
        self.build()
        (self.e / "automated-tests/AT-001.md").write_text(
            md({"id": "AT-001", "testcase_ref": "TC-001", "tda_refs": ["TDA-001"], "surface": "WEB"}), encoding="utf8")
        if report is not None:
            (self.e / "automated-tests" / "web" / "shell-principal").mkdir(parents=True, exist_ok=True)
            rep = dict(report)
            rep.setdefault("ejecucion", {"estado": ejecucion})
            (self.e / "automated-tests/web/shell-principal/web-automation-report.yaml").write_text(
                yaml.safe_dump(rep, allow_unicode=True), encoding="utf8")

    def check(self):
        return self.res()["web-automation-subordinate-traceable"]

    def test_at_web_sin_reporte_falla(self):
        self.make_web(report=None)
        self.assertEqual(self.check(), "FAIL")

    def test_at_web_con_tc_automatizado_y_ejecucion_pasa(self):
        self.make_web(report={"casos": [{"id": "TC-001", "estado": "AUTOMATED"}]})
        self.assertEqual(self.check(), "PASS")

    def test_tc_parcial_tambien_pasa(self):
        self.make_web(report={"casos": [{"id": "TC-001", "estado": "PARTIAL"}]})
        self.assertEqual(self.check(), "PASS")

    def test_tc_no_automatizado_en_el_reporte_falla(self):
        self.make_web(report={"casos": [{"id": "TC-001", "estado": "NOT_AUTOMATED"}]})
        self.assertEqual(self.check(), "FAIL")

    def test_tc_ausente_del_reporte_falla(self):
        self.make_web(report={"casos": [{"id": "TC-999", "estado": "AUTOMATED"}]})
        self.assertEqual(self.check(), "FAIL")

    def test_ejecucion_no_realizada_falla(self):
        self.make_web(report={"casos": [{"id": "TC-001", "estado": "AUTOMATED"}]}, ejecucion="NOT_EXECUTED")
        self.assertEqual(self.check(), "FAIL")

    def test_at_no_web_no_exige_reporte(self):
        self.build()  # AT-001 sin superficie WEB
        self.assertEqual(self.check(), "PASS")


if __name__ == "__main__":
    unittest.main()
