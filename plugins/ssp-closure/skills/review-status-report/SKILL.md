---
name: review-status-report
description: Recuperar y clasificar hechos de estado de historias y casos de prueba del SSP, con referencias verificables, sin métricas de tiempo.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "specialist"
---

# Review Status Report

## Activación y alcance

Invocar para recopilar el estado del periodo previo a Sprint Review. Produce datos operativos que el orchestrator consolida en el `STR`; no publica un documento por separado. La plantilla final es propiedad del orchestrator.

## Entradas

`project_id`, `ssp_id`/milestone, periodo, issues User Story y Task, consultas/exportaciones autorizadas y referencias de fuente.

## Procedimiento

1. Verificar cobertura del milestone y fecha de extracción.
2. Agrupar historias y casos de prueba por estado; conservar ID y referencia de issue por fila y cifra.
3. No añadir horas, estimados ni gasto. Si faltan datos o hay inconsistencia, informarlo como limitación/bloqueo.
4. Guardar payload estructurado sin frontmatter en `.comsatel/ssp-closure/runs/<run-id>/task-results/T2/status-data.json`.
5. Proponer `REVIEW_REPORT_GATE` con periodo cubierto, cobertura, fuentes y faltantes.

## Salida y gate

Payload consumido por el orchestrator para generar un `STR` en `management/status-reports/`. No es documento OKF ni un tipo nuevo. Sin acceso o datos fiables, `BLOCKED`; no completar desde memoria.

## Restricciones

Lectura solamente. No modificar issues, no aprobar aceptación ni gate y no declarar integración GitLab si la consulta fue manual o basada en exportación.
