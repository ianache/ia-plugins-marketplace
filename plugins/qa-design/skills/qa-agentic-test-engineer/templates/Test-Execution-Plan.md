---
type: QTE
title: "QA Test Engineering Pack"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-QTE-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, qte]
pack: qa-sdlc-pack
skill: qa-agentic-test-engineer
generated:
  by: qa-agentic-test-engineer/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
---
# Test Execution Plan
## Superficie y entorno autorizado
## TC a ejecutar (manual / automatizado)
Por cada TC: `automation_status` y los modos de ejecución previstos.
## Modos de ejecución
- MANUAL: sin AT; ejecutor, entorno y evidencia.
- AUTOMATED_STANDALONE: AT, runtime autorizado y versión.
- AUTOMATED_CICD: AT, especificación CI/CD y GitLab pipeline/job como execution engine.
## Harness y framework resueltos desde el contexto
## Datos y credenciales (solo referencias)
## Evidencia esperada y reproducibilidad
## Riesgos y acciones prohibidas (PROD, destructivas)
