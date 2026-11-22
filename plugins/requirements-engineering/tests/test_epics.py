import contextlib
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_okf import validate  # noqa: E402

spec = importlib.util.spec_from_file_location("us_ids", ROOT / "scripts" / "us_ids.py")
us_ids = importlib.util.module_from_spec(spec)
spec.loader.exec_module(us_ids)

pspec = importlib.util.spec_from_file_location("validate_pathmap", ROOT / "scripts" / "validate_pathmap.py")
pathmap = importlib.util.module_from_spec(pspec)
pspec.loader.exec_module(pathmap)

US_DOC = """---
type: US
id: {id}
title: Historia {id}
description: Historia de prueba
version: '0.1.0'
status: draft
owner: team:requirements
classification: internal
tags: [requirements]
product: CL2
pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: af-user-story-designer/1.1.0
  at: '2026-10-24T10:00:00-05:00'
sources:
  - resource: requirements/input.md
---
# Historia {id}
"""

EPC_DOC = """---
type: EPC
id: {id}
title: Épica {id}
description: Épica de prueba
version: '0.1.0'
status: draft
owner: team:requirements
classification: internal
tags: [requirements, epic]
pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: af-user-story-designer/1.1.0
  at: '2026-11-07T10:00:00-05:00'
sources:
  - id: RCP-002
    resource: requirements/context-packs/RCP-002-x.md
related: {related}
---
# Épica {id}
"""

STORIES = "requirements/context-packs/user-stories"
EPICS = "requirements/context-packs/epics"


def us(ws, id_):
    p = pathlib.Path(ws) / STORIES / f"{id_}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(US_DOC.format(id=id_), encoding="utf-8")


def epic(ws, id_, related, name=None):
    p = pathlib.Path(ws) / EPICS / (name or f"{id_}.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(EPC_DOC.format(id=id_, related="[" + ", ".join(related) + "]"), encoding="utf-8")
    return p


def check(ws):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = us_ids.main(["check", "--workspace", ws])
    return code, buf.getvalue()


class EpicValidator(unittest.TestCase):
    def test_accepts_epic_with_related_stories(self):
        with tempfile.TemporaryDirectory() as d:
            p = epic(d, "RCP-002-EPC-001", ["RCP-002-US-001"])
            self.assertEqual([], validate(p))

    def test_rejects_wrong_epic_id(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ("EPC-001", "CL2-EPC-001", "RCP-002-US-001", "RCP-2-EPC-001"):
                p = epic(d, bad, ["RCP-002-US-001"], name=f"{bad}.md")
                issues = validate(p)
                self.assertTrue(any("id de EPC" in i for i in issues), (bad, issues))

    def test_requires_related(self):
        with tempfile.TemporaryDirectory() as d:
            p = epic(d, "RCP-002-EPC-001", [])
            self.assertTrue(any("related" in i for i in validate(p)))


class EpicMembership(unittest.TestCase):
    def test_valid_grouping_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001"); us(d, "RCP-002-US-002")
            epic(d, "RCP-002-EPC-001", ["RCP-002-US-001", "RCP-002-US-002"])
            self.assertEqual(0, check(d)[0])

    def test_epic_citing_missing_story_fails(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001")
            epic(d, "RCP-002-EPC-001", ["RCP-002-US-001", "RCP-002-US-009"])
            code, out = check(d)
            self.assertEqual(1, code)
            self.assertIn("RCP-002-US-009", out)

    def test_story_in_two_epics_fails(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001")
            epic(d, "RCP-002-EPC-001", ["RCP-002-US-001"])
            epic(d, "RCP-002-EPC-002", ["RCP-002-US-001"])
            code, out = check(d)
            self.assertEqual(1, code)
            self.assertIn("más de una épica", out)

    def test_duplicate_epic_id_fails(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001")
            epic(d, "RCP-002-EPC-001", ["RCP-002-US-001"])
            epic(d, "RCP-002-EPC-001", ["RCP-002-US-001"], name="RCP-002-EPC-001-copia.md")
            self.assertEqual(1, check(d)[0])

    def test_story_without_epic_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001")
            self.assertEqual(0, check(d)[0])

    def test_epics_do_not_shift_story_numbering(self):
        with tempfile.TemporaryDirectory() as d:
            us(d, "RCP-002-US-001")
            epic(d, "RCP-002-EPC-007", ["RCP-002-US-001"])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                us_ids.main(["next", "--workspace", d, "--rcp", "RCP-002"])
            self.assertEqual("RCP-002-US-002", buf.getvalue().strip())


class EpicRoute(unittest.TestCase):
    def test_epic_route_and_type(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / EPICS / "RCP-002-EPC-001.md"
            p.parent.mkdir(parents=True)
            p.write_text("---\ntype: EPC\n---\n", encoding="utf-8")
            self.assertTrue(pathmap.validate(d, "EPC", p)[0])
            self.assertFalse(pathmap.validate(d, "EPC", pathlib.Path(d) / STORIES / "RCP-002-EPC-001.md")[0])


class EpicInG3(unittest.TestCase):
    def test_g3_task_declares_epic_output(self):
        wspec = importlib.util.spec_from_file_location("workflow", ROOT / "scripts" / "workflow.py")
        wf = importlib.util.module_from_spec(wspec)
        wspec.loader.exec_module(wf)
        t02 = next(t for t in wf.TASKS if t[0] == "T02")
        self.assertEqual("G3", t02[2])
        self.assertIn("EPC", t02[3])
        self.assertEqual("requirements/context-packs/epics/", wf.OUT_DIR["EPC"] + "/")


if __name__ == "__main__":
    unittest.main()
