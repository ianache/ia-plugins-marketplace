---
name: qa-quality-intelligence
description: Usar para correlacionar evidencia QA (packs, ejecuciones, defectos, CI/CD, observabilidad e historia) y recomendar una decisión de calidad sin aprobar el release.
metadata:
  version: "1.6.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Quality Intelligence
Consumir packs, ejecuciones, evidencia, defectos, CI/CD, observabilidad e historia.
## Traceability
Evaluar cobertura y confianza sobre `DSP→US→RISK→TSN→TC→AT?→EXEC→EVD→DEFECT→QUALITY_DECISION`; `AT` es opcional.
## Segmentación y métricas
Segmentar por `execution_mode`, `automation_status`, test surface, entorno, pipeline, suite, riesgo y requisito. Métricas sugeridas: cobertura de ejecución manual, cobertura de automatización, tasa de ejecución standalone y CI/CD, pass/fail/error/blocked, tests flaky, tasa de re-run, duración, completitud de evidencia, readiness TDR/TDA, detección de defectos por modo y cobertura de riesgos críticos.
**No confundir** una falla de pipeline/job con una falla funcional sin clasificar la causa (`failure_class`: FUNCTIONAL, PIPELINE, ENVIRONMENT, TEST_DATA, TOOLING).
`python scripts/quality_metrics.py --pack <engineering-pack> --design-pack <design-pack>` calcula las métricas; con `--checks` devuelve los checks `script` del gate (`results-segmented-by-mode`, `failures-classified-by-cause`).
## Output
`QQI` con recomendación `READY | READY_WITH_RISK | NOT_READY | INSUFFICIENT_EVIDENCE`. Es una recomendación, no el gate: la decisión de calidad es humana (HUMAN_GATE). Sin provenance o scope establecido, declarar `INSUFFICIENT_EVIDENCE` y proponer el check como `FAIL`.
Todos los archivos generados por este skill se almacenan en la carpeta `testing\<DSP-ID>\[<SSP-ID>\]\`. Excepción: el `gate-report-T07.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/QUALITY_INTELLIGENCE_GATE/gate-report-T07.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/QUALITY_INTELLIGENCE_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla.
