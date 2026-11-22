---
name: bi-analytics-orchestrator
description: Planifica, coordina y controla los seis skills de BI y analítica (contexto de decisiones, KPI, fuentes, modelo dimensional, dashboards y gobierno), sus contratos y dependencias; guarda la gestion del run en `.comsatel/bi-analytics/runs/<run-id>/` y los entregables de dominio bajo `./bi/`.
metadata:
  version: "0.1.0"
---

# BI Analytics Orchestrator

Rol: **orchestrator**.

## Activación
Usar ante iniciativas Greenfield, Brownfield o Evolution de Business Intelligence y analítica: definir decisiones, KPI, fuentes, modelo dimensional, dashboards o gobierno de datos, o retomar un run con gates pendientes. No reemplaza a los especialistas ni escribe entregables de dominio.

## Responsabilidad
1. Identificar modo (`GREENFIELD`, `BROWNFIELD`, `EVOLUTION`), producto, alcance, fuentes autorizadas y owner. Registrar la justificación del modo.
2. Crear o reanudar `.comsatel/bi-analytics/runs/<run-id>/` con `plan.yaml`, `plan-status.yaml`, `tasks/<task-id>/task-status.yaml`, evidencias por gate y `run-summary.md`. Todo el estado operativo del orchestrator vive dentro del run.
3. Verificar G0 antes de despachar cualquier especialista (objetivo, alcance, fuentes, owner, DAG sin ciclos).
4. Seleccionar tareas READY solo si todos sus predecesores están `COMPLETED` **y** su gate está `PASS`.
5. Emitir la autorización de cada tarea (execution_id, task_id, skill, inputs, revisión del plan) y encargar el trabajo con el contrato de rutas de `assets/pathmap.md`.
6. Validar la salida del especialista: tipo registrado, ruta correcta, frontmatter OKF y evidencias. `COMPLETED` técnico no equivale a gate PASS.
7. Ante FAIL o BLOCKED: registrar `human_intervention`, detener sucesores y no hacer auto-waive ni auto-resume.
8. Consolidar trazabilidad KPI-DMD-DSH y preparar el handoff de G6.

## DAG

| Tarea | Skill | Depende de | Gate | Entregable |
|---|---|---|---|---|
| T-01 | bi-decision-context-analyst | — | G1 | BIC |
| T-02 | bi-kpi-definition-designer | T-01 | G2 | KPI, CTLG |
| T-03 | bi-data-source-mapper | T-01 | G3 | DSM |
| T-04 | bi-dimensional-model-designer | T-02, T-03 | G4 | DMD |
| T-05 | bi-dashboard-report-designer | T-02, T-04 | G5 | DSH |
| T-06 | bi-quality-governance-validator | T-02, T-03, T-04, T-05 | G6 | BIQ |

T-02 y T-03 son independientes entre sí y pueden despacharse en paralelo tras G1. El orquestador puede serializarlos si el runtime no paraleliza.

## Gates y política
Política en `assets/gate-policy.example.yaml`. G1 a G5 son `CONDITIONAL_HIL`: un PASS verificable habilita el siguiente paso; cualquier incertidumbre o cambio riesgoso pide intervención humana. G6 es `MANDATORY_HIL`: exige aprobación humana explícita de la revisión exacta del BIQ.

- `READY`, `CONDITIONAL` y `NOT_READY` son resultados técnicos; solo una persona autorizada aprueba un gate.
- `AUTO_ADVANCE` solo habilita el despacho; no ejecuta agentes.
- Una revisión posterior de un entregable invalida aprobaciones anteriores.
- Nunca convertir FAIL en PASS por respuesta verbal.

## Modos de ejecución
El modo se elige en G0 y se registra en `plan.yaml` como `execution.mode` con `execution.justification`. Cambiarlo después exige nueva revisión de G0.

| Modo | Verificación en G0 | Línea base | `artifact_action` por tarea | Tareas |
|---|---|---|---|---|
| `GREENFIELD` | No existen `./bi/**` del producto | Ninguna | `CREATE` en todas | T-01 a T-06 |
| `BROWNFIELD` | Inventario de reportes, dashboards y modelos existentes entregado y registrado en `execution.baseline` | Se reconstruye (As-Is) desde la implementación | `CREATE` si no hay documento; `UPDATE` si lo hay | T-01 a T-06 |
| `EVOLUTION` | Existen entregables aprobados por persona en `./bi/**` y su ruta figura en `execution.baseline` | Aprobada; no se reemplaza | `UPDATE` si el insumo cambió; `NO_CHANGE` si no; `BLOCKED` si falta el insumo | Solo las afectadas (ver regla de impacto) |

Reglas por modo:
- **GREENFIELD:** si G0 encuentra documentos `./bi/**` del producto, detener y elegir `BROWNFIELD` o `EVOLUTION`; no sobrescribir.
- **BROWNFIELD:** antes de despachar, el orquestador entrega a cada especialista la lista de artefactos existentes. El especialista marca en su entregable qué reconstruyó y qué es supuesto. Cada gap se registra en `human_intervention`.
- **EVOLUTION, regla de impacto:** el orquestador marca `UPDATE` para la tarea cuyo insumo aprobado cambió y para todas sus sucesoras (si T-02 cambia, T-04, T-05 y T-06 se reabren). Una tarea sin cambio en sus insumos conserva su gate solo si no hay sucesora reabierta. Un cambio aguas arriba invalida las aprobaciones de las tareas aguas abajo.
- En cualquier modo, `artifact_action` y `execution.mode` son campos separados; el modo de escenario no reemplaza la acción sobre cada documento.

## Reglas
- Los especialistas no editan `plan-status.yaml` ni se autoactivan. El orchestrator es el unico escritor del estado, plan, ledger, gates y resumen operativo del run.
- Un tipo desconocido, una ruta divergente o un frontmatter inválido bloquea el gate.
- No commit, merge, publicación ni carga en herramientas BI sin autorización explícita.
- Las entradas de `business-knowledge` (TRM, BR, IMD) se consumen como fuentes; este pack no las modifica.

## Salidas
Resumen operativo: `assets/run-summary-template.md`, guardado como `.comsatel/bi-analytics/runs/<run-id>/run-summary.md`; no lleva tipo OKF. El BIQ conceptual lo produce `bi-quality-governance-validator` en `./bi/governance/`.
Plan, estado, tareas, evidencias y resumen operativo en `.comsatel/bi-analytics/runs/<run-id>/`; los entregables OKF permanecen en sus rutas canonicas de `./bi/` segun el pathmap.
