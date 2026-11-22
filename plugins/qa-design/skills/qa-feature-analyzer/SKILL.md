---
name: qa-feature-analyzer
description: Usar cuando un Development Scope Pack (DSP) validado deba convertirse en análisis QA trazable, identificando riesgos, ambigüedades, evidencia y test surfaces sin redefinir el alcance.
metadata:
  version: "1.6.0"
  author: "COMSATEL"
  type: "qa"
---
# QA Feature Analyzer
## Purpose
Transformar DSP + evidencia upstream en `QFA` (QA Feature Analysis Pack).
## Required
DSP id/versión/estado/ruta y User Stories en scope. Verificar que la versión efectiva de cada US coincide con la que el DSP declara; si una US es posterior a la fecha del DSP, registrar la deriva como observación.
## Conditional
Architecture/API/security/integration/data; UX para WEB/MOBILE; defectos/incidentes históricos.
## Tasks
Validar DSP/provenance; contar criterios por US contra los archivos; detectar surfaces; producir `RISK-*`; registrar ambigüedades y **contradicciones entre criterios** (una contradicción abierta no se esconde: se registra como AMB-* y marca el criterio `NEEDS_CLARIFICATION`); evaluar readiness por criterio.
## Output
RISK conserva trazabilidad a DSP/US. No producir TSN, TC ni AT. Usar la plantilla `templates/QA-Feature-Analysis-Pack.md`.
Todos los archivos generados por este skill se almacenan en la carpeta `testing\<DSP-ID>\[<SSP-ID>\]\`. Excepción: el `gate-report-T01.yaml` (gate_proposal) se escribe en `.comsatel/qa-design/runs/<run-id>/evidence/FEATURE_ANALYSIS_GATE/gate-report-T01.yaml`, la carpeta de evidencia del orquestador, y es lo único que este skill escribe allí.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/FEATURE_ANALYSIS_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial: lo no listo se declara en `deferred_items` con decisión humana o el gate falla.
## Invariants
Nunca modificar el DSP. No diseñar pruebas. Marcar inferencias `[I]` y preguntas abiertas.
