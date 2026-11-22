#!/usr/bin/env python3
"""Controlador fail-closed del workflow qa-sdlc-pack. Stdlib + PyYAML.

Único escritor autorizado del estado operativo en .comsatel/qa-design/runs/<run-id>/:
  plan.yaml, plan-status.yaml, tasks/<id>/task-status.yaml, events.jsonl, evidence/.
No ejecuta agentes ni calcula calidad: decide si una tarea puede despacharse y registra el resultado
de gates evaluados con gate_governance.decide(). Un YAML por sí solo no impide invocaciones fuera de
banda: el runtime debe llamar a `verify-authorization` antes de invocar un skill.
"""
import argparse, hashlib, json, os, re, subprocess, sys, time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_governance import decide  # noqa: E402

SCHEMA = "1.1"
PACK = "qa-sdlc-pack"
MODES = ["GREENFIELD", "BROWNFIELD", "EVOLUTION"]
SURFACES = ["API", "WEB", "MOBILE", "CROSS_SURFACE", "DATABASE", "EVENT", "BATCH", "INTEGRATION"]
GATE_OK = ("PASS", "WAIVED")
ORCH = "orchestrator"
POLICIES_FILE = Path(__file__).resolve().parent.parent / "resources" / "gate-policies.yaml"
SKILLS_DIR = Path(__file__).resolve().parents[2]
HUMAN_ID = re.compile(r"^human:\S+$")
REVIEWER_ID = re.compile(r"^(human|agent):\S+$")
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")  # sin separadores ni '..': el run queda dentro de la raíz


class Reject(Exception):
    """Operación rechazada por una regla fail-closed."""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def file_digest(path):
    p, h = Path(path), hashlib.sha256()
    if p.is_dir():
        for f in sorted(x for x in p.rglob("*") if x.is_file()):
            h.update(str(f.relative_to(p)).encode())
            h.update(f.read_bytes())
    elif p.is_file():
        h.update(p.read_bytes())
    else:
        raise Reject(f"salida inexistente: {path}")
    return h.hexdigest()


def load_policies():
    return yaml.safe_load(POLICIES_FILE.read_text(encoding="utf8"))["gates"]


SUBORDINADO_TIPOS = {
    # tipo: (skill, reporte por microservicio, sufijo de id, clave del scope con los TC)
    "funcional": ("postman-automation", "automated-tests/postman/{ms}/postman-automation-report.yaml", "FUN", "tc_funcional"),
    "carga": ("loadtest-automation", "automated-tests/k6/{ms}/loadtest-automation-report.yaml", "CARGA", "tc_carga"),
}


def declared_microservices(scope):
    """Microservicios API involucrados, identificados por api_id. Los TC se asignan después de T03, no en init."""
    out = []
    for ms in (scope or {}).get("microservices") or []:
        if not isinstance(ms, dict):
            raise Reject("scope.microservices: cada entrada debe ser un objeto")
        if "tc_funcional" in ms or "tc_carga" in ms:
            raise Reject(f"{ms.get('id')}: no declarar TC en init; la asignación por api_id se hace tras T03")
        mid = check_id(ms.get("id"), "api_id")
        if mid in out:
            raise Reject(f"microservicio duplicado en scope: {mid}")
        out.append(mid)
    return out


def build_subordinates(microservices, tcs, ssp_id=None):
    """Subordinados por api_id y tipo de prueba, a partir de los TC API asignados tras T03.

    rendimiento -> loadtest-automation (CARGA); resto -> postman-automation (FUN).
    Un TC API sin api_id, o con api_id no declarado en G0, bloquea.
    """
    declared = set(microservices or [])
    por = {}
    for tc in tcs:
        api = tc.get("api_id")
        if not api:
            raise Reject(f"{tc.get('id')}: TC de superficie API sin api_id")
        if api not in declared:
            raise Reject(f"{tc.get('id')}: api_id {api} no declarado en G0")
        tipo = "carga" if tc.get("test_type") == "rendimiento" else "funcional"
        por.setdefault((api, tipo), []).append(tc["id"])
    out = []
    for (api, tipo), ids in sorted(por.items()):
        skill, reporte, sufijo, _ = SUBORDINADO_TIPOS[tipo]
        out.append({"id": f"SUB-{api}-{sufijo}", "microservice": api, "tipo": tipo, "skill": skill,
                    "tc_refs": sorted(ids), "scope_ssp": ssp_id, "report": reporte.format(ms=api)})
    return out


def read_tc_api(pack):
    """Front matter de los TC del pack (carpeta TC/ o TC-*.md en la raíz): campos que usa la asignación por api_id."""
    p = Path(pack)
    files = sorted((p / "TC").glob("*.md")) if (p / "TC").is_dir() else sorted(p.glob("TC-*.md"))
    out = []
    for f in files:
        raw = f.read_text(encoding="utf8")
        try:
            fm = (yaml.safe_load(raw.split("---", 2)[1]) or {}) if raw.startswith("---") else {}
        except yaml.YAMLError as e:
            raise Reject(f"{f.name}: front matter ilegible: {e}")
        out.append({"id": str(fm.get("id") or f.stem), "surface": fm.get("surface"),
                    "api_id": fm.get("api_id"), "test_type": fm.get("test_type"),
                    "user_stories": [str(u) for u in (fm.get("user_stories") or [])]})
    return out


def build_tasks(surfaces, ssp_id=None, subordinates=None):
    def t(i, skill, deps, gate, outs, executor="agent", **kw):
        d = {"id": i, "skill": skill, "executor": executor, "depends_on": deps, "gate": gate,
             "expected_outputs": outs, "inputs": []}
        d.update(kw)
        return d
    eng = [f"T05-{s}" for s in surfaces]
    tasks = [
        t("T01", "qa-feature-analyzer", [], "FEATURE_ANALYSIS_GATE", ["QFA"]),
        t("T02", "qa-test-design", ["T01"], "TEST_DESIGN_GATE", ["QTD", "QTS", "QTP", "TSN", "TC", "TDR"]),
        t("T03", "qa-test-design-reviewer", ["T02"], "TEST_DESIGN_REVIEW_GATE", ["QTR"]),
        t("T04", "qa-sdlc-orchestrator", ["T03"], "TESTCASE_PUBLICATION_GATE", ["gitlab_issue_refs"],
          executor=ORCH, human_approval_before_dispatch=True),
    ]
    # Alcance SSP: cada T05 se limita a los TC del SSP. En API, el engineer delega en un subordinado
    # por microservicio y tipo de prueba (postman-automation o loadtest-automation).
    tasks += [t(f"T05-{s}", "qa-agentic-test-engineer", ["T03"], "TEST_ENGINEERING_GATE", ["QTE", "AT", "TDA", "EXEC", "EVD"],
                surface=s, scope_ssp=ssp_id,
                subordinates=[x["id"] for x in (subordinates or [])] if s == "API" else [])
              for s in surfaces]
    tasks += [
        t("T06", "qa-agentic-test-reviewer", eng, "TEST_ENGINEERING_REVIEW_GATE", ["QER"]),
        t("T07", "qa-quality-intelligence", ["T06"], "QUALITY_INTELLIGENCE_GATE", ["QQI"]),
        t("T08", "qa-sdlc-orchestrator", ["T07"], "HUMAN_GATE", ["QDC"], executor=ORCH),
    ]
    return tasks


def validate_dag(tasks):
    ids = [t["id"] for t in tasks]
    errs = []
    if len(ids) != len(set(ids)):
        errs.append("ids de tarea duplicados")
    for t in tasks:
        for d in t["depends_on"]:
            if d not in ids:
                errs.append(f"{t['id']}: dependencia desconocida {d}")
    graph, seen, active = {t["id"]: t["depends_on"] for t in tasks}, set(), set()

    def visit(n):
        if n in active:
            errs.append("ciclo de tareas")
            return
        if n in seen or n not in graph:
            return
        active.add(n)
        for d in graph[n]:
            visit(d)
        active.discard(n)
        seen.add(n)
    for n in graph:
        visit(n)
    return sorted(set(errs))


def successors(tasks, roots):
    out, changed = set(roots), True
    while changed:
        changed = False
        for t in tasks:
            if t["id"] not in out and any(d in out for d in t["depends_on"]):
                out.add(t["id"])
                changed = True
    return out


def normalize_checks(raw, tid="gate"):
    """Acepta la lista de checks o la salida de los check_*.py ({"checks": [...]}); rechaza con mensaje cualquier otra forma."""
    if isinstance(raw, dict):
        if raw.get("error"):
            raise Reject(f"{tid}: el script de checks reportó un error y no hay evidencia: {raw['error']}")
        raw = raw.get("checks")
    if not isinstance(raw, list) or not raw:
        raise Reject(f"{tid}: --checks debe ser una lista de checks o un objeto con la clave 'checks' no vacía")
    for i, c in enumerate(raw):
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not c["id"]:
            raise Reject(f"{tid}: checks[{i}] debe ser un objeto con 'id' (texto)")
        if c.get("result") not in ("PASS", "FAIL", "UNCERTAIN"):
            raise Reject(f"{tid}: checks[{i}] ({c['id']}) tiene 'result' inválido; use PASS, FAIL o UNCERTAIN")
        if c.get("evidence_ref") is None:
            raise Reject(f"{tid}: checks[{i}] ({c['id']}) sin 'evidence_ref'")
    return raw


def run_gate_scripts(gate, verify, tid):
    """Ejecuta los verificadores `runners` de la política del gate y devuelve {check_id: check}.

    Un runner se omite si falta alguno de sus parámetros ({pack}, {design_pack}, {critical_risks}); sus checks
    caen entonces en la atestación humana. Un runner que falla al ejecutarse o reporta error rechaza el gate.
    """
    verify = verify or {}
    out = {}
    for r in load_policies()[gate].get("runners") or []:
        needed = set(re.findall(r"\{(\w+)\}", " ".join(r["args"])))
        if any(k != "critical_risks" and not verify.get(k) for k in needed):
            continue
        script = SKILLS_DIR / r["script"]
        if not script.is_file():
            raise Reject(f"{tid}: verificador inexistente {r['script']}")
        args = [a.format(**{k: verify.get(k, "") for k in needed}) for a in r["args"]]
        try:
            p = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=300)
            data = json.loads(p.stdout)
        except (OSError, subprocess.TimeoutExpired, ValueError) as e:
            raise Reject(f"{tid}: el verificador {r['script']} no produjo una salida JSON válida: {e}")
        if not isinstance(data, dict) or data.get("error") or not isinstance(data.get("checks"), list) or not data["checks"]:
            raise Reject(f"{tid}: el verificador {r['script']} no entregó checks: {data.get('error') if isinstance(data, dict) else data}")
        for c in data["checks"]:
            out[c["id"]] = {**c, "evaluation": {"source": "script", "script": r["script"]}}
    return out


def authoritative_checks(gate, tid, author, declared, verify, computed=None):
    """Resultado definitivo de cada check de la política (fail-closed, sin PASS declarados no verificables).

    - evaluator `script`: manda el resultado del verificador ejecutado por el orquestador; si no hay verificador
      que lo cubra, un PASS solo se acepta con `attested_by: human:<id>` (atestación humana registrada).
    - evaluator `independent-review`: un PASS exige `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor.
    Un FAIL/UNCERTAIN declarado se acepta siempre (es el lado seguro).
    """
    pol = load_policies()[gate]["checks"]
    ran = {**run_gate_scripts(gate, verify, tid), **(computed or {})}  # computed: checks calculados por el orquestador
    by_id = {c["id"]: c for c in declared}
    final, problems = [], []
    for pc in pol:
        cid = pc["id"]
        d = by_id.get(cid)
        if pc["evaluator"] == "script" and cid in ran:
            c = dict(ran[cid])
            if d is not None and d.get("result") != c["result"]:
                c["declared_result_ignored"] = d.get("result")
            final.append(c)
            continue
        if d is None:
            if pc.get("required"):
                final.append({"id": cid, "result": "MISSING"})
            continue
        c = dict(d)
        if d["result"] == "PASS":
            if pc["evaluator"] == "script":
                if not HUMAN_ID.match(str(d.get("attested_by", ""))):
                    problems.append(f"{cid}: sin verificador ejecutable; un PASS exige attested_by 'human:<id>'")
                c["evaluation"] = {"source": "human-attested", "attested_by": d.get("attested_by")}
            else:
                rv = str(d.get("reviewer", ""))
                if not REVIEWER_ID.match(rv):
                    problems.append(f"{cid}: la revisión independiente exige reviewer 'human:<id>' o 'agent:<skill>'")
                elif rv in (f"agent:{author}", f"human:{ORCH}", f"agent:{ORCH}"):
                    problems.append(f"{cid}: el revisor ({rv}) no puede ser el autor ni el orquestador")
                c["evaluation"] = {"source": "independent-review", "reviewer": rv}
        final.append(c)
    missing = sorted(c["id"] for c in final if c["result"] == "MISSING")
    if missing:
        raise Reject(f"{tid}: evidencia ausente no aprueba; faltan checks {missing}")
    if problems:
        raise Reject(f"{tid}: checks sin verificación válida: " + "; ".join(problems))
    extra = [c for c in declared if c["id"] not in {p["id"] for p in pol}]
    return final + extra


class Runtime:
    def __init__(self, root):
        self.root = Path(root)

    # ---- persistencia -------------------------------------------------
    @contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        lp, end = self.root / ".lock", time.time() + 5
        while True:
            try:
                fd = os.open(lp, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                if time.time() > end:
                    raise Reject("estado bloqueado por otra operación en curso")
                time.sleep(0.05)
        try:
            yield
        finally:
            lp.unlink(missing_ok=True)

    def _write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf8")
        for i in range(10):  # Windows: antivirus/indexador pueden bloquear el reemplazo unos ms
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if i == 9:
                    raise
                time.sleep(0.05 * (i + 1))

    def load(self):
        try:
            self.plan = yaml.safe_load((self.root / "plan.yaml").read_text(encoding="utf8"))
            self.st = yaml.safe_load((self.root / "plan-status.yaml").read_text(encoding="utf8"))
        except FileNotFoundError:
            raise Reject("plan no inicializado: ejecutar init")
        self.tasks = {t["id"]: t for t in self.plan["tasks"]}

    def save(self):
        self._recompute()
        self._write(self.root / "plan.yaml", self.plan)
        self._write(self.root / "plan-status.yaml", self.st)
        for i, v in self.st["tasks"].items():
            self._write(self.root / "tasks" / i / "task-status.yaml", v)

    def log(self, actor, action, task=None, before=None, after=None, evidence_refs=None):
        p = self.root / "events.jsonl"
        n = (len(p.read_text(encoding="utf8").splitlines()) + 1) if p.exists() else 1
        ev = {"id": f"EV-{n:05d}", "ts": now(), "actor": actor, "action": action, "task": task,
              "before": before, "after": after, "evidence_refs": evidence_refs or []}
        with p.open("a", encoding="utf8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    def _recompute(self):
        ts = self.st["tasks"].values()
        if any(h["status"] == "OPEN" for h in self.st["human_intervention"]) or any(v["status"] == "BLOCKED" for v in ts):
            self.st["status"] = "BLOCKED"
        elif any(v["status"] == "FAILED" for v in ts):
            self.st["status"] = "FAILED"
        elif all(v["status"] == "CANCELLED" or (v["status"] == "COMPLETED" and v["gate_status"] in GATE_OK) for v in ts):
            self.st["status"] = "COMPLETED"
        elif self.st["planning_gate"]["status"] == "PASS":
            self.st["status"] = "IN_PROGRESS"
        else:
            self.st["status"] = "BLOCKED" if self.st["planning_gate"]["status"] == "BLOCKED" else "PLANNED"

    # ---- reglas comunes -------------------------------------------------
    def _need_orch(self, actor, action, task=None):
        if actor != ORCH:
            self.log(actor, f"REJECTED:{action}", task)
            raise Reject(f"{action}: solo el orquestador puede cambiar el estado operativo (actor={actor})")

    def _task(self, tid):
        if tid not in self.tasks:
            raise Reject(f"tarea desconocida: {tid}")
        return self.tasks[tid], self.st["tasks"][tid]

    def _open_hi(self, gate, issue, decision_required, task=None, evidence=None):
        n = len(self.st["human_intervention"]) + 1
        hi = {"id": f"HI-{n:03d}", "task": task, "gate": gate, "issue": issue,
              "decision_required": decision_required, "evidence_refs": evidence or [],
              "status": "OPEN", "opened_at": now(), "resolution": None}
        self.st["human_intervention"].append(hi)
        return hi

    def _preds_ok(self, tid):
        for d in self.tasks[tid]["depends_on"]:
            s = self.st["tasks"][d]
            if not (s["status"] == "COMPLETED" and s["gate_status"] in GATE_OK):
                return False, d
        return True, None

    def _halted(self):
        return self.plan.get("halt_scope", "all") == "all" and any(
            h["status"] == "OPEN" for h in self.st["human_intervention"])

    def _eligible_check(self, tid):
        if self.st["planning_gate"]["status"] != "PASS":
            raise Reject("G0 no está en PASS: no se puede despachar ninguna tarea")
        t, s = self._task(tid)
        if s["status"] != "PENDING":
            raise Reject(f"{tid}: estado {s['status']}; solo una tarea PENDING puede autorizarse (doble despacho rechazado)")
        if self._halted():
            raise Reject("hay intervención humana abierta: ejecución detenida")
        ok, dep = self._preds_ok(tid)
        if not ok:
            raise Reject(f"{tid}: la dependencia {dep} no está COMPLETED con gate PASS/WAIVED")
        active = sum(1 for v in self.st["tasks"].values() if v["status"] in ("AUTHORIZED", "IN_PROGRESS"))
        if active >= self.plan.get("max_parallel_tasks", 4):
            raise Reject("límite de paralelismo alcanzado")
        return t, s

    def _input_versions(self, tid):
        return {d: (self.st["tasks"][d]["evidence_refs"] or [{}])[-1].get("sha256") for d in self.tasks[tid]["depends_on"]}

    def _token(self, tid, a):
        return digest({"execution_id": self.st["execution_id"], "task_id": tid, "skill": a["skill"],
                       "input_versions": a["input_versions"], "plan_revision": a["plan_revision"],
                       "gate_snapshot": a["gate_snapshot"]})

    # ---- comandos -------------------------------------------------------
    def init(self, plan_id, dsp, gitlab_id, objective, surfaces, scope=None, max_parallel=4, halt_scope="all", ssp_id=None, ssp_path=None):
        if (self.root / "plan.yaml").exists():
            raise Reject("el plan ya existe: no se sobrescribe estado operativo")
        bad = [s for s in surfaces if s not in SURFACES]
        if not surfaces or bad:
            raise Reject(f"superficies inválidas o ausentes: {bad or surfaces}")
        deliv = deliverable_root(dsp.get("id"), ssp_id)  # valida DSP-ID y SSP-ID antes de escribir nada
        ssp_src = None
        if ssp_id:
            if not ssp_path:
                raise Reject("--ssp-id requiere --ssp-path (documento del SSP)")
            ssp_src = ssp_source(ssp_path, ssp_id)  # falla antes de escribir si el documento no existe
        pol = load_policies()
        microservicios = declared_microservices(scope)  # valida api_id antes de escribir nada
        tasks = build_tasks(surfaces, ssp_id, [])  # subordinados: se crean tras T03 (asignación por api_id)
        for t in tasks:
            t["acceptance_criteria"] = [c["id"] for c in pol[t["gate"]]["checks"] if c.get("required")]
        dsp = dict(dsp)
        dsp["digest"] = file_digest(dsp["path"]) if dsp.get("path") and Path(dsp["path"]).exists() else None
        plan = {"schema_version": SCHEMA, "pack_name": PACK, "plan_id": plan_id, "workflow_modes": MODES,
                "dsp_ref": dsp, "ssp_ref": ssp_id, "ssp_source": ssp_src, "microservices": microservicios, "subordinates": [], "deliverable_root": deliv,
                "gitlab_id": str(gitlab_id), "objective": objective, "scope": scope or {},
                "surfaces": surfaces, "planning_gate": "G0", "plan_revision": 1,
                "max_parallel_tasks": max_parallel, "halt_scope": halt_scope,
                "gate_policies": {k: {"mode": v["mode"], "max_retries": v["max_retries"],
                                       "waiver_allowed": v["waiver_allowed"]} for k, v in pol.items()},
                "tasks": tasks}
        st = {"schema_version": "1.0", "execution_id": f"QAEXEC-{int(time.time())}", "status": "BLOCKED",
              "plan_revision": 1, "planning_gate": {"id": "G0", "status": "BLOCKED", "evidence_refs": []},
              "tasks": {t["id"]: {"status": "PENDING", "gate_status": "PENDING", "authorization": None,
                                  "evidence_refs": [], "attempts": 0, "technically_completed": False,
                                  "observations": []} for t in tasks},
              "human_intervention": []}
        self.plan, self.st, self.tasks = plan, st, {t["id"]: t for t in tasks}
        self._open_hi("G0", "Esperando validación de planificación", "Ejecutar g0 con evidencia")
        self.save()
        self.log(ORCH, "INIT", None, None, {"status": "BLOCKED"})
        return {"status": "BLOCKED", "planning_gate": "BLOCKED", "tasks": [t["id"] for t in tasks]}

    def g0(self, actor):
        self._need_orch(actor, "g0")
        p, checks = self.plan, []
        errs = validate_dag(p["tasks"])
        checks.append({"id": "dag-valid", "result": "FAIL" if errs else "PASS", "evidence_ref": "plan.yaml", "detail": errs})
        d = p["dsp_ref"]
        placeholders = any("<" in str(x) for x in (d.get("id"), d.get("version"), d.get("path"), p["gitlab_id"]))
        inputs_ok = bool(d.get("id") and d.get("version") and d.get("path") and d.get("digest") and p["gitlab_id"]) and not placeholders
        checks.append({"id": "inputs-identified", "result": "PASS" if inputs_ok else "FAIL", "evidence_ref": "plan.yaml#dsp_ref"})
        crit = all(t["acceptance_criteria"] and t["expected_outputs"] and t["gate"] in p["gate_policies"] for t in p["tasks"])
        checks.append({"id": "criteria-defined", "result": "PASS" if crit else "FAIL", "evidence_ref": "plan.yaml#tasks"})
        checks.append({"id": "surfaces-declared", "result": "PASS" if p["surfaces"] else "FAIL", "evidence_ref": "plan.yaml#surfaces"})
        if "API" in p["surfaces"]:
            ok_sub = bool(p.get("microservices"))
            checks.append({"id": "subordinates-declared", "result": "PASS" if ok_sub else "FAIL", "evidence_ref": "plan.yaml#subordinates",
                           "detail": [] if ok_sub else ["superficie API sin microservicios: declarar en scope.microservices los api_id involucrados (los TC se asignan tras T03)"]})
        else:
            checks.append({"id": "subordinates-declared", "result": "PASS", "evidence_ref": "plan.yaml#subordinates", "detail": ["sin superficie API"]})
        src = p.get("ssp_source")
        if p.get("ssp_ref"):
            # El SSP es parte del alcance: debe seguir siendo el documento aprobado y pertenecer al DSP del plan.
            vigente = bool(src and src.get("path") and Path(src["path"]).exists() and file_digest(src["path"]) == src.get("digest"))
            checks.append({"id": "ssp-identified", "result": "PASS" if vigente else "FAIL", "evidence_ref": "plan.yaml#ssp_source",
                           "detail": [] if vigente else ["SSP ausente o modificado desde init"]})
            mismo = bool(src) and src.get("declared_dsp_id") == d.get("id")
            checks.append({"id": "ssp-belongs-to-dsp", "result": "PASS" if mismo else "FAIL", "evidence_ref": "plan.yaml#ssp_source",
                           "detail": [] if mismo else [f"el SSP declara {src.get('declared_dsp_id') if src else None}, no {d.get('id')}"]})
        else:
            checks.append({"id": "ssp-scope", "result": "PASS", "evidence_ref": "plan.yaml#ssp_ref", "detail": ["alcance DSP completo (sin SSP)"]})
        res = decide({"mode": "AUTO", "max_retries": 0}, checks)
        ev = self.root / "evidence" / "G0.yaml"
        self._write(ev, {"gate": "G0", "evaluated_at": now(), "checks": checks, "decision": res})
        before = self.st["planning_gate"]["status"]
        self.st["planning_gate"] = {"id": "G0", "status": res["gate_status"], "evidence_refs": [str(ev.relative_to(self.root))]}
        if res["gate_status"] == "PASS":
            for h in self.st["human_intervention"]:
                if h["gate"] == "G0" and h["status"] == "OPEN":
                    h["status"], h["resolution"] = "CLOSED_BY_REVALIDATION", {"by": ORCH, "at": now()}
        elif not any(h["gate"] == "G0" and h["status"] == "OPEN" for h in self.st["human_intervention"]):
            self._open_hi("G0", "G0 falló: " + ", ".join(c["id"] for c in checks if c["result"] == "FAIL"), "Corregir el plan y reevaluar G0")
        self.save()
        self.log(ORCH, "G0", None, before, res["gate_status"], [str(ev.relative_to(self.root))])
        return {"planning_gate": res["gate_status"], "checks": checks}

    def eligible(self):
        out = []
        for tid in self.tasks:
            try:
                self._eligible_check(tid)
                out.append(tid)
            except Reject:
                pass
        return out

    def authorize(self, actor, tid, human_approval=None, artifact_revision=None, ttl_minutes=240):
        self._need_orch(actor, "authorize", tid)
        t, s = self._eligible_check(tid)
        if t.get("human_approval_before_dispatch"):
            ha = human_approval or {}
            if not (ha.get("approved") and ha.get("actor") and ha.get("evidence_ref") and ha.get("artifact_revision")):
                raise Reject(f"{tid}: requiere aprobación humana explícita antes del despacho")
            if ha["artifact_revision"] != artifact_revision:
                raise Reject(f"{tid}: la aprobación humana es de otra revisión del artefacto (obsoleta)")
        a = {"id": f"AUTH-{tid}-{self.st['plan_revision']}-{s['attempts']}", "task_id": tid, "skill": t["skill"],
             "input_versions": self._input_versions(tid), "plan_revision": self.st["plan_revision"],
             "gate_snapshot": {d: self.st["tasks"][d]["gate_status"] for d in t["depends_on"]},
             "issued_at": now(), "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "human_approval": ha if t.get("human_approval_before_dispatch") else None}
        a["token"] = self._token(tid, a)
        before = s["status"]
        s["status"], s["authorization"] = "AUTHORIZED", a
        self.save()
        self.log(ORCH, "AUTHORIZE", tid, before, "AUTHORIZED")
        return a

    def verify_authorization(self, tid, auth_id, token=None):
        t, s = self._task(tid)
        a = s.get("authorization")
        if not a or a["id"] != auth_id:
            raise Reject(f"{tid}: autorización inexistente o distinta")
        if token and token != a["token"]:
            raise Reject(f"{tid}: token de autorización inválido")
        if a["token"] != self._token(tid, a):
            raise Reject(f"{tid}: autorización adulterada")
        if a["plan_revision"] != self.st["plan_revision"]:
            raise Reject(f"{tid}: autorización obsoleta (cambió la revisión del plan)")
        if a["input_versions"] != self._input_versions(tid):
            raise Reject(f"{tid}: autorización obsoleta (cambiaron las entradas)")
        if a["expires_at"] < now():
            raise Reject(f"{tid}: autorización vencida")
        if self.st["planning_gate"]["status"] != "PASS":
            raise Reject("G0 no está en PASS")
        return {"valid": True, "task": tid, "execution_id": self.st["execution_id"]}

    def start(self, actor, tid, auth_id):
        self._need_orch(actor, "start", tid)
        t, s = self._task(tid)
        if s["status"] != "AUTHORIZED":
            raise Reject(f"{tid}: estado {s['status']}; solo AUTHORIZED puede iniciar (doble despacho rechazado)")
        self.verify_authorization(tid, auth_id)
        s["status"] = "IN_PROGRESS"
        self.save()
        self.log(ORCH, "START", tid, "AUTHORIZED", "IN_PROGRESS")
        return {"task": tid, "status": "IN_PROGRESS"}

    def complete(self, actor, tid, outputs):
        self._need_orch(actor, "complete", tid)
        t, s = self._task(tid)
        if s["status"] != "IN_PROGRESS":
            raise Reject(f"{tid}: solo una tarea IN_PROGRESS puede completarse")
        if not outputs:
            raise Reject(f"{tid}: se exigen salidas/evidencias; la sola existencia de la tarea no completa nada")
        refs = [{"path": str(o), "sha256": file_digest(o)} for o in outputs]
        s["status"], s["technically_completed"], s["evidence_refs"] = "COMPLETED", True, refs
        s["gate_status"] = "PENDING"
        self.save()
        self.log(ORCH, "COMPLETE", tid, "IN_PROGRESS", "COMPLETED", [r["path"] for r in refs])
        return {"task": tid, "status": "COMPLETED", "gate_status": "PENDING (COMPLETED técnico != gate PASS)"}

    def _api_assignment(self, verify):
        """Check `tc-api-assigned` de T03 y los TC API del pack. Lo calcula el orquestador: el especialista no lo declara."""
        base = {"id": "tc-api-assigned", "evidence_ref": "plan.yaml#microservices", "evaluation": {"source": "orchestrator"}}
        if "API" not in self.plan["surfaces"]:
            return {**base, "result": "PASS", "detail": ["sin superficie API"]}, []
        pack = (verify or {}).get("tc_pack") or (verify or {}).get("pack")  # tc_pack: carpeta de TC (CLI: --pack)
        if not pack or not Path(pack).is_dir():
            return {**base, "result": "FAIL", "detail": ["falta el pack de TC (--pack)"]}, None
        declared = set(self.plan.get("microservices") or [])
        api = [x for x in read_tc_api(pack) if x.get("surface") == "API"]
        problemas = [] if api else ["sin TC de superficie API en el pack"]
        for x in api:
            if not x.get("api_id"):
                problemas.append(f"{x['id']}: sin api_id")
            elif x["api_id"] not in declared:
                problemas.append(f"{x['id']}: api_id {x['api_id']} no declarado en G0")
        if problemas:
            return {**base, "result": "FAIL", "detail": problemas}, None
        n_ms = len({x["api_id"] for x in api})
        return {**base, "result": "PASS", "detail": [f"{len(api)} TC API asignados a {n_ms} microservicios"]}, api

    def _ssp_selection(self, verify):
        """Check `ssp-tc-selection` de T03: con SSP, sus TC son los que comparten historia con él. Lo calcula el orquestador."""
        base = {"id": "ssp-tc-selection", "evidence_ref": "plan.yaml#ssp_source", "evaluation": {"source": "orchestrator"}}
        if not self.plan.get("ssp_ref"):
            self.plan["ssp_tc_ids"] = None
            return {**base, "result": "PASS", "detail": ["sin SSP: alcance DSP completo"]}
        pack = (verify or {}).get("tc_pack") or (verify or {}).get("pack")
        if not pack or not Path(pack).is_dir():
            return {**base, "result": "FAIL", "detail": ["falta el pack de TC (--pack)"]}
        us = (self.plan.get("ssp_source") or {}).get("user_stories") or []
        seleccionados, sin_tc = ssp_tc_selection(read_tc_api(pack), us)
        self.plan["ssp_tc_ids"] = seleccionados
        if sin_tc:
            return {**base, "result": "FAIL", "detail": [f"historias del SSP sin ningún TC: {', '.join(sin_tc)}"]}
        if not seleccionados:
            return {**base, "result": "FAIL", "detail": ["ningún TC comparte historia con el SSP"]}
        return {**base, "result": "PASS", "detail": [f"{len(seleccionados)} TC seleccionados por el SSP"]}

    def _assign_subordinates(self, tcs_api):
        subs = build_subordinates(self.plan.get("microservices") or [], tcs_api, self.plan.get("ssp_ref"))
        self.plan["subordinates"] = subs
        ids = [x["id"] for x in subs]
        for task in self.plan["tasks"]:
            if task.get("surface") == "API":
                task["subordinates"] = ids

    def gate(self, actor, tid, checks, human_approval=None, verify=None):
        self._need_orch(actor, "gate", tid)
        t, s = self._task(tid)
        pol = self.plan["gate_policies"][t["gate"]]
        required = {c["id"] for c in load_policies()[t["gate"]]["checks"] if c.get("required")}
        mine_open = [h for h in self.st["human_intervention"] if h.get("task") == tid and h["status"] == "OPEN"]
        resolved = [h for h in self.st["human_intervention"] if h.get("task") == tid and h["status"] == "RESOLVED"]
        if s["status"] == "BLOCKED" and s["technically_completed"]:
            if mine_open or not any(h["resolution"]["decision"] == "REVALIDATE" for h in resolved):
                raise Reject(f"{tid}: gate BLOCKED; hace falta una decisión humana REVALIDATE registrada antes de reevaluar")
        elif s["status"] != "COMPLETED":
            raise Reject(f"{tid}: el gate solo se evalúa sobre una tarea COMPLETED con salidas")
        checks = normalize_checks(checks, tid)
        computed, tcs_api = {}, None
        if tid == "T03":
            chk, tcs_api = self._api_assignment(verify)
            chk_ssp = self._ssp_selection(verify)
            computed = {"tc-api-assigned": chk, "ssp-tc-selection": chk_ssp}
            checks = [c for c in checks if c.get("id") not in ("tc-api-assigned", "ssp-tc-selection")] + [chk, chk_ssp]
        if t["gate"] == "TEST_ENGINEERING_GATE":
            seleccion = ",".join(self.plan.get("ssp_tc_ids") or []) or "-" if self.plan.get("ssp_ref") else "*"
            verify = {**(verify or {}), "ssp_tc_ids": seleccion}
        checks = authoritative_checks(t["gate"], tid, t["skill"], checks, verify, computed)
        ids = {c.get("id") for c in checks}
        missing = sorted(required - ids)
        if missing:
            raise Reject(f"{tid}: evidencia ausente no aprueba; faltan checks {missing}")
        revision = digest(s["evidence_refs"])
        try:
            res = decide({"mode": pol["mode"], "max_retries": pol["max_retries"], "artifact_revision": revision},
                         checks, attempts=s["attempts"], human_approval=human_approval)
        except ValueError as e:
            raise Reject(f"{tid}: {e}")
        before = (s["status"], s["gate_status"])
        ev = self.root / "evidence" / t["gate"] / f"{tid}-attempt{s['attempts']}.yaml"
        self._write(ev, {"task": tid, "gate": t["gate"], "evaluated_at": now(), "artifact_revision": revision,
                         "checks": checks, "decision": res})
        s["observations"] = [{"check": c["id"], "note": c["observation"]} for c in checks if c.get("observation")]
        if res["gate_status"] == "PASS":
            s["status"], s["gate_status"] = "COMPLETED", "PASS"
            if tid == "T03" and tcs_api is not None:
                self._assign_subordinates(tcs_api)
            for h in resolved:
                h["status"] = "CLOSED_BY_REVALIDATION"
        elif res["action"] == "AUTO_RETRY":
            s.update({"status": "PENDING", "gate_status": "FAIL", "authorization": None,
                      "attempts": s["attempts"] + 1, "technically_completed": False})
        else:
            s["status"], s["gate_status"] = "BLOCKED", "BLOCKED"
            for h in resolved:
                h["status"] = "CLOSED_BY_REVALIDATION"
            self._open_hi(t["gate"], f"{tid}: gate {t['gate']} BLOCKED ({res['reason']})",
                          "Decidir: aportar evidencia y reevaluar, rehacer la tarea (reopen) o cancelar",
                          task=tid, evidence=[str(ev.relative_to(self.root))])
        self.save()
        self.log(ORCH, "GATE", tid, before, (s["status"], s["gate_status"], res["reason"]), [str(ev.relative_to(self.root))])
        return {"task": tid, "gate": t["gate"], "decision": res, "task_status": s["status"]}

    def human(self, hi_id, actor, decision, evidence_ref, note=""):
        if actor in ("", None, ORCH):
            raise Reject("la decisión humana debe registrar la identidad de la persona (actor != orchestrator)")
        if decision not in ("REVALIDATE", "REWORK", "CANCEL") or not evidence_ref:
            raise Reject("decisión inválida o sin evidencia (REVALIDATE|REWORK|CANCEL + evidence_ref)")
        hi = next((h for h in self.st["human_intervention"] if h["id"] == hi_id), None)
        if not hi or hi["status"] != "OPEN":
            raise Reject(f"{hi_id}: no existe o no está OPEN")
        if hi["gate"] == "G0":
            raise Reject("G0 no se reanuda por decisión humana: corregir el plan y ejecutar g0")
        hi["status"] = "RESOLVED"
        hi["resolution"] = {"actor": actor, "decision": decision, "evidence_ref": evidence_ref, "note": note, "at": now()}
        self.save()
        self.log(actor, "HUMAN_DECISION", hi.get("task"), "OPEN", f"RESOLVED:{decision}", [evidence_ref])
        return {"id": hi_id, "status": "RESOLVED", "next": "reevaluar el gate; la decisión humana no convierte en PASS"}

    def reopen(self, actor, tid, reason):
        self._need_orch(actor, "reopen", tid)
        if not reason:
            raise Reject("reopen exige motivo")
        return self._reset([tid], f"reopen: {reason}", actor)

    def invalidate(self, actor, tids, reason):
        self._need_orch(actor, "invalidate")
        if not reason:
            raise Reject("invalidate exige motivo")
        for t in tids:
            self._task(t)
        return self._reset(tids, f"invalidate: {reason}", actor, bump=True)

    def _reset(self, tids, why, actor, bump=False):
        hit = sorted(successors(self.plan["tasks"], tids))
        if bump:
            self.st["plan_revision"] += 1
            self.plan["plan_revision"] = self.st["plan_revision"]
        for i in hit:
            s = self.st["tasks"][i]
            self.log(actor, "RESET", i, (s["status"], s["gate_status"]), ("PENDING", "PENDING"), [])
            s.update({"status": "PENDING", "gate_status": "PENDING", "authorization": None, "evidence_refs": [],
                      "technically_completed": False, "attempts": s["attempts"] + (0 if bump else 1), "observations": []})
            for h in self.st["human_intervention"]:
                if h.get("task") == i and h["status"] in ("OPEN", "RESOLVED"):
                    h["status"] = "CLOSED_BY_RESET"
        self.save()
        self.log(actor, "RESET_SUMMARY", None, None, {"tasks": hit, "reason": why})
        return {"reset": hit, "plan_revision": self.st["plan_revision"]}

    def waive(self, actor, tid, waiver):
        self._need_orch(actor, "waive", tid)
        t, s = self._task(tid)
        if not self.plan["gate_policies"][t["gate"]].get("waiver_allowed"):
            raise Reject(f"{tid}: la política de {t['gate']} no admite waiver")
        need = ("actor", "reason", "scope", "risk_accepted", "expires_at", "evidence_ref")
        if any(not waiver.get(k) for k in need) or waiver["expires_at"] < now():
            raise Reject(f"{tid}: waiver incompleto o vencido (se exige {', '.join(need)})")
        s["gate_status"] = "WAIVED"
        s["waiver"] = waiver
        self.save()
        self.log(ORCH, "WAIVE", tid, None, "WAIVED", [waiver["evidence_ref"]])
        return {"task": tid, "gate_status": "WAIVED"}

    def cancel(self, actor, tid, justification, evidence_ref):
        self._need_orch(actor, "cancel", tid)
        if not (justification and evidence_ref):
            raise Reject("cancel exige justificación y evidencia")
        t, s = self._task(tid)
        s["status"], s["cancellation"] = "CANCELLED", {"justification": justification, "evidence_ref": evidence_ref, "at": now()}
        self.save()
        self.log(ORCH, "CANCEL", tid, None, "CANCELLED", [evidence_ref])
        return {"task": tid, "status": "CANCELLED"}

    def status(self):
        return {"status": self.st["status"], "planning_gate": self.st["planning_gate"]["status"],
                "plan_revision": self.st["plan_revision"],
                "tasks": {k: (v["status"], v["gate_status"]) for k, v in self.st["tasks"].items()},
                "eligible": self.eligible(),
                "open_human_interventions": [h["id"] for h in self.st["human_intervention"] if h["status"] == "OPEN"]}


def _jload(path):
    return json.loads(Path(path).read_text(encoding="utf8")) if path else None


def _pathmap():
    for d in Path(__file__).resolve().parents:
        f = d / "assets" / "pathmap.json"
        if f.is_file(): return json.loads(f.read_text(encoding="utf8"))
    raise SystemExit("assets/pathmap.json no encontrado")


def check_id(value, what):
    """Identificador usado como nombre de carpeta (run-id, DSP-ID, SSP-ID): sin separadores ni '..'."""
    if not value or not RUN_ID.match(str(value)):
        raise Reject(f"{what} inválido: {value!r} (letras, dígitos, '.', '_' o '-'; debe empezar por letra o dígito)")
    return str(value)


def run_root(base, run_id):
    """Raíz de un run: <orchestrator_root>/<run-id>/ (mismo patrón que requirements-engineering)."""
    return Path(base) / check_id(run_id, "run-id")


def ssp_tc_selection(tcs, ssp_us):
    """TC que entran en el SSP (comparten alguna historia con él) y las historias del SSP sin ningún TC."""
    us = set(ssp_us)
    seleccionados = sorted(x["id"] for x in tcs if us & set(x.get("user_stories") or []))
    cubiertas = {u for x in tcs for u in (x.get("user_stories") or []) if u in us}
    return seleccionados, sorted(us - cubiertas)


def ssp_user_stories(fm):
    """Historias que el SSP incluye en su frontmatter (user_stories: [US-n, ...]). Obligatorio."""
    raw = fm.get("user_stories") or []
    if not isinstance(raw, list) or not raw:
        raise Reject("el SSP debe declarar user_stories: [US-n, ...] (al menos una historia)")
    out = []
    for us in raw:
        if not re.fullmatch(r"US-\d+", str(us)):
            raise Reject(f"el SSP declara un ID de historia inválido: {us!r}")
        out.append(str(us))
    return out


def ssp_source(path, ssp_id):
    """Metadatos del SSP fijados en init: documento, digest y el DSP que declara su frontmatter (dsp_id)."""
    p = Path(path)
    if not p.is_file():
        raise Reject(f"no existe el documento del SSP: {path}")
    texto = p.read_text(encoding="utf8", errors="replace")
    m = re.search(r'^dsp_id:\s*"?(DSP-\d{3})', texto, re.M)
    return {"id": check_id(ssp_id, "SSP-ID"), "path": str(p), "digest": file_digest(str(p)),
            "declared_dsp_id": m.group(1) if m else None,
            "user_stories": ssp_user_stories(_frontmatter_de(p))}


def _frontmatter_de(path):
    """Front matter YAML de un Markdown; {} si no tiene."""
    raw = Path(path).read_text(encoding="utf8", errors="replace")
    if not raw.startswith("---"):
        return {}
    try:
        return yaml.safe_load(raw.split("---", 2)[1]) or {}
    except yaml.YAMLError as e:
        raise Reject(f"front matter ilegible en {path}: {e}")


def dsp_from_ssp(ssp_path, kb_root="."):
    """DSP de un plan que se inicia solo con SSP.

    El SSP declara su DSP en `dsp_id`. El documento del DSP se localiza así:
      1. entrada de `sources` del SSP cuyo `resource` existe en la KB y cuyo nombre empieza por el DSP-ID;
      2. búsqueda en la KB por nombre DSP-NNN*.md: debe haber exactamente un candidato.
    Devuelve {id, version, path}. Si no se localiza o no es único, bloquea: no se inventa el DSP.
    """
    ssp = Path(ssp_path)
    if not ssp.is_file():
        raise Reject(f"no existe el documento del SSP: {ssp_path}")
    fm = _frontmatter_de(ssp)
    dsp_id = str(fm.get("dsp_id") or "")
    if not re.fullmatch(r"DSP-\d{3}", dsp_id):
        raise Reject(f"el SSP no declara un dsp_id válido (DSP-NNN): {dsp_id!r}")
    raiz = Path(kb_root)
    candidato = None
    for src in fm.get("sources") or []:
        recurso = str((src or {}).get("resource") or "")
        if recurso and Path(recurso).name.startswith(dsp_id) and (raiz / recurso).is_file():
            candidato = raiz / recurso
            break
    if candidato is None:
        hallados = sorted(p for p in raiz.glob(f"**/{dsp_id}*.md") if ".comsatel" not in p.parts)
        if not hallados:
            raise Reject(f"no se localiza el documento de {dsp_id} en la KB ({raiz}); indique --dsp-path")
        if len(hallados) > 1:
            raise Reject(f"hay varios documentos para {dsp_id} en la KB: {[str(p) for p in hallados]}; indique --dsp-path")
        candidato = hallados[0]
    dfm = _frontmatter_de(candidato)
    if dfm.get("id") and str(dfm["id"]) != dsp_id:
        raise Reject(f"{candidato} declara id {dfm['id']}, no {dsp_id}")
    version = dfm.get("version")
    if not version:
        raise Reject(f"{candidato} no declara versión: indique --dsp-version y --dsp-path")
    return {"id": dsp_id, "version": str(version), "path": str(candidato)}


def dsp_de_args(args):
    """DSP del init: explícito (--dsp-id, --dsp-version, --dsp-path) o derivado del SSP (--ssp-id, --ssp-path)."""
    if args.dsp_id:
        if not (args.dsp_version and args.dsp_path):
            raise Reject("--dsp-id requiere --dsp-version y --dsp-path")
        return {"id": args.dsp_id, "version": args.dsp_version, "path": args.dsp_path}
    if not (args.ssp_id and args.ssp_path):
        raise Reject("sin --dsp-id, el plan se inicia con --ssp-id y --ssp-path")
    return dsp_from_ssp(args.ssp_path, args.kb_root)


def deliverable_root(dsp_id, ssp_id=None):
    """Carpeta de entregables QA por alcance: testing/<DSP-ID>/[<SSP-ID>/]. Sin versión: las pruebas pertenecen a un DSP y SSP concretos."""
    base = _pathmap()["deliverable_root"].replace("<DSP-ID>", check_id(dsp_id, "DSP-ID"))
    return base + (check_id(ssp_id, "SSP-ID") + "/" if ssp_id else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="./" + _pathmap()["orchestrator_root"].strip("/"),  # campo orchestrator_root de pathmap.json (raíz base de todos los runs)
                    help="raíz base de los runs; el estado se guarda en <root>/<run-id>/")
    ap.add_argument("--run-id", required=True, help="identificador del run: su carpeta de estado es <root>/<run-id>/")
    ap.add_argument("--actor", default=ORCH)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("init")
    for k in ("plan-id", "gitlab-id", "objective"):
        a.add_argument("--" + k, required=True)
    a.add_argument("--dsp-id", help="DSP del plan; si se omite, se toma del dsp_id del SSP (--ssp-path)")
    a.add_argument("--dsp-version", help="versión del DSP (con --dsp-id)")
    a.add_argument("--dsp-path", help="documento del DSP (con --dsp-id)")
    a.add_argument("--kb-root", default=".", help="raíz de la KB del producto donde localizar el DSP cuando se entra solo con SSP")
    a.add_argument("--surfaces", required=True, help="API,WEB,CROSS_SURFACE")
    a.add_argument("--scope-json")
    a.add_argument("--max-parallel", type=int, default=4)
    a.add_argument("--halt-scope", choices=["all", "dependents"], default="all")
    a.add_argument("--ssp-id", help="SSP opcional: los entregables van a testing/<DSP-ID>/<SSP-ID>/ y el alcance de los TC se limita al SSP")
    a.add_argument("--ssp-path", help="documento del SSP (management/sprints/SSP-*.md); obligatorio con --ssp-id")
    sp.add_parser("g0")
    sp.add_parser("status")
    sp.add_parser("eligible")
    a = sp.add_parser("authorize"); a.add_argument("--task", required=True); a.add_argument("--human-approval"); a.add_argument("--artifact-revision"); a.add_argument("--ttl-minutes", type=int, default=240)
    a = sp.add_parser("verify-authorization"); a.add_argument("--task", required=True); a.add_argument("--auth-id", required=True); a.add_argument("--token")
    a = sp.add_parser("start"); a.add_argument("--task", required=True); a.add_argument("--auth-id", required=True)
    a = sp.add_parser("complete"); a.add_argument("--task", required=True); a.add_argument("--output", action="append", default=[])
    a = sp.add_parser("gate"); a.add_argument("--task", required=True); a.add_argument("--checks", required=True); a.add_argument("--human-approval")
    a.add_argument("--pack", help="directorio del pack a verificar con los scripts del gate"); a.add_argument("--design-pack", help="pack de diseño (gates de ingeniería)"); a.add_argument("--critical-risks", default="", help="IDs de riesgos críticos separados por coma")
    a = sp.add_parser("human"); a.add_argument("--id", required=True); a.add_argument("--decision", required=True); a.add_argument("--evidence", required=True); a.add_argument("--note", default="")
    a = sp.add_parser("reopen"); a.add_argument("--task", required=True); a.add_argument("--reason", required=True)
    a = sp.add_parser("invalidate"); a.add_argument("--tasks", required=True); a.add_argument("--reason", required=True)
    a = sp.add_parser("waive"); a.add_argument("--task", required=True); a.add_argument("--waiver", required=True)
    a = sp.add_parser("cancel"); a.add_argument("--task", required=True); a.add_argument("--justification", required=True); a.add_argument("--evidence", required=True)
    args = ap.parse_args(argv)
    try:
        rt = Runtime(run_root(args.root, args.run_id))
        with rt.lock():
            if args.cmd == "init":
                out = rt.init(args.plan_id, dsp_de_args(args),
                              args.gitlab_id, args.objective, args.surfaces.split(","), _jload(args.scope_json),
                              args.max_parallel, args.halt_scope, ssp_id=args.ssp_id, ssp_path=args.ssp_path)
            else:
                rt.load()
                c = args.cmd
                if c == "g0": out = rt.g0(args.actor)
                elif c == "status": out = rt.status()
                elif c == "eligible": out = rt.eligible()
                elif c == "authorize": out = rt.authorize(args.actor, args.task, _jload(args.human_approval), args.artifact_revision, args.ttl_minutes)
                elif c == "verify-authorization": out = rt.verify_authorization(args.task, args.auth_id, args.token)
                elif c == "start": out = rt.start(args.actor, args.task, args.auth_id)
                elif c == "complete": out = rt.complete(args.actor, args.task, args.output)
                elif c == "gate": out = rt.gate(args.actor, args.task, _jload(args.checks), _jload(args.human_approval), {"pack": args.pack, "tc_pack": args.pack, "design_pack": args.design_pack, "critical_risks": args.critical_risks})
                elif c == "human": out = rt.human(args.id, args.actor, args.decision, args.evidence, args.note)
                elif c == "reopen": out = rt.reopen(args.actor, args.task, args.reason)
                elif c == "invalidate": out = rt.invalidate(args.actor, args.tasks.split(","), args.reason)
                elif c == "waive": out = rt.waive(args.actor, args.task, _jload(args.waiver))
                elif c == "cancel": out = rt.cancel(args.actor, args.task, args.justification, args.evidence)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except Reject as e:
        print(json.dumps({"rejected": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
