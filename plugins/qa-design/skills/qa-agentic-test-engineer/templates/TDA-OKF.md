---
type: TDA
title: "Test Data Asset"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-TDA-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, tda]
pack: qa-sdlc-pack
skill: qa-agentic-test-engineer
generated:
  by: qa-agentic-test-engineer/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
tdr_ref: TDR-XXX
testcase_refs: [TC-XXX]
asset_kind: dataset   # dataset | fixture | factory | seed | setup | cleanup
source_type: SYNTHETIC   # SYNTHETIC | FIXTURE | REFERENCE | MASKED_COPY | GENERATED | SEEDED
path: test-data/datasets/<archivo>
sha256: null
readiness: PENDING   # PENDING | READY | FAILED
contains_pii: false
contains_secrets: false
---
# TDA-XXX — <título>
## TDR que materializa
## Mecanismo de provisión
## Determinismo y aislamiento
## Limpieza
## Validación de preparación
## Privacidad y secretos
Preferir datos sintéticos; referencias a secretos, nunca valores.
