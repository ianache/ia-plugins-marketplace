"""Pruebas del controlador fail-closed (positivas y negativas obligatorias de orchestration-contract)."""
import io, json, sys, tempfile, unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SK / "scripts"))
import yaml  # noqa: E402
import qa_orchestrator as qo  # noqa: E402
from qa_orchestrator import Reject, Runtime  # noqa: E402

ORCH = "orchestrator"
# Alcance por defecto: superficie API necesita al menos un microservicio (api_id) en G0: subordinates-declared.
DEFAULT_SCOPE = {"microservices": [{"id": "position-enricher"}]}


def passing(gate, extra=None):
    """Checks aprobados con la verificación que exige la política: atestación humana (script) o revisor (independent-review)."""
    pol = qo.load_policies()[gate]
    out = []
    for c in pol["checks"]:
        d = {"id": c["id"], "result": "PASS", "evidence_ref": f"ev/{c['id']}.yaml"}
        d.update({"attested_by": "human:qa-lead"} if c["evaluator"] == "script" else {"reviewer": "human:qa-reviewer"})
        out.append(d)
    return out


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.tc_pack = t / "tcpack"
        (self.tc_pack / "TC").mkdir(parents=True)
        (self.tc_pack / "TC" / "TC-PE-01.md").write_text(
            "---\nid: TC-PE-01\nsurface: API\napi_id: position-enricher\ntest_type: positivo\n---\ncuerpo\n", encoding="utf8")
        self.dsp = t / "DSP-001.md"
        self.dsp.write_text("dsp v1", encoding="utf8")
        self.out = t / "out.md"
        self.out.write_text("salida v1", encoding="utf8")
        self.rt = Runtime(t / "rt")

    def init(self, surfaces=("API", "WEB"), **kw):
        dsp = {"id": "DSP-001", "version": "1.0", "path": str(self.dsp)}
        kw.setdefault("scope", DEFAULT_SCOPE)
        self.rt.init("QAPLAN-T", dsp, 633, "obj", list(surfaces), **kw)
        return self

    def g0(self):
        self.rt.load()
        return self.rt.g0(ORCH)

    def ready(self, **kw):
        self.init(**kw)
        self.g0()
        return self

    def run_task(self, tid, gate=None, outputs=None, human_approval=None):
        """authorize -> start -> complete -> gate (todo como orquestador)."""
        self.rt.load()
        t = self.rt.tasks[tid]
        a = self.rt.authorize(ORCH, tid)
        self.rt.load(); self.rt.start(ORCH, tid, a["id"])
        self.rt.load(); self.rt.complete(ORCH, tid, outputs or [self.out])
        self.rt.load()
        verify = {"tc_pack": str(self.tc_pack)} if tid == "T03" else None
        return self.rt.gate(ORCH, tid, gate or passing(t["gate"]), human_approval, verify)


class G0(Base):
    def test_init_blocks_everything(self):
        self.init()
        self.rt.load()
        self.assertEqual(self.rt.st["planning_gate"]["status"], "BLOCKED")
        self.assertEqual(self.rt.st["status"], "BLOCKED")
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T01")

    def test_g0_blocked_when_dsp_missing(self):
        self.dsp.unlink()
        self.init()
        r = self.g0()
        self.assertEqual(r["planning_gate"], "BLOCKED")
        self.assertEqual(self.rt.eligible(), [])

    def test_g0_blocked_with_placeholder_gitlab(self):
        dsp = {"id": "DSP-001", "version": "1.0", "path": str(self.dsp)}
        self.rt.init("P", dsp, "<provided-project-id>", "o", ["API"])
        self.assertEqual(self.g0()["planning_gate"], "BLOCKED")

    def test_g0_pass_makes_only_t01_eligible(self):
        self.ready()
        self.rt.load()
        self.assertEqual(self.rt.eligible(), ["T01"])

    def test_init_does_not_overwrite_state(self):
        self.init()
        with self.assertRaises(Reject):
            self.init()

    def test_invalid_surface_rejected(self):
        with self.assertRaises(Reject):
            self.init(surfaces=("TELEPATHY",))


class Dispatch(Base):
    def test_successor_needs_gate_pass(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load(); self.rt.start(ORCH, "T01", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T01", [self.out])
        self.rt.load()
        with self.assertRaises(Reject):  # COMPLETED técnico != gate PASS
            self.rt.authorize(ORCH, "T02")

    def test_double_dispatch_rejected(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T01")
        self.rt.start(ORCH, "T01", a["id"])
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.start(ORCH, "T01", a["id"])

    def test_specialist_cannot_change_state(self):
        self.ready()
        self.rt.load()
        for fn in (lambda: self.rt.authorize("qa-feature-analyzer", "T01"),
                   lambda: self.rt.g0("qa-test-design"),
                   lambda: self.rt.complete("qa-test-design", "T01", [self.out])):
            with self.assertRaises(Reject):
                fn()
        log = (self.rt.root / "events.jsonl").read_text(encoding="utf8")
        self.assertIn("REJECTED:authorize", log)
        self.rt.load()
        self.assertEqual(self.rt.st["tasks"]["T01"]["status"], "PENDING")

    def test_complete_without_outputs_rejected(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load(); self.rt.start(ORCH, "T01", a["id"])
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.complete(ORCH, "T01", [])
        with self.assertRaises(Reject):
            self.rt.complete(ORCH, "T01", [self.out.parent / "no-existe.md"])

    def test_verify_authorization(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.assertTrue(self.rt.verify_authorization("T01", a["id"])["valid"])
        with self.assertRaises(Reject):
            self.rt.verify_authorization("T01", "AUTH-otra")
        with self.assertRaises(Reject):
            self.rt.verify_authorization("T01", a["id"], token="x" * 64)
        self.rt.st["tasks"]["T01"]["authorization"]["skill"] = "otro-skill"  # adulteración
        with self.assertRaises(Reject):
            self.rt.verify_authorization("T01", a["id"])

    def test_authorization_stale_after_invalidate(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load()
        self.rt.invalidate(ORCH, ["T02"], "cambio DSP")  # T01 conserva su autorización, pero cambia la revisión
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.verify_authorization("T01", a["id"])

    def test_parallel_limit(self):
        self.ready(max_parallel=1)
        self.run_task("T01"); self.run_task("T02"); self.run_task("T03")
        self.rt.load()
        self.rt.authorize(ORCH, "T05-API")
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T05-WEB")


class Gates(Base):
    def test_missing_check_rejected(self):
        self.ready()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load(); self.rt.start(ORCH, "T01", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T01", [self.out])
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.gate(ORCH, "T01", passing("FEATURE_ANALYSIS_GATE")[:-1])

    def test_check_without_evidence_rejected(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0]["evidence_ref"] = None
        self.rt.load()
        a = self.rt.authorize(ORCH, "T01")
        self.rt.load(); self.rt.start(ORCH, "T01", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T01", [self.out])
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.gate(ORCH, "T01", chk)

    def test_uncertain_blocks_and_opens_hil(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0]["result"] = "UNCERTAIN"
        r = self.run_task("T01", gate=chk)
        self.assertEqual(r["task_status"], "BLOCKED")
        self.rt.load()
        self.assertEqual(self.rt.st["status"], "BLOCKED")
        self.assertEqual(len([h for h in self.rt.st["human_intervention"] if h["status"] == "OPEN"]), 1)
        with self.assertRaises(Reject):  # ejecución detenida: ni siquiera otras tareas
            self.rt.authorize(ORCH, "T02")

    def test_fail_blocks_without_retry(self):
        # max_retries = 0 en todos los gates: el primer FAIL bloquea y abre intervención humana.
        self.ready()
        self.assertEqual(self.rt.plan["gate_policies"]["FEATURE_ANALYSIS_GATE"]["max_retries"], 0)
        bad = passing("FEATURE_ANALYSIS_GATE")
        bad[1]["result"] = "FAIL"
        r = self.run_task("T01", gate=bad)
        self.assertNotEqual(r["decision"]["action"], "AUTO_RETRY")
        self.assertEqual(r["decision"]["action"], "REQUEST_HIL")
        self.assertEqual(r["task_status"], "BLOCKED")
        self.assertEqual(r["decision"]["reason"], "retries_exhausted")
        self.rt.load()
        self.assertEqual(self.rt.st["tasks"]["T01"]["attempts"], 0)
        self.assertEqual(len([h for h in self.rt.st["human_intervention"] if h["status"] == "OPEN"]), 1)

    def test_human_decision_does_not_resume_without_regate(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0]["result"] = "UNCERTAIN"
        self.run_task("T01", gate=chk)
        self.rt.load()
        hi = [h for h in self.rt.st["human_intervention"] if h["status"] == "OPEN"][0]["id"]
        with self.assertRaises(Reject):  # sin decisión humana no se reevalúa
            self.rt.gate(ORCH, "T01", passing("FEATURE_ANALYSIS_GATE"))
        with self.assertRaises(Reject):  # el orquestador no puede decidir por la persona
            self.rt.human(hi, ORCH, "REVALIDATE", "ev/x")
        self.rt.human(hi, "ianache", "REVALIDATE", "ev/aprobacion.md")
        self.rt.load()
        self.assertEqual(self.rt.st["tasks"]["T01"]["gate_status"], "BLOCKED")  # sigue bloqueado
        with self.assertRaises(Reject):
            self.rt.authorize(ORCH, "T02")
        r = self.rt.gate(ORCH, "T01", passing("FEATURE_ANALYSIS_GATE"))  # nueva validación
        self.assertEqual(r["decision"]["gate_status"], "PASS")
        self.rt.load()
        self.assertEqual(self.rt.st["status"], "IN_PROGRESS")

    def test_rework_decision_requires_reopen(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0]["result"] = "UNCERTAIN"
        self.run_task("T01", gate=chk)
        self.rt.load()
        hi = [h for h in self.rt.st["human_intervention"] if h["status"] == "OPEN"][0]["id"]
        self.rt.human(hi, "ianache", "REWORK", "ev/rehacer.md")
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.gate(ORCH, "T01", passing("FEATURE_ANALYSIS_GATE"))
        self.rt.reopen(ORCH, "T01", "rehacer según decisión humana")
        self.rt.load()
        self.assertEqual(self.rt.eligible(), ["T01"])

    def test_g0_cannot_be_resumed_by_human_note(self):
        self.init()
        self.rt.load()
        hi = self.rt.st["human_intervention"][0]["id"]
        with self.assertRaises(Reject):
            self.rt.human(hi, "ianache", "REVALIDATE", "ev/x")

    def test_waiver_rejected_by_policy(self):
        self.ready()
        self.rt.load()
        w = {"actor": "ianache", "reason": "r", "scope": "T01", "risk_accepted": "x", "expires_at": "2999-01-01T00:00:00Z", "evidence_ref": "e"}
        with self.assertRaises(Reject):
            self.rt.waive(ORCH, "T01", w)

    def test_cancel_requires_justification(self):
        self.ready()
        self.rt.load()
        with self.assertRaises(Reject):
            self.rt.cancel(ORCH, "T04", "", "")
        self.rt.cancel(ORCH, "T04", "publicación diferida por el usuario", "ev/diferido.md")


class Workflow(Base):
    def test_full_happy_path_with_surfaces_and_mandatory_hil(self):
        self.ready(surfaces=("API", "WEB"))
        for t in ("T01", "T02", "T03"):
            self.assertEqual(self.run_task(t)["decision"]["gate_status"], "PASS")
        self.rt.load()
        self.assertEqual(sorted(self.rt.eligible()), ["T04", "T05-API", "T05-WEB"])
        self.run_task("T05-API")
        self.rt.load()
        with self.assertRaises(Reject):  # T06 espera a TODAS las superficies
            self.rt.authorize(ORCH, "T06")
        self.run_task("T05-WEB")
        self.run_task("T06"); self.run_task("T07")
        # T08: MANDATORY_HIL, aprobación ligada a la revisión exacta
        self.rt.load()
        a = self.rt.authorize(ORCH, "T08")
        self.rt.load(); self.rt.start(ORCH, "T08", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T08", [self.out])
        self.rt.load()
        rev = qo.digest(self.rt.st["tasks"]["T08"]["evidence_refs"])
        chk = passing("HUMAN_GATE")
        stale = {"approved": True, "actor": "ianache", "evidence_ref": "ev/ok.md", "artifact_revision": "otra"}
        r = self.rt.gate(ORCH, "T08", chk, stale)
        self.assertEqual(r["decision"]["reason"], "approval_stale")
        self.assertEqual(r["task_status"], "BLOCKED")

    def test_mandatory_hil_pass_with_bound_approval_and_publication_precondition(self):
        self.ready(surfaces=("API",))
        for t in ("T01", "T02", "T03"):
            self.run_task(t)
        self.rt.load()
        with self.assertRaises(Reject):  # T04 exige aprobación humana previa
            self.rt.authorize(ORCH, "T04")
        ha = {"approved": True, "actor": "ianache", "evidence_ref": "ev/tc.md", "artifact_revision": "rev-1"}
        with self.assertRaises(Reject):  # aprobación de otra revisión
            self.rt.authorize(ORCH, "T04", ha, "rev-2")
        a = self.rt.authorize(ORCH, "T04", ha, "rev-1")
        self.assertEqual(a["human_approval"]["actor"], "ianache")

    def test_invalidate_resets_successors_only(self):
        self.ready(surfaces=("API",))
        for t in ("T01", "T02", "T03"):
            self.run_task(t)
        self.rt.load()
        r = self.rt.invalidate(ORCH, ["T02"], "cambió US-025 en el DSP")
        self.assertEqual(set(r["reset"]), {"T02", "T03", "T04", "T05-API", "T06", "T07", "T08"})
        self.rt.load()
        self.assertEqual(self.rt.st["tasks"]["T01"]["gate_status"], "PASS")  # T01 no se invalida
        self.assertEqual(self.rt.st["tasks"]["T02"]["status"], "PENDING")
        self.assertEqual(self.rt.st["plan_revision"], 2)

    def test_event_log_is_append_only_and_ids_unique(self):
        self.ready(surfaces=("API",))
        self.run_task("T01")
        lines = (self.rt.root / "events.jsonl").read_text(encoding="utf8").splitlines()
        ids = [json.loads(x)["id"] for x in lines]
        self.assertEqual(ids, sorted(set(ids)))
        self.assertGreaterEqual(len(ids), 6)
        self.run_task("T02")
        lines2 = (self.rt.root / "events.jsonl").read_text(encoding="utf8").splitlines()
        self.assertEqual(lines2[:len(lines)], lines)

    def test_resume_from_persisted_state(self):
        self.ready(surfaces=("API",))
        self.run_task("T01")
        rt2 = Runtime(self.rt.root)  # proceso nuevo
        rt2.load()
        self.assertEqual(rt2.eligible(), ["T02"])


class Dag(unittest.TestCase):
    def test_cycle_rejected(self):
        tasks = [{"id": "A", "depends_on": ["B"]}, {"id": "B", "depends_on": ["A"]}]
        self.assertIn("ciclo de tareas", qo.validate_dag(tasks))

    def test_unknown_dependency_rejected(self):
        self.assertTrue(qo.validate_dag([{"id": "A", "depends_on": ["Z"]}]))

    def test_default_dag_is_valid(self):
        self.assertEqual(qo.validate_dag(qo.build_tasks(["API", "WEB", "CROSS_SURFACE"])), [])


class PolicyConsistency(unittest.TestCase):
    """Los checks del orquestador deben coincidir con los criterios de cada especialista."""

    def test_gate_checks_match_specialist_gate_files(self):
        pol = qo.load_policies()
        skills = SK.parent
        seen = set()
        for f in skills.glob("*/resources/gates/*.yaml"):
            d = yaml.safe_load(f.read_text(encoding="utf8"))
            if "policy" not in d:
                continue
            seen.add(d["gate"])
            self.assertEqual([c["id"] for c in d["checks"]], [c["id"] for c in pol[d["gate"]]["checks"]], f.name)
            self.assertEqual(d["policy"]["mode"], pol[d["gate"]]["mode"], f.name)
        self.assertEqual(seen, set(pol))

    def test_no_gate_allows_waiver_by_default(self):
        self.assertFalse(any(g["waiver_allowed"] for g in qo.load_policies().values()))


if __name__ == "__main__":
    unittest.main()


class GateInput(Base):
    """D-16: `gate --checks` acepta la salida de los check_*.py y rechaza con mensaje cualquier entrada inválida."""

    def test_acepta_mapa_con_clave_checks(self):
        self.ready()
        r = self.run_task("T01", gate={"checks": passing("FEATURE_ANALYSIS_GATE")})
        self.assertEqual(r["task_status"], "COMPLETED")

    def test_rechaza_salida_con_error_del_script_real(self):
        import subprocess
        script = SK.parent / "qa-test-design" / "scripts" / "check_test_design.py"
        with tempfile.TemporaryDirectory() as t:
            p = subprocess.run([sys.executable, str(script), "--pack", t, "--profile", "design"], capture_output=True, text=True)
        salida = json.loads(p.stdout)
        self.assertIn("error", salida)  # pack incompleto: {"checks": [], "error": "..."}
        self.ready()
        with self.assertRaises(Reject) as cm:
            self.run_task("T01", gate=salida)
        self.assertIn("script de checks", str(cm.exception))

    def test_rechaza_formas_invalidas_sin_traza(self):
        for malo in (["PASS"], "texto", 3, {"checks": "x"}, [{"result": "PASS", "evidence_ref": "e"}],
                     [{"id": "a", "result": "OK", "evidence_ref": "e"}]):
            with self.subTest(malo=malo):
                with self.assertRaises(Reject):
                    qo.normalize_checks(malo, "T01")


class GateVerificacion(Base):
    """D-14 (opción A): el gate no acepta PASS declarados sin verificación ejecutada, atestación humana o revisor independiente."""

    def raw_pass(self, gate):
        return [{"id": c["id"], "result": "PASS", "evidence_ref": "x"} for c in qo.load_policies()[gate]["checks"]]

    def test_json_a_mano_con_todo_pass_ya_no_aprueba(self):
        self.ready()
        with self.assertRaises(Reject) as cm:
            self.run_task("T01", gate=self.raw_pass("FEATURE_ANALYSIS_GATE"))
        self.assertIn("attested_by", str(cm.exception))

    def test_atestacion_debe_ser_humana(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0]["attested_by"] = "orchestrator"
        with self.assertRaises(Reject):
            self.run_task("T01", gate=chk)

    def test_revisor_no_puede_ser_el_autor_ni_faltar(self):
        for rv in (None, "qa-feature-analyzer", "agent:qa-feature-analyzer", "agent:orchestrator"):
            with self.subTest(reviewer=rv):
                self.setUp(); self.ready()
                chk = passing("FEATURE_ANALYSIS_GATE")
                for c in chk:
                    if "reviewer" in c:
                        c.pop("reviewer") if rv is None else c.update(reviewer=rv)
                with self.assertRaises(Reject) as cm:
                    self.run_task("T01", gate=chk)
                self.assertIn("revis", str(cm.exception))

    def test_revisor_agente_distinto_del_autor_es_valido(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        for c in chk:
            if "reviewer" in c:
                c["reviewer"] = "agent:qa-test-design-reviewer"
        self.assertEqual(self.run_task("T01", gate=chk)["task_status"], "COMPLETED")

    def test_fail_declarado_se_acepta_sin_atestacion(self):
        self.ready()
        chk = passing("FEATURE_ANALYSIS_GATE")
        chk[0] = {"id": chk[0]["id"], "result": "FAIL", "evidence_ref": "x"}
        self.assertNotEqual(self.run_task("T01", gate=chk)["task_status"], "COMPLETED")

    def test_el_orquestador_ejecuta_el_verificador_y_manda_sobre_el_pass_declarado(self):
        # TEST_DESIGN_GATE con un pack vacío: el script reporta error -> el gate rechaza aunque el JSON diga PASS
        self.ready()
        for tid in ("T01",):
            self.run_task(tid)
        pack = Path(self.tmp.name) / "pack"
        pack.mkdir()
        self.rt.load()
        a = self.rt.authorize(ORCH, "T02"); self.rt.load(); self.rt.start(ORCH, "T02", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T02", [self.out]); self.rt.load()
        with self.assertRaises(Reject) as cm:
            self.rt.gate(ORCH, "T02", passing("TEST_DESIGN_GATE"), None, {"pack": str(pack), "critical_risks": ""})
        self.assertIn("verificador", str(cm.exception))

    def test_runners_apuntan_a_scripts_existentes(self):
        for gate, pol in qo.load_policies().items():
            for r in pol.get("runners") or []:
                self.assertTrue((qo.SKILLS_DIR / r["script"]).is_file(), (gate, r["script"]))

    def test_resultado_del_script_manda_sobre_el_pass_declarado(self):
        self.ready()
        self.run_task("T01")
        pack = Path(self.tmp.name) / "pack"
        (pack / "TSN").mkdir(parents=True); (pack / "TC").mkdir()
        for f in ("coverage-matrix.yaml", "requirements-test-traceability.yaml"):
            (pack / f).write_text("items: []\n", encoding="utf8")
        self.rt.load()
        a = self.rt.authorize(ORCH, "T02"); self.rt.load(); self.rt.start(ORCH, "T02", a["id"])
        self.rt.load(); self.rt.complete(ORCH, "T02", [self.out]); self.rt.load()
        r = self.rt.gate(ORCH, "T02", passing("TEST_DESIGN_GATE"), None, {"pack": str(pack), "critical_risks": "RISK-1"})
        self.assertNotEqual(r["task_status"], "COMPLETED")  # el script reporta FAIL en riesgos críticos sin TSN
        ev = next((self.rt.root / "evidence" / "TEST_DESIGN_GATE").glob("T02-attempt*.yaml"))
        checks = {c["id"]: c for c in yaml.safe_load(ev.read_text(encoding="utf8"))["checks"]}
        self.assertEqual(checks["critical-risk-has-tsn"]["result"], "FAIL")
        self.assertEqual(checks["critical-risk-has-tsn"]["declared_result_ignored"], "PASS")
        self.assertEqual(checks["critical-risk-has-tsn"]["evaluation"]["source"], "script")


class RunIsolation(unittest.TestCase):
    """Un run por carpeta: <root>/<run-id>/ independiente (mismo patrón que requirements-engineering)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name)
        self.base = self.ws / "runs"
        self.dsp = self.ws / "DSP-001.md"
        self.dsp.write_text("dsp v1", encoding="utf8")

    def cli(self, run_id, *args):
        argv = ["--root", str(self.base), "--run-id", run_id, *args]
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return qo.main(argv)

    def init_args(self, plan_id):
        return ["init", "--plan-id", plan_id, "--dsp-id", "DSP-001", "--dsp-version", "1.0",
                "--dsp-path", str(self.dsp), "--gitlab-id", "633", "--objective", "obj", "--surfaces", "API,WEB"]

    def plan(self, run_id):
        return yaml.safe_load((self.base / run_id / "plan.yaml").read_text(encoding="utf8"))

    def test_each_run_gets_its_own_folder(self):
        self.assertEqual(self.cli("R1", *self.init_args("QAPLAN-1")), 0)
        self.assertEqual(self.cli("R2", *self.init_args("QAPLAN-2")), 0)
        self.assertEqual(self.plan("R1")["plan_id"], "QAPLAN-1")
        self.assertEqual(self.plan("R2")["plan_id"], "QAPLAN-2")
        self.assertFalse((self.base / "plan.yaml").exists())  # nada en la raíz base

    def test_reinit_same_run_rejected_and_other_run_untouched(self):
        self.assertEqual(self.cli("R1", *self.init_args("QAPLAN-1")), 0)
        self.assertEqual(self.cli("R2", *self.init_args("QAPLAN-2")), 0)
        self.assertEqual(self.cli("R1", *self.init_args("QAPLAN-OTRO")), 1)  # no sobrescribe el run existente
        self.assertEqual(self.plan("R1")["plan_id"], "QAPLAN-1")
        self.assertEqual(self.plan("R2")["plan_id"], "QAPLAN-2")

    def test_invalid_run_id_rejected_without_writing(self):
        for bad in ["../fuera", "a/b", "", "..", ".oculto"]:
            self.assertEqual(self.cli(bad, *self.init_args("QAPLAN-X")), 1, bad)
        self.assertFalse(self.base.exists())
        self.assertFalse((self.ws / "fuera").exists())

    def test_run_root_is_under_base(self):
        self.assertEqual(qo.run_root(self.base, "R1"), self.base / "R1")
        with self.assertRaises(Reject):
            qo.run_root(self.base, "../R1")


class DeliverableFolders(unittest.TestCase):
    """Entregables en testing/<DSP-ID>/[<SSP-ID>/]: sin versión; el SSP es opcional."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name)
        self.base = self.ws / "runs"
        self.dsp = self.ws / "DSP-001.md"
        self.dsp.write_text("dsp v1", encoding="utf8")
        self.sprint = self.ws / "SSP-003.md"
        self.sprint.write_text('---\ndsp_id: "DSP-001"\nuser_stories: ["US-101"]\n---\nsprint', encoding="utf8")

    def cli(self, run_id, *args):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return qo.main(["--root", str(self.base), "--run-id", run_id, *args])

    def init_args(self, dsp_id="DSP-001", *extra):
        return ["init", "--plan-id", "QAPLAN-1", "--dsp-id", dsp_id, "--dsp-version", "1.0",
                "--dsp-path", str(self.dsp), "--gitlab-id", "633", "--objective", "obj", "--surfaces", "API", *extra]

    def plan(self, run_id):
        return yaml.safe_load((self.base / run_id / "plan.yaml").read_text(encoding="utf8"))

    def test_without_ssp_deliverables_go_under_dsp(self):
        self.assertEqual(self.cli("R1", *self.init_args()), 0)
        self.assertEqual(self.plan("R1")["deliverable_root"], "testing/DSP-001/")
        self.assertIsNone(self.plan("R1")["ssp_ref"])

    def test_with_ssp_deliverables_go_under_dsp_and_ssp(self):
        self.assertEqual(self.cli("R1", *self.init_args("DSP-001", "--ssp-id", "SSP-003", "--ssp-path", str(self.sprint))), 0)
        self.assertEqual(self.plan("R1")["deliverable_root"], "testing/DSP-001/SSP-003/")
        self.assertEqual(self.plan("R1")["ssp_ref"], "SSP-003")

    def test_no_version_in_deliverable_path(self):
        self.cli("R1", *self.init_args())
        self.assertNotIn("1.0", self.plan("R1")["deliverable_root"])

    def test_invalid_dsp_or_ssp_id_rejected(self):
        self.assertEqual(self.cli("R1", *self.init_args("../fuera")), 1)
        self.assertEqual(self.cli("R2", *self.init_args("DSP-001", "--ssp-id", "a/b")), 1)
        self.assertFalse((self.base / "R1" / "plan.yaml").exists())
        self.assertFalse((self.base / "R2" / "plan.yaml").exists())
        self.assertFalse((self.ws / "fuera").exists())

    def test_deliverable_root_helper(self):
        self.assertEqual(qo.deliverable_root("DSP-007"), "testing/DSP-007/")
        self.assertEqual(qo.deliverable_root("DSP-007", "SSP-002"), "testing/DSP-007/SSP-002/")
        with self.assertRaises(Reject):
            qo.deliverable_root("DSP-007", "../x")
