import sys, tempfile, unittest
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import quality_metrics as q  # noqa: E402


def md(meta):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n"


class Metrics(unittest.TestCase):
    def build(self, execs):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        root = Path(t.name); d = root / "design"; e = root / "eng"
        for p in (d / "TC", d / "TDR", e / "executions", e / "evidence"):
            p.mkdir(parents=True)
        (d / "coverage-matrix.yaml").write_text(yaml.safe_dump({"risks": [{"risk": "RISK-001", "critical": True}]}), encoding="utf8")
        (d / "TC/TC-001.md").write_text(md({"id": "TC-001", "surface": "API", "automation_status": "AUTOMATED", "risks": ["RISK-001"], "user_story": "US-1"}), encoding="utf8")
        (d / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"]}), encoding="utf8")
        (e / "test-data-manifest.yaml").write_text(yaml.safe_dump({"test_data": [{"id": "TDA-001", "tdr_ref": "TDR-001", "readiness": "READY"}]}), encoding="utf8")
        (e / "evidence/EVD-001.md").write_text(md({"id": "EVD-001"}), encoding="utf8")
        for i, ex in enumerate(execs, 1):
            meta = {"id": f"EXEC-{i:03d}", "testcase_ref": "TC-001", "environment": "QA", "result": "PASSED", "evidence_refs": ["EVD-001"],
                    "started_at": "2026-10-26T10:00:00-05:00", "finished_at": "2026-10-26T10:00:30-05:00", "ci": {}}
            meta.update(ex)
            (e / "executions" / f"EXEC-{i:03d}.md").write_text(md(meta), encoding="utf8")
        return e, d

    def test_segmentation_by_mode_and_pipeline(self):
        e, d = self.build([{"execution_mode": "MANUAL"}, {"execution_mode": "AUTOMATED_STANDALONE"},
                           {"execution_mode": "AUTOMATED_CICD", "ci": {"pipeline_id": 77}}])
        m = q.compute(e, d)
        self.assertEqual(set(m["segments"]["execution_mode"]), set(q.MODES))
        self.assertEqual(m["segments"]["pipeline"]["77"]["executions"], 1)
        self.assertEqual(m["segments"]["risk"]["RISK-001"]["executions"], 3)
        self.assertEqual(m["global"]["cicd_execution_rate"], 0.333)
        self.assertEqual(m["global"]["critical_risk_coverage"], 1.0)
        self.assertEqual(m["global"]["tdr_tda_readiness"], 1.0)
        self.assertEqual(m["global"]["automation_coverage"], 1.0)

    def test_pipeline_failure_is_not_a_functional_failure(self):
        e, d = self.build([{"execution_mode": "AUTOMATED_CICD", "result": "ERROR", "failure_class": "PIPELINE"},
                           {"execution_mode": "AUTOMATED_CICD", "result": "FAILED", "failure_class": "FUNCTIONAL"}])
        g = q.compute(e, d)["global"]
        self.assertEqual((g["functional_failures"], g["non_functional_failures"], g["unclassified_failures"]), (1, 1, 0))
        self.assertEqual(g["defect_detection_by_mode"]["AUTOMATED_CICD"], 1)

    def test_unclassified_failure_and_unknown_mode_fail_the_checks(self):
        e, d = self.build([{"execution_mode": "MANUAL", "result": "FAILED"}, {"execution_mode": "OTHER"}])
        r = {c["id"]: c["result"] for c in q.checks(e, d)}
        self.assertEqual(r, {"results-segmented-by-mode": "FAIL", "failures-classified-by-cause": "FAIL"})

    def test_flaky_and_rerun_rate(self):
        e, d = self.build([{"execution_mode": "AUTOMATED_CICD", "result": "FAILED", "failure_class": "FUNCTIONAL", "ci": {"commit_sha": "a1"}},
                           {"execution_mode": "AUTOMATED_CICD", "rerun_of": "EXEC-001", "ci": {"commit_sha": "a1"}}])
        g = q.compute(e, d)["global"]
        self.assertEqual(g["flaky_tests"], ["TC-001"])
        self.assertEqual(g["rerun_rate"], 0.5)

    def test_cli_error_on_missing_dirs(self):
        self.assertEqual(q.main(["--pack", "/no/existe", "--design-pack", "/no/existe"]), 2)


if __name__ == "__main__":
    unittest.main()
