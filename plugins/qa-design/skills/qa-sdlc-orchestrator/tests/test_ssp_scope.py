"""El alcance del plan incluye el SSP y los microservicios API identificados por api_id.

- SSP: se fija en init, G0 lo valida y limita los T05.
- Microservicios: G0 exige, si hay superficie API, al menos un api_id declarado en scope.microservices.
- Los TC NO se declaran en init: tras T03 cada TC API lleva su api_id (frontmatter) y se crean los subordinados
  SUB-<api_id>-FUN (postman-automation) y SUB-<api_id>-CARGA (loadtest-automation, test_type rendimiento).
- Un TC API sin api_id, o con api_id no declarado en G0, bloquea la asignación.
"""
import sys
import tempfile
import unittest
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SK / "scripts"))
import qa_orchestrator as qo  # noqa: E402
from qa_orchestrator import Reject, Runtime  # noqa: E402

ORCH = "orchestrator"
SCOPE = {"microservices": [{"id": "position-enricher"}, {"id": "tenancy"}]}


def sprint_doc(dsp_id):
    return f'---\nokf_version: "0.2"\nid: "SSP-003"\ndsp_id: "{dsp_id}"\nuser_stories: ["US-101"]\n---\nSprint de prueba\n'


class SspScope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.dsp = t / "DSP-001.md"
        self.dsp.write_text("dsp v1", encoding="utf8")
        self.sprint = t / "SSP-003.md"
        self.sprint.write_text(sprint_doc("DSP-001"), encoding="utf8")
        self.rt = Runtime(t / "rt")

    def init(self, surfaces=("API", "WEB"), ssp_id="SSP-003", ssp_path=None, scope=SCOPE):
        dsp = {"id": "DSP-001", "version": "1.0", "path": str(self.dsp)}
        path = str(self.sprint) if ssp_path is None else ssp_path
        self.rt.init("QAPLAN-S", dsp, 633, "obj", list(surfaces), scope=scope, ssp_id=ssp_id, ssp_path=path)

    def g0(self):
        self.rt.load()
        out = self.rt.g0(ORCH)
        return out, {c["id"]: c["result"] for c in out["checks"]}

    def tasks(self):
        return {t["id"]: t for t in self.rt.plan["tasks"]}

    # --- SSP ---
    def test_ssp_sin_documento_se_rechaza_antes_de_escribir(self):
        with self.assertRaises(Reject):
            self.rt.init("QAPLAN-S", {"id": "DSP-001", "version": "1.0", "path": str(self.dsp)}, 633, "obj", ["API"],
                         scope=SCOPE, ssp_id="SSP-003")
        self.assertFalse((self.rt.root / "plan.yaml").exists())

    def test_ssp_con_documento_inexistente_se_rechaza(self):
        with self.assertRaises(Reject):
            self.init(ssp_path=str(Path(self.tmp.name) / "no-existe.md"))

    def test_plan_guarda_identidad_del_ssp(self):
        self.init()
        src = self.rt.plan["ssp_source"]
        self.assertEqual(src["id"], "SSP-003")
        self.assertEqual(src["declared_dsp_id"], "DSP-001")
        self.assertTrue(src["digest"])

    def test_ssp_del_mismo_dsp_pasa_g0(self):
        self.init()
        out, checks = self.g0()
        self.assertEqual(checks["ssp-identified"], "PASS")
        self.assertEqual(checks["ssp-belongs-to-dsp"], "PASS")
        self.assertEqual(out["planning_gate"], "PASS")

    def test_ssp_de_otro_dsp_bloquea_g0(self):
        self.sprint.write_text(sprint_doc("DSP-002"), encoding="utf8")
        self.init()
        out, checks = self.g0()
        self.assertEqual(checks["ssp-belongs-to-dsp"], "FAIL")
        self.assertNotEqual(out["planning_gate"], "PASS")

    def test_ssp_modificado_despues_de_init_bloquea_g0(self):
        self.init()
        self.sprint.write_text(sprint_doc("DSP-001") + "cambio posterior\n", encoding="utf8")
        out, checks = self.g0()
        self.assertEqual(checks["ssp-identified"], "FAIL")
        self.assertNotEqual(out["planning_gate"], "PASS")

    def test_sin_ssp_g0_declara_alcance_dsp_completo(self):
        self.rt.init("QAPLAN-S", {"id": "DSP-001", "version": "1.0", "path": str(self.dsp)}, 633, "obj", ["API"],
                     scope=SCOPE)
        out, checks = self.g0()
        self.assertEqual(checks["ssp-scope"], "PASS")
        self.assertNotIn("ssp-identified", checks)
        self.assertIsNone(self.rt.plan["ssp_source"])
        self.assertIsNone(self.tasks()["T05-API"]["scope_ssp"])

    # --- Microservicios (api_id) y asignación de TC tras T03 ---
    def write_tc(self, folder, tc_id, api_id=None, test_type="positivo", surface="API"):
        lineas = ["---", f"id: {tc_id}", f"surface: {surface}", f"test_type: {test_type}"]
        if api_id is not None:
            lineas.append(f"api_id: {api_id}")
        lineas += ["---", "cuerpo"]
        (folder / f"{tc_id}.md").write_text("\n".join(lineas) + "\n", encoding="utf8")

    def test_init_no_acepta_tc_en_scope(self):
        with self.assertRaises(Reject):
            self.init(scope={"microservices": [{"id": "a", "tc_funcional": ["TC-1"]}]})
        self.assertFalse((self.rt.root / "plan.yaml").exists())

    def test_init_declara_microservicios_sin_subordinados(self):
        self.init()
        self.assertEqual(self.rt.plan["microservices"], ["position-enricher", "tenancy"])
        self.assertEqual(self.rt.plan["subordinates"], [])
        self.assertEqual(self.tasks()["T05-API"]["subordinates"], [])

    def test_asignacion_por_api_id_crea_subordinados_por_tipo(self):
        self.init()
        pack = Path(self.tmp.name) / "pack" / "TC"
        pack.mkdir(parents=True)
        self.write_tc(pack, "TC-PE-01", "position-enricher")
        self.write_tc(pack, "TC-PE-02", "position-enricher")
        self.write_tc(pack, "TC-PE-09", "position-enricher", test_type="rendimiento")
        self.write_tc(pack, "TC-T-01", "tenancy")
        check, tcs = self.rt._api_assignment({"pack": str(pack.parent)})
        self.assertEqual(check["result"], "PASS")
        self.rt._assign_subordinates(tcs)
        sub = {s["id"]: s for s in self.rt.plan["subordinates"]}
        self.assertEqual(sorted(sub), ["SUB-position-enricher-CARGA", "SUB-position-enricher-FUN", "SUB-tenancy-FUN"])
        self.assertEqual(sub["SUB-position-enricher-FUN"]["skill"], "postman-automation")
        self.assertEqual(sub["SUB-position-enricher-FUN"]["tc_refs"], ["TC-PE-01", "TC-PE-02"])
        self.assertEqual(sub["SUB-position-enricher-CARGA"]["skill"], "loadtest-automation")
        self.assertEqual(sub["SUB-position-enricher-CARGA"]["tc_refs"], ["TC-PE-09"])
        self.assertEqual(sub["SUB-position-enricher-CARGA"]["report"],
                         "automated-tests/k6/position-enricher/loadtest-automation-report.yaml")
        self.assertEqual(sub["SUB-tenancy-FUN"]["scope_ssp"], "SSP-003")
        self.assertEqual(sorted(self.tasks()["T05-API"]["subordinates"]), sorted(sub))
        self.assertEqual(self.tasks()["T05-WEB"].get("subordinates", []), [])

    def test_tc_api_sin_api_id_falla_la_asignacion(self):
        self.init()
        pack = Path(self.tmp.name) / "pack" / "TC"
        pack.mkdir(parents=True)
        self.write_tc(pack, "TC-PE-01", None)
        check, tcs = self.rt._api_assignment({"pack": str(pack.parent)})
        self.assertEqual(check["result"], "FAIL")
        self.assertIsNone(tcs)
        self.assertTrue(any("sin api_id" in d for d in check["detail"]))

    def test_api_id_no_declarado_en_g0_falla_la_asignacion(self):
        self.init()
        pack = Path(self.tmp.name) / "pack" / "TC"
        pack.mkdir(parents=True)
        self.write_tc(pack, "TC-X-01", "no-declarado")
        check, _ = self.rt._api_assignment({"pack": str(pack.parent)})
        self.assertEqual(check["result"], "FAIL")
        self.assertTrue(any("no declarado en G0" in d for d in check["detail"]))

    def test_api_sin_tc_en_el_pack_falla(self):
        self.init()
        pack = Path(self.tmp.name) / "pack" / "TC"
        pack.mkdir(parents=True)
        check, _ = self.rt._api_assignment({"pack": str(pack.parent)})
        self.assertEqual(check["result"], "FAIL")

    def test_sin_pack_falla_la_asignacion(self):
        self.init()
        check, tcs = self.rt._api_assignment({})
        self.assertEqual(check["result"], "FAIL")
        self.assertIsNone(tcs)

    def test_microservicio_duplicado_se_rechaza(self):
        with self.assertRaises(Reject):
            self.init(scope={"microservices": [{"id": "a"}, {"id": "a"}]})

    def test_microservicio_con_id_invalido_se_rechaza(self):
        with self.assertRaises(Reject):
            self.init(scope={"microservices": [{"id": "../fuera"}]})

    def test_api_sin_microservicios_bloquea_g0(self):
        self.init(scope={})
        out, checks = self.g0()
        self.assertEqual(checks["subordinates-declared"], "FAIL")
        self.assertNotEqual(out["planning_gate"], "PASS")

    def test_sin_api_no_exige_microservicios(self):
        self.init(surfaces=("WEB",), scope={})
        out, checks = self.g0()
        self.assertEqual(checks["subordinates-declared"], "PASS")


if __name__ == "__main__":
    unittest.main()
