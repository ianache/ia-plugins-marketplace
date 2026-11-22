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
check_mgmt = load("check_management", "skills/mgt-release-closure-auditor/scripts/check_management.py")

TYPES = {"PCH": "charters", "RMP": "roadmaps", "SSP": "sprints", "STR": "status-reports", "RSK": "risks", "CHG": "changes", "CLS": "closure"}

DOC = """---
type: {type}
id: "{id}"
title: "Documento {id}"
description: "Documento de prueba"
version: "0.1.0"
status: draft
owner: "team:gestion"
classification: internal
tags: [management]
product: "CL2"
pack: project-management
skill: mgt-test
generated:
  by: "mgt-test/1.0.0"
  at: "2026-10-24T10:00:00-05:00"
sources:
  - id: s1
    resource: docs/fuente.md
related: {related}
---
# Documento {id}

{body}
"""


def write_doc(ws, type_, id_, related="[]", body="Contenido."):
    p = pathlib.Path(ws) / "management" / TYPES[type_] / f"{id_}-x.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(DOC.format(type=type_, id=id_, related=related, body=body), encoding="utf-8")
    return p


class A:
    def __init__(self, **k):
        self.__dict__.update(k)


class OkfAndPathmap(unittest.TestCase):
    def test_types_are_approved_and_routed(self):
        self.assertEqual(set(pm.MAP), set(TYPES))
        with tempfile.TemporaryDirectory() as d:
            for t in TYPES:
                p = write_doc(d, t, f"{t}-001")
                self.assertFalse(any("type propuesto" in i for i in validate_okf.validate(p)), t)
                self.assertFalse(any("no aprobado" in i for i in validate_okf.validate(p, True)), t)
                self.assertTrue(pm.validate(d, t, p)[0], t)

    def test_pack_fields_required(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_doc(d, "PCH", "PCH-001")
            q = p.with_name("PCH-002-x.md")
            q.write_text(p.read_text(encoding="utf-8").replace("skill: mgt-test\n", ""), encoding="utf-8")
            self.assertTrue(any("skill requerido" in i for i in validate_okf.validate(q)))

    def test_wrong_dir_and_id_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_doc(d, "PCH", "PCH-001")
            moved = pathlib.Path(d) / "management/roadmaps/PCH-001-x.md"
            moved.parent.mkdir(parents=True, exist_ok=True)
            moved.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertFalse(pm.validate(d, "PCH", moved)[0])
            other = pathlib.Path(d) / "management/charters/otro.md"
            other.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertFalse(pm.validate(d, "PCH", other)[0])


class WorkflowTests(unittest.TestCase):
    def run_dir(self, scenario="initiative", just=None):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        r = pathlib.Path(d.name) / ".comsatel/project-management/runs/RUN-1"
        wf.init(A(run=str(r), scenario=scenario, workspace=d.name, justification=just))
        return r

    def test_no_gate_cycle_in_any_scenario(self):
        for sc in wf.SCENARIOS:
            r = self.run_dir(sc, "motivo" if wf.SCENARIOS[sc] else None)
            for t in wf.check(r)[0]["tasks"]:
                self.assertLess(wf.GATES.index(t["entry_gate"]), wf.GATES.index(t["gate"]))

    def test_task_chain_matches_skills(self):
        p = wf.check(self.run_dir())[0]
        self.assertEqual([t["skill"] for t in p["tasks"]], [
            "mgt-charter-roadmap-planner", "mgt-backlog-iteration-planner", "mgt-work-publisher-synchronizer",
            "mgt-risk-change-controller", "mgt-progress-reporting-analyst", "mgt-release-closure-auditor"])
        self.assertEqual(p["tasks"][3]["output_paths"], {"RSK": "management/risks", "CHG": "management/changes"})
        self.assertTrue(p["tasks"][2]["output_paths"]["gitlab-publication"].startswith(".comsatel/project-management/runs/"))

    def test_risks_before_report(self):
        gates = {t["skill"]: t["gate"] for t in wf.check(self.run_dir())[0]["tasks"]}
        self.assertLess(gates["mgt-risk-change-controller"], gates["mgt-progress-reporting-analyst"])

    def test_cadence_runs_only_risk_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / ".comsatel/project-management/runs/R"
            with self.assertRaises(ValueError):
                wf.init(A(run=str(r), scenario="cadence", workspace=d, justification=None))
        p = wf.check(self.run_dir("cadence", "ciclo semanal"))[0]
        self.assertEqual([t["gate"] for t in p["tasks"]], ["G4", "G5"])
        self.assertEqual(p["tasks"][0]["entry_gate"], "G0")

    def test_iteration_skips_charter(self):
        p = wf.check(self.run_dir("iteration", "acta ya aprobada"))[0]
        self.assertEqual([t["gate"] for t in p["tasks"]], ["G2", "G3", "G4", "G5", "G6"])

    def test_gates_in_order_and_human_actor(self):
        r = self.run_dir()
        d = tempfile.mkdtemp(); self.addCleanup(__import__("shutil").rmtree, d, True)
        ev = str(pathlib.Path(d) / "evidencia.md"); pathlib.Path(ev).write_text("ok", encoding="utf8")
        with self.assertRaises(ValueError):
            wf.approve(A(run=str(r), gate="G0", actor="agent", evidence="x"))
        wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence=ev))
        with self.assertRaises(ValueError):
            wf.approve(A(run=str(r), gate="G2", actor="human:ana", evidence="x"))
        for to in ("READY", "IN_PROGRESS", "NEEDS_REVIEW", "DONE"):
            wf.transition(A(run=str(r), task="T01", to=to, actor="agent", reason="r", evidence=ev))
        wf.approve(A(run=str(r), gate="G1", actor="human:ana", evidence="MR-12"))
        with self.assertRaises(ValueError):
            wf.transition(A(run=str(r), task="T03", to="READY", actor="agent", reason="r", evidence=None))

    def test_evidencia_debe_ser_archivo_o_referencia(self):
        # D-17: texto libre o archivo inexistente ya no se acepta; las aprobaciones admiten referencias MR-12 / URL
        r = self.run_dir()
        for malo in ("no-existe.md", "x", "texto libre", "MR-", "12"):
            with self.subTest(evidence=malo), self.assertRaises(ValueError):
                wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence=malo))
        for ok in ("MR-12", "https://gitlab.example/g/p/-/merge_requests/9"):
            self.setUp(); r = self.run_dir()
            wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence=ok))
        self.setUp(); r = self.run_dir()
        wf.approve(A(run=str(r), gate="G0", actor="human:ana", evidence="MR-1"))
        for to in ("READY", "IN_PROGRESS"):
            wf.transition(A(run=str(r), task="T01", to=to, actor="agent", reason="r", evidence=None))
        wf.transition(A(run=str(r), task="T01", to="NEEDS_REVIEW", actor="agent", reason="r", evidence=__file__))
        for malo in ("MR-12", "no-existe.md"):  # en transition la evidencia debe ser un archivo
            with self.subTest(transition=malo), self.assertRaises(ValueError):
                wf.transition(A(run=str(r), task="T01", to="DONE", actor="agent", reason="r", evidence=malo))

    def test_cycle_detected(self):
        r = self.run_dir()
        p = json.loads((r / "execution-plan.json").read_text())
        p["tasks"][1]["entry_gate"] = "G2"
        (r / "execution-plan.json").write_text(json.dumps(p))
        with self.assertRaises(ValueError):
            wf.check(r)


class CheckManagementTests(unittest.TestCase):
    def test_clean_and_findings(self):
        with tempfile.TemporaryDirectory() as d:
            write_doc(d, "PCH", "PCH-001")
            write_doc(d, "RMP", "RMP-001", related="[PCH-001]", body="Acta: [PCH](../charters/PCH-001-x.md).")
            write_doc(d, "SSP", "SSP-001", related="[RMP-001]")
            write_doc(d, "RSK", "RSK-001", related="[PCH-001]",
                      body="| ID | Riesgo | P | I | Dueño | R | D | Estado | F |\n|---|---|---|---|---|---|---|---|---|\n| R-01 | x | a | a | PMO | m | s | mitigated | f |")
            write_doc(d, "CHG", "CHG-001", related="[PCH-001]", body="- **Estado:** approved\n- **Decidido por:** human:ana — 2026-10-24")
            res = check_mgmt.check(d)
            self.assertEqual([], res["errors"], res)
            self.assertTrue(all("type propuesto" in w for w in res["warnings"]), res["warnings"])
            # rompe: related inexistente, enlace roto, CHG aprobado sin decisor, riesgo sin dueño
            write_doc(d, "STR", "STR-001", related="[SSP-999]", body="[x](../sprints/NOPE.md)")
            write_doc(d, "CHG", "CHG-002", body="- **Estado:** approved\n- **Decidido por:** <human:nombre — fecha>")
            write_doc(d, "RSK", "RSK-002", body="| R-01 | x | a | a |  | m | s | open | f |")
            joined = " ".join(check_mgmt.check(d)["errors"])
            for fragment in ("SSP-999", "enlace roto", "sin 'Decidido por", "sin dueño"):
                self.assertIn(fragment, joined)

    def test_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(PLUGIN / "skills/mgt-release-closure-auditor/scripts/check_management.py"), "--workspace", d],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(1, r.returncode)


class StructureTests(unittest.TestCase):
    SKILLS = ["mgt-delivery-orchestrator", "mgt-charter-roadmap-planner", "mgt-backlog-iteration-planner", "mgt-work-publisher-synchronizer",
              "mgt-risk-change-controller", "mgt-progress-reporting-analyst", "mgt-release-closure-auditor"]

    def test_seven_skills_with_frontmatter_and_templates(self):
        self.assertEqual(sorted(p.name for p in (PLUGIN / "skills").iterdir()), sorted(self.SKILLS))
        for s in self.SKILLS:
            text = (PLUGIN / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {s}\ndescription: "), s)
            self.assertTrue((PLUGIN / "skills" / s / "VERSION").is_file(), s)
        for t in TYPES:
            self.assertTrue(any((PLUGIN / "skills").glob(f"*/templates/*.md")), t)

    def test_templates_use_declared_types(self):
        found = set()
        for p in (PLUGIN / "skills").glob("*/templates/*.md"):
            meta = check_mgmt.meta_of(p.read_text(encoding="utf-8"))
            if meta.get("type"):
                found.add(meta["type"])
                self.assertEqual(meta.get("pack"), "project-management", p)
        self.assertEqual(found, set(TYPES))


if __name__ == "__main__":
    unittest.main()
