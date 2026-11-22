---
name: retro-experiment-tracker
description: Convertir acciones de mejora aprobadas en payloads de issues de GitLab y seguir sus referencias, exigiendo dueño, métrica y fecha de cierre.
metadata:
  version: "1.0.0"
  author: "COMSATEL"
  type: "specialist"
---

# Retro Experiment Tracker

## Activación y alcance

Invocar solo para acciones acordadas explícitamente durante una retrospectiva. No crea un tipo documental ni reporta resultados no medidos.

## Entradas

`project_id`, SSP, acuerdos confirmados, persona dueña, métrica y fecha de cierre anterior al siguiente SSP. GitLab project y permisos deben estar disponibles para publicar.

## Procedimiento

1. Validar los tres campos obligatorios y la evidencia del acuerdo.
2. Preparar un payload de issue por experimento en `.comsatel/ssp-closure/runs/<run-id>/task-results/T4/`.
3. Crear issues únicamente con autorización explícita y una integración autenticada disponible; si no, devolver payloads listos para publicación y marcar `NOT_PUBLISHED`.
4. Registrar IID/URL/estado devuelto, o motivo del bloqueo, como evidencia operativa.
5. Emitir `RETRO_TRACKER_GATE` con checks por experimento y referencias.

## Salida y gate

Payloads operativos de issues y estado (`CREATED`, `NOT_PUBLISHED`, `BLOCKED`); no son documentos OKF. `RETRO_TRACKER_GATE` queda `NOT_READY` si falta dueño, métrica, fecha válida o acuerdo.

## Restricciones

No modificar/cerrar issues ajenos, no publicar sin autorización, no fingir que hubo llamada a GitLab y no completar resultados antes de medir. Usar `templates/experiment-issue.md` como plantilla de payload.
