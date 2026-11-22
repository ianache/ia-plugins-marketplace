---
name: qa-agentic-test-engineer
description: Usar cuando un QA Test Design Pack aprobado y Development Context deban convertirse en Test Execution Plan, harness, tests automatizados, ejecuciones y evidencia por test surface.
metadata:
  version: "1.8.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Agentic Test Engineer
## Purpose
Definir **HOW to implement/execute** los TC aprobados, una tarea por test surface.
## Required
QTD aprobado (TEST_DESIGN_REVIEW_GATE en PASS), Development Context Pack, DSP y la surface asignada.
## Output
`QTE` (Engineering Pack): `test-execution-plan.md`, `test-data-generation-plan.md`, `test-data-manifest.yaml`, `test-data/{datasets,fixtures,scripts}/` (TDA), `automated-tests/AT-*`, `executions/EXEC-*`, `evidence/EVD-*`, `gate-report`; condicional a `AUTOMATED_CICD`: `cicd/ci-test-execution.yaml` y fragments/templates de `.gitlab-ci.yml`. Plantillas en `templates/`.
Todos los archivos generados por este skill se almacenan en la carpeta `testing\<DSP-ID>\[<SSP-ID>\]\`. Excepción: el `gate-report-T05-<SURFACE>.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_ENGINEERING_GATE/gate-report-T05-<SURFACE>.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.
## Rules
- `TC-*` es la especificación verificable; `AT-*` es una implementación opcional de un TC aprobado y referencia exactamente un TC primario.
- Un TC manual se ejecuta sin AT. No automatizar un TSN directamente. Resolver framework desde el contexto.
- Credenciales solo por referencia. Sin acciones destructivas ni PROD sin autorización explícita (el check `no-destructive-or-unauthorized-prod` escala a HIL).
- No ejecutar contra sistemas con datos reales (p. ej. el proyecto GitLab que aloja las US) salvo autorización expresa; preferir entornos de prueba de solo lectura.
## Alcance SSP
Con SSP, `T05` solo implementa los TC de `plan.ssp_tc_ids` (los TC que comparten historia con el SSP). Un AT o un EXEC que referencie un TC fuera de esa selección hace fallar el check `ssp-scope-respected`. Sin SSP, el alcance es el DSP completo.

## Execution modes
`execution_mode` pertenece a cada `EXEC-*` (no al TC) y es explícito: `MANUAL`, `AUTOMATED_STANDALONE` o `AUTOMATED_CICD`. El `automation_status` del TC es independiente. Un mismo TC puede tener EXEC MANUAL y luego EXEC automatizadas; cada re-run crea una EXEC nueva (`rerun_of`) y conserva el historial.
- `MANUAL`: TC → ejecución manual → EXEC → EVD. No requiere AT. Capturar resultado, observaciones, capturas, adjuntos, defectos, entorno, marcas de tiempo y ejecutor.
- `AUTOMATED_STANDALONE`: TC → AT → runtime autorizado → EXEC → EVD. El runtime puede ser estación de trabajo, entorno QA, agente IA, Playwright, pytest, Newman, BrowserStack u otro autorizado; no hardcodear una herramienta universal.
- `AUTOMATED_CICD`: TC → AT → CI/CD Test Execution Specification → GitLab pipeline → job → EXEC → EVD. GitLab CI/CD es el execution engine (no existe un skill runner). Preparar AT, TDA, suites, `cicd/ci-test-execution.yaml`, fragments de `.gitlab-ci.yml`, rules, dependencias, variables por referencia, artifacts/reports y el mapeo job↔TC/AT. La EXEC captura provider GITLAB, pipeline_id/URL, job_id/nombre, commit_sha, rama o tag, entorno, TC, AT, TDA, marcas de tiempo, estado y evidencia; no inventar identificadores.
- No asumir que toda automatización usa CI/CD. No redefinir el alcance, no modificar silenciosamente un TC, no generar AT desde un TSN.
## Test Data (CÓMO crear o proveer)
Recibe TC y TDR aprobados y materializa cada `TDR-*` como `TDA-*` (datasets, fixtures, factories/generadores, seeds/setup y cleanup) con `test-data-generation-plan.md` y `test-data-manifest.yaml`. Trazabilidad `TC → TDR → TDA → EXEC → EVD`. Preferir datos sintéticos, no persistir secretos, controlar PII, aplicar masking, favorecer determinismo y evitar contaminación entre pruebas. Ninguna EXEC que dependa de datos pasa a READY sin TDR/TDA obligatorios en estado READY o una excepción con `decision_ref` humano.
## Verificación determinista
`python scripts/check_test_engineering.py --pack <engineering-pack> --design-pack <design-pack> --profile engineering` devuelve los checks `script` del gate. Los `independent-review` los aporta un revisor distinto del autor.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/TEST_ENGINEERING_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla.

## Validación previa a AT (contrato TC 1.3)
Antes de generar un AT: 1) comprobar que el TC fue aprobado por el gate (readiness READY en `coverage-matrix.yaml`) y pasa `check_tc_detail.py`; 2) leer `automation_status`; 3) leer `Restricciones de ejecución`; 4) leer los TDR; 5) materializar TDA cuando corresponda; 6) derivar el AT preservando el oracle del TC; 7) no modificar el TC.
El AT declara `testcase_ref: TC-...`. Flujos: AUTOMATED_STANDALONE, TC → AT → runtime → EXEC → EVD; AUTOMATED_CICD, TC → AT → pipeline/job GitLab → EXEC → EVD. El EXEC conserva `testcase_ref` y `at_ref`. No se inventan identificadores de CI/CD. Solo se exigen las evidencias del modo utilizado.

## Automatización API subordinada (postman-automation)
Para los TC aprobados de superficie API, T05-API delega la implementación en `postman-automation` (modo subordinado; excepto los TC de `test_type: rendimiento`, ver la sección de carga). Reglas:
1. El engineer no escribe por su cuenta los AT-* de superficie API: cada AT API corresponde a un caso de la colección del microservicio (carpeta `<TC-ID> - <Nombre>`).
2. El skill escribe la colección en el repositorio del microservicio (`test/functional/postman.json`) y el reporte en el pack de ingeniería: `automated-tests/postman/<microservicio>/postman-automation-report.yaml` (un subordinado por microservicio).
3. Cada AT API declara `surface: API` y `testcase_ref: TC-...`. El reporte debe listar ese TC con `estado` `AUTOMATED` o `PARTIAL`.
4. La ejecución newman se registra como EXEC (`execution_mode: AUTOMATED_STANDALONE`, runtime `newman`) con su `at_ref`.
5. El alcance es el SSP del plan (`scope_ssp`) cuando existe; sin SSP, el DSP completo.

El check `api-automation-subordinate-traceable` (`scripts/check_test_engineering.py`, perfil engineering) falla si falta el reporte, si un TC de un AT API no aparece como `AUTOMATED` o `PARTIAL`, o si `newman.estado` no es `EXECUTED`. Sin AT de superficie API, el check pasa.

## Automatización web subordinada (web-automation)
Para los TC aprobados de superficie `WEB` de un AUT, `T05-WEB` delega la implementación en `web-automation`. El AUT es el Shell cuando hay micro-frontends, o la aplicación web específica en el caso legado. El framework (Playwright o Selenium) lo declara el documento `WEB` del AUT en la KB; si no lo declara, la tarea se bloquea.
1. El engineer no escribe por su cuenta los AT de superficie WEB. Cada AT web corresponde a un TC de la lista que `web-automation` implementa.
2. El subordinado escribe el código en `test/functional/<framework>/` del repositorio del AUT, en una rama con MR, y su reporte en `automated-tests/web/<aut>/web-automation-report.yaml`.
3. Cada AT web declara `surface: WEB` y `testcase_ref: TC-...`. El reporte debe listar ese TC con estado `AUTOMATED` o `PARTIAL`.
4. La ejecución la realiza el pipeline del MR. Cuando termina, el engineer registra la EXEC (`execution_mode: AUTOMATED_CICD`) con el ID y la URL reales del pipeline, y actualiza `ejecucion` del reporte.

El check `web-automation-subordinate-traceable` (perfil engineering) falla si falta el reporte, si un TC de un AT web no aparece como `AUTOMATED` o `PARTIAL`, o si `ejecucion.estado` no es `EXECUTED`. Sin AT de superficie WEB, el check pasa.

## Carga subordinada (loadtest-automation)
Los AT de TC `test_type: rendimiento` no van a postman-automation. Los implementa `loadtest-automation` (suite k6 en `test/load/`) y su reporte va en `automated-tests/k6/<microservicio>/loadtest-automation-report.yaml`, un reporte por microservicio. Cada AT de rendimiento corresponde a un módulo `scenarios/TC-<ID>.js`. El reporte declara `criterio` (`BASELINE` o `APROBADO <DATA-xx|NFR-xx>`), lista el TC con `estado: IMPLEMENTED` y tiene `k6.estado: EXECUTED`. El check `load-automation-subordinate-traceable` falla si falta cualquiera de estos elementos. Sin AT de rendimiento, pasa.
