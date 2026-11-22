import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_okf import validate  # noqa: E402

spec = importlib.util.spec_from_file_location("us_ids", ROOT / "scripts" / "us_ids.py")
us_ids = importlib.util.module_from_spec(spec)
spec.loader.exec_module(us_ids)

DOC = """---
type: US
id: {id}
title: Historia {id}
description: Historia de prueba
version: '0.1.0'
status: draft
owner: team:requirements
classification: internal
tags: [requirements]
{product_line}pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: af-user-story-designer/1.1.0
  at: '2026-10-24T10:00:00-05:00'
sources:
  - resource: requirements/input.md
{extra}---
# Historia {id}
"""


def story(ws, id_, product="CL2", name=None, extra=""):
    product_line = "" if product is None else f"product: {product}\n"
    p = pathlib.Path(ws) / "requirements/context-packs/user-stories" / (name or f"{id_}.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(DOC.format(id=id_, product_line=product_line, extra=extra), encoding="utf-8")
    return p


def run(*args):
    return us_ids.main(list(args))


class IdFormat(unittest.TestCase):
    def test_validator_accepts_rcp_prefixed_id(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], validate(story(d, "RCP-002-US-001")))
            self.assertEqual([], validate(story(d, "RCP-002-US-014", product="CL2-BAS")))

    def test_product_is_optional(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], validate(story(d, "RCP-002-US-001", product=None)))

    def test_validator_rejects_wrong_ids(self):
        with tempfile.TemporaryDirectory() as d:
            for id_ in ("US-001", "HU-01-02", "CL2-US-001", "DSP-003-US-001", "RCP-2-US-001", "rcp-002-US-001", "RCP-002-US-1"):
                issues = validate(story(d, id_, name=f"{id_}.md"))
                self.assertTrue(any("id de US" in i for i in issues), (id_, issues))

    def test_validator_rejects_lowercase_product(self):
        with tempfile.TemporaryDirectory() as d:
            issues = validate(story(d, "RCP-002-US-001", product="cl2"))
            self.assertTrue(any("product de US" in i for i in issues), issues)

    def test_legacy_id_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], validate(story(d, "RCP-002-US-001", extra="legacy_id: CL2-US-014\n")))


class CheckAndNext(unittest.TestCase):
    def test_next_increments_per_rcp(self):
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001")
            story(d, "RCP-002-US-007")
            story(d, "RCP-003-US-003")
            self.assertEqual(0, run("next", "--workspace", d, "--rcp", "RCP-002"))
            self.assertEqual(0, run("next", "--workspace", d, "--rcp", "RCP-009"))

    def test_next_values(self):
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-007")
            story(d, "RCP-003-US-004")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                run("next", "--workspace", d, "--rcp", "RCP-002", "--count", "2")
                run("next", "--workspace", d, "--rcp", "RCP-003")
                run("next", "--workspace", d, "--rcp", "RCP-009")
            self.assertEqual(["RCP-002-US-008", "RCP-002-US-009", "RCP-003-US-005", "RCP-009-US-001"], buf.getvalue().split())

    def test_next_rejects_bad_rcp(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ("CL2", "rcp-002", "RCP-2", "DSP-003", "US-001"):
                with self.assertRaises(SystemExit):
                    run("next", "--workspace", d, "--rcp", bad)

    def test_same_number_in_two_rcps_is_fine(self):
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001")
            story(d, "RCP-003-US-001")
            self.assertEqual(0, run("check", "--workspace", d))

    def test_duplicate_id_in_one_kb_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001")
            story(d, "RCP-002-US-001", name="RCP-002-US-001-copia.md")
            self.assertEqual(1, run("check", "--workspace", d))

    def test_collision_across_kbs(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            story(a, "RCP-002-US-001")
            story(b, "RCP-002-US-001")  # misma ruta relativa en otra KB: es otro documento
            self.assertEqual(0, run("check", "--workspace", a))
            self.assertEqual(1, run("check", "--workspace", a, "--also", b))

    def test_malformed_and_misnamed(self):
        with tempfile.TemporaryDirectory() as d:
            story(d, "US-001")
            self.assertEqual(1, run("check", "--workspace", d))
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001", name="otro-nombre.md")
            self.assertEqual(1, run("check", "--workspace", d))

    def test_git_refs_detect_parallel_numbering(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*a):
                subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t", *a], check=True, capture_output=True)
            git("init", "-q", "-b", "main")
            story(d, "RCP-002-US-001")
            git("add", "."); git("commit", "-q", "-m", "base")
            git("checkout", "-q", "-b", "otra")
            story(d, "RCP-002-US-002", name="RCP-002-US-002-ruta-a.md")
            git("add", "."); git("commit", "-q", "-m", "otra rama")
            git("checkout", "-q", "main")
            # misma US en main y en la rama: un solo documento, sin colisión
            self.assertEqual(0, run("check", "--workspace", d, "--git-ref", "otra"))
            # en main alguien numera otra historia con el mismo ID
            story(d, "RCP-002-US-002", name="RCP-002-US-002-ruta-b.md")
            self.assertEqual(1, run("check", "--workspace", d, "--git-ref", "otra"))

    def test_bad_git_ref_stops(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "-C", d, "init", "-q"], check=True, capture_output=True)
            with self.assertRaises(SystemExit):
                run("check", "--workspace", d, "--git-ref", "no-existe")


class Alcance(unittest.TestCase):
    """D-21: solo se recorre requirements/; copias de modelos o ejemplos fuera de esa carpeta no cuentan."""

    def copia(self, d, rel):
        p = pathlib.Path(d) / rel / "RCP-002-US-001.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text((pathlib.Path(d) / "requirements/context-packs/user-stories/RCP-002-US-001.md").read_text(encoding="utf-8"), encoding="utf-8")

    def test_copias_fuera_de_requirements_no_cuentan(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001"); story(d, "RCP-002-US-002")
            self.copia(d, "examples"); self.copia(d, "modelos/ejemplo")
            self.assertEqual(0, run("check", "--workspace", d))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                run("next", "--workspace", d, "--rcp", "RCP-002")
            self.assertEqual("RCP-002-US-003", out.getvalue().strip())

    def test_exclude_omite_rutas_dentro_de_requirements(self):
        with tempfile.TemporaryDirectory() as d:
            story(d, "RCP-002-US-001")
            self.copia(d, "requirements/examples")
            self.assertEqual(1, run("check", "--workspace", d))          # duplicado dentro de requirements/
            self.assertEqual(0, run("check", "--workspace", d, "--exclude", "requirements/examples/*"))


if __name__ == "__main__":
    unittest.main()
