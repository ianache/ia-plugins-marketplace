import json, sys, unittest
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SK / "scripts"))
import publish_testcase_issues as pub  # noqa: E402

EXAMPLE = json.loads((SK / "examples/gitlab-testcases.json").read_text(encoding="utf8"))


def payload(**tc_over):
    p = json.loads(json.dumps(EXAMPLE))
    p["human_approval"].update(approved=True, actor="human:ianache")
    p["test_cases"][0].update(approved=True, **tc_over)
    return p


class Publish(unittest.TestCase):
    def test_example_is_consistent_with_script_but_not_publishable_unapproved(self):
        with self.assertRaises(RuntimeError):  # el ejemplo no trae aprobación humana
            pub.publish(EXAMPLE, dry_run=True)

    def test_dry_run_ok_when_approved(self):
        r = pub.publish(payload(), dry_run=True)
        self.assertTrue(r["dry_run"])
        self.assertIn("testcase_id: TC-001", r["issues"][0]["description"])
        self.assertNotIn("Pasos", r["issues"][0]["description"])  # no copia el contenido del TC

    def test_tsn_is_never_published(self):
        with self.assertRaises(ValueError):
            pub.publish(payload(testcase_id="TSN-001"), dry_run=True)

    def test_unapproved_tc_rejected(self):
        p = payload()
        p["test_cases"][0]["approved"] = False
        with self.assertRaises(ValueError):
            pub.publish(p, dry_run=True)

    def test_missing_scenario_or_kb_rejected(self):
        for k in ("scenario_refs", "kb_local_path", "kb_gitlab_url"):
            with self.assertRaises(ValueError, msg=k):
                pub.publish(payload(**{k: ""}), dry_run=True)

    def test_requires_pat_for_real_publication(self):
        import os
        os.environ.pop("GITLAB_PAT", None)
        with self.assertRaises(RuntimeError):
            pub.publish(payload())


if __name__ == "__main__":
    unittest.main()
