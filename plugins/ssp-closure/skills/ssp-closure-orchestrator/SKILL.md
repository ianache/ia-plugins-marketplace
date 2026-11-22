---
name: ssp-closure-orchestrator
description: Coordina el cierre de un SSP: agenda Review, estado del periodo, Retrospective, seguimiento de experimentos y readiness, manteniendo plan, resultados, gates y evidencia bajo .comsatel/ssp-closure/runs/<run-id>.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "orchestrator"
---

# SSP Closure Orchestrator

## Activación y alcance

Usar para coordinar actividades de cierre de un SSP/milestone existente: Sprint Review, Retrospective y/o revisión de readiness previa al release. Acepta como contexto el modo de ciclo de vida del producto, pero no implementa Greenfield/Brownfield/Evolution ni reconstruye una línea base de producto.

## Entradas

`project_id`, `ssp_id`/milestone, periodo, actividades solicitadas, fuentes de historias/TC/defectos, resultados de Review y Retrospective cuando estén disponibles, evidencias de QA y persona responsable de aceptar historias. Registrar las referencias, no copiar secretos.

## Procedimiento

1. Leer `assets/pathmap.json` y `assets/pathmap.md`; validar identificadores y alcance solicitado.
2. Inicializar el run con `python scripts/workflow.py init <run-id> --root <workspace> --project-id <id> --ssp-id <ssp> --period <periodo>`.
3. Crear/usar únicamente `.comsatel/ssp-closure/runs/<run-id>/` como raíz operativa. El workflow genera `run-manifest.json`, `execution-plan.json`, `gate-register.json`, `task-results/` y `evidence/`.
4. Enrutar las tareas de `execution-plan.json` y pasar entradas, referencias de fuentes, precondiciones, tipo/ruta OKF y gate correspondiente.
5. Conservar los payloads de agenda, estado y readiness bajo `task-results/<task-id>/`; las propuestas y referencias de evidencia van bajo `evidence/<gate-id>/`. Los especialistas no editan plan ni gate-register.
6. Consolidar datos verificados en un único `STR` por periodo y un único `CLS` por SSP, usando `skills/ssp-closure-orchestrator/templates/status-report.md` y los destinos del pathmap. La consolidación no puede inferir aceptaciones, mediciones o decisiones.
7. Evaluar la propuesta técnica de cada gate; registrar el resultado humano solo cuando haya evidencia y aprobación externa. `approve-gate` captura una declaración de actor, no autentica identidad.
8. Validar documentos con `scripts/check_closure.py` y resolver bloqueos antes de cerrar el run. Conservar la evidencia y resultados; no borrar el directorio.

## Secuencia y dependencias

T1 `review-agenda` precede a T2 `review-status-report`; T3 `retro-agenda` consume los resultados de Review y entrega el CLS tras la ceremonia; T4 `retro-experiment-tracker` consume acciones acordadas; T5 `release-readiness` consume estado y evidencia de QA y aporta sus hallazgos al STR consolidado. Los especialistas emiten `gate_proposal`; el orquestador no aprueba automáticamente.

## Modos de operación

El alcance se selecciona por actividad (`sprint-review`, `sprint-retrospective`, `release-readiness`). Los modos Greenfield/Brownfield/Evolution no aplican al control de ceremonias: el plugin procesa un SSP y evidencia existentes. La ausencia de datos requeridos bloquea la tarea; no se sustituye con inferencias.

## Entregables y rutas

- `STR` en `management/status-reports/`, un informe por periodo.
- `CLS` en `management/closure/`, un cierre por SSP.
- Registros de run y payloads operativos bajo `.comsatel/ssp-closure/runs/<run-id>/`. El workflow crea subdirectorios `task-results/T1..T5/` y `evidence/<GATE>/`.

## Restricciones y limitaciones

No aceptar historias, no decidir calidad ni despliegue, no crear issues sin autorización y acceso GitLab, no afirmar que `project_id` fue consultado si no hubo integración, no tratar registro local como autenticación. El script solo comprueba estructura y declaraciones.
