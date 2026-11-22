import sys, tempfile, unittest
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_test_engineering as c  # noqa: E402


def md(meta, body=""):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n" + body


def ci(**over):
    d = {"provider": "GITLAB", "pipeline_id": 101, "pipeline_url": "https://gitlab.example/p/101", "job_id": 7, "job_name": "api-tests",
         "commit_sha": "abc123", "ref": "main"}
    d.update(over)
    return d


class Pack(unittest.TestCase):
    def build(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        root = Path(t.name); self.d = root / "design"; self.e = root / "eng"
        for sub in ("TC", "TDR"):
            (self.d / sub).mkdir(parents=True)
        for sub in ("automated-tests", "executions", "evidence", "cicd"):
            (self.e / sub).mkdir(parents=True)
        (self.d / "coverage-matrix.yaml").write_text(yaml.safe_dump({"test_cases": [{"id": "TC-001", "readiness": "READY"}]}), encoding="utf8")
        (self.d / "TC/TC-001.md").write_text(md({"id": "TC-001", "tsn": "TSN-001", "automation_status": "AUTOMATED", "tdr_refs": ["TDR-001"]}), encoding="utf8")
        (self.d / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"], "source_type": "SYNTHETIC", "pii": "NONE"}), encoding="utf8")
        self.manifest()
        (self.e / "automated-tests/AT-001.md").write_text(md({"id": "AT-001", "testcase_ref": "TC-001", "tda_refs": ["TDA-001"]}), encoding="utf8")
        (self.e / "evidence/EVD-001.md").write_text(md({"id": "EVD-001", "exec_ref": "EXEC-001"}), encoding="utf8")
        (self.e / "cicd/ci-test-execution.yaml").write_text("provider: GITLAB\n", encoding="utf8")
        self.put("EXEC-001", execution_mode="MANUAL", executor="qa.analyst")
        self.put("EXEC-002", execution_mode="AUTOMATED_STANDALONE", at_ref="AT-001", runtime={"name": "pytest", "version": "8.4"})
        self.put("EXEC-003", execution_mode="AUTOMATED_CICD", at_ref="AT-001", ci=ci())
        return self

    def manifest(self, **over):
        m = {"test_data": [{"id": "TDA-001", "tdr_ref": "TDR-001", "testcase_refs": ["TC-001"], "readiness": "READY",
                            "contains_pii": False, "contains_secrets": False}], "exceptions": []}
        m.update(over)
        (self.e / "test-data-manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf8")

    def put(self, eid, **over):
        meta = {"id": eid, "testcase_ref": "TC-001", "at_ref": None, "tda_refs": ["TDA-001"], "environment": "QA", "executor": "runner",
                "runtime": {"name": None, "version": None}, "result": "PASSED", "oracle_evaluated": True,
                "started_at": "2026-10-26T10:00:00-05:00", "finished_at": "2026-10-26T10:01:00-05:00",
                "rerun_of": None, "failure_class": None, "ci": {}, "evidence_refs": ["EVD-001"]}
        meta.update(over)
        (self.e / "executions" / f"{eid}.md").write_text(md(meta), encoding="utf8")

    def res(self, profile="engineering"):
        return {x["id"]: x["result"] for x in c.checks(self.e, self.d, profile)}


class EngineeringPack(Pack):
    def test_valid_pack_passes_both_profiles(self):
        self.build()
        self.assertEqual(set(self.res().values()), {"PASS"}, c.checks(self.e, self.d, "engineering"))
        self.assertEqual(set(self.res("review").values()), {"PASS"}, c.checks(self.e, self.d, "review"))

    def test_manual_does_not_require_at(self):
        self.build()
        for n in (2, 3):
            (self.e / f"executions/EXEC-00{n}.md").unlink()
        (self.e / "automated-tests/AT-001.md").unlink()
        self.assertEqual(self.res()["execution-mode-requirements"], "PASS")
        self.assertEqual(self.res()["at-references-approved-tc"], "PASS")

    def test_standalone_and_cicd_require_at(self):
        self.build(); self.put("EXEC-002", execution_mode="AUTOMATED_STANDALONE", runtime={"name": "pytest", "version": "8"})
        self.assertEqual(self.res()["execution-mode-requirements"], "FAIL")
        self.build(); self.put("EXEC-003", execution_mode="AUTOMATED_CICD", ci=ci())
        self.assertEqual(self.res()["cicd-provenance-complete"], "FAIL")

    def test_at_is_never_generated_from_tsn(self):
        self.build()
        (self.e / "automated-tests/AT-002.md").write_text(md({"id": "AT-002", "testcase_ref": "TSN-001"}), encoding="utf8")
        self.assertEqual(self.res()["at-references-approved-tc"], "FAIL")

    def test_cicd_gitlab_pipeline_job_provenance(self):
        self.build(); self.put("EXEC-003", execution_mode="AUTOMATED_CICD", at_ref="AT-001", ci=ci(pipeline_id=None))
        self.assertEqual(self.res()["cicd-provenance-complete"], "FAIL")
        self.assertEqual(self.res("review")["cicd-provenance-verified"], "FAIL")
        self.build(); self.put("EXEC-003", execution_mode="AUTOMATED_CICD", at_ref="AT-001", ci=ci(provider="JENKINS"))
        self.assertEqual(self.res()["cicd-provenance-complete"], "FAIL")
        self.build(); (self.e / "cicd/ci-test-execution.yaml").unlink()
        self.assertEqual(self.res()["cicd-provenance-complete"], "FAIL")

    def test_missing_test_data_blocks_execution(self):
        self.build(); self.manifest(test_data=[])
        self.assertEqual(self.res()["test-data-ready"], "FAIL")
        self.manifest(test_data=[], exceptions=[{"tdr_ref": "TDR-001"}])   # sin decisión humana
        self.assertEqual(self.res()["test-data-ready"], "FAIL")
        self.manifest(test_data=[], exceptions=[{"tdr_ref": "TDR-001", "decision_ref": "HI-005"}])
        self.assertEqual(self.res()["test-data-ready"], "PASS")

    def test_tda_must_trace_to_tdr_and_tc(self):
        self.build()
        self.manifest(test_data=[{"id": "TDA-001", "tdr_ref": "TDR-404", "testcase_refs": ["TC-001"], "readiness": "READY"}])
        self.assertEqual(self.res()["tda-traces-to-tdr-and-tc"], "FAIL")
        self.assertEqual(self.res("review")["test-data-traceable"], "FAIL")

    def test_rerun_creates_new_exec_and_keeps_history(self):
        self.build(); self.put("EXEC-004", execution_mode="MANUAL", rerun_of="EXEC-001")
        self.assertEqual(self.res()["execution-mode-requirements"], "PASS")
        self.assertTrue((self.e / "executions/EXEC-001.md").exists())
        self.put("EXEC-004", execution_mode="MANUAL", rerun_of="EXEC-999")
        self.assertEqual(self.res()["execution-mode-requirements"], "FAIL")
        self.put("EXEC-004", execution_mode="MANUAL", rerun_of="EXEC-004")
        self.assertEqual(self.res()["execution-mode-requirements"], "FAIL")

    def test_failed_exec_needs_failure_class(self):
        self.build(); self.put("EXEC-001", execution_mode="MANUAL", result="FAILED")
        self.assertEqual(self.res()["exec-evaluates-tc-oracle"], "FAIL")
        self.put("EXEC-001", execution_mode="MANUAL", result="FAILED", failure_class="PIPELINE")
        self.assertEqual(self.res()["exec-evaluates-tc-oracle"], "PASS")

    def test_secrets_pii_and_prod_are_blocked(self):
        self.build(); (self.e / "executions/notes.md").write_text("api_key: AbCdEf123456789\n", encoding="utf8")
        self.assertEqual(self.res()["no-secrets-or-scope-drift"], "FAIL")
        self.assertEqual(self.res("review")["security-clean"], "FAIL")
        self.build(); (self.e / "executions/notes.md").write_text("api_key: ref:vault/qa/key\n", encoding="utf8")
        self.assertEqual(self.res()["no-secrets-or-scope-drift"], "PASS")
        self.build(); self.manifest(test_data=[{"id": "TDA-001", "tdr_ref": "TDR-001", "testcase_refs": ["TC-001"], "readiness": "READY", "contains_pii": True}])
        self.assertEqual(self.res()["no-unauthorized-pii"], "FAIL")
        self.build(); self.put("EXEC-001", execution_mode="MANUAL", environment="PROD")
        self.assertEqual(self.res()["no-destructive-or-unauthorized-prod"], "FAIL")
        self.put("EXEC-001", execution_mode="MANUAL", environment="PROD", authorization_ref="HI-010")
        self.assertEqual(self.res()["no-destructive-or-unauthorized-prod"], "PASS")

    def test_exec_readiness_blocks_data_dependent_execution(self):
        tcs = {"TC-001": {"tdr_refs": ["TDR-001"]}}
        tdrs = {"TDR-001": {}}
        ats = {"AT-001": {"testcase_ref": "TC-001"}}
        ex = {"execution_mode": "AUTOMATED_STANDALONE", "testcase_ref": "TC-001", "at_ref": "AT-001"}
        self.assertEqual(c.exec_readiness(ex, tcs, tdrs, [], set(), ats)[0], "BLOCKED")
        ready = [{"tdr_ref": "TDR-001", "readiness": "READY"}]
        self.assertEqual(c.exec_readiness(ex, tcs, tdrs, ready, set(), ats)[0], "READY")
        self.assertEqual(c.exec_readiness(ex, tcs, tdrs, [], {"TDR-001"}, ats)[0], "READY")
        self.assertEqual(c.exec_readiness({**ex, "at_ref": None}, tcs, tdrs, ready, set(), ats)[0], "BLOCKED")
        manual = {"execution_mode": "MANUAL", "testcase_ref": "TC-001"}
        self.assertEqual(c.exec_readiness(manual, tcs, tdrs, ready, set(), {})[0], "READY")

    def test_cli_error_on_missing_pack(self):
        self.assertEqual(c.main(["--pack", "/no/existe", "--design-pack", "/no/existe"]), 2)


if __name__ == "__main__":
    unittest.main()
