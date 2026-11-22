# Reglas locales del orquestador

- Excepción acotada: cada especialista escribe solo su `gate-report-<TASK_ID>.yaml` (gate_proposal) en `evidence/<GATE>/`; el orquestador lo lee, no lo sobrescribe y sus intentos van como `<TASK_ID>-attemptN.yaml`.
- Único escritor de estado operativo en `.comsatel/qa-design/runs/<run-id>/`: `plan.yaml`, `plan-status.yaml`,
  `tasks/<id>/task-status.yaml`, `events.jsonl` (append-only) y `evidence/`. Se opera con `scripts/qa_orchestrator.py`.
- Orden obligatorio: `init` → `g0` (PASS con evidencia) → `authorize` → `start` → `complete` → `gate`.
- Una tarea solo se autoriza si `G0` es PASS y todas sus dependencias están `COMPLETED` con gate `PASS` o `WAIVED`.
- `COMPLETED` técnico no es gate PASS. El gate lo evalúa `gate_governance.decide()` con checks que cumplen
  `{id, result, evidence_ref}`; falta de un check requerido, evidencia ausente o `UNCERTAIN` no aprueban.
- `BLOCKED`/`FAIL` agotado abre `human_intervention` y detiene la ejecución (`halt_scope: all` por defecto).
  La decisión humana no reanuda: obliga a reevaluar el gate (`REVALIDATE`) o a `reopen`/`cancel`.
- `MANDATORY_HIL` (publicación a GitLab y decisión de calidad) exige aprobación humana ligada a la revisión exacta del artefacto.
- El runtime debe llamar a `verify-authorization` antes de invocar un especialista; un YAML por sí solo no impide
  una invocación fuera de banda.
- Cambio de DSP: `invalidate --tasks <ids>` reinicia esas tareas y sus sucesores, revoca autorizaciones y sube `plan_revision`.
- Prohibido el PASS parcial: lo diferido se declara con `deferred_items` y decisión humana, o el gate falla.
