"""Local single-writer workflow engine. All plan mutations via this module or its CLI."""
from pathlib import Path
import argparse, json, os, tempfile, hashlib, datetime, uuid, sys
try: import yaml
except ImportError as e: raise ImportError("workflow.py requires PyYAML (pip install pyyaml)") from e
ROOT=Path(__file__).resolve().parents[1]
def _yaml(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf8"))
_SM=_yaml("resources/state-machine.yaml")
STATES=set(_SM["states"])
TRANSITIONS={k:set(v) for k,v in _SM["transitions"].items()}
RESULT_STATUSES=tuple(_SM["specialist_result_statuses"])
SPECIALISTS={s["name"] for s in _yaml("resources/skill-registry.yaml")["skills"] if s["role"]=="specialist"}
MODES=("greenfield","brownfield","evolution")
def _pathmap():
    for d in Path(__file__).resolve().parents:
        f=d/"assets"/"pathmap.json"
        if f.is_file(): return json.loads(f.read_text(encoding="utf-8"))
    raise SystemExit("assets/pathmap.json no encontrado")
ORCH_ROOT=_pathmap()["orchestrator_root"].strip("/")  # campo orchestrator_root de pathmap.json
def run_dir(run_id,root="."):
    return Path(root)/ORCH_ROOT/run_id
def check_layout(plan_path):
    """STD-OKF-001: operational files live in <orchestrator_root>/<run-id>/."""
    base=Path(ORCH_ROOT).parts; parts=Path(plan_path).resolve().parts
    if len(parts)<len(base)+2 or tuple(parts[-len(base)-2:-2])!=base: raise ValueError(f"plan must live in {ORCH_ROOT}/<run-id>/ (use --run-id)")
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _atomic(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=".plan-")
    try:
        with os.fdopen(fd,"w",encoding="utf8") as f:
            json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def _event(path,**kw):
    with Path(str(path)+".events.jsonl").open("a",encoding="utf8") as f:f.write(json.dumps(dict(kw,at=utc()))+"\n")
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def default_graph(mode):
    if mode not in MODES: raise ValueError("mode")
    data=_yaml("assets/dependency-map.yaml")
    return [dict(t) for t in data["modes"][mode]["tasks"]],[dict(g) for g in data["gates"]]
def create(path,mode,task_specs=None,gate_specs=None):
    if mode not in MODES: raise ValueError("mode")
    if task_specs is None:
        task_specs,default_gates=default_graph(mode)
        if gate_specs is None: gate_specs=default_gates
    gate_specs=gate_specs or []
    ids=[x["id"] for x in task_specs]; gids=[g["id"] for g in gate_specs]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate tasks")
    if len(gids)!=len(set(gids)): raise ValueError("duplicate gates")
    for x in task_specs:
        if any(d not in ids or d==x["id"] for d in x.get("depends_on",[])): raise ValueError("invalid dependency")
        if any(g not in gids for g in x.get("requires_gates",[])): raise ValueError("unknown gate")
        if x.get("skill") and x["skill"] not in SPECIALISTS: raise ValueError("unknown skill")
    for g in gate_specs:
        if any(t not in ids for t in g.get("after",[])): raise ValueError("gate references unknown task")
    graph={x["id"]:x.get("depends_on",[]) for x in task_specs}
    done=set()
    def visit(k,stack):
        if k in stack: raise ValueError("dependency cycle")
        if k in done: return
        for d in graph[k]:visit(d,stack|{k})
        done.add(k)
    for k in ids:visit(k,set())
    tasks={x["id"]:dict(x,status="PENDING",execution_id=None,evidence=[],history=[]) for x in task_specs}
    gates={g["id"]:{"title":g.get("title",g["id"]),"after":g.get("after",[]),"status":"PENDING"} for g in gate_specs}
    plan={"id":"INPLAN-"+uuid.uuid4().hex[:12],"mode":mode,"revision":0,"owner":"infrastructure-orchestrator","tasks":tasks,"gates":gates,"updated_at":utc()}
    _atomic(path,plan);return plan
def load(path): return json.loads(Path(path).read_text(encoding="utf8"))
def _blockers(plan,t):
    out=[d for d in t.get("depends_on",[]) if plan["tasks"][d]["status"]!="COMPLETED"]
    return out+[g for g in t.get("requires_gates",[]) if plan["gates"].get(g,{}).get("status")!="APPROVED"]
def update(path,task_id,to,*,execution_id=None,evidence=None,reason=None,expected_revision=None,submitted=None):
    plan=load(path)
    if expected_revision is not None and plan["revision"]!=expected_revision:raise ValueError("stale revision")
    t=plan["tasks"][task_id]; old=t["status"]
    if to not in TRANSITIONS[old]:raise ValueError(f"invalid transition {old}->{to}")
    if to=="READY":
        if any(plan["tasks"][d]["status"]!="COMPLETED" for d in t.get("depends_on",[])):raise ValueError("dependencies incomplete")
        if any(plan["gates"].get(g,{}).get("status")!="APPROVED" for g in t.get("requires_gates",[])):raise ValueError("required gates not approved")
    if to=="IN_PROGRESS":
        if not execution_id:execution_id=uuid.uuid4().hex
        t["execution_id"]=execution_id
    elif old in ("IN_PROGRESS","IN_REVIEW") and execution_id!=t["execution_id"]:
        raise ValueError("stale execution id")
    if to=="COMPLETED":
        if not evidence:raise ValueError("evidence required")
        for entry in evidence:
            if not Path(entry["path"]).is_file():raise ValueError("evidence missing")
            if _sha(entry["path"])!=entry.get("sha256"):raise ValueError("evidence hash mismatch")
        t["evidence"]=evidence
    if to in ("BLOCKED","FAILED","SKIPPED") and not reason:raise ValueError("reason required")
    if submitted is not None:t["submitted"]=submitted
    t["status"]=to;t["history"].append({"at":utc(),"from":old,"to":to,"execution_id":execution_id,"reason":reason})
    plan["revision"]+=1;plan["updated_at"]=utc();_atomic(path,plan)
    _event(path,task=task_id,to=to,revision=plan["revision"])
    return plan
def refresh(path):
    """Move every PENDING task whose dependencies are COMPLETED and gates APPROVED to READY."""
    moved=[]
    for tid,t in load(path)["tasks"].items():
        if t["status"]=="PENDING" and not _blockers(load(path),t):
            update(path,tid,"READY");moved.append(tid)
    return moved
def ready(path):
    plan=load(path)
    return [tid for tid,t in plan["tasks"].items() if t["status"]=="READY"]
def approve_gate(path,gate,actor,evidence):
    if not actor or not evidence:raise ValueError("human approval evidence required")
    if not str(actor).startswith("human:"):raise ValueError("gate actor must be human:<id>")
    plan=load(path)
    if gate not in plan["gates"]:raise ValueError("unknown gate")
    pending=[t for t in plan["gates"][gate]["after"] if plan["tasks"][t]["status"]!="COMPLETED"]
    if pending:raise ValueError("tasks not completed: "+", ".join(pending))
    plan["gates"][gate].update(status="APPROVED",actor=actor,evidence=evidence,at=utc())
    plan["revision"]+=1;plan["updated_at"]=utc();_atomic(path,plan)
    _event(path,gate=gate,actor=actor,revision=plan["revision"])
    return plan
def submit_result(path,result_path):
    """Ingest a specialist task-result.yaml. A specialist may only report IN_REVIEW, BLOCKED or FAILED."""
    r=yaml.safe_load(Path(result_path).read_text(encoding="utf8")) or {}
    for k in ("task_id","execution_id","skill","status"):
        if not r.get(k):raise ValueError("result missing "+k)
    if r["status"] not in RESULT_STATUSES:raise ValueError("result status must be one of "+"/".join(RESULT_STATUSES))
    t=load(path)["tasks"].get(r["task_id"])
    if t is None:raise ValueError("unknown task")
    if t.get("skill") and t["skill"]!=r["skill"]:raise ValueError("skill mismatch")
    if r["status"]=="IN_REVIEW":
        arts=r.get("artifacts") or []
        if not arts:raise ValueError("artifacts required")
        for a in arts:
            if not Path(a["path"]).is_file():raise ValueError("artifact missing")
            if _sha(a["path"])!=a.get("sha256"):raise ValueError("artifact hash mismatch")
        return update(path,r["task_id"],"IN_REVIEW",execution_id=r["execution_id"],submitted={"artifacts":arts,"evidence":r.get("evidence") or [],"at":utc()})
    reason=r.get("blocked_reason") or "; ".join(map(str,r.get("errors") or []))
    return update(path,r["task_id"],r["status"],execution_id=r["execution_id"],reason=reason)
def _evidence(specs):
    return [{"path":p,"sha256":_sha(p)} for p in specs]
def main(argv=None):
    ap=argparse.ArgumentParser(prog="workflow.py",description=__doc__)
    sub=ap.add_subparsers(dest="cmd",required=True)
    def cmd(name,*args):
        p=sub.add_parser(name)
        p.add_argument("--run-id",help="run folder name; the plan is <orchestrator_root>/<run-id>/plan.json")
        p.add_argument("--root",default=".",help="project root that contains the orchestrator_root folder (default: current directory)")
        p.add_argument("--plan",help="explicit plan path; must still live in <orchestrator_root>/<run-id>/")
        for a,kw in args:p.add_argument(a,**kw)
        return p
    cmd("create",("--mode",dict(required=True,choices=MODES)),("--tasks",dict(help="JSON file with task specs; default: graph from assets/dependency-map.yaml")),("--gates",dict(help="JSON file with gate specs (only with --tasks)")))
    cmd("status"); cmd("ready"); cmd("refresh")
    cmd("update",("--task",dict(required=True)),("--to",dict(required=True,choices=sorted(STATES))),("--execution-id",dict()),("--reason",dict()),("--expected-revision",dict(type=int)),("--evidence",dict(nargs="*",default=[],help="paths; sha256 is computed")),("--use-submitted",dict(action="store_true",help="COMPLETED with the artifacts the specialist submitted")))
    cmd("submit-result",("--result",dict(required=True)))
    cmd("approve-gate",("--gate",dict(required=True)),("--actor",dict(required=True,help="human:<id>")),("--evidence",dict(required=True,help="approval reference, e.g. MR-42")))
    a=ap.parse_args(argv)
    try:
        if a.run_id: a.plan=str(run_dir(a.run_id,a.root)/"plan.json")
        elif a.plan: check_layout(a.plan)
        else: raise ValueError("--run-id or --plan is required")
        if a.cmd=="submit-result" and Path(a.plan).resolve().parent not in Path(a.result).resolve().parents:
            raise ValueError("task result must be stored inside the run folder (e.g. <run>/task-results/)")
        if a.cmd=="create":
            tasks=json.loads(Path(a.tasks).read_text(encoding="utf8")) if a.tasks else None
            gates=json.loads(Path(a.gates).read_text(encoding="utf8")) if a.gates else None
            plan=create(a.plan,a.mode,tasks,gates); print(json.dumps({"id":plan["id"],"mode":plan["mode"],"tasks":list(plan["tasks"]),"gates":list(plan["gates"])},indent=2))
        elif a.cmd=="status":
            plan=load(a.plan); print(f"{plan['id']} mode={plan['mode']} revision={plan['revision']}")
            for tid,t in plan["tasks"].items():print(f"  {tid:<20} {t['status']:<12} {t.get('skill') or '-':<36} blockers={_blockers(plan,t) or '-'}")
            for gid,g in plan["gates"].items():print(f"  gate {gid:<34} {g['status']}")
        elif a.cmd=="ready": print(json.dumps(ready(a.plan)))
        elif a.cmd=="refresh": print(json.dumps(refresh(a.plan)))
        elif a.cmd=="update":
            ev=_evidence(a.evidence)
            if a.use_submitted:ev=load(a.plan)["tasks"][a.task].get("submitted",{}).get("artifacts",[])
            plan=update(a.plan,a.task,a.to,execution_id=a.execution_id,evidence=ev or None,reason=a.reason,expected_revision=a.expected_revision); print(json.dumps({"task":a.task,"status":plan["tasks"][a.task]["status"],"revision":plan["revision"]}))
        elif a.cmd=="submit-result":
            plan=submit_result(a.plan,a.result); print(json.dumps({"revision":plan["revision"]}))
        elif a.cmd=="approve-gate":
            plan=approve_gate(a.plan,a.gate,a.actor,a.evidence); print(json.dumps({"gate":a.gate,"status":plan["gates"][a.gate]["status"],"revision":plan["revision"]}))
    except (ValueError,KeyError,FileNotFoundError) as e:
        print("ERROR: "+str(e),file=sys.stderr); return 1
    return 0
if __name__=="__main__": sys.exit(main())
