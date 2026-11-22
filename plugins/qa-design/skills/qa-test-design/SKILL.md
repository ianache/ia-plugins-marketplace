---
name: qa-test-design
description: Usar cuando un QA Feature Analysis Pack aprobado deba convertirse en estrategia, condiciones, técnicas, Test Cases, datos y oracles trazables por API, WEB, MOBILE o CROSS_SURFACE.
metadata:
  version: "2.0.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Test Design
## Purpose
Definir **WHAT to test** con `TSN-*` y **HOW to verify** con `TC-*`.
## Required
QFA con FEATURE_ANALYSIS_GATE en PASS (verificado por el orquestador) y referencia DSP.
## Outputs
`QTD` con: `qa-test-strategy.md` (QTS), `qa-test-plan.md` y `test-prioritization.md` (QTP), `coverage-matrix.yaml`, `test-data-plan.md` (QTD), `requirements-test-traceability.yaml`, `TSN-*` (TSN), `TC-*` (TC), `TDR-*` (TDR), `test-design-gate.md`; el `gate-report-T02.yaml` (proposal) va en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_DESIGN_GATE/`, no en el pack. Plantillas en `templates/`; todas las `.md` siguen STD-OKF-001.
Todos los archivos generados se almacenan en la carpeta `testing\<DSP-ID>\[<SSP-ID>\]`. Excepción: el `gate-report-T02.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_DESIGN_GATE/gate-report-T02.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.
## Semantic model
- Regresión: el `QTS` incluye `## Estrategia de regresión` (criterios de selección por impacto usando el `IMP` de requisitos, pruebas de caracterización de la línea base, humo y retest) y el `QTP` `## Selección de regresión` con los TC elegidos y su motivo. En Greenfield se declara «no aplica» con justificación.
- `qa-test-strategy.md` responde **¿cómo vamos a probar?** (alcance, enfoque por riesgo, niveles/tipos/superficies, técnicas, estrategia de automatización, entorno y datos, criterios de entrada/salida, restricciones, supuestos, provenance). `qa-test-plan.md` responde **¿cómo organizamos y ejecutamos las pruebas?** (alcance concreto, actividades, prioridades, TSN/TC, entornos, datos, dependencias, responsabilidades, secuenciación, criterios, contingencias, provenance). Ambos viven aquí; no hay skills separados.
- `TC` lleva `automation_status` (`MANUAL_ONLY`, `AUTOMATION_CANDIDATE`, `PARTIALLY_AUTOMATED`, `AUTOMATED`). El modo de ejecución (`MANUAL`, `AUTOMATED_STANDALONE`, `AUTOMATED_CICD`) **no** es propiedad del TC: pertenece a cada `EXEC`.
- **Test Data (QUÉ datos):** `test-data-plan.md` y un `TDR-*` por requisito de datos (TC/TSN, entidades, relaciones, invariantes, clases de equivalencia, límites, combinaciones, estado esperado, aislamiento, privacidad/masking, limpieza, `source_type`, `pii`). No elegir el mecanismo físico de provisión, no materializar datos (TDA) ni ejecutar pruebas.
- `TSN`: situación de alto nivel. `TC`: verificación concreta con precondiciones, datos, pasos y oracle. Un TSN tiene 1..N TC. Un TC puede ser manual; no crear `AT-*`.
- Secciones obligatorias de un TC: `## Precondiciones`, `## Datos de prueba`, `## Pasos`, `## Resultado esperado (oracle)`.
- Readiness de cada TC (`READY`, `BLOCKED_CLARIFICATION`, `DEFERRED`) se registra en `coverage-matrix.yaml`, no en el frontmatter (`status` es `draft`).
- Un TC que depende de una pregunta abierta es `BLOCKED_CLARIFICATION`. No cuenta como cubierto y el gate falla mientras siga en alcance; solo se admite fuera con `deferred_items[].decision_ref`.
- Datos y precondiciones de olas posteriores se declaran como datos sembrados en el plan, nunca se asumen.
- Oracles que dependan de un término sin definir (p. ej. «datos sensibles») citan la definición propuesta y su pregunta abierta.
## Verificación determinista
`python scripts/check_test_design.py --pack <dir> --critical-risks RISK-001,… --profile design` devuelve los checks `script` del gate (cobertura RISK→TSN→TC, oracle y datos, TDR y seguridad de datos, trazabilidad, superficies, pendientes en alcance). Los checks `independent-review` los aporta un revisor distinto del autor.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/TEST_DESIGN_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla.
## Publication
Solo un TC aprobado es elegible para issue GitLab `TestCase`; un TSN nunca se publica. `publication_eligible` es decisión del orquestador tras TEST_DESIGN_REVIEW_GATE.

## Contrato obligatorio de especificación detallada de TC (v5.2.1)
Cada TC `READY` DEBE ser ejecutable por un tercero sin suposiciones. Aplicar `resources/test-case-detail-standard.md` y `templates/TestCase-OKF.md`.
- **Precondiciones**: identificadores PC-*, estado inicial verificable, evidencia/consulta de comprobación y dependencia de ambiente; nunca suponer datos existentes.
- **Datos de prueba**: identificadores TD-*, valores concretos o dataset versionado + fila/seed, estrategia aplicada (equivalence partitioning, boundary value analysis, decision table, state transition, pairwise, negative/security), razón de selección, origen, preparación y cleanup; nunca secretos reales.
- **Pasos**: tabla con STEP-*, acción inequívoca, input TD-*, resultado esperado observable por paso y referencia a evidencia; no usar «validar correctamente».
- **Oracle**: aserciones exactas (status, payload/campo, mensaje, persistencia, evento, estado UI, latencia con umbral cuando corresponda), fuente normativa AC/BR/API, tolerancia explícita y método de observación.
- **Postcondiciones**: estado final, reversión/cleanup e idempotencia cuando aplique.
- **Bloqueos**: valores, reglas o resultados no definidos se registran como AMB-* y TC `BLOCKED_CLARIFICATION`; no inventar oracles.
- **Revisión**: `qa-test-design-reviewer` comprueba precisión, reproducibilidad, consistencia TD→STEP→oracle y estrategia de datos; el orquestador conserva la decisión del gate.

## Surface Target obligatorio
Todo TC identifica inequívocamente su elemento bajo prueba según `resources/surface-target-standard.md`. El gate `surface-target-complete` bloquea READY ante información incompleta o ambigua.

## Contrato TestCase 1.3 (MINOR)
Cada TC nuevo declara `tc_contract: "1.4"` y `api_id` en el frontmatter si `surface: API` (debe coincidir con `api_id` de la tabla Surface Target); completa: `## Intención`; el oracle con `Pass when:` y `Fail when:`; `## Postcondiciones y limpieza` con `Idempotencia`, `cleanup.required` y `cleanup.strategy_ref`; `## Requisitos de evidencia` por modo (`MANUAL`, `AUTOMATED_STANDALONE`, `AUTOMATED_CICD`; `none` si no aplica); `## Restricciones de ejecución` (PRODUCTION siempre prohibido; `destructive: true` exige `requires_human_authorization: true`); `## Trazabilidad` coherente con el frontmatter; y `test_level` y `criticality`. Esquema: `resources/schemas/test-case.schema.yaml`. Los TC sin `tc_contract` se validan con las reglas previas (legacy) y no se migran masivamente.
- Responsabilidades: generar TC conforme al contrato; definir Intención; generar PC-*; asociar TDR-*; generar STEP-* con resultado esperado por paso; definir oracle global; definir postcondiciones y cleanup; definir requisitos de evidencia y restricciones de ejecución; definir automation_status; preservar provenance.
- Prohibido: generar AT; seleccionar un execution mode final; ejecutar TC; materializar TDA; introducir código específico de framework; modificar el scope del DSP.
