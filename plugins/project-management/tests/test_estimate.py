import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
SKILL = PLUGIN / "skills/mgt-backlog-iteration-planner"
spec = importlib.util.spec_from_file_location("estimate", SKILL / "scripts/estimate.py")
est = importlib.util.module_from_spec(spec)
spec.loader.exec_module(est)
COEF = json.loads((SKILL / "assets/estimation-coefficients.json").read_text(encoding="utf-8"))


def story(id_="CL2-US-001", criteria=1, factors=(), oq=0, qa=None, **kw):
    s = {"id": id_, "criteria": criteria, "factors": list(factors), "open_questions": oq, **kw}
    if qa is not None:
        s["qa"] = qa
    return s


def run(stories, **sprint):
    sp = {"working_days": 10}
    sp.update(sprint)
    return est.run({"sprint": sp, "stories": stories}, copy.deepcopy(COEF))


class HumanFormulaV2(unittest.TestCase):
    def test_worked_example_of_the_practice(self):
        # US-036: 5 criterios, factores E y D, sin preguntas: (3 + 2,5 x 5) x 1,4 = 21,7 -> 22 h, talla M, confianza Media
        e = run([story(criteria=5, factors="ED", qa={"manual_tc": 0, "automated_tc": 0, "estimated": False})])["stories"][0]
        self.assertEqual(22, e["dev_human_h"])
        self.assertEqual(("M", "Media"), (e["size"], e["confidence"]))

    def test_rounding_up_to_even_hours_and_sizes(self):
        self.assertEqual(6, run([story(criteria=1)])["stories"][0]["dev_human_h"])      # 5,5 -> 6
        self.assertEqual(8, run([story(criteria=2)])["stories"][0]["dev_human_h"])      # 8 exacto
        self.assertEqual("S", run([story(criteria=3)])["stories"][0]["size"])           # 10,5 -> 12
        self.assertEqual("L", run([story(criteria=12)])["stories"][0]["size"])          # 33 -> 34
        self.assertEqual("XL", run([story(criteria=20)])["stories"][0]["size"])         # 53 -> 54

    def test_open_questions_are_capped_and_confidence_levels(self):
        self.assertEqual(0.15, run([story(oq=9)])["stories"][0]["factor_sum"])
        self.assertEqual("Alta", run([story(oq=3)])["stories"][0]["confidence"])
        self.assertEqual("Baja", run([story(factors="ESV")])["stories"][0]["confidence"])

    def test_xl_and_l_raise_warnings(self):
        w = " ".join(run([story("A", criteria=20), story("B", criteria=12)])["warnings"])
        self.assertIn("A: talla XL", w)
        self.assertIn("B: talla L", w)

    def test_cost_is_time_times_rate(self):
        r = run([story(criteria=5, factors="ED", qa={"manual_tc": 0, "automated_tc": 0, "estimated": False})] * 1)
        t = r["totals"]
        self.assertEqual(22 + 0, t["time_h"])
        self.assertEqual(22 * 30, t["cost_pen"])
        self.assertEqual("S/ 660.00", r["header"]["cost"])
        self.assertEqual("22 h", r["header"]["time"])


class QaAndAgent(unittest.TestCase):
    def test_manual_and_automated_tc_split(self):
        s = run([story(criteria=5, factors="ED", qa={"manual_tc": 4, "automated_tc": 2})])["stories"][0]
        self.assertEqual(3.0, s["qa"]["human_h"])     # 0,5 diseño + 4 x 0,5 + 2 x 0,25
        self.assertEqual(2.0, s["qa"]["agent_h"])     # 1 diseño + 2 x 0,5
        self.assertEqual(25.0, s["human_h"])
        self.assertEqual(24.0, s["agent_h"])          # 22 de desarrollo x razón 1,0 + 2 de QA

    def test_header_totals(self):
        r = run([story(criteria=5, factors="ED", qa={"manual_tc": 4, "automated_tc": 2})])
        self.assertEqual({"cost": "S/ 750.00", "time": "25 h", "time_agent": "24 h"}, {k: r["header"][k] for k in ("cost", "time", "time_agent")})

    def test_agent_cost_prorates_subscription_by_sprint_days(self):
        r = run([story()], fx_pen_per_usd=3.75)
        self.assertEqual(11.36, r["totals"]["cost_agent_usd"])          # 25 x 10 / 22
        self.assertEqual("S/ 42.61 (USD 11.36)", r["header"]["cost_agent"])
        r2 = run([story()], fx_pen_per_usd=3.75, seats=2, working_days=22)
        self.assertEqual(50.0, r2["totals"]["cost_agent_usd"])          # 2 puestos, un mes completo

    def test_default_exchange_rate_comes_from_the_coefficients(self):
        r = run([story()])
        self.assertEqual(3.45, COEF["agent_cost"]["fx_pen_per_usd"])
        self.assertEqual("S/ 39.20 (USD 11.36)", r["header"]["cost_agent"])        # 11,3636 x 3,45
        self.assertFalse(any("tipo de cambio" in w for w in r["warnings"]))

    def test_missing_exchange_rate_is_pending_not_invented(self):
        coef = copy.deepcopy(COEF)
        coef["agent_cost"]["fx_pen_per_usd"] = None
        r = est.run({"sprint": {"working_days": 10}, "stories": [story()]}, coef)
        self.assertEqual("S/ PENDIENTE (USD 11.36)", r["header"]["cost_agent"])
        self.assertIsNone(r["totals"]["cost_agent_pen"])
        self.assertTrue(any("tipo de cambio" in w for w in r["warnings"]))

    def test_all_groups_are_approved_but_qa_and_agent_are_uncalibrated(self):
        self.assertTrue(all(COEF[g]["status"] == "aprobado" for g in ("human", "agent_cost", "agent_effort", "qa")))
        w = " ".join(run([story()])["warnings"])
        self.assertNotIn("en estado", w)
        self.assertIn("sin calibrar", w)
        self.assertIn("'agent_effort', 'qa'", w)

    def test_unapproved_group_is_flagged(self):
        coef = copy.deepcopy(COEF)
        coef["qa"]["status"] = "propuesto"
        w = " ".join(est.run({"sprint": {"working_days": 10}, "stories": [story()]}, coef)["warnings"])
        self.assertIn("'qa' en estado 'propuesto'", w)

    def test_story_without_tc_is_flagged_and_not_estimated_for_qa(self):
        r = run([story("CL2-US-009")])
        self.assertTrue(any("sin casos de prueba" in w for w in r["warnings"]))
        self.assertEqual(0, r["stories"][0]["qa"]["human_h"])


class InputsFromFiles(unittest.TestCase):
    def test_counts_ac_and_tc_from_files(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "US.md").write_text("---\ntype: US\n---\n### AC-1\nx\n### AC-2\ny\n### AC-3\nz\n", encoding="utf-8")
            tcs = d / "tc"
            tcs.mkdir()
            for n, (us, ex) in enumerate((("US-001", "manual"), ("US-001", "manual"), ("CL2-US-001", "automated"), ("US-002", "manual")), 1):
                (tcs / f"TC-{n}.md").write_text(f"---\ntype: TC\nid: TC-{n}\nuser_story: {us}\nexecution: {ex}\n---\ncuerpo\n", encoding="utf-8")
            data = {"sprint": {"working_days": 10}, "tc_dir": "tc",
                    "stories": [{"id": "CL2-US-001", "aliases": ["US-001"], "us_file": "US.md", "factors": []}]}
            (d / "in.json").write_text(json.dumps(data), encoding="utf-8")
            r = est.run(data, copy.deepcopy(COEF), d)
            s = r["stories"][0]
            self.assertEqual(3, s["criteria"])
            self.assertEqual((2, 1), (s["qa"]["manual_tc"], s["qa"]["automated_tc"]))
            code = subprocess.run([sys.executable, str(SKILL / "scripts/estimate.py"), str(d / "in.json"), "--format", "text"],
                                  capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, code.returncode, code.stderr)
            self.assertIn("/time_agent", code.stdout)

    def test_validation_errors(self):
        for bad in ([story(factors="Z")], [story(criteria=0)], [story(oq=-1)], [{"criteria": 2}], []):
            with self.assertRaises(est.EstimateError):
                run(bad)
        with self.assertRaises(est.EstimateError):
            est.run({"sprint": {}, "stories": [story()]}, copy.deepcopy(COEF))
        with tempfile.TemporaryDirectory() as d:
            bad = pathlib.Path(d) / "x.json"
            bad.write_text("{}", encoding="utf-8")
            self.assertEqual(2, est.main([str(bad)]))


if __name__ == "__main__":
    unittest.main()
