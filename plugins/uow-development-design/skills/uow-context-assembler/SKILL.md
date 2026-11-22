---
name: uow-context-assembler
description: "Usar cuando una User Story y sus insumos (DSP o SSP, FDT, contratos API, modelos de BD, UX, ADR y handoffs existentes) deban reunirse y versionarse como contexto de partida, separando hechos, inferencias, supuestos y desconocidos, antes de derivar Unidades de Trabajo."
metadata:
  version: "1.3.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Context Assembler
Reúne y versiona el contexto de partida de una User Story. Produce un `UCX` con cada insumo identificado por ID, versión y ruta, y cada afirmación clasificada.
## Required
US (id, versión, ruta), modo y, en Brownfield y Evolution, la línea base. Rutas de búsqueda: las de `inputs_read_only` en `assets/pathmap.json` (no se repiten aquí).
## Output
`UCX` (plantilla `templates/UCX-OKF.md`). Lista los criterios de aceptación de la US (`acceptance_criteria`) y los insumos con `id`, `resource` y `version`.
## Rules
- Separar `Hechos` (con fuente versionada), `Inferencias`, `Supuestos` y `Desconocidos y preguntas abiertas`. Lo que no se encuentra es un desconocido, nunca un hecho.
- Reportar conflictos entre fuentes (p. ej. la US y el FDT discrepan) sin resolverlos.
- No diseñar la solución, no partir la US y no copiar el contenido de otros documentos: referenciar.
- Brownfield y Evolution: registrar `baseline.ref` y `baseline.commit`.
## Verificación determinista
`python scripts/check_uow_package.py --root <dir> --profile context` devuelve los checks `script` de `CONTEXT_GATE`.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/CONTEXT_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T01.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/CONTEXT_GATE/` y es lo único que este skill escribe allí.

