#!/usr/bin/env python3
"""Inicialización y control declarativo de runs del plugin ssp-closure.

No autentica actores, consulta GitLab ni aprueba decisiones de negocio/calidad.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
PATHMAP = json.loads((PLUGIN / "assets" / "pathmap.json").read_text(encoding="utf-8-sig"))
ORCHESTRATOR_ROOT = PATHMAP["operational_artifacts"]["orchestrator_root"]
TASKS = [
    {"id": "T1", "skill": "review-agenda", "gate": "REVIEW_AGENDA_GATE", "depends_on": []},
    {"id": "T2", "skill": "review-status-report", "gate": "REVIEW_REPORT_GATE", "depends_on": ["REVIEW_AGENDA_GATE"]},
    {"id": "T3", "skill": "retro-agenda", "gate": "RETRO_AGENDA_GATE", "depends_on": ["REVIEW_AGENDA_GATE", "REVIEW_REPORT_GATE"]},
    {"id": "T4", "skill": "retro-experiment-tracker", "gate": "RETRO_TRACKER_GATE", "depends_on": ["RETRO_AGENDA_GATE"]},
    {"id": "T5", "skill": "release-readiness", "gate": "RELEASE_READINESS_GATE", "depends_on": ["REVIEW_REPORT_GATE"]},
]
GATES = [task["gate"] for task in TASKS]


def validate_run_id(run_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", run_id)) and run_id not in {".", ".."}


def run_dir(root: Path, run_id: str) -> Path:
    if not validate_run_id(run_id):
        raise ValueError("run-id inválido; use letras, números, punto, guion o guion bajo (1–100 caracteres).")
    return root / ORCHESTRATOR_ROOT / run_id


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def cmd_init(root: Path, run_id: str, project_id: str, ssp_id: str, period: str) -> int:
    rd = run_dir(root, run_id)
    if rd.exists():
        print(f"El run {run_id} ya existe; no se sobrescribió.")
        return 1
    rd.mkdir(parents=True)
    (rd / "task-results").mkdir()
    (rd / "evidence").mkdir()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for task in TASKS:
        (rd / "task-results" / task["id"]).mkdir()
        (rd / "evidence" / task["gate"]).mkdir()
    save(rd / "run-manifest.json", {
        "schema_version": "1.0.0", "run_id": run_id, "plugin": "ssp-closure",
        "project_id": project_id, "ssp_id": ssp_id, "period": period,
        "workflow_scope": ["sprint-review", "sprint-retrospective", "release-readiness"],
        "product_lifecycle_mode": "not-applicable", "pathmap_version": PATHMAP["pathmap_version"],
        "created_at": now,
    })
    save(rd / "execution-plan.json", {"schema_version": "1.0.0", "run_id": run_id, "tasks": TASKS})
    save(rd / "gate-register.json", {
        "schema_version": "1.0.0", "run_id": run_id,
        "gates": {g: {"status": "PENDING_PROPOSAL", "approved": False, "proposal": None, "approval": None} for g in GATES},
    })
    print(f"Run {run_id} creado en {rd}")
    return 0


def load_register(root: Path, run_id: str):
    path = run_dir(root, run_id) / "gate-register.json"
    if not path.is_file():
        print(f"No existe el registro de gates para el run {run_id}.")
        return None
    return path, json.loads(path.read_text(encoding="utf-8"))


def cmd_status(root: Path, run_id: str) -> int:
    loaded = load_register(root, run_id)
    if loaded is None:
        return 1
    for gate, record in loaded[1]["gates"].items():
        proposal = record["proposal"]
        result = proposal["result"] if proposal else "NO_PROPOSAL"
        print(f"{gate}: {record['status']} (proposal={result})")
    return 0


def cmd_propose(root: Path, run_id: str, gate: str, result: str, evidence: list[str], checks: list[str]) -> int:
    loaded = load_register(root, run_id)
    if loaded is None:
        return 1
    path, data = loaded
    if gate not in data["gates"]:
        print(f"Gate desconocido: {gate}")
        return 1
    if result not in {"READY", "NOT_READY", "UNCERTAIN", "BLOCKED"}:
        print("Resultado inválido; use READY, NOT_READY, UNCERTAIN o BLOCKED.")
        return 1
    refs = [item.strip() for item in evidence if item.strip()]
    if result == "READY" and (not refs or not checks):
        print("Una propuesta READY requiere al menos una referencia de evidencia y un check.")
        return 1
    proposal = {
        "result": result, "checks": checks, "evidence_refs": refs,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
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
    if not actor.startswith("human:") or len(actor) <= len("human:"):
        print("El actor debe tener la forma human:<nombre>.")
        return 1
    if not evidence.strip():
        print("La referencia a la decisión humana no puede estar vacía.")
        return 1
    proposal = data["gates"][gate]["proposal"]
    if not proposal or proposal["result"] != "READY" or not proposal["evidence_refs"]:
        print("No se aprueba: falta propuesta READY con evidencia.")
        return 1
    task = next(item for item in TASKS if item["gate"] == gate)
    unmet = [dep for dep in task["depends_on"] if not data["gates"][dep]["approved"]]
    if unmet:
        print("No se aprueba: gates previos pendientes: " + ", ".join(unmet))
        return 1
    record = data["gates"][gate]
    record["status"] = "APPROVED"
    record["approved"] = True
    record["approval"] = {
        "actor_declaration": actor, "actor_authenticated_by_script": False,
        "decision_evidence_ref": evidence,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save(path, data)
    print(f"{gate} registrado como aprobado por declaración {actor}; el script no autentica identidad.")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Control operativo de runs de ssp-closure")
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init")
    init.add_argument("run_id")
    init.add_argument("--root", default=".")
    init.add_argument("--project-id", required=True)
    init.add_argument("--ssp-id", required=True)
    init.add_argument("--period", required=True)
    for name in ("status",):
        cmd = sub.add_parser(name)
        cmd.add_argument("run_id")
        cmd.add_argument("--root", default=".")
    proposal = sub.add_parser("propose-gate")
    proposal.add_argument("run_id")
    proposal.add_argument("--gate", required=True)
    proposal.add_argument("--result", required=True)
    proposal.add_argument("--check", action="append", default=[])
    proposal.add_argument("--evidence", action="append", default=[])
    proposal.add_argument("--root", default=".")
    approve = sub.add_parser("approve-gate")
    approve.add_argument("run_id")
    approve.add_argument("--gate", required=True)
    approve.add_argument("--actor", required=True)
    approve.add_argument("--evidence", required=True)
    approve.add_argument("--root", default=".")
    args = p.parse_args(argv[1:])
    try:
        root = Path(args.root).resolve()
        if args.cmd == "init":
            return cmd_init(root, args.run_id, args.project_id, args.ssp_id, args.period)
        if args.cmd == "status":
            return cmd_status(root, args.run_id)
        if args.cmd == "propose-gate":
            return cmd_propose(root, args.run_id, args.gate, args.result, args.evidence, args.check)
        return cmd_approve(root, args.run_id, args.gate, args.actor, args.evidence)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
