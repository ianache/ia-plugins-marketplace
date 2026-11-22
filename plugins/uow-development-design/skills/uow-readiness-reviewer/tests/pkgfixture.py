"""Fixture compartido: construye un paquete UOW válido en un directorio temporal."""
import tempfile
from pathlib import Path

import yaml

SECTIONS = {
    "UCX": ["Alcance y modo", "Insumos", "Hechos", "Inferencias", "Supuestos", "Desconocidos y preguntas abiertas"],
    "UOW": ["Objetivo y resultado esperado", "Alcance", "Criterios de aceptación cubiertos", "Contratos y datos", "Mapa de código",
            "Dependencias", "Plan para el agente", "Criterios de terminado", "Dimensión", "Riesgos y preguntas abiertas", "Handoff a QA", "Trazabilidad"],
}


UCM_EVOLUTION_BODY = "## Compatibilidad hacia atr\u00e1s\nsin cambios de contrato\n## Rollback\nrevertir el MR\n"


def md(meta, body=""):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + body


def body(sig, alcance="**Incluye**\n- alta de cliente\n\n**Excluye**\n- baja de cliente\n"):
    out = ""
    for s in SECTIONS.get(sig, []):
        out += f"## {s}\n" + (alcance if s == "Alcance" else "contenido\n") + "\n"
    return out


def build(mode="GREENFIELD", **over):
    t = tempfile.TemporaryDirectory()
    root = Path(t.name) / "uows"
    (root / "UOW-001").mkdir(parents=True)
    base = {"status": "draft", "version": "1.0.0"}
    ucx = {**base, "type": "UCX", "id": "CL2-UCX-001", "us_ref": "US-001", "mode": mode, "acceptance_criteria": ["AC-1", "AC-2"],
           "baseline": {"ref": "main", "commit": "abc1234"} if mode != "GREENFIELD" else {"ref": None, "commit": None},
           "sources": [{"id": "US-001", "resource": "requirements/US-001.md", "version": "1.0.0"},
                       {"id": "FDT-001", "resource": "architecture/FDT-001.md", "version": "1.2.0"}]}
    uow = {**base, "type": "UOW", "id": "CL2-UOW-001", "us_ref": "US-001", "mode": mode, "scope_state": "IN_REVIEW",
           "acceptance_criteria": ["AC-1", "AC-2"], "depends_on_uow": [], "authored_by": ["agent:slice"], "open_questions": []}
    ucb = {**base, "type": "UCB", "id": "CL2-UCB-001", "uow_ref": "UOW-001", "authored_by": ["agent:binder"],
           "api_operations": [{"operation_id": "createCustomer", "method": "POST", "path": "/customers", "contract_ref": "API-001", "contract_version": "1.0.0", "fdt_ref": "FDT-001"}],
           "data_objects": [{"name": "customer", "schema_ref": "PDM-001", "version": "1.0.0"}],
           "api_fields": ["name", "email"],
           "mapping": [{"api_field": "name", "column": "customer.name"}, {"api_field": "email", "column": "customer.email"}]}
    ucm = {**base, "type": "UCM", "id": "CL2-UCM-001", "uow_ref": "UOW-001", "service_id": "customers", "authored_by": ["agent:mapper"],
           "repository": {"project": "customers-svc", "target_branch": "develop", "source_ref": "develop", "source_commit": "9f3c2ab"},
           "allowed_paths": ["src/customers/"], "forbidden_paths": ["src/shared/", "deploy/"], "adr_refs": ["ADR-004"],
           "existing_code_analysis": {"performed": mode != "GREENFIELD", "summary_ref": "analysis.md" if mode != "GREENFIELD" else None}}
    if mode == "EVOLUTION":
        ucm["backward_compatibility"] = {"assessed": True, "summary": "contratos v1 intactos"}
        ucm["rollback"] = {"defined": True, "summary": "revertir MR y bandera"}
    uap = {**base, "type": "UAP", "id": "CL2-UAP-001", "uow_ref": "UOW-001", "authored_by": ["agent:planner"], "profile": "claude-code-superpowers",
           "steps": [{"id": "S-01", "kind": "test", "goal": "prueba de alta", "files": ["src/customers/test_create.py"], "test_first": True,
                      "verify": "pytest -q", "expected": "falla"},
                     {"id": "S-02", "kind": "impl", "goal": "alta", "files": ["src/customers/create.py"], "test_first": True,
                      "verify": "pytest -q", "expected": "pasa"}],
           "stop_conditions": ["contrato ambiguo"], "deviation_protocol": {"escalate_to": "tech-lead", "record_in": "issue"},
           "definition_of_done": [{"id": "D-1", "check": "alta funciona", "verify": "pytest -q"}]}
    uwr = {**base, "type": "UWR", "id": "CL2-UWR-001", "uow_ref": "UOW-001", "reviewer": "human:reviewer", "recommendation": "READY_FOR_APPROVAL", "findings": []}
    docs = {"UCX-001-ctx.md": (ucx, body("UCX")), "UOW-001-alta.md": (uow, body("UOW"))}
    for k, (n, m) in {"UCB": ("UCB-001-alta.md", ucb), "UCM": ("UCM-001-alta.md", ucm), "UAP": ("UAP-001-alta.md", uap), "UWR": ("UWR-001-alta.md", uwr)}.items():
        docs[f"UOW-001/{n}"] = (m, UCM_EVOLUTION_BODY if k == "UCM" and mode == "EVOLUTION" else "")
    for name, (m, b) in docs.items():
        m.update(over.get(m["type"], {}))
        (root / name).write_text(md(m, b), encoding="utf8")
    return t, root
