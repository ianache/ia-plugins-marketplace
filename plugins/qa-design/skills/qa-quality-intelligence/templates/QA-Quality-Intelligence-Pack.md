---
type: QQI
title: "QA Quality Intelligence Pack"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-QQI-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, qqi]
pack: qa-sdlc-pack
skill: qa-quality-intelligence
generated:
  by: qa-quality-intelligence/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
---
# QA Quality Intelligence Pack
## Propósito y alcance
## Insumos y procedencia
## Desarrollo
## Decisiones y supuestos (marcar [I] las inferencias)
## Relaciones
## Limitaciones y preguntas abiertas
## Validación

## Cobertura y confianza sobre la cadena DSP → … → QUALITY_DECISION
## Segmentación y métricas
Segmentar por `execution_mode` (MANUAL, AUTOMATED_STANDALONE, AUTOMATED_CICD), `automation_status`, test surface, entorno, pipeline, suite, riesgo y requisito. Métricas: cobertura de ejecución manual, cobertura de automatización, tasa de ejecución standalone y CI/CD, pass/fail/error/blocked, tests flaky, tasa de re-run, duración, completitud de evidencia, readiness TDR/TDA, detección de defectos por modo y cobertura de riesgos críticos.
## Clasificación de fallas
Una falla de pipeline o job no es una falla funcional: clasificar la causa (`failure_class`) antes de contarla.
## Recomendación
READY | READY_WITH_RISK | NOT_READY | INSUFFICIENT_EVIDENCE (la decisión final es humana).
