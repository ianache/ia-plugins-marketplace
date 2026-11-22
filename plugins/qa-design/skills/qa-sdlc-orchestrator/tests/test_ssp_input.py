"""El plan puede iniciarse con un DSP o solo con un SSP.

- Con SSP: el DSP se toma del `dsp_id` del SSP y se localiza en la KB (por `sources` o por búsqueda única).
- Si el DSP no se localiza, no es único o no declara versión, el init se bloquea: no se inventa el DSP.
- El SSP solo selecciona alcance; el TC lo define el DSP, no el SSP.
"""
import argparse
import sys
import tempfile
import unittest
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SK / "scripts"))
import qa_orchestrator as qo  # noqa: E402
from qa_orchestrator import Reject, Runtime  # noqa: E402

ORCH = "orchestrator"


def dsp_doc(dsp_id, version="1.0"):
    return f'---\nid: "{dsp_id}"\nversion: "{version}"\n---\nDSP de prueba\n'


def ssp_doc(dsp_id, sources=None):
    extra = ""
    if sources:
        extra = "sources:\n" + "".join(f'  - id: "{s[0]}"\n    resource: "{s[1]}"\n' for s in sources)
    return f'---\ntype: SSP\nid: "SSP-003"\ndsp_id: "{dsp_id}"\nuser_stories: ["US-101"]\n{extra}---\nSprint de prueba\n'


class DspDesdeSsp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kb = Path(self.tmp.name) / "kb"
        (self.kb / "requirements/scope-packs").mkdir(parents=True)
        (self.kb / "management/sprints").mkdir(parents=True)

    def _ssp(self, sources=None, dsp_id="DSP-001"):
        p = self.kb / "management/sprints/SSP-003.md"
        p.write_text(ssp_doc(dsp_id, sources), encoding="utf8")
        return p

    def test_localiza_el_dsp_por_sources(self):
        dsp = self.kb / "requirements/scope-packs/DSP-001-pagos.md"
        dsp.write_text(dsp_doc("DSP-001", "2.0"), encoding="utf8")
        ssp = self._ssp(sources=[("dsp-001", "requirements/scope-packs/DSP-001-pagos.md")])
        r = qo.dsp_from_ssp(ssp, self.kb)
        self.assertEqual(r["id"], "DSP-001")
        self.assertEqual(r["version"], "2.0")
        self.assertEqual(Path(r["path"]).name, "DSP-001-pagos.md")

    def test_localiza_el_dsp_por_busqueda_unica(self):
        (self.kb / "requirements/scope-packs/DSP-001-pagos.md").write_text(dsp_doc("DSP-001"), encoding="utf8")
        ssp = self._ssp()
        self.assertEqual(qo.dsp_from_ssp(ssp, self.kb)["id"], "DSP-001")

    def test_dsp_ausente_bloquea(self):
        ssp = self._ssp()
        with self.assertRaises(Reject) as ctx:
            qo.dsp_from_ssp(ssp, self.kb)
        self.assertIn("no se localiza", str(ctx.exception))

    def test_dsp_ambiguo_bloquea(self):
        (self.kb / "requirements/scope-packs/DSP-001-a.md").write_text(dsp_doc("DSP-001"), encoding="utf8")
        (self.kb / "requirements/scope-packs/DSP-001-b.md").write_text(dsp_doc("DSP-001"), encoding="utf8")
        with self.assertRaises(Reject) as ctx:
            qo.dsp_from_ssp(self._ssp(), self.kb)
        self.assertIn("varios documentos", str(ctx.exception))

    def test_dsp_sin_version_bloquea(self):
        (self.kb / "requirements/scope-packs/DSP-001-x.md").write_text('---\nid: "DSP-001"\n---\nsin versión\n', encoding="utf8")
        with self.assertRaises(Reject) as ctx:
            qo.dsp_from_ssp(self._ssp(), self.kb)
        self.assertIn("no declara versión", str(ctx.exception))

    def test_ssp_sin_dsp_id_valido_bloquea(self):
        p = self.kb / "management/sprints/SSP-003.md"
        p.write_text('---\ntype: SSP\nid: "SSP-003"\ndsp_id: "PAGOS"\n---\n', encoding="utf8")
        with self.assertRaises(Reject):
            qo.dsp_from_ssp(p, self.kb)

    def test_dsp_explicito_incompleto_bloquea(self):
        args = argparse.Namespace(dsp_id="DSP-001", dsp_version=None, dsp_path=None, ssp_id=None, ssp_path=None, kb_root=".")
        with self.assertRaises(Reject):
            qo.dsp_de_args(args)

    def test_sin_dsp_ni_ssp_bloquea(self):
        args = argparse.Namespace(dsp_id=None, dsp_version=None, dsp_path=None, ssp_id=None, ssp_path=None, kb_root=".")
        with self.assertRaises(Reject):
            qo.dsp_de_args(args)

    def test_init_solo_con_ssp_planifica_el_dsp_completo_con_alcance_ssp(self):
        (self.kb / "requirements/scope-packs/DSP-001-pagos.md").write_text(dsp_doc("DSP-001", "3.1"), encoding="utf8")
        ssp = self._ssp()
        dsp = qo.dsp_from_ssp(ssp, self.kb)
        rt = Runtime(Path(self.tmp.name) / "rt")
        rt.init("QAPLAN-SSP", dsp, 633, "obj", ["API"], scope={"microservices": [{"id": "pos"}]},
                ssp_id="SSP-003", ssp_path=str(ssp))
        plan = rt.plan
        self.assertEqual(plan["dsp_ref"]["id"], "DSP-001")
        self.assertEqual(plan["dsp_ref"]["version"], "3.1")
        self.assertEqual(plan["ssp_ref"], "SSP-003")
        self.assertTrue(plan["deliverable_root"].endswith("SSP-003/"))


class SspSeleccionaTc(unittest.TestCase):
    """El SSP selecciona TC por historia compartida; el TC lo define el DSP y no se duplica."""

    TCS = [
        {"id": "TC-001", "user_stories": ["US-101"]},
        {"id": "TC-002", "user_stories": ["US-101", "US-102"]},
        {"id": "TC-003", "user_stories": ["US-200"]},
    ]

    def test_selecciona_los_tc_que_comparten_historia(self):
        sel, sin_tc = qo.ssp_tc_selection(self.TCS, ["US-101"])
        self.assertEqual(sel, ["TC-001", "TC-002"])
        self.assertEqual(sin_tc, [])

    def test_historia_del_ssp_sin_tc_queda_reportada(self):
        sel, sin_tc = qo.ssp_tc_selection(self.TCS, ["US-101", "US-999"])
        self.assertEqual(sin_tc, ["US-999"])

    def test_ssp_sin_historias_coincidentes_no_selecciona_nada(self):
        sel, _ = qo.ssp_tc_selection(self.TCS, ["US-500"])
        self.assertEqual(sel, [])

    def test_ssp_sin_user_stories_bloquea(self):
        with self.assertRaises(Reject):
            qo.ssp_user_stories({"dsp_id": "DSP-001"})

    def test_ssp_con_id_de_historia_invalido_bloquea(self):
        with self.assertRaises(Reject):
            qo.ssp_user_stories({"user_stories": ["historia-1"]})

    def test_ssp_con_historias_validas_devuelve_la_lista(self):
        self.assertEqual(qo.ssp_user_stories({"user_stories": ["US-101", "US-102"]}), ["US-101", "US-102"])


if __name__ == "__main__":
    unittest.main()
