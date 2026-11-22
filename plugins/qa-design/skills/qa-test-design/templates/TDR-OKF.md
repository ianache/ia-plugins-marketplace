---
type: TDR
title: "Test Data Requirement"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-TDR-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, tdr]
pack: qa-sdlc-pack
skill: qa-test-design
generated:
  by: qa-test-design/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
test_cases: [TC-XXX]
scenario_refs: [TSN-XXX]
source_type: SYNTHETIC   # SYNTHETIC | FIXTURE | REFERENCE | MASKED_COPY | GENERATED | SEEDED
pii: NONE   # NONE | SYNTHETIC | MASKED | REAL_AUTHORIZED (exige decision_ref)
decision_ref: null
---
# TDR-XXX — <título>
## Datos requeridos
Entidades y atributos que el TC necesita, en lenguaje verificable (sin elegir el mecanismo de provisión).
## Relaciones e invariantes
## Clases de equivalencia y valores límite
## Combinaciones positivas, negativas e inválidas
## Estado esperado
## Aislamiento y limpieza
## Privacidad y masking
## Procedencia
