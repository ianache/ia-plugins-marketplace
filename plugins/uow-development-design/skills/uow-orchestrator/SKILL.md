---
name: uow-orchestrator
description: "Usar para planificar, controlar y reanudar la conversión de una User Story, el diseño de API y el diseño de BD en Unidades de Trabajo (UOW) asignables a un developer con agente IA, con gates fail-closed, intervención humana y aprobación del paquete ligada a su digest, sin diseñar ni redactar el contenido de la UOW."
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Orchestrator
Planner + execution controller. **Único escritor** del estado operativo en `.comsatel/uow-development-design/runs/` (`plan.yaml`, `plan-status.yaml`, `tasks/<id>/task-status.yaml`, `events.jsonl`, `evidence/`). Excepción acotada: los especialistas escriben solo su `gate-report-<TASK_ID>.yaml` (gate_proposal) en `evidence/<GATE>/`. No diseña UOW, contratos ni planes de ejecución. Lee `resources/orchestration.md`.
## Required
User Story (id, versión, ruta), objetivo, **modo** (`GREENFIELD`, `BROWNFIELD` o `EVOLUTION`) y, en Brownfield y Evolution, la línea base (`ref` y `commit`). Opcional: DSP o SSP de origen. Los demás insumos (FDT, contratos API, BD, UX, ADR, HCB) los reúne T01.
## Plan (DAG)
`G0` → `T01` contexto → `T02` slice → **`expand`** (una cadena por UOW) → `T03-<uow>` contratos ‖ `T04-<uow>` código → `T05-<uow>` plan del agente → `T06-<uow>` revisión → `T07-<uow>` aprobación humana del paquete.
- `expand --uows UOW-001,UOW-002 [--depends UOW-002=UOW-001]` solo se acepta con T02 `COMPLETED` y `SLICE_GATE` en PASS. La partición en UOW la valida el gate, no el orquestador.
- Cada UOW avanza de forma independiente. T07 la ejecuta el orquestador y `UOW_READY_GATE` es `MANDATORY_HIL`: la aprobación humana queda ligada al digest exacto del paquete (`uow-package.yaml`).
- Hasta `UOW_READY_GATE` en PASS la UOW no se asigna a nadie. La asignación es de Gestión (project-management).
## Operación (scripts/uow_orchestrator.py)
`init` → `g0` → `authorize` → `start` → `complete` → `gate`; `expand`, `human`, `reopen`, `invalidate`, `cancel`, `waive`, `status`, `eligible`, `verify-authorization`.
- Una tarea se autoriza solo con G0 PASS y dependencias `COMPLETED` con gate `PASS|WAIVED`; nunca por la existencia de archivos.
- Los especialistas entregan `gate_proposal`; el orquestador evalúa con `gate_governance.decide()` y registra el evento. `gate --pack <raíz>` **ejecuta por su cuenta** `check_uow_package.py` (los `runners` de `resources/gate-policies.yaml`; `{uow}` sale de la tarea) y su resultado manda sobre cualquier PASS declarado. Un check `script` sin verificador solo pasa con `attested_by: human:<id>`; un `independent-review` solo con `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor. Un check faltante, evidencia ausente o `UNCERTAIN` no aprueban.
- `BLOCKED` o `FAIL` agotado abre una `human_intervention` y detiene la ejecución. Una decisión humana (`REVALIDATE`, `REWORK`, `CANCEL`) no equivale a PASS: se reevalúa el gate.
- **Sin PASS parcial.** Lo diferido se declara con decisión humana o el gate falla.
- `python scripts/uow_package.py build --root <dir> --uow UOW-001` genera `uow-package.yaml` (documentos, sha256 y digest) antes de T07.
- El runtime debe invocar `verify-authorization` antes de cada especialista.
## Insumos existentes
Consume por ID y versión lo que producen los demás plugins (`US`, `DSP`, `SSP`, `FDT`, `API`, `LDM`, `PDM`, `DBM`, `HOF`, `WEB`, `MOB`, `HCB`, `ADR`, `ASR`); no los copia ni redefine. No existe un "Development Context Pack" único: se referencia el que corresponda.
## Invariant
El orquestador no decide alcance, no modela contratos, no analiza código y no redacta planes para el agente.
