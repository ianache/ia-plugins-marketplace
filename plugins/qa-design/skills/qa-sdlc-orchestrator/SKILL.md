---
name: qa-sdlc-orchestrator
description: Usar para planificar, controlar y reanudar un workflow QA completo sobre un DSP, resolviendo contratos, gates fail-closed, dependencias, paralelismo, intervención humana y publicación de Test Cases en GitLab sin ejecutar lógica QA de dominio.
metadata:
  version: "2.0.0"
  author: "COMSATEL"
  type: "qa"
---
# QA SDLC Orchestrator
Planner + execution controller. **Único escritor** del estado operativo en `.comsatel/qa-design/runs/<run-id>/` (`plan.yaml`, `plan-status.yaml`, `tasks/<id>/task-status.yaml`, `events.jsonl`, `evidence/`). Excepción acotada: los especialistas escriben solo su `gate-report-<TASK_ID>.yaml` (gate_proposal) en `evidence/<GATE>/`; el orquestador no lo sobrescribe y registra sus intentos como `<TASK_ID>-attemptN.yaml`. No ejecuta lógica QA especializada. Lee `resources/orchestration.md`.
## Required
objective, DSP id/versión/ruta, gitlab_id, surfaces, available_artifacts y decisiones upstream. Para publicar: `GITLAB_PAT` solo en runtime, `kb_local_path` y `kb_gitlab_url` por TC.
## Canonical entities
`DSP→US→RISK→TSN→TC→AT→EXEC→EVD→DEFECT→QUALITY_DECISION`.
## Coordinación dinámica por Test Case
```
TC
├── MANUAL → ejecución manual → EXEC
└── AUTOMATED → AT
    ├── AUTOMATED_STANDALONE → EXEC
    └── AUTOMATED_CICD → GitLab pipeline → job → EXEC
EXEC → EVD → revisión → Quality Intelligence
```
El `execution_mode` (`MANUAL`, `AUTOMATED_STANDALONE`, `AUTOMATED_CICD`) pertenece a cada `EXEC`, no al TC; no confundir con `scheduling_mode` (SEQUENTIAL, PARALLEL_ELIGIBLE) de las tareas del plan ni con `workflow_modes` (GREENFIELD, BROWNFIELD, EVOLUTION). Ninguna EXEC que dependa de datos pasa a READY sin TDR/TDA obligatorios o una excepción aprobada: `python scripts/exec_readiness.py --pack <engineering-pack> --design-pack <design-pack>` lo comprueba (solo lectura). Cada re-run genera una EXEC nueva (`rerun_of`) y conserva el historial. El orquestador coordina; no diseña, no materializa datos ni ejecuta pruebas.
## Plan (DAG)
`G0` (barrera global) → T01 feature-analysis → T02 test-design → T03 test-design-review → { T04 publish-testcase-issues ‖ T05-<surface> test-engineering por surface } → T06 engineering-review (espera todas las T05) → T07 quality-intelligence → T08 human-quality-gate. T04 y T08 las ejecuta el orquestador (`executor: orchestrator`).
**Alcance DSP y SSP.** El plan se ejecuta sobre un DSP y, opcionalmente, sobre un SSP (`init --ssp-id <SSP> --ssp-path management/sprints/SSP-*.md`). Con SSP, G0 añade `ssp-identified` (el documento sigue siendo el de `init`, verificado por digest) y `ssp-belongs-to-dsp` (el `dsp_id` que declara el SSP coincide con el DSP del plan). Sin SSP, G0 registra `ssp-scope` como alcance DSP completo. Cada T05 recibe `scope_ssp` (sus TC se limitan al SSP). En T05-API, un subordinado por microservicio API y tipo de prueba: `SUB-<ms>-FUN` (postman-automation) y `SUB-<ms>-CARGA` (loadtest-automation), declarados en `scope.microservices` por `api_id` (sin TC en `init`). Tras T03, cada TC API declara su `api_id` (frontmatter) y los subordinados se crean a partir de esos TC (`rendimiento` → CARGA, resto → FUN). G0 añade `subordinates-declared`: superficie API sin microservicios bloquea el plan; T03 añade `tc-api-assigned`. El engineer invoca esos subordinados (ver `qa-agentic-test-engineer`, sección de automatización API).
## Operación (scripts/qa_orchestrator.py)
`init` → `g0` → `authorize` → `start` → `complete` → `gate`; `human`, `reopen`, `invalidate`, `cancel`, `waive`, `status`, `eligible`, `verify-authorization`.
- Una tarea se autoriza solo con G0 PASS y dependencias `COMPLETED` + gate `PASS|WAIVED`; nunca por la existencia de archivos.
- Estados de tarea: PENDING, AUTHORIZED, IN_PROGRESS, COMPLETED, BLOCKED, FAILED, CANCELLED. Gates: PENDING, PASS, FAIL, BLOCKED, WAIVED, NOT_APPLICABLE. Plan: PLANNED, IN_PROGRESS, BLOCKED, COMPLETED, FAILED. Migración desde 5.1 en `resources/contracts/common-contract.yaml`.
- Los especialistas entregan `gate_proposal`; el orquestador evalúa con `gate_governance.decide()` y registra el evento. `gate` **ejecuta por su cuenta** los verificadores `runners` de `resources/gate-policies.yaml` (`--pack`, `--design-pack`, `--critical-risks`) y su resultado manda sobre cualquier PASS declarado. Un check `script` sin verificador solo pasa con `attested_by: human:<id>`; un `independent-review` solo pasa con `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor de la tarea. Falta de check, evidencia ausente o `UNCERTAIN` no aprueban.
- `BLOCKED`/`FAIL` agotado abre `human_intervention` y detiene la ejecución. La decisión humana (`REVALIDATE`, `REWORK`, `CANCEL`) no equivale a PASS: se reevalúa el gate.
- **Sin PASS parcial.** Lo diferido se declara en `deferred_items` con `decision_ref`; si no, el gate falla.
- T04 (publicación) y T08 (decisión de calidad) son `MANDATORY_HIL`: aprobación humana ligada a la revisión exacta (digest) del artefacto. T04 solo publica `TC-*` aprobados, nunca TSN (`scripts/publish_testcase_issues.py`).
- Cambio de DSP: `invalidate --tasks …` reinicia esas tareas y sus sucesores y revoca autorizaciones.
- El runtime debe invocar `verify-authorization` antes de cada especialista.
## Invariant
El orquestador no calcula riesgos, no diseña TSN/TC, no implementa AT y no interpreta calidad.

## Plantillas
- Los registros operativos de control del flujo están en `templates/`: `gate-report.yaml` (lo escriben los especialistas como gate_proposal; el orquestador lo lee). Son registros operativos sin `type` OKF.
