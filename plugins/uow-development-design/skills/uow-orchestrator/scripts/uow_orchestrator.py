#!/usr/bin/env python3
"""Controlador fail-closed del workflow uow-development-design. Stdlib + PyYAML.

Único escritor autorizado del estado operativo en .comsatel/uow-development-design/runs/:
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
PACK = "uow-development-design"
MODES = ["GREENFIELD", "BROWNFIELD", "EVOLUTION"]
UOW_ID = re.compile(r"^UOW-\d+$")
GATE_OK = ("PASS", "WAIVED")
ORCH = "orchestrator"
POLICIES_FILE = Path(__file__).resolve().parent.parent / "resources" / "gate-policies.yaml"
SKILLS_DIR = Path(__file__).resolve().parents[2]
HUMAN_ID = re.compile(r"^human:\S+$")
REVIEWER_ID = re.compile(r"^(human|agent):\S+$")


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


def _t(i, skill, deps, gate, outs, executor="agent", **kw):
    d = {"id": i, "skill": skill, "executor": executor, "depends_on": deps, "gate": gate, "expected_outputs": outs, "inputs": []}
    d.update(kw)
    return d


def base_tasks():
    return [
        _t("T01", "uow-context-assembler", [], "CONTEXT_GATE", ["UCX"]),
        _t("T02", "uow-slice-designer", ["T01"], "SLICE_GATE", ["UOW"]),
    ]


def uow_tasks(u):
    """Cadena de una UOW: contratos y código en paralelo, luego plan del agente, revisión y aprobación humana."""
    return [
        _t(f"T03-{u}", "uow-contract-binder", ["T02"], "BINDING_GATE", ["UCB"], uow=u),
        _t(f"T04-{u}", "uow-codebase-mapper", ["T02"], "CODEBASE_GATE", ["UCM"], uow=u),
        _t(f"T05-{u}", "uow-agent-execution-planner", [f"T03-{u}", f"T04-{u}"], "AGENT_PLAN_GATE", ["UAP"], uow=u),
        _t(f"T06-{u}", "uow-readiness-reviewer", [f"T05-{u}"], "READINESS_GATE", ["UWR"], uow=u),
        _t(f"T07-{u}", "uow-orchestrator", [f"T06-{u}"], "UOW_READY_GATE", ["uow-package"], executor=ORCH, uow=u),
    ]


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

    Un runner se omite si falta alguno de sus parámetros ({pack}, {uow}); sus checks
    caen entonces en la atestación humana. Un runner que falla al ejecutarse o reporta error rechaza el gate.
    """
    verify = verify or {}
    out = {}
    for r in load_policies()[gate].get("runners") or []:
        needed = set(re.findall(r"\{(\w+)\}", " ".join(r["args"])))
        if any(not verify.get(k) for k in needed):
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


def authoritative_checks(gate, tid, author, declared, verify):
    """Resultado definitivo de cada check de la política (fail-closed, sin PASS declarados no verificables).

    - evaluator `script`: manda el resultado del verificador ejecutado por el orquestador; si no hay verificador
      que lo cubra, un PASS solo se acepta con `attested_by: human:<id>` (atestación humana registrada).
    - evaluator `independent-review`: un PASS exige `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor.
    Un FAIL/UNCERTAIN declarado se acepta siempre (es el lado seguro).
    """
    pol = load_policies()[gate]["checks"]
    ran = run_gate_scripts(gate, verify, tid)
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


def commit_exists(repo, commit):
    """Verifica con `git cat-file -e <commit>^{commit}` que el commit existe en el repositorio indicado."""
    if not commit or not re.fullmatch(r"[0-9a-fA-F]{4,64}", str(commit)):
        return False, f"commit inválido: {commit}"
    try:
        p = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"no se pudo ejecutar git en {repo}: {e}"
    return (True, "") if p.returncode == 0 else (False, f"el commit {commit} no existe en {repo}")


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
        elif self.plan.get("expanded") and all(v["status"] == "CANCELLED" or (v["status"] == "COMPLETED" and v["gate_status"] in GATE_OK) for v in ts):
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
    def init(self, plan_id, us, objective, mode, baseline=None, dsp=None, scope=None, max_parallel=4, halt_scope="all"):
        if (self.root / "plan.yaml").exists():
            raise Reject("el plan ya existe: no se sobrescribe estado operativo")
        if mode not in MODES:
            raise Reject(f"modo inválido: {mode}")
        pol = load_policies()
        tasks = base_tasks()
        for t in tasks:
            t["acceptance_criteria"] = [c["id"] for c in pol[t["gate"]]["checks"] if c.get("required")]
        us = dict(us)
        us["digest"] = file_digest(us["path"]) if us.get("path") and Path(us["path"]).exists() else None
        plan = {"schema_version": SCHEMA, "pack_name": PACK, "plan_id": plan_id, "mode": mode, "workflow_modes": MODES,
                "us_ref": us, "dsp_ref": dsp or None, "baseline": baseline or None, "objective": objective, "scope": scope or {},
                "expanded": False, "uows": [], "planning_gate": "G0", "plan_revision": 1,
                "max_parallel_tasks": max_parallel, "halt_scope": halt_scope,
                "gate_policies": {k: {"mode": v["mode"], "max_retries": v["max_retries"],
                                       "waiver_allowed": v["waiver_allowed"]} for k, v in pol.items()},
                "tasks": tasks}
        st = {"schema_version": "1.0", "execution_id": f"UOWEXEC-{int(time.time())}", "status": "BLOCKED",
              "plan_revision": 1, "planning_gate": {"id": "G0", "status": "BLOCKED", "evidence_refs": []},
              "tasks": {t["id"]: self._new_status() for t in tasks},
              "human_intervention": []}
        self.plan, self.st, self.tasks = plan, st, {t["id"]: t for t in tasks}
        self._open_hi("G0", "Esperando validación de planificación", "Ejecutar g0 con evidencia")
        self.save()
        self.log(ORCH, "INIT", None, None, {"status": "BLOCKED"})
        return {"status": "BLOCKED", "planning_gate": "BLOCKED", "tasks": [t["id"] for t in tasks]}

    @staticmethod
    def _new_status():
        return {"status": "PENDING", "gate_status": "PENDING", "authorization": None, "evidence_refs": [],
                "attempts": 0, "technically_completed": False, "observations": []}

    def expand(self, actor, uows):
        """Fan-out por UOW tras un SLICE_GATE en PASS. uows: [{"id": "UOW-001", "depends_on": []}]."""
        self._need_orch(actor, "expand")
        if self.plan.get("expanded"):
            raise Reject("expand ya se aplicó: una nueva partición en UOW exige un plan nuevo")
        s2 = self.st["tasks"]["T02"]
        if not (s2["status"] == "COMPLETED" and s2["gate_status"] in GATE_OK):
            raise Reject("expand exige T02 COMPLETED con SLICE_GATE en PASS: la partición en UOW la valida el gate")
        ids = [u.get("id") for u in uows or []]
        bad = [i for i in ids if not UOW_ID.match(str(i))]
        if not ids or bad or len(ids) != len(set(ids)):
            raise Reject(f"UOW inválidas, duplicadas o ausentes: {bad or ids}")
        unknown = [d for u in uows for d in u.get("depends_on", []) if d not in ids]
        if unknown:
            raise Reject(f"dependencias entre UOW desconocidas: {unknown}")
        if validate_dag([{"id": u["id"], "depends_on": list(u.get("depends_on", []))} for u in uows]):
            raise Reject("ciclo de dependencias entre UOW")
        pol = load_policies()
        new = []
        for u in ids:
            new += uow_tasks(u)
        for t in new:
            t["acceptance_criteria"] = [c["id"] for c in pol[t["gate"]]["checks"] if c.get("required")]
        self.plan["tasks"] += new
        self.plan["uows"] = [{"id": u["id"], "depends_on": list(u.get("depends_on", []))} for u in uows]
        self.plan["expanded"] = True
        self.st["plan_revision"] += 1
        self.plan["plan_revision"] = self.st["plan_revision"]
        for t in new:
            self.st["tasks"][t["id"]] = self._new_status()
        self.tasks = {t["id"]: t for t in self.plan["tasks"]}
        errs = validate_dag(self.plan["tasks"])
        if errs:
            raise Reject("DAG inválido tras expand: " + ", ".join(errs))
        self.save()
        self.log(ORCH, "EXPAND", None, None, {"uows": ids, "plan_revision": self.st["plan_revision"]})
        return {"expanded": ids, "tasks": [t["id"] for t in new], "plan_revision": self.st["plan_revision"]}

    def g0(self, actor):
        self._need_orch(actor, "g0")
        p, checks = self.plan, []
        errs = validate_dag(p["tasks"])
        checks.append({"id": "dag-valid", "result": "FAIL" if errs else "PASS", "evidence_ref": "plan.yaml", "detail": errs})
        d = p["us_ref"]
        placeholders = any("<" in str(x) for x in (d.get("id"), d.get("version"), d.get("path")))
        inputs_ok = bool(d.get("id") and d.get("version") and d.get("path") and d.get("digest")) and not placeholders
        checks.append({"id": "inputs-identified", "result": "PASS" if inputs_ok else "FAIL", "evidence_ref": "plan.yaml#us_ref"})
        crit = all(t["acceptance_criteria"] and t["expected_outputs"] and t["gate"] in p["gate_policies"] for t in p["tasks"])
        checks.append({"id": "criteria-defined", "result": "PASS" if crit else "FAIL", "evidence_ref": "plan.yaml#tasks"})
        b = p.get("baseline") or {}
        mode_ok = p.get("mode") in MODES and (p["mode"] == "GREENFIELD" or bool(b.get("ref") and b.get("commit")))
        checks.append({"id": "mode-declared", "result": "PASS" if mode_ok else "FAIL", "evidence_ref": "plan.yaml#mode",
                       "detail": [] if mode_ok else ["BROWNFIELD y EVOLUTION exigen baseline.ref y baseline.commit"]})
        if b.get("repo"):  # D-23: con --baseline-repo, el commit debe existir en ese repositorio
            ok, why = commit_exists(b["repo"], b.get("commit"))
            checks.append({"id": "baseline-commit-exists", "result": "PASS" if ok else "FAIL", "evidence_ref": "plan.yaml#baseline",
                           "detail": [] if ok else [why]})
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
        verify = dict(verify or {})
        verify.setdefault("uow", t.get("uow"))
        checks = authoritative_checks(t["gate"], tid, t["skill"], checks, verify)
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
    """Los argumentos --checks, --human-approval, --waiver y --scope-json son la RUTA de un archivo JSON, no el JSON en línea."""
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf8"))
    except OSError:
        raise Reject(f"no se puede leer '{path}': el argumento espera la ruta de un archivo JSON, no el JSON en línea")
    except ValueError as e:
        raise Reject(f"'{path}' no contiene JSON válido: {e}")


def _pathmap():
    for d in Path(__file__).resolve().parents:
        f = d / "assets" / "pathmap.json"
        if f.is_file(): return json.loads(f.read_text(encoding="utf8"))
    raise SystemExit("assets/pathmap.json no encontrado")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="./" + _pathmap()["orchestrator_root"].strip("/"))  # campo orchestrator_root de pathmap.json
    ap.add_argument("--actor", default=ORCH)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("init")
    for k in ("plan-id", "us-id", "us-version", "us-path", "objective", "mode"):
        a.add_argument("--" + k, required=True)
    a.add_argument("--baseline-ref")
    a.add_argument("--baseline-commit")
    a.add_argument("--baseline-repo", help="ruta del repositorio git donde se verifica que baseline-commit existe (opcional)")
    a.add_argument("--dsp-id")
    a.add_argument("--scope-json")
    a.add_argument("--max-parallel", type=int, default=4)
    a.add_argument("--halt-scope", choices=["all", "dependents"], default="all")
    a = sp.add_parser("expand")
    a.add_argument("--uows", required=True, help="UOW-001,UOW-002")
    a.add_argument("--depends", action="append", default=[], help="UOW-002=UOW-001 (orden de desarrollo)")
    sp.add_parser("g0")
    sp.add_parser("status")
    sp.add_parser("eligible")
    a = sp.add_parser("authorize"); a.add_argument("--task", required=True); a.add_argument("--human-approval", help="ruta de un ARCHIVO JSON {approved, actor, evidence_ref, artifact_revision}; no el JSON en línea"); a.add_argument("--artifact-revision"); a.add_argument("--ttl-minutes", type=int, default=240)
    a = sp.add_parser("verify-authorization"); a.add_argument("--task", required=True); a.add_argument("--auth-id", required=True); a.add_argument("--token")
    a = sp.add_parser("start"); a.add_argument("--task", required=True); a.add_argument("--auth-id", required=True)
    a = sp.add_parser("complete"); a.add_argument("--task", required=True); a.add_argument("--output", action="append", default=[])
    a = sp.add_parser("gate"); a.add_argument("--task", required=True); a.add_argument("--checks", required=True, help="ruta de un ARCHIVO JSON con los checks (lista o {\"checks\": [...]})"); a.add_argument("--human-approval", help="ruta de un ARCHIVO JSON {approved, actor, evidence_ref, artifact_revision}; no el JSON en línea")
    a.add_argument("--pack", help="raíz de los documentos de las UOW (p. ej. ./management/uows) para que el orquestador ejecute check_uow_package.py")
    a = sp.add_parser("human"); a.add_argument("--id", required=True); a.add_argument("--decision", required=True); a.add_argument("--evidence", required=True); a.add_argument("--note", default="")
    a = sp.add_parser("reopen"); a.add_argument("--task", required=True); a.add_argument("--reason", required=True)
    a = sp.add_parser("invalidate"); a.add_argument("--tasks", required=True); a.add_argument("--reason", required=True)
    a = sp.add_parser("waive"); a.add_argument("--task", required=True); a.add_argument("--waiver", required=True)
    a = sp.add_parser("cancel"); a.add_argument("--task", required=True); a.add_argument("--justification", required=True); a.add_argument("--evidence", required=True)
    args = ap.parse_args(argv)
    rt = Runtime(args.root)
    try:
        with rt.lock():
            if args.cmd == "init":
                base = {"ref": args.baseline_ref, "commit": args.baseline_commit, **({"repo": args.baseline_repo} if args.baseline_repo else {})} if (args.baseline_ref or args.baseline_commit) else None
                out = rt.init(args.plan_id, {"id": args.us_id, "version": args.us_version, "path": args.us_path},
                              args.objective, args.mode, base, args.dsp_id, _jload(args.scope_json),
                              args.max_parallel, args.halt_scope)
            else:
                rt.load()
                c = args.cmd
                if c == "g0": out = rt.g0(args.actor)
                elif c == "expand":
                    deps = {}
                    for d in args.depends:
                        a_, _, b_ = d.partition("=")
                        deps.setdefault(a_, []).append(b_)
                    out = rt.expand(args.actor, [{"id": u, "depends_on": deps.get(u, [])} for u in args.uows.split(",")])
                elif c == "status": out = rt.status()
                elif c == "eligible": out = rt.eligible()
                elif c == "authorize": out = rt.authorize(args.actor, args.task, _jload(args.human_approval), args.artifact_revision, args.ttl_minutes)
                elif c == "verify-authorization": out = rt.verify_authorization(args.task, args.auth_id, args.token)
                elif c == "start": out = rt.start(args.actor, args.task, args.auth_id)
                elif c == "complete": out = rt.complete(args.actor, args.task, args.output)
                elif c == "gate": out = rt.gate(args.actor, args.task, _jload(args.checks), _jload(args.human_approval), {"pack": args.pack})
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
