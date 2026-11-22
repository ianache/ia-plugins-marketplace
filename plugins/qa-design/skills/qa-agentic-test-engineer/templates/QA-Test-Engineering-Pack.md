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
# QA Test Engineering Pack
## Propósito y alcance
## Insumos y procedencia
## Desarrollo
## Decisiones y supuestos (marcar [I] las inferencias)
## Relaciones
## Limitaciones y preguntas abiertas
## Validación

## Artefactos del pack
test-execution-plan.md, test-data-generation-plan.md, test-data-manifest.yaml, test-data/{datasets,fixtures,scripts}/,
automated-tests/AT-*, executions/EXEC-*, evidence/EVD-*, gate-report.yaml;
cicd/ci-test-execution.yaml y fragments gitlab-ci (solo si hay AUTOMATED_CICD).
## Trazabilidad
TC → TDR → TDA → EXEC → EVD; TC → AT? → EXEC.
## AT / EXEC / EVD
