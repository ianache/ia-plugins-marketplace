---
type: QTD
title: "Test Data Plan"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-QTD-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, qtd]
pack: qa-sdlc-pack
skill: qa-test-design
generated:
  by: qa-test-design/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
---
# Test Data Plan
Responde **QUÉ datos se necesitan** para ejecutar el diseño. No elige el mecanismo físico de provisión (eso lo decide `qa-agentic-test-engineer` al materializar los TDR como TDA).
## Alcance
## Estrategia de datos de prueba
Preferir datos SYNTHETIC. Fuentes admitidas: SYNTHETIC, FIXTURE, REFERENCE, MASKED_COPY, GENERATED, SEEDED.
## Inventario de TDR
| TDR-ID | TC / TSN | Entidades | Tipo de fuente | PII | Estado |
|---|---|---|---|---|---|
| TDR-001 | TC-001 | <entidades> | SYNTHETIC | NONE | draft |
## Entidades, relaciones e invariantes
## Privacidad y masking
## Aislamiento y limpieza
## Riesgos de datos y preguntas abiertas
## Provenance
