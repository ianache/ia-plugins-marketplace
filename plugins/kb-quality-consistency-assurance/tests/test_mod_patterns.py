import pathlib, shutil, subprocess, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]


class ModRiskPatterns(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "requiere Node.js")
    def test_detectores_del_mod(self):
        # D-19: rm con banderas en cualquier orden y push a ramas protegidas con refspecs (HEAD:main, +main, --delete main)
        p = subprocess.run(["node", str(ROOT / "tests/mod-risk-patterns.test.mjs")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("OK:", p.stdout)

    def test_readme_cita_archivos_que_existen(self):
        txt = (ROOT / "README.md").read_text(encoding="utf-8")
        for rel in ("hooks/hooks.json", "hooks/register.js", "standards/STD-OKF-001-v1.11.0-stable.md", "tests/mod-risk-patterns.test.mjs"):
            self.assertIn(rel, txt, rel)
            self.assertTrue((ROOT / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()


class RutasDeSalida(unittest.TestCase):
    def test_skills_escriben_bajo_el_orchestrator_root_del_pathmap(self):
        # D-20: las rutas de los SKILL salen de assets/pathmap.json (.comsatel/<plugin>/runs/), con punto
        import json, re
        root = json.loads((ROOT / "assets/pathmap.json").read_text(encoding="utf-8"))["orchestrator_root"]
        self.assertEqual(root, ".comsatel/kb-quality-consistency-assurance/runs/")
        skills = list((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 7)
        for f in skills:
            t = f.read_text(encoding="utf-8")
            self.assertIn(root + "<run_id>/", t, f)
            self.assertIsNone(re.search(r"(^|[^.\w])comsatel/kb-qca", t), f)
