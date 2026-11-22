---
name: qa-agentic-test-reviewer
description: Usar para revisar independientemente implementación, ejecución y evidencia de Test Cases aprobados contra el Test Design, el DSP, el Development Context y el entorno.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Agentic Test Reviewer
Revisar los `QTE` de **todas** las superficies del plan contra `QTD`, DSP, Development Context y entorno.
## Checks
`AT→TC`, `TDA→TDR→TC`, `TC→TSN`, ejecución contra oracle, evidencia reproducible, seguridad (secrets, PII, destructivo, PROD), scope y cobertura manual/automatizada, distinguiendo explícitamente los tres modos de ejecución.
## Execution modes
El gate distingue `MANUAL`, `AUTOMATED_STANDALONE` y `AUTOMATED_CICD` y aplica evidencia según el modo:
- `MANUAL`: TC, oracle, datos, ejecutor, entorno y evidencia. No exige AT.
- `AUTOMATED_STANDALONE`: AT→TC, runtime y versión, entorno, TDA, reportes y reproducibilidad.
- `AUTOMATED_CICD`: AT→TC, pipeline y job, commit, entorno, TDA, artifacts, reportes y logs, y procedencia GITLAB real (sin identificadores inventados).
`python scripts/check_test_engineering.py --pack <engineering-pack> --design-pack <design-pack> --profile review` ejecuta los checks deterministas; un modo sin EXEC cuenta como no aplicable (PASS).
## Output
`QER`: hallazgos y acciones correctivas. Plantilla `templates/Test-Engineering-Review.md`.
Todos los archivos generados por este skill se almacenan en la carpeta `testing\<DSP-ID>\[<SSP-ID>\]\`. Excepción: el `gate-report-T06.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_ENGINEERING_REVIEW_GATE/gate-report-T06.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/TEST_ENGINEERING_REVIEW_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla.
