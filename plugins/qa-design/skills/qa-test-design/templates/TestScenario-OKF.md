---
type: TSN
title: "Test Scenario"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-TSN-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, tsn]
pack: qa-sdlc-pack
skill: qa-test-design
generated:
  by: qa-test-design/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
dsp_ref: <DSP-ID>@<versión>
user_stories: [US-XXX]
acceptance_criteria: [AC-1]
risks: [RISK-XXX]
surfaces: [API]
priority: P1
test_cases: [TC-XXX]
---
# TSN-XXX — <título>
## Qué validar
Situación o comportamiento de alto nivel.
## Trazabilidad
DSP → US (AC) → RISK → TSN → TC
## Casos de prueba
- TC-XXX
