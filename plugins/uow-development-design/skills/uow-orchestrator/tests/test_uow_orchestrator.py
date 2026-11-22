"""Pruebas del controlador fail-closed del pack uow-development-design (positivas y negativas obligatorias)."""
import sys, tempfile, unittest
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SK / "scripts"))
import yaml  # noqa: E402
import uow_orchestrator as uo  # noqa: E402
from uow_orchestrator import Reject, Runtime  # noqa: E402

ORCH = "orchestrator"


def passing(gate):
    """Checks aprobados con la verificación que exige la política: atestación humana (script) o revisor (independent-review)."""
    out = []
    for c in uo.load_policies()[gate]["checks"]:
        d = {"id": c["id"], "result": "PASS", "evidence_ref": f"ev/{c['id']}.yaml"}
        d.update({"attested_by": "human:uow-lead"} if c["evaluator"] == "script" else {"reviewer": "human:uow-reviewer"})
        out.append(d)
    return out


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.us = t / "US-001.md"; self.us.write_text("us v1", encoding="utf8")
        self.out = t / "out.md"; self.out.write_text("salida v1", encoding="utf8")
        self.rt = Runtime(t / "rt")

    def init(self, mode="GREENFIELD", baseline=None, us=None):
        return self.rt.init("P1", us or {"id": "US-001", "version": "1.0.0", "path": str(self.us)}, "demo", mode, baseline)

    def ready(self, **kw):
        self.init(**kw); self.rt.g0(ORCH)

    def run_task(self, tid, human=None):
        a = self.rt.authorize(ORCH, tid)
        self.rt.start(ORCH, tid, a["id"])
        self.rt.complete(ORCH, tid, [str(self.out)])
        return self.rt.gate(ORCH, tid, passing(self.rt.tasks[tid]["gate"]), human)

    def to_expanded(self, uows=(("UOW-001", []),)):
        self.ready(); self.run_task("T01"); self.run_task("T02")
        return self.rt.expand(ORCH, [{"id": u, "depends_on": d} for u, d in uows])


class Planning(Base):
    def test_init_blocks_everything_until_g0(self):
        self.init()
        self.assertEqual(self.rt.status()["planning_gate"], "BLOCKED")
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T01")

    def test_g0_blocked_when_us_missing_or_placeholder(self):
        self.init(us={"id": "US-001", "version": "1.0.0", "path": "/no/existe.md"})
        self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "BLOCKED")
        self.setUp(); self.init(us={"id": "<US>", "version": "1.0.0", "path": str(self.us)})
        self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "BLOCKED")

    def test_brownfield_and_evolution_require_baseline(self):
        for mode in ("BROWNFIELD", "EVOLUTION"):
            self.setUp(); self.init(mode=mode)
            self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "BLOCKED", mode)
            self.setUp(); self.init(mode=mode, baseline={"ref": "main", "commit": "abc123"})
            self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "PASS", mode)

    def test_invalid_mode_and_overwrite_rejected(self):
        with self.assertRaises(Reject):
            self.init(mode="FREESTYLE")
        self.init()
        with self.assertRaises(Reject):
            self.init()

    def test_g0_pass_makes_only_t01_eligible(self):
        self.ready()
        self.assertEqual(self.rt.eligible(), ["T01"])

    def test_dag_has_no_cycles_and_plan_not_complete_before_expand(self):
        self.ready(); self.run_task("T01"); self.run_task("T02")
        self.assertEqual(uo.validate_dag(self.rt.plan["tasks"]), [])
        self.assertNotEqual(self.rt.status()["status"], "COMPLETED")


class FailClosed(Base):
    def test_successor_needs_gate_pass(self):
        self.ready()
        a = self.rt.authorize(ORCH, "T01"); self.rt.start(ORCH, "T01", a["id"]); self.rt.complete(ORCH, "T01", [str(self.out)])
        with self.assertRaises(Reject):   # COMPLETED técnico sin gate PASS
            self.rt.authorize(ORCH, "T02")

    def test_specialist_cannot_change_state(self):
        self.ready()
        for fn in (lambda: self.rt.authorize("uow-context-assembler", "T01"), lambda: self.rt.g0("uow-context-assembler"),
                   lambda: self.rt.expand("uow-slice-designer", [{"id": "UOW-001"}])):
            with self.assertRaises(Reject):
                fn()

    def test_double_dispatch_rejected(self):
        self.ready(); self.rt.authorize(ORCH, "T01")
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T01")

    def test_complete_requires_outputs_and_gate_requires_every_check(self):
        self.ready()
        a = self.rt.authorize(ORCH, "T01"); self.rt.start(ORCH, "T01", a["id"])
        with self.assertRaises(Reject):
            self.rt.complete(ORCH, "T01", [])
        self.rt.complete(ORCH, "T01", [str(self.out)])
        with self.assertRaises(Reject):   # falta un check requerido
            self.rt.gate(ORCH, "T01", passing("CONTEXT_GATE")[:-1])

    def test_failed_gate_halts_and_human_decision_does_not_pass(self):
        self.ready()
        a = self.rt.authorize(ORCH, "T01"); self.rt.start(ORCH, "T01", a["id"]); self.rt.complete(ORCH, "T01", [str(self.out)])
        bad = passing("CONTEXT_GATE"); bad[0]["result"] = "UNCERTAIN"
        res = self.rt.gate(ORCH, "T01", bad)
        self.assertEqual(res["task_status"], "BLOCKED")
        self.assertEqual(self.rt.status()["status"], "BLOCKED")
        hi = self.rt.status()["open_human_interventions"][0]
        self.rt.human(hi, "human:ana", "REVALIDATE", "ev/1")
        self.assertNotEqual(self.rt.st["tasks"]["T01"]["gate_status"], "PASS")   # la decisión no aprueba
        self.assertEqual(self.rt.gate(ORCH, "T01", passing("CONTEXT_GATE"))["task_status"], "COMPLETED")

    def test_human_decision_needs_a_person(self):
        self.ready()
        with self.assertRaises(Reject):
            self.rt.human("HI-001", ORCH, "REVALIDATE", "ev")


class Expansion(Base):
    def test_expand_requires_slice_gate_pass(self):
        self.ready(); self.run_task("T01")
        with self.assertRaises(Reject):
            self.rt.expand(ORCH, [{"id": "UOW-001"}])

    def test_expand_builds_a_chain_per_uow_and_only_once(self):
        r = self.to_expanded((("UOW-001", []), ("UOW-002", ["UOW-001"])))
        self.assertEqual(len(r["tasks"]), 10)
        self.assertEqual(self.rt.plan["plan_revision"], 2)
        self.assertEqual(self.rt.tasks["T05-UOW-002"]["depends_on"], ["T03-UOW-002", "T04-UOW-002"])
        with self.assertRaises(Reject):
            self.rt.expand(ORCH, [{"id": "UOW-003"}])

    def test_expand_rejects_bad_ids_duplicates_unknown_deps_and_cycles(self):
        self.ready(); self.run_task("T01"); self.run_task("T02")
        for uows in ([], [{"id": "X-1"}], [{"id": "UOW-001"}, {"id": "UOW-001"}], [{"id": "UOW-001", "depends_on": ["UOW-009"]}],
                     [{"id": "UOW-001", "depends_on": ["UOW-002"]}, {"id": "UOW-002", "depends_on": ["UOW-001"]}]):
            with self.assertRaises(Reject, msg=str(uows)):
                self.rt.expand(ORCH, uows)

    def test_contracts_and_code_run_in_parallel_and_plan_waits_for_both(self):
        self.to_expanded()
        self.assertEqual(sorted(self.rt.eligible()), ["T03-UOW-001", "T04-UOW-001"])
        self.run_task("T03-UOW-001")
        self.assertNotIn("T05-UOW-001", self.rt.eligible())
        self.run_task("T04-UOW-001")
        self.assertIn("T05-UOW-001", self.rt.eligible())

    def test_uows_advance_independently(self):
        self.to_expanded((("UOW-001", []), ("UOW-002", [])))
        self.run_task("T03-UOW-001"); self.run_task("T04-UOW-001")
        self.assertNotIn("T05-UOW-002", self.rt.eligible())
        self.assertIn("T05-UOW-001", self.rt.eligible())

    def test_uow_ready_gate_needs_human_approval_bound_to_digest(self):
        self.to_expanded()
        for t in ("T03", "T04", "T05", "T06"):
            self.run_task(f"{t}-UOW-001")
        tid = "T07-UOW-001"
        a = self.rt.authorize(ORCH, tid); self.rt.start(ORCH, tid, a["id"]); self.rt.complete(ORCH, tid, [str(self.out)])
        self.assertEqual(self.rt.gate(ORCH, tid, passing("UOW_READY_GATE"))["task_status"], "BLOCKED")   # sin aprobación humana
        self.setUp(); self.to_expanded()
        for t in ("T03", "T04", "T05", "T06"):
            self.run_task(f"{t}-UOW-001")
        a = self.rt.authorize(ORCH, tid); self.rt.start(ORCH, tid, a["id"]); self.rt.complete(ORCH, tid, [str(self.out)])
        rev = uo.digest(self.rt.st["tasks"][tid]["evidence_refs"])
        stale = {"approved": True, "actor": "human:ana", "evidence_ref": "MR-9", "artifact_revision": "otro-digest"}
        self.assertEqual(self.rt.gate(ORCH, tid, passing("UOW_READY_GATE"), stale)["task_status"], "BLOCKED")
        self.setUp(); self.to_expanded()
        for t in ("T03", "T04", "T05", "T06"):
            self.run_task(f"{t}-UOW-001")
        a = self.rt.authorize(ORCH, tid); self.rt.start(ORCH, tid, a["id"]); self.rt.complete(ORCH, tid, [str(self.out)])
        rev = uo.digest(self.rt.st["tasks"][tid]["evidence_refs"])
        ok = {"approved": True, "actor": "human:ana", "evidence_ref": "MR-9", "artifact_revision": rev}
        res = self.rt.gate(ORCH, tid, passing("UOW_READY_GATE"), ok)
        self.assertEqual((res["task_status"], self.rt.st["tasks"][tid]["gate_status"]), ("COMPLETED", "PASS"))
        self.assertEqual(self.rt.status()["status"], "COMPLETED")

    def test_invalidating_the_context_resets_every_uow_chain(self):
        self.to_expanded()
        self.run_task("T03-UOW-001")
        r = self.rt.invalidate(ORCH, ["T01"], "cambió la US")
        self.assertIn("T03-UOW-001", r["reset"])
        self.assertEqual(self.rt.st["tasks"]["T03-UOW-001"]["status"], "PENDING")
        self.assertEqual(self.rt.plan["plan_revision"], 3)


class Policies(unittest.TestCase):
    def test_specialist_gate_files_match_orchestrator_policy(self):
        pol, seen = uo.load_policies(), set()
        for f in SK.parent.glob("*/resources/gates/*.yaml"):
            d = yaml.safe_load(f.read_text(encoding="utf8"))
            seen.add(d["gate"])
            self.assertEqual([c["id"] for c in d["checks"]], [c["id"] for c in pol[d["gate"]]["checks"]], f.name)
            self.assertEqual(d["policy"]["mode"], pol[d["gate"]]["mode"], f.name)
            self.assertEqual(d["policy"]["max_retries"], pol[d["gate"]]["max_retries"], f.name)
        self.assertEqual(seen, set(pol))

    def test_only_the_final_gate_is_mandatory_hil_and_no_gate_allows_waiver(self):
        pol = uo.load_policies()
        self.assertEqual([g for g, v in pol.items() if v["mode"] == "MANDATORY_HIL"], ["UOW_READY_GATE"])
        self.assertFalse(any(v["waiver_allowed"] for v in pol.values()))

    def test_every_task_owner_is_a_skill_of_the_plugin(self):
        skills = {p.name for p in SK.parent.iterdir() if p.is_dir()}
        tasks = uo.base_tasks() + uo.uow_tasks("UOW-001")
        self.assertTrue({t["skill"] for t in tasks} <= skills)
        self.assertEqual(len(skills), 7)


if __name__ == "__main__":
    unittest.main()


class ArgumentosDeArchivo(unittest.TestCase):
    """D-18: --human-approval / --checks son rutas de archivos JSON; el error es claro y el --help lo dice."""

    def test_jload_rechaza_con_mensaje_claro(self):
        with self.assertRaises(Reject) as cm:
            uo._jload('{"approved": true}')
        self.assertIn("archivo JSON", str(cm.exception))
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "x.json"; f.write_text("no es json", encoding="utf8")
            with self.assertRaises(Reject):
                uo._jload(str(f))
            f.write_text('{"approved": true}', encoding="utf8")
            self.assertEqual(uo._jload(str(f)), {"approved": True})
        self.assertIsNone(uo._jload(None))

    def test_help_documenta_que_es_un_archivo(self):
        import subprocess, sys
        for cmd in ("gate", "authorize"):
            out = subprocess.run([sys.executable, str(uo.__file__), cmd, "--help"], capture_output=True, text=True).stdout
            self.assertIn("ARCHIVO JSON", out)


class GateVerificacion(Base):
    """D-18 (opción A): el gate no acepta PASS declarados sin verificador ejecutado, atestación humana o revisor independiente."""

    def raw_pass(self, gate):
        return [{"id": c["id"], "result": "PASS", "evidence_ref": "x"} for c in uo.load_policies()[gate]["checks"]]

    def test_json_a_mano_con_todo_pass_ya_no_aprueba(self):
        self.ready()
        with self.assertRaises(Reject) as cm:
            self.run_task_con("T01", self.raw_pass("CONTEXT_GATE"))
        self.assertIn("attested_by", str(cm.exception))

    def run_task_con(self, tid, checks, verify=None):
        a = self.rt.authorize(ORCH, tid)
        self.rt.start(ORCH, tid, a["id"])
        self.rt.complete(ORCH, tid, [str(self.out)])
        return self.rt.gate(ORCH, tid, checks, None, verify)

    def test_revisor_no_puede_ser_el_autor(self):
        for rv in (None, "agent:uow-context-assembler", "agent:orchestrator"):
            with self.subTest(reviewer=rv):
                self.setUp(); self.ready()
                chk = passing("CONTEXT_GATE")
                for c in chk:
                    if "reviewer" in c:
                        c.pop("reviewer") if rv is None else c.update(reviewer=rv)
                with self.assertRaises(Reject) as cm:
                    self.run_task_con("T01", chk)
                self.assertIn("revis", str(cm.exception))

    def test_acepta_mapa_con_clave_checks_y_rechaza_formas_invalidas(self):
        self.ready()
        self.assertEqual(self.run_task_con("T01", {"checks": passing("CONTEXT_GATE")})["task_status"], "COMPLETED")
        for malo in (["PASS"], "texto", {"checks": "x"}, {"checks": [], "error": "pack incompleto"}):
            with self.subTest(malo=malo), self.assertRaises(Reject):
                uo.normalize_checks(malo, "T01")

    def test_el_script_manda_sobre_el_pass_declarado(self):
        self.ready()
        pack = Path(self.tmp.name) / "uows"; pack.mkdir()   # pack vacío: check_uow_package.py reporta FAIL en context
        r = self.run_task_con("T01", passing("CONTEXT_GATE"), {"pack": str(pack)})
        self.assertNotEqual(r["task_status"], "COMPLETED")
        ev = next((self.rt.root / "evidence" / "CONTEXT_GATE").glob("T01-attempt*.yaml"))
        checks = yaml.safe_load(ev.read_text(encoding="utf8"))["checks"]
        ejecutados = [c for c in checks if c.get("evaluation", {}).get("source") == "script"]
        self.assertTrue(ejecutados)
        self.assertTrue(any(c.get("declared_result_ignored") == "PASS" for c in ejecutados))

    def test_runners_apuntan_a_scripts_existentes_y_cubren_los_checks_script(self):
        import importlib.util
        for gate, pol in uo.load_policies().items():
            self.assertEqual(len(pol["runners"]), 1, gate)
            r = pol["runners"][0]
            script = uo.SKILLS_DIR / r["script"]
            self.assertTrue(script.is_file(), (gate, r["script"]))
            spec = importlib.util.spec_from_file_location("chk", script); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            ids = {c["id"] for c in m.checks(self.tmp.name, r["args"][3], "UOW-001")}
            self.assertTrue({c["id"] for c in pol["checks"] if c["evaluator"] == "script"} <= ids, gate)


class BaselineRepo(Base):
    """D-23a: con baseline.repo, G0 verifica que el commit exista (git cat-file -e)."""

    def repo(self):
        import subprocess
        d = Path(self.tmp.name) / "repo"; d.mkdir()
        run = lambda *a: subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True)
        run("init"); run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-m", "x")
        return d, run("rev-parse", "HEAD").stdout.strip()

    def test_commit_real_pasa_y_hash_inventado_bloquea(self):
        d, sha = self.repo()
        self.init(mode="BROWNFIELD", baseline={"ref": "main", "commit": sha, "repo": str(d)})
        self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "PASS")
        self.setUp(); d, sha = self.repo()
        self.init(mode="BROWNFIELD", baseline={"ref": "main", "commit": "deadbeef1234", "repo": str(d)})
        r = self.rt.g0(ORCH)
        self.assertEqual(r["planning_gate"], "BLOCKED")
        self.assertTrue(any(c["id"] == "baseline-commit-exists" and c["result"] == "FAIL" for c in r["checks"]))

    def test_sin_repo_no_verifica(self):
        self.init(mode="BROWNFIELD", baseline={"ref": "main", "commit": "deadbeef1234"})
        self.assertEqual(self.rt.g0(ORCH)["planning_gate"], "PASS")
