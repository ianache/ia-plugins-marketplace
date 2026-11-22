"""Check api-automation-subordinate-traceable: los AT de superficie API se producen con postman-automation."""
import unittest

import yaml

from test_check_test_engineering import Pack, md


class ApiSubordinate(Pack):
    def make_api(self, report=None, newman="EXECUTED"):
        self.build()
        (self.e / "automated-tests/AT-001.md").write_text(
            md({"id": "AT-001", "testcase_ref": "TC-001", "tda_refs": ["TDA-001"], "surface": "API"}), encoding="utf8")
        if report is not None:
            (self.e / "automated-tests" / "postman" / "position-enricher").mkdir(parents=True, exist_ok=True)
            rep = dict(report)
            rep.setdefault("newman", {"estado": newman})
            (self.e / "automated-tests/postman/position-enricher/postman-automation-report.yaml").write_text(
                yaml.safe_dump(rep, allow_unicode=True), encoding="utf8")

    def check(self):
        return self.res()["api-automation-subordinate-traceable"]

    def test_at_api_sin_reporte_falla(self):
        self.make_api(report=None)
        self.assertEqual(self.check(), "FAIL")

    def test_at_api_con_tc_automatizado_y_newman_ejecutado_pasa(self):
        self.make_api(report={"casos": [{"id": "TC-001", "estado": "AUTOMATED"}]})
        self.assertEqual(self.check(), "PASS")

    def test_tc_parcial_tambien_pasa(self):
        self.make_api(report={"casos": [{"id": "TC-001", "estado": "PARTIAL"}]})
        self.assertEqual(self.check(), "PASS")

    def test_tc_no_automatizado_en_el_reporte_falla(self):
        self.make_api(report={"casos": [{"id": "TC-001", "estado": "NOT_AUTOMATED"}]})
        self.assertEqual(self.check(), "FAIL")

    def test_tc_ausente_del_reporte_falla(self):
        self.make_api(report={"casos": [{"id": "TC-999", "estado": "AUTOMATED"}]})
        self.assertEqual(self.check(), "FAIL")

    def test_newman_no_ejecutado_falla(self):
        self.make_api(report={"casos": [{"id": "TC-001", "estado": "AUTOMATED"}]}, newman="NOT_EXECUTED")
        self.assertEqual(self.check(), "FAIL")

    def test_at_no_api_no_exige_reporte(self):
        self.build()  # AT-001 sin superficie API
        self.assertEqual(self.check(), "PASS")


if __name__ == "__main__":
    unittest.main()
