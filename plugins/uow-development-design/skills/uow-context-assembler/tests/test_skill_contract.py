"""Prueba de contrato local del skill (estructura, metadatos, plantillas OKF y gates). Stdlib + PyYAML."""
import json, re, unittest
from pathlib import Path
import yaml

SK = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED = ["SKILL.md", "VERSION", "README.md", "contracts/input.schema.json", "contracts/output.schema.json", "resources/contract.md",
            "resources/orchestration.md", "resources/artifact-standard.md", "resources/STD-OKF-001.md", "resources/STD-HANDOFF-001-v1.0.md",
            "resources/workflow-modes.md", "resources/contracts/common-contract.yaml", "scripts/check_uow_package.py", "assets/artifact.md"]
OKF_KEYS = ["type", "id", "title", "description", "version", "status", "owner", "classification", "tags", "generated", "sources"]


def front(path):
    return yaml.safe_load(path.read_text(encoding="utf8").split("---", 2)[1])


class SkillContract(unittest.TestCase):
    def test_required_files(self):
        for f in REQUIRED:
            self.assertTrue((SK / f).is_file(), f)

    def test_skill_frontmatter_and_metadata(self):
        m = front(SK / "SKILL.md")
        self.assertEqual(m["name"], SK.name)
        self.assertTrue(m["description"])
        v = (SK / "VERSION").read_text(encoding="utf8").strip()
        self.assertRegex(v, SEMVER)
        self.assertEqual(m["metadata"], {"version": v, "author": "COMSATEL", "type": "development"})

    def test_templates_follow_std_okf(self):
        for f in (SK / "templates").glob("*.md"):
            m = front(f)
            for k in OKF_KEYS:
                self.assertIn(k, m, f"{f.name}: falta {k}")
            self.assertEqual(m["status"], "draft", f.name)
            for bad in ("artifact_type", "okf", "kind", "okf_version", "artifact_id", "provenance"):
                self.assertNotIn(bad, m, f"{f.name}: campo no permitido {bad}")
            self.assertIn(m["type"], ("UCX", "UOW", "UCB", "UCM", "UAP", "UWR"), f.name)

    def test_gates_use_policy_format_and_do_not_self_approve(self):
        for f in (SK / "resources/gates").glob("*.yaml"):
            g = yaml.safe_load(f.read_text(encoding="utf8"))
            self.assertIn(g["policy"]["mode"], ("AUTO", "CONDITIONAL_HIL", "MANDATORY_HIL"), f.name)
            self.assertTrue(g["checks"], f.name)
            self.assertTrue(all("id" in c and "evaluator" in c for c in g["checks"]), f.name)
            self.assertFalse(g["policy"]["waiver_allowed"], f.name)

    def test_templates_do_not_declare_gate_decision(self):
        for f in (SK / "templates").glob("gate-report.yaml"):
            g = yaml.safe_load(f.read_text(encoding="utf8"))
            self.assertNotIn("decision", g)
            self.assertIn("checks", g)

    def test_no_external_links(self):
        for f in SK.rglob("*.md"):
            self.assertNotRegex(f.read_text(encoding="utf8"), r"\]\(\.\./", f.name)

    def test_contracts_are_valid_json_and_yaml(self):
        for f in (SK / "contracts").glob("*.json"):
            json.loads(f.read_text(encoding="utf8"))
        for f in (SK / "resources").rglob("*.yaml"):
            yaml.safe_load(f.read_text(encoding="utf8"))

    def test_output_schema_forbids_self_approval(self):
        if SK.name == "uow-orchestrator":
            return
        s = json.loads((SK / "contracts/output.schema.json").read_text(encoding="utf8"))
        self.assertIn("gate_proposal", s["required"])
        self.assertTrue(s.get("not"))


if __name__ == "__main__":
    unittest.main()
