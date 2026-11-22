"""Pruebas del plugin qa-design (instrucciones de ajuste 2026-10-26): estructura, metadata, Test Data, modos de ejecución y GitLab CI/CD."""
import importlib.util, json, re, tempfile, unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SK = ROOT / "skills"
SKILLS = ["qa-feature-analyzer", "qa-test-design", "qa-test-design-reviewer", "qa-agentic-test-engineer",
          "qa-agentic-test-reviewer", "qa-quality-intelligence", "qa-sdlc-orchestrator"]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PLUGIN = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf8"))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def front(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf8").split("---", 2)[1])


def contract(skill="qa-test-design", name="common-contract.yaml"):
    return yaml.safe_load((SK / skill / "resources/contracts" / name).read_text(encoding="utf8"))


eng = load(SK / "qa-agentic-test-engineer/scripts/check_test_engineering.py", "eng")
design = load(SK / "qa-test-design/scripts/check_test_design.py", "design")
publish = load(SK / "qa-sdlc-orchestrator/scripts/publish_testcase_issues.py", "publish")


def md(meta, body=""):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n" + body


class Metadata(unittest.TestCase):
    def test_01_exactly_seven_skills(self):
        self.assertEqual(sorted(p.name for p in SK.iterdir() if p.is_dir()), sorted(SKILLS))

    def test_02_to_05_homogeneous_metadata(self):
        for s in SKILLS:
            m = front(SK / s / "SKILL.md")["metadata"]
            self.assertEqual(m["version"], PLUGIN["version"], s)
            self.assertEqual(m["author"], "COMSATEL", s)
            self.assertEqual(m["type"], "qa", s)
            self.assertRegex(m["version"], SEMVER, s)
            self.assertEqual((SK / s / "VERSION").read_text(encoding="utf8").strip(), PLUGIN["version"], s)

    def test_22_version_is_consistent_everywhere(self):
        self.assertRegex(PLUGIN["version"], SEMVER)
        for f in SK.rglob("templates/*.md"):
            by = front(f)["generated"]["by"]
            self.assertTrue(by.endswith("/" + PLUGIN["version"]), f"{f.name}: {by}")
        mc = contract(name="skill-metadata-contract.yaml")
        self.assertEqual(mc["qa_pack_constraints"]["type"], "qa")
        self.assertEqual(mc["validation"]["type_not_qa"], "BLOCKED")
        self.assertEqual(mc["validation"]["missing_required_metadata"], "BLOCKED")
        self.assertEqual(mc["validation"]["invalid_semver"], "BLOCKED")


class Design(unittest.TestCase):
    def test_06_strategy_and_plan_are_explicit(self):
        t = SK / "qa-test-design/templates"
        self.assertEqual(front(t / "qa-test-strategy.md")["type"], "QTS")
        self.assertEqual(front(t / "qa-test-plan.md")["type"], "QTP")
        s = (t / "qa-test-strategy.md").read_text(encoding="utf8")
        for h in ("Alcance y exclusiones", "Enfoque basado en riesgo", "Niveles y tipos de prueba", "Técnicas de diseño", "Estrategia de automatización",
                  "Estrategia de entorno", "Estrategia de datos de prueba", "Criterios de entrada y salida", "Restricciones", "Supuestos", "Provenance"):
            self.assertIn("## " + h, s)
        p = (t / "qa-test-plan.md").read_text(encoding="utf8")
        for h in ("Alcance", "Actividades", "Prioridades", "Entornos", "Datos de prueba (TDR)", "Dependencias", "Criterios de entrada y salida", "Provenance"):
            self.assertIn("## " + h, p)

    def test_07_08_test_data_plan_tdr_tda_defined(self):
        self.assertEqual(front(SK / "qa-test-design/templates/test-data-plan.md")["type"], "QTD")
        self.assertEqual(front(SK / "qa-test-design/templates/TDR-OKF.md")["type"], "TDR")
        self.assertEqual(front(SK / "qa-agentic-test-engineer/templates/TDA-OKF.md")["type"], "TDA")
        self.assertEqual(contract()["test_data_entities"], ["TDR", "TDA"])
        for s in SKILLS:
            self.assertEqual(contract(s)["test_data_entities"], ["TDR", "TDA"], s)
        self.assertIn("test-data-plan.md", contract(name="qa-pack-contracts.yaml")["packs"]["QTD"]["required_artifacts"])

    def test_09_10_11_traceability_and_cardinality(self):
        c = contract()
        self.assertEqual(c["cardinality"]["TSN_to_TC"], "1:N")
        self.assertEqual(c["cardinality"]["TC_to_AT"], "1:0..N")
        self.assertEqual(c["cardinality"]["TC_to_TDR"], "1:N")
        self.assertIn("TC → TDR → TDA → EXEC → EVD", c["traceability_test_data"]["forward"])
        self.assertIn("TDA → TDR → TC → TSN → RISK → US → DSP", c["traceability_test_data"]["backward"])
        tc = front(SK / "qa-test-design/templates/TestCase-OKF.md")
        self.assertIn("tdr_refs", tc)
        self.assertIn("automation_status", tc)
        self.assertNotIn("execution", tc)
        self.assertIn("tdr_ref", front(SK / "qa-agentic-test-engineer/templates/TDA-OKF.md"))

    def test_20_unauthorized_real_pii_blocks_design(self):
        self.assertIn("test-data-safe", design.PROFILE["design"])
        self.assertNotIn("REAL", design.PII)
        self.assertIn("REAL_AUTHORIZED", design.PII)


class Engineering(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        r = Path(t.name); self.d = r / "d"; self.e = r / "e"
        for p in (self.d / "TC", self.d / "TDR", self.e / "executions", self.e / "automated-tests", self.e / "evidence", self.e / "cicd"):
            p.mkdir(parents=True)
        (self.d / "TC/TC-001.md").write_text(md({"id": "TC-001", "tdr_refs": ["TDR-001"]}), encoding="utf8")
        (self.d / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "pii": "NONE"}), encoding="utf8")
        (self.e / "evidence/EVD-001.md").write_text(md({"id": "EVD-001"}), encoding="utf8")
        (self.e / "cicd/ci-test-execution.yaml").write_text("provider: GITLAB\n", encoding="utf8")
        (self.e / "automated-tests/AT-001.md").write_text(md({"id": "AT-001", "testcase_ref": "TC-001"}), encoding="utf8")
        self.manifest([{"id": "TDA-001", "tdr_ref": "TDR-001", "testcase_refs": ["TC-001"], "readiness": "READY"}])

    def manifest(self, tdas, exceptions=()):
        (self.e / "test-data-manifest.yaml").write_text(yaml.safe_dump({"test_data": tdas, "exceptions": list(exceptions)}), encoding="utf8")

    def put(self, eid, **over):
        m = {"id": eid, "testcase_ref": "TC-001", "environment": "QA", "executor": "x", "result": "PASSED", "oracle_evaluated": True,
             "started_at": "2026-10-26T10:00:00-05:00", "finished_at": "2026-10-26T10:01:00-05:00", "evidence_refs": ["EVD-001"],
             "runtime": {}, "ci": {}}
        m.update(over)
        (self.e / "executions" / f"{eid}.md").write_text(md(m), encoding="utf8")

    def res(self):
        return {c["id"]: c["result"] for c in eng.checks(self.e, self.d, "engineering")}

    def test_12_at_never_from_tsn(self):
        (self.e / "automated-tests/AT-009.md").write_text(md({"id": "AT-009", "testcase_ref": "TSN-001"}), encoding="utf8")
        self.assertEqual(self.res()["at-references-approved-tc"], "FAIL")
        self.assertEqual(contract()["rules"]["at_from_tsn"], "forbidden")

    def test_13_manual_needs_no_at(self):
        st, why = eng.exec_readiness({"execution_mode": "MANUAL", "testcase_ref": "TC-001"}, {"TC-001": {"tdr_refs": ["TDR-001"]}},
                                     {"TDR-001": {}}, [{"tdr_ref": "TDR-001", "readiness": "READY"}], set(), {})
        self.assertEqual((st, why), ("READY", []))

    def test_14_15_automated_modes_require_at(self):
        for mode in ("AUTOMATED_STANDALONE", "AUTOMATED_CICD"):
            st, why = eng.exec_readiness({"execution_mode": mode, "testcase_ref": "TC-001"}, {"TC-001": {"data_required": False}}, {}, [], set(), {})
            self.assertEqual(st, "BLOCKED", mode)
            self.assertTrue(any("AT" in w for w in why), mode)

    def test_16_cicd_supports_gitlab_pipeline_and_job_provenance(self):
        g = contract("qa-sdlc-orchestrator", "gitlab-testcase-contract.yaml")["gitlab_cicd_execution"]
        self.assertEqual(g["provider"], "GITLAB")
        for k in ("pipeline_id", "pipeline_url", "job_id", "job_name", "commit_sha"):
            self.assertIn(k, g["exec_fields"])
        ci = front(SK / "qa-agentic-test-engineer/templates/Execution-OKF.md")["ci"]
        for k in ("provider", "pipeline_id", "job_id", "job_name", "commit_sha"):
            self.assertIn(k, ci)
        self.put("EXEC-001", execution_mode="AUTOMATED_CICD", at_ref="AT-001", ci={"provider": "GITLAB", "pipeline_id": 5, "job_id": 9, "commit_sha": "abc"})
        self.assertEqual(self.res()["cicd-provenance-complete"], "PASS")
        self.put("EXEC-001", execution_mode="AUTOMATED_CICD", at_ref="AT-001", ci={"provider": "GITLAB", "pipeline_id": 5})
        self.assertEqual(self.res()["cicd-provenance-complete"], "FAIL")

    def test_17_rerun_creates_new_exec_and_keeps_history(self):
        self.put("EXEC-001", execution_mode="MANUAL", result="FAILED", failure_class="FUNCTIONAL")
        self.put("EXEC-002", execution_mode="MANUAL", rerun_of="EXEC-001")
        self.assertEqual(self.res()["execution-mode-requirements"], "PASS")
        self.assertTrue((self.e / "executions/EXEC-001.md").exists() and (self.e / "executions/EXEC-002.md").exists())
        self.put("EXEC-002", execution_mode="MANUAL", rerun_of="EXEC-002")
        self.assertEqual(self.res()["execution-mode-requirements"], "FAIL")

    def test_18_missing_test_data_blocks_execution(self):
        self.manifest([])
        self.put("EXEC-001", execution_mode="MANUAL")
        self.assertEqual(self.res()["test-data-ready"], "FAIL")

    def test_19_secrets_are_not_persisted(self):
        (self.e / "test-data-notes.md").write_text("password: Sup3rSecret99\n", encoding="utf8")
        self.assertEqual(self.res()["no-secrets-or-scope-drift"], "FAIL")
        self.assertIn("never persist", contract()["rules"]["secrets"] + " never persist")

    def test_20_unauthorized_real_pii_blocks_engineering(self):
        self.manifest([{"id": "TDA-001", "tdr_ref": "TDR-001", "testcase_refs": ["TC-001"], "readiness": "READY", "contains_pii": True}])
        self.assertEqual(self.res()["no-unauthorized-pii"], "FAIL")


class Publication(unittest.TestCase):
    def test_21_only_tc_is_published_as_gitlab_testcase(self):
        base = {"approved": True, "testcase_title": "t", "scenario_refs": ["TSN-1"], "kb_local_path": "p", "kb_gitlab_url": "u"}
        for bad in ("TSN-001", "TDR-001", "TDA-001", "AT-001", "EXEC-001", "EVD-001"):
            with self.assertRaises(ValueError, msg=bad):
                publish.validate_case({**base, "testcase_id": bad})
        self.assertEqual(publish.validate_case({**base, "testcase_id": "TC-001"})["testcase_id"], "TC-001")
        forbidden = " ".join(contract("qa-sdlc-orchestrator", "gitlab-testcase-contract.yaml")["gitlab_testcase_issue"]["forbidden"])
        for e in ("TSN", "TDR", "TDA", "AT", "EXEC", "EVD"):
            self.assertIn(e, forbidden)


class Modes(unittest.TestCase):
    def test_execution_modes_and_automation_status_in_every_contract_copy(self):
        for s in SKILLS:
            c = contract(s)
            self.assertEqual(c["execution_modes"], ["MANUAL", "AUTOMATED_STANDALONE", "AUTOMATED_CICD"], s)
            self.assertEqual(c["automation_status"], ["MANUAL_ONLY", "AUTOMATION_CANDIDATE", "PARTIALLY_AUTOMATED", "AUTOMATED"], s)
            self.assertEqual(c["scheduling_modes"], ["SEQUENTIAL", "PARALLEL_ELIGIBLE"], s)
            self.assertEqual(c["workflow_modes"], ["GREENFIELD", "BROWNFIELD", "EVOLUTION"], s)

    def test_gates_distinguish_modes(self):
        g = yaml.safe_load((SK / "qa-agentic-test-reviewer/resources/gates/TEST_ENGINEERING_REVIEW_GATE.yaml").read_text(encoding="utf8"))
        ids = {c["id"] for c in g["checks"]}
        self.assertTrue({"execution-mode-explicit", "manual-execution-evidence-complete", "standalone-execution-reproducible", "cicd-provenance-verified"} <= ids)

    def test_no_dedicated_gitlab_runner_skill(self):
        self.assertFalse(any("gitlab" in s.lower() or "runner" in s.lower() for s in SKILLS))


class Plantillas(unittest.TestCase):
    """Registros operativos (gate-report) viven en la carpeta del orquestador; cada skill guarda sus plantillas OKF en skills/<skill>/templates/."""
    ORCH = "qa-sdlc-orchestrator"

    def test_raiz_sin_templates(self):
        self.assertFalse((ROOT / "templates").exists())

    def test_gate_report_en_orquestador(self):
        self.assertTrue((SK / self.ORCH / "templates/gate-report.yaml").is_file())
        for skill in sorted(p for p in SK.iterdir() if p.is_dir() and p.name != self.ORCH):
            self.assertFalse((skill / "templates" / "gate-report.yaml").exists(), f"{skill.name}: gate-report es registro del orquestador")

    def test_gate_report_sin_decision_de_gate(self):
        g = yaml.safe_load((SK / self.ORCH / "templates/gate-report.yaml").read_text(encoding="utf8"))
        self.assertNotIn("decision", g)
        self.assertTrue(g["proposal_only"])


if __name__ == "__main__":
    unittest.main()


class DocumentacionVsPolitica(unittest.TestCase):
    def test_tabla_de_gates_coincide_con_gate_policies(self):
        # D-14 (evidencia 3): los checks de DOCUMENTACION.md son los de gate-policies.yaml
        pol = yaml.safe_load((SK / "qa-sdlc-orchestrator/resources/gate-policies.yaml").read_text(encoding="utf8"))["gates"]
        doc = (ROOT / "DOCUMENTACION.md").read_text(encoding="utf8")
        for gate, cfg in pol.items():
            fila = next(l for l in doc.splitlines() if l.startswith(f"| `{gate}` |"))
            self.assertEqual(re.findall(r"`([a-z0-9-]+)`", fila.split(" | ")[-1]), [c["id"] for c in cfg["checks"]], gate)

    def test_docstrings_de_checks_no_prometen_checks_que_el_orquestador_no_agrega(self):
        for f in SK.glob("*/scripts/check_test_*.py"):
            self.assertNotIn("el orquestador añade los checks", f.read_text(encoding="utf8"), f)


class Regresion(unittest.TestCase):
    def test_qts_y_qtp_tienen_secciones_de_regresion(self):
        # D-26a: criterios de selección por impacto y pruebas de caracterización en QTS; selección en QTP
        tpl = SK / "qa-test-design/templates"
        qts = (tpl / "qa-test-strategy.md").read_text(encoding="utf8")
        qtp = (tpl / "qa-test-plan.md").read_text(encoding="utf8")
        self.assertIn("## Estrategia de regresión", qts)
        self.assertIn("caracterización", qts)
        self.assertIn("IMP", qts)
        self.assertIn("## Selección de regresión", qtp)
        self.assertIn("Estrategia de regresión", (SK / "qa-test-design/SKILL.md").read_text(encoding="utf8"))
