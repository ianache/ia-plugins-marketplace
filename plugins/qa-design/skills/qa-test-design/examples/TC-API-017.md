---
type: TC
title: "Impedir acceso a vehículos de otro tenant"
description: "Verifica que un usuario del Tenant A no consulte un vehículo del Tenant B por la API de vehículos."
id: TC-API-017
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, tc, seguridad]
pack: qa-sdlc-pack
skill: qa-test-design
generated:
  by: qa-test-design/1.5.0
  at: "2026-11-04T10:00:00-05:00"
sources:
  - id: dsp
    resource: "dsp/DSP-001.md"
    title: "DSP-001@1.0"
tc_contract: "1.4"
tsn: TSN-001
dsp_ref: DSP-001
user_stories: [US-101]
acceptance_criterion: AC-1
risks: [RISK-001]
surface: API
surface_target_id: api-vehicles-get-v1
api_id: api-vehicles-v1
test_level: security
test_type: seguridad
priority: P0
criticality: CRITICAL
automation_status: AUTOMATION_CANDIDATE
data_required: true
tdr_refs: [TDR-017-01, TDR-017-02]
---
# TC-API-017 — Impedir acceso a vehículos de otro tenant

## Intención
Verificar que un usuario autenticado del Tenant A no pueda consultar información de un vehículo del Tenant B.

## Elemento bajo prueba (Surface Target)
| Campo | Valor verificable |
|---|---|
| Surface | API |
| Producto / aplicación / servicio | plataforma-vehiculos |
| Elemento bajo prueba | GET /vehicles/{vehicleId} (api-vehicles-get-v1) |
| Ambiente / versión / build | QA, build 2026.11.0 |
| Acceso / invocación | HTTPS sobre el gateway de QA |
| Contrato o especificación | OpenAPI vehicles-api@1.4.0 |

### Detalles específicos del Surface
| Atributo | Valor |
|---|---|
| api_id | api-vehicles-v1 |
| base_url_or_service | https://api-qa.example.internal/vehicles |
| http_method | GET |
| endpoint_path | /vehicles/{vehicleId} |
| operation_id | getVehicleById |
| request_contract | vehicles-api@1.4.0 |
| auth_scheme | bearer-token (referencia al secreto del entorno) |
| response_contract | vehicles-api@1.4.0 |

## Precondiciones
| PC-ID | Estado inicial requerido | Cómo comprobarlo | Preparación / dependencia |
|---|---|---|---|
| PC-01 | El usuario USER_A existe y pertenece al Tenant A | GET /users/{USER_A}/tenant devuelve Tenant A | Fixture de tenants |
| PC-02 | El vehículo VEH_B existe y pertenece al Tenant B | GET /admin/vehicles/{VEH_B} devuelve Tenant B | Fixture de tenants |
| PC-03 | USER_A tiene una sesión autenticada válida | Token de USER_A aceptado por GET /session | Entorno QA |

## Datos de prueba
| TD-ID | TDR-ID | Técnica/estrategia | Partición/límite/condición | Valor exacto o dataset@versión/fila | Razón de selección | Origen | Preparación/seed | Cleanup |
|---|---|---|---|---|---|---|---|---|
| TD-01 | TDR-017-01 | security | Usuario autenticado del Tenant A | tenants-fixture@1.2 fila 4 | Es el actor del ataque de acceso cruzado | synthetic | seed tenants-fixture | No requerido |
| TD-02 | TDR-017-02 | negative | Vehículo perteneciente a otro tenant | tenants-fixture@1.2 fila 17 | Caso de rechazo por tenant ajeno | synthetic | seed tenants-fixture | No requerido |

## Pasos
| STEP-ID | Acción concreta | Datos TD-ID | Resultado esperado observable | Evidencia |
|---|---|---|---|---|
| STEP-01 | Enviar GET /vehicles/{vehicleId} con el token de USER_A y vehicleId del TD-02 | TD-01, TD-02 | Respuesta HTTP 403 | Captura de respuesta |
| STEP-02 | Inspeccionar el cuerpo de la respuesta del STEP-01 | TD-02 | El cuerpo no contiene datos del vehículo ni del Tenant B | Cuerpo de respuesta |

## Resultado esperado (oracle)
| OR-ID | Aserción exacta | Fuente AC/BR/API | Método de observación | Tolerancia |
|---|---|---|---|---|
| OR-01 | Código de estado 403 | AC-1@1.0 / vehicles-api@1.4.0 | Código HTTP de STEP-01 | Exacto |
| OR-02 | Cuerpo sin campos del vehículo del Tenant B | AC-1@1.0 | Inspección del cuerpo de STEP-02 | Exacto |

Pass when:
- La solicitud es rechazada con HTTP 403.
- No se devuelve información del vehículo del Tenant B.
- No ocurre ningún cambio de estado no autorizado.

Fail when:
- Se devuelve información del vehículo del Tenant B.
- La solicitud responde con HTTP 2xx.
- Se expone información de otro tenant en cualquier campo de la respuesta.

## Postcondiciones y limpieza
- Estado final verificable: el vehículo del Tenant B y los permisos de USER_A no cambian.
- Idempotencia: sí; la consulta es de solo lectura y puede repetirse sin efectos.
- cleanup.required: false
- cleanup.strategy_ref: null
- Cleanup/rollback: no requerido.

## Requisitos de evidencia
- MANUAL: execution_result, response_capture
- AUTOMATED_STANDALONE: test_report, execution_log
- AUTOMATED_CICD: test_report, pipeline_job_reference, execution_log

## Restricciones de ejecución
- allowed_environments: QA, CERTIFICATION
- forbidden_environments: PRODUCTION
- destructive: false
- requires_human_authorization: false

## Trazabilidad
Representación del frontmatter; no es una fuente independiente. Debe coincidir con él.
- dsp_ref: DSP-001
- user_stories: [US-101]
- risks: RISK-001
- tsn: TSN-001

## Automatización
- Estado: ver `automation_status` en el frontmatter (el modo de ejecución pertenece a cada EXEC, no al TC).
- automated_test_refs: []
