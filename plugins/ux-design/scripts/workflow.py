#!/usr/bin/env python3
"""Control operativo del plugin ux-design; no publica ni autentica aprobaciones."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
PATHMAP = json.loads((PLUGIN / "assets" / "pathmap.json").read_text(encoding="utf-8-sig"))
RUN_ROOT = PATHMAP["operational_artifacts"]["orchestrator_root"]
TASKS = [
    {"id": f"T-{i:02d}", "skill": skill, "gate": f"G{i}", "depends_on": [f"G{i-1}"] if i else []}
    for i, skill in enumerate([
        "ux-ui-orchestrator", "ux-requirements-analyzer", "user-flow-designer", "ui-spec-writer",
        "stitch-ui-generator|claude-design-orchestrator", "accessibility-reviewer",
        "figma-design-validator", "ux-development-handoff",
    ])
]
GATES = [f"G{i}" for i in range(8)]

def safe_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", value)) and value not in {".", ".."}

def run_dir(root: Path, run_id: str) -> Path:
    if not safe_id(run_id):
        raise ValueError("run-id inválido; use letras, números, punto, guion o guion bajo (1–100 caracteres).")
    return root / RUN_ROOT / run_id

def save(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def cmd_init(root: Path, run_id: str, initiative: str, mode: str, scenario: str, baseline: str | None) -> int:
    rd = run_dir(root, run_id)
    if mode not in {"greenfield", "brownfield", "evolution"}:
        raise ValueError("mode debe ser greenfield, brownfield o evolution")
    if scenario not in list("ABCDEFG"):
        raise ValueError("scenario UX debe ser una ruta A–G")
    if mode in {"brownfield", "evolution"} and not (baseline and baseline.strip()):
        raise ValueError("brownfield y evolution requieren --baseline verificable")
    if mode == "greenfield" and baseline:
        raise ValueError("greenfield no acepta baseline como línea base existente")
    if rd.exists():
        print(f"El run {run_id} ya existe; no se sobrescribió.")
        return 1
    rd.mkdir(parents=True)
    (rd / "task-results").mkdir()
    (rd / "evidence").mkdir()
    for task in TASKS:
        (rd / "task-results" / task["id"]).mkdir()
        (rd / "evidence" / task["gate"]).mkdir()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save(rd / "run-manifest.json", {"schema_version": "1.0.0", "plugin": "ux-design", "run_id": run_id,
        "initiative": initiative, "lifecycle_mode": mode, "ux_scenario": scenario, "baseline_ref": baseline,
        "pathmap_version": PATHMAP["pathmap_version"], "status": "IN_PROGRESS", "created_at": now})
    save(rd / "execution-plan.json", {"schema_version": "1.0.0", "run_id": run_id, "tasks": TASKS})
    save(rd / "plan-status.json", {"schema_version": "1.0.0", "run_id": run_id,
        "tasks": {t["id"]: {"status": "PENDING", "gate": t["gate"]} for t in TASKS}})
    save(rd / "gate-register.json", {"schema_version": "1.0.0", "run_id": run_id,
        "gates": {g: {"status": "PENDING_PROPOSAL", "approved": False, "proposal": None, "approval": None} for g in GATES}})
    print(f"Run {run_id} creado en {rd}")
    return 0

def load_register(root: Path, run_id: str):
    path = run_dir(root, run_id) / "gate-register.json"
    if not path.is_file():
        print(f"No existe el run {run_id}.")
        return None
    return path, json.loads(path.read_text(encoding="utf-8"))

def cmd_status(root: Path, run_id: str) -> int:
    loaded = load_register(root, run_id)
    if loaded is None:
        return 1
    for gate, record in loaded[1]["gates"].items():
        result = record["proposal"]["result"] if record["proposal"] else "NO_PROPOSAL"
        print(f"{gate}: {record['status']} (proposal={result})")
    return 0

def cmd_propose(root: Path, run_id: str, gate: str, result: str, checks: list[str], evidence: list[str]) -> int:
    loaded = load_register(root, run_id)
    if loaded is None:
        return 1
    path, data = loaded
    if gate not in data["gates"]:
        print(f"Gate desconocido: {gate}")
        return 1
    if result not in {"READY", "CONDITIONAL", "NOT_READY", "BLOCKED"}:
        print("Resultado inválido.")
        return 1
    evidence = [e.strip() for e in evidence if e.strip()]
    if result == "READY" and (not checks or not evidence):
        print("READY requiere al menos un check y una referencia de evidencia.")
        return 1
    proposal = {"result": result, "checks": checks, "evidence_refs": evidence,
                "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    data["gates"][gate].update({"status": "PENDING_APPROVAL", "approved": False, "proposal": proposal, "approval": None})
    save(path.parent / "evidence" / gate / "gate-proposal.json", proposal)
    save(path, data)
    print(f"Propuesta {result} registrada para {gate}; requiere decisión humana.")
    return 0

def cmd_approve(root: Path, run_id: str, gate: str, actor: str, evidence: str) -> int:
    loaded = load_register(root, run_id)
    if loaded is None:
        return 1
    path, data = loaded
    if gate not in data["gates"]:
        print(f"Gate desconocido: {gate}")
        return 1
    if not actor.startswith("human:") or len(actor) <= len("human:") or not evidence.strip():
        print("Requiere --actor human:<id> y una referencia de evidencia no vacía.")
        return 1
    proposal = data["gates"][gate]["proposal"]
    if not proposal or proposal["result"] != "READY" or not proposal["evidence_refs"]:
        print("No se aprueba sin propuesta READY y evidencia.")
        return 1
    index = GATES.index(gate)
    if index and not data["gates"][GATES[index - 1]]["approved"]:
        print(f"No se aprueba: {GATES[index - 1]} sigue pendiente.")
        return 1
    record = data["gates"][gate]
    record["status"] = "APPROVED"
    record["approved"] = True
    record["approval"] = {"actor_declaration": actor, "actor_authenticated_by_script": False,
                          "decision_evidence_ref": evidence,
                          "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    save(path, data)
    print(f"{gate} registrado como aprobado por declaración; el script no autentica identidad.")
    return 0

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Control de runs ux-design")
    sub = parser.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init")
    init.add_argument("run_id"); init.add_argument("--root", default=".")
    init.add_argument("--initiative", required=True)
    init.add_argument("--mode", required=True, choices=["greenfield", "brownfield", "evolution"])
    init.add_argument("--scenario", required=True, choices=list("ABCDEFG")); init.add_argument("--baseline")
    status = sub.add_parser("status"); status.add_argument("run_id"); status.add_argument("--root", default=".")
    propose = sub.add_parser("propose-gate")
    propose.add_argument("run_id"); propose.add_argument("--gate", required=True); propose.add_argument("--result", required=True)
    propose.add_argument("--check", action="append", default=[]); propose.add_argument("--evidence", action="append", default=[]); propose.add_argument("--root", default=".")
    approve = sub.add_parser("approve-gate")
    approve.add_argument("run_id"); approve.add_argument("--gate", required=True); approve.add_argument("--actor", required=True)
    approve.add_argument("--evidence", required=True); approve.add_argument("--root", default=".")
    args = parser.parse_args(argv[1:])
    try:
        root = Path(args.root).resolve()
        if args.cmd == "init":
            return cmd_init(root, args.run_id, args.initiative, args.mode, args.scenario, args.baseline)
        if args.cmd == "status":
            return cmd_status(root, args.run_id)
        if args.cmd == "propose-gate":
            return cmd_propose(root, args.run_id, args.gate, args.result, args.check, args.evidence)
        return cmd_approve(root, args.run_id, args.gate, args.actor, args.evidence)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
