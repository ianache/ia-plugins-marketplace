import argparse
import importlib.util
import os
import pathlib
import re
import tempfile
import unittest
import urllib.parse
from unittest import mock

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gitlab_milestone", PLUGIN / "skills/mgt-work-publisher-synchronizer/scripts/gitlab_milestone.py")
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)

SSP = """---
type: SSP
id: "SSP-001"
title: "Sprint 12 - Prueba"
description: "Meta del Sprint"
version: "0.1.0"
status: draft
owner: "team:gestion"
classification: internal
tags: [management, ssp]
product: "CL2"
pack: project-management
skill: mgt-backlog-iteration-planner
dsp_id: "DSP-001"
generated:
  by: "mgt-backlog-iteration-planner/1.0.0"
  at: "2026-10-24T10:00:00-05:00"
sources:
  - id: dsp-001
    resource: requirements/scope-packs/DSP-001-x.md
related: []
---

# SSP-001 — Sprint 12

## Sprint Goal
Algo.

## Descripción del Milestone
{desc}

# Sprint GitLab Control Pack

| Elemento | Estado |
|---|---|
"""


def make_desc(sub="Sprint 12 - Prueba", body="", **hdr):
    values = dict(project="Proyecto X", subproject=sub, cost="1000", time="PENDIENTE", client="COMSATEL", group="Proyectos", cost_agent="S/ 42.61 (USD 11.36)", time_agent="24 h")
    values.update(hdr)
    lines = [f"/{k} {v}".rstrip() for k, v in values.items() if v is not None]
    return "\n".join(lines) + (("\n\n" + body) if body else "")


class FakeGitLab:
    """Servidor GitLab mínimo en memoria: milestones de proyecto."""

    def __init__(self, existing=None):
        self.items = list(existing or [])
        self.calls = []

    def __call__(self, method, url, payload):
        self.calls.append((method, url, payload))
        path = urllib.parse.urlparse(url).path
        if method == "GET":
            title = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("title", [""])[0]
            return 200, [m for m in self.items if m["title"] == title]
        if method == "POST":
            m = dict(payload, id=100 + len(self.items), iid=len(self.items) + 1, state="active", web_url="https://gl/x/-/milestones/1")
            self.items.append(m)
            return 201, m
        if method == "PUT":
            mid = int(path.rsplit("/", 1)[1])
            m = next(i for i in self.items if i["id"] == mid)
            m.update(payload)
            return 200, m
        return 405, "método no soportado"


def args(ssp, **kw):
    base = dict(ssp=str(ssp), project_id=605, group_id=None, mode="dry-run", start_date=None, due_date=None, approved_by=None)
    base.update(kw)
    return argparse.Namespace(**base)


class MilestoneTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.dir = pathlib.Path(d.name)
        self.ssp = self.write(make_desc())
        env = mock.patch.dict(os.environ, {"GITLAB_PAT": "glpat-SECRET123"})
        env.start()
        self.addCleanup(env.stop)

    def write(self, desc):
        p = self.dir / "SSP-001.md"
        p.write_text(SSP.format(desc=desc), encoding="utf-8")
        return p

    def test_dry_run_never_writes(self):
        fake = FakeGitLab()
        r = gm.run(args(self.ssp), opener=fake)
        self.assertEqual("crearía", r["action"])
        self.assertEqual(["GET"], [c[0] for c in fake.calls])
        self.assertEqual("Sprint 12 - Prueba", r["fields_to_send"]["title"])

    def test_dry_run_without_pat_makes_no_network_call(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            r = gm.run(args(self.ssp))
        self.assertIn("sin consulta", r["action"])

    def test_live_modes_need_human_approval_and_pat(self):
        for mode in ("create", "update", "sync"):
            for approver in (None, "agent", "human:"):
                with self.assertRaises(gm.MilestoneError):
                    gm.run(args(self.ssp, mode=mode, approved_by=approver), opener=FakeGitLab())
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(gm.MilestoneError):
                gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=FakeGitLab())

    def test_create_is_idempotent(self):
        fake = FakeGitLab()
        r1 = gm.run(args(self.ssp, mode="create", approved_by="human:ana", due_date="2026-11-07"), opener=fake)
        self.assertEqual("creado", r1["action"])
        self.assertEqual("2026-11-07", fake.items[0]["due_date"])
        self.assertNotIn("start_date", fake.items[0])  # las fechas no pasadas no se inventan
        r2 = gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=fake)
        self.assertEqual(1, len(fake.items))
        self.assertIn("ya existía", r2["action"])
        self.assertIn("human:ana", r1["control_pack_row"])
        self.assertIn("ejecutada", r1["control_pack_row"])

    def test_update_and_sync(self):
        fake = FakeGitLab()
        with self.assertRaises(gm.MilestoneError):
            gm.run(args(self.ssp, mode="update", approved_by="human:ana"), opener=fake)
        gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)  # crea
        self.assertEqual(1, len(fake.items))
        self.write(make_desc(cost="2500"))
        r = gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)
        self.assertEqual("actualizado", r["action"])
        self.assertIn("/cost 2500", fake.items[0]["description"].splitlines())
        r = gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)
        self.assertEqual("sin cambios", r["action"])
        self.assertEqual("GET", fake.calls[-1][0])  # la última sincronización solo consultó

    def test_never_closes_or_deletes(self):
        fake = FakeGitLab()
        gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)
        self.write(make_desc(body="Otra."))
        gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)
        self.assertTrue(all(c[0] in ("GET", "POST", "PUT") for c in fake.calls))
        self.assertTrue(all("state_event" not in (c[2] or {}) for c in fake.calls))

    def test_duplicate_titles_stop(self):
        fake = FakeGitLab([{"id": 1, "iid": 1, "title": "Sprint 12 - Prueba"}, {"id": 2, "iid": 2, "title": "Sprint 12 - Prueba"}])
        with self.assertRaises(gm.MilestoneError):
            gm.run(args(self.ssp, mode="sync", approved_by="human:ana"), opener=fake)

    def test_group_scope_uses_group_path(self):
        fake = FakeGitLab()
        gm.run(args(self.ssp, project_id=None, group_id=77, mode="create", approved_by="human:ana"), opener=fake)
        self.assertTrue(all("/groups/77/milestones" in c[1] for c in fake.calls))

    def test_validation_errors(self):
        for kw in (dict(project_id=None), dict(group_id=5), dict(start_date="12/11/2026"), dict(start_date="2026-12-01", due_date="2026-11-01")):
            with self.assertRaises(gm.MilestoneError):
                gm.run(args(self.ssp, **kw), opener=FakeGitLab())
        with self.assertRaises(gm.MilestoneError):  # plantilla sin completar
            self.write("<Propuesta para publicar en el Milestone>")
            gm.run(args(self.ssp), opener=FakeGitLab())
        not_ssp = self.dir / "otro.md"
        not_ssp.write_text(SSP.format(desc="x").replace("type: SSP", "type: STR"), encoding="utf-8")
        with self.assertRaises(gm.MilestoneError):
            gm.run(args(not_ssp), opener=FakeGitLab())

    def test_header_is_required_and_validated(self):
        def raw(*lines):
            return "\n".join(lines)
        for desc, fragment in (
            ("Solo texto libre sin cabecera.", "cabecera"),
            (make_desc(cost=None), "debe tener, en este orden"),
            (make_desc(time_agent=None), "debe tener, en este orden"),
            (raw("/subproject S", "/project P", "/cost 1", "/time 1", "/client C", "/group G", "/cost_agent 1", "/time_agent 1", "", "texto"), "en este orden"),
            (make_desc(sub="PENDIENTE"), "no puede estar vacío ni PENDIENTE"),
            (make_desc(project_end="20-10-2026"), "/project_end"),
            (raw("/project P", "/subproject S", "/cost 1", "/time 1", "/client C", "/group G", "/cost_agent 1", "/time_agent 1", "/otro x", "", "texto"), "en este orden"),
        ):
            self.write(desc)
            with self.assertRaises(gm.MilestoneError) as cm:
                gm.run(args(self.ssp), opener=FakeGitLab())
            self.assertIn(fragment, str(cm.exception), desc)

    def test_title_comes_from_subproject_and_pending_values_are_reported(self):
        self.write(make_desc(sub="Sprint 3 - P3M", cost="", project_end="2026-11-30"))
        r = gm.run(args(self.ssp), opener=FakeGitLab())
        self.assertEqual("Sprint 3 - P3M", r["title"])
        self.assertEqual(["cost", "time"], r["pending_header_values"])
        self.write(make_desc(cost_agent="S/ PENDIENTE (USD 11.36)"))
        self.assertIn("cost_agent", gm.run(args(self.ssp), opener=FakeGitLab())["pending_header_values"])
        self.assertEqual("2026-11-30", r["header"]["project_end"])
        self.assertEqual("Sprint 3 - P3M", r["fields_to_send"]["title"])

    def test_description_has_only_the_header_commands(self):
        fake = FakeGitLab()
        gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=fake)
        sent = fake.items[0]["description"]
        lines = ["/project Proyecto X", "/subproject Sprint 12 - Prueba", "/cost 1000", "/time PENDIENTE", "/client COMSATEL", "/group Proyectos", "/cost_agent S/ 42.61 (USD 11.36)", "/time_agent 24 h"]
        self.assertEqual(lines, sent.splitlines())

    def test_text_after_the_header_is_not_published_and_project_end_is_optional(self):
        self.write(make_desc(body="SSP-001 (DSP-001). Objetivo: algo.\n\nHistorias: CL2-US-001.", project_end="2026-11-30"))
        fake = FakeGitLab()
        gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=fake)
        sent = fake.items[0]["description"]
        self.assertTrue(sent.splitlines()[-1] == "/project_end 2026-11-30")
        self.assertNotIn("Objetivo", sent)
        self.assertNotIn("CL2-US-001", sent)

    def test_template_matches_the_live_milestone_format(self):
        live = ("/project Catálogo de Skills - business, requirements y management\n/subproject Sprint 1 - Catálogo de Skills (business y management)\n"
                "/cost S/ 4,860.00\n/time 162 h\n/client COMSATEL\n/group Proyectos\n/cost_agent S/ 39.20 (USD 11.36)\n/time_agent 167 h")
        self.write(live)
        title, desc, header, pending = gm.read_ssp(self.ssp)
        self.assertEqual(live, desc)
        self.assertEqual([], pending)
        self.assertNotIn("<!--", desc)

    def test_fenced_block_is_what_gets_published(self):
        fence = chr(96) * 3
        self.write("\n".join(["Explicación para quien revisa.", "", fence + "text", make_desc(), fence, "", "Nota posterior."]))
        fake = FakeGitLab()
        gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=fake)
        sent = fake.items[0]["description"]
        self.assertTrue(sent.startswith("/project "))
        self.assertNotIn("Explicación", sent)
        self.assertNotIn("Nota posterior", sent)

    def test_unfilled_template_is_rejected(self):
        tpl = PLUGIN / "skills/mgt-backlog-iteration-planner/templates/sprint-scope-pack.md"
        with self.assertRaises(gm.MilestoneError) as cm:
            gm.read_ssp(tpl)
        self.assertIn("/subproject", str(cm.exception))

    def test_token_is_redacted_in_errors(self):
        def failing(method, url, payload):
            return 500, "boom glpat-SECRET123 PRIVATE-TOKEN"
        with self.assertRaises(gm.MilestoneError) as cm:
            gm.run(args(self.ssp, mode="create", approved_by="human:ana"), opener=failing)
        self.assertNotIn("glpat-SECRET123", str(cm.exception))
        self.assertNotIn("PRIVATE-TOKEN", str(cm.exception))

    def test_cli_error_exit_code_and_no_secret(self):
        import io
        import contextlib
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = gm.main([str(self.ssp), "--mode", "create"])
        self.assertEqual(2, code)
        self.assertNotIn("SECRET", err.getvalue())


if __name__ == "__main__":
    unittest.main()
