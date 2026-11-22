"""Check ssp-scope-respected: con SSP, AT y EXEC solo referencian TC de la selección del SSP."""
import unittest

import yaml

from test_check_test_engineering import Pack, md
import check_test_engineering as c


class SspScopeRespected(Pack):
    def run_checks(self, ssp_tc_ids):
        self.build()
        res = c.checks(self.e, self.d, "engineering", ssp_tc_ids)
        return {x["id"]: x["result"] for x in res}["ssp-scope-respected"]

    def test_sin_ssp_no_restringe(self):
        self.assertEqual(self.run_checks("*"), "PASS")

    def test_tc_dentro_de_la_seleccion_pasa(self):
        self.assertEqual(self.run_checks("TC-001,TC-002"), "PASS")

    def test_tc_fuera_de_la_seleccion_falla(self):
        self.assertEqual(self.run_checks("TC-900"), "FAIL")

    def test_seleccion_vacia_falla_si_hay_at(self):
        self.assertEqual(self.run_checks("-"), "FAIL")

    def test_ssp_scope_check_devuelve_detalle(self):
        self.build()
        ok, detail = c.ssp_scope_check(self.e, "TC-900")
        self.assertFalse(ok)
        self.assertTrue(any("TC-001" in d for d in detail))


if __name__ == "__main__":
    unittest.main()
