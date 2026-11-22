import argparse
import importlib.util
import os
import pathlib
import tempfile
import unittest
import urllib.parse
from unittest import mock

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "skills/mgt-work-publisher-synchronizer/scripts"
spec = importlib.util.spec_from_file_location("gitlab_issues", SCRIPTS / "gitlab_issues.py")
gi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gi)

US = """---
type: US
id: {id}
title: "{id} — {title}"
description: "{title}: resumen."
version: "0.1.0"
status: draft
owner: team:requirements
classification: internal
tags: [requirements]
product: CL2
pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: af-user-story-designer/1.1.0
  at: "2026-10-24T10:00:00-05:00"
sources:
  - resource: requirements/input.md
---
# {id}

### AC-1 — Ingreso válido
### AC-2 — Ingreso inválido
"""
DSP = """---
type: DSP
id: DSP-001
title: "DSP-001 — Alcance de ingreso"
description: "Alcance candidato de ingreso seguro."
version: "0.1.0"
status: draft
---
# DSP-001

Historias: {ids}
"""
SSP = """---
type: SSP
id: SSP-001
dsp_id: {dsp}
---
# SSP-001

Incluye: {ids}
"""


class FakeGitLab:
    def __init__(self, milestones=None, issues=None):
        self.milestones = milestones if milestones is not None else [{"id": 1773, "iid": 1, "title": "Sprint 1 - P3M"}]
        self.issues = list(issues or [])
        self.links = {}
        self.calls = []

    def __call__(self, method, url, payload):
        self.calls.append((method, url, payload))
        u = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(u.query)
        if "/milestones" in u.path and method == "GET":
            return 200, [m for m in self.milestones if m["title"] == q.get("title", [""])[0]]
        if u.path.endswith("/links") and method == "GET":
            iid = int(u.path.split("/")[-2])
            return 200, [{"iid": n, "project_id": 587} for n in self.links.get(iid, [])]
        if u.path.endswith("/links") and method == "POST":
            iid = int(u.path.split("/")[-2])
            for a_, b_ in ((iid, payload["target_issue_iid"]), (payload["target_issue_iid"], iid)):
                self.links.setdefault(a_, []).append(b_)
            return 201, {"link_type": payload["link_type"]}
        if u.path.endswith("/issues") and method == "GET":
            term = q.get("search", [""])[0]
            where = "title" if q.get("in") == ["title"] else "description"
            want = [l for l in q.get("labels", [""])[0].split(",") if l]
            return 200, [i for i in self.issues if term in (i.get(where) or "") and all(l in i.get("labels", []) for l in want)]
        if u.path.endswith("/issues") and method == "POST":
            n = len(self.issues) + 1
            issue = {"id": 900 + n, "iid": n, "state": "opened", "web_url": f"https://gl/p/-/issues/{n}",
                     "title": payload["title"], "description": payload["description"],
                     "labels": [l for l in payload["labels"].split(",") if l],
                     "milestone": next((m for m in self.milestones if m["id"] == payload.get("milestone_id")), None)}
            self.issues.append(issue)
            return 201, issue
        if u.path.endswith("/time_estimate") and method == "POST":
            iid = int(u.path.split("/")[-2])
            issue = next(i for i in self.issues if i["iid"] == iid)
            import re
            parts = dict((u_, int(n_)) for n_, u_ in re.findall(r"(\d+)([hm])", payload["duration"]))
            issue["time_stats"] = {"time_estimate": parts.get("h", 0) * 3600 + parts.get("m", 0) * 60}
            return 200, issue["time_stats"]
        if method == "PUT":
            iid = int(u.path.rsplit("/", 1)[1])
            issue = next(i for i in self.issues if i["iid"] == iid)
            for k, v in payload.items():
                if k == "add_labels":
                    issue["labels"] += [l for l in v.split(",") if l not in issue["labels"]]
                elif k == "milestone_id":
                    issue["milestone"] = next((m for m in self.milestones if m["id"] == v), None)
                else:
                    issue[k] = v
            return 200, issue
        return 405, "no soportado"


class IssuesTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.dir = pathlib.Path(d.name)
        self.ids = ["CL2-US-001", "CL2-US-002"]
        self.paths = [self.story(i, f"Historia {n}") for n, i in enumerate(self.ids, 1)]
        self.dsp = self.dir / "DSP-001.md"
        self.dsp.write_text(DSP.format(ids=", ".join(self.ids)), encoding="utf-8")
        env = mock.patch.dict(os.environ, {"GITLAB_PAT": "glpat-SECRET123"})
        env.start()
        self.addCleanup(env.stop)

    def story(self, id_, title):
        p = self.dir / f"{id_}.md"
        p.write_text(US.format(id=id_, title=title), encoding="utf-8")
        return p

    def args(self, **kw):
        base = dict(project_id=587, dsp=str(self.dsp), story=[str(p) for p in self.paths], ssp=None, milestone_title="Sprint 1 - P3M", milestone_id=None,
                    label=[], kb_base_url=None, kb_root=str(self.dir), mode="dry-run", approved_by=None, estimates=None, project_issue_iid=None, project_data=None)
        base.update(kw)
        return argparse.Namespace(**base)

    def live(self, **kw):
        return self.args(mode="sync", approved_by="human:ana", **kw)

    def test_dry_run_never_writes_and_plans_creation(self):
        fake = FakeGitLab()
        r = gi.run(self.args(), opener=fake)
        self.assertEqual({"GET"}, {c[0] for c in fake.calls})
        self.assertEqual(7, len(r["rows"]))
        self.assertTrue(all(x["action"].startswith("crearía") for x in r["rows"]))

    def test_dry_run_without_pat_makes_no_calls(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            r = gi.run(self.args())
        self.assertTrue(all("sin consulta" in x["action"] for x in r["rows"]))

    def test_creates_story_issues_with_label_and_milestone_and_one_project_issue(self):
        fake = FakeGitLab()
        r = gi.run(self.live(), opener=fake)
        stories = [i for i in fake.issues if "User Story" in i["labels"]]
        project = [i for i in fake.issues if "Proyecto" in i["labels"]]
        self.assertEqual(2, len(stories))
        self.assertEqual(1, len(project))
        self.assertTrue(all(i["milestone"]["id"] == 1773 for i in stories))
        self.assertIsNone(project[0]["milestone"])
        self.assertEqual(["creado"] * 7, [x["action"] for x in r["rows"]])
        self.assertEqual(["US2: Historia 1", "US5: Historia 2"], [s["title"] for s in stories])
        d = stories[0]["description"]
        self.assertIn("# CL2-US-001 — Historia 1", d)
        self.assertIn("Fuente única de la historia:", d)
        self.assertIn("- US: `CL2-US-001.md`", d)
        self.assertIn("- DSP: `DSP-001`", d)
        self.assertIn("- Issue IID: `2`", d)
        self.assertIn("- Milestone: Sprint 1 - P3M", d)
        self.assertIn("- Project Issue: #1", d)  # el Project Issue se crea antes que las historias
        self.assertIn("Por definir", d)  # sin --estimates no se inventa una estimación
        self.assertNotIn("Criterios de aceptación", d)  # la historia y sus criterios viven solo en su archivo
        self.assertNotIn("AC-1", d)
        pd = project[0]["description"]
        self.assertIn("| CL2-US-001 | Historia 1 | #2 |", pd)
        self.assertIn("| CL2-US-002 | Historia 2 | #5 |", pd)
        for section in ("## Objetivo", "## Alcance", "## Exclusiones", "## Riesgos", "## Milestones", "## Trazabilidad"):
            self.assertIn(section, pd)
        self.assertIn("- Issue IID: `1`", pd)
        self.assertNotIn("<!--\nPlantilla", pd)  # la guía de la plantilla no se publica

    def test_sync_is_idempotent_and_updates_in_place(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        n = len(fake.issues)
        r = gi.run(self.live(), opener=fake)
        self.assertEqual(n, len(fake.issues))
        self.assertEqual(["sin cambios"] * 7, [x["action"] for x in r["rows"]])
        self.story("CL2-US-001", "Historia 1 corregida")
        r = gi.run(self.live(), opener=fake)
        self.assertEqual("actualizado", r["rows"][0]["action"])
        self.assertEqual(n, len(fake.issues))
        self.assertIn("corregida", [i for i in fake.issues if "User Story" in i["labels"]][0]["title"])

    def test_create_does_not_modify_existing(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        self.story("CL2-US-001", "Otro título")
        before = [dict(i) for i in fake.issues]
        r = gi.run(self.args(mode="create", approved_by="human:ana"), opener=fake)
        self.assertIn("ya existía", r["rows"][0]["action"])
        self.assertEqual(before, fake.issues)

    def test_update_keeps_labels_added_by_the_team_and_adds_missing(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        story["labels"] = ["TO TEST"]  # el equipo quitó 'User Story' y puso su propio label
        gi.run(self.live(), opener=fake)
        self.assertEqual({"TO TEST", "User Story"}, set(story["labels"]))
        put = [c for c in fake.calls if c[0] == "PUT"][-1]
        self.assertIn("add_labels", put[2])
        self.assertNotIn("labels", put[2])

    def test_extra_labels_and_never_closes(self):
        fake = FakeGitLab()
        gi.run(self.live(label=["Producto::CL2"]), opener=fake)
        self.assertTrue(all("Producto::CL2" in i["labels"] for i in fake.issues if "Task" not in i["labels"]))  # los labels extra son de historias y Project Issue
        self.assertTrue(all("state_event" not in (c[2] or {}) for c in fake.calls))
        self.assertTrue(all(c[0] in ("GET", "POST", "PUT") for c in fake.calls))

    def test_live_modes_need_human_approval_and_pat(self):
        for approver in (None, "agent", "human:"):
            with self.assertRaises(gi.MilestoneError):
                gi.run(self.args(mode="create", approved_by=approver), opener=FakeGitLab())
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(gi.MilestoneError):
                gi.run(self.args(mode="create", approved_by="human:ana"), opener=FakeGitLab())

    def test_story_outside_dsp_or_ssp_is_a_change_not_an_addition(self):
        extra = self.story("CL2-US-009", "Fuera del alcance")
        with self.assertRaises(gi.MilestoneError) as cm:
            gi.run(self.args(story=[str(p) for p in self.paths] + [str(extra)]), opener=FakeGitLab())
        self.assertIn("fuera del alcance", str(cm.exception))
        ssp = self.dir / "SSP-001.md"
        ssp.write_text(SSP.format(dsp="DSP-001", ids="CL2-US-001"), encoding="utf-8")  # el SSP omite la 002
        with self.assertRaises(gi.MilestoneError) as cm:
            gi.run(self.args(ssp=str(ssp)), opener=FakeGitLab())
        self.assertIn("CL2-US-002", str(cm.exception))
        ssp.write_text(SSP.format(dsp="DSP-999", ids=" ".join(self.ids)), encoding="utf-8")
        with self.assertRaises(gi.MilestoneError):
            gi.run(self.args(ssp=str(ssp)), opener=FakeGitLab())

    def test_ids_must_be_global_and_types_correct(self):
        legacy = self.story("US-001", "Heredada")
        with self.assertRaises(gi.MilestoneError) as cm:
            gi.run(self.args(story=[str(legacy)]), opener=FakeGitLab())
        self.assertIn("<PRODUCTO>-US-NNN", str(cm.exception))
        with self.assertRaises(gi.MilestoneError):
            gi.run(self.args(dsp=str(self.paths[0])), opener=FakeGitLab())  # un US no es un DSP
        with self.assertRaises(gi.MilestoneError):
            gi.run(self.args(story=[]), opener=FakeGitLab())

    def test_milestone_must_exist_and_ids_can_be_given_directly(self):
        with self.assertRaises(gi.MilestoneError) as cm:
            gi.run(self.args(milestone_title="No existe"), opener=FakeGitLab())
        self.assertIn("gitlab_milestone.py", str(cm.exception))
        fake = FakeGitLab()
        gi.run(self.live(milestone_title=None, milestone_id=1773), opener=fake)
        self.assertTrue(all(c[0] != "GET" or "milestones" not in c[1] for c in fake.calls))

    def test_duplicate_markers_stop(self):
        marker = "<!-- concept_id: CL2-US-001 -->"
        fake = FakeGitLab(issues=[{"id": 1, "iid": 1, "description": marker, "labels": []}, {"id": 2, "iid": 2, "description": marker, "labels": []}])
        with self.assertRaises(gi.MilestoneError):
            gi.run(self.live(), opener=fake)

    def test_links_use_kb_base_url_and_lineage_rows(self):
        fake = FakeGitLab()
        r = gi.run(self.live(kb_base_url="https://gl/kb/-/blob/main/"), opener=fake)
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        self.assertIn("[CL2-US-001.md](https://gl/kb/-/blob/main/CL2-US-001.md)", story["description"])
        self.assertEqual(7, len(r["lineage"]))
        self.assertTrue(r["lineage"][0].startswith("| CL2-US-001 | 2 | https://gl/p/-/issues/2 | creado | User Story |"))

    def estimates(self, **over):
        import json
        est = {"CL2-US-001": {"hours": 68, "size": "XL", "confidence": "Media", "basis": "15 criterios; factores: V, D",
                              "note": "Talla XL: se decide la división en el Sprint Planning."}}
        est.update(over)
        f = self.dir / "est.json"
        f.write_text(json.dumps(est), encoding="utf-8")
        return str(f)

    def test_estimate_goes_in_description_and_in_the_native_gitlab_estimate(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimates()), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        self.assertIn("68 h (talla XL, confianza Media). Propuesta; la confirma el equipo en el Sprint Planning. Talla XL", story["description"])
        self.assertIn("- **Base de la estimación:** 15 criterios; factores: V, D", story["description"])
        self.assertEqual(68 * 3600, story["time_stats"]["time_estimate"])
        other = next(i for i in fake.issues if "- US: `CL2-US-002.md`" in i["description"])
        self.assertNotIn("time_stats", other)  # sin dato no se fija el estimate
        n = len([c for c in fake.calls if c[1].endswith("time_estimate")])
        gi.run(self.live(estimates=self.estimates()), opener=fake)  # idempotente
        self.assertEqual(n, len([c for c in fake.calls if c[1].endswith("time_estimate")]))

    def test_estimates_are_validated(self):
        for bad in ({"CL2-US-999": {"hours": 4}}, {"CL2-US-001": {"hours": 0}}, {"CL2-US-001": {"hours": "68"}}):
            with self.assertRaises(gi.MilestoneError):
                gi.run(self.args(estimates=self.estimates(**bad)), opener=FakeGitLab())

    def test_governed_project_issue_is_linked_but_not_touched(self):
        fake = FakeGitLab()
        r = gi.run(self.live(project_issue_iid=6), opener=fake)
        self.assertEqual(2, len([i for i in fake.issues if "User Story" in i["labels"]]))
        self.assertFalse([i for i in fake.issues if "Proyecto" in i["labels"]])
        self.assertTrue(all("- Project Issue: #6" in i["description"] for i in fake.issues if "User Story" in i["labels"]))
        self.assertEqual("gobernado aparte: no se modificó", r["rows"][-1]["action"])

    def test_finds_issue_without_marker_by_its_source_line(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        n = len(fake.issues)
        gi.run(self.live(), opener=fake)
        self.assertEqual(n, len(fake.issues))
        self.assertNotIn("concept_id", story["description"])

    def test_project_issue_uses_dsp_sections_data_risks_and_milestone_row(self):
        import json
        self.dsp.write_text(DSP.format(ids=", ".join(self.ids)) + "\n## Objetivo\nHabilitar el ingreso.\n\n## Trabajo excluido\nBiometría.\n", encoding="utf-8")
        ssp = self.dir / "SSP-001.md"
        ssp.write_text(SSP.format(dsp="DSP-001", ids=" ".join(self.ids)).replace("dsp_id", 'title: "SSP-001 — Sprint 1"\ndsp_id'), encoding="utf-8")
        data = self.dir / "pd.json"
        data.write_text(json.dumps({"risks": [{"id": "R-01", "risk": "ARQ sin confirmar", "classification": "Técnico", "impact": 4, "probability": 4,
                                                "incidence": 16, "affects": "Alcance", "response": "Mitigar", "owner": "ARQ"}]}), encoding="utf-8")
        fake = FakeGitLab()
        gi.run(self.live(ssp=str(ssp), project_data=str(data)), opener=fake)
        pd = next(i for i in fake.issues if "Proyecto" in i["labels"])["description"]
        self.assertIn("## Objetivo\nHabilitar el ingreso.", pd)
        self.assertIn("## Exclusiones\nBiometría.", pd)
        self.assertIn("| R-01 | ARQ sin confirmar | Técnico | 4 | 4 | 16 | Alcance | Mitigar | ARQ |", pd)
        self.assertIn("| 1 | SSP-001 — Sprint 1 | Sprint 1 - P3M |", pd)
        self.assertNotIn("Aún no hay Milestones", pd)
        n = len(fake.issues)
        r = gi.run(self.live(ssp=str(ssp), project_data=str(data)), opener=fake)
        self.assertEqual(n, len(fake.issues))
        self.assertEqual("sin cambios", r["rows"][-1]["action"])

    def test_risks_are_never_invented(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        pd = next(i for i in fake.issues if "Proyecto" in i["labels"])["description"]
        self.assertNotIn("R-01", pd)
        self.assertIn("Aún no hay Milestones.", pd)

    def test_templates_exist_and_render_requires_every_value(self):
        for name in ("user-story-issue.md", "project-issue.md"):
            self.assertTrue((gi.TEMPLATES / name).is_file())
        with self.assertRaises(gi.MilestoneError):
            gi.render_template("user-story-issue.md", {"hu_id": "X"})
        out = gi.render_template("project-issue.md", {k: "v" for k in gi.PLACEHOLDER.findall((gi.TEMPLATES / "project-issue.md").read_text(encoding="utf-8"))})
        self.assertNotIn("{{", out)
        self.assertNotIn("<!--", out)

    def tasks_of(self, fake, story):
        return [i for i in fake.issues if "Task" in i["labels"] and i["title"].startswith(f"US{story['iid']}:")]

    def test_each_story_gets_a_dev_and_a_qa_task_linked_and_in_the_same_milestone(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        for story in [i for i in fake.issues if "User Story" in i["labels"]]:
            tasks = self.tasks_of(fake, story)
            self.assertEqual(2, len(tasks))
            by_role = {("Dev" if "Dev" in x["labels"] else "QA"): x for x in tasks}
            self.assertEqual(f"US{story['iid']}: Coordinación del desarrollo con Superpowers", by_role["Dev"]["title"])
            self.assertEqual(f"US{story['iid']}: Coordinación del Aseguramiento de Calidad", by_role["QA"]["title"])
            self.assertEqual({"Task", "Dev"}, set(by_role["Dev"]["labels"]))
            self.assertEqual({"Task", "QA"}, set(by_role["QA"]["labels"]))
            for x in tasks:
                self.assertEqual(story["milestone"]["id"], x["milestone"]["id"])  # mismo Milestone que la historia
                self.assertIn(x["iid"], fake.links[story["iid"]])  # enlazado con la historia
                self.assertIn(story["iid"], fake.links[x["iid"]])

    def test_task_description_has_toc_and_the_three_sections_per_role(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        dev, qa = (next(x for x in self.tasks_of(fake, story) if role in x["labels"]) for role in ("Dev", "QA"))
        for d in (dev["description"], qa["description"]):
            self.assertIn("## Tabla de contenido", d)
            for anchor in ("[Scope](#scope)", "[Acceptance Criteria](#acceptance-criteria)", "[Condition of Done](#condition-of-done)"):
                self.assertIn(anchor, d)
            for heading in ("## Scope", "## Acceptance Criteria", "## Condition of Done"):
                self.assertIn(heading, d)
            self.assertNotIn("<!--", d)
            self.assertIn(f"#{story['iid']}", d)
        self.assertIn("Superpowers", dev["description"])
        self.assertIn("Claude Code", dev["description"])
        self.assertIn("Cowork", dev["description"])
        self.assertIn("analista de calidad", qa["description"])
        self.assertNotEqual(dev["description"], qa["description"])

    def test_tasks_are_reused_not_duplicated_and_missing_ones_are_completed(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        n = len(fake.issues)
        r = gi.run(self.live(), opener=fake)
        self.assertEqual(n, len(fake.issues))
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        qa = next(x for x in self.tasks_of(fake, story) if "QA" in x["labels"])
        fake.issues.remove(qa)  # falta la tarea de QA: se vuelve a crear solo esa
        fake.links[story["iid"]].remove(qa["iid"])
        r = gi.run(self.live(), opener=fake)
        self.assertEqual(n, len(fake.issues))
        self.assertEqual(1, [x["action"] for x in r["rows"] if x["kind"] == "task"].count("creado"))
        self.assertEqual(2, len(self.tasks_of(fake, story)))

    def test_existing_task_without_link_or_milestone_is_fixed(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        story = next(i for i in fake.issues if "User Story" in i["labels"])
        dev = next(x for x in self.tasks_of(fake, story) if "Dev" in x["labels"])
        dev["milestone"] = None
        fake.links[story["iid"]].remove(dev["iid"])
        r = gi.run(self.live(), opener=fake)
        row = next(x for x in r["rows"] if x["kind"] == "task" and x["role"] == "dev" and x["concept_id"].startswith("CL2-US-001"))
        self.assertEqual("actualizado", row["action"])
        self.assertIn("link", row["changes"])
        self.assertEqual(story["milestone"]["id"], dev["milestone"]["id"])
        self.assertIn(dev["iid"], fake.links[story["iid"]])

    def estimator_output(self, with_qa=True):
        import json
        story = {"id": "CL2-US-001", "criteria": 5, "factors": ["E", "D"], "open_questions": 0, "factor_sum": 0.4, "dev_human_h": 22, "dev_agent_h": 22,
                 "size": "M", "confidence": "Media",
                 "qa": {"manual_tc": 4, "automated_tc": 2, "estimated": with_qa, "human_h": 6.5 if with_qa else 0, "agent_h": 9.5 if with_qa else 0},
                 "human_h": 22 + (6.5 if with_qa else 0), "agent_h": 22 + (9.5 if with_qa else 0)}
        f = self.dir / "estimator.json"
        f.write_text(json.dumps({"stories": [story], "totals": {"rate_pen_per_h": 30.0},
                                 "header": {"cost": "S/ 855.00", "time": "29 h", "cost_agent": "S/ 39.20 (USD 11.36)", "time_agent": "32 h"}}), encoding="utf-8")
        return str(f)

    def hours_of(self, issue):
        return issue["time_stats"]["time_estimate"] / 3600

    def test_story_and_task_estimates_are_human_plus_ai(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output()), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        self.assertEqual(22 + 6.5 + 22 + 9.5, self.hours_of(story))  # humano + IA de la historia
        dev = next(x for x in self.tasks_of(fake, story) if "Dev" in x["labels"])
        qa = next(x for x in self.tasks_of(fake, story) if "QA" in x["labels"])
        self.assertEqual(22 + 22, self.hours_of(dev))  # solo desarrollo: persona + IA
        self.assertEqual(6.5 + 9.5, self.hours_of(qa))  # solo QA: persona + IA
        self.assertEqual(self.hours_of(story), self.hours_of(dev) + self.hours_of(qa))
        self.assertIn("60 h (28.5 h de persona + 31.5 h de agente de IA, talla M, confianza Media)", story["description"])
        other = next(i for i in fake.issues if "- US: `CL2-US-002.md`" in i["description"])
        self.assertNotIn("time_stats", other)  # sin dato no se fija estimate, ni en la historia ni en sus tareas
        self.assertTrue(all("time_stats" not in x for x in self.tasks_of(fake, other)))

    def test_qa_without_test_cases_is_not_estimated_and_estimate_is_idempotent(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output(with_qa=False)), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        qa = next(x for x in self.tasks_of(fake, story) if "QA" in x["labels"])
        self.assertNotIn("time_stats", qa)
        self.assertEqual(44, self.hours_of(story))
        n = len([c for c in fake.calls if c[1].endswith("time_estimate")])
        r = gi.run(self.live(estimates=self.estimator_output(with_qa=False)), opener=fake)
        self.assertEqual(n, len([c for c in fake.calls if c[1].endswith("time_estimate")]))
        self.assertEqual({"sin cambios"}, {x["action"] for x in r["rows"]})

    def test_changed_estimate_updates_story_and_tasks(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output(with_qa=False)), opener=fake)
        r = gi.run(self.live(estimates=self.estimator_output(with_qa=True)), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        qa = next(x for x in self.tasks_of(fake, story) if "QA" in x["labels"])
        self.assertEqual(16, self.hours_of(qa))
        self.assertEqual(60, self.hours_of(story))
        self.assertIn("time_estimate", next(x for x in r["rows"] if x["kind"] == "task" and x["role"] == "qa" and x["concept_id"].startswith("CL2-US-001"))["changes"])

    def test_duration_format(self):
        self.assertEqual(["68h", "2h30m", "45m", "0h"], [gi.duration(h) for h in (68, 2.5, 0.75, 0)])

    def test_story_issue_has_costing_table_and_links_to_its_two_tasks(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output()), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        d = story["description"]
        self.assertIn("## Costeo", d)
        self.assertIn("| Concepto | Horas persona | Horas agente IA | Total horas | Costo persona (S/) |", d)
        self.assertIn("| Desarrollo | 22 | 22 | 44 | 660.00 |", d)
        self.assertIn("| QA | 6.5 | 9.5 | 16 | 195.00 |", d)
        self.assertIn("| **Total** | **28.5** | **31.5** | **60** | **855.00** |", d)
        self.assertIn("Tarifa de persona: S/ 30.00 por hora.", d)
        dev = next(x for x in self.tasks_of(fake, story) if "Dev" in x["labels"])
        qa = next(x for x in self.tasks_of(fake, story) if "QA" in x["labels"])
        self.assertIn("## Tareas", d)
        self.assertIn(f"| Dev | #{dev['iid']} — Coordinación del desarrollo con Superpowers | 44 h |", d)
        self.assertIn(f"| QA | #{qa['iid']} — Coordinación del Aseguramiento de Calidad | 16 h |", d)
        # además de la lista, las dos tareas están enlazadas en GitLab con la historia
        self.assertEqual({dev["iid"], qa["iid"]}, set(fake.links[story["iid"]]))

    def test_without_estimates_costing_is_pending_but_tasks_are_still_listed(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        d = story["description"]
        self.assertIn("## Costeo\n\nPor definir", d)
        self.assertNotIn("(por crear)", d)  # las tareas ya existen y la historia las lista
        self.assertEqual(2, d.count("— Coordinación"))

    def test_second_run_does_not_rewrite_story_description(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output()), opener=fake)
        puts = len([c for c in fake.calls if c[0] == "PUT"])
        r = gi.run(self.live(estimates=self.estimator_output()), opener=fake)
        self.assertEqual(puts, len([c for c in fake.calls if c[0] == "PUT"]))
        self.assertEqual({"sin cambios"}, {x["action"] for x in r["rows"]})

    def test_costing_without_rate_says_pending_not_zero(self):
        out = gi.costing_table({"dev_human_h": 4, "dev_agent_h": 4, "qa_human_h": 0, "qa_agent_h": 0})
        self.assertIn("Por definir", out)
        self.assertNotIn("0.00", out)

    def test_project_issue_has_estimation_and_costing_section_before_traceability(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output()), opener=fake)
        d = next(i for i in fake.issues if "Proyecto" in i["labels"])["description"]
        self.assertIn("## Estimación y Costeo", d)
        self.assertLess(d.index("## Estimación y Costeo"), d.index("## Trazabilidad"))
        self.assertLess(d.index("## Milestones"), d.index("## Estimación y Costeo"))
        self.assertIn("| Código | Título | Talla | # CA | Horas persona QA | Horas agente QA | Horas persona Dev | Horas agente Dev | Horas total QA | Horas total Dev | Horas total |", d)
        self.assertIn("| CL2-US-001 | Historia 1 | M | 5 | 6.5 | 9.5 | 22 | 22 | 16 | 44 | 60 |", d)
        self.assertIn("| CL2-US-002 | Historia 2 | " + " | ".join(["Por definir"] * 9) + " |", d)  # sin estimación no se inventa
        self.assertIn("| **Total** | | | | **6.5** | **9.5** | **22** | **22** | **16** | **44** | **60** |", d)
        for row in ("| Horas persona (`/time`) | 29 h |", "| Costo persona (`/cost`) | S/ 855.00 |", "| Horas agente IA (`/time_agent`) | 32 h |", "| Costo agente IA (`/cost_agent`) | S/ 39.20 (USD 11.36) |"):
            self.assertIn(row, d)

    def test_estimation_section_without_estimates_and_idempotent(self):
        fake = FakeGitLab()
        gi.run(self.live(), opener=fake)
        d = next(i for i in fake.issues if "Proyecto" in i["labels"])["description"]
        self.assertIn("| CL2-US-001 | Historia 1 | " + " | ".join(["Por definir"] * 9) + " |", d)
        self.assertNotIn("Total del Sprint", d)
        r = gi.run(self.live(), opener=fake)
        self.assertEqual("sin cambios", r["rows"][-1]["action"])

    def test_qa_not_estimated_is_shown_as_sin_tc_not_zero(self):
        fake = FakeGitLab()
        gi.run(self.live(estimates=self.estimator_output(with_qa=False)), opener=fake)
        story = next(i for i in fake.issues if "- US: `CL2-US-001.md`" in i["description"])
        self.assertIn("| QA | Sin TC | Sin TC | Sin TC | Sin TC |", story["description"])
        project = next(i for i in fake.issues if "Proyecto" in i["labels"])["description"]
        self.assertIn("| CL2-US-001 | Historia 1 | M | 5 | Sin TC | Sin TC | 22 | 22 | Sin TC | 44 | 44 |", project)

    def test_token_is_never_in_output_or_errors(self):
        def failing(method, url, payload):
            return 500, "boom glpat-SECRET123"
        with self.assertRaises(gi.MilestoneError) as cm:
            gi.run(self.live(), opener=failing)
        self.assertNotIn("glpat-SECRET123", str(cm.exception))
        import io
        import contextlib
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = gi.main(["--project-id", "1", "--dsp", str(self.dsp), "--story", str(self.paths[0]), "--mode", "create"])
        self.assertEqual(2, code)
        self.assertNotIn("SECRET", err.getvalue())


if __name__ == "__main__":
    unittest.main()
