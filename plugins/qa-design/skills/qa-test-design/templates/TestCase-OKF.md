---
type: TC
title: "Test Case"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-TC-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, tc]
pack: qa-sdlc-pack
skill: qa-test-design
generated:
  by: qa-test-design/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
tc_contract: "1.4"
tsn: TSN-XXX
dsp_ref: <DSP-ID>@<versión>
user_stories: [US-XXX]
acceptance_criterion: AC-1
risks: [RISK-XXX]
surface: API
surface_target_id: <identificador-estable>
api_id: <identificador-del-microservicio>   # obligatorio si surface: API
test_level: integration   # unit | integration | system | e2e | security | performance
test_type: positivo   # positivo | negativo | seguridad | rendimiento | regresion
priority: P1   # P0 | P1 | P2 | P3
criticality: HIGH   # CRITICAL | HIGH | MEDIUM | LOW
automation_status: MANUAL_ONLY   # MANUAL_ONLY | AUTOMATION_CANDIDATE | PARTIALLY_AUTOMATED | AUTOMATED
data_required: true
tdr_refs: [TDR-XXX]
---
# TC-XXX — <título>
## Intención
<Una sola intención verificable, alineada con TSN, RISK y requisito. No repetir el título ni introducir alcance nuevo.>
## Elemento bajo prueba (Surface Target)
| Campo | Valor verificable |
|---|---|
| Surface | <API/WEB/MOBILE/DATABASE/EVENT/BATCH/INTEGRATION/CROSS_SURFACE> |
| Producto / aplicación / servicio | <identificador> |
| Elemento bajo prueba | <nombre e identificador> |
| Ambiente / versión / build | <valor> |
| Acceso / invocación | <valor> |
| Contrato o especificación | <referencia versionada> |

### Detalles específicos del Surface
| Atributo | Valor |
|---|---|
| <atributo requerido> | <valor concreto> |

## Precondiciones
| PC-ID | Estado inicial requerido | Cómo comprobarlo | Preparación / dependencia |
|---|---|---|---|
| PC-01 | <estado exacto> | <consulta o verificación> | <fixture / ambiente> |

## Datos de prueba
| TD-ID | TDR-ID | Técnica/estrategia | Partición/límite/condición | Valor exacto o dataset@versión/fila | Razón de selección | Origen | Preparación/seed | Cleanup |
|---|---|---|---|---|---|---|---|---|
| TD-01 | TDR-XXX | <equivalence/boundary/decision-table/state-transition/pairwise/negative/security> | <partición o límite> | <valor o referencia reproducible> | <por qué esta técnica para este riesgo> | <synthetic/fixture/reference/masked_copy/generated/seeded> | <script/seed> | <reversión> |

## Pasos
| STEP-ID | Acción concreta | Datos TD-ID | Resultado esperado observable | Evidencia |
|---|---|---|---|---|
| STEP-01 | <acción explícita> | TD-01 | <aserción concreta> | <respuesta/log/UI/consulta> |

## Resultado esperado (oracle)
| OR-ID | Aserción exacta | Fuente AC/BR/API | Método de observación | Tolerancia |
|---|---|---|---|---|
| OR-01 | <status/campo/estado/evento exacto> | <AC-1@versión / BR-XXX@versión / API@versión> | <cómo medir/verificar> | <valor o no aplica> |

Pass when:
- <condición observable que determina el PASS>

Fail when:
- <condición observable que determina el FAIL>

## Postcondiciones y limpieza
- Estado final verificable: <estado>.
- Idempotencia: <sí/no y cómo se re-ejecuta sin efectos acumulados>.
- cleanup.required: <true|false>
- cleanup.strategy_ref: <TDR-XXX o null; obligatorio si cleanup.required es true>
- Cleanup/rollback: <pasos o script>.

## Requisitos de evidencia
- MANUAL: <execution_result, response_capture>
- AUTOMATED_STANDALONE: <test_report, execution_log>
- AUTOMATED_CICD: <test_report, pipeline_job_reference, execution_log>
(Usar `none` si una modalidad no aplica. Esta sección define requisitos, no resultados.)

## Restricciones de ejecución
- allowed_environments: <QA, CERTIFICATION>
- forbidden_environments: PRODUCTION
- destructive: <true|false>
- requires_human_authorization: <true|false; obligatorio true si destructive es true>

## Trazabilidad
Representación del frontmatter; no es una fuente independiente. Debe coincidir con él.
- dsp_ref: <DSP-ID>@<versión>
- user_stories: [US-XXX]
- risks: RISK-XXX
- tsn: TSN-XXX

## Automatización
- Estado: ver `automation_status` en el frontmatter (el modo de ejecución pertenece a cada EXEC, no al TC).
- automated_test_refs: []
