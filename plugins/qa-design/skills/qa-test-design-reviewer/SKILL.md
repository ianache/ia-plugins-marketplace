---
name: qa-test-design-reviewer
description: Usar como quality gate independiente para revisar un QA Test Design Pack, cobertura, trazabilidad, oracles, redundancia y cobertura por test surface antes de automatización o ejecución.
metadata:
  version: "1.6.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Test Design Reviewer
Revisar el mismo `QTD` completo (Strategy, Plan, TSN, TC, Test Data Plan y TDR) como una sola unidad gobernada, sin rediseñarlo silenciosamente. El revisor **no puede ser el autor** del diseño (check `reviewer-independent-of-author`).
## Checks
Estrategia, plan, coverage matrix, priorización, Test Data Plan y TDR (cobertura de datos, privacidad, secretos), trazabilidad, TSN y TC. Cobertura `RISK→TSN`; `TSN→1..N TC`; oracle y datos por TC; surfaces; duplicados; scope drift; trazabilidad `DSP→US→RISK→TSN→TC`; TC bloqueados por aclaración que siguen dentro del alcance.
`python scripts/check_test_design.py --pack <dir> --profile review` ejecuta los checks deterministas del gate.
## Output
`QTR`: hallazgos con severidad, acciones correctivas y `human_review_required`. Plantilla `templates/Test-Design-Review.md`.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/TEST_DESIGN_REVIEW_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla. Excepción: el `gate-report-T03.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_DESIGN_REVIEW_GATE/gate-report-T03.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.

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

## Dimensiones de revisión de TC (contrato 1.3)
Revisar cada TC en: SCOPE, TRACEABILITY, INTENT, PRECONDITIONS, TEST_DATA, STEPS, STEP_EXPECTATIONS, ORACLE, POSTCONDITIONS, CLEANUP, EVIDENCE_REQUIREMENTS, EXECUTION_CONSTRAINTS, AUTOMATION_STATUS y SECURITY.
Debe detectar: TC sin TSN, sin requirement o sin risk; scope inventado; TDR inexistente; precondición no verificable; step ambiguo; resultado esperado no observable; oracle débil; contradicción entre expected y oracle; destructive sin autorización; PRODUCTION permitido indebidamente; PII o secretos; automation_status inconsistente.
No corrige silenciosamente el TC: emite REWORK con acciones correctivas. El validador determinista (`scripts/check_tc_detail.py`) cubre la estructura; la semántica queda en esta revisión.
