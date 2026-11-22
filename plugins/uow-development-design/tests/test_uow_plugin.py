"""Pruebas del plugin uow-development-design: estructura, catálogo de tipos, consistencia entre skills y recorrido completo."""
import hashlib, importlib.util, json, re, sys, tempfile, unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SK = ROOT / "skills"
PLUGIN = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf8"))
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SPECIALISTS = {"uow-context-assembler": "UCX", "uow-slice-designer": "UOW", "uow-contract-binder": "UCB", "uow-codebase-mapper": "UCM",
               "uow-agent-execution-planner": "UAP", "uow-readiness-reviewer": "UWR"}
TYPES = list(SPECIALISTS.values())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def front(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf8").split("---", 2)[1])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


sys.path.insert(0, str(SK / "uow-orchestrator/scripts"))
uo = load(SK / "uow-orchestrator/scripts/uow_orchestrator.py", "uow_orchestrator")
chk = load(SK / "uow-orchestrator/scripts/check_uow_package.py", "check_uow_package")
pkg = load(SK / "uow-orchestrator/scripts/uow_package.py", "uow_package")
fx = load(SK / "uow-readiness-reviewer/tests/pkgfixture.py", "pkgfixture")


class Structure(unittest.TestCase):
    def test_one_orchestrator_and_at_most_six_specialists(self):
        names = sorted(p.name for p in SK.iterdir() if p.is_dir())
        self.assertEqual(names, sorted(["uow-orchestrator", *SPECIALISTS]))
        self.assertLessEqual(len(SPECIALISTS), 6)
        self.assertEqual([n for n in names if n.endswith("-orchestrator")], ["uow-orchestrator"])

    def test_metadata_is_homogeneous(self):
        self.assertRegex(PLUGIN["version"], SEMVER)
        for p in SK.iterdir():
            m = front(p / "SKILL.md")
            self.assertEqual(m["name"], p.name)
            self.assertEqual(m["metadata"], {"version": PLUGIN["version"], "author": "COMSATEL", "type": "development"}, p.name)
            self.assertEqual((p / "VERSION").read_text(encoding="utf8").strip(), PLUGIN["version"], p.name)

    def test_each_specialist_owns_exactly_one_type_gate_and_template(self):
        pol = uo.load_policies()
        for name, sig in SPECIALISTS.items():
            t = SK / name / "templates" / f"{sig}-OKF.md"
            self.assertEqual(front(t)["type"], sig, name)
            gates = [f.stem for f in (SK / name / "resources/gates").glob("*.yaml")]
            self.assertEqual(len(gates), 1, name)
            self.assertEqual(pol[gates[0]]["checks"][0]["id"], yaml.safe_load((SK / name / f"resources/gates/{gates[0]}.yaml").read_text(encoding="utf8"))["checks"][0]["id"])
        self.assertEqual(len(pol), 7)

    def test_pack_spec_matches_the_plugin(self):
        spec = yaml.safe_load((ROOT / "assets/pack.yaml").read_text(encoding="utf8"))
        self.assertEqual(spec["pack_name"], PLUGIN["name"])
        self.assertEqual({s["name"] for s in spec["skills"]}, {p.name for p in SK.iterdir()})
        self.assertEqual(set(spec["artifact_types"]), set(TYPES))
        self.assertEqual(spec["execution_modes"], ["GREENFIELD", "BROWNFIELD", "EVOLUTION"])
        self.assertEqual(sum(1 for s in spec["skills"] if s["role"] == "orchestrator"), 1)

    def test_registered_in_the_marketplace(self):
        mk = json.loads((REPO / ".claude-plugin/marketplace.json").read_text(encoding="utf8"))
        e = [p for p in mk["plugins"] if p["name"] == PLUGIN["name"]]
        self.assertEqual(len(e), 1)
        self.assertTrue((REPO / e[0]["source"]).is_dir())

    def test_has_changelog_with_current_version(self):
        self.assertIn(f"## [{PLUGIN['version']}]", (ROOT / "CHANGELOG.md").read_text(encoding="utf8"))


class Standard(unittest.TestCase):
    def test_types_are_in_the_master_standard_and_copies_are_identical(self):
        master = REPO / "plugins/STD-OKF-001-v1.11.0-stable.md"
        txt = master.read_text(encoding="utf8")
        for sig in TYPES:
            self.assertIn(f"| `{sig}` |", txt, sig)
            self.assertIn(f"| {sig} |", txt, sig)
        copies = [ROOT / "standards/STD-OKF-001-v1.11.0-stable.md"] + [p / "resources/STD-OKF-001.md" for p in SK.iterdir()]
        self.assertEqual({sha(c) for c in copies} | {sha(master)}, {sha(master)})

    def test_shared_files_are_identical_across_skills(self):
        for rel in ("scripts/check_uow_package.py", "resources/contracts/common-contract.yaml", "resources/orchestration.md"):
            self.assertEqual(len({sha(p / rel) for p in SK.iterdir()}), 1, rel)

    def test_no_dedicated_development_context_pack_type_is_invented(self):
        text = (ROOT / "DOCUMENTACION.md").read_text(encoding="utf8")
        self.assertIn("No existe un \"Development Context Pack\" único", text)


class EndToEnd(unittest.TestCase):
    """Recorre el flujo completo: gates con los checks reales del paquete y aprobación humana ligada al digest."""

    def setUp(self):
        self.t, self.pack = fx.build("EVOLUTION")
        self.addCleanup(self.t.cleanup)
        tmp = Path(self.t.name)
        self.us = tmp / "US-001.md"; self.us.write_text("us", encoding="utf8")
        self.rt = uo.Runtime(tmp / "rt")
        self.rt.init("P1", {"id": "US-001", "version": "1.0.0", "path": str(self.us)}, "alta de cliente", "EVOLUTION", {"ref": "main", "commit": "abc1234"})
        self.rt.g0(uo.ORCH)

    def checks(self, gate, profile, uow=None):
        res = {c["id"]: c for c in chk.checks(self.pack, profile, uow)}
        out = []
        for c in uo.load_policies()[gate]["checks"]:
            out.append(res.get(c["id"]) or {"id": c["id"], "result": "PASS", "evidence_ref": f"review/{c['id']}", "reviewer": "human:uow-reviewer"})   # independent-review aportado por el revisor
        return out

    def run_task(self, tid, outputs, profile, uow=None, human=None):
        a = self.rt.authorize(uo.ORCH, tid); self.rt.start(uo.ORCH, tid, a["id"]); self.rt.complete(uo.ORCH, tid, [str(o) for o in outputs])
        return self.rt.gate(uo.ORCH, tid, self.checks(self.rt.tasks[tid]["gate"], profile, uow), human, {"pack": str(self.pack)})   # el orquestador ejecuta check_uow_package.py

    def test_full_flow_to_a_human_approved_package(self):
        p = self.pack
        self.assertEqual(self.run_task("T01", [next(p.glob("UCX-*.md"))], "context")["task_status"], "COMPLETED")
        self.assertEqual(self.run_task("T02", [next(p.glob("UOW-001-*.md"))], "slice")["task_status"], "COMPLETED")
        self.rt.expand(uo.ORCH, [{"id": "UOW-001", "depends_on": []}])
        u = "UOW-001"
        self.run_task(f"T03-{u}", [next(p.glob("UOW-001/UCB-*.md"))], "binding", u)
        self.run_task(f"T04-{u}", [next(p.glob("UOW-001/UCM-*.md"))], "codebase", u)
        self.run_task(f"T05-{u}", [next(p.glob("UOW-001/UAP-*.md"))], "agent-plan", u)
        self.run_task(f"T06-{u}", [next(p.glob("UOW-001/UWR-*.md"))], "readiness", u)
        man = pkg.build(p, u)
        self.assertEqual(pkg.verify(p, u)["valid"], True)
        tid = f"T07-{u}"
        a = self.rt.authorize(uo.ORCH, tid); self.rt.start(uo.ORCH, tid, a["id"]); self.rt.complete(uo.ORCH, tid, [str(p / u / "uow-package.yaml")])
        rev = uo.digest(self.rt.st["tasks"][tid]["evidence_refs"])
        ok = {"approved": True, "actor": "human:lead", "evidence_ref": "MR-1", "artifact_revision": rev}
        res = self.rt.gate(uo.ORCH, tid, self.checks("UOW_READY_GATE", "ready", u), ok, {"pack": str(self.pack)})
        self.assertEqual(res["decision"]["gate_status"], "PASS")
        self.assertEqual(self.rt.status()["status"], "COMPLETED")
        self.assertEqual(len(man["documents"]), 5)

    def test_a_failing_script_check_blocks_the_gate(self):
        p = self.pack
        f = next(p.glob("UOW-001/UCM-*.md")); f.write_text(f.read_text(encoding="utf8").replace("9f3c2ab", "HEAD"), encoding="utf8")
        self.run_task("T01", [next(p.glob("UCX-*.md"))], "context"); self.run_task("T02", [next(p.glob("UOW-001-*.md"))], "slice")
        self.rt.expand(uo.ORCH, [{"id": "UOW-001"}])
        self.run_task("T03-UOW-001", [next(p.glob("UOW-001/UCB-*.md"))], "binding", "UOW-001")
        res = self.run_task("T04-UOW-001", [f], "codebase", "UOW-001")
        self.assertNotEqual(res["decision"]["gate_status"], "PASS")
        self.assertNotIn("T05-UOW-001", self.rt.eligible())

    def test_tampering_after_review_breaks_the_digest(self):
        p = self.pack
        pkg.build(p, "UOW-001")
        f = next(p.glob("UOW-001/UAP-*.md")); f.write_text(f.read_text(encoding="utf8") + "\ncambio posterior\n", encoding="utf8")
        self.assertFalse(pkg.verify(p, "UOW-001")["valid"])
        self.assertEqual({c["id"]: c["result"] for c in chk.checks(p, "ready", "UOW-001")}["package-digest-matches"], "FAIL")

    def test_package_builder_refuses_an_incomplete_package(self):
        next(self.pack.glob("UOW-001/UWR-*.md")).unlink()
        with self.assertRaises(ValueError):
            pkg.build(self.pack, "UOW-001")


if __name__ == "__main__":
    unittest.main()
