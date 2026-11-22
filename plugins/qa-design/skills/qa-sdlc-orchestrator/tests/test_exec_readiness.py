import sys, tempfile, unittest
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import exec_readiness as x  # noqa: E402


def md(meta):
    return "---\n" + yaml.safe_dump(meta) + "---\n"


class Readiness(unittest.TestCase):
    def build(self, tdas, exceptions=(), execs=None):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        r = Path(t.name); d = r / "d"; e = r / "e"
        for p in (d / "TC", d / "TDR", e / "executions", e / "automated-tests"):
            p.mkdir(parents=True)
        (d / "TC/TC-001.md").write_text(md({"id": "TC-001", "tdr_refs": ["TDR-001"]}), encoding="utf8")
        (d / "TDR/TDR-001.md").write_text(md({"id": "TDR-001", "test_cases": ["TC-001"]}), encoding="utf8")
        (e / "automated-tests/AT-001.md").write_text(md({"id": "AT-001", "testcase_ref": "TC-001"}), encoding="utf8")
        (e / "test-data-manifest.yaml").write_text(yaml.safe_dump({"test_data": tdas, "exceptions": list(exceptions)}), encoding="utf8")
        for ex in execs or [{"id": "EXEC-001", "execution_mode": "AUTOMATED_STANDALONE", "testcase_ref": "TC-001", "at_ref": "AT-001"}]:
            (e / "executions" / f"{ex['id']}.md").write_text(md(ex), encoding="utf8")
        return e, d

    def test_missing_test_data_blocks_data_dependent_exec(self):
        e, d = self.build([])
        self.assertEqual(x.evaluate(e, d)["EXEC-001"]["readiness"], "BLOCKED")
        self.assertEqual(x.main(["--pack", str(e), "--design-pack", str(d)]), 1)

    def test_ready_with_tda_or_approved_exception(self):
        e, d = self.build([{"id": "TDA-001", "tdr_ref": "TDR-001", "readiness": "READY"}])
        self.assertEqual(x.evaluate(e, d)["EXEC-001"]["readiness"], "READY")
        e, d = self.build([], [{"tdr_ref": "TDR-001", "decision_ref": "HI-001"}])
        self.assertEqual(x.evaluate(e, d)["EXEC-001"]["readiness"], "READY")
        e, d = self.build([], [{"tdr_ref": "TDR-001"}])
        self.assertEqual(x.evaluate(e, d)["EXEC-001"]["readiness"], "BLOCKED")

    def test_automated_modes_need_at_and_manual_does_not(self):
        tda = [{"id": "TDA-001", "tdr_ref": "TDR-001", "readiness": "READY"}]
        e, d = self.build(tda, execs=[{"id": "EXEC-001", "execution_mode": "MANUAL", "testcase_ref": "TC-001"},
                                      {"id": "EXEC-002", "execution_mode": "AUTOMATED_CICD", "testcase_ref": "TC-001"}])
        out = x.evaluate(e, d)
        self.assertEqual(out["EXEC-001"]["readiness"], "READY")
        self.assertEqual(out["EXEC-002"]["readiness"], "BLOCKED")

    def test_rerun_keeps_both_execs(self):
        tda = [{"id": "TDA-001", "tdr_ref": "TDR-001", "readiness": "READY"}]
        e, d = self.build(tda, execs=[{"id": "EXEC-001", "execution_mode": "MANUAL", "testcase_ref": "TC-001"},
                                      {"id": "EXEC-002", "execution_mode": "MANUAL", "testcase_ref": "TC-001", "rerun_of": "EXEC-001"}])
        self.assertEqual(set(x.evaluate(e, d)), {"EXEC-001", "EXEC-002"})

    def test_cli_error_on_missing_dirs(self):
        self.assertEqual(x.main(["--pack", "/no/existe", "--design-pack", "/no/existe"]), 2)


if __name__ == "__main__":
    unittest.main()
