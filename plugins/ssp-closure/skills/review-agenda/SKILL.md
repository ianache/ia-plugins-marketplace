---
name: review-agenda
description: Preparar una agenda y payload de acta de Sprint Review desde historias de un SSP; separar aceptación humana de preparación técnica y devolver propuesta de gate.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "specialist"
---

# Review Agenda

## Activación y alcance

Invocar para planificar Sprint Review de un SSP existente. No redacta un documento OKF independiente ni registra aceptación de historias.

## Entradas

- `project_id`, `ssp_id`/milestone y periodo.
- Issues de historias, estado, responsables de demo y criterios de aceptación con sus referencias.

## Procedimiento

1. Comprobar que cada historia del alcance tiene fuente y estado.
2. Ordenar presentaciones y asociar responsable de demo y criterios que se revisarán.
3. Preparar campos vacíos para la decisión del Product Owner; marcar como bloqueantes historias sin criterios.
4. No incluir métricas de horas/estimados/gasto.
5. Guardar payload Markdown sin frontmatter en `.comsatel/ssp-closure/runs/<run-id>/task-results/T1/review-agenda.md` y emitir gate proposal con checks y evidencia.

## Salida y gate

Payload operativo para la ceremonia, consumido luego como fuente del `CLS`; no tiene `type` OKF. `REVIEW_AGENDA_GATE`: lista completa, fuentes trazables, bloqueos identificados y aceptación sin prellenar. Sin datos de entrada, `BLOCKED`.

## Restricciones

Solo el Product Owner registra aceptación o rechazo. El skill no modifica GitLab ni gate-register. Usar `templates/agenda-payload.md` como estructura, no como documento publicable.
