# Reglas locales del orquestador

- Único escritor de estado operativo en `.comsatel/uow-development-design/runs/`: `plan.yaml`, `plan-status.yaml`, `tasks/<id>/task-status.yaml`, `events.jsonl` (append-only) y `evidence/`. Se opera con `scripts/uow_orchestrator.py`.
- Excepción acotada: cada especialista escribe solo su `gate-report-<TASK_ID>.yaml` (gate_proposal) en `evidence/<GATE>/`.
- Orden obligatorio: `init` → `g0` (PASS con evidencia) → `authorize` → `start` → `complete` → `gate`. G0 verifica DAG, entradas (US con digest), criterios y modo (Brownfield y Evolution exigen línea base).
- `expand` crea la cadena T03..T07 de cada UOW, solo con T02 `COMPLETED` y `SLICE_GATE` en PASS, y una sola vez. Una nueva partición en UOW exige un plan nuevo.
- Una tarea solo se autoriza si `G0` es PASS y todas sus dependencias están `COMPLETED` con gate `PASS` o `WAIVED`. `COMPLETED` técnico no es gate PASS.
- `BLOCKED`/`FAIL` agotado abre `human_intervention` y detiene la ejecución. La decisión humana no reanuda: obliga a reevaluar el gate.
- `UOW_READY_GATE` es `MANDATORY_HIL`: aprobación humana ligada a la revisión exacta (digest) del paquete. Una revisión posterior invalida la aprobación.
- El runtime debe llamar a `verify-authorization` antes de invocar un especialista.
- Cambio de la US: `invalidate --tasks <ids>` reinicia esas tareas y sus sucesores y revoca autorizaciones.
- Prohibido el PASS parcial.
