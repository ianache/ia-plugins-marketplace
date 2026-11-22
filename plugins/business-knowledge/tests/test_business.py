import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
import validate_okf  # noqa: E402
import validate_pathmap as pm  # noqa: E402


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, PLUGIN / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wf = load("wf", "scripts/workflow.py")
glossary = load("glossary", "skills/biz-glossary-curator/scripts/glossary.py")
check_pack = load("check_pack", "skills/biz-pack-validator-publisher/scripts/check_pack.py")

DOC = """---
type: {type}
id: "{id}"
title: "Documento {id}"
description: "Documento de prueba"
version: "0.1.0"
status: draft
owner: "team:negocio"
classification: internal
tags: [business]
product: "CL2"
pack: business-knowledge
skill: biz-test
generated:
  by: "biz-test/1.0.0"
  at: "2026-10-24T10:00:00-05:00"
sources:
  - id: s1
    resource: docs/fuente.md
related: {related}
---
# Documento {id}

{body}
"""


def write_doc(ws, rel, type_, id_, related="[]", body="Contenido."):
    p = pathlib.Path(ws) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(DOC.format(type=type_, id=id_, related=related, body=body), encoding="utf-8")
    return p


class A:
    def __init__(self, **k):
        self.__dict__.update(k)


class OkfTests(unittest.TestCase):
    def test_new_types_are_approved_in_v130_stable(self):
        with tempfile.TemporaryDirectory() as d:
            for t in ("TRM", "BCP", "BO", "STK", "BCAP", "IMD"):
                p = write_doc(d, f"x/{t}-001.md", t, f"{t}-001")
                self.assertEqual([], validate_okf.validate(p), t)
                self.assertFalse(any("no aprobado" in i for i in validate_okf.validate(p, True)), t)
            p = write_doc(d, "x/ZZZ-001.md", "ZZZ", "ZZZ-001")
            self.assertTrue(any("no aprobado" in i for i in validate_okf.validate(p, True)))

    def test_br_is_approved_and_needs_pack_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_doc(d, "business/rules/BR-001.md", "BR", "BR-001")
            self.assertEqual([], validate_okf.validate(p))
            q = pathlib.Path(d) / "business/rules/BR-002.md"
            q.write_text(p.read_text(encoding="utf-8").replace("product:", "producto:"), encoding="utf-8")
            self.assertTrue(any("product requerido" in i for i in validate_okf.validate(q)))


class PathmapTests(unittest.TestCase):
    def test_every_type_routes_to_business(self):
        self.assertEqual(set(pm.MAP), {"BCP", "BO", "STK", "BCAP", "TRM", "BR", "IMD", "BSN"})
        self.assertTrue(all(v.startswith("business/") for v in pm.MAP.values()))
        with tempfile.TemporaryDirectory() as d:
            for t, rel in pm.MAP.items():
                p = write_doc(d, f"{rel}/{t}-001-x.md", t, f"{t}-001")
                self.assertTrue(pm.validate(d, t, p)[0], t)

    def test_wrong_dir_unmapped_and_id_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_doc(d, "business/rules/TRM-001-x.md", "TRM", "TRM-001")
            self.assertFalse(pm.validate(d, "TRM", p)[0])
            q = write_doc(d, "business/terms/otro.md", "TRM", "TRM-002")
            self.assertFalse(pm.validate(d, "TRM", q)[0])
            r = write_doc(d, "business/x/XYZ-001.md", "XYZ", "XYZ-001")
            self.assertFalse(pm.validate(d, "XYZ", r)[0])

    def test_catalog_is_one_to_one_with_documents(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / "business/rules"
            r.mkdir(parents=True)
            (r / "BR-001.md").write_text("x")
            (r / "CTLG-BR.md").write_text("| [BR-001](BR-001.md) |")
            self.assertTrue(pm.check_catalog(d, "BR")[0])
            (r / "BR-002.md").write_text("x")
            ok, msg = pm.check_catalog(d, "BR")
            self.assertFalse(ok)
            self.assertIn("BR-002.md", msg)  # documento fuera del catálogo
            (r / "CTLG-BR.md").write_text("| [BR-001](BR-001.md) | [BR-001](BR-001.md) | [BR-009](BR-009.md) |")
            ok, msg = pm.check_catalog(d, "BR")
            self.assertFalse(ok)
            self.assertIn("duplicadas", msg)
            self.assertIn("BR-009.md", msg)  # fila sin documento
            (r / "index.md").write_text("x")
            self.assertIn("obsoleto", pm.check_catalog(d, "BR")[1])

    def test_ctlg_routes_by_id_to_its_catalog_directory(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_doc(d, "business/rules/CTLG-BR.md", "CTLG", "CTLG-BR")
            self.assertTrue(pm.validate(d, "CTLG", p)[0])
            q = write_doc(d, "business/terms/CTLG-BR.md", "CTLG", "CTLG-BR")
            self.assertFalse(pm.validate(d, "CTLG", q)[0])
            r = write_doc(d, "business/rules/CTLG-XX.md", "CTLG", "CTLG-XX")
            self.assertFalse(pm.validate(d, "CTLG", r)[0])

    def test_narrative_catalog_routes_by_indexes_field(self):
        # Catálogo narrativo genérico: CTLG con `indexes: BR` vive en el directorio de las reglas.
        fm = '---\ntype: CTLG\nid: "CTLG-SIGO-X-001"\nindexes: BR\n---\n# x\n'
        with tempfile.TemporaryDirectory() as d:
            ok_path = pathlib.Path(d) / "business/rules/CTLG-SIGO-X-001-ejemplo.md"
            ok_path.parent.mkdir(parents=True)
            ok_path.write_text(fm, encoding="utf-8")
            self.assertTrue(pm.validate(d, "CTLG", ok_path)[0])
            wrong = pathlib.Path(d) / "business/terms/CTLG-SIGO-X-001-ejemplo.md"
            wrong.parent.mkdir(parents=True)
            wrong.write_text(fm, encoding="utf-8")
            self.assertFalse(pm.validate(d, "CTLG", wrong)[0])
            sin = pathlib.Path(d) / "business/rules/CTLG-SIN-001.md"
            sin.write_text('---\ntype: CTLG\nid: "CTLG-SIN-001"\n---\n# x\n', encoding="utf-8")
            self.assertFalse(pm.validate(d, "CTLG", sin)[0])

    def test_area_index_lives_in_business_root(self):
        # Índice de área (indexes: AREA) vive en la raíz de business/, no en un directorio de tipo.
        fm = '---\ntype: CTLG\nid: "CTLG-BUS-INDEX"\nindexes: AREA\n---\n# x\n'
        with tempfile.TemporaryDirectory() as d:
            ok_path = pathlib.Path(d) / "business" / "CTLG-BUS-INDEX.md"
            ok_path.parent.mkdir(parents=True)
            ok_path.write_text(fm, encoding="utf-8")
            self.assertTrue(pm.validate(d, "CTLG", ok_path)[0])
            wrong = pathlib.Path(d) / "business" / "rules" / "CTLG-BUS-INDEX.md"
            wrong.parent.mkdir(parents=True)
            wrong.write_text(fm, encoding="utf-8")
            self.assertFalse(pm.validate(d, "CTLG", wrong)[0])

    def test_pathmap_declares_catalogs_and_no_index_files(self):
        pathmap = json.loads((PLUGIN / "assets/pathmap.json").read_text(encoding="utf-8"))
        self.assertEqual({"CTLG-TRM": "TRM", "CTLG-BR": "BR"}, {k: v["indexes"] for k, v in pathmap["catalogs"].items()})
        self.assertEqual("2.0.0", pathmap["pathmap_version"])
        self.assertEqual([], [p for p in PLUGIN.rglob("index.md") if "pytest_cache" not in p.parts])


class WorkflowTests(unittest.TestCase):
    def run_dir(self, scenario="greenfield", just=None):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        r = pathlib.Path(d.name) / ".comsatel/business-knowledge/runs/RUN-1"
        wf.init(A(run=str(r), scenario=scenario, workspace=d.name, justification=just))
        (pathlib.Path(d.name) / "evidence.md").write_text("ok", encoding="utf-8")
        return r

    def test_evidencia_debe_ser_archivo_existente_dentro_del_workspace(self):
        # D-21: texto libre, archivos inexistentes o fuera del workspace se rechazan; se guarda la ruta relativa
        r = self.run_dir()
        for malo in ("no-existe.md", "x", "texto libre", "MR-12"):
            with self.assertRaises(ValueError, msg=malo):
                wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence=malo))
        with tempfile.TemporaryDirectory() as fuera:
            f = pathlib.Path(fuera) / "ev.md"
            f.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence=str(f)))
        wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence="evidence.md"))
        self.assertEqual(json.loads((r / "gate-register.json").read_text(encoding="utf-8"))["gates"][0]["evidence"], ["evidence.md"])
        for to in ("READY", "IN_PROGRESS"):
            wf.transition(A(run=str(r), task="T01", to=to, actor="agent", reason="r", evidence=None))
        with self.assertRaises(ValueError):
            wf.transition(A(run=str(r), task="T01", to="NEEDS_REVIEW", actor="agent", reason="r", evidence="no-existe.md"))

    def test_omit_g5_exige_justificacion_y_ajusta_el_encadenamiento(self):
        # D-24a: --omit G5 + --justification omite T05/G5; T06 pasa a depender de G4
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / ".comsatel/business-knowledge/runs/R"
            with self.assertRaises(ValueError):
                wf.init(A(run=str(r), scenario="evolution", workspace=d, justification=None, omit=["G5"]))
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / ".comsatel/business-knowledge/runs/R"
            wf.init(A(run=str(r), scenario="evolution", workspace=d, justification="solo cambia una regla y un término", omit=["G5"]))
            p = wf.check(r)[0]
            self.assertEqual(p["omitted_gates"], ["G5"])
            self.assertNotIn("G5", [t["gate"] for t in p["tasks"]])
            self.assertNotIn("biz-scenario-modeler", [t["skill"] for t in p["tasks"]])
            self.assertEqual(next(t for t in p["tasks"] if t["gate"] == "G6")["depends_on"], ["T04"])
            self.assertEqual(next(t for t in p["tasks"] if t["gate"] == "G6")["entry_gate"], "G4")
            g = json.loads((r / "gate-register.json").read_text(encoding="utf-8"))["gates"]
            self.assertEqual(next(x for x in g if x["id"] == "G5")["status"], "OMITTED")
        self.assertEqual(wf.OMITTABLE, ["G5"])

    def test_no_gate_cycle_in_any_scenario(self):
        for sc in wf.SCENARIOS:
            r = self.run_dir(sc, "actualización de línea base" if sc == "incremental" else None)
            for t in wf.check(r)[0]["tasks"]:
                self.assertLess(wf.GATES.index(t["entry_gate"]), wf.GATES.index(t["gate"]))

    def test_task_chain_matches_skills(self):
        p = wf.check(self.run_dir())[0]
        self.assertEqual([t["skill"] for t in p["tasks"]], [
            "biz-context-objectives-analyst", "biz-stakeholder-capability-mapper", "biz-glossary-curator",
            "biz-rules-modeler", "biz-information-model-designer", "biz-scenario-modeler", "biz-pack-validator-publisher"])
        self.assertEqual(p["tasks"][2]["output_paths"], {"TRM": "business/terms"})
        t = {x["id"]: x for x in p["tasks"]}
        self.assertEqual(t["T05"]["depends_on"], ["T04"])
        self.assertEqual(t["T07"]["depends_on"], ["T04"])
        self.assertEqual(t["T07"]["gate"], "G5")
        self.assertEqual(sorted(t["T06"]["depends_on"]), ["T05", "T07"])

    def test_gates_in_order_and_human_actor(self):
        r = self.run_dir()
        with self.assertRaises(ValueError):
            wf.approve(A(run=str(r), gate="G0", actor="agent", evidence="x"))
        wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence="evidence.md"))
        with self.assertRaises(ValueError):
            wf.approve(A(run=str(r), gate="G2", actor="human:ana", evidence="x"))
        for to in ("READY", "IN_PROGRESS", "NEEDS_REVIEW", "DONE"):
            wf.transition(A(run=str(r), task="T01", to=to, actor="agent", reason="r", evidence="evidence.md"))
        wf.approve(A(run=str(r), gate="G1", actor="human:ana", evidence="evidence.md"))
        with self.assertRaises(ValueError):
            wf.transition(A(run=str(r), task="T03", to="READY", actor="agent", reason="r", evidence=None))

    def test_incremental_needs_justification_and_skips_g1_g2(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / ".comsatel/business-knowledge/runs/R"
            with self.assertRaises(ValueError):
                wf.init(A(run=str(r), scenario="incremental", workspace=d, justification=None))
        p = wf.check(self.run_dir("incremental", "actualiza glosario y reglas"))[0]
        self.assertEqual([t["gate"] for t in p["tasks"]], ["G3", "G4", "G5", "G5", "G6"])
        self.assertEqual(p["tasks"][0]["entry_gate"], "G0")

    def test_cycle_detected(self):
        r = self.run_dir()
        p = json.loads((r / "execution-plan.json").read_text())
        p["tasks"][1]["entry_gate"] = "G2"
        (r / "execution-plan.json").write_text(json.dumps(p))
        with self.assertRaises(ValueError):
            wf.check(r)


class GlossaryTests(unittest.TestCase):
    def make_term(self, folder, name, definition="Empresa con contrato vigente.", level="N2", classification="fact"):
        glossary.cmd_new(str(folder), name, "CL2")
        f = sorted(pathlib.Path(folder).glob("TRM-*.md"))[-1]
        s = f.read_text(encoding="utf-8")
        for a, b in (("<team:responsable>", "team:negocio"), ("<ISO-8601-CON-ZONA>", "2026-10-24T10:00:00-05:00"),
                     ("concepto | término | sigla | abreviatura", "concepto"),
                     ("<solo siglas y abreviaturas: una sola expansión, sin \";\", con su fuente entre corchetes; o \"Desconocida\">", "Desconocida"),
                     ("<Sinónimo [fuente:Lnn]; Otro sinónimo [fuente:Lnn]> | —", "—"),
                     ("<significado en el negocio, en una o dos frases>", definition),
                     ("<solo si el significado N1 externo difiere del de negocio>", "—"),
                     ("<producto, dominio o \"general\">", "CL2"),
                     ("[N2] <título> — <ruta/desde/la/raiz.md:Lnn o URL> — consultada <AAAA-MM-DD>", f"[{level}] Contrato — docs/contrato.md:L10 — consultada 2026-10-24"),
                     ("fact | decision | assumption | inference | gap", classification), ("high | medium | low", "high"),
                     ("<rol dueño del dominio según las fuentes, o \"Por definir\">", "Por definir"),
                     ("[<Término>](TRM-001-<slug>.md) | —", "—"), ("<ambigüedades, contradicciones o reemplazo si está deprecated> | —", "—")):
            s = s.replace(a, b)
        f.write_text(s, encoding="utf-8")
        return f

    def test_lifecycle_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business/terms"
            self.make_term(folder, "Cliente corporativo")
            self.assertEqual(1, glossary.cmd_check(str(folder)))  # sin build: description/sources/index desfasados
            glossary.cmd_build(str(folder))
            self.assertEqual(0, glossary.cmd_check(str(folder)))
            before = (folder / "CTLG-TRM.md").read_text(encoding="utf-8")
            glossary.cmd_build(str(folder))
            self.assertEqual(before, (folder / "CTLG-TRM.md").read_text(encoding="utf-8"))
            term = sorted(folder.glob("TRM-*.md"))[0]
            self.assertEqual([], [i for i in validate_okf.validate(term) if not i.startswith("type propuesto")])
            self.assertTrue(pm.validate(d, "TRM", term)[0])
            self.assertTrue(pm.check_catalog(d, "TRM")[0])

    def test_catalog_is_ctlg_without_definitions_and_no_index(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business/terms"
            self.make_term(folder, "Cliente corporativo", definition="Definición única que no debe repetirse.")
            glossary.cmd_build(str(folder))
            (folder / "index.md").write_text("obsoleto", encoding="utf-8")
            self.assertEqual(1, glossary.cmd_check(str(folder)))  # index.md obsoleto presente
            glossary.cmd_build(str(folder))
            self.assertFalse((folder / "index.md").exists())
            text = (folder / "CTLG-TRM.md").read_text(encoding="utf-8")
            self.assertIn("type: CTLG", text)
            self.assertIn("id: CTLG-TRM", text)
            self.assertNotIn("Definición única", text)
            self.assertEqual([], [i for i in validate_okf.validate(folder / "CTLG-TRM.md") if "type propuesto" not in i])
            self.assertEqual(0, glossary.cmd_check(str(folder)))

    def test_ids_increment_and_template_text_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business/terms"
            glossary.cmd_new(str(folder), "Primero", "CL2")
            glossary.cmd_new(str(folder), "Segundo", "CL2")
            self.assertEqual(["TRM-001-primero.md", "TRM-002-segundo.md"], sorted(p.name for p in folder.glob("TRM-*.md")))
            glossary.cmd_build(str(folder))
            self.assertEqual(1, glossary.cmd_check(str(folder)))  # placeholders de plantilla sin completar

    def test_truncated_definition_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business/terms"
            self.make_term(folder, "Definición cortada", definition="Documento que describe los servicios y incluye la…")
            glossary.cmd_build(str(folder))
            self.assertEqual(1, glossary.cmd_check(str(folder)))
            term = glossary.Term(str(sorted(folder.glob("TRM-*.md"))[0]))
            self.assertIn("truncada", " ".join(glossary.check_term(term, {term.file})))

    def test_gap_required_without_n1_n2(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business/terms"
            self.make_term(folder, "Término débil", level="N3", classification="fact")
            glossary.cmd_build(str(folder))
            self.assertEqual(1, glossary.cmd_check(str(folder)))



    def test_glossary_rejects_non_term_documents(self):
        # Un glosario con otro type (p. ej. "Business Glossary") no se admite en business/terms/.
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d) / "business" / "terms"
            folder.mkdir(parents=True)
            (folder / "GLS-001-glosario.md").write_text('---\ntype: Business Glossary\nid: GLS-001\n---\n# x\n', encoding="utf-8")
            self.assertEqual(1, glossary.cmd_check(str(folder)))

class CheckPackTests(unittest.TestCase):
    def test_clean_pack_and_findings(self):
        with tempfile.TemporaryDirectory() as d:
            write_doc(d, "business/objectives/BO-001-x.md", "BO", "BO-001")
            write_doc(d, "business/capabilities/BCAP-001-x.md", "BCAP", "BCAP-001", related="[BO-001]")
            write_doc(d, "business/rules/BR-001.md", "BR", "BR-001", related="[BCAP-001]", body="Usa [término](../terms/TRM-001-x.md).")
            write_doc(d, "business/terms/TRM-001-x.md", "TRM", "TRM-001")
            write_doc(d, "business/information-model/IMD-001-x.md", "IMD", "IMD-001", related="[BR-001]", body="Concepto TRM-001. Regla BR-001.")
            write_doc(d, "business/rules/CTLG-BR.md", "CTLG", "CTLG-BR", body="| [BR-001](BR-001.md) |")
            write_doc(d, "business/terms/CTLG-TRM.md", "CTLG", "CTLG-TRM", body="| [x](TRM-001-x.md) |")
            res = check_pack.check(d)
            self.assertEqual([], res["errors"], res)
            self.assertTrue(all("type propuesto" in w or "hueco" in w for w in res["warnings"]))
            # rompe: related inexistente, enlace roto, regla fuera del catálogo
            write_doc(d, "business/rules/BR-002.md", "BR", "BR-002", related="[BCAP-999]", body="[x](../terms/NOPE.md)")
            res = check_pack.check(d)
            joined = " ".join(res["errors"])
            self.assertIn("BCAP-999", joined)
            self.assertIn("enlace roto", joined)
            self.assertIn("fuera del catálogo", joined)
            # un index.md residual también rompe el pack
            (pathlib.Path(d) / "business/terms/index.md").write_text("| [x](TRM-001-x.md) |")
            self.assertIn("index.md obsoleto", " ".join(check_pack.check(d)["errors"]))

    def test_bsn_must_cite_existing_rules(self):
        with tempfile.TemporaryDirectory() as d:
            write_doc(d, "business/rules/BR-001.md", "BR", "BR-001")
            write_doc(d, "business/rules/CTLG-BR.md", "CTLG", "CTLG-BR", body="| [BR-001](BR-001.md) |")
            write_doc(d, "business/scenarios/BSN-001-ok.md", "BSN", "BSN-001", body="Paso 1 usa BR-001.")
            res = check_pack.check(d)
            self.assertEqual([], [e for e in res["errors"] if "BSN" in e], res)
            write_doc(d, "business/scenarios/BSN-002-mal.md", "BSN", "BSN-002", body="Paso 1 usa BR-777.")
            joined = " ".join(check_pack.check(d)["errors"])
            self.assertIn("BSN-002: cita una regla inexistente en el pack: BR-777", joined)
            write_doc(d, "business/scenarios/BSN-003-sin.md", "BSN", "BSN-003", body="Sin reglas.")
            self.assertTrue(any("BSN-003" in w and "no cita" in w for w in check_pack.check(d)["warnings"]))


class RulesTests(unittest.TestCase):
    RULE = {
        "title": "Descuento máximo por cliente",
        "description": "Ningún pedido supera el 15 % de descuento sin aprobación.",
        "statement": "El descuento total de un pedido no puede superar el 15 % del precio de lista.",
        "owner": "team:comercial",
        "conditions": "Aplica a pedidos B2B; no a muestras gratuitas.",
        "terms": ["TRM-001"],
        "sources": [{"id": "src-001", "resource": "docs/politica-descuentos.md", "title": "Política de descuentos"}],
    }

    def setup_ws(self, d):
        terms = pathlib.Path(d) / "business/terms"
        terms.mkdir(parents=True)
        (terms / "TRM-001-pedido.md").write_text("x", encoding="utf-8")
        rules = pathlib.Path(d) / "business/rules"
        return rules

    def write_json(self, d, items):
        p = pathlib.Path(d) / "reglas.json"
        p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        return str(p)

    def test_one_file_per_rule_and_one_to_one_catalog(self):
        rules_mod = load("rules", "skills/biz-rules-modeler/scripts/rules.py")
        with tempfile.TemporaryDirectory() as d:
            folder = str(self.setup_ws(d))
            second = dict(self.RULE, title="Pedido mínimo", terms=[], sources=[], open_questions=["¿Mínimo por país?"])
            rules_mod.cmd_from_json(folder, self.write_json(d, [self.RULE, second, dict(self.RULE, title="Tercera")]), "CL2")
            files = sorted(p.name for p in pathlib.Path(folder).glob("BR-*.md"))
            self.assertEqual(["BR-001.md", "BR-002.md", "BR-003.md"], files)
            rules_mod.cmd_build(folder)
            self.assertEqual(0, rules_mod.cmd_check(folder))
            self.assertTrue(pm.check_catalog(d, "BR")[0])
            catalog = (pathlib.Path(folder) / "CTLG-BR.md").read_text(encoding="utf-8")
            self.assertEqual(3, catalog.count("](BR-"))
            self.assertIn("type: CTLG", catalog)
            self.assertNotIn("15 % de descuento sin aprobación", catalog)  # el catálogo no repite enunciados
            self.assertEqual([], [i for i in validate_okf.validate(pathlib.Path(folder) / "BR-001.md")])

    def test_batch_is_all_or_nothing_and_rejects_unsourced_rules_without_question(self):
        rules_mod = load("rules", "skills/biz-rules-modeler/scripts/rules.py")
        with tempfile.TemporaryDirectory() as d:
            folder = str(self.setup_ws(d))
            bad = dict(self.RULE, title="Sin fuente", sources=[])
            with self.assertRaises(SystemExit):
                rules_mod.cmd_from_json(folder, self.write_json(d, [self.RULE, bad]), "CL2")
            self.assertEqual([], list(pathlib.Path(folder).glob("BR-*.md")))
            with self.assertRaises(SystemExit):  # término que no existe en el glosario
                rules_mod.cmd_from_json(folder, self.write_json(d, [dict(self.RULE, terms=["TRM-999"])]), "CL2")
            self.assertEqual([], list(pathlib.Path(folder).glob("BR-*.md")))

    def test_check_detects_orphans_missing_rows_and_placeholders(self):
        rules_mod = load("rules", "skills/biz-rules-modeler/scripts/rules.py")
        with tempfile.TemporaryDirectory() as d:
            folder = str(self.setup_ws(d))
            rules_mod.cmd_from_json(folder, self.write_json(d, [self.RULE]), "CL2")
            rules_mod.cmd_build(folder)
            self.assertEqual(0, rules_mod.cmd_check(folder))
            write_doc(d, "business/rules/BR-002.md", "BR", "BR-002")  # documento sin fila en el catálogo
            self.assertEqual(1, rules_mod.cmd_check(folder))
            self.assertIn("reglas fuera del catálogo", " ".join(self.check_output(rules_mod, folder)))
            (pathlib.Path(folder) / "BR-002.md").unlink()
            rules_mod.cmd_build(folder)
            (pathlib.Path(folder) / "BR-001.md").unlink()  # fila sin documento
            self.assertEqual(1, rules_mod.cmd_check(folder))
            self.assertTrue(pm.check_catalog(d, "BR")[0] is False)

    def test_rule_may_reference_other_rules_in_related(self):
        rules_mod = load("rules", "skills/biz-rules-modeler/scripts/rules.py")
        with tempfile.TemporaryDirectory() as d:
            folder = str(self.setup_ws(d))
            rules_mod.cmd_from_json(folder, self.write_json(d, [self.RULE]), "CL2")
            rules_mod.cmd_build(folder)
            meta = {"type": "BR", "id": "BR-001", "title": "T", "description": "D", "owner": "o", "product": "CL2",
                    "pack": "business-knowledge", "skill": "biz-rules-modeler", "version": "0.1.0", "status": "draft",
                    "sources": [{"id": "s", "resource": "x.md"}], "related": ["BR-002", "TRM-001", "BCAP-001"]}
            errors = rules_mod.check_rule(str(pathlib.Path(folder) / "BR-001.md"), meta, "# T\n")
            self.assertEqual([], [e for e in errors if "related" in e], errors)

    def test_template_text_is_flagged_by_check(self):
        rules_mod = load("rules", "skills/biz-rules-modeler/scripts/rules.py")
        with tempfile.TemporaryDirectory() as d:
            folder = str(self.setup_ws(d))
            rules_mod.cmd_new(folder, "Plantilla", "CL2")
            rules_mod.cmd_build(folder)
            self.assertEqual(1, rules_mod.cmd_check(folder))

    def check_output(self, rules_mod, folder):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rules_mod.cmd_check(folder)
        return buf.getvalue().splitlines()

    def test_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(PLUGIN / "skills/biz-pack-validator-publisher/scripts/check_pack.py"), "--workspace", d],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(1, r.returncode)


class StructureTests(unittest.TestCase):
    SKILLS = ["biz-knowledge-orchestrator", "biz-context-objectives-analyst", "biz-stakeholder-capability-mapper", "biz-glossary-curator",
              "biz-rules-modeler", "biz-information-model-designer", "biz-pack-validator-publisher", "biz-scenario-modeler"]

    def test_eight_skills_with_frontmatter(self):
        self.assertEqual(sorted(p.name for p in (PLUGIN / "skills").iterdir()), sorted(self.SKILLS))
        for s in self.SKILLS:
            text = (PLUGIN / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {s}\ndescription: "), s)
            self.assertNotIn("../", text.replace("](../", ""), s)

    def test_no_stale_references(self):
        for p in PLUGIN.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".py", ".json"} and "tests" not in p.parts:
                t = p.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn("af-business-rules-modeler", t.replace("antes `af-business-rules-modeler`", "").replace("`af-business-rules-modeler`, **movido", "").replace("| `biz-rules-modeler` | `af-business-rules-modeler`,", ""), str(p))


class ScenarioTests(unittest.TestCase):
    """Contrato de contenido de BSN (templates/scenario.md) y su verificador."""
    SKILL = PLUGIN / "skills" / "biz-scenario-modeler"

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("check_scenario", cls.SKILL / "scripts" / "check_scenario.py")
        cls.cs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.cs)

    def _filled(self, d, readiness="CONDITIONAL", step_br="BR-001"):
        body = f"""---
type: BSN
id: "BSN-001"
title: "Escenario de prueba"
description: "Recorrido de prueba del contrato de BSN"
version: "0.1.0"
status: draft
owner: "team:prueba"
classification: internal
tags: [business, bsn]
product: "PRUEBA"
pack: business-knowledge
skill: biz-scenario-modeler
generated:
  by: "biz-scenario-modeler/1.0.0"
  at: "2026-11-07T10:00:00-05:00"
sources:
  - id: F1
    resource: "fuente.md"
    title: "Fuente de prueba"
related: ["BR-001"]
---
# Escenario de prueba

## 1. Identificación
Actor STK-001, capacidad BCAP-001, objetivo BO-001.

## 2. Propósito y alcance
Disparador: solicitud. Inicio: registrado. Fin: activo.

## 3. Precondiciones
1. El cliente existe (BR-001).

## 4. Pasos del escenario
| Nº | Actor | Acción o evento | Regla (BR) | Resultado o estado siguiente | Excepción |
|---|---|---|---|---|---|
| 1 | Operador | Registra el cliente | {step_br} | Registrado | — |

## 5. Excepciones y alternativas
Sin excepciones registradas.

## 6. Resultado y estados finales
Activo cuando se cumple BR-001.

## 7. Términos TRM
Sin términos citados.

## 8. Trazabilidad
Paso 1 → BR-001 → BCAP-001 → BO-001.

## 9. Clasificación de afirmaciones
| Afirmación | Clasificación | Fuente | Confianza |
|---|---|---|---|
| Cliente existe | hecho | F1 | alta |

## 10. Preguntas abiertas
| ID | Pregunta | Owner | Bloquea |
|---|---|---|---|
| Q1 | ¿Hay excepciones? | PO | no |

## 11. Readiness y aprobación
- **Readiness:** {readiness}
- **Motivo:** fuente única.
- **Aprobación humana:** pendiente.
"""
        p = pathlib.Path(d) / "BSN-001-prueba.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_filled_scenario_conforms(self):
        with tempfile.TemporaryDirectory() as d:
            ws = pathlib.Path(d)
            (ws / "business" / "rules").mkdir(parents=True)
            (ws / "business" / "rules" / "BR-001.md").write_text("x", encoding="utf-8")
            p = self._filled(d)
            issues, _ = self.cs.check(str(p), str(ws))
            self.assertEqual([], issues)

    def test_step_without_existing_rule_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._filled(d, step_br="BR-999")
            issues, _ = self.cs.check(str(p), d)
            self.assertTrue(any("BR citada no existe: BR-999" in i for i in issues), issues)

    def test_bad_readiness_and_template_placeholders_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._filled(d, readiness="ANULADO")
            issues, notes = self.cs.check(str(p))
            self.assertTrue(any("readiness" in i for i in issues), issues)
            self.assertTrue(any("sin --workspace" in n for n in notes))
            issues, _ = self.cs.check(str(self.SKILL / "templates" / "scenario.md"))
            self.assertTrue(any("marcador de plantilla" in i for i in issues))

    def test_example_conforms_with_workspace(self):
        ex = self.SKILL / "examples" / "BSN-001-alta-cliente-con-servicio.md"
        with tempfile.TemporaryDirectory() as d:
            ws = pathlib.Path(d)
            for br in ("BR-001", "BR-002", "BR-003"):
                (ws / "business" / "rules").mkdir(parents=True, exist_ok=True)
                (ws / "business" / "rules" / f"{br}.md").write_text("x", encoding="utf-8")
            (ws / "business" / "terms").mkdir(parents=True, exist_ok=True)
            (ws / "business" / "terms" / "TRM-001-cliente.md").write_text("x", encoding="utf-8")
            issues, _ = self.cs.check(str(ex), str(ws))
            self.assertEqual([], issues)
            issues, _ = self.cs.check(str(ex))
            self.assertEqual([], issues)

    def test_sections_must_be_present(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._filled(d)
            p.write_text(p.read_text(encoding="utf-8").replace("## 9. Clasificación de afirmaciones", "## 9. X"), encoding="utf-8")
            issues, _ = self.cs.check(str(p))
            self.assertTrue(any("sección ausente: ## 9." in i for i in issues), issues)


if __name__ == "__main__":
    unittest.main()
