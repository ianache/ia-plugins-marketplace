import sys, tempfile, unittest
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_test_design as c  # noqa: E402


def md(meta, body=""):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n" + body


TDR_OK = "## Datos requeridos\n- d\n## Aislamiento y limpieza\n- a\n## Privacidad y masking\n- m\n"
TC_OK = "## Precondiciones\n- p\n## Datos de prueba\n- d\n## Pasos\n1. x\n## Resultado esperado (oracle)\n- o\n"


class Pack(unittest.TestCase):
    def build(self, **over):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        p = Path(t.name) / "pack"; (p / "TSN").mkdir(parents=True); (p / "TC").mkdir(); (p / "TDR").mkdir()
        (p / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "source_type": "SYNTHETIC", "pii": "NONE"}, TDR_OK), encoding="utf8")
        for f in ("qa-test-strategy.md", "qa-test-plan.md", "test-prioritization.md", "test-data-plan.md"):
            (p / f).write_text("x", encoding="utf8")
        (p / "TSN/TSN-001.md").write_text(md({"id": "TSN-001", "test_cases": ["TC-001"]}), encoding="utf8")
        (p / "TC/TC-001.md").write_text(md({"id": "TC-001", "tsn": "TSN-001", "surface": "API", "priority": "P1", "automation_status": "MANUAL_ONLY", "tdr_refs": ["TDR-001"]}, TC_OK), encoding="utf8")
        cm = {"risks": [{"risk": "RISK-001", "critical": True, "tsn": ["TSN-001"], "surfaces": ["API"]}],
              "test_cases": [{"id": "TC-001", "readiness": "READY"}]}
        tr = {"traceability": [{"dsp_ref": "DSP-1@1", "requirement_ref": "US-1", "risk_refs": ["RISK-001"],
                                "scenario_refs": ["TSN-001"], "testcase_refs": ["TC-001"]}]}
        cm.update(over.get("cm", {})); tr.update(over.get("tr", {}))
        (p / "coverage-matrix.yaml").write_text(yaml.safe_dump(cm), encoding="utf8")
        (p / "requirements-test-traceability.yaml").write_text(yaml.safe_dump(tr), encoding="utf8")
        return p

    def result(self, p, profile="design"):
        return {x["id"]: x["result"] for x in c.checks(p, [], profile)}

    def test_valid_pack_passes_all(self):
        self.assertEqual(set(self.result(self.build()).values()), {"PASS"})
        self.assertEqual(set(self.result(self.build(), "review").values()), {"PASS"})

    def test_critical_risk_without_tsn(self):
        p = self.build(cm={"risks": [{"risk": "RISK-001", "critical": True, "tsn": [], "surfaces": ["API"]}]})
        self.assertEqual(self.result(p)["critical-risk-has-tsn"], "FAIL")
        self.assertEqual(self.result(p, "review")["no-critical-risk-uncovered"], "FAIL")

    def test_tsn_without_tc(self):
        p = self.build()
        (p / "TSN/TSN-002.md").write_text(md({"id": "TSN-002", "test_cases": []}), encoding="utf8")
        self.assertEqual(self.result(p)["tsn-has-tc"], "FAIL")

    def test_ready_tc_without_oracle(self):
        p = self.build()
        (p / "TC/TC-001.md").write_text(md({"id": "TC-001", "tsn": "TSN-001", "surface": "API", "priority": "P1"},
                                           "## Precondiciones\n- p\n## Datos de prueba\n- d\n## Resultado esperado (oracle)\n\n"), encoding="utf8")
        self.assertEqual(self.result(p)["approved-tc-has-oracle-and-data"], "FAIL")

    def test_pending_clarification_in_scope_fails_unless_deferred_with_decision(self):
        blocked = {"test_cases": [{"id": "TC-001", "readiness": "READY"}, {"id": "TC-009", "readiness": "BLOCKED_CLARIFICATION"}]}
        self.assertEqual(self.result(self.build(cm=blocked))["no-pending-clarification-in-scope"], "FAIL")
        blocked["deferred_items"] = [{"id": "TC-009"}]  # sin decisión humana
        self.assertEqual(self.result(self.build(cm=blocked))["no-pending-clarification-in-scope"], "FAIL")
        blocked["deferred_items"] = [{"id": "TC-009", "decision_ref": "HI-004"}]
        self.assertEqual(self.result(self.build(cm=blocked))["no-pending-clarification-in-scope"], "PASS")

    def test_tc_without_traceability(self):
        p = self.build()
        (p / "TC/TC-002.md").write_text(md({"id": "TC-002", "tsn": "TSN-001", "surface": "API", "priority": "P1"}, TC_OK), encoding="utf8")
        self.assertEqual(self.result(p)["traceability-complete"], "FAIL")

    def test_critical_surface_gap(self):
        p = self.build(cm={"risks": [{"risk": "RISK-001", "critical": True, "tsn": ["TSN-001"], "surfaces": ["API", "WEB"]}]})
        self.assertEqual(self.result(p)["critical-surfaces-covered"], "FAIL")

    def test_missing_priority_or_strategy(self):
        p = self.build()
        (p / "qa-test-plan.md").unlink()
        self.assertEqual(self.result(p)["coverage-prioritization-defined"], "FAIL")

    def tc(self, p, **extra):
        meta = {"id": "TC-001", "tsn": "TSN-001", "surface": "API", "priority": "P1", "automation_status": "MANUAL_ONLY", "tdr_refs": ["TDR-001"]}
        meta.update(extra)
        for k in [k for k, v in meta.items() if v is None]:
            del meta[k]
        (p / "TC/TC-001.md").write_text(md(meta, TC_OK), encoding="utf8")

    def test_tc_without_tdr_fails_unless_data_not_required(self):
        p = self.build(); self.tc(p, tdr_refs=None)
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "FAIL")
        self.assertEqual(self.result(p, "review")["no-tc-without-test-data-requirement"], "FAIL")
        self.tc(p, tdr_refs=None, data_required=False)
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "PASS")

    def test_missing_test_data_plan_or_dangling_tdr(self):
        p = self.build(); (p / "test-data-plan.md").unlink()
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "FAIL")
        p = self.build(); self.tc(p, tdr_refs=["TDR-999"])
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "FAIL")

    def test_legacy_execution_field_and_bad_automation_status(self):
        p = self.build(); self.tc(p, execution="manual")
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "FAIL")
        p = self.build(); self.tc(p, automation_status="MAYBE")
        self.assertEqual(self.result(p)["test-data-requirements-defined"], "FAIL")

    def test_unauthorized_real_pii_and_secrets_block(self):
        p = self.build()
        (p / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "source_type": "SYNTHETIC", "pii": "REAL"}, TDR_OK), encoding="utf8")
        self.assertEqual(self.result(p)["test-data-safe"], "FAIL")
        (p / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "source_type": "SYNTHETIC", "pii": "REAL_AUTHORIZED"}, TDR_OK), encoding="utf8")
        self.assertEqual(self.result(p)["test-data-safe"], "FAIL")
        (p / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "source_type": "SYNTHETIC", "pii": "REAL_AUTHORIZED", "decision_ref": "HI-009"}, TDR_OK), encoding="utf8")
        self.assertEqual(self.result(p)["test-data-safe"], "PASS")
        (p / "test-data-plan.md").write_text("password: Sup3rSecret99\n", encoding="utf8")
        self.assertEqual(self.result(p)["test-data-safe"], "FAIL")
        (p / "test-data-plan.md").write_text("password: ref:vault/qa/db\n", encoding="utf8")
        self.assertEqual(self.result(p)["test-data-safe"], "PASS")

    def test_cli_error_on_missing_files(self):
        self.assertEqual(c.main(["--pack", "/no/existe"]), 2)


if __name__ == "__main__":
    unittest.main()
